(() => {
  const statusEl = document.getElementById('status');

  async function poll() {
    try {
      const res = await fetch(window.STATUS_ENDPOINT, { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const text = window.PROCESSING_TEXTS[data.status] || 'Processing…';
      if (statusEl) statusEl.textContent = text;

      if (data.status === 'completed') {
        setTimeout(() => { window.location.replace(window.DESTINATION); }, 500);
        return;
      }
      if (data.status === 'error') {
        return; // stop polling on error
      }
    } catch (e) {
      if (statusEl) statusEl.textContent = 'Network error… retrying';
    }
    setTimeout(poll, 2000);
  }

  if (window.PAGE_CONTEXT === 'processing') {
    poll();
  }
})();

