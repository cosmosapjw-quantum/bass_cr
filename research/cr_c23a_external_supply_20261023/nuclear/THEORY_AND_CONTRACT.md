# C23A: beta primary-electron coverage of an FS2010 energy domain

## Frozen scope and source admission

This is a new source-coverage calculation. It does not call or replace the existing
REI beta abundance/energy ledger, HH81 cold-COM capture, or historical ODE runs.
The source contract is `source/EVALUATED_ENERGY_AND_DOMAIN_CONTRACT.json`.
The verified existing `EVALUATED_DECAY_INPUTS.json` supplies lifetimes only. Its
energy fields are absent. The two separately downloaded IAEA ENDF/B-VIII.0 decay
files supply central energy values; their older lifetimes are not adopted.

The ENDF records have one beta-minus branch with unit intensity, TYPE=1 (allowed),
LCON=0 (no tabulated continuous spectrum), and ER=Q. Their 2005 evaluation/2011
conversion/2018 distribution dates are preserved. For neutron beta, the selected
record gives Q=ER=782347 eV and ERAV=301370 eV. Tritium gives Q=ER=18590 eV and
ERAV=5690 eV with recorded mean uncertainty40 eV. The neutron recorded uncertainty
of zero does not establish zero physical uncertainty. Calculations below are
conditional on these selected central values, not an uncertainty propagation or
a claim that they are the newest/best physical evaluations.

ENDF section8.4 defines Q as total decay energy and ERAV as average radiation
energy. We use Q as a conservative support ceiling and as the declared endpoint
parameter of an illustrative model. ER=Q in a legacy file is not a precision
recoil-corrected free-neutron or atomic/molecular-tritium electron endpoint.
The legacy zero recoil fields do not establish physical recoil-free decay.

FS2010's actual author table `log_xi_-1.0.dat` contains258 energy rows from
L=10 eV to U=9937.21 eV. The parent source audit binds these values to electron
kinetic energy despite the upstream Photon Energy column label. This task only
computes energy-domain support. It neither executes the upstream code nor admits
the table's bath composition, ionization-axis metadata, or energy-closure defects.

## Moment information does not determine the coverage

Let nu be a positive primary-electron probability measure on [0,Q], with
integral1 and mean m in (0,Q). Set D=[L,U], where0<L<U<Q. Define P_D=integral_D dnu
and E_D=integral_D T dnu. Direct pointwise inequalities give

\[
0\le P_D\le\min\{1,m/L,(Q-m)/(Q-U)\},\qquad
0\le E_D/m\le\min\{1,U(Q-m)/[m(Q-U)]\}.
\]

For number coverage, bound the indicator by1, T/L, and (Q-T)/(Q-U) separately.
For energy coverage, bound T times the indicator by T and by
U(Q-T)/(Q-U). All inequalities hold everywhere on [0,Q], including the tails.
This proves the bounds without any spectrum interpolation or deposition model.

These bounds are sharp in the class of all positive probability measures with
the stated support ceiling and mean. The zero lower bounds are attained by
(1-m/Q)delta_0+(m/Q)delta_Q. The upper number bound is attained by an appropriate
mixture at0,L when m<L, a mass at m when L<=m<=U, or a mixture at U,Q when m>U.
For the upper energy bound, use a mixture at0,L for m<L, a mass at m for
L<=m<=U, and a mixture at U,Q for m>U. If full continuous support is imposed,
these discrete extrema become limiting constructions rather than claims about
actual beta spectra. The universal inequalities remain valid.

A second measure `(1-p)delta_t+p delta_Q`, with t inside D and t<m and
p=(m-t)/(Q-t), has the same normalization, mean, and endpoint Q as the zero-domain
measure but has positive domain coverage. The run checks both moments exactly
using rational arithmetic. Thus the missing spectrum cannot be recovered from
the endpoint and mean alone.

This ambiguity also exists for smooth densities. Choose three normalized smooth
compact bumps phi_a,phi_b,phi_c with means a<L, b in D, and c>U, supported wholly
in those three regions. Then

\[
h=(c-b)\phi_a-(c-a)\phi_b+(b-a)\phi_c
\]

has zero zeroth and first moments, but its integral over D is -(c-a). A positive
full-support base density g with mean m can be perturbed to g+epsilon h and
g-epsilon h for sufficiently small nonzero epsilon. Positivity, normalization,
mean, and support endpoint persist while coverage changes. This is a conditional
moment underdetermination argument, not a statement that known nuclear physics
cannot further constrain a spectrum.

## Separate illustrative allowed phase-space diagnostic

In energy units, define M=m_e c^2=510998.95069 eV from NIST2022 CODATA and

\[
w(T)=\sqrt{T(T+2M)}(T+M)(Q-T)^2,\quad 0\le T\le Q.
\]

The square root is p_e c. This is an explicitly constant-matrix-element allowed
phase-space shape with Fermi functionF=1, massless antineutrino, and neglected
daughter recoil. It omits Coulomb enhancement, weak magnetism/recoil, radiative
effects and radiative emission, screening/exchange, atomic or molecular final
states, and forbidden shape corrections. TYPE=1 in the evaluation does not
justify omitting these corrections in a production spectrum. The diagnostic
is not fitted to the evaluated mean and is never named an evaluated beta spectrum.

Define I_k(a,b)=integral_a^b T^k w(T)dT. Number fractions are I_0/I_0(total),
kinetic energy per primary is I_1/I_0(total), and kinetic-energy fractions are
I_1/I_1(total). The partition consists of [0,L), [L,U], (U,Q]. Each unresolved
tail retains both particle number and kinetic energy. Heat and ionization outputs
are null because no deposition was performed. The toy complement Q-mean(T)
belongs to the massless antineutrino only in this toy's recoil-free partition.
No physical neutrino, recoil, radiative, or daughter energy is fed to FS.

## Independent calculation and dimensional checks

The primary double-precision quadrature uses x=T/Q=u^2, r=M/Q:

\[
I_k/Q^{k+5}=\int 2u^{2k+2}\sqrt{u^2+2r}(u^2+r)(1-u^2)^2du.
\]

This removes the square-root endpoint and prevents large energy powers in the
quadrature. Independently, mpmath80-digit quadrature directly integrates in x.
A third method uses a closed antiderivative. For y=T+M, R=sqrt(y^2-M^2),
J_n=integral y^n R dy,

\[
J_0=(yR-M^2\operatorname{acosh}(y/M))/2,\quad J_1=R^3/3,
\qquad J_n=[y^{n-1}R^3+(n-1)M^2J_{n-2}]/(n+2).
\]

Expand `(y-M)^k*y*(Q+M-y)^2` and sum the corresponding primitives. The run
compares k=0,1,2 on all segments and the total with both independent methods.
It also checks eV/keV scaling, number/energy closure of the partition, exact
moment witnesses, and electron-only API rejection. These numerical comparisons
are not a global physical error bound; `global_error_bound=null`.

## Execution, publication, backup, and DAG

The new numerical run uses one worker with process affinityCPU5 and native
numerical threads1, under the parent's cooperative CPU assignment. The outer
process budget is60seconds with an internal55second alarm. Its create-only run
directory records the lease, source/code hashes, outputs, and release. No old
science run is re-executed. Publication and durable backup remain parent-owned.

| Axis | Frozen state before execution |
|---|---|
| EXECUTION | source bytes read and pinned; new bounded quadrature pending; historical ODE0 |
| PUBLICATION | PARENT_PENDING |
| BACKUP | PARENT_PENDING; no new remote-backup success claimed |
| DAG | energy source contract -> moment proof -> illustrative diagnostic -> independent checks -> parent publication/backup |

Full high-energy nuclear transport remains HOLD. Evaluated spectral data or a
separately validated corrected beta spectrum, bath-compatible electron transport,
tail treatment, neutrino/recoil ownership, and the parent's FS table defects must
be resolved before any physical beta-to-IGM heating contract is admitted.

## Primary sources and exact evidence

- IAEA ENDF/B-VIII.0 decay distribution: https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/decay/
- Neutron bytes: https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/decay/decay_0001_0-Nn-1.zip
- Tritium bytes: https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/decay/decay_0004_1-H-3.zip
- CSEWG ENDF-102 section8.4: https://www-nds.iaea.org/exfor/x4guide/manuals/endf-manual.pdf
- NIST2022 CODATA: https://physics.nist.gov/cuu/pdf/wall_2022.pdf
- Ivanov et al., Phys.Rev.D99,053004(2019), corrected neutron-decay theory context: https://doi.org/10.1103/PhysRevD.99.053004 (2021 erratum exists; no implementation copied).
- Furlanetto and Stoever2010: https://arxiv.org/abs/0910.4410 ; actual author table archive https://cosmicdawn.astro.ucla.edu/elec_interp.tar .

Full local source bytes, SHA256, ZIP CRC receipt, selected format retrievals,
the legacy input Gitblob binding, and failed LNHB retrieval are preserved in
`source/`. Failure to retrieve the LNHB PDF is not treated as reading it.
