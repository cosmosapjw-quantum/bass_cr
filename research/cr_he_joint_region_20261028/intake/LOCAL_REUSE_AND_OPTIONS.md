# Local read-only reuse survey and next-unit options

## 1. Scope and actual access

Survey owner: `/root/cross_flow_code`.

Current local `bass_cr` HEAD was read as
`b457bb58d74cc9b64f7c760ffc690eda7a51ef9a`. Its tracked worktree was clean.
This survey read local source, saved results, instructions and release receipts;
it hashed source and attachment bytes, inspected ZIP central directories and
five small previously extracted archive members, and extracted the first three
pages of the attached HTT report as text. It did **not** import scientific code,
load NPZ arrays, run a scientific solver/test, allocate a science budget, change
project code, publish remotely, or claim a fresh remote-owner census.

`FILE_MANIFEST.json` identifies the inspected local files and all 20 visible
project attachments. Mathematical constructions below are handwritten analysis
for selection of the next unit; they are not an executed numerical result or
the next unit's final independently reviewed theorem.

## 2. Exact local predecessor state

### PR115: cross-energy envelope

Read `research/cr_he_energy_cross_20261028/{ADMISSION.json,DAG.json,
SCIENTIFIC_SUMMARY.json,HANDOFF_KO.md,theory/THEOREM.md,review/C09_FINAL.json,
publication/FINAL_DELIVERY.json}`.

- Unit `CR_PHYS02_HE_ENERGY_CROSS_V1`, decision
  `PASS_SCOPED_EXACT_CROSS_ENVELOPE`, scoped child `1/1`.
- Scientific S `9ec654379074b731ce20f0b7dbae05077ddf4d4b`; document D
  `9c0cc44c87ed3f416e2ca37f8fa3ed82bb562698`; local final receipt head is the
  `b457bb58...` value above. These roles must not be collapsed into one SHA.
- Exact finite divisible marginal; every cross-bin pair with
  `E_i+E_j<=K` is allowed; singles remain available.
  `Cmax=(N-Delta)/2` is optimized and certified.
- Nine native dual cases are saved; explicit full-size primal cases are only
  `K=0,3,20`. The saved evidence does not claim nine full-size primal runs.
- Accepted checks include 116 small independent cases, 20 original controls,
  8 targeted repair controls, 12,804 source fields, 9,603 primal marginal
  comparisons, and three independently checked consumer returns.
- Closed charge `28.653943/40 CPU-s`; unused `11.346057` is nontransferable,
  additional science allowance `0`, automatic next node `false`.
- Preserve `native_v1` exit `-9`, charge `23.924732 CPU-s`, its eight saved
  partial cases, and `recover_v1` syntax failure, charge `0.069671 CPU-s`.
  The accepted K20 recovery used the direct full-support construction;
  generic full-flow replay was not the accepted repair.
- SOURCE and CLOSEOUT receipts state actual dual original full-GET R3.
  SOURCE is immutable, SHA256
  `e606aea543f2dbf66832a549f4010ecb5cb51f642b45d6293ce1fd1b077f2a11`.
- The 20 stage-labelled checkpoints were assembled during closeout.
  This is explicitly historical timing. The new user requirement for
  contemporaneous stage publication and backup needs a new workflow that
  actually performs them at each stage.
- Central observation in this snapshot remains qualified `28/88`, 88 nodes,
  17 edges, current child count effect `0`; there was no central mutation.

The nonduplication evidence is direct: PR115 THEOREM section 4 says that
same-bin doubles alter total `d` without changing `C`, and that the fixed-`d`
joint boundary was not computed. Its DAG names
`CR_ENERGY_CROSS_FIXED_D_REGION` as a separate optional unit.

### PR114: total-double envelope

The inherited local snapshot of `research/cr_he_energy_sum_20261028` is the
immutable C08-era base `c87c50208a7585ff1713bd54303e1a1e29c962cf`, not an
assertion that PR114 stopped there. PR115's handoff records later PR114 heads
`3230790e...` and `3d9818b4...`; root's fresh remote survey must decide current
authority before borrowing later receipts.

The local theorem, implementation and saved SUMMARY establish

`D=dmax=(L+M)/2`,

where `L` is mass at `E<=K/2` and `M` is the maximum permitted high-low
matching mass. Low loops fill the remaining low legs. The maximum total `d`
is distinct from the chosen witness's cross `C`; the local README labels
the latter `CHOSEN_WITNESS_ONLY_NOT_MAX_C`.

The stored K6 `dmax` equals the PR115 K6 `cmax` as the same exact rational:

`3363067269495032297/6129982163463555433433388108601236734474956488734408704`.

This is a comparison of existing serialized values, not a rerun. K2 and K20
also have saved exact total/cross extrema and are useful retained cases.

## 3. Input and code that can be reused

The local NPZ bytes were hashed without loading arrays:

- Path: `research/cr_he_energy_cross_20261028/inputs/ATTRIBUTION_ARRAYS.npz`.
- SHA256:
  `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`.
- Retained source revision:
  `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`.
- Original source JSON SHA256:
  `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`.
- Saved atom digest:
  `2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690`.
- Immutable PR112 consumer SHA256:
  `6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d`.

Retain 3,200 active atoms plus the distinct cutoff ghost; exact binary64-to-
rational conventions; the four unchanged birth-energy partitions; conditional
100 K H1/He4 state; explicit `nb=8750/47 m^-3`; fixed proper volume, gas rest
frame and zero recoil; `q_i(t)=t A_i` on proper `[0,10^10] s` only. Apply
`W=(b^2-a^2)/2` once. Saved RR and retained photons remain separate once-only
ports. Actual physical K, exclusive kernel, outside response, donor work,
EOS/T, absolute volume and full physical native25 remain null.

| Existing component | Safe reuse | Required new work |
|---|---|---|
| PR112 `event_union.py` | Byte-pinned source loader, event claims, same-state species and charge/energy bookkeeping, inventory/history/replay guards | New joint witnesses must pass the unchanged consumer; do not weaken attestation |
| PR114 `energy_sum.py` | Exact total-double theorem/certificates and saved native maxima; validated `E<=K/2` split and diagonal convention | Reuse saved maximum witnesses where actually available, or classify a genuinely new construction separately |
| PR115 `cross_envelope.py` | Exact cross bound and dual, domain/source binding, saved certified extrema | Joint geometry and witnesses having independently specified `d` and `C` |
| PR115 `cross_flow.py` | General exact cross primal machinery and existing validation record | Do not repeat the expensive K20 chain calculation; no claim of constant/linear max-flow time |
| Saved summaries / manifests | Exact endpoint values, existing marginal digests and accepted failures | New dependency changes only; no old source fit, transport, quadrature or RR replay |

The old consumer already computes full-source union species from total `d`
and the partition-sum correction from `C`. Thus the new mathematical object
has an existing concrete consumer, rather than requiring a new physical model.

## 4. Why the joint object changes a concrete return

For full selected support, write `N=sum_i w_i`, total internal-double count `d`,
and cross-bin double count `C`. Per coefficient, the source-union returns are

`He(I,II,III)=(-N+d, N-2d, d)`,

`parents=N-d`,

`Uchem=I1*N+(I2-I1)*d`, with `I1=24.59 eV`, `I2=54.42 eV`.

The independently summed partition return has an additional `( -C,0,+C )`
species contribution, so the once-only union correction is `(C,0,-C)` and
its chemical-reference correction is `-(I1+I2)*C`. A joint admissible region
therefore couples parent consumption / source chemical storage to the allowed
partition correction. Separate `d<=D` and `C<=X` bounds do not supply this
correlation.

Multiply all coefficient counts/energies by W once and divide native species
by the same explicit nb. For an inventory condition the valid restriction is
`d>=max(0,N-Hneutral/W)`, not a generic lower bound on C. Any inferred C
restriction must follow from the new joint theorem. The current actual source
already passes the all-single inventory endpoint, so this survey does not
claim that its present inventory gate becomes active.

### An exact general-domain discriminator

Take K=1, four unit-mass atoms: partition A has energies `3/10,9/10` and
partition B has energies `1/20,3/5`. This is a labelled general fixture, **not**
the native energy-bin partition. Let p be A-high/B-low cross mass, q be
B-high/A-low cross mass, r be low/low cross mass, and s be B-high/B-low
same-bin mass. The only loops are on the two low atoms.

The exact projected region is

`0<=C<=2`, `C<=d<=3/2+C/4`.

To attain its upper boundary use `p=q=C/2`, `r=0`, `s=1-C/2`, the A-low
loop of mass `(1-C/2)/2`, and the remaining high-A single. To lower d at fixed
C, continuously remove the same-bin events into singles. The upper bound
follows from `q+s<=1`, `p+r+s<=1`, `C=p+q+r`, and low-leg accounting.
Thus `(d,C)=(2,0)` is outside the joint set even though both separate maxima
are 2. This does not contradict either predecessor, which did not claim a
joint rectangle. It is a new exact test for a general joint implementation.

## 5. Recommended next option: closed joint polygon at separated low/high bins

This option is materially narrower and cheaper than a full generic parametric
weighted-matching implementation, while directly including retained native
K2, K6 and K20 cases.

### Exact scope condition

Every allowed high-low pair must be cross-bin; equivalently, no same-bin
high-low pair satisfies `E_i+E_j<=K`. All low-low pairs and low loops remain
allowed by the energy cap. This follows for the native declaration at K=2
and K=6 because K/2 is an exact energy-bin boundary; at K20 there are no high
atoms. It is an actual verifiable condition, not a new forbidden-edge mask.

A linear scan can check it by each partition's minimum low and minimum high
energy: if both exist and their sum is at most K, this specialized theorem's
scope condition fails. No eligible pair is silently removed.

### Candidate theorem and constructive first connection

Let `L` be total low mass, `M` maximum high-low matching mass,
`D=(L+M)/2`, and `X=Cmax`. Under the scope condition, the proposed exact joint
region is

`P={(d,C): 0<=d<=D, 0<=C<=X, C<=d, 2d-C<=L}`.

Necessity: high-high pairs are absent. If m is high-low mass and l total
low-low mass, then `d=m+l`, `2l+m<=L`, and `m<=C`, because every high-low
pair is cross-bin. Consequently `2d<=L+C`. The other bounds are inherited
primal bounds or definitions.

The crucial additional lemma is compatibility of the two maxima. Among
cross-maximal witnesses choose one with the greatest high-low mass m. If
`m<M`, its bipartite high-low residual graph has an augmenting path ending at
a low atom with capacity unused by high-low pairs. If that capacity is a
single, augmenting increases C, a contradiction. If it is occupied by a
low-low cross pair, remove a sufficiently small mass from that pair and
augment the high-low path by the same mass: C is unchanged and m increases,
again a contradiction. Hence a cross-maximal witness with `m=M` exists.
Fill every remaining low leg with its allowed loop, giving `(d,C)=(D,X)`.

The other attainable vertices are `(0,0)`, `(L/2,0)`, `(D,M)` and `(X,X)`.
Their convex hull is precisely P (with coincident vertices removed).
Convex combinations combine the exact event measures and preserve every atom
marginal. This gives a concrete route to every point of the polygon.

This lemma and the full region need independent proof review before admission.
The survey does not claim that generic K3 or K10, which have a straddling bin,
satisfy this specialized formula.

### Observable meaning and native selection

At fixed d, the exact proposed correction interval becomes

`max(0,2d-L) <= C <= min(d,X)`.

At native K6, saved exact `D=X`, so the joint polygon is a quadrilateral
after degeneracies. Its lower correction endpoint at maximal d is `M=2D-L`;
its upper endpoint is D. Native K2 has `X<D`, giving the general five-vertex
case. K20 supplies the complete-support / all-low limiting case, for which
old direct half-shift and diagonal constructions are available.

This result changes the admissible combinations of a parent/chemical source
return and its bookkeeping correction. It still leaves actual physical d,
C and K unidentified; no physical heating or rate is activated by the polygon.

### Implementation and cost implications

Region metadata and affine observable mapping require O(n) source scans plus
the already established D/X ingredients. The vertex `(D,M)` uses a maximal
high-low witness plus residual low loops. The vertex `(X,X)` uses a maximum
cross witness plus singles. The compatibility construction needs residual
high-low augmentations only when a saved cross witness is not already
high-low maximal. `(D,X)` then follows by adding low loops.

Native K6 has D=X exactly, so any exact maximum cross witness already has
the required total d. K20 has M=0 and its direct witness can be reused.
K2 is the useful nontrivial compatibility/completion case. Reuse a published
full PR114 witness only after obtaining and checking its actual saved bytes;
the local compact SUMMARY alone is not the full primal certificate.

Each new witness should be checked atomwise, including same-atom loop
incidence twice, all pair support, actual d/C sums, and the unchanged consumer
formulas. General-domain controls must reject the specialized theorem on a
same-bin eligible low-high pair. Independent small fixtures can compare an
explicit LP/vertex enumeration against the proposed polygon. A native
support-condition check must not be replaced by the labels 'K2' or 'K6'.

The old prefix-chain solver exhausted its first native reservation before K20
completed. That observed failure is a concrete cost warning for a new weighted
or repeated-flow design. Reuse saved endpoints and cheap complete-support
constructions; benchmark only the changed nontrivial construction after the
new root-owned budget is frozen. This survey allocates no new allowance.

### Actual saved PR114 primal-certificate locator

The exact full certificate is
`research/cr_he_energy_sum_20261028/runs/primary_v2/PRIMARY_CERTIFICATES.json`,
15,160,355 bytes, SHA256
`4f3cad59cb65f901b72674ce99749878efe6ca84ff3e0e337e38540b0c06540e`.
This identity is recorded by the existing independent-v1 RESULT and
`coding/C07_INDEPENDENT_ACTUAL.md`. The file is not present in this local
checkout and is explicitly archive-only. Its schema, as authored in the
saved primary module, contains `native_atoms` and `native_cases`; each native
case contains `id`, `K_eV`, `dmax`, `target_d`, `dual_by_key`, `max_events` and
`events`. Select `max_events` for the total-maximum witness; K3's `events`
deliberately use half the maximum and must not be substituted.

The sibling backup survey has located the existing candidate canonical archive
`BASS_CR_HE_ENERGY_SUM_SOURCE_20261028_3230790ebeb2.zip`, 3,255,109 bytes:

- Drive ID `18nYXTNsWg5dFPEOS-sKjmdgge0FJUDON`.
- Dropbox ID `id:BSpOijBcT10AAAAAAEFUmw`.
- Metadata evidence: `next_survey/backups_context/DRIVE_CR_METADATA.json` and
  `DROPBOX_CR_METADATA.json`.

Those are observed archive locators, not a claim that this survey downloaded
the archive or checked its member payload. Root can acquire the existing
SOURCE, verify its release SHA/manifest and the specific full-certificate
identity above, then reuse K2/K6/K20 `max_events` and `dual_by_key` without
calling the previous solver. If a matching source member is absent, report
the precise missing witness rather than relabelling the compact summary as
a full certificate.

The root-selected possibility of a C++ `__int128` flow backend belongs after
the future C5 implementation checkpoint. A safe contract would compute exact
integer capacities in Python, assert the admitted sum bound before conversion,
and independently verify all returned integer flows/cuts after conversion.
No such backend was implemented or compiled during this survey.

## 6. Other next-unit options

| Option | Constructive first connection | Scientific increment and remaining input |
|---|---|---|
| A. Separated-bin exact joint polygon (recommended if fresh survey finds no superseding work) | Prove the compatibility lemma above; compose actual event-measure vertices and apply the existing consumer | Correlated parent/chemical/correction admissibility on retained native boundary caps, with modest new algorithmic work |
| B. General K, including a straddling bin | For allowed pairs including loops, optimize `alpha*d+beta*C`; dual requires `y_i+y_j>=alpha+beta*1_cross`, including `2y_i>=alpha` on loops. Or fix flow `F=2d` in a bipartite double cover and optimize cross edge cost | Full piecewise-linear joint frontier; needs exact min-cost/parametric flow and new cost/proof analysis. Separate bounds and unweighted flow are insufficient |
| C. Actual source-specific exclusive kernel | Bind `d sigma_single/dE` and `d² sigma_double/dE1 dE2`, isotope/state/projectile distribution, excitation/recoil and donor-energy bookkeeping to the retained marginal | Supplies physical d/C or justified support. Current local files do not supply it; new primary/provider input is required. A constant actual K must not be inferred from the conditional scans |

Option B's support graph can still use prefix connections, with same-bin and
cross-bin costs kept on entry edges, but constant-weight unweighted dual labels
`0,1/2,1` are not a complete general parametric certificate. Full polygon
enumeration may have many breakpoints; no cheap full-native bound has been
established by this survey. New references are required for any adopted
general weighted-flow claim.

## 7. Project attachment reuse and coverage

All 20 attachment SHA256 values are recorded. The first 11 current attachments
match historical entries in the extracted August source-dependency manifest.
Selected current members of ZIP11/12/17 were byte-identical to their prior
extracted copies (five comparisons). ZIP17's whole SHA also matches its
provided `.sha256` sidecar.

Thus the prior findings can be reused for those exact inspected objects:
ZIP11 is the PATCH80R/81R low-ell automation flow; ZIP12 is the August 3
background/high-l harness snapshot; ZIP17 is the August 18 locked Rust core
and historical 122-test record. They do not supersede the October bass_cr
science branch. No historical Rust/Python execution was relabelled current.

ZIP18/19 were inspected by their member names only. Their filenames did not
identify an exclusive He double-ionization kernel; this is not a claim that
all paper bodies were searched. The attached report's first three pages
identify the September 13 HTT/CMB morphology and statistical-theory compendium,
not a CR exclusive-source handoff. Large Rust/vendor/xAct archives were hashed
but not unpacked or installed. No full literature-body or global conversation
coverage is claimed here.

## 8. Concrete handoff to the root survey

Before selecting A/B/C, combine this local finding with fresh remote PR114/115,
PR113, relevant source-owner/DAG and backup observations. If no actual exclusive
input or overlapping joint-support implementation appears, A is an exact,
nonduplicative bounded next unit with a current consumer and retained source.

The next unit must use its own contract/budget and current-user authorization;
all predecessor closures and failed attempts remain. Freeze R1 before science,
and actually publish/back up each R/C stage contemporaneously as requested.
Do not reproduce PR115's closeout-only checkpoint timing under a new label.
