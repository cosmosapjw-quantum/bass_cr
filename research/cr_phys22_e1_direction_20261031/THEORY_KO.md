# PHYS22 constructive E1 direction and fixed observer Stokes crosswalk

Let k be the incident electron unit direction, s the scattered electron direction, and t=(s−(k·s)k)/sqrt(1−(k·s)²) its transverse unit direction, with collision basis (k,t). The 6CCO printed spin-1 reduced two-state density B has B_kk=lambda, B_tt=1−lambda, B_kt=−sqrt(2)(R+i Icorr). Spin/fine/hyperfine and actual precession are not modeled. PSD iff 2(R²+Icorr²)<=lambda(1−lambda).

Embed in 3×3 Cartesian orbital matrix rho(k,t) = lambda kkᵀ+(1−lambda)ttᵀ−sqrt(2)(R+iIcorr)ktᵀ−sqrt(2)(R−iIcorr)tkᵀ. Averaging **unobserved scattered electron azimuth** about fixed k gives <t>=0 and <ttᵀ>=(I−kkᵀ)/2 and rho(k)=(1−lambda)I/2+(3lambda−1)kkᵀ/2. Therefore the local imaginary amplitude does **not** imply surviving circular Stokes after this marginalization.

For an initial atomic hydrogen 1s target in E1 photoionization, the incident photon electric polarization epsilon gives electron ejection f_e(k)=3|epsilon·k|²/(4pi). A single unpolarized photon ray with propagation a gives [1−P2(k·a)]/(4pi), i.e. beta_e=−1. Isotropic unpolarized photon bath beta=0. A normalized axisymmetric unpolarized photon ray intensity f_gamma(n)=[1+alpha P2(n·a)]/(4pi), alpha∈[−1,2], produces f_e(k)=[1−(alpha/5) P2(k·a)]/(4pi) via harmonic convolution; beta_e=−alpha/5. Linearly polarized photon ray along z, epsilon=x gives beta_e=2 about x. Assumes the H1s E1 single-photon transition. The original photon source scalar events do NOT store ray or epsilon, so all five are conditional.

For f_e=(1+beta_e P2(k·a))/(4pi), <kkᵀ>=I/3+(beta_e/15)(3aaᵀ−I). The DCS-integrated collision-plane alignment of each original source event is lambda(E)=[1+P1_PHYS21(E)]/2 (upper original 6CCO 35 or 40eV anchor). With chi=beta_e(3lambda−1)/10,

rho_global(E)=I/3+[chi/3](3aaᵀ−I).

For observer n=(sin theta cos phi,sin theta sin phi,cos theta), e_theta=(cos theta cos phi,cos theta sin phi,−sin theta), e_phi=(−sin phi,cos phi,0), E1 emission J_ab=3/(8pi) e_a rho e_b. Stokes Q=J_theta,theta−J_phi,phi, U=2ReJ_theta,phi, V=−2ImJ_theta,phi, and per original event weight w [m−3]:

I=w/(4pi)[1−chi P2(a·n)], Q=3w chi/(8pi)[(a·e_theta)²−(a·e_phi)²], U=3w chi/(4pi)(a·e_theta)(a·e_phi), V=0.

The photon integral ∫I dΩ=w holds; all rho eigenvalues nonnegative for beta∈[−1,2], lambda∈[0,1]. The source weights are unchanged: source earliest=3.3158906934521573e−31 m−3, latest=9.85567761064524e−32 m−3. Axial sky Q sign is explicitly defined by e_theta vs e_phi. These formulas yield a **source-energy weighted conditional fixed-observer local E1 emissivity** (not observed flux, escape, or full RII radiation).

Independent Wolfram symbolic trace, eigenvalues and sky angular integral CHECKED; Python direct quadrature/3x3 tensor tests normal+optimized 12/12 each; GitHub all 20660 and 540 scientific rows readback. No real independent author or native subagent. Next physical step: obtain actual RR photon-ray and polarization distribution from a truly source-compatible source/tetrad or propagate a declared anisotropic Bianchi radiation field through the E1 kernel while retaining conditional provenance. Main DAG 28/88, extension0/3, production HOLD.
