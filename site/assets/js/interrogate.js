(function () {
  'use strict';

  var state = { records: [], filtered: [] };
  var els = {};

  function text(value) {
    return (value == null ? '' : String(value)).toLowerCase();
  }

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function get(id) { return document.getElementById(id); }

  function matches(record) {
    var query = text(els.search && els.search.value).trim();
    var target = els.target && els.target.value;
    var kind = els.kind && els.kind.value;
    var category = els.category && els.category.value;

    if (target && !(record.target_ids || []).includes(target)) return false;
    if (kind && record.kind !== kind) return false;
    if (category && record.category !== category) return false;

    if (query) {
      var haystack = [
        record.title,
        record.category,
        record.kind,
        (record.targets || []).join(' '),
        record.claim_readiness,
        record.match_reason
      ].join(' ').toLowerCase();
      if (haystack.indexOf(query) === -1) return false;
    }
    return true;
  }

  function render() {
    state.filtered = state.records.filter(matches);
    var total = state.records.length;
    var shown = state.filtered.length;
    if (els.summary) {
      els.summary.textContent = shown + ' of ' + total + ' public-safe records shown. Results are screening/provenance records only.';
    }
    if (!els.results) return;
    if (!shown) {
      els.results.innerHTML = '<article class="interrogate-result"><h3>No matching public-safe records</h3><p class="interrogate-boundary">Try a broader search or reset the filters. Absence here does not mean absence from the protected evidence register.</p></article>';
      return;
    }
    els.results.innerHTML = state.filtered.slice(0, 80).map(function (record) {
      var href = record.link ? esc(record.link) : '#';
      var targetText = (record.targets || []).join(', ') || 'No target label';
      return '<article class="interrogate-result">' +
        '<h3>' + (record.link ? '<a href="' + href + '" target="_blank" rel="noopener noreferrer">' + esc(record.title) + '</a>' : esc(record.title)) + '</h3>' +
        '<div class="interrogate-meta">' +
          '<span class="interrogate-pill">' + esc(record.kind || 'Evidence') + '</span>' +
          '<span class="interrogate-pill">' + esc(record.category || 'other') + '</span>' +
          '<span class="interrogate-pill">' + esc(targetText) + '</span>' +
          '<span class="interrogate-pill">' + esc(record.claim_readiness || 'candidate_only') + '</span>' +
          (record.modified ? '<span class="interrogate-pill">' + esc(record.modified) + '</span>' : '') +
        '</div>' +
        '<p class="interrogate-boundary">' + esc(record.boundary || 'Public-safe screening record only.') + '</p>' +
      '</article>';
    }).join('');
  }

  function applyPreset(preset) {
    if (preset === 'reset') {
      if (els.search) els.search.value = '';
      if (els.kind) els.kind.value = '';
      if (els.category) els.category.value = '';
      if (els.target) els.target.value = '';
    }
    if (preset === 'permit' && els.kind) els.kind.value = 'Permits / licences';
    if (preset === 'inspection' && els.kind) els.kind.value = 'Inspections / compliance';
    if (preset === 'monitoring' && els.kind) els.kind.value = 'Monitoring / data';
    if (preset === 'reports' && els.kind) els.kind.value = 'Reports / assessments';
    if (preset === 'gaps') {
      if (els.search) els.search.value = '';
      if (els.kind) els.kind.value = '';
      if (els.category) els.category.value = '';
    }
    render();
  }

  function init(payload) {
    state.records = Array.isArray(payload.records) ? payload.records : [];
    els.search = get('aq26-search');
    els.target = get('aq26-target');
    els.kind = get('aq26-kind');
    els.category = get('aq26-category');
    els.summary = get('aq26-interrogate-summary');
    els.results = get('aq26-results');

    [els.search, els.target, els.kind, els.category].forEach(function (el) {
      if (el) el.addEventListener('input', render);
      if (el) el.addEventListener('change', render);
    });
    document.querySelectorAll('[data-preset]').forEach(function (button) {
      button.addEventListener('click', function () {
        applyPreset(button.getAttribute('data-preset'));
      });
    });
    render();
  }

  fetch('/assets/data/public-evidence.json', { cache: 'no-store' })
    .then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    })
    .then(init)
    .catch(function () {
      var summary = get('aq26-interrogate-summary');
      var results = get('aq26-results');
      if (summary) summary.textContent = 'The public evidence index could not be loaded. Use the map and target dossier pages instead.';
      if (results) results.innerHTML = '<article class="interrogate-result"><h3>Evidence index unavailable</h3><p class="interrogate-boundary">The generated JSON index is missing or blocked. The public build guard should catch this on the next run.</p></article>';
    });
})();
