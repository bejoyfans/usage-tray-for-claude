// Claude Usage Bridge - background script (Chrome / Edge / Opera / Brave / Vivaldi / Firefox)
// Passive by design: it never opens pages or polls claude.ai by itself.
// When YOU open claude.ai > Settings > Usage, the content script reads the numbers shown there
// and this script forwards them to the tray program on this PC (127.0.0.1 only).
// Clicking the toolbar button simply opens the usage page for you.

const api = typeof browser !== 'undefined' ? browser : chrome;
const BASE = 'http://127.0.0.1:47821';
const USAGE_URL = 'https://claude.ai/settings/usage';

api.action.onClicked.addListener(() => {
  api.tabs.create({ url: USAGE_URL, active: true });
});

api.runtime.onMessage.addListener((msg) => {
  if (!msg || msg.type !== 'usage') return;
  fetch(BASE + '/usage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(msg.data),
  }).catch(() => {}); // tray program not running: nothing to do
});
