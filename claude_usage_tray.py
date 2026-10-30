# -*- coding: utf-8 -*-
"""
Claude Usage tray widget (Windows 11)

- Lives in the system tray: the icon shows your current usage percentage (green / orange / red).
- Left-click the icon for a small window, right-click for the menu.
- Data comes from the browser extension, which reads the numbers shown on claude.ai
  (Settings > Usage) when YOU open that page, and sends them to this program on 127.0.0.1:47821.
  Nothing is fetched automatically in the background.
- The window follows your active window: browser tab / Claude desktop app -> claude.ai products,
  terminal / editor -> Claude Code. (The session and weekly limits are shared; the per-product
  block is what changes.)
- Alerts at 80 / 90 / 95 % and when the page warns that the limit will run out early.
- Interface language follows Windows automatically (see the lang folder; the tray menu can override it).

Install:  double-click START_HERE_Install.bat
Manual:   pip install pystray pillow  ->  pythonw claude_usage_tray.py   (use python to see errors)
"""
import ctypes
import json
import locale
import os
import queue
import re
import sys
import threading
import time
import traceback
import webbrowser
import tkinter as tk
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk

try:
    import winreg
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    IS_WIN = True
except Exception:  # not Windows (e.g. running the tests on Linux)
    IS_WIN = False

try:
    import winsound
except ImportError:
    winsound = None

PORT = 47821
BASE_DIR = Path(__file__).resolve().parent
LANG_DIR = BASE_DIR / "lang"
APP_DIR = Path.home() / ".claude_usage_tray"
CFG_PATH = APP_DIR / "config.json"
DATA_PATH = APP_DIR / "last_usage.json"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "ClaudeUsageTray"

DEFAULT_CFG = {
    "mode": "auto",                 # auto / web / code
    "language": "auto",             # auto, or a code such as en, zh-TW, zh-CN, ja, ko
    "thresholds": [80, 90, 95],     # alert percentages
    "stale_minutes": 60,            # after this the window suggests opening the usage page again
    "browsers": ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "vivaldi.exe", "arc.exe"],
    "code_apps": ["windowsterminal.exe", "cmd.exe", "powershell.exe", "pwsh.exe", "wezterm-gui.exe",
                  "alacritty.exe", "mintty.exe", "code.exe", "cursor.exe", "windsurf.exe"],
}
VIEW_NAMES = {"web": "claude.ai", "code": "Claude Code"}
COLORS = {"ok": "#3a9d5d", "warn": "#e0932b", "bad": "#d64545", "none": "#7a7a7a"}


# ---------------------------------------------------------------- settings and shared state
def load_cfg():
    """Defaults merged with config.json; values that are missing or of the wrong type are ignored."""
    cfg = json.loads(json.dumps(DEFAULT_CFG))
    try:
        user = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        user = {}
    if not isinstance(user, dict):
        user = {}
    if user.get("mode") in ("auto", "web", "code"):
        cfg["mode"] = user["mode"]
    if isinstance(user.get("language"), str) and user["language"].strip():
        cfg["language"] = user["language"].strip()
    th = user.get("thresholds")
    if isinstance(th, list):
        th = sorted({int(x) for x in th if isinstance(x, (int, float)) and not isinstance(x, bool) and 1 <= x <= 100})
        if th:
            cfg["thresholds"] = th
    sm = user.get("stale_minutes")
    if isinstance(sm, (int, float)) and not isinstance(sm, bool):
        cfg["stale_minutes"] = max(5, min(1440, int(sm)))
    for k in ("browsers", "code_apps"):
        v = user.get(k)
        if isinstance(v, list):
            cfg[k] = [x.lower() for x in v if isinstance(x, str)]
    return cfg


def save_cfg(cfg):
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        CFG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


class Shared:
    def __init__(self):
        self.lock = threading.Lock()
        self.usage = None
        self.received = None
        self.cfg = load_cfg()
        self.q = queue.Queue()


SH = Shared()


def save_last():
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with SH.lock:
            obj = {"usage": SH.usage, "received": SH.received.isoformat() if SH.received else None}
        DATA_PATH.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def load_last():
    try:
        obj = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        usage = sanitize(obj.get("usage"))
        if usage and obj.get("received"):
            rec = datetime.fromisoformat(obj["received"])
            if rec.tzinfo is not None:
                SH.usage, SH.received = usage, rec
            else:
                SH.usage = None
    except Exception:
        pass


def log_error():
    """Append the current exception to error.log (pythonw has no console). Keeps the file small."""
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        f = APP_DIR / "error.log"
        if f.exists() and f.stat().st_size > 200_000:
            f.unlink()
        with f.open("a", encoding="utf-8") as fh:
            fh.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S}\n{traceback.format_exc()}\n")
    except Exception:
        pass


# ---------------------------------------------------------------- languages (lang/<code>.json)
EN, STR, CUR_LANG, FONT_FAMILY = {}, {}, "en", "Segoe UI"


def available_langs():
    """{code: display name} for every lang/<code>.json. Drop a new file in to add a language."""
    out = {}
    try:
        for f in sorted(LANG_DIR.glob("*.json")):
            try:
                out[f.stem] = json.loads(f.read_text(encoding="utf-8")).get("_name", f.stem)
            except Exception:
                continue
    except Exception:
        pass
    return out


def system_lang_name():
    try:
        langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        name = locale.windows_locale.get(langid, "")
        if name:
            return name.replace("_", "-")
    except Exception:
        pass
    return (os.environ.get("LC_ALL") or os.environ.get("LANG") or "").split(".")[0].replace("_", "-")


def pick_lang(name, available):
    name = (name or "").strip()
    if re.match(r"(?i)^zh", name):
        cands = ["zh-TW"] if re.match(r"(?i)^(zh-(tw|hk|mo)|zh-hant)", name) else ["zh-CN"]
    else:
        cands = [name, name.split("-")[0]] if name else []
    for c in cands:
        if c in available:
            return c
    return "en"


def _read_lang(code):
    try:
        return json.loads((LANG_DIR / f"{code}.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_strings(pref="auto"):
    global EN, STR, CUR_LANG, FONT_FAMILY
    av = available_langs()
    code = pref if pref in av else pick_lang(system_lang_name(), av)
    en = _read_lang("en")
    cur = en if code == "en" else _read_lang(code)
    EN, STR, CUR_LANG = en.get("app", {}), cur.get("app", {}), code
    FONT_FAMILY = cur.get("_font") or en.get("_font") or "Segoe UI"
    return code


def t(key, **kw):
    s = STR.get(key) or EN.get(key) or key
    try:
        return s.format(**kw) if kw else s
    except (KeyError, IndexError, ValueError):
        return s


# ---------------------------------------------------------------- validating incoming data
def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f != f or f < 0 or f > 1000:
        return None
    return min(f, 100.0)


def _txt(v, n=200):
    return v.strip()[:n] if isinstance(v, str) else ""


def _iso(v):
    if not isinstance(v, str):
        return ""
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return v if dt.tzinfo is not None else ""


def _bar(b):
    if not isinstance(b, dict):
        return None
    pct = _num(b.get("pct"))
    if pct is None:
        return None
    return {"pct": pct, "label": _txt(b.get("label"), 60),
            "resetText": _txt(b.get("resetText"), 80), "resetAt": _iso(b.get("resetAt"))}


def sanitize(d):
    if not isinstance(d, dict):
        return None
    s, w = _bar(d.get("session")), _bar(d.get("week"))
    if not s and not w:
        return None
    prods = {}
    p = d.get("products")
    if isinstance(p, dict):
        for k, v in list(p.items())[:10]:
            n = _num(v)
            if n is not None and isinstance(k, str):
                prods[k[:40]] = n
    extra = []
    if isinstance(d.get("extra"), list):
        for e in d["extra"][:6]:
            b = _bar(e)
            if b:
                extra.append(b)
    return {"session": s, "week": w, "products": prods, "extra": extra, "warning": _txt(d.get("warning"), 200)}


# ---------------------------------------------------------------- local receiver (browser extension only)
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, {"ok": True})

    def do_POST(self):
        if not self.path.startswith("/usage"):
            return self._send(404, {"ok": False})
        # Web pages cannot forge the Origin header; only accept browser extensions.
        if not self.headers.get("Origin", "").startswith(("chrome-extension://", "moz-extension://")):
            return self._send(403, {"ok": False})
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n <= 0 or n > 65536:
            return self._send(400, {"ok": False})
        try:
            data = sanitize(json.loads(self.rfile.read(n).decode("utf-8")))
        except Exception:
            data = None
        if not data:
            return self._send(400, {"ok": False})
        with SH.lock:
            SH.usage = data
            SH.received = datetime.now(timezone.utc)
        save_last()
        SH.q.put(("usage",))
        self._send(200, {"ok": True})


# ---------------------------------------------------------------- foreground window detection
def foreground():
    if not IS_WIN:
        return "", ""
    try:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return "", ""
        n = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = kernel32.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return "", buf.value
        size = wintypes.DWORD(1024)
        path = ctypes.create_unicode_buffer(1024)
        ok = kernel32.QueryFullProcessImageNameW(h, 0, path, ctypes.byref(size))
        kernel32.CloseHandle(h)
        return (os.path.basename(path.value).lower() if ok else ""), buf.value
    except Exception:
        return "", ""


def classify(proc, title, cfg):
    """Return 'web' / 'code', or None (keep the current view)."""
    tl = (title or "").lower()
    if proc == "claude.exe":
        return "code" if "claude code" in tl else "web"
    if proc in cfg["browsers"] and "claude" in tl:
        return "code" if "claude code" in tl else "web"
    if proc in cfg["code_apps"]:
        return "code"
    return None


# ---------------------------------------------------------------- display helpers
def level(pct):
    return "ok" if pct < 70 else ("warn" if pct < 90 else "bad")


def fmt_left(dt):
    s = int((dt - datetime.now(timezone.utc)).total_seconds())
    if s <= 0:
        return t("reset_due")
    d, r = divmod(s, 86400)
    h, r = divmod(r, 3600)
    m = r // 60
    if d:
        return t("left_dh", d=d, h=h)
    if h:
        return t("left_hm", h=h, m=m)
    return t("left_m", m=m)


def reset_text(bar):
    ra = bar.get("resetAt")
    if ra:
        try:
            dt = datetime.fromisoformat(ra.replace("Z", "+00:00"))
            left = fmt_left(dt)
            if dt <= datetime.now(timezone.utc):
                return left
            return t("reset_in", left=left, when=f"{dt.astimezone():%m/%d %H:%M}")
        except (ValueError, TypeError, OverflowError, OSError):
            pass
    return bar.get("resetText") or ""


def make_icon(text, color, size=64):
    """Rounded square with the percentage in bold white. Drawn at 256 px, then scaled down for smooth edges."""
    from PIL import Image, ImageDraw, ImageFont
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, S - 8, S - 8), radius=72, fill=color)
    fs = 176 if len(text) <= 2 else 128
    font = None
    for name in ("segoeuib.ttf", "arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, fs)
            break
        except Exception:
            continue
    if font is None:
        try:
            font = ImageFont.load_default(size=fs)  # Pillow 10.1+
        except TypeError:
            font = ImageFont.load_default()
    box = d.textbbox((0, 0), text, font=font)
    x = (S - (box[2] - box[0])) / 2 - box[0]
    y = (S - (box[3] - box[1])) / 2 - box[1]
    d.text((x, y), text, font=font, fill="white")
    resample = getattr(Image, "Resampling", Image).LANCZOS
    return img.resize((size, size), resample)


# ---------------------------------------------------------------- updating = you opening the usage page
USAGE_URL = "https://claude.ai/settings/usage"


def open_usage_page():
    """Nothing is fetched in the background: the numbers update when you open this page yourself."""
    try:
        webbrowser.open(USAGE_URL)
    except Exception:
        pass


# ---------------------------------------------------------------- only one copy at a time
_MUTEX = None


def another_instance_running():
    """True if another copy already holds the named mutex (released by Windows when that copy exits)."""
    global _MUTEX
    if not IS_WIN:
        return False
    try:
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        _MUTEX = kernel32.CreateMutexW(None, False, "Local\\ClaudeUsageTray_SingleInstance")
        return ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS
    except Exception:
        return False


# ---------------------------------------------------------------- start with Windows
def _autostart_cmd():
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        alt = exe[:-10] + "pythonw.exe"
        if os.path.exists(alt):
            exe = alt
    return f'"{exe}" "{os.path.abspath(__file__)}"'


def is_autostart():
    if not IS_WIN:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as k:
            winreg.QueryValueEx(k, RUN_NAME)
            return True
    except OSError:
        return False


def set_autostart(on):
    if not IS_WIN:
        return
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, _autostart_cmd())
        else:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except OSError:
                pass


# ---------------------------------------------------------------- the application
class TrayApp:
    def __init__(self):
        import pystray
        self.pystray = pystray
        self.cfg = SH.cfg
        load_strings(self.cfg.get("language", "auto"))
        self.view = self.cfg["mode"] if self.cfg["mode"] in VIEW_NAMES else "web"
        self.notified = set()
        self.last_warn = ""
        self._prod_sig = None

        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-toolwindow", True)  # no taskbar button, only the tray icon
        except tk.TclError:
            pass
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
        self.root.withdraw()
        self.f_norm = tkfont.Font(family=FONT_FAMILY, size=9)
        self.f_bold = tkfont.Font(family=FONT_FAMILY, size=9, weight="bold")
        self.f_head = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")
        self._build_ui()

        if another_instance_running():
            messagebox.showinfo(t("window_title"), t("already_running"))
            self.root.destroy()
            sys.exit(0)
        load_last()
        self.server = None
        for _ in range(10):  # right after a restart the old copy may still be releasing the port
            try:
                self.server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
                break
            except OSError:
                time.sleep(0.5)
        if self.server is None:
            messagebox.showerror(t("window_title"), t("already_running"))
            self.root.destroy()
            sys.exit(1)
        self.server.daemon_threads = True
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

        self.icon = pystray.Icon("claude_usage", make_icon("?", COLORS["none"]), t("window_title"), self.build_menu())
        self.update_icon()
        self.icon.run_detached()

        self.root.after(200, self.pump)
        self.root.after(1000, self.tick)
        if "--show" in sys.argv:  # first start after the one-click install: show the window
            self.root.after(800, self.show)

    # ---- tray menu (rebuilt when the language changes)
    def build_menu(self):
        M, Menu = self.pystray.MenuItem, self.pystray.Menu
        langs = available_langs()

        def mode_item(label, m):
            def act(icon, item):
                self.cfg["mode"] = m
                save_cfg(self.cfg)
                SH.q.put(("mode",))
            return M(label, act, checked=lambda item: self.cfg["mode"] == m, radio=True)

        def lang_item(label, code):
            def act(icon, item):
                self.cfg["language"] = code
                save_cfg(self.cfg)
                SH.q.put(("lang",))
            if code == "auto":
                return M(label, act, checked=lambda item: self.cfg.get("language", "auto") not in langs, radio=True)
            return M(label, act, checked=lambda item: self.cfg.get("language", "auto") == code, radio=True)

        lang_menu = Menu(lang_item(t("menu_lang_auto"), "auto"), *[lang_item(n, c) for c, n in langs.items()])
        return Menu(
            M(t("menu_show"), lambda i, it: SH.q.put(("toggle",)), default=True),
            M(t("menu_refresh"), lambda i, it: open_usage_page()),
            M(t("menu_mode"), Menu(mode_item(t("menu_mode_auto"), "auto"), mode_item(t("menu_mode_web"), "web"),
                                   mode_item(t("menu_mode_code"), "code"))),
            M(t("menu_language"), lang_menu),
            M(t("menu_autostart"), self.on_autostart, checked=lambda it: is_autostart()),
            M(t("menu_help"), self.on_help),
            M(t("menu_uninstall"), self.on_uninstall),
            Menu.SEPARATOR,
            M(t("menu_quit"), lambda i, it: SH.q.put(("quit",))),
        )

    # ---- window
    def _block(self, parent):
        w = {"title": ttk.Label(parent, font=self.f_bold), "info": ttk.Label(parent, font=self.f_norm),
             "bar": ttk.Progressbar(parent, length=240, maximum=100), "reset": ttk.Label(parent, foreground="#666", font=self.f_norm)}
        for k in ("title", "info", "bar", "reset"):
            w[k].pack(anchor="w", pady=(0, 2) if k != "bar" else 2, fill="x" if k == "bar" else None)
        return w

    def _build_ui(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        for name in ("ok", "warn", "bad"):
            c = COLORS[name]
            style.configure(f"{name}.Horizontal.TProgressbar", troughcolor="#e6e6e6", background=c,
                            bordercolor="#e6e6e6", lightcolor=c, darkcolor=c, thickness=10)
        body = ttk.Frame(self.root, padding=10)
        body.pack()
        self.hdr = ttk.Label(body, font=self.f_head)
        self.hdr.pack(anchor="w", pady=(0, 4))
        self.w_session = self._block(body)
        ttk.Separator(body).pack(fill="x", pady=4)
        self.w_week = self._block(body)
        self.prod_frame = ttk.Frame(body)
        self.prod_frame.pack(fill="x", pady=(6, 0))
        self.warn_lbl = ttk.Label(body, foreground="#b45309", wraplength=240, font=self.f_norm)
        self.warn_lbl.pack(anchor="w", pady=(4, 0))
        self.status_lbl = ttk.Label(body, foreground="#666", wraplength=240, font=self.f_norm)
        self.status_lbl.pack(anchor="w", pady=(4, 0))
        self.open_btn = ttk.Button(body, command=open_usage_page)
        self.open_btn.pack(anchor="w", pady=(6, 0))

    def _fill(self, w, title, bar):
        w["title"].config(text=title)
        if not bar:
            w["info"].config(text="—")
            w["bar"]["value"] = 0
            w["reset"].config(text="")
            return
        pct = bar["pct"]
        w["info"].config(text=t("used_left", used=f"{pct:g}", left=f"{max(0.0, 100 - pct):g}"))
        w["bar"].config(style=f"{level(pct)}.Horizontal.TProgressbar")
        w["bar"]["value"] = pct
        w["reset"].config(text=reset_text(bar))

    def render(self):
        with SH.lock:
            u, rec = SH.usage, SH.received
        self.root.title(t("window_title"))
        self.open_btn.config(text=t("btn_open"))
        mode = self.cfg["mode"]
        self.hdr.config(text=t("hdr", view=VIEW_NAMES[self.view], mode=t("mode_auto") if mode == "auto" else t("mode_fixed")))
        self._fill(self.w_session, t("session"), u["session"] if u else None)
        self._fill(self.w_week, t("week"), u["week"] if u else None)

        rows = []
        if u:
            for name, pct in u["products"].items():
                if (self.view == "code") == ("claude code" in name.lower()):
                    rows.append((name, pct))
            for e in u["extra"]:
                rows.append((e["label"] or t("other_limit"), e["pct"]))
        sig = (self.view, CUR_LANG, tuple(rows))
        if sig != self._prod_sig:
            self._prod_sig = sig
            for c in self.prod_frame.winfo_children():
                c.destroy()
            if rows:
                ttk.Label(self.prod_frame, text=t("products"), font=self.f_bold).grid(row=0, column=0, columnspan=3, sticky="w")
            for i, (name, pct) in enumerate(rows, start=1):
                ttk.Label(self.prod_frame, text=name, font=self.f_norm, width=9).grid(row=i, column=0, sticky="w")
                b = ttk.Progressbar(self.prod_frame, length=110, maximum=100, value=pct,
                                    style=f"{level(pct)}.Horizontal.TProgressbar")
                b.grid(row=i, column=1, padx=6, pady=2)
                ttk.Label(self.prod_frame, text=f"{pct:g}%", font=self.f_norm).grid(row=i, column=2, sticky="e")

        self.warn_lbl.config(text=(u["warning"] if u else ""))
        if rec:
            age = int((datetime.now(timezone.utc) - rec).total_seconds() // 60)
            if age < 1:
                txt = t("upd_now")
            elif age < 60:
                txt = t("upd_ago", n=age)
            else:
                txt = t("upd_ago_h", h=age // 60, m=age % 60)
            stale = age >= int(self.cfg.get("stale_minutes", 60))
            if stale:
                txt += t("stale")
            self.status_lbl.config(text=txt, foreground="#b45309" if stale else "#666")
        else:
            self.status_lbl.config(text=t("no_data"), foreground="#b45309")

    def show(self, focus=True):
        self.render()
        self.root.update_idletasks()
        w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        self.root.geometry(f"+{self.root.winfo_screenwidth() - w - 16}+{self.root.winfo_screenheight() - h - 64}")
        self.root.deiconify()
        self.root.lift()
        if focus:
            self.root.focus_force()

    def toggle(self):
        if self.root.state() == "normal":
            self.root.withdraw()
        else:
            self.show()

    # ---- tray icon
    def update_icon(self):
        with SH.lock:
            u = SH.usage
        bars = [b for b in ((u or {}).get("session"), (u or {}).get("week")) if b]
        if bars:
            top = max(b["pct"] for b in bars)
            img = make_icon(str(int(round(top))), COLORS[level(top)])
            s = u["session"]["pct"] if u["session"] else 0
            w = u["week"]["pct"] if u["week"] else 0
            tip = t("tip", view=VIEW_NAMES[self.view], s=f"{s:g}", w=f"{w:g}")
        else:
            img, tip = make_icon("?", COLORS["none"]), t("tip_none")
        self.icon.icon = img
        self.icon.title = tip[:127]
        try:
            from PIL import ImageTk
            self._wicon = ImageTk.PhotoImage(img.resize((32, 32)))
            self.root.iconphoto(True, self._wicon)
        except Exception:
            pass

    # ---- notifications
    def alert(self, title, text, urgent=False):
        if winsound:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass
        try:
            self.icon.notify(text, title)
        except Exception:
            pass
        if urgent and self.root.state() != "normal":
            self.show(focus=False)  # pop up without taking the keyboard away from what you are typing

    def check_alerts(self):
        with SH.lock:
            u = SH.usage
        if not u:
            return
        ths = sorted(self.cfg["thresholds"])
        for key, name_key in (("session", "name_session"), ("week", "name_week")):
            b = u.get(key)
            if not b:
                continue
            crossed = [x for x in ths if b["pct"] >= x]
            for x in ths:
                if x not in crossed:
                    self.notified.discard((key, x))  # re-arm after the limit resets
            if crossed and (key, max(crossed)) not in self.notified:
                for x in crossed:
                    self.notified.add((key, x))
                self.alert(t("alert_title", name=t(name_key), pct=f"{b['pct']:g}"),
                           t("alert_body", left=f"{max(0.0, 100 - b['pct']):g}", reset=reset_text(b)),
                           urgent=max(crossed) >= 90)
        w = u.get("warning", "")
        if w and w != self.last_warn:
            self.last_warn = w
            self.alert(t("warn_title"), w, urgent=True)
        elif not w:
            self.last_warn = ""

    # ---- menu actions
    def on_autostart(self, icon, item):
        try:
            set_autostart(not is_autostart())
        except Exception:
            pass

    def on_help(self, icon, item):
        for p in (BASE_DIR / "docs" / f"README.{CUR_LANG}.txt", BASE_DIR / "docs" / "README.en.txt", BASE_DIR / "README.txt"):
            if p.exists():
                try:
                    os.startfile(str(p))
                except Exception:
                    pass
                return
        try:
            icon.notify(t("no_readme"), t("window_title"))
        except Exception:
            pass

    def on_uninstall(self, icon, item):
        bat = BASE_DIR / "uninstall.bat"
        try:
            if bat.exists():
                os.startfile(str(bat))  # asks for confirmation first; nothing is deleted yet
            else:
                icon.notify(t("no_uninstall"), t("window_title"))
        except Exception:
            pass

    # ---- loops
    def pump(self):
        while True:
            try:
                m = SH.q.get_nowait()
            except queue.Empty:
                break
            if m[0] == "quit":
                self.quit()
                return
            try:
                if m[0] == "usage":
                    self.render()
                    self.update_icon()
                    self.check_alerts()
                elif m[0] == "mode":
                    self.sync_view(force=True)
                elif m[0] == "lang":
                    self.apply_language()
                elif m[0] == "toggle":
                    self.toggle()
            except Exception:
                log_error()  # one bad update must never stop the loop
        self.root.after(200, self.pump)

    def apply_language(self):
        load_strings(self.cfg.get("language", "auto"))
        for f in (self.f_norm, self.f_bold, self.f_head):
            f.configure(family=FONT_FAMILY)
        self._prod_sig = None
        self.render()
        self.update_icon()
        self.icon.menu = self.build_menu()
        self.icon.update_menu()

    def sync_view(self, force=False):
        mode = self.cfg["mode"]
        new = self.view
        if mode in VIEW_NAMES:
            new = mode
        else:
            v = classify(*foreground(), self.cfg)
            if v:
                new = v
        if new != self.view or force:
            self.view = new
            self.update_icon()
            self.render()

    def tick(self):
        try:
            self.sync_view()
            if self.root.state() == "normal":
                self.render()
        except Exception:
            log_error()
        self.root.after(1000, self.tick)

    def quit(self):
        try:
            self.icon.stop()
        except Exception:
            pass
        threading.Thread(target=self.server.shutdown, daemon=True).start()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    TrayApp().run()
