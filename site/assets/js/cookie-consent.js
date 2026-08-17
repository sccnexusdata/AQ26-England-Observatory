(function () {
  'use strict';

  var STORAGE_KEY = 'aq26_cookie_choice';
  var banner = document.getElementById('cookie-banner');
  var gaId = document.documentElement.getAttribute('data-ga-id') || window.AQ26_GA_MEASUREMENT_ID || '';

  function hideBanner() {
    if (banner) {
      banner.classList.remove('show');
      banner.setAttribute('hidden', 'hidden');
      banner.style.display = '';
    }
  }

  function showBanner() {
    if (banner) {
      banner.removeAttribute('hidden');
      banner.style.display = '';
      banner.classList.add('show');
    }
  }

  function ensureGtag() {
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== 'function') {
      window.gtag = function gtag(){ window.dataLayer.push(arguments); };
    }
  }

  function grantAnalytics() {
    if (!gaId) return;
    ensureGtag();
    window.gtag('consent', 'update', {
      'analytics_storage': 'granted',
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied'
    });
    window.gtag('config', gaId, { 'anonymize_ip': true });
  }

  function denyAnalytics() {
    ensureGtag();
    window.gtag('consent', 'update', {
      'analytics_storage': 'denied',
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied'
    });
  }

  function setChoice(choice) {
    try { localStorage.setItem(STORAGE_KEY, choice); } catch (e) {}
    if (choice === 'accept') grantAnalytics();
    if (choice === 'essential') denyAnalytics();
    hideBanner();
  }

  var existing = null;
  try { existing = localStorage.getItem(STORAGE_KEY); } catch (e) {}

  if (existing === 'accept') {
    grantAnalytics();
    hideBanner();
    return;
  }

  if (existing === 'essential') {
    denyAnalytics();
    hideBanner();
    return;
  }

  if (!banner) return;

  showBanner();
  banner.addEventListener('click', function (event) {
    var button = event.target.closest('[data-cookie-choice]');
    if (!button) return;
    setChoice(button.getAttribute('data-cookie-choice'));
  });
})();
