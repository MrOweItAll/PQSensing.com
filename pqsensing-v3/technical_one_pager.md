# PQSensing — NSL + DPI Website One-Pager

## Plain-language positioning
PQSensing develops Noise-Stationary Locking (NSL) and Phase-Controlled Dark-Mode Injection (DPI), a PDH-compatible measurement-performance layer for interferometric sensors.

**PDH locks the resonance. NSL locks measurement quality. DPI activates the dark port.**

## What we are trying to do
We are trying to keep precision interferometric sensors at the operating point where photons, integration time, and quantum-noise resources produce the most usable measurement information.

A conventional optical lock can hold a cavity resonance, fringe point, reflected-power null, or transmitted-power peak. That is necessary, but it does not guarantee that the measurement-band noise is minimized or stationary. NSL adds a second layer that directly monitors normalized measurement-band noise and controls the operating point toward a noise-stationary condition.

## Why we are doing it
A sensor’s useful output is not optical power. It is an estimate with an uncertainty, such as:

    x_hat ± sigma_x
    phi_hat ± Delta_phi

For a photon-limited phase measurement:

    (Delta_phi)^2 ≈ V_norm / (N_dot T)

Lower and more stable V_norm means the same photon flux and integration time can produce a smaller error bar. The goal is not uncertainty control for its own sake. The goal is to make integration time productive.

## How NSL works
1. Acquire detector signal y(t).
2. Estimate band-limited noise N_band over the protected measurement band.
3. Estimate optical power metric P.
4. Compute normalized noise objective:

    V_norm = N_band / P^k

5. Apply a small dither to operating parameter delta outside the protected measurement band.
6. Synchronously demodulate V_norm against the dither to estimate dV_norm/delta.
7. Servo delta toward:

    dV_norm/delta ≈ 0

At this noise-stationary point, first-order conversion of detuning jitter into normalized measurement noise is suppressed.

## What DPI adds
DPI uses the nominally dark port as a controlled injection channel. The injected field may carry a phase waveform g(t), pilot tone, chirp, code, coherent auxiliary field, or squeezed vacuum. The output signature can be recovered using synchronous detection, correlation, matched filtering, or homodyne readout.

Use cases include calibration, code-division signatures, multiplexing, interference rejection, ranging or timing signatures, squeezed-light injection, and quadrature/noise-shaping control.

## What this can help measure
NSL + DPI is aimed at weak interferometric signals that are too noisy, too slow, or too unstable to recover reliably with optical power locking alone. Candidate measurement categories include:

- Displacement and vibration
- Strain and deformation
- Acceleration, force, pressure, and acoustic motion
- Rotation and inertial drift
- Refractive-index, chemical, and biological changes
- Quantum-enhanced weak phase shifts
- Timing, ranging, and coded dark-port signatures

## First validation sprint
Build a classical tabletop Mach-Zehnder interferometer, sweep delta, map P(delta), N_band(delta), and V_norm(delta), inject controlled detuning jitter, and compare a conventional power lock against NSL.

Prototype targets:

- Show a V_norm stationary point distinct from the power extremum in at least one noise regime.
- First-demo target: at least 6 dB lower jitter-induced V_norm than power lock.
- Stretch target: 10–20 dB if bench stability supports it.
- Maintain power above a useful floor.
- Complete at least 5 disturbance/reacquisition trials.
- Optional DPI test: recover a known g(t) signature by correlation or matched filtering.

## Website one-liner
NSL + DPI is designed for interferometers that are optically locked but not necessarily measurement-optimized. It helps keep the sensor where integration time produces usable information instead of accumulated noise.


## Seeking collaboration
PQSensing is seeking a university lab, metrology partner, instrument company, or technical sponsor to help validate Noise-Stationary Locking on a classical tabletop interferometer.

The first experiment should compare a conventional PDH, power, or PID-style lock against a normalized noise-objective lock under controlled vibration, thermal drift, and phase/path-length disturbance.

**What we have:** a filed patent application, simulation models, control logic, draft validation protocol, and a lean $10K prototype/data-sprint plan.

**What we need:** access to an optical bench or Mach-Zehnder/cavity setup, photodetector readout, PZT or phase actuator, DAQ/controller support, and technical guidance on a defensible first validation.

**What a partner gets:** a focused applied optics/control project, possible student-useful data, early visibility into Kansas-origin photonics IP, and a clear sponsored-research or prototype path if the traces are interesting.

**Current ask:** a 20–30 minute feasibility call to decide whether this fits as a small sponsored test, student project, supervised lab exercise, or vendor application note.
