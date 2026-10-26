function whaxonRenderMessageRow(container, colspan, message, tone) {
  if (!container) return;
  container.replaceChildren();
  const tr = document.createElement('tr');
  const td = document.createElement('td');
  td.colSpan = colspan;
  td.style.padding = '16px';
  td.style.color = tone === 'muted' ? 'var(--text-dim)' : 'var(--critical)';
  td.textContent = String(message);
  tr.appendChild(td);
  container.appendChild(tr);
}

(function () {
  const app = document.getElementById('app');
  const palette = document.getElementById('palette');
  const paletteInput = document.getElementById('palette-input');
  const slideover = document.getElementById('slideover');
  const notifPanel = document.getElementById('notif-panel');
  const kbdLegend = document.getElementById('kbd-legend');
  const bulkBar = document.getElementById('bulk-bar');
  const bulkCount = document.getElementById('bulk-count');
  const selectAll = document.getElementById('select-all');

  // page navigation
  document.querySelectorAll('.sb-item[data-page]').forEach(item => {
    item.addEventListener('click', () => {
      const p = item.dataset.page;
      document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
      const target = document.getElementById('page-' + p) || document.getElementById('page-findings');
      target.classList.add('active');
      document.querySelectorAll('.sb-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      document.getElementById('crumb-here').textContent = p.charAt(0).toUpperCase() + p.slice(1);
    });
  });

  // sidebar collapse
  document.getElementById('collapse-btn').addEventListener('click', () => app.classList.toggle('collapsed'));

  // density
  document.querySelectorAll('.density-toggle button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.body.dataset.density = btn.dataset.density;
      document.querySelectorAll('.density-toggle button').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
    });
  });

  // findings slide-over
  document.querySelectorAll('#findings-table tbody tr').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('.checkbox-col') || e.target.closest('.copy-btn')) return;
      document.querySelectorAll('#findings-table tbody tr').forEach(r => r.classList.remove('selected'));
      row.classList.add('selected');
      slideover.classList.add('open');
      document.getElementById('so-title').textContent = row.querySelector('.title').textContent;
    });
  });
  window.closeSlideover = () => slideover.classList.remove('open');

  // bulk selection
  function updateBulk() {
    const allBoxes = Array.from(document.querySelectorAll('#findings-table .row-cb'));
    const checked = allBoxes.filter(cb => cb.checked).length;
    if (bulkCount) bulkCount.textContent = checked;
    if (bulkBar) {
      bulkBar.hidden = checked === 0;
      bulkBar.classList.toggle('on', checked > 0);
    }
    if (selectAll) {
      const visibleBoxes = Array.from(document.querySelectorAll('#findings-table tbody tr[data-job-id]'))
        .filter(row => row.style.display !== 'none')
        .map(row => row.querySelector('.row-cb')).filter(Boolean);
      const visibleChecked = visibleBoxes.filter(cb => cb.checked).length;
      selectAll.checked = visibleBoxes.length > 0 && visibleChecked === visibleBoxes.length;
      selectAll.indeterminate = visibleChecked > 0 && visibleChecked < visibleBoxes.length;
      selectAll.disabled = visibleBoxes.length === 0;
    }
  }
  const findingsTable = document.getElementById('findings-table');
  if (findingsTable) findingsTable.addEventListener('change', event => {
    if (event.target && event.target.matches('.row-cb')) updateBulk();
  });
  if (selectAll) selectAll.addEventListener('change', () => {
    document.querySelectorAll('#findings-table tbody tr[data-job-id]').forEach(row => {
      if (row.style.display !== 'none') {
        const cb = row.querySelector('.row-cb');
        if (cb) cb.checked = selectAll.checked;
      }
    });
    updateBulk();
  });
  const bulkClear = document.getElementById('bulk-clear-btn');
  if (bulkClear) bulkClear.addEventListener('click', () => {
    document.querySelectorAll('#findings-table .row-cb').forEach(cb => { cb.checked = false; });
    if (selectAll) { selectAll.checked = false; selectAll.indeterminate = false; }
    updateBulk();
  });

  // copy buttons
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const text = btn.closest('td').querySelector('.target, .mono')?.textContent?.trim();
      if (text) navigator.clipboard?.writeText(text);
    });
  });

  // Command palette: navigation plus live finding/tool search. Selecting a result
  // navigates or opens evidence; it never launches a security tool by itself.
  const paletteResults = palette.querySelector('.palette-results');
  const palettePages = [
    {id: 'findings', label: 'Findings', detail: 'Review and validate findings'},
    {id: 'run', label: 'Run', detail: 'Select a tool and target'},
    {id: 'scope', label: 'Scope', detail: 'Review authorization rules'},
    {id: 'report', label: 'Report', detail: 'Generate an engagement report'},
    {id: 'retest', label: 'Retest', detail: 'Recheck verified findings'},
    {id: 'approvals', label: 'Approvals', detail: 'Review candidate findings'},
    {id: 'sessions', label: 'Sessions', detail: 'View active sessions'},
    {id: 'graph', label: 'Attack Surface', detail: 'View attack-surface status'},
    {id: 'monitoring', label: 'Coverage', detail: 'Review skipped coverage'},
    {id: 'catalog', label: 'Catalog', detail: 'Browse available tools'}
  ];

  function addPaletteItem(group, label, detail, action) {
    const item = document.createElement('div');
    item.className = 'palette-item';
    item.setAttribute('role', 'button');
    item.tabIndex = 0;
    const title = document.createElement('span');
    title.textContent = label;
    const description = document.createElement('span');
    description.className = 'palette-detail';
    description.textContent = detail || '';
    item.appendChild(title);
    item.appendChild(description);
    const choose = () => {
      action();
      palette.classList.remove('open');
      paletteInput.value = '';
    };
    item.addEventListener('click', choose);
    item.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        choose();
      }
    });
    group.appendChild(item);
  }

  function renderPalette(query) {
    if (!paletteResults) return;
    const term = (query || '').trim().toLowerCase();
    paletteResults.innerHTML = '';
    const addGroup = label => {
      const heading = document.createElement('div');
      heading.className = 'palette-group';
      heading.textContent = label;
      paletteResults.appendChild(heading);
      return paletteResults;
    };
    const navMatches = palettePages.filter(p => !term || (p.label + ' ' + p.detail).toLowerCase().includes(term));
    if (navMatches.length) {
      const group = addGroup('Navigate');
      navMatches.forEach(p => addPaletteItem(group, p.label, p.detail, () => {
        document.querySelector('.sb-item[data-page="' + p.id + '"]')?.click();
      }));
    }
    if (term) {
      const findingMatches = (window._whaxonFindings || []).filter(f =>
        [f.title, f.target, f.source, f.status].some(value => String(value || '').toLowerCase().includes(term))
      ).slice(0, 8);
      if (findingMatches.length) {
        const group = addGroup('Findings');
        findingMatches.forEach(f => addPaletteItem(group, f.title, [f.target, f.source, f.status].filter(Boolean).join(' · '), () => {
          document.querySelector('#page-findings .chip[data-filter="all"]')?.click();
          document.querySelector('.sb-item[data-page="findings"]')?.click();
          const row = Array.from(document.querySelectorAll('#findings-tbody tr')).find(el =>
            el.dataset.jobId === f.job_id && el.dataset.seq === String(f.seq)
          );
          if (row) {
            row.style.display = '';
            row.click();
          }
        }));
      }
      const toolMatches = (window._whaxonTools || []).filter(t =>
        [t.id, t.name, t.category, t.description].some(value => String(value || '').toLowerCase().includes(term))
      ).slice(0, 8);
      if (toolMatches.length) {
        const group = addGroup('Tools');
        toolMatches.forEach(tool => addPaletteItem(group, tool.name || tool.id, tool.category || tool.binary || '', () => {
          document.querySelector('.sb-item[data-page="run"]')?.click();
          const item = Array.from(document.querySelectorAll('#run-catalog .tool-item')).find(el => el.dataset.toolId === tool.id);
          if (item) item.click();
        }));
      }
    }
    if (!paletteResults.querySelector('.palette-item')) {
      const empty = document.createElement('div');
      empty.className = 'palette-item';
      empty.textContent = term ? 'No matching pages, findings, or tools.' : 'Type to search pages, findings, and tools.';
      paletteResults.appendChild(empty);
    }
  }

  document.getElementById('palette-trigger').addEventListener('click', () => {
    renderPalette(paletteInput.value);
    palette.classList.add('open');
    paletteInput.focus();
  });
  paletteInput.addEventListener('input', () => renderPalette(paletteInput.value));
  paletteInput.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
      event.preventDefault();
      paletteResults.querySelector('.palette-item[role="button"]')?.click();
    }
  });

  // notifications
  document.getElementById('notif-trigger').addEventListener('click', e => { e.stopPropagation(); notifPanel.classList.toggle('open'); });

  // shortcuts
  document.getElementById('help-trigger').addEventListener('click', () => kbdLegend.classList.add('open'));

  // workspace

  // table sort


  // chips
  // Functional chips manage their own state; only decorative chips use the generic toggle.
  document.querySelectorAll('.chip:not([data-filter]):not([data-intel-source])').forEach(c => c.addEventListener('click', () => c.classList.toggle('on')));

  // accordion
  document.querySelectorAll('.acc-head').forEach(h => h.addEventListener('click', () => h.parentElement.classList.toggle('open')));

  // graph nodes
  document.querySelectorAll('.asg-node').forEach(node => {
    node.addEventListener('click', () => {
      document.querySelectorAll('.sb-item').forEach(i => i.classList.remove('active'));
      document.querySelector('.sb-item[data-page="findings"]')?.classList.add('active');
      document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
      document.getElementById('page-findings').classList.add('active');
      document.getElementById('crumb-here').textContent = 'Findings';
    });
  });

  // outside click closes
  document.addEventListener('click', e => {
    if (!notifPanel.contains(e.target) && e.target.id !== 'notif-trigger') notifPanel.classList.remove('open');
  });

  // Keyboard shortcuts shown in the help legend are implemented here.
  let goPending = false;
  let goTimer = null;
  const isTyping = () => {
    const el = document.activeElement;
    return el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
  };
  function navigateTo(page) {
    document.querySelector('.sb-item[data-page="' + page + '"]')?.click();
  }
  document.addEventListener('keydown', e => {
    const key = e.key.toLowerCase();
    if ((e.metaKey || e.ctrlKey) && key === 'k') {
      e.preventDefault();
      renderPalette(paletteInput.value);
      palette.classList.toggle('open');
      if (palette.classList.contains('open')) paletteInput.focus();
      return;
    }
    if ((e.metaKey || e.ctrlKey) && key === 'b') {
      e.preventDefault();
      app.classList.toggle('collapsed');
      return;
    }
    if (e.key === 'Escape') {
      palette.classList.remove('open');
      closeSlideover();
      notifPanel.classList.remove('open');
      kbdLegend.classList.remove('open');
      document.querySelectorAll('.scope-modal, .confirm-modal').forEach(m => m.classList.remove('open'));
      goPending = false;
      return;
    }
    if (!isTyping() && e.key === '/') {
      e.preventDefault();
      renderPalette('');
      palette.classList.add('open');
      paletteInput.focus();
      return;
    }
    if (!isTyping() && goPending) {
      goPending = false;
      if (goTimer) clearTimeout(goTimer);
      if (key === 'f') navigateTo('findings');
      else if (key === 'r') navigateTo('run');
      else if (key === 'p') navigateTo('report');
      return;
    }
    if (!isTyping() && key === 'g') {
      goPending = true;
      if (goTimer) clearTimeout(goTimer);
      goTimer = setTimeout(() => { goPending = false; }, 1200);
      return;
    }
    if (!isTyping() && key === 'n') {
      navigateTo('run');
      return;
    }
    if (!isTyping() && key === 'd') {
      const current = document.body.dataset.density === 'compact' ? 'compact' : 'comfortable';
      const next = current === 'compact' ? 'comfortable' : 'compact';
      document.body.dataset.density = next;
      document.querySelectorAll('.density-toggle button').forEach(btn => btn.classList.toggle('on', btn.dataset.density === next));
      return;
    }
    if (e.key === '?' && !isTyping()) kbdLegend.classList.toggle('open');
  });

  palette.addEventListener('click', e => { if (e.target === palette) palette.classList.remove('open'); });
})();


// ---- Scope page wiring ----
(function () {
  const rulesEl = document.getElementById('scope-rules');
  const countEl = document.getElementById('scope-count');
  const inputEl = document.getElementById('scope-check-input');
  const btnEl = document.getElementById('scope-check-btn');
  const resultEl = document.getElementById('scope-check-result');
  if (!rulesEl || !countEl) return;

  function row(label, value) {
    const d = document.createElement('div');
    d.className = 'kv';
    const k = document.createElement('span');
    k.className = 'k';
    k.textContent = label;
    const v = document.createElement('span');
    v.className = 'v';
    v.textContent = value;
    d.appendChild(k);
    d.appendChild(v);
    return d;
  }

  function classify(rule) {
    if (rule.includes('/')) return 'Network';
    if (/^\[[0-9a-fA-F:]+\]$/.test(rule) || /^[0-9a-fA-F]{0,4}(:[0-9a-fA-F]{0,4}){2,}$/.test(rule)) return 'Address';
    if (/:[0-9]+$/.test(rule)) return 'Host:port';
    if (/^[0-9.]+$/.test(rule)) return 'Address';
    return 'Host';
  }

  function render(data) {
    rulesEl.innerHTML = '';
    const eng = data.engagement || '(unnamed)';
    rulesEl.appendChild(row('Engagement', eng));
    const engagementName = document.querySelector('.sb-engagement .name');
    if (engagementName) engagementName.textContent = eng;
    const crumb = document.querySelector('.crumb');
    if (crumb && crumb.firstChild) crumb.firstChild.textContent = eng + ' ';
    const list = data.in_scope || [];
    countEl.textContent = list.length;
    list.forEach(rule => rulesEl.appendChild(row(classify(rule), rule)));
    const out = data.out_of_scope || [];
    out.forEach(rule => {
      const d = row('Excluded', rule);
      d.querySelector('.v').style.color = 'var(--critical)';
      rulesEl.appendChild(d);
    });
    if (data.notes) {
      const n = document.createElement('div');
      n.style.marginTop = '12px';
      n.style.fontSize = 'var(--t-xs)';
      n.style.color = 'var(--text-mute)';
      n.style.fontFamily = 'var(--font-mono)';
      n.textContent = data.notes;
      rulesEl.appendChild(n);
    }
  }

  function loadScope() {
    fetch('/api/scope')
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => render(data))
      .catch(err => {
        rulesEl.innerHTML = '';
        rulesEl.appendChild(row('Error', 'Failed to load scope: ' + err));
        countEl.textContent = '—';
      });
  }

  function showResult(html, kind) {
    resultEl.innerHTML = '';
    const d = document.createElement('div');
    d.style.marginTop = '16px';
    d.style.padding = '12px';
    d.style.borderRadius = 'var(--r-md)';
    d.style.fontSize = 'var(--t-sm)';
    if (kind === 'ok') {
      d.style.background = 'var(--low-dim)';
      d.style.color = 'var(--low)';
    } else if (kind === 'denied') {
      d.style.background = 'var(--critical-dim)';
      d.style.color = 'var(--critical)';
    } else {
      d.style.background = 'var(--bg-elev-2)';
      d.style.color = 'var(--text-dim)';
    }
    d.textContent = html;
    resultEl.appendChild(d);
  }

  function checkScope() {
    const target = (inputEl.value || '').trim();
    if (!target) {
      showResult('Enter a target first.', 'warn');
      return;
    }
    btnEl.disabled = true;
    btnEl.textContent = 'Checking…';
    showResult('Checking target against the active scope…', 'warn');
    fetch('/api/scope/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: target })
    })
      .then(async r => {
        let data = {};
        try { data = await r.json(); } catch (_) {}
        if (!r.ok) throw new Error(data.error || ('HTTP ' + r.status));
        return data;
      })
      .then(data => {
        if (data.allowed === true || data.in_scope === true) {
          const reason = data.reason || data.matched_rule || 'matched in-scope rule';
          showResult('✓ ' + target + ' is in scope (' + reason + '). This check does not start a scan.', 'ok');
        } else {
          const reason = data.reason || 'no matching in-scope rule';
          showResult('✗ ' + target + ' is not confirmed in scope (' + reason + '). WHAXON will block the run.', 'denied');
        }
      })
      .catch(err => showResult('Scope check failed closed: ' + String(err && err.message || err) + '. Do not run this target until scope can be confirmed.', 'warn'))
      .finally(() => { btnEl.disabled = false; btnEl.textContent = 'Check scope'; });
  }

  if (btnEl) btnEl.addEventListener('click', checkScope);
  if (inputEl) inputEl.addEventListener('keydown', e => { if (e.key === 'Enter') checkScope(); });

  const scopeNav = document.querySelector('.sb-item[data-page="scope"]');
  if (scopeNav) scopeNav.addEventListener('click', loadScope);

  document.addEventListener('DOMContentLoaded', loadScope);
  if (document.readyState !== 'loading') loadScope();
})();


// ---- Findings page wiring ----
(function () {
  const tbody = document.getElementById('findings-tbody');
  if (!tbody) return;

  let sortKey = 'severity';
  let sortAsc = true;
  let activeFilter = 'all';

  document.addEventListener('whaxon:findings-resort', () => {
    renderTable(sortRows(window._whaxonFindings || [], sortKey, sortAsc));
    applyFilter();
  });

  const filterChips = Array.from(document.querySelectorAll('#page-findings .toolbar .chip[data-filter]'));
  filterChips.forEach(chip => chip.addEventListener('click', () => {
    activeFilter = chip.dataset.filter || 'all';
    filterChips.forEach(item => {
      const active = item === chip;
      item.classList.toggle('on', active);
      item.setAttribute('aria-pressed', String(active));
    });
    applyFilter();
  }));

  function applyFilter() {
    const oldEmpty = tbody.querySelector('tr[data-filter-empty]');
    if (oldEmpty) oldEmpty.remove();
    const rows = Array.from(tbody.querySelectorAll('tr[data-job-id]'));
    rows.forEach(tr => {
      const severity = tr.dataset.severity || 'info';
      const status = tr.dataset.status || 'candidate';
      const matches = activeFilter === 'all'
        || (activeFilter === 'low' && (severity === 'low' || severity === 'info'))
        || (['critical', 'high', 'medium'].includes(activeFilter) && severity === activeFilter)
        || (['verified', 'candidate'].includes(activeFilter) && status === activeFilter);
      tr.style.display = matches ? '' : 'none';
    });
    if (rows.length && !rows.some(row => row.style.display !== 'none')) {
      const row = document.createElement('tr');
      row.dataset.filterEmpty = 'true';
      const cell = document.createElement('td');
      cell.colSpan = 6;
      cell.className = 'findings-empty';
      cell.setAttribute('role', 'status');
      cell.textContent = 'No findings match this filter.';
      row.appendChild(cell);
      tbody.appendChild(row);
    }
    updateSelection();
  }

  function updateFilterCounts(rows) {
    const counts = {
      all: rows.length,
      critical: rows.filter(f => f.severity === 'critical').length,
      high: rows.filter(f => f.severity === 'high').length,
      medium: rows.filter(f => f.severity === 'medium').length,
      low: rows.filter(f => f.severity === 'low' || f.severity === 'info').length,
      verified: rows.filter(f => f.status === 'verified').length,
      candidate: rows.filter(f => f.status === 'candidate').length
    };
    Object.entries(counts).forEach(([key, value]) => {
      const el = document.getElementById('filter-count-' + key);
      if (el) el.textContent = String(value);
    });
  }

  document.querySelectorAll('#findings-table thead th[data-sort]').forEach(th => {
    th.tabIndex = 0;
    th.setAttribute('role', 'button');
    th.setAttribute('aria-sort', th.dataset.sort === sortKey ? 'ascending' : 'none');
    const sort = () => {
      const key = th.dataset.sort;
      if (key === sortKey) sortAsc = !sortAsc;
      else { sortKey = key; sortAsc = true; }
      document.querySelectorAll('#findings-table thead th[data-sort]').forEach(x => {
        x.classList.toggle('sorted', x === th);
        x.setAttribute('aria-sort', x === th ? (sortAsc ? 'ascending' : 'descending') : 'none');
        const icon = x.querySelector('.sort');
        if (icon) icon.textContent = x === th ? (sortAsc ? '▴' : '▾') : '·';
      });
      document.dispatchEvent(new CustomEvent('whaxon:findings-resort'));
    };
    th.addEventListener('click', sort);
    th.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sort(); } });
  });
  const summaryEl = document.getElementById('findings-summary');
  const donutSummary = document.getElementById('donut-summary');

  const SEV_ORDER = ['critical', 'high', 'medium', 'low', 'info'];
  const SEV_PILL = {
    critical: 'pill-critical',
    high: 'pill-high',
    medium: 'pill-medium',
    low: 'pill-low',
    info: 'pill-info'
  };
  const SEV_LABEL = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    info: 'Info'
  };

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function renderKpis(sev) {
    setText('kpi-critical', sev.critical || 0);
    setText('kpi-high', sev.high || 0);
    setText('kpi-medium', sev.medium || 0);
    setText('kpi-low', (sev.low || 0) + (sev.info || 0));
    setText('legend-critical', sev.critical || 0);
    setText('legend-high', sev.high || 0);
    setText('legend-medium', sev.medium || 0);
    setText('legend-low', (sev.low || 0) + (sev.info || 0));
  }

  function renderDonut(sev) {
    const total = (sev.critical || 0) + (sev.high || 0) + (sev.medium || 0) + (sev.low || 0) + (sev.info || 0);
    const map = [
      ['donut-critical', sev.critical || 0],
      ['donut-high', sev.high || 0],
      ['donut-medium', sev.medium || 0],
      ['donut-low', (sev.low || 0) + (sev.info || 0)]
    ];
    if (total === 0) {
      map.forEach(([id]) => {
        const c = document.getElementById(id);
        if (c) c.setAttribute('stroke-dasharray', '0 100');
      });
      return;
    }
    let offset = 25;
    map.forEach(([id, count]) => {
      const pct = (count / total) * 100;
      const c = document.getElementById(id);
      if (c) {
        c.setAttribute('stroke-dasharray', pct.toFixed(2) + ' ' + (100 - pct).toFixed(2));
        c.setAttribute('stroke-dashoffset', offset.toFixed(2));
      }
      offset -= pct;
    });
  }

  function flattenFindings(jobs) {
    const out = [];
    (jobs || []).forEach(entry => {
      const job = entry.job || {};
      (entry.findings || []).forEach(f => {
        out.push({
          severity: (f.severity || 'info').toLowerCase(),
          title: f.title || f.kind || f.raw_line || '(finding)',
          target: job.target || f.target || '',
          source: f.source || job.tool || '',
          status: f.verification_status || f.status || 'candidate',
          verified_by: f.verified_by || 'engine',
          job_id: job.id || '',
          seq: f.seq || 0,
          _raw: f,
          _job: job
        });
      });
    });
    out.sort((a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity));
    return out;
  }

  function updateSelection() {
    const selected = Array.from(tbody.querySelectorAll('.row-cb:checked'));
    const bar = document.getElementById('bulk-bar');
    const count = document.getElementById('bulk-count');
    if (count) count.textContent = String(selected.length);
    if (bar) {
      bar.hidden = selected.length === 0;
      bar.classList.toggle('on', selected.length > 0);
    }
    const selectAll = document.getElementById('select-all');
    const visibleBoxes = Array.from(tbody.querySelectorAll('tr[data-job-id]'))
      .filter(row => row.style.display !== 'none')
      .map(row => row.querySelector('.row-cb')).filter(Boolean);
    const visibleSelected = visibleBoxes.filter(box => box.checked).length;
    if (selectAll) {
      selectAll.checked = visibleBoxes.length > 0 && visibleSelected === visibleBoxes.length;
      selectAll.indeterminate = visibleSelected > 0 && visibleSelected < visibleBoxes.length;
      selectAll.disabled = visibleBoxes.length === 0;
    }
  }

  function selectedFindings() {
    const keys = new Set(Array.from(tbody.querySelectorAll('.row-cb:checked'))
      .map(box => {
        const row = box.closest('tr');
        return row ? row.dataset.jobId + ':' + row.dataset.seq : '';
      }));
    return (window._whaxonFindings || []).filter(f => keys.has(f.job_id + ':' + f.seq));
  }

  function renderSurface(findings) {
    const list = document.getElementById('findings-surface-list');
    const summary = document.getElementById('findings-surface-summary');
    if (!list) return;
    const counts = new Map();
    findings.forEach(f => {
      const target = (f.target || '').trim();
      if (target) counts.set(target, (counts.get(target) || 0) + 1);
    });
    const entries = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 6);
    list.replaceChildren();
    if (summary) summary.textContent = counts.size
      ? counts.size + ' target(s) represented in loaded findings; not a network discovery graph.'
      : 'No target information is available in the loaded findings.';
    if (!entries.length) {
      const empty = document.createElement('p');
      empty.className = 'card-sub';
      empty.textContent = 'No observed targets to summarize yet.';
      list.appendChild(empty);
      return;
    }
    entries.forEach(([target, count]) => {
      const item = document.createElement('div');
      item.className = 'surface-list-item';
      const name = document.createElement('span');
      name.className = 'mono';
      name.textContent = target;
      const total = document.createElement('span');
      total.className = 'pill pill-info';
      total.textContent = count + (count === 1 ? ' finding' : ' findings');
      item.append(name, total);
      list.appendChild(item);
    });
  }

  const exportSelected = document.getElementById('bulk-export-btn');
  if (exportSelected) exportSelected.addEventListener('click', () => {
    const rows = selectedFindings();
    if (!rows.length) return;
    const payload = rows.map(f => ({
      severity: f.severity, title: f.title, target: f.target, source: f.source,
      status: f.status, job_id: f.job_id, sequence: f.seq, finding: f._raw
    }));
    const blob = new Blob([JSON.stringify({ exported_at: new Date().toISOString(), count: payload.length, findings: payload }, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'whaxon-selected-findings.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  function renderTable(findings) {
    // Keep selected findings selected when sorting or refreshing the table.
    const selectedKeys = new Set(Array.from(tbody.querySelectorAll('.row-cb:checked'))
      .map(box => {
        const row = box.closest('tr');
        return row ? row.dataset.jobId + ':' + row.dataset.seq : '';
      }).filter(Boolean));
    tbody.innerHTML = '';
    if (!findings.length) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 6;
      cell.className = 'findings-empty';
      cell.setAttribute('role', 'status');
      cell.textContent = activeFilter === 'all' ? 'No findings yet. Run an authorized tool to populate this view.' : 'No findings match this filter.';
      row.appendChild(cell);
      tbody.appendChild(row);
      updateSelection();
      return;
    }
    findings.forEach(f => {
      const tr = document.createElement('tr');
      const pillCls = SEV_PILL[f.severity] || 'pill-info';
      const sevLabel = SEV_LABEL[f.severity] || 'Info';
      const STATUS_META = {
        verified: ['pill-success', 'Verified'],
        candidate: ['pill-accent', 'Candidate'],
        refuted: ['pill-neutral', 'Refuted'],
        fixed: ['pill-low', 'Fixed'],
        still_vulnerable: ['pill-critical', 'Still Vulnerable']
      };
      const [statusCls, statusLabel] = STATUS_META[f.status] || ['pill-accent', f.status || 'Candidate'];
      const checkCell = document.createElement('td');
      checkCell.className = 'checkbox-col';
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.className = 'cb row-cb';
      checkbox.setAttribute('aria-label', 'Select finding: ' + f.title);
      checkCell.appendChild(checkbox);
      const severityCell = document.createElement('td');
      const severityPill = document.createElement('span');
      severityPill.className = 'pill ' + pillCls;
      const dot = document.createElement('span');
      dot.className = 'dot';
      severityPill.append(dot, document.createTextNode(sevLabel));
      severityCell.appendChild(severityPill);
      const titleCell = document.createElement('td');
      const titleSpan = document.createElement('span');
      titleSpan.className = 'title'; titleSpan.textContent = String(f.title);
      titleCell.appendChild(titleSpan);
      const targetCell = document.createElement('td');
      const targetSpan = document.createElement('span');
      targetSpan.className = 'target'; targetSpan.textContent = String(f.target || '—');
      targetCell.appendChild(targetSpan);
      const sourceCell = document.createElement('td');
      const sourceSpan = document.createElement('span');
      sourceSpan.className = 'mono'; sourceSpan.textContent = String(f.source || '—');
      sourceCell.appendChild(sourceSpan);
      const statusCell = document.createElement('td');
      const statusPill = document.createElement('span');
      statusPill.className = 'pill ' + statusCls;
      statusPill.textContent = String(statusLabel);
      statusCell.appendChild(statusPill);
      tr.append(checkCell, severityCell, titleCell, targetCell, sourceCell, statusCell);
      tr.tabIndex = 0;
      tr.setAttribute('role', 'button');
      tr.setAttribute('aria-label', 'Open finding: ' + f.title);
      tr.dataset.severity = f.severity;
      tr.dataset.title = f.title;
      tr.dataset.target = f.target;
      tr.dataset.source = f.source;
      tr.dataset.status = f.status;
      tr.dataset.jobId = f.job_id;
      tr.dataset.seq = String(f.seq);
      if (f._raw && f._raw.raw_line) tr.dataset.rawLine = f._raw.raw_line;
      if (f._raw && f._raw.data) {
        if (f._raw.data.description) tr.dataset.description = f._raw.data.description;
        if (f._raw.data.remediation) tr.dataset.remediation = f._raw.data.remediation;
      }
      const rowCheckbox = tr.querySelector('.row-cb');
      if (rowCheckbox) {
        rowCheckbox.checked = selectedKeys.has(f.job_id + ':' + f.seq);
        rowCheckbox.addEventListener('change', updateSelection);
      }
      tr.addEventListener('click', e => {
        if (e.target.closest('input, button, a, label, .checkbox-col, .copy-btn')) return;
        tbody.querySelectorAll('tr.selected').forEach(row => row.classList.remove('selected'));
        tr.classList.add('selected');
        openSlideover(tr);
      });
      tr.addEventListener('keydown', e => {
        if ((e.key === 'Enter' || e.key === ' ') && !e.target.closest('input, button, a, label')) {
          e.preventDefault();
          tbody.querySelectorAll('tr.selected').forEach(row => row.classList.remove('selected'));
          tr.classList.add('selected');
          openSlideover(tr);
        }
      });
      tbody.appendChild(tr);
    });
    updateSelection();
  }

  function openSlideover(tr) {
    const so = document.getElementById('slideover');
    if (!so) return;
    const sev = tr.dataset.severity || 'info';
    const sevEl = document.getElementById('so-sev');
    if (sevEl) {
      sevEl.className = 'pill ' + (SEV_PILL[sev] || 'pill-info');
      const dot = document.createElement('span');
      dot.className = 'dot';
      sevEl.replaceChildren(dot, document.createTextNode(SEV_LABEL[sev] || 'Info'));
    }
    const titleEl = document.getElementById('so-title');
    if (titleEl) titleEl.textContent = tr.dataset.title || '';
    const metaEl = document.getElementById('so-meta');
    if (metaEl) metaEl.textContent = [tr.dataset.target, tr.dataset.source].filter(Boolean).join(' · ');

    const descSection = document.getElementById('so-desc-section');
    const descEl = document.getElementById('so-desc');
    if (tr.dataset.description) { descEl.textContent = tr.dataset.description; descSection.style.display = ''; }
    else { descSection.style.display = 'none'; }

    const evSection = document.getElementById('so-evidence-section');
    const evEl = document.getElementById('so-evidence');
    if (tr.dataset.rawLine) { evEl.textContent = tr.dataset.rawLine; evSection.style.display = ''; }
    else { evSection.style.display = 'none'; }

    const remSection = document.getElementById('so-remediation-section');
    const remEl = document.getElementById('so-remediation');
    if (tr.dataset.remediation) { remEl.textContent = tr.dataset.remediation; remSection.style.display = ''; }
    else { remSection.style.display = 'none'; }

    // Validate / Retest buttons (§34.2 step 5)
    const jobId = tr.dataset.jobId || '';
    const seq = tr.dataset.seq || '0';
    const valBtn = document.getElementById('so-validate');
    const retBtn = document.getElementById('so-retest');
    if (valBtn && retBtn && jobId && seq !== undefined) {
      valBtn.style.display = '';
      retBtn.style.display = '';
      const st = tr.dataset.status || 'candidate';
      // Validate only makes sense on unverified. Retest only on verified.
      valBtn.disabled = st !== 'candidate';
      retBtn.disabled = st !== 'verified';
      valBtn.onclick = () => postAction('validate', jobId, seq, valBtn);
      retBtn.onclick = () => postAction('retest', jobId, seq, retBtn);
    } else if (valBtn && retBtn) {
      valBtn.style.display = 'none';
      retBtn.style.display = 'none';
    }
    so.classList.add('open');
  }

  async function postAction(kind, jobId, seq, btn) {
    const original = btn.textContent;
    btn.disabled = true;
    btn.textContent = '...';
    try {
      const r = await fetch('/api/' + kind + '/' + encodeURIComponent(jobId) + '/' + seq, { method: 'POST' });
      const data = await r.json();
      if (!r.ok) {
        alert((data.error || 'error') + (data.verification_status ? ' (current: ' + data.verification_status + ')' : ''));
      } else {
        // Update the slide-over and re-render the row.
        const tr = document.querySelector('#findings-tbody tr.selected');
        if (tr) {
          tr.dataset.status = data.status;
          // Find the status cell by class (last pill in the row)
          const cells = tr.querySelectorAll('td');
          if (cells.length >= 6) {
            const last = cells[5].querySelector('.pill');
            if (last) {
              const MAP = {
                verified: ['pill-success', 'Verified'],
                candidate: ['pill-accent', 'Candidate'],
                refuted: ['pill-neutral', 'Refuted'],
                fixed: ['pill-low', 'Fixed'],
                still_vulnerable: ['pill-critical', 'Still Vulnerable']
              };
              const [cls, label] = MAP[data.status] || ['pill-accent', data.status];
              last.className = 'pill ' + cls;
              last.textContent = label;
            }
          }
        }
        loadFindings();
        window.closeSlideover?.();
        alert(kind + ': ' + data.status + '\n' + data.reason);
      }
    } catch (e) {
      alert(kind + ' failed: ' + e);
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  }

  function sortRows(rows, key, asc) {
    const copy = rows.slice();
    if (key === 'severity') {
      copy.sort((a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity));
    } else {
      copy.sort((a, b) => (a[key] || '').localeCompare(b[key] || ''));
    }
    if (!asc) copy.reverse();
    return copy;
  }

  function loadFindings() {
    fetch('/api/report?format=json')
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => {
        const sev = data.severity_counts || {};
        const jobCount = data.job_count || 0;
        const findingCount = data.finding_count || 0;
        const categories = SEV_ORDER.filter(s => (sev[s] || 0) > 0).length;

        renderKpis(sev);
        renderDonut(sev);

        if (summaryEl) {
          summaryEl.textContent = findingCount + ' findings across ' + jobCount + ' jobs';
        }
        const findingsBadge = document.getElementById('findings-badge');
        if (findingsBadge) findingsBadge.textContent = String(findingCount);
        if (donutSummary) {
          donutSummary.textContent = findingCount + ' total · ' + jobCount + ' jobs · ' + categories + ' categories';
        }

        const rows = flattenFindings(data.jobs);
        window._whaxonFindings = rows;
        updateFilterCounts(rows);
        renderTable(sortRows(rows, sortKey, sortAsc));
        renderSurface(rows);
        applyFilter();
      })
      .catch(err => {
        window._whaxonFindings = [];
        renderKpis({});
        renderDonut({});
        updateFilterCounts([]);
        renderSurface([]);
        if (summaryEl) summaryEl.textContent = 'Findings could not be loaded.';
        if (donutSummary) donutSummary.textContent = 'Data unavailable';
        const badge = document.getElementById('findings-badge');
        if (badge) badge.textContent = '—';
        tbody.replaceChildren();
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 6;
        cell.className = 'findings-empty';
        cell.setAttribute('role', 'alert');
        cell.textContent = 'Could not load findings. Check the server connection and reload this page. Details: ' + String(err && err.message || err);
        row.appendChild(cell);
        tbody.appendChild(row);
        updateSelection();
      });
  }

  document.addEventListener('DOMContentLoaded', loadFindings);
  if (document.readyState !== 'loading') loadFindings();
})();


// ---- Run page wiring ----
(function () {
  const catalogEl = document.getElementById('run-catalog');
  if (!catalogEl) return;
  const countEl = document.getElementById('run-catalog-count');
  const targetEl = document.getElementById('run-target');
  const runBtn = document.getElementById('run-btn');
  const cancelBtn = document.getElementById('run-cancel-btn');
  const scopePill = document.getElementById('run-scope-pill');
  const outputEl = document.getElementById('run-output');
  const jobIdEl = document.getElementById('run-job-id');
  const recentEl = document.getElementById('run-recent-jobs');
  const recentSummary = document.getElementById('run-recent-summary');
  const statusEl = document.getElementById('run-status');
  let selectedTool = null, currentJob = null, eventSource = null, runPending = false;

  function setStatus(message, kind) {
    if (!statusEl) return;
    statusEl.textContent = message; statusEl.dataset.state = kind || 'info';
  }
  function showScopePill(text) {
    if (!scopePill) return;
    scopePill.className = 'pill pill-danger'; scopePill.replaceChildren();
    const dot = document.createElement('span'); dot.className = 'dot';
    scopePill.append(dot, document.createTextNode(text)); scopePill.style.display = '';
  }
  function hideScopePill() { if (scopePill) scopePill.style.display = 'none'; }
  function appendLine(stream, text) {
    if (!outputEl) return;
    const span = document.createElement('span');
    span.className = 'ln' + (stream === 'stderr' ? ' err' : '');
    span.textContent = String(text == null ? '' : text);
    outputEl.appendChild(span); outputEl.scrollTop = outputEl.scrollHeight;
  }
  function clearOutput() { if (outputEl) outputEl.replaceChildren(); }
  function setRunning(running) {
    runPending = running;
    if (runBtn) runBtn.disabled = running || !selectedTool;
    if (cancelBtn) cancelBtn.disabled = !running || !currentJob;
  }
  function selectTool(tool, item) {
    selectedTool = tool.id;
    catalogEl.querySelectorAll('.tool-item').forEach(el => {
      const active = el === item; el.classList.toggle('on', active); el.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    if (runBtn) { runBtn.textContent = '▶ Run ' + (tool.name || tool.id); runBtn.disabled = runPending; }
    setStatus((tool.name || tool.id) + ' selected. Enter a target authorized in the active scope.', 'info');
  }
  function renderCatalog(tools) {
    const safeTools = Array.isArray(tools) ? tools : [];
    window._whaxonTools = safeTools; catalogEl.replaceChildren(); selectedTool = null;
    if (runBtn) runBtn.disabled = true;
    safeTools.forEach(tool => {
      if (!tool || typeof tool.id !== 'string' || !tool.id) return;
      const item = document.createElement('button'); item.type = 'button'; item.className = 'tool-item'; item.dataset.toolId = tool.id; item.setAttribute('aria-pressed', 'false');
      const icon = document.createElement('span'); icon.className = 'ticon'; icon.textContent = String(tool.name || tool.id).charAt(0).toLowerCase();
      const name = document.createElement('span'); name.className = 'run-tool-name'; name.textContent = String(tool.name || tool.id);
      const tid = document.createElement('span'); tid.className = 'tid'; tid.textContent = tool.id;
      item.append(icon, name, tid); item.addEventListener('click', () => selectTool(tool, item)); catalogEl.appendChild(item);
    });
    if (countEl) countEl.textContent = catalogEl.querySelectorAll('.tool-item').length + ' tools';
    if (!catalogEl.children.length) {
      const empty = document.createElement('div'); empty.className = 'run-empty'; empty.textContent = 'No tools are available in the catalog.'; catalogEl.appendChild(empty);
      setStatus('No tools available. Check the server and tool catalog.', 'error');
    } else setStatus('Select a tool to begin. The server enforces the active scope before execution.', 'info');
  }
  function renderRecent(jobs) {
    if (!recentEl) return;
    recentEl.replaceChildren();
    const safeJobs = Array.isArray(jobs) ? jobs.slice(0, 8) : [];
    if (recentSummary) recentSummary.textContent = safeJobs.length + ' recent job' + (safeJobs.length === 1 ? '' : 's');
    if (!safeJobs.length) {
      const row = document.createElement('tr'), cell = document.createElement('td');
      cell.colSpan = 4; cell.className = 'run-empty'; cell.textContent = 'No recent jobs for this engagement.';
      row.appendChild(cell); recentEl.appendChild(row); return;
    }
    safeJobs.forEach(job => {
      const tr = document.createElement('tr'), tool = document.createElement('td');
      const toolText = document.createElement('span'); toolText.className = 'mono'; toolText.textContent = String(job.tool || '—'); tool.appendChild(toolText);
      const target = document.createElement('td'); target.textContent = String(job.target || '—');
      const status = document.createElement('td'), pill = document.createElement('span');
      const value = String(job.status || 'unknown').toLowerCase();
      pill.className = 'pill ' + (value === 'finished' ? 'pill-success' : value === 'failed' ? 'pill-danger' : value === 'running' ? 'pill-accent' : 'pill-neutral');
      pill.textContent = value; status.appendChild(pill);
      const findings = document.createElement('td'); findings.style.textAlign = 'right';
      const count = document.createElement('span'); count.className = 'mono'; count.textContent = String(Number(job.findings_count) || 0) + ' findings'; findings.appendChild(count);
      tr.append(tool, target, status, findings); recentEl.appendChild(tr);
    });
  }
  async function loadCatalog() {
    if (countEl) countEl.textContent = 'Loading…';
    try {
      const response = await fetch('/api/tools'); if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json(); renderCatalog(Array.isArray(data) ? data : (data && Array.isArray(data.tools) ? data.tools : []));
    } catch (err) {
      catalogEl.replaceChildren();
      const row = document.createElement('div'); row.className = 'run-empty'; row.setAttribute('role', 'alert'); row.textContent = 'Could not load tools. Check the server connection and reload.'; catalogEl.appendChild(row);
      if (countEl) countEl.textContent = 'Load failed'; setStatus('Tool catalog request failed: ' + String(err && err.message || err), 'error');
    }
  }
  async function loadRecent() {
    try {
      const response = await fetch('/api/history'); if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json(); renderRecent(Array.isArray(data) ? data : (data && Array.isArray(data.jobs) ? data.jobs : []));
    } catch (err) {
      if (recentEl) {
        recentEl.replaceChildren();
        const row = document.createElement('tr'), cell = document.createElement('td');
        cell.colSpan = 4; cell.className = 'run-empty'; cell.setAttribute('role', 'alert'); cell.textContent = 'Could not load recent jobs: ' + String(err && err.message || err);
        row.appendChild(cell); recentEl.appendChild(row);
      }
      if (recentSummary) recentSummary.textContent = 'History unavailable';
    }
  }
  function closeStream() { if (eventSource) { eventSource.close(); eventSource = null; } }
  function finishJob(message, kind) {
    appendLine(kind === 'error' ? 'stderr' : 'stdout', message); closeStream(); setRunning(false); setStatus(message, kind || 'info'); loadRecent();
  }
  function openStream(jobId) {
    closeStream();
    const es = new EventSource('/api/jobs/' + encodeURIComponent(jobId) + '/stream'); eventSource = es;
    es.onmessage = ev => {
      let msg; try { msg = JSON.parse(ev.data); } catch (_) { return; }
      if (msg.type === 'status') {
        if (msg.status === 'running') setStatus('Job is running…', 'running');
        else if (msg.status === 'queued') setStatus('Job queued…', 'running');
        else if (msg.status === 'cancelled') finishJob('Job cancelled.', 'info');
      } else if (msg.type === 'line') appendLine(msg.stream, msg.text);
      else if (msg.type === 'finished') finishJob('Finished (exit ' + msg.exit_code + ').', msg.exit_code === 0 ? 'success' : 'error');
      else if (msg.type === 'failed') finishJob('Job failed: ' + String(msg.error || 'unknown error'), 'error');
    };
    es.onerror = () => {
      if (!eventSource) return;
      closeStream(); setRunning(false); setStatus('Live output connection ended. Check Recent jobs for final status.', 'error'); loadRecent();
    };
  }
  async function runJob() {
    const target = (targetEl && targetEl.value || '').trim();
    if (runPending) return;
    if (!selectedTool) { setStatus('Select a tool first.', 'error'); return; }
    if (!target) { setStatus('Enter a target.', 'error'); if (targetEl) targetEl.focus(); return; }
    clearOutput(); hideScopePill(); currentJob = null; setRunning(true);
    if (jobIdEl) jobIdEl.textContent = 'Starting job…'; setStatus('Checking scope and starting job…', 'running');
    try {
      const response = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tool_id: selectedTool, target: target, extra_args: '' }) });
      let body = {}; try { body = await response.json(); } catch (_) {}
      if (!response.ok) {
        setRunning(false); const message = body.error || ('Request failed (HTTP ' + response.status + ').');
        if (response.status === 403) {
          showScopePill('Out of scope');
          const modal = document.getElementById('scope-modal');
          const targetLabel = modal && modal.querySelector('[data-scope-target]');
          const reasonLabel = modal && modal.querySelector('[data-scope-reason]');
          if (targetLabel) targetLabel.textContent = target;
          if (reasonLabel) reasonLabel.textContent = message;
          if (modal) modal.classList.add('open');
          setStatus('Blocked: target is not confirmed in the active scope. No job was started.', 'error');
        } else setStatus(message, 'error');
        appendLine('stderr', message); if (jobIdEl) jobIdEl.textContent = 'No job running'; return;
      }
      if (!body.job_id || typeof body.job_id !== 'string') throw new Error('Server response did not include a job ID.');
      currentJob = body.job_id; if (jobIdEl) jobIdEl.textContent = 'Job ' + currentJob;
      setStatus('Job accepted; connecting to live output…', 'running'); if (cancelBtn) cancelBtn.disabled = false;
      openStream(currentJob); loadRecent();
    } catch (err) {
      setRunning(false); if (jobIdEl) jobIdEl.textContent = 'No job running';
      const message = 'Could not start job: ' + String(err && err.message || err); appendLine('stderr', message); setStatus(message, 'error');
    }
  }
  async function cancelJob() {
    if (!currentJob || !cancelBtn || cancelBtn.disabled) return;
    cancelBtn.disabled = true; setStatus('Sending cancellation request…', 'running');
    try {
      const response = await fetch('/api/jobs/' + encodeURIComponent(currentJob) + '/cancel', { method: 'POST' });
      let body = {}; try { body = await response.json(); } catch (_) {}
      if (!response.ok) throw new Error(body.error || ('HTTP ' + response.status));
      if (body.ok) finishJob('Cancellation requested.', 'info');
      else { setStatus('The job could not be cancelled (it may already have finished).', 'error'); loadRecent(); }
    } catch (err) {
      cancelBtn.disabled = false; const message = 'Cancel failed: ' + String(err && err.message || err); setStatus(message, 'error'); appendLine('stderr', message);
    }
  }
  if (runBtn) runBtn.addEventListener('click', runJob);
  if (cancelBtn) cancelBtn.addEventListener('click', cancelJob);
  if (targetEl) targetEl.addEventListener('keydown', e => { if (e.key === 'Enter' && runBtn && !runBtn.disabled) runJob(); });
  document.querySelectorAll('.sb-item[data-page="run"]').forEach(el => el.addEventListener('click', () => { loadCatalog(); loadRecent(); }));
  document.addEventListener('DOMContentLoaded', () => { loadCatalog(); loadRecent(); });
  if (document.readyState !== 'loading') { loadCatalog(); loadRecent(); }
})();

// ---- Approvals page wiring ----
(function () {
  const list = document.getElementById('approvals-list');
  const pendingList = document.getElementById('pending-findings-list');
  if (!list || !pendingList) return;
  const ownerInput = document.getElementById('approvals-owner');
  const summary = document.getElementById('approvals-summary');
  const refresh = document.getElementById('approvals-refresh');
  const pendingCount = document.getElementById('pending-findings-count');
  const pendingSummary = document.getElementById('pending-findings-summary');
  const badge = document.getElementById('approvals-badge');
  let loading = false;

  function empty(container, message, role) {
    container.replaceChildren();
    const note = document.createElement('div'); note.className = 'card-sub approvals-empty'; note.textContent = message;
    if (role) note.setAttribute('role', role);
    container.appendChild(note);
  }
  async function loadApprovals() {
    const owner = (ownerInput && ownerInput.value || '').trim();
    try {
      const response = await fetch('/api/ai/pending' + (owner ? '?owner=' + encodeURIComponent(owner) : ''));
      let rows = []; if (!response.ok) { let body={}; try{body=await response.json();}catch(_){} throw new Error(body.error || ('HTTP '+response.status)); }
      rows = await response.json();
      if (!Array.isArray(rows)) throw new Error('Invalid pending-approval response');
      if (badge) { badge.textContent = String(rows.length); badge.style.display = rows.length ? '' : 'none'; }
      if (summary) summary.textContent = rows.length + ' AI run' + (rows.length === 1 ? '' : 's') + ' awaiting a decision';
      if (!rows.length) { empty(list, 'No AI runs are waiting for a decision.'); return; }
      list.replaceChildren();
      rows.forEach(run => {
        const question = run.pending_question || {};
        const card = document.createElement('div'); card.className = 'card approvals-item'; card.style.marginBottom = '12px';
        const title = document.createElement('div'); title.className = 'card-title'; title.textContent = String(question.rationale || '(No rationale supplied)');
        const detail = document.createElement('div'); detail.className = 'card-sub';
        detail.textContent = 'Run ' + String(run.id || '—') + ' · owner ' + String(run.owner || 'local') + ' · confidence ' + (typeof question.confidence === 'number' ? question.confidence.toFixed(2) : '—') + (question.proposed_phase ? ' · proposed phase ' + String(question.proposed_phase) : '');
        const actions = document.createElement('div'); actions.className = 'approvals-actions';
        const answer = document.createElement('input'); answer.className = 'form-input'; answer.placeholder = 'Answer or decision'; answer.setAttribute('aria-label','Answer for run '+String(run.id||''));
        const button = document.createElement('button'); button.type='button'; button.className='btn btn-primary btn-sm'; button.textContent='Submit answer';
        button.addEventListener('click', async () => {
          const value = answer.value.trim();
          if (!value) { answer.focus(); if(summary)summary.textContent='Enter an answer before submitting.'; return; }
          button.disabled=true; answer.disabled=true;
          try {
            const response = await fetch('/api/ai/runs/'+encodeURIComponent(String(run.id))+'/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer:value,user:owner||'web'})});
            let body={};try{body=await response.json();}catch(_){}
            if (!response.ok && response.status !== 409) throw new Error(body.error||('HTTP '+response.status));
            await loadApprovals();
          } catch(err) {
            if(summary)summary.textContent='Could not submit answer: '+String(err&&err.message||err);
            button.disabled=false; answer.disabled=false;
          }
        });
        actions.append(answer,button); card.append(title,detail,actions); list.appendChild(card);
      });
    } catch(err) {
      empty(list,'Could not load AI approvals: '+String(err&&err.message||err),'alert');
      if(summary)summary.textContent='AI approvals unavailable.';
    }
  }
  async function loadPendingFindings() {
    if (pendingSummary) pendingSummary.textContent='Loading findings awaiting review…';
    try {
      const response=await fetch('/api/report?format=json');
      if(!response.ok)throw new Error('HTTP '+response.status);
      const data=await response.json(), pending=[];
      (Array.isArray(data.jobs)?data.jobs:[]).forEach(entry=>{
        const job=entry.job||{};
        (Array.isArray(entry.findings)?entry.findings:[]).forEach(f=>{
          if((f.verification_status||'candidate')==='candidate')pending.push({job,f});
        });
      });
      if(pendingCount)pendingCount.textContent=String(pending.length);
      if(!pending.length){empty(pendingList,'No findings are waiting for human review.');if(pendingSummary)pendingSummary.textContent='0 candidate findings';return;}
      pendingList.replaceChildren();
      pending.slice(0,50).forEach(({job,f})=>{
        const card=document.createElement('div');card.className='card approvals-item';card.style.marginBottom='8px';
        const title=document.createElement('div');title.className='card-title';title.textContent=String(f.title||f.kind||f.raw_line||'(finding)');
        const detail=document.createElement('div');detail.className='card-sub';detail.textContent='Job '+String(job.id||'—')+' · target '+String(job.target||'—')+' · '+String(f.severity||'info');
        const actions=document.createElement('div');actions.className='approvals-actions';
        ['verified','refuted'].forEach(status=>{
          const button=document.createElement('button');button.type='button';button.className='btn btn-sm '+(status==='verified'?'btn-primary':'btn-ghost');button.textContent=status==='verified'?'Mark verified':'Mark refuted';
          button.addEventListener('click',async()=>{
            button.disabled=true;
            try{
              const response=await fetch('/api/approvals/'+encodeURIComponent(String(job.id))+'/'+encodeURIComponent(String(Number.isInteger(f.seq)?f.seq:0))+'/resolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status,user:'web'})});
              let body={};try{body=await response.json();}catch(_){}
              if(!response.ok)throw new Error(body.error||('HTTP '+response.status));
              if(pendingSummary)pendingSummary.textContent='Finding marked '+status+'. Refreshing queue…';
              await loadPendingFindings();
            }catch(err){if(pendingSummary)pendingSummary.textContent='Could not update finding: '+String(err&&err.message||err);button.disabled=false;}
          });
          actions.appendChild(button);
        });
        card.append(title,detail,actions);pendingList.appendChild(card);
      });
      if(pendingSummary)pendingSummary.textContent=pending.length+' candidate finding(s) awaiting review'+(pending.length>50?' (showing first 50)':'')+'.';
    }catch(err){empty(pendingList,'Could not load pending findings: '+String(err&&err.message||err),'alert');if(pendingSummary)pendingSummary.textContent='Pending findings unavailable.';if(pendingCount)pendingCount.textContent='—';}
  }
  async function loadAll() {
    if(loading)return;loading=true;
    if(refresh){refresh.disabled=true;refresh.textContent='Refreshing…';}
    await Promise.all([loadApprovals(),loadPendingFindings()]);
    loading=false;
    if(refresh){refresh.disabled=false;refresh.textContent='Refresh';}
  }
  if(refresh)refresh.addEventListener('click',loadAll);
  if(ownerInput)ownerInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();loadApprovals();}});
  document.querySelectorAll('.sb-item[data-page="approvals"]').forEach(item=>item.addEventListener('click',loadAll));
  document.addEventListener('DOMContentLoaded',loadAll);
  if(document.readyState!=='loading')loadAll();
})();

// ---- Coverage page wiring (§34.2 step 4) ----
(function () {
  const tbody = document.getElementById('coverage-tbody');
  if (!tbody) return;
  const countEl = document.getElementById('coverage-count');
  const summaryEl = document.getElementById('coverage-summary');
  const KIND_PILL = { scope_blocked:'pill-warning', binary_missing:'pill-neutral', timeout:'pill-medium', auth_required:'pill-accent', waf_blocked:'pill-critical' };
  function render(gaps) {
    tbody.replaceChildren();
    const items = Array.isArray(gaps) ? gaps : [];
    if (!items.length) {
      const tr = document.createElement('tr'), td = document.createElement('td');
      td.colSpan = 4; td.className = 'coverage-empty'; td.textContent = 'No coverage gaps recorded for this engagement.';
      tr.appendChild(td); tbody.appendChild(tr);
      if (countEl) countEl.textContent = '0';
      if (summaryEl) summaryEl.textContent = 'No skipped steps are recorded in the current report data.';
      const badge = document.getElementById('coverage-badge');
      if (badge) { badge.textContent = '0'; badge.style.display = 'none'; }
      return;
    }
    items.forEach(g => {
      const tr = document.createElement('tr');
      const kind = String(g.kind || 'unknown');
      const reason = document.createElement('td'), pill = document.createElement('span');
      pill.className = 'pill ' + (KIND_PILL[kind] || 'pill-info'); pill.textContent = kind; reason.appendChild(pill);
      const tool = document.createElement('td'); tool.className = 'mono'; tool.textContent = String(g.tool_id || '—');
      const target = document.createElement('td'); target.className = 'target'; target.textContent = String(g.target || '—');
      const detail = document.createElement('td'); detail.className = 'title'; detail.textContent = String(g.detail || '—');
      tr.append(reason, tool, target, detail); tbody.appendChild(tr);
    });
    if (countEl) countEl.textContent = String(items.length);
    if (summaryEl) summaryEl.textContent = items.length + ' skipped step(s) across the engagement.';
    const badge = document.getElementById('coverage-badge');
    if (badge) { badge.textContent = String(items.length); badge.style.display = ''; }
  }
  async function loadCoverage() {
    if (summaryEl) summaryEl.textContent = 'Loading coverage data…';
    try {
      const response = await fetch('/api/report?format=json');
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json(), all = [];
      (Array.isArray(data.jobs) ? data.jobs : []).forEach(entry => {
        (Array.isArray(entry.coverage) ? entry.coverage : []).forEach(item => all.push(item));
      });
      render(all);
    } catch (err) {
      tbody.replaceChildren();
      const tr = document.createElement('tr'), td = document.createElement('td');
      td.colSpan = 4; td.className = 'coverage-empty'; td.setAttribute('role', 'alert');
      td.textContent = 'Could not load coverage data: ' + String(err && err.message || err);
      tr.appendChild(td); tbody.appendChild(tr);
      if (countEl) countEl.textContent = '—';
      if (summaryEl) summaryEl.textContent = 'Coverage data unavailable.';
    }
  }
  document.querySelectorAll('.sb-item[data-page="monitoring"]').forEach(el => el.addEventListener('click', loadCoverage));
  document.addEventListener('DOMContentLoaded', loadCoverage);
  if (document.readyState !== 'loading') loadCoverage();
})();

// ---- Report page wiring (§34.4 step 1) ----
(function () {
  const buttons = [
    { element: document.getElementById('report-md'), format: 'md', label: 'Markdown' },
    { element: document.getElementById('report-html'), format: 'html', label: 'HTML' },
    { element: document.getElementById('report-pdf'), format: 'pdf', label: 'PDF' }
  ].filter(item => item.element);
  if (!buttons.length) return;
  const statusEl = document.getElementById('report-status');
  let active = false;
  function status(message, kind) {
    if (!statusEl) return;
    statusEl.textContent = message; statusEl.dataset.state = kind || 'info';
  }
  async function download(item) {
    if (active) return;
    active = true;
    const btn = item.element, original = btn.textContent;
    buttons.forEach(entry => { entry.element.disabled = true; });
    btn.textContent = 'Generating…';
    status('Generating ' + item.label + ' report from current engagement data…', 'busy');
    try {
      const response = await fetch('/api/report?format=' + encodeURIComponent(item.format) + '&engagement=default');
      if (!response.ok) {
        let message = 'HTTP ' + response.status;
        try {
          const body = await response.json();
          if (body && body.error) message = body.error;
        } catch (_) {
          try { const text = await response.text(); if (text) message = text; } catch (_e) {}
        }
        throw new Error(message);
      }
      const blob = await response.blob();
      if (!blob.size) throw new Error('The server returned an empty report.');
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url; link.download = 'whaxon-report.' + item.format; link.hidden = true;
      document.body.appendChild(link); link.click(); link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      status(item.label + ' report generated. Your download should begin shortly.', 'success');
    } catch (err) {
      status('Report generation failed: ' + String(err && err.message || err), 'error');
    } finally {
      active = false;
      buttons.forEach(entry => { entry.element.disabled = false; });
      btn.textContent = original;
    }
  }
  buttons.forEach(item => item.element.addEventListener('click', () => download(item)));
})();
// ---- Retest page wiring (live queue) ----
(function () {
  const tbody = document.getElementById('retest-tbody');
  if (!tbody) return;
  const countEl = document.getElementById('retest-count');
  const summaryEl = document.getElementById('retest-summary');
  let loading = false;
  function message(text, role) {
    tbody.replaceChildren();
    const row = document.createElement('tr'), cell = document.createElement('td');
    cell.colSpan = 6; cell.className = 'retest-empty'; cell.textContent = text;
    if (role) cell.setAttribute('role', role);
    row.appendChild(cell); tbody.appendChild(row);
  }
  async function load() {
    if (loading) return;
    loading = true;
    if (summaryEl) summaryEl.textContent = 'Loading verified findings…';
    try {
      const response = await fetch('/api/report?format=json');
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      const rows = [];
      (Array.isArray(data.jobs) ? data.jobs : []).forEach(entry => {
        const job = entry.job || {};
        (Array.isArray(entry.findings) ? entry.findings : []).forEach(f => {
          if (f.verification_status === 'verified' && job.id && Number.isInteger(Number(f.seq))) rows.push({ job, f });
        });
      });
      if (countEl) countEl.textContent = String(rows.length);
      if (!rows.length) {
        message('No verified findings yet. Validate a finding first.');
        if (summaryEl) summaryEl.textContent = 'Nothing to retest.';
        return;
      }
      if (summaryEl) summaryEl.textContent = rows.length + ' verified finding(s) available for retest.';
      tbody.replaceChildren();
      rows.forEach(({ job, f }) => {
        const tr = document.createElement('tr');
        const titleCell = document.createElement('td'), title = document.createElement('span');
        title.className = 'title'; title.textContent = String(f.title || f.kind || '(finding)'); titleCell.appendChild(title);
        const severityCell = document.createElement('td'), severityPill = document.createElement('span');
        const raw = String(f.severity || 'info').toLowerCase();
        const severity = ['critical','high','medium','low','info'].includes(raw) ? raw : 'info';
        severityPill.className = 'pill pill-' + severity + ' no-border';
        const dot = document.createElement('span'); dot.className = 'dot';
        const label = document.createElement('span'); label.textContent = severity;
        severityPill.append(dot, label); severityCell.appendChild(severityPill);
        const targetCell = document.createElement('td'); targetCell.textContent = String(job.target || '—');
        const sourceCell = document.createElement('td'); sourceCell.className = 'mono'; sourceCell.textContent = String(f.source || job.tool || '—');
        const statusCell = document.createElement('td'), status = document.createElement('span');
        status.className = 'pill pill-success'; status.textContent = 'Verified'; statusCell.appendChild(status);
        const actionCell = document.createElement('td'), button = document.createElement('button');
        button.type = 'button'; button.className = 'btn btn-sm btn-primary'; button.textContent = 'Retest';
        button.setAttribute('aria-label', 'Retest ' + String(f.title || f.kind || 'finding'));
        button.addEventListener('click', async () => {
          if (button.disabled) return;
          button.disabled = true; button.textContent = 'Retesting…';
          if (summaryEl) summaryEl.textContent = 'Retesting finding against the current target…';
          try {
            const result = await fetch('/api/retest/' + encodeURIComponent(job.id) + '/' + encodeURIComponent(String(f.seq)), { method: 'POST' });
            let body = {}; try { body = await result.json(); } catch (_) {}
            if (!result.ok) throw new Error(body.error || ('HTTP ' + result.status));
            const resultStatus = String(body.status || 'completed');
            const reason = body.reason ? ': ' + String(body.reason) : '';
            if (summaryEl) summaryEl.textContent = 'Retest result: ' + resultStatus + reason;
            await load();
          } catch (err) {
            if (summaryEl) summaryEl.textContent = 'Retest failed: ' + String(err && err.message || err);
            button.disabled = false; button.textContent = 'Retest';
          }
        });
        actionCell.appendChild(button); tr.append(titleCell, severityCell, targetCell, sourceCell, statusCell, actionCell); tbody.appendChild(tr);
      });
    } catch (err) {
      message('Could not load retest queue: ' + String(err && err.message || err), 'alert');
      if (summaryEl) summaryEl.textContent = 'Retest queue unavailable.';
      if (countEl) countEl.textContent = '—';
    } finally { loading = false; }
  }
  document.querySelectorAll('.sb-item[data-page="retest"]').forEach(el => el.addEventListener('click', load));
  document.addEventListener('DOMContentLoaded', load);
  if (document.readyState !== 'loading') load();
})();
// ---- Sessions page wiring ----
(function () {
  const tbody = document.getElementById('sessions-tbody');
  if (!tbody) return;
  const summary = document.getElementById('sessions-summary');
  const refresh = document.getElementById('sessions-refresh');
  let loading = false;
  function showMessage(text, role) {
    tbody.replaceChildren();
    const tr = document.createElement('tr'), td = document.createElement('td');
    td.colSpan = 5; td.className = 'sessions-empty'; td.textContent = text;
    if (role) td.setAttribute('role', role);
    tr.appendChild(td); tbody.appendChild(tr);
  }
  async function load() {
    if (loading) return;
    loading = true;
    if (refresh) { refresh.disabled = true; refresh.textContent = 'Refreshing…'; }
    if (summary) summary.textContent = 'Loading sessions…';
    try {
      const response = await fetch('/api/msf/sessions');
      let data = {}; try { data = await response.json(); } catch (_) {}
      if (!response.ok) throw new Error(data.error || ('HTTP ' + response.status));
      const live = Object.entries(data.live || {}).map(([sid, info]) => ({ sid, info: info || {}, status: 'live' }));
      const stored = (Array.isArray(data.stored) ? data.stored : []).map(s => ({ sid: s.id, info: s.info || s, status: s.status || 'stored' }));
      const entries = live.concat(stored);
      tbody.replaceChildren();
      if (!entries.length) {
        showMessage(data.available === false ? 'Metasploit RPC is unavailable. Configure it to view live sessions.' : 'No live or stored sessions were returned.');
        if (summary) summary.textContent = data.available === false ? 'Metasploit RPC unavailable' : '0 sessions';
        return;
      }
      entries.forEach(({sid, info, status}) => {
        const tr = document.createElement('tr');
        const session = document.createElement('td'), sessionId = document.createElement('span');
        sessionId.className = 'mono'; sessionId.textContent = String(sid); session.appendChild(sessionId);
        const host = document.createElement('td'); host.className = 'target'; host.textContent = String(info.target_host || info.tunnel_peer || info.session_host || '—');
        const type = document.createElement('td'), typePill = document.createElement('span');
        typePill.className = 'pill pill-accent'; typePill.textContent = String(info.type || info.session_type || 'unknown'); type.appendChild(typePill);
        const infoCell = document.createElement('td'); infoCell.className = 'mono'; infoCell.textContent = String(info.info || info.platform || '—');
        const state = document.createElement('td'), statusPill = document.createElement('span');
        statusPill.className = 'pill ' + (status === 'live' ? 'pill-success' : 'pill-neutral'); statusPill.textContent = String(status); state.appendChild(statusPill);
        tr.append(session, host, type, infoCell, state); tbody.appendChild(tr);
      });
      if (summary) summary.textContent = entries.length + ' session record(s): ' + live.length + ' live, ' + stored.length + ' stored.';
    } catch (err) {
      showMessage('Could not load sessions: ' + String(err && err.message || err), 'alert');
      if (summary) summary.textContent = 'Session data unavailable.';
    } finally {
      loading = false;
      if (refresh) { refresh.disabled = false; refresh.textContent = 'Refresh'; }
    }
  }
  if (refresh) refresh.addEventListener('click', load);
  document.querySelectorAll('.sb-item[data-page="sessions"]').forEach(el => el.addEventListener('click', load));
  document.addEventListener('DOMContentLoaded', load);
  if (document.readyState !== 'loading') load();
})();
// ---- Catalog page wiring ----
(function () {
  const tbody = document.getElementById('catalog-tbody');
  if (!tbody) return;
  const summaryEl = document.getElementById('catalog-summary');
  const refresh = document.getElementById('catalog-refresh');
  let loading = false;
  function showMessage(message, role) {
    tbody.replaceChildren();
    const tr = document.createElement('tr'), td = document.createElement('td');
    td.colSpan = 5; td.className = 'catalog-empty'; td.textContent = message;
    if (role) td.setAttribute('role', role);
    tr.appendChild(td); tbody.appendChild(tr);
  }
  async function load() {
    if (loading) return;
    loading = true;
    if (refresh) { refresh.disabled = true; refresh.textContent = 'Refreshing…'; }
    if (summaryEl) summaryEl.textContent = 'Loading tools…';
    try {
      const response = await fetch('/api/tools');
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const payload = await response.json();
      const tools = Array.isArray(payload) ? payload : (payload && Array.isArray(payload.tools) ? payload.tools : []);
      tbody.replaceChildren();
      if (!tools.length) {
        showMessage('No tools are currently registered in the catalog.');
        if (summaryEl) summaryEl.textContent = '0 tools in the catalog.';
        return;
      }
      tools.forEach(tool => {
        const tr = document.createElement('tr');
        const id = document.createElement('td'), idText = document.createElement('span');
        idText.className = 'mono'; idText.textContent = String(tool.id || '—'); id.appendChild(idText);
        const category = document.createElement('td'), categoryPill = document.createElement('span');
        categoryPill.className = 'pill pill-neutral'; categoryPill.textContent = String(tool.category || '—'); category.appendChild(categoryPill);
        const binary = document.createElement('td'); binary.className = 'mono'; binary.textContent = String(tool.binary || '—');
        const adapter = document.createElement('td'), adapterPill = document.createElement('span');
        adapterPill.className = 'pill ' + (tool.adapter_available ? 'pill-success' : 'pill-neutral');
        adapterPill.textContent = tool.adapter_available ? 'Available' : 'Not registered'; adapter.appendChild(adapterPill);
        const pkg = document.createElement('td'); pkg.className = 'mono'; pkg.textContent = String(tool.package || '—');
        tr.append(id, category, binary, adapter, pkg); tbody.appendChild(tr);
      });
      if (summaryEl) summaryEl.textContent = tools.length + ' tools in the catalog.';
    } catch (err) {
      showMessage('Could not load catalog: ' + String(err && err.message || err), 'alert');
      if (summaryEl) summaryEl.textContent = 'Catalog unavailable.';
    } finally {
      loading = false;
      if (refresh) { refresh.disabled = false; refresh.textContent = 'Refresh'; }
    }
  }
  if (refresh) refresh.addEventListener('click', load);
  document.querySelectorAll('.sb-item[data-page="catalog"]').forEach(el => el.addEventListener('click', load));
  document.addEventListener('DOMContentLoaded', load);
  if (document.readyState !== 'loading') load();
})();
// ---- Scope override modal ----
(function () {
  const btn = document.getElementById('scope-override-btn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    // The scope modal was opened by the run page when scope refused.
    // Read the pending target from the modal's sm-card text if needed,
    // or from the run-target input.
    const modal = document.getElementById('scope-modal');
    const targetEl = document.getElementById('run-target');
    const target = (targetEl && targetEl.value) || '';
    if (!target) { alert('No target to override.'); return; }
    btn.disabled = true;
    try {
      const r = await fetch('/api/scope/override', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ target: target, tool: '' })
      });
      if (r.ok) {
        if (modal) modal.classList.remove('open');
        alert('Override request logged for ' + target + '. The scan was not launched; update the active scope before retrying.');
      } else {
        const data = await r.json();
        alert('Override failed: ' + (data.error || r.status));
      }
    } catch (e) { alert('Override failed: ' + e); }
    finally { btn.disabled = false; }
  });
})();


// ---- Functional appearance preferences and threat-intel search ----
(function () {
  const themeSelect = document.getElementById('settings-theme');
  const densityButtons = Array.from(document.querySelectorAll('[data-density]'));
  const storageKey = 'whaxon-ui-preferences';
  const defaults = { theme: 'dark', density: 'comfortable' };
  let prefs = { ...defaults };
  try { prefs = { ...defaults, ...JSON.parse(localStorage.getItem(storageKey) || '{}') }; } catch (_) {}

  function applyTheme(theme) {
    const resolved = theme === 'system'
      ? (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
      : theme;
    document.documentElement.dataset.theme = resolved;
    if (themeSelect) themeSelect.value = theme;
  }
  function applyDensity(density) {
    document.documentElement.dataset.density = density;
    densityButtons.forEach(button => {
      const active = button.dataset.density === density;
      button.classList.toggle('on', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }
  function savePrefs() {
    const statusEl = document.getElementById('settings-save-status');
    try {
      localStorage.setItem(storageKey, JSON.stringify(prefs));
      if (statusEl) statusEl.textContent = 'Appearance preferences saved in this browser.';
    } catch (_) {
      if (statusEl) statusEl.textContent = 'Appearance changed for this session, but browser storage is unavailable.';
    }
  }
  applyTheme(prefs.theme);
  applyDensity(prefs.density);
  if (themeSelect) themeSelect.addEventListener('change', () => {
    prefs.theme = ['dark', 'light', 'system'].includes(themeSelect.value) ? themeSelect.value : 'dark';
    applyTheme(prefs.theme); savePrefs();
  });
  densityButtons.forEach(button => button.addEventListener('click', () => {
    prefs.density = button.dataset.density === 'compact' ? 'compact' : 'comfortable';
    applyDensity(prefs.density); savePrefs();
  }));
  if (window.matchMedia) {
    const media = window.matchMedia('(prefers-color-scheme: light)');
    media.addEventListener?.('change', () => { if (prefs.theme === 'system') applyTheme('system'); });
  }

  const queryInput = document.getElementById('intel-query');
  const searchButton = document.getElementById('intel-search');
  const status = document.getElementById('intel-status');
  const result = document.getElementById('intel-results');
  if (!queryInput || !searchButton || !status || !result) return;
  let source = 'nvd';
  document.querySelectorAll('[data-intel-source]').forEach(button => {
    button.addEventListener('click', () => {
      source = button.dataset.intelSource === 'exploit' ? 'exploit' : 'nvd';
      document.querySelectorAll('[data-intel-source]').forEach(item => {
        const active = item === button;
        item.classList.toggle('on', active);
        item.setAttribute('aria-pressed', String(active));
      });
      status.textContent = source === 'nvd'
        ? 'Search National Vulnerability Database (NVD).'
        : 'Search Exploit-DB for published exploit references.';
    });
  });
  function searchIntel() {
    const query = queryInput.value.trim();
    if (!query) {
      status.textContent = 'Enter a CVE identifier, product name, or version first.';
      queryInput.focus();
      return;
    }
    const url = source === 'nvd'
      ? 'https://nvd.nist.gov/vuln/search/results?query=' + encodeURIComponent(query) + '&search_type=all'
      : 'https://www.exploit-db.com/search?text=' + encodeURIComponent(query);
    result.replaceChildren();
    const title = document.createElement('div');
    title.className = 'card-title';
    title.textContent = source === 'nvd' ? 'NVD search' : 'Exploit-DB search';
    const description = document.createElement('p');
    description.className = 'card-sub';
    description.textContent = 'Search query: ' + query + '. Results are provided by the external source and are not independently verified by this page.';
    const link = document.createElement('a');
    link.className = 'btn btn-primary';
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = source === 'nvd' ? 'Open results on NVD' : 'Open results on Exploit-DB';
    result.append(title, description, link);
    status.textContent = 'Search prepared. Open the source results to view current records.';
  }
  searchButton.addEventListener('click', searchIntel);
  queryInput.addEventListener('keydown', event => { if (event.key === 'Enter') searchIntel(); });
})();


// ---- Attack surface / pivot relationship view ----
(function () {
  const tbody = document.getElementById('graph-tbody');
  const summary = document.getElementById('graph-summary');
  const refresh = document.getElementById('graph-refresh');
  if (!tbody || !summary) return;

  function cell(text, className) {
    const td = document.createElement('td');
    if (className) {
      const span = document.createElement('span');
      span.className = className;
      span.textContent = text || '—';
      td.appendChild(span);
    } else {
      td.textContent = text || '—';
    }
    return td;
  }
  function nodeLabel(node) {
    return node ? String(node.kind || 'node') + ': ' + String(node.id || '') : '—';
  }
  async function loadGraph() {
    if (refresh) { refresh.disabled = true; refresh.textContent = 'Refreshing…'; }
    summary.textContent = 'Loading stored pivot relationships…';
    tbody.replaceChildren();
    try {
      const response = await fetch('/api/pivot/graph', { headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      const edges = Array.isArray(data.edges) ? data.edges : [];
      summary.textContent = edges.length + ' recorded relationship' + (edges.length === 1 ? '' : 's') + '.';
      if (!edges.length) {
        const tr = document.createElement('tr');
        const td = cell('No pivot relationships have been recorded for this workspace yet.');
        td.colSpan = 5;
        td.style.padding = '16px';
        td.style.color = 'var(--text-dim)';
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
      }
      edges.forEach(edge => {
        const tr = document.createElement('tr');
        tr.append(
          cell(nodeLabel(edge.parent), 'mono'),
          cell(String(edge.relation || '')),
          cell(nodeLabel(edge.child), 'mono'),
          cell(String(edge.evidence || '')),
          cell(edge.created_at ? new Date(Number(edge.created_at) * 1000).toLocaleString() : '—', 'mono')
        );
        tbody.appendChild(tr);
      });
    } catch (error) {
      summary.textContent = 'Could not load pivot relationships.';
      const tr = document.createElement('tr');
      const td = cell('Request failed: ' + (error && error.message ? error.message : error));
      td.colSpan = 5;
      td.style.padding = '16px';
      td.style.color = 'var(--critical)';
      tr.appendChild(td);
      tbody.appendChild(tr);
    } finally {
      if (refresh) { refresh.disabled = false; refresh.textContent = 'Refresh'; }
    }
  }
  refresh?.addEventListener('click', loadGraph);
  document.querySelectorAll('.sb-item[data-page="graph"]').forEach(item => item.addEventListener('click', loadGraph));
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loadGraph);
  else loadGraph();
})();
