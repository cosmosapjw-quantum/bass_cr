# Reversible Coulomb core-tail pilot, 2026-10-14

Selected node `NT_REVERSIBLE_COULOMB_CORE_TAIL_PILOT`, R5 derivation and local checks. Parent PR59 head `029b2122db4f76f5a639e8ae4d58cf552e71b91d` and its actual archive/report/CONTRACT/DECISION/NEXT_DAG were read. Parent branch was rechecked unchanged before this additive publication. No old scientific suite was replayed.

## Main result and exact boundary

Construct a new fixed-volume, Coulomb-only four-component electron comparison. Retain reciprocal core-tail and all tail-tail ordered pairs, with actual finite bath heat capacity. The positive numerical representation is a sum of four labelled zero-mean Maxwellians of the SAME species, while ownership is explicitly `f=M(total moments)+g`, with signed zero-count/momentum/energy correction. M is not an extra population.

The P/S/A monoenergetic energy shells are replaced by Maxwell energy distributions matching their counts and mean energies. This is NOT a continuation of the old atomic/moving source. Nuclei are spectators; electron-ion/neutral thermal exchange, HI/HeI events and cosmological transport are not part of this local collision substep.

At100000 proper seconds the exact four-temperature MOMENT ODE gives cold-origin component temperature in **[101.35823826449,101.35823827299] K**, with numerical error radius<4.244696981117e-9K. This is not the true nonlinear kinetic Landau temperature or the original full-source gas temperature. An exact nonzero fourth-velocity-moment defect explicitly exposes the remaining shape-closure error. Physical tau and new full-source T/opacity intervals remain null.

At the initial diagnostic cut20theta_C,82.63percent of low-energy heat gain is bulk Coulomb exchange, not boundary-crossing heat. Omitting C(g,g) misses96.27percent of the net count flux; at10theta_C and30theta_C the linearized flux even has the wrong sign for this pivot/mixture. A separate LRS anisotropic Gaussian probe includes self scattering and has nonzero relaxing stress at zero total collision-energy trace.

## Source, conventions and exact distribution

Signature(-,+,+,+), proper seconds, W and theta=kB*T/epsilon_eV in eV, counts per fixed proper cell; epsilon_eV=1.602176634e-19J/eV and cv=3kB/(2epsilon_eV). Common frozen Coulomb logarithm, nonrelativistic/nondegenerate/weak-coupling electron-electron Landau operator. One reciprocal pair uses the same log. Original SOURCE_RATES.npz SHA2563c63d0cd77c6fa03b19a2349f6a039cb9056d3594afd7dfcf50d192a5c066ae2.

Counts(C,P,S,A)=(1,1,999/1000,1/1000), theta_C=2cv*T0/3, theta_(P,S,A)=2E_(P,S,23)/3. Original V=1257522545067581081/1250000000000000000m3 and source mean energies are unchanged, higher distribution moments are not. Initial theta approximately(.008712327653334757,19.966541276874562,.6628650249518994,.11616666666666668)eV.

From exact source dyadics:

    K=alpha23/V * [L0_23-.5log((1/V)/(1m^-3))]*sqrt(E23)
      approximately2.07388865415459805580054704314444e-10
      eV^(3/2)/(s count).

The exact source constants are defined by CASE fractions and saved rate dyadics. PILOT_ANCHOR.json is a point diagnostic, not the exact-input authority. The directed numerical certificate includes the small difference from the floating reference initialization.

For f=sum f_a, use M with Ntotal3 and theta_bar=sum N_a theta_a/3 approximately6.87919064370717eV. The cold C label is not M and is not identical to the W<q population. C(f,f)=C(M,g)+C(g,M)+C(g,g); all terms retained. Origin labels are not physical species or disjoint energy regions.

## 1. Exact snapshot radial flux and reciprocal energy

Let p_theta(W)=2sqrt(W)exp(-W/theta)/(sqrt(pi)theta^(3/2)) and P3(x)=erf(sqrt(x))-2sqrt(x)exp(-x)/sqrt(pi). Apply the inherited Maxwell-bath divergence-form coefficient D_b=theta_b*K*N_b*P3(W/theta_b)/sqrt(W) to N_a*p_theta_a. Positive flux points to increasing W:

    j_ab(W)=2K N_a N_b/(sqrt(pi)theta_a^(3/2))
       *(theta_b/theta_a-1)*exp(-W/theta_a)*P3(W/theta_b),
    Q_ab=integral j_ab dW
       =2K N_a N_b(theta_b-theta_a)
         /[sqrt(pi)(theta_a+theta_b)^(3/2)],
    Q_ab=-Q_ba.

This includes drift AND energy diffusion. Equal-temperature pairs have zero flux at every energy. Endpoint fluxes vanish. Ordered reciprocal moments, not an unrelated added heat prescription, supply the bath exchange.

Initial Q_CP=5.231368806198e-11, Q_CS=2.778696131759e-10, Q_CA=5.698103888934e-13, Q_PS=-4.816326434055e-11, Q_PA=-5.161498355241e-14, Q_SA=-1.858750356076e-13eV/s.

## 2. Finite-bath moment IVP and exact shape defect

The explicit Maxwell-projected comparison is

    (3/2)N_a theta_a'=sum_b Q_ab.

Positive pair conductances make the minimum temperature nondecreasing and maximum nonincreasing; the positive initial box gives a unique regular finite-dimensional solution. Total sum(3N_a theta_a/2) is conserved. The LABELLED Maxwell entropy, not entropy of the total mixture, obeys

    S_tag'/kB=sum_(a<b) Q_ab*(1/theta_a-1/theta_b)>=0.

Actual DOP853/Radau new runs used113/58 RHS calls. Final temperatures approximately(101.3582382687379,231702.0122998107,7692.0511713944,1347.8011904795)K. Maximum inter-method difference4.1228e-11K; stored energy drift7.11e-15eV. S_tag/kB increase.0037559976290. These point checks are not the error certificate.

Exact Landau evolution of the second ENERGY moment differs from the Gaussian tangent:

    R2_a = d_Landau<int W² N_a>-d_Maxwell<int W² N_a>
         =-3theta_a² sum_b Q_ab/(theta_a+theta_b).

Initial values C/P/S/A approximately(-9.5853573e-14,5.9275390e-9,5.4263868e-10,1.7496138e-13)eV²/s. They are nonzero. Finite-domain numerical L1 residual diagnostics also exist, but neither these diagnostics nor the moment numerical bound are relabelled as a full kinetic forward certificate.

The no-tail-tail control changes final P/S/A temperatures by about+.0373007/-.0371544/-.1837461K. Frozen-C thermostat without an external-reservoir ledger changes electron energy by-3.30755e-5eV. Including that external reservoir would make a different thermostat model consistent, not turn it into an isolated finite bath.

## 3. Whole-cell numerical certificate for the SAME moment ODE

Freeze101 endpoint values and RHS slopes as exact dyadic reference data. Construct the C1 cubic Hermite polynomial P_i in normalized cell coordinate. Its four Bernstein controls prove positivity and theta>=theta_safe=.999theta_C0 over every cell. The true moment IVP has theta>=theta_C0 by the minimum principle.

On the common segment domain, direct derivatives give

    L_infinity<=5*[4K/(3sqrt(pi))]*Ntotal/(2theta_safe)^(3/2)
              <1.0189338006390e-6/s.

Expand normalized residual r=P_x-hF(P) to second order about each midpoint. Since P is cubic, r's third coefficient is-hF3. Outward Taylor jets evaluated on the whole derivative/state tube give

    rho_i>=max_a(|r0|+|r1|/2+|r2|/4+sup|hF3|/8).

Propagate e_out<=exp(Lh)e_in+phi1(Lh)rho_i. This includes exact initial/source inputs, Machin-series pi, sqrt/log/exp roundoff, slope/node quantization and the whole-cell residual. It is not a sampled residual maximum or a refinement-difference bound.100 cell records are retained. Final numerical temperature radius<4.244696981117e-9K and cold-component interval[101.35823826449,101.35823827299]K. Gaussian-shape/physical-source errors are excluded and explicitly unresolved.

## 4. Same-distribution partition and nonlinear correction

For a diagnostic energy cut q:

    N_< =sum N_a P(3/2,q/theta_a),
    U_< =sum (3/2)N_a theta_a P(5/2,q/theta_a),
    Jrel=sum_ab j_ab(q)-qdot*N(q),
    Ic=sum_ab integral_q^infinity j_ab(W)dW,
    N_<'=-Jrel, N_>'=Jrel,
    U_<'=-q*Jrel-Ic, U_>'=q*Jrel+Ic.

The exact tail primitive is

    integral_q^infinity exp(-W/ta)P3(W/tb)dW
    =ta[exp(-q/ta)P3(q/tb)+(ta/(ta+tb))^(3/2)
         Q(3/2,q*(1/ta+1/tb))].

At q=20theta_C0=.17424655306669512eV, N_<=1.08792998180788, not the cold label count1. J=-3.262780361587e-10count/s, Ic=-2.703922365783e-10eV/s, U_<'=3.272450597203e-10eV/s. Bulk exchange accounts for82.63percent. The actual source node23=.17425eV differs slightly from this diagnostic20theta_C cut.

At this point j_Mg=-4.083948511286e-11, j_gM=2.866344498507e-11, j_gg=-3.141019960309e-10count/s. Their sum is the complete j. At10theta_C and30theta_C the sum of only the two linear terms is positive although the full flux is negative. This is a source/pivot-specific diagnosis of a non-small correction, not a universal no-go against perturbative cores.

## 5. Nonzero angular/self response

Use z=sqrt(m_e/(2epsilon_eV))*v, W=z². A separate P Gaussian covariance is(theta_P/2)diag(.85,.85,1.30); other components remain isotropic. For diagonal common-axis Sa,Sb, relative covariance S=Sa+Sb and score=-Sa^-1 z+Sb^-1 z':

    E[z|w]=Sa S^-1 w, E[score|w]=-2S^-1 w,
    Cov(z,score|w)=(Sa-Sb)S^-1.

Let si=Sai+Sbi, A(n)=sum ni²/si, ci=(Sai-Sbi)/si and gamma=K/4. Gaussian radial integration is exact:

    Mdot_ab,ii=gamma Na Nb/[(2pi)^(3/2)sqrt(detS)]
      *integral_S²[8(Sai/si)ni²(1/si-A)/A²-2ci(1-ni²)/A]dOmega.

Actual64/96-node LRS angular evaluations include all16 ordered pairs and self terms. Total diagonal approximately(6.933222800676e-12,6.933222800676e-12,-1.386644560135e-11)eV/s; P-P self diagonal(1.063025265663e-12,1.063025265663e-12,-2.126050531325e-12)eV/s. Total trace residual2.585e-26, rule difference1.681e-25eV/s. Separate85-digit selected pair integrals agree. No total angular-roundoff enclosure or full angular IVP is claimed.

The spatial Landau projector h-ee annihilates the relative vector; hence paired energy trace vanishes while anisotropic stress can change. Physical stress=2epsilon_eV M. Bianchi work remains-K_ab Pi^ab, separately derived/checked rather than integrated in this fixed-volume pilot. Total current is preserved under a mere same-distribution partition; retain source age A=q_a k^a distinct from Doppler D=-u.k and apply passive sigma only once. No new source-current receiver was run.

## Evidence, reuse and next

Actual Wolfram15.0.1:27 scalar components in17groups all literal0. Actual xTensor1.3.0:9 tensor zeros; pinned official xCore/xPerm/xTensor hashes matched. Submitted scripts were saved before calls; observed outputs are normalized transcriptions, not raw connector bytes. Same author and separate formula/CAS paths; external independent review and native subagents NOT_RUN.

Independent validation58conditions and12unit tests passed. Tests include6 direct85-digit pair heat/moment/tail integrals,4 inherited-operator flux matches, tensor normalization/independent integration, exact constants and source identity, numerical certificate consistency, and interval/jet/precision edge cases. Tests-after, not a fabricated TDD campaign. First missing-poly_jet import failure and pre-success Decimal sign/abs precision repair are preserved; no physics/tolerance relaxation.

Read actual HE49 head40659a752b9348fb7919cf5afcf42f310e05d064 full R4_RESULT: immutable Hermite/Bernstein/whole-cell distinction reused with entirely NEW moment coefficients. HH65 detailed PR15a9ee97d7c1b27f65e289e61c614ce3a1ab894c and REI117 detailed PR477f3756044df89ff63cceb6b432e63015c07f0a read without importing foreign rates, observer numbers or claiming inherited formatting CI green.

Primary comparison: Pfefferle-Hirvijoki-Lingam arXiv1701.08037v3 DOI10.1063/1.4979992, and Ricketson et al arXiv1301.5678 DOI10.1016/j.jcp.2014.04.059. SciSpace discovery, Exa primary Gaussian/Hermite and hybrid split passages, web primary metadata used. Direct derivations above do not claim general-method novelty. No source-paper PDF or font redistributed.

Next READY:NT_CORE_TAIL_KINETIC_DEFECT_PROPAGATION. Propagate the actual shape residual in the SAME pilot, preserving signed ownership, positivity, reciprocal and nonlinear terms; no repeated old moment-precision campaign. Existing20kBT/FR source families,F/G/atomic/b-grid/globalREI and CR/RCT/HH OFF unchanged. No full kinetic/source IVP, native receiver, HPC, main merge or external-repo mutation.

## Immutable complete package and delivery

[Full Korean proof, tested code, exact inputs, outputs, failures and DAG](https://drive.google.com/file/d/1xauVe3tuf6ox_Z_kIhkXZfJEAAZdZ38I/view?usp=drivesdk).

- Archive:BASS_CR_CORE_TAIL_PILOT_20261014_SOURCE.zip.
-1529716bytes,52members,51manifest-bound payloads.
- SHA256:14dde3e79cbc3e7280801e1f9f652a857a830a7e00cfe42416bc38e52a2f2b39.
- Drive ID1xauVe3tuf6ox_Z_kIhkXZfJEAAZdZ38I; existing parent1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI. Upload and metadata ID/name/size/parent matched.
- Dropbox completed same1529716bytes, IDid:BSpOijBcT10AAAAAAD5Umw, path/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_CORE_TAIL_PILOT_20261014_SOURCE.zip.
- Local CRC,51payloads and5nested archive/font checks passed. The final ZIP was relocated and the read-only verifier passed. These storage checks do not rerun science.
- Remote verification R1 ACK/ID/name/size/parent, not full-byte restoration. No originals or access changed.

The full runnable core_tail.py, evaluator, directed certifier, tests and100cell evidence are inside the immutable ZIP; this Git file is the substantive compact result/restore entrypoint, not a claim that every payload is expanded in Git. Read REPORT_KO.md and CONTRACT.json; run python checks/verify_package.py for read-only validation.