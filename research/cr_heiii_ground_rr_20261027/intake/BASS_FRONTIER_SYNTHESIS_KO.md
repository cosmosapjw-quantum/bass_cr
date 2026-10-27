# bass_cr 최신 frontier 조사 — 2026-10-27

## 결론

현재 공개된 bass_cr source frontier는 PR106의 Documents D
`b11b2e9255f2b10fb5582376412e045bd1e9151c` 그대로다. 전수 metadata census에서
현재 branch **184개**, open PR **105개**, closed PR **1개**를 확보했고 각각
끝 페이지까지 확인했다. 2026-10-25 이후 닫힘/병합 PR은 **0개**다.
원격 repository metadata의 pushed_at은 `2026-10-25T13:36:46Z`다.

새로운 원문 증분은 2026-10-26의 **백업 backfill 영수증**이다. PR105의
H1 canonical/authority Drive 후속 보존과 PR96의 C22C Drive 14-part 복원은
새 storage 객체의 성공 기록으로 이어 붙인다. 과거 UNKNOWN_NO_ACK는 해당
시점의 사실로 보존하고, 물리 채택이나 재실행으로 세지 않는다.

다음 실행 단위는 source-qualified **He4++ + e → He4+(1s) + spontaneous photon**
ground RR 소비자가 적절하다. 현재 입력과 전자 체인을 재사용할 수 있고,
기존 He4+ → He4 neutral ground 결과와 분명히 구별된다. 접근한 현재
branch/PR 및 관련 source 문서에는 이 후속 소비자를 이미 수행한 별도
owner가 확인되지 않았다. 미게시 개인 worktree나 접근 불가능한 대화의
부재까지 증명한 것은 아니다.

## 조사 범위와 pagination

| 표면 | 실제 회수 | 종료 확인 |
|---|---:|---|
| branches, per_page=100 | 100 + 84 = 184 | page 3 = [] |
| open pulls, per_page=100, updated desc | 100 + 5 = 105 | page 3 = [] |
| closed pulls, per_page=100, updated desc | 1 | page 2 = [] |
| 연구 root at fixed D | 107 directories | GitHub contents response |
| He4 subtree | 123 entries | truncated=false |
| external-interface subtree | 30 entries | truncated=false |
| expansion-assignment subtree | 4 entries | truncated=false |
| C23B subtree | 448 entries | truncated=false |
| PR105 current discussion | 1 comment | complete short page |
| PR96 current discussion | 2 comments | complete short page |

전체 branch 이름/정확한 head와 모든 PR의 상태·head/base·시간은
`INVENTORY.json`에 있다. 최신 PR bodies, native source, 계약·manifest·기존
source audit는 `snapshots/`에 보존했다. 처음 root recursive-tree fetch의
Transport closed는 scientific failure가 아니며, 실제 관련 subtree GET으로
필요한 source 목록을 확보했다. 전체 repository의 모든 과거 blob을 읽었다는
주장은 하지 않는다.

## 주요 source authority와 재사용

| 범위 | 현재 authority | 재사용 내용 |
|---|---|---|
| PR106 / expansion | D b11b2e9255f2b10fb5582376412e045bd1e9151c | HeI-ground RR, external source/event interfaces, exact delivery |
| He4 science S | 4caf4273eefd51f2c605a8667c3533d8489dd0f5 | 8 saved chains, 192 primary RHS, scoped independent checks |
| PR105 H1 | D b1aed87852d4f8994494c2ae41a913afd390eccd | H1 ground RR remains in common killed operator |
| C23E | 8623d7b2035677fc231976d85fea309f48afd57c | Existing signed event results; no source/ODE replay |
| C23B provider at D | spectral_photo_source.py blob e7d474d5145cb264102206e0403b0aa5916c3140 | Exact point cross section only; quadrature not called |
| Verner native table | blob 754b5ce11cbe662f96394430beeafe3f102f339c | HeII (Z,N)=(2,1) exact parameter row |
| REI151 | 8a4f5df46f6e3058f5e685b85cc1cf3c20926368 | Ground Milne formula, electronic d=1 HeII convention |

Point-provider file is 10,712 bytes, SHA256
`71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`.
Table is 17,760 bytes, SHA256
`a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.
The downloaded text bytes reproduce both advertised Git blob IDs. Full identities
of 14 actual retrieved files are in `SOURCE_SNAPSHOT_MANIFEST.json`.

The REI151 rate module was **read, not imported**: module import would construct
historical quadrature nodes. The existing rate block and independently failed BDF
kinetics reference remain separate claims.

## Source-qualified next channel

The native table row is

```
Z=2, N=1
(I_eV, Emax_eV, E0_eV, sigma0_Mb, ya, P, yw, y0, y1)
= (54.42, 50000, 1.720, 13690, 32.88, 2.963, 0, 0, 0).
```

The recombination is bare He4++ plus a tagged electron into He4+ ground 1s.
Electronic weights are g_bound=2 and g_ion=1, hence d=2*g_ion/g_bound=1.
The inherited composition assigns n_HeIII=0.01 cm^-3. The hazard uses this
capturing-ion density, not thermal ne=0.14 cm^-3. The source remains an elemental
HeII model conditionally mapped to He4; no empirical isotope-resolved correction,
finite-mass target averaging, recoil or angular emission law is supplied.

For E>0 and E+I within [54.42,50000] eV,

```
sigma_RR(E) = sigma_PI(E+I) (E+I)^2 / [d (m_e c^2)_eV E]
lambda_HeIII(E) = n_HeIII * v(E) * sigma_RR(E).
```

Use the preserved CR electron mass 9.1093837015e-31 kg with exact current c and eV
conversion. The REI151 mass is distinct and does not silently replace it. Preserve
the fit-native threshold alongside all its coefficients; do not substitute an
independently chosen ionization energy. No source extrapolation or E=0 floor is
authorized by this source reading.

Per event: fast electron count -1, HeIII -1, HeII +1, photon +1;
signed energies are fast -E, internal -54.42 eV, photon +(E+54.42) eV. The retained
photon is a radiation owner, with no bath-heat assignment.

## Numerical baseline selected by root

Root selected **A**, communicated during this survey:

```
K_new = exact stored PR106 HeI K_diag + diag(new HeII hazard).
Independent Decimal reference =
    Decimal(stored PR106 HeI K_diag) + Decimal(new HeII hazard).
```

The existing HeI rounding-loss diagnosis is inherited and remains recorded.
All old off-diagonals, first-entry/CE/bath RHS, H1 hazard, HeI hazard, saved
source projections and source masks remain exact inputs. This allows a new
single-addition comparison without replaying a completed H1 or HeI solve.
The current He4 NPZ fields include `K_H1_diag`, rounded `K_diag`,
`lambda_He`, `lambda_H1`, `rhs_physical16`,
`solution_physical16`, `p_H1`, `p_He`, and stable response columns.

A distinct alternative B would set the real operator to
stored H1 K_diag + lambda_HeI + lambda_HeII. B is **not** the selected baseline
and remains a future comparison. Its exact-real sum must not be silently
identified with A after the inherited binary64 HeI addition.

The single-new-hazard total bound may be reused for A:
w=K_old^-1 lambda_new, eta=max(w), and w/(1+eta)<=p_new<=w.
For several simultaneous newly added channels, the existing source review
already supplies a two-state counterexample to a per-channel multiplicative
lower bound. Reuse that result and the valid individual additive estimate rather
than rediscovering or relabeling it as a new strong no-go.

Stable signed change for a reused nonnegative response h_old is
-K_new^-1 diag(lambda_new) h_old. Its frozen meaning must include the stored
baseline column used on the RHS; independent review checks the corresponding
new linear problems. Per-channel photon/internal rewards retain their individual
13.60 / 24.59 / 54.42 eV thresholds in the shared competition matrix.

## Recovery input paths

The He4 canonical source archive is
`BASS_CR_HE4_EXTERNAL_SOURCE_20261025T131931428504Z_4caf4273eefd.zip`,
29,763,489 bytes, SHA256
`7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa`.

Within it reuse:

- `research/cr_he4_ground_rr_20261025/inputs/INPUT_MANIFEST.json` and CONFIG;
- `inputs/reused/pr104/chi{1.5,3}_R{40,80}_N{1024,2048}.npz`;
- `inputs/reused/pr105/chi{1.5,3}_R{40,80}_N{1024,2048}.npz`;
- the eight new PR106 He4 results under
  `runs/cr_he4_rr_primary_20261025_v1/`;
- three `inputs/reused/c23d/ATOMS_{2.316,2.479,2.649}.csv`;
- the exact C23B point provider and table.

The parent owns archive recovery. This child downloaded no duplicate canonical
archive and performed no array solve, quadrature, projection rebuild, ODE or
old test replay.

## October 26 backup observations

PR105 comment 6415035533 reports:

- H1 canonical Drive `1eXKj4aQUXPW_XjMtKjPVvghseaT8pnpU`,
  18,232,953 B and SHA256 f1afdb40303b28a498a62f9f8d38858b8bea584d0ed8a4e63bd87e4e11d362c5;
- authority JSON Drive `1cwtOkPLqVoXrEj8r_ZepPQ-F5H3VcQHy`,
  38,849 B and SHA256 5f37395452dea969b9f35ec295b667daadf01928e98c6280dbb56d241d852a94;
- actual whole Drive raw readbacks matched source bytes;
- existing Dropbox objects were untouched; fresh Dropbox raw GET NOT_RUN.

PR96 comment 6415034627 reports C22C ZIP
114,019,304 B, SHA256 b8e3448a8cdba0f0b8512dc241098a1829400c37064917048d8438788655c3fb,
in Drive folder `1dFvfDSGpXaOBOILUfVDUYRwQSZrBDfvS`, 14 contiguous immutable
parts and reconstruction manifest, all part raw readbacks plus whole SHA/CRC and
657 internal payload checks passed.

Both cite audit ZIP Drive `1Hw_ywJ8uLdSZPR60SdGWgaIt8K3-T-Gz`.
These are **comment observations** in this child; the parallel backup investigator
owns direct provider/receipt verification. Exact bodies and IDs are preserved in
`COMMENTS_105.json` and `COMMENTS_96.json`.

## Gates, costs and survey limits

N4/N5 remain PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4=false,
global physical completion/error bound=null. This survey does not alter any
DAG count. The central investigator supplies the exact latest whole-DAG count;
the old D file's 87-node central observation is historical, not a current census.

H1 known lineage 39.097868524 CPU s and C23E separate lineage15.493261114 CPU s
are not summed without overlap proof. Previous HeI 4.207939602 CPU s and external
interface0.147428830 CPU s remain their own completed-unit records. New unit
allowance must be separately bound. This child's scientific executions and new
scientific CPU debit are zero; one mechanical snapshot/hash operation measured
0.001355288 CPU s.

Skill context: physmath plugin1.3.0 main, POLICY_INTEGRATION and THEORY_LOOP
R1–R3 definitions actually read; user-supplied1.0/v0.2 scope preserved. This is
source/survey support only and does not assert R4–R10 or any coding-stage completion.
No recursive delegate, remote mutation, PR comment or publication occurred.

Private/local unposted work, deleted or unadvertised refs, inaccessible
conversations and historical provider uploads without a current receipt remain
outside this census. All current GitHub branches and pull requests were listed;
relevant current documents were read. No broader absence conclusion is needed to
begin the new source-qualified conditional HeIII consumer.

