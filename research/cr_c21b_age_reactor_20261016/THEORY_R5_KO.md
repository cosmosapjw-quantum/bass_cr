# C21B: source-age-aware positive H/He photon reaction, constructive R5

## Authority, question and boundaries (2026-10-16 KST)

- `bass_cr` PR75 head `6eda7834abb33750439e4316916b06cc2885b9fc`: FLRW common-q, MD14 GL2, conditional opacity oracle.
- `bass_cr` PR74 head `caf587b3edf4e27d038c6a918419be498d7d389c`: exact C20 Rust source and 20 original NCP cases (frozen ion fractions).
- User-reported C21 native epoch bridge commit `807a46029cd2ebca16ab58cc3d92669277be3c00`, 3/3 tests on NCP. This run has **not** fetched/executed that NCP source.
- `rei_bianchi` PR160 / PR162 / PR163: native Case-A thermo-chemical ownership, exact backward-Euler birth/old cancellation identity, and native source-on still first-order, respectively. Don't silently duplicate or replace these.
- Independent literature relevant to numerical methodology: Friedrich et al. (2012) *Radiative transfer of energetic photons: X-rays and helium ionization in C2-Ray*, DOI 10.1111/j.1365-2966.2012.20449.x; Norman et al. (2015) *Fully coupled simulation of cosmic reionization. I*, DOI 10.1088/0067-0049/216/1/16; Pawlik & Schaye (2011) *Multifrequency, thermally coupled radiative transfer with TRAPHIC*, DOI 10.1111/j.1365-2966.2010.18032.x. These establish photon-conserving methods, not the correctness of this new implementation.

**New narrow research question.** Construct and quantitatively test a nonnegative, age-tagged, multigroup H I/He I/He II photo-reaction integrator with changing gas opacities, physical FLRW redshift, original Verner fit and MD14 emissivity. Isolate it from the untested Case-A native thermal RHS; produce an independent SciPy reference and an explicit adapter contract.

## Variables, units and exact pair map

Use x=ln a, dt=dx/H(a) in proper seconds. Let `Y=nHe,total/nH,total`, and `a*=1/21`. Each photon packet i has birth x_i, birth physical E_i, canonical `q_i=a_i E_i`, reference `qref_i=q_i/a*`, and nonnegative `N_i` **photons per total H nucleus**. Physical energy `E_i(x)=q_i exp(-x)` eV. For one packet and absorber species j, define population per total H:

A_HI = 1-x_HII,
A_HeI = Y(1-x_HeII-x_HeIII),
A_HeII = Y x_HeII.

At frozen midpoint scale a_m, `k_ij = c nH,total(a_m) sigma_j(E_i(a_m))` [s^-1 per dimensionless absorber/H]. The **joint dynamic subreaction**, for an individual packet and individual absorber,

`dN/dt=-k N A`, `dA/dt=-k N A`,

preserves `D=N-A`; its lost packet number equals ionizations of that absorber per total H. With `m=min(N0,A0)`, `d=abs(N0-A0)`, `M=m+d`, `z=k*d*dt`, define the nonnegative ratio `eta=-expm1(-z)/d` for d>0 and `eta=k*dt` at d=0. Then

`m_new = m*exp(-z)/(1+m*eta)`;
`M_new = d+m_new`;
`lost = m-m_new`, `N_new=N0-lost`, `A_new=A0-lost`.

If z is large, compute `exp(-z)` directly (underflow to 0 is physically admissible); `expm1` avoids cancellation at z<<1. At d=0 the exact limit is `m_new=m/(1+k*m*dt)`. All terms are nonnegative for k,dt,m,d>=0; both species have exactly equal losses. There is no post-update clipping. If absorber=0 or stock=0, the map is the identity.

For helium, individual exact pair updates convert HeI→HeII and HeII→HeIII; each update preserves total He/H=Y. Photoheat per event = `(E_mid-I_j)` eV, with true ionization binding energies `I=[13.598434599702,24.587389011,54.41776]` eV, whereas Verner cross-section activation cutoffs are `[13.60,24.59,54.42]` eV; treat them separately. Atomic rates are evaluated from the original Verner (1996) fitting form, not E^-3 surrogate. Binding per H is

`B=I_H xHII + Y[I_HeI(xHeII+xHeIII)+I_HeII xHeIII]`.

At each subreaction: `delta U_gamma=-lost*E_mid`, `delta B=lost*I_j`, `delta w_thermal=lost*(E_mid-I_j)`. Thus `delta(U_gamma+B+w)=0` at fixed geometry, per pair and for the composition.

## Source birth and redshift: separated owners

At each parent time cell [x0,x1], represent original positive MD14 proper emissivity j(a)=fesc 10^log_yield psi(z)/(MPC_CM^3 nH0) photons/(H nucleus*s), with psi(z) from native `axbi_sources.rs`. GL2 in x places two separate source births at `x_b=x_mid +/- dx/(2sqrt(3))`, with packet count `w_b dx*j(a_b)/H(a_b)*f_s` per chosen positive spectral source quadrature weight f_s. Store birth x_b and q=a_b E_s; **do not relabel both births as a single midpoint cohort**.

For every subinterval between birth events and redshifted fit-cut crossings, use symmetric `G(dt/2) R(dt) G(dt/2)`, where G maps E=q/a and gas adiabatic `w→w*(a_old/a_new)^2` with their respective photon-work and gas-work ledgers. R is the palindromic composition of **all** exact pair maps at the reaction midpoint, each at half duration in forward then reverse order. This is a positive, self-adjoint frozen-coefficient second-order split in smooth intervals. Under changing rates use the midpoint; global O(dt^2) requires smoothness and sufficiently controlled quadrature, which must be tested, not asserted for moving threshold/birth discontinuities.

Split subintervals at every active packet's `xcrit=ln(q/E_fit_j)` with x0<xcrit<x1. At the crossing equality, evaluate the Verner fit using the original `E<E_fit -> sigma=0` convention; no interval crosses a discontinuity. The threshold count is a diagnostic, not photon creation or loss.

`G`: no photon-number changes. For expansion, `delta W_gamma=Sum_i N_i(E_before-E_after)`. Gas adiabatic work `delta W_gas=w_before-w_after` is tracked once (the photo-reaction operator excludes Hubble cooling). This remains a scalar FLRW-only expression. No signed Bianchi recoil claim.

Overall (photo-only, no recombination, no CMB) discrete identities:

`N0 + S_N - N1 - sum_j A_j = 0`;
`Ugamma0 + S_U - Ugamma1 - (B1-B0) - (w1-w0) - W_gamma - W_gas=0`.

A source at birth has energy E_birth, not its redshifted endpoint energy. This identity is independent of timestep accuracy; convergence against an independent ODE is separately required. Native future interface: `Gamma_j=A_j/(dt alpha_j)` and `photoheat_per_absorber_s=heat_j*EV_ERG/(dt alpha_j)` for `alpha=[A_HI,A_HeI,A_HeII]` evaluated consistently with the implicit native trial state; nonzero A with zero alpha must **HOLD**. Native RHS `h=0` when external geometry applies gas work.

## Symbolic check evidence

Wolfram Language on 2026-10-16: for `m,d,k,t>0`, `m(t)=m*d*Exp[-k*d*t]/(d+m(1-Exp[-k*d*t]))`, checks (initial value, derivative `m' + k m(m+d)`, equal-stock limit `d→0`, photon number and energy algebraic balances) yielded exactly `{0,0,0,0,0}`. Transient `Power::infy`/`Infinity::indet` messages appeared while Wolfram evaluated an intermediate limit, but the final simplified limit was zero. Derivation is native-kernel-independent.

## Claim admission

- `DERIVED`: exact frozen pair map, positivity, stoichiometric ledger, q mapping, birth/cut partition.
- `NOT_YET_RUN` at R5 close: compiled implementation, numerical order, native C21 bridge parity, full H/He Case-A/CI/DR/CMB, native NCP history, Bianchi, observations.
- Do not claim second order across unresolved thresholds or spectrum reconstruction without independent numerical comparisons.
