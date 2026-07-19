/* ============================================================
   PQSensing — NSL pedagogical model (framework-agnostic core)

   Pure, dependency-free functions describing the Noise-Stationary
   Locking thesis. Imported by the interactive island (browser) AND
   the Vitest suite (Node), so the demo and its tests exercise the
   exact same math.

     P(delta)      = (1 + cos delta) / 2
     N_band(delta) = N_FLOOR
                     + A_excess * (1 + cos(delta - delta_off)) / 2
                     + A_jitter * sin^2(delta) / 4
     V_norm(delta) = N_band(delta) / max(P(delta), eps)^k

   Story: the power lock parks at delta = 0 (the fringe maximum).
   The slope-null of V_norm sits elsewhere whenever the structured
   noise term is misaligned with the fringe.
   ============================================================ */

export const N_FLOOR = 0.04;
export const A_JITTER = 0.06;
export const EPS = 0.01;

/** Optical transmission / fringe power, normalized to [0, 1]. */
export function P(d) {
  return 0.5 * (1 + Math.cos(d));
}

/** Measurement-band noise: floor + misaligned structured excess + fringe jitter. */
export function Nband(d, off, amp) {
  return (
    N_FLOOR +
    amp * 0.5 * (1 + Math.cos(d - off)) +
    A_JITTER * Math.sin(d) * Math.sin(d) * 0.25
  );
}

/** The NSL objective: normalized measurement-band noise. */
export function Vnorm(d, off, amp, k) {
  const p = Math.max(P(d), EPS);
  return Nband(d, off, amp) / Math.pow(p, k);
}

export function linspace(a, b, n) {
  const out = new Array(n);
  const dx = (b - a) / (n - 1);
  for (let i = 0; i < n; i++) out[i] = a + i * dx;
  return out;
}

export function findMin(arr, allowedFn) {
  let bestI = -1;
  let bestV = Infinity;
  for (let i = 0; i < arr.length; i++) {
    if (allowedFn && !allowedFn(i)) continue;
    if (arr[i] < bestV) {
      bestV = arr[i];
      bestI = i;
    }
  }
  return { i: bestI, v: bestV };
}

export function findMax(arr) {
  let bestI = -1;
  let bestV = -Infinity;
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] > bestV) {
      bestV = arr[i];
      bestI = i;
    }
  }
  return { i: bestI, v: bestV };
}

/**
 * Sample the model across delta in [-pi, pi] and locate both lock points.
 *
 * Returns the sampled arrays plus:
 *   dPower  — where a power/PDH lock parks (fringe power maximum)
 *   dNSL    — where the NSL objective is stationary (V_norm minimum,
 *             restricted to a usable power floor)
 *   gainDb  — 10*log10(V_norm@power / V_norm@NSL); the NSL advantage
 */
export function computeLocks(offset, amp, k, N = 401) {
  const dRange = [-Math.PI, Math.PI];
  const xs = linspace(dRange[0], dRange[1], N);
  const ps = xs.map((d) => P(d));
  const ns = xs.map((d) => Nband(d, offset, amp));
  const vs = xs.map((d) => Vnorm(d, offset, amp, k));

  const idxPmax = findMax(ps).i;
  // Restrict the NSL search to points where enough optical power survives —
  // the controller enforces a power floor rather than chasing a dark fringe.
  const allowed = (i) => ps[i] > 0.18;
  const idxV = findMin(vs, allowed).i;

  const dPower = xs[idxPmax];
  const dNSL = xs[idxV];
  const vAtPower = vs[idxPmax];
  const vAtNSL = vs[idxV];

  const gainDb =
    vAtNSL > 0 && isFinite(vAtPower) && isFinite(vAtNSL)
      ? 10 * Math.log10(vAtPower / vAtNSL)
      : null;

  return {
    xs, ps, ns, vs,
    idxPmax, idxV,
    dPower, dNSL, vAtPower, vAtNSL, gainDb,
  };
}
