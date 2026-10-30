// Claude Usage Bridge - content script
// Reads the percentages and reset times shown on claude.ai's usage screen (settings page or dialog)
// while YOU have that page open, and hands them to the background script. It only reads what is
// displayed on the page; it never opens pages, clicks anything, or touches passwords or cookies.
//
// The parser does not rely on the page language: a "bar" is a short line with a percentage and a
// word, sitting right after a line that contains a time. The first bar is the session limit and
// the second one the weekly limit unless the labels say otherwise (many languages are recognised).

const api = typeof browser !== 'undefined' ? browser : (typeof chrome !== 'undefined' ? chrome : null);

const PCT_RE = /(\d{1,3}(?:[.,]\d+)?)\s*%/;
const TIME_RE = /\d{1,2}:\d{2}/;
const PCT_ONLY_RE = /^(\d{1,3}(?:[.,]\d+)?)\s*%$/;
const USED_RE = /(已使用|used|使用済|사용|usado|utilis|verwendet|usata|gebruikt)/i;
const RESET_RE = /(重設|重置|重新設定|resets?|リセット|재설정|초기화|restablec|réinitialis|zurückgesetzt|reimposta)/i;
const SESSION_RE = /(工作階段|工作阶段|会话|會話|session|セッション|세션|sesión|sessão|sitzung|sessione)/i;
const WEEK_RE = /(本週|本周|每週|每周|week|週間|今週|주간|이번 주|semana|semaine|woche|settimana)/i;
const WARN_RE = /(用完|耗尽|耗盡|run out|hit your|reach your limit|使い切|なくなる|소진|agotar|épuiser|aufgebraucht)/i;

const NOISE_RE = /(重設|重置|重新設定|resets?|リセット|재설정|초기화|上午|下午|凌晨|晚上|傍晚|早上|清晨|中午|午前|午後|오전|오후|AM|PM|今天|今日|오늘|today|明天|明日|내일|tomorrow|at|on|に|에)/gi;
const WD_ZH = { 日: 0, 天: 0, 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6 };
const WD_JA = { 日: 0, 月: 1, 火: 2, 水: 3, 木: 4, 金: 5, 土: 6 };
const WD_KO = { 일: 0, 월: 1, 화: 2, 수: 3, 목: 4, 금: 5, 토: 6 };
const WD_EN = { sun: 0, mon: 1, tue: 2, wed: 3, thu: 4, fri: 5, sat: 6 };
const MON_EN = { jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11 };

function toIso(d) {
  return d.toISOString().replace(/\.\d+Z$/, 'Z');
}

// Turns "週五上午3:40 重設", "Resets Fri 3:40 AM", "金曜日 午前3:40 にリセット", "금요일 오전 3:40",
// "2 小時 10 分鐘後重設" ... into the next reset time (ISO). Returns null when it cannot tell.
function parseReset(t, now = new Date()) {
  if (!t) return null;
  const tm = t.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i);
  if (tm) {
    let h = +tm[1];
    const mi = +tm[2];
    const pre = t.slice(0, tm.index);
    let ap = tm[3] ? tm[3].toUpperCase() : null;
    if (!ap) {
      if (/下午|晚上|傍晚|午後|오후/.test(pre)) ap = 'PM';
      else if (/上午|凌晨|早上|清晨|午前|오전/.test(pre)) ap = 'AM';
      else if (/中午/.test(pre)) ap = 'NOON';
    }
    if (ap === 'PM' && h < 12) h += 12;
    else if (ap === 'AM' && h === 12) h = 0;
    else if (ap === 'NOON' && h < 11) h += 12;

    const d = new Date(now);
    d.setHours(h, mi, 0, 0);
    let wd = null;
    const zw = t.match(/(?:週|周|星期)([一二三四五六日天])/);
    const jw = t.match(/([日月火水木金土])曜/);
    const kw = t.match(/([일월화수목금토])요일/);
    const ew = t.match(/\b(sun|mon|tue|wed|thu|fri|sat)[a-z]*/i);
    if (zw) wd = WD_ZH[zw[1]];
    else if (jw) wd = WD_JA[jw[1]];
    else if (kw) wd = WD_KO[kw[1]];
    else if (ew) wd = WD_EN[ew[1].toLowerCase()];
    const zd = t.match(/(\d{1,2})\s*[月월]\s*(\d{1,2})\s*[日일]/);
    const ed = t.match(/\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})\b/i);

    if (zd || ed) {
      const mo = zd ? +zd[1] - 1 : MON_EN[ed[1].toLowerCase()];
      const da = zd ? +zd[2] : +ed[2];
      d.setMonth(mo, da);
      if (d <= now) d.setFullYear(d.getFullYear() + 1);
    } else if (wd !== null) {
      d.setDate(d.getDate() + ((wd - d.getDay() + 7) % 7));
      if (d <= now) d.setDate(d.getDate() + 7);
    } else if (/明天|내일|明日|tomorrow/i.test(t)) {
      d.setDate(d.getDate() + 1);
    } else {
      const rest = t.replace(TIME_RE, '').replace(NOISE_RE, '');
      if (/\p{L}/u.test(rest)) return null; // a weekday or date word in a language we cannot read
      if (d <= now && !/今天|今日|오늘|today/i.test(t)) d.setDate(d.getDate() + 1);
    }
    return toIso(d);
  }

  const g = (re) => {
    const m = t.match(re);
    return m ? +m[1] : 0;
  };
  const dd = g(/(\d+)\s*(?:天|日|일|days?|d\b)/i);
  const hh = g(/(\d+)\s*(?:小時|小时|時間|시간|hours?|hrs?|h\b)/i);
  const mm = g(/(\d+)\s*(?:分鐘|分钟|分|분|minutes?|mins?|m\b)/i);
  if (dd || hh || mm) return toIso(new Date(now.getTime() + ((dd * 24 + hh) * 60 + mm) * 60000));
  return null;
}

function isBarLine(lines, i) {
  const l = lines[i];
  if (l.length > 30 || !PCT_RE.test(l)) return false;
  if (!/[^\d\s%.,]/.test(l.replace(PCT_RE, ''))) return false; // "9%" alone is a product row, not a bar
  if (USED_RE.test(l)) return true;
  const prev = lines[i - 1] || '';
  return prev.length <= 60 && (RESET_RE.test(prev) || TIME_RE.test(prev)); // a reset/time line comes right before
}

function parse(text, now = new Date()) {
  const lines = text.split('\n').map((s) => s.replace(/\s+/g, ' ').trim()).filter(Boolean);

  const bars = [];
  lines.forEach((l, i) => {
    if (!isBarLine(lines, i)) return;
    let k0 = -1;
    for (let k = i - 1; k >= Math.max(0, i - 3); k--) {
      if (RESET_RE.test(lines[k])) {
        k0 = k;
        break;
      }
    }
    const prev = lines[i - 1] || '';
    if (k0 < 0 && TIME_RE.test(prev) && !PCT_RE.test(prev)) k0 = i - 1;
    const resetText = k0 >= 0 ? lines[k0] : '';
    const label = k0 >= 0 ? lines[k0 - 1] || '' : prev;
    bars.push({ idx: i, pct: parseFloat(l.match(PCT_RE)[1].replace(',', '.')), label, resetText });
  });

  let session = bars.find((b) => SESSION_RE.test(b.label));
  let week = bars.find((b) => WEEK_RE.test(b.label) && b !== session);
  if (!session) session = bars.find((b) => b !== week);
  if (!week) week = bars.find((b) => b !== session);
  if (!session || !week) return null;
  const extra = bars.filter((b) => b !== session && b !== week).slice(0, 6);
  const lastIdx = Math.max(...bars.map((b) => b.idx));
  for (const b of [session, week, ...extra]) {
    b.resetAt = parseReset(b.resetText, now);
    delete b.idx;
  }

  // Per-product rows: a short label line followed by a line that is just "NN%".
  const products = {};
  const firstProductIdx = lines.findIndex((l, i) => i > lastIdx && PCT_ONLY_RE.test(l));
  if (firstProductIdx > 0) {
    for (let j = firstProductIdx; j < lines.length && Object.keys(products).length < 10; j++) {
      const m = lines[j].match(PCT_ONLY_RE);
      const label = lines[j - 1] || '';
      if (m && label.length <= 40 && !/^[\d\s%.,]+$/.test(label) && !PCT_ONLY_RE.test(label)) {
        products[label] = parseFloat(m[1].replace(',', '.'));
      }
    }
  }

  const warning = lines.find((l) => l.length > 12 && WARN_RE.test(l)) || '';
  return { v: 1, session, week, extra, products, warning, scrapedAt: toIso(new Date()) };
}

let lastSig = '';

function findRoot() {
  const dlg = document.querySelector('[role="dialog"]');
  if (dlg && /%/.test(dlg.innerText || '')) return dlg;
  if (location.pathname.startsWith('/settings')) return document.body;
  return null;
}

function tick() {
  const root = findRoot();
  if (!root) return;
  const data = parse(root.innerText || '');
  if (!data) return;
  const sig = JSON.stringify([data.session.pct, data.week.pct, data.session.resetText, data.week.resetText, data.products, data.warning]);
  if (sig !== lastSig) {
    // Send only when the numbers on screen change, so "updated N min ago" stays truthful.
    lastSig = sig;
    try {
      api.runtime.sendMessage({ type: 'usage', data });
    } catch (e) {
      /* the extension was reloaded; refresh the page */
    }
  }
}

if (typeof module !== 'undefined') {
  module.exports = { parse, parseReset };
} else {
  setInterval(tick, 2000);
}
