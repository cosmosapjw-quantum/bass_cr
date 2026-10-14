# Nonlinear continuum tail stability and REI reconstruction support

2026-10-14, Asia/Seoul. Selected R5 continuation `NT_KINETIC_CONTINUUM_TAIL_STABILITY` under `NT_CORE_TAIL_KINETIC_DEFECT_PROPAGATION`. Actual unchanged PR61 parent `8a2bb3d8220ecc871ae786d9fa67a9f94465202f`. Parent ZIP SHA256 `3f601795158e533fdb65ed327488741d0f1dcb853e2551e30bbaf45283510599` was present, checked and selectively read after the interruption. No old kinetic/moment/atomic history was replayed.

## Decision and exact scope

A COARSE finite-time continuum mean-energy-temperature bound is now nonnull for the SAME four-origin-label Gaussian initial, fixed-volume, common-log, isotropic electron-electron Landau problem. The quadratic error is retained, not dropped. Exact Gaussian moment evolution is the smooth reference; its already certified stored Hermite data supplies a reference tube only.

At100000proper seconds:

| Origin label | True continuum mean-energy temperature, K, outward displayed |
|---|---|
| C | [101.30796502966,101.40851150782] |
| P | [231702.01206757838,231702.01253204304] |
| S | [7692.04947147843,7692.05287131041] |
| A | [1347.79241001781,1347.80997094119] |

The cold-origin component therefore warms by more than0.2056K. It need not remain Maxwellian, and its mean-energy temperature is NOT a unique thermal-core/gas temperature. The C kinetic-versus-exact-moment radius is below0.050273234834K, not a microkelvin certificate. The prior approximately-7.69e-6K shape correction is NOT resolved in sign by this bound.

The separate fine saved-kinetic continuous residual/reflecting-boundary/global-state certificate remains open. Physical tau and new coupled HI/HeI/source temperature/optical intervals remain null. Existing20kBT/FR baselines, source families, F/G/atomic/b-grid/globalREI and CR/RCT/HH OFF remain unchanged.

## 1. Exact nonlinear positive-background split

Signature(-,+,+,+), proper seconds, W and theta=kBT/epsilon_eV in eV, F_a in cellcount/eV. Counts(1,1,.999,.001), totalN=3. cv=1380649/10681177560eV/K. K is the same inherited directed source interval, approximately2.0738886541545980558e-10eV^(3/2)/(s count). Nuclei are spectators. No dilution/source/photo/recombination/ion heat is added in this fixed-volume substep.

Natural endpoint premise: positive classical radial solution, bounded h=F/sqrt(W) at0, zero mass/energy flux at0 and infinity, and sufficient decay for the displayed integrations. This is not a new theorem for every weak or singular initial solution.

Set A_B(W)=integral_0^W B and

    D[B]=(2K/3)[W^-1/2 integral_0^W E B(E)dE
                          +W integral_W^infty B(E)/sqrt(E)dE],
    C(g,B)=partial_W{D[B](g'-g/(2W))+K g A_B/sqrt(W)}.

For e_a=F_a-M_a, e=sum e_a, F=sum F_a, M=sum M_a and R_a=C(M_a,M)-M_a,t:

    e_a'=C(e_a,F)+C(M_a,e)+R_a.                         (TS-02)

C(e_a,e) is retained inside the actual positive backgroundF. The time-dependent mass-preserving positive Fokker-Planck part C(.,F) is L1 nonexpansive under the natural endpoints. Kato therefore gives

    D+||e_a||1 <= ||C(M_a,e)||1+||R_a||1.

Write h_a=M_a/sqrt(W). Then exactly

    C(M_a,e)=(sqrt(W)D[e]'+D[e]/(2sqrt(W))+K A_e)h_a'
                     +D[e]sqrt(W)h_a''+K h_a e.

The piecewise kernel bounds |D[e]|<=(2K/3)sqrt(W)E0, |D[e]'|<=(2K/3)E0/sqrt(W), |A_e|<=E0 yield

    ||C(M_a,e)||1 <= ell_a E0,
    ell_a=K[2||h_a'||1+(2/3)||W h_a''||1+||h_a||infty].

For Gaussian h_a=A_a exp(-W/theta_a), A_a=2N_a/(sqrt(pi)theta_a^1.5), ell_a=(11/3)K A_a. These are newly derived kinetic coefficients, not the parent4moment Lipschitz constant.

## 2. Phase maximum and weak energy readout

The exact total phase equation is

    h_t=D h_WW+[D'+D/(2W)+K A_F/sqrt(W)]h_W+K h^2.

At maxima the diffusion/drift terms have the required sign, including the natural origin. Thus

    ||h(t)||infty <= H0/(1-KH0t),
    H0=sum 2N_a/(sqrt(pi)theta_a0^1.5).

The actual horizon denominator exceeds0.971179; H0<1389.697 and H(1e5)<1430.937count/eV^1.5. For anyr>0:

    I_-1/2(F)<=H*r+N/sqrt(r).

Use the explicitr=.01eV, not an unenclosed optimizer. At epsilon1e-8eV, count belowepsilon is<9.53958e-10 and energy<5.72375e-18eV uniformly through the horizon.

All-energy Gaussian integrals give valid whole-reference-tube bounds

    r0_a>=sup||R_a||1,
    r0_a=sum_(b!=a)2|Q_ab|/theta_a
                  +N_a|theta_a'|sqrt(3/2)/theta_a.

Q_ab is the original antisymmetric pair heat. Bounds are assembled with directed70digit arithmetic using the exact moment RHS and the inherited certified Hermite tube. Selected snapshot residual quadratures are separate diagnostics, not maxima used as proofs.

For L=sum ell_a, rho=sum r0_a and phi_m(z)=sum_(k>=0)z^k/(k+m)!:

    E0<=rho*t*phi1(Lt),
    integral E0<=rho*t^2*phi2(Lt),
    integral ||e_a||1<=r0_a*t^2/2+ell_a*rho*t^3*phi3(Lt).

L<1.056761e-6/s and E0(1e5)<.011415133count. Initial mismatch is0 between the EXACT continuum Gaussian reference and exact same initial kinetic solution, not between the finite grid and continuum.

General W-weighted L1 gives C-radius1.49941K. Use the exact per-label identity integral W R_a=0 instead. With

    a_B=K[integral_W^infty B(E)/sqrt(E)dE-A_B/sqrt(W)],
    d*=K Iupper, d_a=2K N_a/(sqrt(pi theta_a)),

reciprocal energy exchange gives exactly

    deltaU_a'=integral a_F e_a -integral a_Ma e,
    |deltaU_a(t)|<=d*[r0_a*t^2/2+ell_a*rho*t^3*phi3(Lt)]
                            +d_a*rho*t^2*phi2(Lt).            (TS-15)

This is a full-horizon unsigned bound retaining nonlinearity, not an unbounded initial t^2 extrapolation. It yields temperature radii C.050273234834, P.000232228074, S.001699911738,A.008780457442K. Add the small inherited moment NUMERICAL enclosure to obtain the table above. Total energy imposes correlations; not every point of this rectangle is simultaneously attainable.

The saved N2048 kinetic final readout was also reconstructed by exact Fractions from the existing eV energy/count arrays. Its difference to this continuum interval gives a coarse bound for that saved readout. No kinetic solver was rerun, and the numerical spatial/time decomposition remains unresolved.

## 3. Actual future high-energy tail

For convexphi, the total drift contribution has the signed pair form

    integral phi' a_F F
      =K integral_(u<v)[phi'(u)-phi'(v)]F(u)F(v)/sqrt(v)<=0.

Also D[F]<=2KNsqrt(W)/3. For E*>0, sqrt(W)<=(W+E*)/(2sqrt(E*)). The exponential moment M(lambda,t)=integral exp(lambda W)F satisfies

    M_t<=a lambda^2(M_lambda+E* M), a=KN/(3sqrt(E*)),
    lambda(t)=lambda0/(1+a lambda0t),
    M(lambda(t),t)<=M(lambda0,0)exp[E*(lambda0-lambda(t))].

Gaussian initial data gives M(lambda0,0)=sum N_a(1-lambda0theta_a0)^-1.5. Here E*=theta_P0,lambda0=.95/theta_P0. For lambda_h R>=1, uniformly0..h:

    N(>R)<=Mupper exp(-lambda_h R),
    U(>R)<=R Mupper exp(-lambda_h R).

At R40theta_P0=798.661651...eV: count<2.872098e-15,energy<2.293834e-12eV. At R60theta_P0: count<1.609185e-23,energy<1.927791e-20eV. No R60 solver success is implied. These are evolving-continuum bounds, not a frozen Maxwell tail.

For W<R the omitted E>R background contribution is exactly deltaD=(2K/3)W Jtail, deltaa=K Jtail, Jtail<=Ntail/sqrt(R). AtR40, deltaa<2.107673e-26eV/s. This controls tail background coefficients, NOT the reflecting numerical boundary's trace/flux residual. Keep that fine obligation open.

## 4. Actual REI worktree support, without owner mutation

The live authorized Desktop was read, not inferred from old PR summaries. It advanced during inspection from b07274e... to1cff09ef35196443d3a25d484c928b1512ae22c2. At the final11:52:41UTC state read and following exact PID check, tracked files were clean, AX07 ZERO was completed at its conditional scope, AX08 IN_PROGRESS and AX11/12 PENDING. Existing observer and SHEAR_HALF_PLUS were live. Old SHEAR_MINUS PIDs were absent but no terminal outcome was classified. Snapshot is not continued monitoring or an execution permission.

Owner4096MiB output allocation/T1config/binary, AX12variants and signed epoch-recovery were already prepared. Do not duplicate or attribute them to this supplier. Preserve all-five-baseline, owner lifecycle/review/staging and shared-slot gates. No external STATE/source edit, kill or solver launch occurred.

The actual reviewed comparison reducer labels its1001ln(a)-sample norms as sampled/interpolated and leaves true error UNKNOWN. The new adjacent tested `reconstruction_support.py` adds:

1. Exact Fraction sup of two piecewise-linear reconstructions on the UNION of knots, with O(n+m) merge. No extrapolation, silent coordinate change or Tgas sorting. A narrow between-sample spike control is caught. This norm alone is NOT an IVP error.
2. Conditional interpolation envelope from same-source node errors and curvature, retaining slope jumps. Radius=(1-u)eps_l+u eps_r+M(x-a)(b-x)/2; integral=h(eps_l+eps_r)/2+M h^3/12. Interior slope-jump bounds add their exact Green-kernel terms. Missing witnesses produce UNKNOWN, never0.
3. For ln(a), O_LL=O_tt/H^2-O_t H_t/H^3. Require actual source H lower and derivative upper bounds; do not import CR constants.

The complete312238-row ZERO history bytes were hashed once and21selected actual rows were used for a small21->11coarsening interface probe. This is not a new convergence campaign or the error of the original full history. Private selected rows/runtime snapshots remain only in the archive.

Consume HH68's actual `source_pair_guard.py` at b8c6fef512cdc3b3b109749b9d4e76335a03aa1f before this helper; it requires identical source bytes or a pair-bound reviewed semantic relation. Keep HE51 normalization/current/clock support and owner completed-history intake separate. Their actual source snippets/owner updates were read. No duplicate source guard or foreign numerical bound is inserted.

`CR_REI_RECONSTRUCTION_SUPPORT`: READY_FOR_OWNER_REVIEW_AND_SCOPED_INTEGRATION. **Owner AX11/AX12 are not marked READY or completed by this contribution.** Missing actual refinement histories, runtime lifecycle and curvature witnesses remain explicit.

## Evidence, complete archive and continuation

Actual Wolfram15.0.1:16scalar zeros in12groups. Actual xTensor1.3.0:5tensor zeros; official xCore/xPerm/xTensor hashes matched. New47formula/arithmetic/source conditions and13helper tests passed. Eight Gaussian residual snapshot integrals are diagnostics. Same author plus separate CAS/arithmetic; external independent scientific review and native subagents NOT_RUN. New/old scientific IVP runs0; native/HPC/atomic campaigns0.

Preserve the new missing-curvature-as-zero RED/GREEN, corrected eV/dimensionless saved-reader mistake and directed Decimal unary-sign repair. They did not change the source or loosen criteria. A detached receipt-composition variable-shadowing error after ZIP creation was repaired by a targeted read-only check; immutable archive and science were unchanged.

[Complete private research archive](https://drive.google.com/file/d/1ww-asM6iT2aOAP0p-rtrGC15BJtZTo99/view?usp=drivesdk): `BASS_CR_TAIL_STABILITY_20261014_SOURCE.zip`,1413389bytes,59members/58manifest payloads,SHA256 `2b88400dc5226628040acaf01255c9c5cc97d4fbb1fa5e31b383eaac2660db70`.

Dropbox completed matching1413389bytes at the existing BASS_DERIVATION_DOSSIERS_20260912 destination, ID`id:BSpOijBcT10AAAAAAD6XzA`. Drive ID1ww-asM6iT2aOAP0p-rtrGC15BJtZTo99 and existing parent1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI matched. R1 ACK/ID/name/size/parent, not remote full restore. Local and relocated58payload verification passed; altered temporary code was rejected, restored copy passed. No original or sharing changes.

Full proof, outward constants, source inputs, saved kinetic readout, helper/tests, actual CAS, selected private live intake, failures and DAG are in the ZIP. Read REPORT_KO.md,CONTRACT.json,HANDOFF.json and integration/FINAL_OWNER_UPDATE.json. `python verify_package.py` is read-only and reexecutes no scientific producer.

Next SAME-node fine continuation: source-bound continuous weak kinetic residual/adjoint, reflecting-boundary trace and nonlinear remainder sufficient to resolve the microkelvin shape correction. Preserve this now-nonnull COARSE continuum result and endpoint tails; do not return them to null or repeat the old kinetic campaign. Parallel supplier intake is ready, owner science gates unchanged. No main/owner merge or production activation.

Literature comparison only: Ilin arXiv2510.15089v1(relative entropy); Filbet/Gui/He arXiv2509.09276(spectral approximation); Carrapatoso/Desvillettes/He arXiv1510.08704(moment propagation); Guillen/Silvestre arXiv2311.09420(regularity). SciSpace/Exa/primary web were used within stated abstract/introduction scopes; their unevaluated constants are not the constants above. No novelty assertion or unread PDF proof is substituted for the direct derivation.
