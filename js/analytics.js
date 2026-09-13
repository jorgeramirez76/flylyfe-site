/* FLYLYFE analytics loader.
   Fill in the IDs below to activate. While both are empty this file does nothing
   (no cookies, no network requests, no consent bar). */
(function () {
  var CFG = { ga4: 'G-QWLTKE091E', metaPixel: '' }; // e.g. ga4: 'G-XXXXXXXXXX', metaPixel: '123456789012345'
  if (!CFG.ga4 && !CFG.metaPixel) return;
  var KEY = 'flylyfe_consent', consent = null;
  try { consent = localStorage.getItem(KEY); } catch (e) {}
  function loadGA() {
    if (!CFG.ga4) return;
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CFG.ga4; document.head.appendChild(s);
    window.dataLayer = window.dataLayer || []; window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date()); window.gtag('config', CFG.ga4, { anonymize_ip: true });
  }
  function loadMeta() {
    if (!CFG.metaPixel) return;
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init', CFG.metaPixel); window.fbq('track', 'PageView');
  }
  function activate() { loadGA(); loadMeta(); }
  if (consent === 'yes') { activate(); return; }
  if (consent === 'no') return;
  function showBar() {
    var bar = document.createElement('div'); bar.id = 'flyConsent'; bar.setAttribute('role', 'dialog'); bar.setAttribute('aria-label', 'Cookie consent');
    bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#111;color:#eee;font:13px/1.5 Archivo,Arial,sans-serif;padding:14px 18px;display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap;border-top:1px solid #333';
    bar.innerHTML = '<span>We use cookies for analytics and to measure ads. <a href="/privacy.html" style="color:#d9b54b">Privacy</a></span>' +
      '<button id="flyConsentYes" type="button" style="background:#d9b54b;color:#111;border:0;padding:8px 14px;font-weight:700;cursor:pointer">Accept</button>' +
      '<button id="flyConsentNo" type="button" style="background:transparent;color:#eee;border:1px solid #555;padding:8px 14px;cursor:pointer">Decline</button>';
    document.body.appendChild(bar);
    document.getElementById('flyConsentYes').onclick = function () { try { localStorage.setItem(KEY, 'yes'); } catch (e) {} bar.remove(); activate(); };
    document.getElementById('flyConsentNo').onclick = function () { try { localStorage.setItem(KEY, 'no'); } catch (e) {} bar.remove(); };
  }
  if (document.body) showBar(); else document.addEventListener('DOMContentLoaded', showBar);
})();
