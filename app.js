/* ============================================================
   PQSensing — interactive V_norm slope-null demonstration
   Pedagogical model of the NSL thesis.

   P(δ)      = (1 + cos δ) / 2
   N_band(δ) = N_FLOOR + A_excess · (1 + cos(δ - δ_off))/2
                       + A_jitter · sin²(δ) / 4
   V_norm(δ) = N_band(δ) / max(P(δ), ε)^k

   Story: the power lock parks at δ = 0 (fringe maximum). The
   slope-null of V_norm sits somewhere else whenever the
   structured-noise term is misaligned with the fringe.
   ============================================================ */
(function () {
  'use strict';
  const plotEl = document.getElementById('exhibitPlot');
  if (!plotEl) return;

  // ----- model constants -----
  const N_FLOOR  = 0.04;
  const A_JITTER = 0.06;
  const EPS      = 0.01;
  const N        = 401;
  const dRange   = [-Math.PI, Math.PI];

  // ----- plot geometry -----
  const VB = { w: 800, h: 480, padL: 60, padR: 30, padT: 30, padB: 60 };
  const PX = VB.padL;
  const PW = VB.w - VB.padL - VB.padR;
  const PY = VB.padT;
  const PH = VB.h - VB.padT - VB.padB;

  // ----- palette (matches styles.css tokens) -----
  const C = {
    cyan:   '#39dfff',
    gold:   '#e8c27a',
    teal:   '#49f4c8',
    muted:  'rgba(167,196,216,0.55)',
    line:   'rgba(57,223,255,0.10)',
    inkSub: 'rgba(167,196,216,0.85)',
  };

  // ----- DOM hooks -----
  const ctrlOffset = document.getElementById('ctrlOffset');
  const ctrlAmp    = document.getElementById('ctrlAmp');
  const ctrlK      = document.getElementById('ctrlK');
  const outOffset  = document.getElementById('outOffset');
  const outAmp     = document.getElementById('outAmp');
  const outK       = document.getElementById('outK');
  const readPowerDelta = document.getElementById('readPowerDelta');
  const readPowerVnorm = document.getElementById('readPowerVnorm');
  const readNSLDelta   = document.getElementById('readNSLDelta');
  const readNSLVnorm   = document.getElementById('readNSLVnorm');
  const readGain       = document.getElementById('readGain');

  // ----- math -----
  function P(d) { return 0.5 * (1 + Math.cos(d)); }
  function Nband(d, off, amp) {
    return N_FLOOR
         + amp * 0.5 * (1 + Math.cos(d - off))
         + A_JITTER * Math.sin(d) * Math.sin(d) * 0.25;
  }
  function Vnorm(d, off, amp, k) {
    const p = Math.max(P(d), EPS);
    return Nband(d, off, amp) / Math.pow(p, k);
  }
  function linspace(a, b, n) {
    const out = new Array(n);
    const dx = (b - a) / (n - 1);
    for (let i = 0; i < n; i++) out[i] = a + i * dx;
    return out;
  }
  function findMin(arr, allowedFn) {
    let bestI = -1, bestV = Infinity;
    for (let i = 0; i < arr.length; i++) {
      if (allowedFn && !allowedFn(i)) continue;
      if (arr[i] < bestV) { bestV = arr[i]; bestI = i; }
    }
    return { i: bestI, v: bestV };
  }
  function findMax(arr) {
    let bestI = -1, bestV = -Infinity;
    for (let i = 0; i < arr.length; i++) {
      if (arr[i] > bestV) { bestV = arr[i]; bestI = i; }
    }
    return { i: bestI, v: bestV };
  }

  function xMap(d) {
    return PX + ((d - dRange[0]) / (dRange[1] - dRange[0])) * PW;
  }
  function fmtDelta(d) {
    const piFrac = d / Math.PI;
    if (Math.abs(piFrac) < 0.005) return 'δ = 0';
    const sign = piFrac < 0 ? '−' : '';
    return 'δ = ' + sign + Math.abs(piFrac).toFixed(2) + 'π';
  }
  function fmtV(v) {
    if (!isFinite(v)) return '—';
    if (v < 0.01) return v.toExponential(2);
    return v.toFixed(3);
  }

  function buildScaffold() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', `0 0 ${VB.w} ${VB.h}`);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

    svg.innerHTML = `
      <defs>
        <linearGradient id="gradP" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${C.cyan}" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="${C.cyan}" stop-opacity="0"/>
        </linearGradient>
      </defs>

      <g stroke="${C.line}" stroke-width="0.8">
        <line x1="${PX}" y1="${PY}"           x2="${PX + PW}" y2="${PY}"/>
        <line x1="${PX}" y1="${PY + PH/4}"    x2="${PX + PW}" y2="${PY + PH/4}" stroke-dasharray="2 4"/>
        <line x1="${PX}" y1="${PY + PH/2}"    x2="${PX + PW}" y2="${PY + PH/2}" stroke-dasharray="2 4"/>
        <line x1="${PX}" y1="${PY + 3*PH/4}"  x2="${PX + PW}" y2="${PY + 3*PH/4}" stroke-dasharray="2 4"/>
        <line x1="${PX}" y1="${PY + PH}"      x2="${PX + PW}" y2="${PY + PH}"/>
        <line x1="${xMap(-Math.PI/2).toFixed(1)}" y1="${PY}" x2="${xMap(-Math.PI/2).toFixed(1)}" y2="${PY + PH}" stroke-dasharray="2 4"/>
        <line x1="${xMap(0).toFixed(1)}"          y1="${PY}" x2="${xMap(0).toFixed(1)}"          y2="${PY + PH}"/>
        <line x1="${xMap(Math.PI/2).toFixed(1)}"  y1="${PY}" x2="${xMap(Math.PI/2).toFixed(1)}"  y2="${PY + PH}" stroke-dasharray="2 4"/>
      </g>

      <g font-family="'IBM Plex Mono', monospace" font-size="11" fill="${C.muted}" letter-spacing="0.04em">
        <text x="${PX}" y="${VB.h - 18}" text-anchor="start">−π</text>
        <text x="${xMap(-Math.PI/2).toFixed(1)}" y="${VB.h - 18}" text-anchor="middle">−π/2</text>
        <text x="${xMap(0).toFixed(1)}" y="${VB.h - 18}" text-anchor="middle">0</text>
        <text x="${xMap(Math.PI/2).toFixed(1)}" y="${VB.h - 18}" text-anchor="middle">π/2</text>
        <text x="${PX + PW}" y="${VB.h - 18}" text-anchor="end">π</text>
        <text x="${PX + PW/2}" y="${VB.h - 4}" text-anchor="middle" font-style="italic">detuning δ</text>
        <text x="20" y="${PY + PH/2}" text-anchor="middle" transform="rotate(-90 20 ${PY + PH/2})" font-style="italic">normalized amplitude</text>
      </g>

      <path id="exFillP" fill="url(#gradP)" stroke="none"/>

      <path id="exPathP" fill="none" stroke="${C.cyan}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" opacity="0.7"/>
      <path id="exPathN" fill="none" stroke="${C.gold}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>
      <path id="exPathV" fill="none" stroke="${C.teal}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>

      <line id="exGuidePower" stroke="${C.cyan}" stroke-width="1" stroke-dasharray="3 4" opacity="0.5"/>
      <line id="exGuideNSL"   stroke="${C.teal}" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.85"/>

      <g id="exMarkPower">
        <circle r="7" fill="#04101e" stroke="${C.cyan}" stroke-width="1.6"/>
        <circle r="3" fill="${C.cyan}"/>
      </g>
      <g id="exMarkNSL">
        <circle r="9" fill="#04101e" stroke="${C.teal}" stroke-width="2"/>
        <path d="M0,-5L1.4,-1.6L5,-1.6L2.1,0.7L3.2,4.5L0,2.4L-3.2,4.5L-2.1,0.7L-5,-1.6L-1.4,-1.6Z" fill="${C.teal}"/>
      </g>

      <g id="exLabelPower" font-family="'IBM Plex Mono', monospace" font-size="11" letter-spacing="0.06em" fill="${C.cyan}">
        <text x="0" y="-14" text-anchor="middle" font-weight="500">PDH lock</text>
      </g>
      <g id="exLabelNSL" font-family="'IBM Plex Mono', monospace" font-size="11" letter-spacing="0.06em" fill="${C.teal}">
        <text x="0" y="-16" text-anchor="middle" font-weight="600">NSL lock</text>
      </g>

      <g id="exGap" opacity="0">
        <line x1="0" y1="0" x2="0" y2="0" stroke="${C.inkSub}" stroke-width="0.8" stroke-dasharray="2 3"/>
        <text font-family="'IBM Plex Mono', monospace" font-size="10" letter-spacing="0.08em" fill="${C.inkSub}"
              text-anchor="middle" font-style="italic">Δδ</text>
      </g>
    `;

    plotEl.innerHTML = '';
    plotEl.appendChild(svg);
  }

  function update() {
    const offsetRaw = parseFloat(ctrlOffset.value) / 100;
    const offset    = (offsetRaw * 2 - 1) * Math.PI;
    const amp       = parseFloat(ctrlAmp.value) / 100;
    const k         = parseFloat(ctrlK.value) / 100;

    const piFrac = offset / Math.PI;
    outOffset.textContent = (piFrac >= 0 ? '+' : '−') + Math.abs(piFrac).toFixed(2) + 'π';
    outAmp.textContent    = amp.toFixed(2);
    outK.textContent      = 'k = ' + k.toFixed(2);

    const xs = linspace(dRange[0], dRange[1], N);
    const ps = xs.map(d => P(d));
    const ns = xs.map(d => Nband(d, offset, amp));
    const vs = xs.map(d => Vnorm(d, offset, amp, k));

    const vsSorted = [...vs].sort((a, b) => a - b);
    const v99 = vsSorted[Math.floor(N * 0.97)];
    const vDisplayMax = Math.min(v99, vsSorted[N - 1]);

    const pMax = 1.0;
    const nMax = Math.max(...ns) * 1.08;
    const vMax = vDisplayMax * 1.06;

    function yP(v) { return PY + PH - (v / pMax) * PH * 0.92; }
    function yN(v) { return PY + PH - (v / nMax) * PH * 0.92; }
    function yV(v) {
      const clamped = Math.min(v, vMax);
      return PY + PH - (clamped / vMax) * PH * 0.92;
    }

    const pathP = xs.map((d, i) => `${i === 0 ? 'M' : 'L'}${xMap(d).toFixed(2)},${yP(ps[i]).toFixed(2)}`).join('');
    const pathN = xs.map((d, i) => `${i === 0 ? 'M' : 'L'}${xMap(d).toFixed(2)},${yN(ns[i]).toFixed(2)}`).join('');

    // V_norm broken where P falls below the controller's effective power floor —
    // mirrors the power-floor penalty in the real loop and avoids ugly walls.
    const P_FLOOR_DRAW = 0.12;
    let pathV = '';
    let inSegment = false;
    for (let i = 0; i < xs.length; i++) {
      if (ps[i] >= P_FLOOR_DRAW) {
        pathV += (inSegment ? 'L' : 'M') + xMap(xs[i]).toFixed(2) + ',' + yV(vs[i]).toFixed(2);
        inSegment = true;
      } else {
        inSegment = false;
      }
    }

    const baselineY = PY + PH;
    const fillP = pathP + `L${xMap(dRange[1]).toFixed(2)},${baselineY}L${xMap(dRange[0]).toFixed(2)},${baselineY}Z`;

    document.getElementById('exFillP').setAttribute('d', fillP);
    document.getElementById('exPathP').setAttribute('d', pathP);
    document.getElementById('exPathN').setAttribute('d', pathN);
    document.getElementById('exPathV').setAttribute('d', pathV);

    const idxPmax = findMax(ps).i;
    const allowed = (i) => ps[i] > 0.18;
    const idxV = findMin(vs, allowed).i;

    const dPower = xs[idxPmax];
    const dNSL   = xs[idxV];
    const vAtPower = vs[idxPmax];
    const vAtNSL   = vs[idxV];

    const xPower = xMap(dPower);
    const xNSL   = xMap(dNSL);
    const yMarkP = yP(ps[idxPmax]);
    const yMarkN = yV(vs[idxV]);

    document.getElementById('exGuidePower').setAttribute('x1', xPower);
    document.getElementById('exGuidePower').setAttribute('x2', xPower);
    document.getElementById('exGuidePower').setAttribute('y1', PY);
    document.getElementById('exGuidePower').setAttribute('y2', PY + PH);
    document.getElementById('exGuideNSL').setAttribute('x1', xNSL);
    document.getElementById('exGuideNSL').setAttribute('x2', xNSL);
    document.getElementById('exGuideNSL').setAttribute('y1', PY);
    document.getElementById('exGuideNSL').setAttribute('y2', PY + PH);

    document.getElementById('exMarkPower').setAttribute('transform', `translate(${xPower},${yMarkP})`);
    document.getElementById('exMarkNSL').setAttribute('transform', `translate(${xNSL},${yMarkN})`);
    document.getElementById('exLabelPower').setAttribute('transform', `translate(${xPower},${yMarkP})`);
    document.getElementById('exLabelNSL').setAttribute('transform', `translate(${xNSL},${yMarkN})`);

    const gapEl = document.getElementById('exGap');
    if (Math.abs(dPower - dNSL) > 0.05) {
      const gapY = PY + PH - 12;
      const midX = (xPower + xNSL) / 2;
      gapEl.setAttribute('opacity', 0.55);
      gapEl.children[0].setAttribute('x1', xPower);
      gapEl.children[0].setAttribute('x2', xNSL);
      gapEl.children[0].setAttribute('y1', gapY);
      gapEl.children[0].setAttribute('y2', gapY);
      gapEl.children[1].setAttribute('x', midX);
      gapEl.children[1].setAttribute('y', gapY - 5);
    } else {
      gapEl.setAttribute('opacity', 0);
    }

    readPowerDelta.textContent = fmtDelta(dPower);
    readPowerVnorm.innerHTML   = 'V<sub>norm</sub> there = ' + fmtV(vAtPower);
    readNSLDelta.textContent   = fmtDelta(dNSL);
    readNSLVnorm.innerHTML     = 'V<sub>norm</sub> there = ' + fmtV(vAtNSL);

    if (vAtNSL > 0 && isFinite(vAtPower) && isFinite(vAtNSL)) {
      const dB = 10 * Math.log10(vAtPower / vAtNSL);
      readGain.textContent = (dB > 0.05 ? '+' : '') + dB.toFixed(2) + ' dB';
    } else {
      readGain.textContent = '— dB';
    }
  }

  function attach() {
    [ctrlOffset, ctrlAmp, ctrlK].forEach(el => {
      el.addEventListener('input', update);
      el.addEventListener('change', update);
    });
  }

  buildScaffold();
  attach();
  update();

  let resizeT;
  window.addEventListener('resize', () => {
    clearTimeout(resizeT);
    resizeT = setTimeout(update, 120);
  });
})();
