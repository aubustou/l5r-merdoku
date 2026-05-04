(function () {
  'use strict';

  const STORAGE_KEY = 'merdoku-tweaks';
  const DEFAULTS = {
    cardDensity: 'comfortable',
    showFlavor: true,
    accentColor: '#c9a84c',
    backgroundTexture: 'wood',
  };

  let state = Object.assign({}, DEFAULTS);
  try { Object.assign(state, JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')); } catch (_) {}

  // ── Apply effects ──────────────────────────────────────────────────────────

  function applyAll() {
    const root = document.documentElement;
    const app  = document.getElementById('app');

    // Density → --cols / --cols-extra
    const cols = state.cardDensity === 'compact' ? 7 : state.cardDensity === 'comfortable' ? 5 : 4;
    root.style.setProperty('--cols', cols);
    root.style.setProperty('--cols-extra', cols + 1);

    // Accent color → --bronze
    root.style.setProperty('--bronze', state.accentColor);

    // Background texture
    if (app) {
      app.classList.toggle('wood-bg', state.backgroundTexture === 'wood');
    }

    // Flavor text: toggle .show-flavor class on body
    document.body.classList.toggle('show-flavor', !!state.showFlavor);
  }

  function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (_) {}
  }

  function set(key, value) {
    state[key] = value;
    save();
    applyAll();
    render();
  }

  // ── Panel DOM ──────────────────────────────────────────────────────────────

  let panel = null;
  const offset = { x: 16, y: 16 };
  const PAD = 16;

  function clamp() {
    if (!panel) return;
    const w = panel.offsetWidth, h = panel.offsetHeight;
    offset.x = Math.min(Math.max(PAD, offset.x), Math.max(PAD, window.innerWidth  - w - PAD));
    offset.y = Math.min(Math.max(PAD, offset.y), Math.max(PAD, window.innerHeight - h - PAD));
    panel.style.right  = offset.x + 'px';
    panel.style.bottom = offset.y + 'px';
  }

  function startDrag(e) {
    if (!panel) return;
    const r = panel.getBoundingClientRect();
    const sx = e.clientX, sy = e.clientY;
    const sr = window.innerWidth  - r.right;
    const sb = window.innerHeight - r.bottom;
    function move(ev) {
      offset.x = sr - (ev.clientX - sx);
      offset.y = sb - (ev.clientY - sy);
      clamp();
    }
    function up() {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    }
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
  }

  // ── Segmented radio (drag-capable) ───────────────────────────────────────

  function makeSegmented(opts, key) {
    const track = document.createElement('div');
    track.className = 'twk-seg';

    const thumb = document.createElement('div');
    thumb.className = 'twk-seg-thumb';
    track.appendChild(thumb);

    function updateThumb() {
      const idx = Math.max(0, opts.indexOf(state[key]));
      const n   = opts.length;
      thumb.style.left  = `calc(2px + ${idx} * (100% - 4px) / ${n})`;
      thumb.style.width = `calc((100% - 4px) / ${n})`;
    }

    function segAt(clientX) {
      const r = track.getBoundingClientRect();
      const i = Math.floor(((clientX - r.left - 2) / (r.width - 4)) * opts.length);
      return opts[Math.max(0, Math.min(opts.length - 1, i))];
    }

    track.addEventListener('pointerdown', function (e) {
      track.classList.add('dragging');
      const v0 = segAt(e.clientX);
      if (v0 !== state[key]) set(key, v0);
      function move(ev) {
        const v = segAt(ev.clientX);
        if (v !== state[key]) set(key, v);
      }
      function up() {
        track.classList.remove('dragging');
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', up);
      }
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up);
    });

    opts.forEach(function (opt) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = opt;
      track.appendChild(btn);
    });

    updateThumb();
    return { el: track, update: updateThumb };
  }

  // ── Render panel contents ─────────────────────────────────────────────────

  const _controls = {};

  function render() {
    if (!panel) return;
    // Update segmented thumb positions
    if (_controls.density) _controls.density.update();
    if (_controls.texture)  _controls.texture.update();
    // Update toggle
    if (_controls.flavorToggle) _controls.flavorToggle.dataset.on = state.showFlavor ? '1' : '0';
    // Update color swatch
    if (_controls.accentSwatch) _controls.accentSwatch.value = state.accentColor;
  }

  function buildPanel() {
    panel = document.createElement('div');
    panel.className = 'twk-panel';
    panel.style.right  = offset.x + 'px';
    panel.style.bottom = offset.y + 'px';

    // Header
    const hd = document.createElement('div');
    hd.className = 'twk-hd';
    hd.innerHTML = '<b>Tweaks</b>';
    hd.addEventListener('mousedown', startDrag);
    const closeBtn = document.createElement('button');
    closeBtn.className = 'twk-x';
    closeBtn.textContent = '✕';
    closeBtn.addEventListener('mousedown', function (e) { e.stopPropagation(); });
    closeBtn.addEventListener('click', hidePanel);
    hd.appendChild(closeBtn);
    panel.appendChild(hd);

    // Body
    const body = document.createElement('div');
    body.className = 'twk-body';

    // Section: Layout
    const s1 = document.createElement('div');
    s1.className = 'twk-sect';
    s1.textContent = 'Layout';
    body.appendChild(s1);

    // Card density
    const densRow = document.createElement('div');
    densRow.className = 'twk-row';
    const densLbl = document.createElement('div');
    densLbl.className = 'twk-lbl';
    densLbl.innerHTML = '<span>Card Density</span>';
    densRow.appendChild(densLbl);
    _controls.density = makeSegmented(['compact', 'comfortable', 'spacious'], 'cardDensity');
    densRow.appendChild(_controls.density.el);
    body.appendChild(densRow);

    // Show flavor
    const flavRow = document.createElement('div');
    flavRow.className = 'twk-row twk-row-h';
    const flavLbl = document.createElement('div');
    flavLbl.className = 'twk-lbl';
    flavLbl.innerHTML = '<span>Show Flavor Text</span>';
    flavRow.appendChild(flavLbl);
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'twk-toggle';
    toggle.dataset.on = state.showFlavor ? '1' : '0';
    toggle.innerHTML = '<i></i>';
    toggle.addEventListener('click', function () { set('showFlavor', !state.showFlavor); });
    _controls.flavorToggle = toggle;
    flavRow.appendChild(toggle);
    body.appendChild(flavRow);

    // Background texture
    const bgRow = document.createElement('div');
    bgRow.className = 'twk-row';
    const bgLbl = document.createElement('div');
    bgLbl.className = 'twk-lbl';
    bgLbl.innerHTML = '<span>Background</span>';
    bgRow.appendChild(bgLbl);
    _controls.texture = makeSegmented(['wood', 'plain'], 'backgroundTexture');
    bgRow.appendChild(_controls.texture.el);
    body.appendChild(bgRow);

    // Section: Color
    const s2 = document.createElement('div');
    s2.className = 'twk-sect';
    s2.textContent = 'Color';
    body.appendChild(s2);

    // Accent color
    const accentRow = document.createElement('div');
    accentRow.className = 'twk-row twk-row-h';
    const accentLbl = document.createElement('div');
    accentLbl.className = 'twk-lbl';
    accentLbl.innerHTML = '<span>Accent Color</span>';
    accentRow.appendChild(accentLbl);
    const swatch = document.createElement('input');
    swatch.type = 'color';
    swatch.className = 'twk-swatch';
    swatch.value = state.accentColor;
    swatch.addEventListener('input', function (e) { set('accentColor', e.target.value); });
    _controls.accentSwatch = swatch;
    accentRow.appendChild(swatch);
    body.appendChild(accentRow);

    panel.appendChild(body);
    document.body.appendChild(panel);

    // Clamp on resize
    const ro = typeof ResizeObserver !== 'undefined'
      ? new ResizeObserver(clamp)
      : null;
    if (ro) ro.observe(document.documentElement);
    else window.addEventListener('resize', clamp);

    clamp();
  }

  function showPanel() {
    if (!panel) buildPanel();
    panel.style.display = 'flex';
  }

  function hidePanel() {
    if (panel) panel.style.display = 'none';
  }

  // ── Init ───────────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', function () {
    applyAll();

    const gearBtn = document.getElementById('tweaks-gear');
    if (gearBtn) {
      gearBtn.addEventListener('click', function () {
        if (!panel || panel.style.display === 'none') showPanel();
        else hidePanel();
      });
    }
  });

  window.merdokuTweaks = { show: showPanel, hide: hidePanel };
})();
