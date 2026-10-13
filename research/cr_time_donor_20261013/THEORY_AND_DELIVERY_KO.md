# BASS_CR: 실제 시간과 새 donor의 오차 (2026-10-13)

연구 단위 `CR_TIME_DONOR_20261013`. SG_NONLINEAR_TIME_AND_DONOR_STEP의 고정 collision subinterval을 완료했다. physmath-research-loop 1.1.0의 실제 규약을 읽고 R1–R10을 수행했으며, 검증 독립성은 저자 검토 + 별도 CAS/산술이다. 외부 독립 심사는 미수행이다.

## 전체 보고서와 재현 자료

[10쪽 보고서·LaTeX·전체 코드·입력·검산 ZIP](https://drive.google.com/file/d/1f0154gLWC7f8vjcAJeX2ybDjoo-OMeRw/view?usp=drivesdk)

- File: `BASS_CR_TIME_DONOR_20261013_SOURCE.zip`.
- 3,068,042 bytes / 120 members / font binaries 0.
- SHA256: `b1c2aed364c03cfd4d583d6014b361fbc0b1b0a764426d1479f55ef840950b63`.
- Manifest SHA256: `e93c74e3ef967dfb8e9fd92f54aded848cacdae64507bbbb549ed6ea637cb49e`.
- Drive ID: `1f0154gLWC7f8vjcAJeX2ybDjoo-OMeRw`; parent `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`.
- Dropbox ID: `id:BSpOijBcT10AAAAAAD4iFw`; path `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_TIME_DONOR_20261013_SOURCE.zip`.
- Both providers returned successful completion; metadata matched filename, ID/path, exact byte count and Drive parent. R1 metadata verification, not remote raw-byte restoration. Optional Drive checksums were not exposed.

Git contains this mathematical summary and the tested stable convolution module with unit tests. Complete report, source-bound arrays, scalar/xAct inputs and results, outward arithmetic and refinement drivers are in the immutable ZIP. Embedded HANDOFF is archive-stage; this document appends actual publication and provider completion without changing scientific bytes.

## 1. Scope and actual source

Reuse the SG fixed post-G1 snapshot, with proper volume 1.0060180360540648648 m^3, parent energies 29.949811915311845 eV and 0.994297537427849 eV, initial parent counts1+1, HI7/HeI3/HII3, thermal electron1, nuclei13, and initial temperature99.600798934399147236 K. Fixed prefix23 has cutoff between0.17115625 and0.17425 eV. The mathematical comparison model admits HI/HeI ionization and Coulomb downward stopping for all active donors. No excitation/recombination, external source, recoil or moving geometry is added.

The stored full HI/HeI sharing profiles are reused. New work evaluates total rates and derivatives at4,739 energy coordinates; no full9600-column generator is built. Original binary64 coefficients are exact inputs of this bounded finite model. Active mean spectra are retained; thermal count and energy are completed by beta_a=2-sum_j M_ja and e_a=E_P-B_a-sum_j E_j M_ja. The tiny differences from separately rounded old thermal accumulators are explicitly recorded in MODEL.json, not hidden as unchanged input.

## 2. Actual-time exposure solution

Let x_a be ionization extents, z_P the original ionizing parent's stopping extent, s the separate slow-parent extent. P=A0-sum_a x_a-z_P and N_e=N_e0+sum_a beta_a x_a. The first-event surrogate satisfies

$$\dot x_a=\kappa_a P(X_{a0}-x_a)/V,\quad\dot z_P=\lambda_P(N_e/V)P,\quad\dot s=\lambda_S(N_e/V)(S0-s).$$

Set qdot=P/V. Then

$$x_a(q)=X_{a0}(1-e^{-\kappa_aq}),\quad z_P(q)=V\int_0^q\lambda_P(N_e(v)/V)dv,$$
$$P(q)=A0-\sum_a x_a(q)-z_P(q),\quad t(q)=V\int_0^q\frac{dv}{P(v)},$$
$$s(q)=S0\left[1-\exp\left(-V\int_0^q\frac{\lambda_S(N_e(v)/V)}{P(v)}dv\right)\right].$$

On P>0 the proper-time map is strictly increasing. The zero-rate limits are continuous. Every retained event uses the same extent for count, charge, chemical energy and heat. Thermal EOS is U/[cv_e*(N_nuc+N_e)], with explicit cv_e=3 k_B/(2 epsilon_eV).

## 3. Newborn-donor error theorem

Embed the full selected model and surrogate in positive energy coordinates Z=(E_j N_j,U,C_H,C_He). At fixed gas, the conservative collision matrix A(u) is Metzler with zero column sums. Its time-dependent propagator has l1 norm1. For e=Z-Zhat,

$$e'=A(u(Z))e+[A(u(Z))-A(u(Zhat))]Zhat+R,$$

where R contains the omitted newborn-donor reactions. Hence only gas feedback needs an exponential majorant; raw stopping stiffness stays in the contractive propagation.

A single ionization event has energy-coordinate l1 increment2E_j. A stopping edge has increment2Delta_j when its product remains active, and2E_j when it joins the thermal bath. Write this value sigma_j. With active minimum energy Emin and c_n=1/Emin, the gas feedback coefficient per donor count is

$$\Gamma_j=\sum_a\frac{2E_j\kappa_{ja}}{VB_a}+\frac{\sigma_j b'_j(n_0)c_n}{\Delta_j V}.$$

The actual Coulomb b_j(n)=alpha_j*n*(L_j0-0.5*ln(n/n_ref)) is used, n_ref=1m^-3. Its derivative decreases on the verified positive-log domain. Newborn counts are bounded by their integrated original-parent birth rates. This yields constants L_h,C_I,C_P,C_S with

$$\|R(t)\|_1\le C_I t+C_P(1-e^{-\lambda_P^+t})+C_S(1-e^{-\lambda_S^+t}).$$

Variation of constants gives

$$\|e(h)\|_1\le\mathcal B(h)=C_IJ_2(L_h,h)+C_PK(L_h,\lambda_P^+,h)+C_SK(L_h,\lambda_S^+,h),$$

$$J_2(L,h)=(e^{Lh}-1-Lh)/L^2,$$
$$K(L,\lambda,h)=(e^{Lh}-1)/L-(e^{Lh}-e^{-\lambda h})/(L+\lambda).$$

The stable implementation uses K=lambda/(L+lambda)*[L*J2(L,h)+lambda*J2(-lambda,h)]. Limits at L=0 or lambda=0 are included. For fixed constants the bound is O(h^2). All later reactions of omitted donors are covered by the full propagator; no full downstream integration is required to evaluate the certificate.

With N_min=N_nuc+N_e0 and an all-time surrogate temperature upper bound,

$$|T-\widehat T|\le[1/(c_{v,e}N_{\min})+\widehat T_{\max}c_n/N_{\min}]\mathcal B(h).$$

An all-time cutoff enclosure strictly inside the original prefix closes the fixed-branch assumption by a first-exit bootstrap. The detailed constants and complete proof are in report sections3–5; outward Decimal code is checks/run_bound.py in the ZIP.

## 4. Actual checked interval

At proper h=100000s:

- x_H=1.1954667454293617e-8, x_He=6.7395383436470245e-10.
- z_P=0.0014870047023201717, s=0.1058955521796434152.
- Remaining original parent=0.9985129826690585396.
- Surrogate T=99.61541491399172148K; rigorous enclosure [99.61541491398850339,99.61541491399494277]K.
- Full selected donor-model energy-error upper bound2.468901438e-6eV/cell.
- Temperature-error upper bound0.001465122K.
- Full path cutoff lies inside [0.17165613042525469,0.17168637076567832]eV, strictly inside the original prefix.
- Feedback L_h=3.39868453e-9/s; separate slow-edge hazard about1.11932679e-6/s.

Five time bounds from1000 to200000s all close the same branch. At200000s the temperature-error bound is0.005653139K. Values displayed here are rounded outward; authoritative endpoints are in DONOR_ERROR_BOUNDS.json.

The exact exposure representation was evaluated independently with65-digit16/24-point quadrature, and lies inside the outward enclosure. A stage-updated SSPRK2 comparison at1,2,4,...64 substeps has final observed extent order2.00189277. This tests surrogate integration; the full-cascade difference is controlled separately by the theorem.

## 5. Evidence and continuation

New tests:9 unit cases,12 postchecks including an exact3-state conservative energy-chain witness,9 physical-time reference checks,10 warning-free Wolfram scalar zeros and4 xAct tensor zeros. Wolfram15.0.1; xTensor1.3.0; xPerm1.2.4; official source hashes pinned. A first scalar harness used protected symbol N and was rejected despite its apparent all-zero summary, then corrected and rerun. An initial repeated-log interval implementation timed out; density-separable aggregation completed the same bound in about10s. All diagnostics are retained.

The 10-page PDF was compiled twice and all pages visually inspected, with no final overflow, missing glyph or undefined command. Atomic-model uncertainty, angular closure and evolving geometry error are separate. No global production promotion, NCP job, old scientific-suite rerun or external independent review is asserted.

Next: NT_BUDGETED_DONOR_ACTIVATION ranks the three residual contributions and activates the dominant next generation; NT_GEOMETRY_TEMPORAL_BINDING combines actual changing rates and geometric work with the collision-time and angular budgets. Original REI/atomic/operator gates are preserved.

Primary comparisons: Le–Cambier (2017), arXiv1711.05946, conservative isotropic plasma kinetics; Söderlind (1984), doi10.1007/BF01934923, logarithmic-norm error propagation; Michel–Siegle (2024), arXiv2403.07618, linear Markov reduction errors. The specific nonlinear energy-coordinate donor theorem above is derived here; retrieved abstract/bibliographic scope and external full-text limitations are documented in REFERENCES.json.
