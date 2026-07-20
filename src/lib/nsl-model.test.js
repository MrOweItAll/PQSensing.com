import { describe, it, expect } from 'vitest';
import {
  P, Nband, Vnorm, linspace, findMin, findMax, computeLocks,
  N_FLOOR, EPS,
} from './nsl-model.js';

describe('fringe power P(delta)', () => {
  it('peaks at delta = 0', () => {
    expect(P(0)).toBeCloseTo(1, 12);
  });
  it('is dark at delta = +/- pi', () => {
    expect(P(Math.PI)).toBeCloseTo(0, 12);
    expect(P(-Math.PI)).toBeCloseTo(0, 12);
  });
  it('is symmetric in delta', () => {
    expect(P(0.7)).toBeCloseTo(P(-0.7), 12);
  });
});

describe('objective V_norm(delta)', () => {
  it('reduces to N_band when k = 0', () => {
    const d = 0.3, off = 0.5, amp = 0.4;
    expect(Vnorm(d, off, amp, 0)).toBeCloseTo(Nband(d, off, amp), 12);
  });
  it('applies the power-floor guard (never divides by zero at the dark fringe)', () => {
    const v = Vnorm(Math.PI, 0.5, 0.4, 2); // P(pi) = 0 -> clamped to EPS
    expect(Number.isFinite(v)).toBe(true);
    expect(v).toBeCloseTo(Nband(Math.PI, 0.5, 0.4) / Math.pow(EPS, 2), 6);
  });
});

describe('helpers', () => {
  it('linspace spans the endpoints inclusively', () => {
    const xs = linspace(-1, 1, 5);
    expect(xs[0]).toBe(-1);
    expect(xs[xs.length - 1]).toBe(1);
    expect(xs.length).toBe(5);
  });
  it('findMax / findMin locate extrema', () => {
    const a = [3, 1, 4, 1, 5, 9, 2];
    expect(findMax(a).v).toBe(9);
    expect(findMin(a).v).toBe(1);
  });
  it('findMin honours the allowed predicate', () => {
    const a = [3, 1, 4, 1, 5];
    const res = findMin(a, (i) => i >= 2); // ignore the leading small values
    expect(res.i).toBe(3);
    expect(res.v).toBe(1);
  });
});

describe('NSL thesis invariants (computeLocks)', () => {
  it('at zero noise offset the NSL setpoint coincides with the power extremum', () => {
    const { dPower, dNSL } = computeLocks(0, 0.6, 1);
    expect(dPower).toBeCloseTo(0, 6);
    // aligned noise -> both locks park at the fringe maximum
    expect(Math.abs(dNSL - dPower)).toBeLessThan(0.05);
  });

  it('with misaligned structured noise the two setpoints diverge', () => {
    const { dPower, dNSL } = computeLocks(Math.PI / 2, 0.8, 1);
    expect(dPower).toBeCloseTo(0, 6);
    expect(Math.abs(dNSL - dPower)).toBeGreaterThan(0.05);
  });

  it('the NSL advantage is always non-negative (it minimizes the objective)', () => {
    for (const off of [-2, -1, 0, 0.3, 1, 2]) {
      for (const amp of [0.2, 0.6, 1.0]) {
        for (const k of [0, 0.5, 1, 2]) {
          const { gainDb } = computeLocks(off, amp, k);
          expect(gainDb).not.toBeNull();
          expect(gainDb).toBeGreaterThanOrEqual(-1e-9);
        }
      }
    }
  });

  it('keeps the NSL lock at a usable power floor (never the dark fringe)', () => {
    const { dNSL } = computeLocks(Math.PI, 1.0, 2);
    expect(P(dNSL)).toBeGreaterThan(0.18);
  });
});
