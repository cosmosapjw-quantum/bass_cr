# PHYS02 부모 사건과 조건부 native25 유한 반환

## 문서 상태와 현재 결론

**C05–C08의 실제 산출물을 반영한 최종 보고서용 후속 초안이다.** 실제 게시·dual R2의 기준점은 C08 commit `d84de9418a135b093a589af8dfc35d8d40c0d821`의 **18/20**이다. C05 preparation은 15/15, 기존 C06 controls는 50/50, C07의 두 targeted controls는 2/2, 복구된 primary는 58/58을 통과했다. controls는 **51개 unique name / 52회 평가**이며 같은 검사 한 번의 복구 평가를 새 검사로 중복 세지 않는다. C08 독립 비교의 원 run은 **3446/3450, 4건 실패**였고, 실제 exact-zero oracle 복구는 **4/4 PASS**다. composite는 **3450개 unique 검사 PASS = 원3446개 재사용+새4개**, 전체 실제 평가 이력은 **3454회**다. 원 FAILED 결과와 비용은 보존된다. 그림 worker와 root의 실제 육안 검토도 완료됐다. C9의 최종 독립 심사와 C09–C10 게시 완료는 아직 PENDING이다. [C08 실제 요약][c8]

중앙은 **28/88**, 이번 CR의 원 중앙 집계 효과는 **0**이다. 과학 실행 완료 시점의 실제 장부는 **charge10.45384/40 CPU-s = measured9.80384 + conservative tails0.65**이며 미사용 **29.54616은 nontransferable**이다. S/D/M, canonical SOURCE·CLOSEOUT, 실제 R3와 Library ID는 여전히 null이다. 이전 C04/14-of-20 초안은 `parent_ops/drafts/preserved_C04/`에 보존했고, root는 마지막 표의 실제 receipt·판정·게시 필드를 채운 뒤 최종 확정한다. 이 문서 보완은 저장 증거의 읽기와 문서 작성만이며 새 과학 실행·import·compile·network·게시를 수행하지 않았다. 메타데이터 CPU는 미측정이다.

이번에 해결하려는 문제는 저장된 PHYS02 저에너지 전자 source의 H/He 기원을 식별하고, 그 부모 원자의 변화와 이미 계산된 유한 RR·cutoff 반환을 같은 물리 상태의 native25 장부에 연결하는 것이다. 이론은 **표적별 전자 귀속과 필요한 He 사건 family를 구성할 수 있음**을 보였다. 반면 inclusive He 전자 spectrum만으로 exclusive single/double ionization 사건, 선택 밖 partner, 잔류 He⁺ excitation 또는 실제 proton 에너지 debit가 결정되지는 않는다. 따라서 numerical criteria를 나중에 모두 통과하더라도 실제 full physical native25 점은 자동으로 얻어지지 않는다. 이 구분은 오류를 감추기 위한 임시 예외가 아니라 이번 입력의 식별 가능 범위다. [고정 계약][contract], [교정된 유도][theory], [R6 독립 심사][r6]

```json
{
  "unit": "CR_PHYS02_PARENT_EVENT_NATIVE25_V1",
  "unit_path": "research/cr_parent_event_native25_20261028",
  "PR": "https://github.com/cosmosapjw-quantum/bass_cr/pull/111",
  "draft_reference_commit": "d84de9418a135b093a589af8dfc35d8d40c0d821",
  "draft_reference_actual_published_dual_R2_stages": 18,
  "final_actual_published_dual_R2_stages": null,
  "primary_status": "PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN",
  "primary_checks": "58/58",
  "controls_unique_names": 51,
  "control_evaluations": 52,
  "independent_v1": "FAILED_3446_OF_3450_WITH_FOUR_ORACLE_FAILURES",
  "targeted_reference_recovery": "PASS_4_OF_4",
  "reference_composite_unique_accepted": 3450,
  "reference_actual_evaluations": 3454,
  "observed_charged_CPU_s": 10.45384,
  "C9_final_verdict": null,
  "S": null,
  "D": null,
  "M": null,
  "canonical_SOURCE": null,
  "final_CLOSEOUT": null,
  "Library_ids": null,
  "automatic_next_scientific_unit": false
}
```

## 1. 실제 입력, 계보와 동일 상태

원 입력은 retained revision `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`에 결속된 PHYS02 source다. 이 revision은 보존된 이전 snapshot이며 최초 생성 commit이라고 주장하지 않는다. 실제 JSON `research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json`의 SHA256은 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`다. 이 JSON과 binary NPZ는 보존된 archive payload로 식별하며, Git에 게시되지 않은 경로의 raw 링크를 만들어 접근 가능하다고 주장하지 않는다. 전체 17개 source payload의 bytes/SHA와 역할은 `inputs/INPUT_MANIFEST.json` 및 [SOURCE_LINEAGE_MANIFEST][lineage]가 규정한다.

| 입력 | 고정 identity와 이번 역할 |
|---|---|
| PHYS02A 저장 band moments | `NUMERICAL_RESULT.json`, SHA `4e210fb042c8b4d92fd8577b30af78686500de8d7b7ea89be5baeea6564ee1f8`. 세 recovery band와 세 holdout band의 원 binary64 값 |
| 원 Rudd port | `rudd.py`, SHA `757e4c8b33618ad6ef88f422919fe813654454c836f0942cf9792be133e8eac2`. rational basis·threshold·원 source convention |
| 원 projector | `causal_cascade.py`, SHA `d87a9cc122125b2d37b47f261f57eab698baa59e07a6b21723860f39313c7b72`. cell별 Gauss8 및 number-linear projection 정의만 읽음 |
| 원 total low source | 앞의 `ACTUAL_SOURCE_RECORDS.json`. `direct_0p1_10` tag, 원 3200 active atoms와 별도 cutoff ghost의 authoritative bytes |
| PR110 저장 응답 | `runs/primary_v1/RESULT.json`, SHA `ae8452f25958c47349d313926ef14e7ab7d78691ba6bb3b8395dc399aa49b0ce`; `ARRAYS.npz`, SHA `2c3624e4ca6d087436f79360497e75b0c84fb2c8ea6b83bb855a9a0cd0005c1d`. 네 prefix/네 observation bin의 RR·cutoff·Coulomb·photon 원 항 |
| 현재 고정 입력 manifest | 17 payload, SHA `2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3` |

선택한 birth support는 **0.1–10 eV**이고 원 projectile 범위는 **1–4 MeV**다. `q_j(t)=t A_j`가 알려진 proper-time 구간은 **0≤t≤10¹⁰ s**다. 그 밖의 continuation 또는 shutoff는 주어지지 않았다. frame은 gas-rest, nonrelativistic scalar이며, fixed proper-volume density를 사용한다. 절대 proper volume이 없어 worldtube 총 N/E는 null이다. 현재 에너지가 10 eV 이하라는 이유만으로 high-born atom을 섞지 않는다. 0.1 eV ghost는 원 첫 cell의 projection 결과이며, 0.1 eV 미만에서 태어난 실제 전자 분포를 새로 추정한 것이 아니다. [계약][contract], [유도 §1·5–6][theory]

recipient는 PR110에서 명시한 **새 조건부 H1/He4-only total-nuclei inventory**와 정확히 같은 의미를 갖는다.

| 상태량 | 값과 의미 |
|---|---|
| T₀ | 100 K, 응답 계산의 frozen bath |
| nH | 140 m⁻³, neutral HI가 아닌 전체 H 핵 수 |
| nHe | 1085/94 m⁻³, 전체 He 핵 수 |
| xHII, xHeII, xHeIII | 0.01, 0.01, 0 |
| 초기 ne | 2849/1880 m⁻³ |
| nb | 8750/47 m⁻³, per-baryon 사상의 명시적 분모 |

source의 0.99 neutral target factor, 원 comoving→proper 729, projectile speed와 angle integration은 원 A에 이미 들어 있다. 새 시간 적분·native 사상에서 다시 곱하지 않는다. H/He→H1/He4는 명시적 isotope 조건이지 새 isotope-resolved 측정 결과가 아니다. 과거 PR109의 nb=null을 소급 변경하지 않고, PR107/108의 10000 K bath나 PR236/PW19의 T·nb를 가져오지 않는다.

기존 REI 코드에서는 21 species 뒤 ζ₂₁, w_nt,₂₂, w_ext,₂₃, logT₂₄의 순서와 atomic-storage 표현을 확인했다. 그 근거는 [native atomic model][native-model], [native coefficients][native-coeff], [atomic-storage consumer][storage-consumer]다. 이 코드가 존재한다는 사실이 현재 CR의 실제 전체 상태·partner·EOS를 제공하는 것은 아니다. 이번 명명된 소비자 `consume_selected_parent_event_window`는 새 동일상태 partial/conditional contract이며, foreign consumer activation은 false다.

## 2. 새로 식별할 양과 재사용할 계산

고정 source 모형은 표적 s에 대해

\[
A_s(W)=\frac{c_{1s}+c_{2s}W/I_s}{(1+W/I_s)^3}
\]

를 사용한다. H Williams-limit의 실수식 `c1_H=(7/3)c2_H`에 따라 세 고정 basis로 쓸 수 있다. 코드의 계수 순서는 `theta_H=c2_H`, `theta_He1=c1_He`, `theta_He2=c2_He`다. 이론 본문의 0-based He 기호와 코드의 1-based 이름은 R6에서 명시적으로 대응시켰다. 접미사만 보고 열을 바꾸지 않는다.

새 계산은 저장된 **[0,0.1], [3,10], [100,1000] eV** band energy moments에서 80-digit 3×3 system을 푸는 것이다. **[0.1,1], [1,3], [10,100] eV**는 fit에 사용하지 않은 holdout이다. 넓은 band는 공유된 source 계수를 식별하는 정보이며 이번 transport birth support를 1000 eV까지 확장하지 않는다. 원 64-point proton quadrature, full G9600, 이전 Cascade·RR solver는 실행 대상이 아니다. 새 계수는 `MODEL_IDENTIFIED_FROM_PINNED_MOMENTS`이며 과거 저장 coefficient bytes를 복원했다고 명명하지 않는다. [유도 §2–5][theory], [계산 계약][computational]

작은 band moment는 양의 primitive와 고정밀 산술로 평가한다. 새 target basis마다 원 Gauss8·barycentric projector를 적용해 3200 active atoms와 ghost를 얻는다. projected atom에 점별 `A_H(E)/A(E)`를 곱하는 shortcut은 cell projection과 교환되지 않아 허용하지 않는다. H+He의 재구성 잔차를 한 표적에 밀어 넣거나 원 A를 renormalize하지 않는다.

검증 기준은 실행 전에 고정됐다.

| 검사 | 허용 기준 |
|---|---:|
| scaled matrix rcond∞ | ≥10⁻⁶ |
| 저장 moment consistency envelope η | 2×10⁻¹² |
| componentwise relative sensitivity | ≤10⁻⁸, 선언 envelope에서 계수 양수 |
| 각 positive holdout moment | 상대오차 ≤2×10⁻¹² |
| 각 positive canonical atom 및 split total N/E | 상대오차 ≤2×10⁻¹¹ |
| exact-zero atom | absolute zero |
| 독립 target별 N/E | 각 target 자체 scale에서 ≤10⁻⁹ |
| native stoichiometry·charge·baryon·energy·caloric 증분 | 해당 증분 scale에서 ≤10⁻¹¹ |

이 기준은 새 attribution 및 ordinary arithmetic의 일관성 기준이다. physical uncertainty, outward interval certificate 또는 전체 source의 오차 한계로 승격하지 않는다. 실패 시 `MODEL_IDENTIFICATION_UNRESOLVED`로 남기며 자동 four-coefficient fit, 원 source 재실행 또는 tolerance 확대를 하지 않는다.

## 3. 유한 시간과 부모–RR 합성

source birth extent는 알려진 이력 안에서

\[
J_s[a,b]=\tfrac12(b-a)(b+a)A_{sN},\qquad
U_s[a,b]=\tfrac12(b-a)(b+a)A_{sU}
\]

이다. endpoint rate는 tA이며 마지막 T에서는 known-history left limit이다. conditional mean time을 exposure로 쓰지 않는다. 네 누적 prefix는 비가산 진단이며, 실제 additive adoption은 네 disjoint observation bin을 사용한다. 저장 RR bin에는 앞 bin에서 태어나 살아남은 전자가 포함되어 있다. 각 bin을 빈 초기상태로 재시작하지 않는다. [유도 §6][theory]

inclusive He spectrum은 전자 수의 marginal이다. 실제 single·mixed-double·double-selected event의 누적 밀도를 각각 s,p,d로 두면

\[
s+p+2d=N_{eHe},\qquad p\ge0,\ d\ge0,\ p+2d\le N_{eHe}.
\]

mixed-double p는 선택 전자 하나 외에 선택되지 않은 partner 하나를 필요로 한다. 따라서 `N_eHe`를 actual HeI→HeII 사건 수로 바로 대입할 수 없다. 이 삼각형은 필요한 affine 제약이며, 전체 energy/time joint kernel의 충분조건이 아니다. 추가 branch 자료의 존재 가능성을 부정하는 strong no-go도 아니다. [Rudd et al. 1992][rudd], [문헌 대조][literature], [R6][r6]

동일 observation interval의 model-identified H births J_H, He electron births N_eHe와 저장된 selected RR captures C_H,C_He를 합치면

\[
\begin{aligned}
\Delta n_{H1I}&=-J_H+C_H,&\Delta n_{H1II}&=J_H-C_H,\\
\Delta n_{He4I}&=-N_{eHe}+d+C_{He},\\
\Delta n_{He4II}&=N_{eHe}-p-2d-C_{He},&\Delta n_{He4III}&=p+d.
\end{aligned}
\]

원소별 핵 수와 nb는 보존된다. 이는 선택된 direct collision의 장부이며 전체 외부 proton injection의 baryon history를 닫았다는 뜻이 아니다. source parent target과 RR capture target은 다른 label이다. H에서 태어난 전자를 반드시 H capture로 짝짓지 않는다. 이 species 증분을 같은 상태의 nb로 한 번 나누고 native index H1I/II=1/2, He4I/II/III=10/11/12에 놓는다.

출력은 `baseline + intercept + p*coefficient_p + d*coefficient_d`의 두 부분 표현을 보존한다. algebraic intercept의 p=d=0은 actual branch가 아니다. actual s/p/d와 unknown partner addendum은 null이다. 큰 baseline에 작은 source 증분을 더해 반올림한 endpoint는 diagnostic일 뿐이며, 그 차이를 역산해 authoritative 증분을 복원하지 않는다. source보다 훨씬 작은 RR 항도 `event_terms`에 원 값·hex·payload SHA와 함께 따로 남긴다.

## 4. 실제 반환, fixture와 아직 열린 항

| 구분 | 수용할 표현 | 실제 상태로 해석하지 않는 것 |
|---|---|---|
| 원 low source·저장 response | exact bytes에 결속된 A/E/history와 RR·cutoff·photon 원 항 | 새로 계산한 full source 또는 G9600 |
| 새 H/He 귀속 | 실행 기준 통과 시 fixed-model target attribution | 직접 측정한 exclusive He 분기 |
| native species | H transaction과 He affine p/d ledger | p=d=0을 actual 기본값으로 채운 full state |
| selected nonthermal subset | default cutoff-retention ζ/w_nt 기여 | 미지 partner를 자동 thermal electron으로 보충 |
| retained photon | 저장된 capture atoms/energy descriptors의 독립 port | 흡수·탈출·deposition·heating 또는 w_ext로 이동 |
| conditional fixture | p=0에서 d/N_eHe=0,1/4,1/2 및 명시적 EOS closure | actual branch probability, actual temperature point |

default cutoff는 retained unresolved reservoir다. 선택 subset의 `nb Δζ=ΔN_active+N_cut`, `nb Δw_nt=(ΔU_active+U_cut)eV_J`를 표시할 수 있지만 cutoff 아래 분포나 thermalization은 새로 만들지 않는다. instantaneous assimilation은 따로 명시한 fixture에서만 `N_cut`을 thermal count로 옮긴다. negative signed bin active change는 endpoint 차이일 수 있어 무조건 clipping하지 않는다. [유도 §8·10–12][theory]

binding convention도 별도 장부다. source H threshold는 **13.605693122994 eV**, recipient/RR H는 **13.60 eV**다. HeI는 24.59 eV, recipient HeII는 54.42 eV다. source 계열 상수와 PR110 CODATA2022 응답의 identity를 유지한다. H 차이 `0.005693122994 eV × J_H`를 heat로 숨기지 않는다.

\[
L_0=U_{inj}^{saved}+I_H^{src}J_H+I_1^{src}N_{eHe}
\]

는 원 source 모형의 selected kinetic-plus-binding functional이다. 실제 donor proton depletion/history는 아니다. native chemical storage는

\[
\Delta B^*=I_H^*(J_H-C_H)+I_1^*(N_{eHe}-C_{He})
 +I_2^*p+(I_2^*-I_1^*)d
\]

이고, literal convention residual과 branch lift를 별도 필드에 둔다. 추가 donor work에는 실제 I₂src, partner kinetic energy/history/response, residual excitation이 필요하다. recipient의 54.42 eV를 미제공 source double-ionization 자료로 대입하지 않는다. `actual_external_work=null`이며 retained-photon의 w_ext 기여가 0이라는 사실은 total actual w_ext가 0이라는 뜻이 아니다. [유도 §9][theory], [CRIPTIC Eq23–26][criptic]

명시적 ideal-gas EOS fixture에서만 `c_v=3k_B/2`와 thermal count 증분 n을 사용해

\[
\frac{\Delta T}{T_0}=\frac{Q/(c_vT_0)-n}{n_{part,0}+n},
\qquad \Delta\log T=\log1p(\Delta T/T_0)
\]

를 계산한다. retention fixture는 Q=Q_C eV_J, n=0이며, assimilation fixture는 Q=(Q_C+U_cut)eV_J, n=N_cut이다. 각 bin은 앞 prefix의 실제 **조건부** energy/count endpoint를 baseline으로 써야 한다. Q>0만으로 ΔT>0를 단정하지 않는다. 이 출력은 frozen100K response의 EOS postprocessing이며 source·hazard·stopping을 새 T로 갱신한 coupled thermal history가 아니다. **physical_heating_complete=false**를 유지한다.

## 5. 이론·문헌·상징 검증의 실제 상태

R6 판정은 `PASS_SCOPED_THEORY`, 12개 수동 심사 주제, 해결된 문서 교정 3건, 열린 blocker 0이다. 교정은 He coefficient alias, 실제 파일 경로, Eq7의 z=0 끝점에서 비음수 remainder 표시였다. 원 R5 SHA `2b74ce08…`와 교정 후 SHA **`1a35e091aed4e2db58f4db1d355cf88ccb79a9041a57330a76bf5ff2a5857652`**를 구별한다. R6는 numerical recovery PASS를 선언하지 않는다. [R6 원문][r6]

R7의 Wolfram 실제 evaluator 호출은 **1회**, 대수 residual **22개 모두 0**이다. moment derivatives·zero-width·charge/baryon·energy sidecar·finite-bin EOS·proper clock의 항등식에 한정된다. 앞선 context-tool internal error는 `symbolic/CONTEXT_CALL_V1.json`에 남아 있다. remote provider CPU는 null이며 이를 새 local 40 CPU-s에 임의 합산하거나 0으로 만들지 않는다. [실제 symbolic 결과][symbolic]

문헌 discovery에는 SciSpace·Exa 각 2회의 bounded 검색을 사용했고, Rudd 기관 사본의 읽힌 §I–II/§IV 일부, CRIPTIC primary PDF의 §2.3.3/Eq23–26 및 fixed upstream code, Meng 기관 사본의 제한된 범위를 대조했다. 직접 PDF/DOI 접근 실패와 extraction 경로를 남겼으며 PDF original-byte full GET를 수행했다고 주장하지 않는다. 문헌에서 가져온 것은 electron marginal의 의미와 원 loss functional이다. PHYS02 1–4 MeV·0.1–10 eV에 대응하는 exclusive He joint branch가 확보됐다고 쓰지 않는다. [문헌 범위·접근 영수증 지도][literature]

## 6. C05–C08 실제 결과와 실패를 보존한 독립 복구

### 6.1 식별·projection 및 보존된 preparation

`runs/prepare_v1/PREPARATION.json`은 **15/15**, `PASS_SCOPED_MODEL_IDENTIFICATION`이다. 파일은 28,835 bytes, SHA `da5c18c810f47d501648faf77c398f4f0f91c9da9066c7f38c196e989d2eb39f`이고 원 producer는 `69e7068573401db41f8c37797b47e455b684979b4094424d2156c05a126bcc81`이다. 생성된 `ATTRIBUTION_ARRAYS.npz`는 233,050 bytes, SHA `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`로 이후 primary에 그대로 복사됐다. [C05 실제 요약][c5]

다음 값은 저장된 80-digit 원문의 표시용 유효숫자다. authoritative 값은 원 JSON의 decimal string이다.

| 식별/검증량 | 실제 저장 결과 |
|---|---:|
| theta_H | 약 1.344181900712665×10⁻³⁶ |
| theta_He1 | 약 2.539899387530946×10⁻³⁷ |
| theta_He2 | 약 6.741633240728523×10⁻³⁸ |
| scaled rcond∞ | 약 0.0576573628085325 |
| 최대 componentwise sensitivity | 약 1.568397143914627×10⁻¹⁰ |
| 세 holdout 상대오차 | 4.460268496549474×10⁻¹⁴, 3.398973603644494×10⁻¹⁴, 5.128719123831941×10⁻¹⁴ |
| 3201 canonical atom 최대 상대오차 | 5.3532333465297213×10⁻¹⁴ |
| canonical total N/E 상대오차 | 약 1.985331266985948×10⁻¹⁴ / 5.397341039383144×10⁻¹⁵ |
| exact-zero atoms | PASS, absolute zero 기준 유지 |

세 coefficient의 선언된 입력 envelope에서 양수 하한이 유지됐다. H/He 각각의 analytic target N/E와 원 Q8/projector 결과도 고정 기준을 통과했다. canonical A를 교체하거나 residual을 다른 표적에 재분배하지 않았으며 원 source normalization factor를 추가하지 않았다.

### 6.2 C07 실제 실패와 최소 복구

원 `controls_v1`은 **50/50 PASS**였다. 그러나 실제 `primary_v1`은 `HE_SELECTED_MARGINAL_DOMAIN_REFUSED`로 실패했다. stderr는 prefix의 closed-He fixture 경로를 가리키지만 실패 operand와 prefix 번호는 저장되지 않았다. 특정 prefix의 rounding 방향을 실측 사실처럼 보충하지 않는다. 정적 검토는 80-digit Decimal의 half 생성 및 `p+2*d` 비교가 각각 반올림될 수 있음을 확인했다. [C06][c6], [C07 실패 보존][c7-failure]

수리는 finite Decimal의 정확한 Fraction 표현을 이용해 d/prior_d/s를 만들고 domain을 정확한 유리수로 비교하는 변경에 한정했다. tolerance·global precision·fit·Q8는 바꾸지 않았다. 원 코드·실패·receipt를 보존하고, 실제 독립 review `1aa209251c0a459bde7b1dfbe4c347f37de74084c529382b1044b9516a6b8559`와 root의 budget-bound reuse admission `9417dd4f6713fff96587a6a8d9a0ee01aefd3774d270a68b367dfdc913d36652`로 기존 preparation의 재사용을 결속했다. `load_preparation()`의 3-value API는 유지했다. 준비 fit/projection 재실행은 **0**이다.

unique `controls_v2`는 affected old control 1개와 새 경계 control 1개만 실행해 **2/2 PASS**였다. 변경하지 않은 49개를 반복하지 않았다. 따라서 원 50개+새 1개=**51개 unique 검사**, 실제 평가는 원 50+targeted 2=**52회**다. unique `primary_v2`는 **58/58**, `PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN`으로 네 prefix와 네 disjoint observation bin을 생성했다. 실제 결과는 399,835 bytes, SHA **`efbd18ba864982ca6436345b1d25d75ad084b3c5f77db6e3bb40186db07b4901`**이다. [C07 실제 요약][c7]

### 6.3 유한 source 귀속과 partial 반환

마지막 prefix `[0,10¹⁰] s`의 model-identified 값은 다음과 같다. 밀도이며 절대 worldtube total은 아니다.

| 물리량 | H-parent 전자 | He-parent 전자 marginal |
|---|---:|---:|
| 누적 N [m⁻³] | 약 7.789388584793693×10⁻¹⁶ | 약 7.943146027889112×10⁻¹⁷ |
| 누적 kinetic E [eV m⁻³] | 약 3.072409890625962×10⁻¹⁵ | 약 3.419024347163867×10⁻¹⁶ |
| endpoint N rate [m⁻³ s⁻¹] | 약 1.557877716958739×10⁻²⁵ | 약 1.588629205577822×10⁻²⁶ |

authoritative canonical source는 N=8.583703187582433×10⁻¹⁶ m⁻³, E=3.414312325342331×10⁻¹⁵ eV m⁻³다. target 합과 canonical 값의 작은 잔차는 `split_residuals`로 남았으며 heat/thermal particle로 분류되지 않았다. endpoint는 제공된 history의 마지막 left limit이다. [C07 마지막 prefix][c7]

같은 prefix의 default-retention selected contribution은 Δζ≈4.610674853578180×10⁻¹⁸, Δw_nt≈2.480838299866415×10⁻³⁶ J/baryon이다. 이 값은 actual full nonthermal state나 미지 partner addendum이 아니다. H literal-convention residual≈4.434594726129009×10⁻¹⁸ eV m⁻³와 symbolic branch lift를 따로 보존한다. explicit retention EOS fixture의 ΔlogT≈2.687084754105897×10⁻¹⁶도 실제 physical temperature/heating 완료를 의미하지 않는다.

`event_terms`는 작은 RR capture·binding·photon 항과 원 binary64 hex를 보존한다. `retained_photon_reference`는 저장 atom descriptor를 가리키며 moment로 새 spectrum을 만들지 않는다. `native_affine_Y`는 actual s/p/d와 partner addendum을 null로 유지한다. `conditional_closed_He_family` 및 `conditional_caloric`는 표시된 fixture 조건에서만 읽는다. prefix끼리 합산하지 않으며 `adoption_registry`는 disjoint bins의 partial component와 이미 포함된 RR의 중복을 막는다.

### 6.4 C08 원 독립 비교의 네 실패와 실제 한정 수리

`runs/independent_v1/RESULT.json`은 1,651,412 bytes, SHA **`fedc2a34a857f5de7c8035db580bdc746319366914efa9094a36a71e6923f8c9`**이며 실제 상태는 **FAILED: 3446 PASS / 3450 evaluations / 4 FAIL**이다. production import 없이 별도 90-digit 원시함수와 raw-M solve, analytic target N/E를 사용했다. saved-event 232/232, null-gate 325/325, native-affine 528/528, caloric 112/112와 two-part caloric 64/64 등이 원 결과에서 통과했다. 이는 실패 4건을 지우거나 전체 검토 PASS로 바꾸는 근거가 아니다.

실패 ID는 `prefixes.0.fixture.2.s_m3`, `prefixes.2.fixture.2.s_m3`, `prefixes.3.fixture.2.s_m3`, `observation_bins.0.fixture.2.s_m3`다. 실제 primary의 s는 모두 0인데, 원 reference의 `d=N/2; s=N−2d` 순차 Decimal 연산은 expected −10⁻¹⁰⁷ 또는 +10⁻¹⁰⁶을 만들었다. 명시된 p=0, fraction=1/2 fixture에서 `s=N(1−2f)−p=0`은 exact identity다. 독립 정적 진단 `review/C08_REFERENCE_ORACLE_FAILURE_STATIC.json`은 이 oracle artifact와 실제 실패행을 결속했다. actual He branch가 0이라는 물리 판정이 아니다.

후속 `review/C08_REFERENCE_RECOVERY_STATIC.json`의 판정은 `PASS_SCOPED_EXACT_HALF_ORACLE_REPAIR`다. root의 실제 새 code/budget admission 아래 `independent_v2`가 원 independent `window_reference`의 저장 N을 사용해 네 identity만 Fraction으로 대조했고 **4/4 PASS**했다. 원 3446 PASS 행은 계산 없이 재사용했다. production·원 reference·tolerance·prepared/primary/source/RR는 바꾸지 않았다. 원 FAILED JSON·executed source·receipt·charge0.548229는 그대로 보존한다.

실제 targeted `runs/independent_v2/RESULT.json`은 7,477 bytes, SHA **`305bec080443a6a1e9c81c3a7e6d6a41c5d1f533a456eef1be08e62cfcc6c937`**, status `PASS_SCOPED_EXACT_HALF_RECOVERY`다. `ACCEPTED_REFERENCE.json`은 1,586,125 bytes, SHA **`661ba71d49c52e8b8f44964ab7031540953349cdfe51928e7fd4941e9647b5da`**, status `PASS_SCOPED_INDEPENDENT_REFERENCE_COMPOSITE`다. **accepted unique3450 = reused3446+new4**, 실제 evaluation3454에는 이전 실패4가 포함된다. 전체 reference를 다시 실행한 것이 아니다. 새 receipt SHA는 `c7ae85bd3906509244f79fd0f42543ffc29efc5df2f83fb624672f9c7e90ac26`, measured0.491872+tail0.05=charge0.541872다. C9 최종 판정은 이 numerical composite와 별도로 실제 심사 뒤 채택한다.

### 6.5 저장 값 그림과 결과 해석

`plot_saved_v1`은 새 fit나 source/RR 계산 없이 실제 primary JSON/NPZ에서 한 figure·세 panel을 생성했다. worker exit0, reservation 내 완료이며 root의 후속 `review/C08_PLOT_VISUAL_AUDIT.json`은 `PASS_SCOPED_SAVED_OUTPUT_VISUAL`이다. SHA는 `258a48b289919a5ddd30622fb88608bc8880852355a47bdd8ea76c751473bb18`이며 실제 image inspection, label 가독성, 별도 cutoff ghost, stored residual·고정 threshold와 조건부 caloric 표기를 기록했다. 원 `PLOT_RECEIPT.json`의 `PLOT_GENERATED_PENDING_VISUAL_AUDIT`는 생성 당시 값으로 보존한다. 그림 재생성이나 추가 science check는0이다. [실제 visual audit][visual]

SVG는 102,037 bytes/SHA `63b07a3b59f61d85d7ea6b93b59a5bbd7afcfb113ba300bc22d3ed9b7cef50b1`, PNG는 111,983 bytes/SHA `5199fe0e0336385a45b3993e0b99de12875088b562a0792fc8d1526dae343fef`, `PLOT_DATA.json`은 940 bytes/SHA `1dcc7c6fe666fce5332f08c351e56d4cb79812f6265736ae3bcb28cbdd482a18`다. 경로는 `runs/plot_saved_v1/`이며 raw JSON이 정량 근거다. 아직 Git에 게시되지 않은 raw/artifact의 URL을 만들지 않는다. canonical SOURCE에 실제 수록한 뒤 manifest로 공개 경로와 archive-only를 구별한다.

선행 PR110의 46 accepted controls, 112 primary flags, 517 independent comparisons는 이번 검사 수에 더하지 않는다. 그 결과는 저장 RR 응답의 identity/scope를 재사용하는 근거다. 이번 numerical composite의 통과와 source·He joint branch·full physical consumer의 미식별성도 서로 다른 상태로 유지한다.

## 7. C4 실제 입장, 실패와 별도 예산

C4의 실제 판정은 `ADMITTED_FOR_FIVE_BOUNDED_CURRENT_UNIT_WORKERS`다. admission JSON SHA는 **`91bd59beaeb559c288dd231e03f9760c43aabf66ff461408234e55993607eedc`**이며 frozen budget SHA는 **`79e7befb18d6c988dbf776a72c0d0d3448c29302088c7d0f93ec4c5a6b5f95f3`**다. 이것은 이후 worker 결과의 성공 선언이 아니다. [C4 실제 admission][c4]

| C4 preparation attempt | 실제 상태 | measured CPU-s | tail | charge |
|---|---|---:|---:|---:|
| c4_v1 | raw memory gate 거절 | 0.139732 | 0.05 | 0.189732 |
| c4_v2 | memory PASS 뒤 live-PID 관측 실패 | 0.138373 | 0.05 | 0.188373 |
| c4_pid_diagnostic_v1 | default namespace의 `/proc/2/stat` 부재, child 전 실패 | 0.150783 | 0.05 | 0.200783 |
| c4_pid_diagnostic_v2 | 일치하는 승인된 실행 context에서 PID/parent/group/session/start·cleanup 확인 | 0.101814 | 0.05 | 0.151814 |
| c4_v3 | namespace guard·실제 PID probe·메모리 admission 완료 | 0.147815 | 0.05 | 0.197815 |
| **C4 subtotal** | 앞선 실패 포함 | **0.678517** | **0.25** | **0.928517** |

표는 표시용 소수 자릿수이며 원 JSON의 binary64 표현을 덮어쓰지 않는다. C4 subtotal은 최종 단위 비용이 아니다. v2의 nested `NOT_RUN`은 stale initialization으로 보존되며 probe가 전혀 시작되지 않았다는 증거로 쓰지 않는다. 실제 진단은 default executor의 PID와 visible procfs namespace가 일치하지 않았음을 보여 주었다. v3는 숫자 PID를 추측·번역하지 않고 자기 PID 일치 guard를 둔다. 관련 없는 process를 찾아 종료하는 복구를 하지 않는다.

새 memory policy `CAPPED_CLEAN_FILE_LRU25_V2`는 현재 단위에서 별도로 검토됐다. 과거 50% file-LRU credit을 자동 이월하지 않았다. eligible estimate는 `min(file,active_file+inactive_file)`에서 shmem/mapped/dirty/writeback/unevictable을 빼고 음수면 0으로 둔다. 그 1/4만, 최대 1 GiB를 고려하며 memory.min/low 보호가 있으면 credit은 0이다. raw headroom 자체도 selected worker 256 MiB 이상이어야 한다.

v3의 실제 raw headroom은 **277,471,232 bytes**, credit은 **1,073,741,824 bytes**, host-capped available estimate는 **1,351,213,056 bytes**였다. 필요한 worker256MiB+reserve1GiB는 **1,342,177,280 bytes**다. 이는 비원자적 counter snapshot에 근거한 입장 추정이며 lower-bound certificate나 메모리 보장이 아니다. OS memory 설정·cache pressure를 조작하지 않았고, worker selected256MiB/upper512MiB, native thread1을 유지한다.

새 단위 cap은 **40 CPU-s**다. 최초 C4 계획은 preparation reserve4, worker3/3/4/6/6, 각 coordinator+tail2.05(그중 tail0.05), 합계36.25와 미배정 contingency3.75였다. 이 최초 계획과 C07의 unique 복구 allocation을 구별하며, 실제 활성 예산은 원본을 보존한 뒤 root가 새 code/reuse pin과 함께 고정했다. 재실행을 위해 이전 charge를 초기화하거나 preparation을 다시 실행하지 않았다.

| actual attempt | 상태 | worker CPU-s | coordinator measured | tail | charge |
|---|---|---:|---:|---:|---:|
| prepare_v1 | completed, 15/15 | 0.347402 | 0.178066 | 0.05 | 0.575468 |
| controls_v1 | completed, 50/50 | 0.848750 | 0.281809 | 0.05 | 1.180559 |
| primary_v1 | **failed**, He boundary | 0.154997 | 0.142928 | 0.05 | **0.347925** |
| controls_v2 | completed, targeted2/2 | 0.117692 | 0.115636 | 0.05 | 0.283328 |
| primary_v2 | completed, 58/58 | 0.205492 | 0.116558 | 0.05 | 0.372050 |
| independent_v1 | **failed**, 4 oracle rows | 0.317903 | 0.180326 | 0.05 | **0.548229** |
| plot_saved_v1 | completed, saved-only | 4.950508 | 0.675384 | 0.05 | 5.675892 |
| independent_v2 | completed, targeted4/4 | 0.306077 | 0.185795 | 0.05 | 0.541872 |

과학 실행 완료 시점의 `evidence/EXECUTION_LEDGER.json` SHA는 `7b65b5cd4375277392a9fc3ebdf466e8a02870230600875b9e8d25ea4897dff4`다. C4 preparation measured0.6785169999999999, worker7.2488209999999995, coordinator1.876502을 포함한 **measured9.80384**, conservative tails **0.65**, **charge10.45384/40**을 기록한다. 미사용 **29.54616은 nontransferable**이며 global budget remaining은 null이다. targeted 전 중간값9.911968도 시간 순서상 보존한다. 표는 표시용 반올림이며 원 ledger/receipt의 저장 수치를 대체하지 않는다. 최종 closeout의 actual 비용 증거 pin은 마지막 표에서 추가한다.

실패를 포함한 preparation·worker·coordinator·conservative tail을 유지하며 **all_runtime_attempts_pass=false**다. cumulative amendment는 같은 attempt의 최대 누적 debit을 한 번만 합산한다. no-ACK reservation을 비용0으로 리셋하지 않는다. preventive hard aggregate CPU proof는 false다. 출력 성공과 resource accounting의 완료를 구별하고, 새 오류가 생기면 같은40CPU 안에서 별도 입장·비용·판정으로 남긴다.

## 8. 외부 owner의 관측과 중앙 수

root가 R07에서 채택한 중앙 기준은 `b99a9468abd53de77ddae36d93180e60072885bc`다. 실제 DAG SHA `ab873fd7f5b7d55c3b6fe650323447a23a4fec820fbe8dc29110908501636ccb`와 authoritative owner-return을 대조해 **28/88**, 88 nodes/17 integration edges, CR0을 유지했다. 역사적27→28은 foreign B3h의 기존 완료 기여다. PR236의32/88 또는 REI working33을 더하지 않는다. [R07 실제 baseline adoption][central]

아래는 **C03의 고정 관측 2026-10-27 16:49:07 UTC**를 후속 packet으로 정리한 결과이며 실시간 최신 HEAD 주장이나 새 조사 결과가 아니다. 원문은 `intake/providers/FINAL_OWNER_DELTA_PRE_C9.json`(SHA `1950c17f8c63d37d49c355f0257ac6542d52da4eee98ea211bbadaa4889a1b37`) 및 대응 `_KO.md`다. 이 packet의 numerical C9 판정을 대신하는 효력은 없다.

| Owner | exact observed revision | 이번 CR에 가져오지 않는 항 |
|---|---|---|
| WU R8 | `b3ba2e4aff1f237a2835b2f3a1b07de81133e9f7` | local17/32·workflow20/20, 실제 source 접근과 조건부 lag-kernel은 He joint branch·실제 rate/Q·state/domain·deposition·consumer activation이 아님 |
| REC native path | `a21a99cd676671421ff4437f926834ec5e65af07` | theory10/10과 C1–C3 receipt는 별도 native cosmology 계약. 실제 새 capture/physical bound를 CR100K/nb/clock에 이식하지 않음 |
| HE KINEMATIC08 | `e56573a5961623c49428f6f8d566fb13edf8a6b9` | bare-alpha γ+α→d+d의 조건부 기하/운동학은 원자 He 부모 branch·photon flux/history/deposition을 주지 않음 |
| BASS endpoint | `0f3fb1802d8edcc60a74312f791ba6e98752c5a9` | native knot5126/5127, V0/temperature convention·예산을 CR에 가져오지 않음 |
| BASS KM2B | `af1adc28488c3f11b5ac65672430b0f697508a95` | fixed-beta Thomson finite-history 모델의 once-only clock/initial-memory 원리를 물리 source·nb·spectrum 자료로 바꾸지 않음 |
| REI causal consumer | `da525e474a1fb583931897e82808c92101f963c3` | atomic-storage 표현과 full native25/EOS/nb의 actual null을 구별; cap47 BUDGET_STOP·누적≥48.263016494와 미승인60/8 제안 보존 |

WU의 원 reference726/727+1FAIL와 exact-scalar24/24 복구, scientific4.320964와 별도 plot30.609091666 비용을 합쳐 성공 이력으로 바꾸지 않는다. REC의600CPU 계획·UNKNOWN_NOT_ZERO, HE의 validation14/14 및 최초 환경 실패와 plot7.040661/6FAIL, BASS endpoint의 pre-driver failure/닫힌 예산, KM2B의 provider별 다른 readback tier를 원 owner 기록대로 보존한다. 이 CR 조사에서 foreign ZIP full GET를 추가로 했다고 쓰지 않는다. REC programme `4a8e541030ee2cbd02e26ba671083b705d309d49` 및 HE APERTURE07 `5c71a19e303642e1df11ff0fe6da1460113479a4`와 별도 work branch 관측을 함께 구별한다.

## 9. 선행 단위와 보존할 실패

직접 재사용한 PR110은 S=`2eed7ef835c55ee17e4ce96e0eda7fe8d82dc47c`, D=`616b166fa0108ca35defece3f8c9d99fc79895cb`, M=`42cc3a909688d670200ba09c500e2ca83a94fa10`이다. source ZIP은 **5,421,103 bytes**, SHA `5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58`, 415 members이며 closeout은 **2,420,589 bytes**, SHA `1ef6dcb0abfcc994fd05bbad77b92bb152182e532a2ccc75e48c3024ff8bc2a8`, 186 members다. 둘의 actual dual full-GET R3를 선행 provenance로 재사용한다. 이 초안에서 다시 다운로드하거나 재포장하지 않았다. [PR110 최종 게시][pr110]

PR110 charge24.692011/40=순수측정14.616973+tails10.075038, 이전 C4 refusal, controls_v1 45/46 실패와 한정 oracle 교정의 1-control v2, plot_v1 reservation failure와 unique v2, monitor 한계 및 C06 tree `UNKNOWN_NO_ACK`를 보존한다. PR109의10.238419/20와 independent_v1 preworker failure·plot reservation failure, PR107의6.988054525/30와 C9 v1 preworker 실패·owned stale lease·unique v2 복구도 그대로다. 어느 잔여도 새40CPU에 이월하지 않는다. 과거 H1/HeI/C23E/source science replay는0이며, 완료된 이전 test 수를 새 test 수에 합산하지 않는다.

현재 단위의 sparse-checkout 복구 원천은 **봉인된 PR110 canonical SOURCE ZIP의 payload**다. Git switch 뒤 누락된 파일을 D의 ls-tree로 확인했으나 `git cat-file`의 promisor lazy-fetch는 네트워크 실패로 완료되지 않았다. 이후 ZIP 전체 SHA와 member별 bytes/SHA를 대조해 **missing-only 347개**를 복구했고 기존 파일 overwrite는0이었다. 따라서 이를 “exact D blob에서 복구”라고 쓰지 않는다. `intake/ENTRY_SPARSE_REHYDRATION.json` SHA `38f53d848c123c9cc11c527d85f19412d4dd3d39b1b19b0eb90cf7e74c3f99f9`에 이 chronology와 metadataCPU=null, old-science replay0, 새 remote archive R3 주장false가 남아 있다.

R06 입력 오류, R6 read-only Git diff의 promisor/proxy 실패와 보존 원문 비교, R07 잘못된 status 경로404 및 고유 V2 읽기, C4 metadata diff 실패도 보존한다. C07의 실제 numerical consumer 실패와 C08의 reference oracle 실패는 각각 원 run·review·비용에 남긴다. 최신 성공으로 과거 실패를 덮어쓰지 않는다.

## 10. 게시·백업·종료 상태를 확정할 자리

C04 stage ZIP `BASS_CR_PARENT_EVENT_C04_20261028_c5bb50f76215.zip`은 **1,491,185 bytes**, SHA `7a80335d09577f1265ab22fd2830c989a791cbe1fd0ee3c7655dff05538fde6b`,153 members/152 payloads다. Dropbox `id:BSpOijBcT10AAAAAAEDIeQ`와 Drive `1uFRrDZMZ_SADS1PvrT8VjDq3mTe0Aryx`의 실제 ACK/size R2를 확인한 기록이다. `raw_archive_readback=false`이므로 이 ordinary stage를 R3라고 쓰지 않는다. C04 postcommit receipt SHA는 `aa1718b5b29006b166b0fde207019760eb935f0bd63286b9a8a60746ccc86a56`다.

그 뒤 실제 게시된 C05=`7f170fb8fb0709bd95bd930ad9ff5072920650b0`, C06=`d72f474bbc761403cbac0424128043f5b5c5ca49`, C07=`d97d3620efdd7b46cf479004cfd2e27444f7ebea`는 각각15/20,16/20,17/20이다. C08=`d84de9418a135b093a589af8dfc35d8d40c0d821`까지 **18/20**의 expected-parent/non-force ref readback과 Dropbox/Drive ACK·size R2가 실제 존재한다. C07 stage ZIP은 4,425,354 bytes,269members/268payloads,SHA `d2008a9dd2b43109c37042300043dc2b016ab663942ae383ee513e4ba4b93606`, Dropbox `id:BSpOijBcT10AAAAAAEDIfA`, Drive `1Uh0BQ3ZtURnmf8C5bK8uqTeW7HHqAmJk`다.

C08 stage ZIP `BASS_CR_PARENT_EVENT_C08_20261028_d84de9418a13.zip`은 **5,314,113 bytes**,329members/328payloads,SHA `bb0d7f337cade883fe98dc69e3639d353c1e295ffd93150aae581394377ffeff`, Dropbox `id:BSpOijBcT10AAAAAAEDIfQ`, Drive `1aQPYW5qxsHI8ZHyJq6ZgaVSkFT3_pBs4`다. ordinary stage R2이며 원본 full GET R3는 아니다. 모든 단계의 중앙 표시는28/88이고 CR effect0이다. root가 보고한 C09 fresh preflight PASS는 C9 판정·게시를 대신하지 않는다.

최종 S는 실제 C09 과학 게시, D는 그 뒤 문서 게시, M은 실제 expected-SHA/non-force 중앙 owner-return 게시로 각각 확정한다. SOURCE는 실제 S snapshot에 한 번 봉인하고 이후 D/M·Library·R3 receipt 때문에 다시 만들지 않는다. CLOSEOUT은 별도 archive이며 자신의 미래 hash/IDs/R3를 내부에 미리 채우지 않는다. Git-published와 archive-only payload를 구분하고 실제 공개 경로에만 selective Git raw R3를 적용한다. provider R3는 실제 양 원본 full GET와 모든 member bytes/SHA/CRC를 확인한 후에만 기록한다.

| 최종 항목 | 값 |
|---|---|
| C08 targeted reference 및 composite | 실제4/4와3450 unique PASS; final C9 adoption pin은 PENDING, 원3446/3450·4FAIL 보존 |
| root visual-audit 후속 receipt pin | 실제 PASS, SHA258a48b2…; 생성 당시 PENDING 원문 보존 |
| C9 실제 판정·scope·blockers | PENDING |
| R1–R10/C1–C10 실제 게시·dual R2 | PENDING — 현재 확인18/20과 구별 |
| 새 scoped child 완료/전체 | PENDING |
| S / D / M | null / null / null |
| canonical SOURCE name·bytes·SHA·members·provider IDs·Library ID·R3 | null |
| final CLOSEOUT name·bytes·SHA·members·provider IDs·Library ID·R3 | null |
| 실제 중앙 owner-return URL·central post-readback | null |
| 최종 current-unit 비용 closeout pin | PENDING — 실제 과학 장부 charge10.45384/measured9.80384/tail0.65, nontransferable29.54616 |

R1–R10 이론 완료나 C4 admission을 full numerical·physical 완료로 바꾸지 않는다. N4/N5는 **PARTIAL_OPEN**, N6/N7은 **PREDECESSOR_GATED**, L4는 **false**다. 실제 s/p/d, partner state/energy/history/response, excitation, donor debit, full physical native25, actual temperature point, absolute worldtube totals 및 global physical completion/error/budget remaining/currency는 필요한 실제 입력이 없는 동안 **null**이다.

현재 단위의 남은 실행·검토·게시·백업·중앙 인계까지만 마친다. 기존에 승인된 additive publication, backup 및 이 단위의 bounded 실행 권한은 유지하되 **다음 연구 단위의 자동 개시·실행은 false**다. 개인 대화 전체 검색 unavailable 및 Drive partial inventory 한계도 보존한다.

[contract]: https://github.com/cosmosapjw-quantum/bass_cr/blob/fbc039ff5c357571cbbf2ff61d96fde8b3ce8594/research/cr_parent_event_native25_20261028/CONTRACT.json
[theory]: https://github.com/cosmosapjw-quantum/bass_cr/blob/4a1bb9bc67b3168e7c187e7d64fa13e0f61aebb2/research/cr_parent_event_native25_20261028/THEORY_KO.md
[r6]: https://github.com/cosmosapjw-quantum/bass_cr/blob/4a1bb9bc67b3168e7c187e7d64fa13e0f61aebb2/research/cr_parent_event_native25_20261028/review/R6_INDEPENDENT_KO.md
[symbolic]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d5963e8e431cd8b37471913fa9cb57e32b2a9b2d/research/cr_parent_event_native25_20261028/symbolic/RESULT_V1.json
[computational]: https://github.com/cosmosapjw-quantum/bass_cr/blob/72eaddeac1d41f45c32e712b885666536227db64/research/cr_parent_event_native25_20261028/COMPUTATIONAL_CONTRACT.json
[lineage]: https://github.com/cosmosapjw-quantum/bass_cr/blob/fbc039ff5c357571cbbf2ff61d96fde8b3ce8594/research/cr_parent_event_native25_20261028/inputs/SOURCE_LINEAGE_MANIFEST.json
[literature]: https://github.com/cosmosapjw-quantum/bass_cr/blob/fbc039ff5c357571cbbf2ff61d96fde8b3ce8594/research/cr_parent_event_native25_20261028/literature/LITERATURE_MAP_KO.md
[c4]: https://github.com/cosmosapjw-quantum/bass_cr/blob/c5bb50f76215d6b2f4e7b618c225ec108a41174f/research/cr_parent_event_native25_20261028/coding/C04_ACTUAL_ADMISSION.json
[c5]: https://github.com/cosmosapjw-quantum/bass_cr/blob/7f170fb8fb0709bd95bd930ad9ff5072920650b0/research/cr_parent_event_native25_20261028/coding/C05_ACTUAL_PREPARATION.json
[c6]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d72f474bbc761403cbac0424128043f5b5c5ca49/research/cr_parent_event_native25_20261028/coding/C06_ACTUAL_CONTROLS.json
[c7]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d97d3620efdd7b46cf479004cfd2e27444f7ebea/research/cr_parent_event_native25_20261028/coding/C07_ACTUAL_PRIMARY.json
[c7-failure]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d97d3620efdd7b46cf479004cfd2e27444f7ebea/research/cr_parent_event_native25_20261028/coding/C07_FAILURE_PRESERVATION.json
[c8]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d84de9418a135b093a589af8dfc35d8d40c0d821/research/cr_parent_event_native25_20261028/coding/C08_ACTUAL_REFERENCE_AND_PLOT.json
[visual]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d84de9418a135b093a589af8dfc35d8d40c0d821/research/cr_parent_event_native25_20261028/review/C08_PLOT_VISUAL_AUDIT.json
[central]: https://github.com/cosmosapjw-quantum/bass_cr/blob/d5963e8e431cd8b37471913fa9cb57e32b2a9b2d/research/cr_parent_event_native25_20261028/intake/central/R07_BASELINE_ADOPTION.json
[native-model]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/d91de6299e614520949c5873a9378000ceb1f85c/research/rei_expanded_event_consumer/cr_integrated_return_20261027/vendor/native_identity/atomic_model.json
[native-coeff]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/d91de6299e614520949c5873a9378000ceb1f85c/research/rei_expanded_event_consumer/cr_integrated_return_20261027/vendor/native_identity/atomic_coefficients.json
[storage-consumer]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/835707bb00ef8f778f24f667f102a412ae8ce0ca/research/rei_expanded_event_consumer/bass_atomic_storage_consumer_20261027/implementation/atomic_storage.py
[rudd]: https://doi.org/10.1103/RevModPhys.64.441
[criptic]: https://arxiv.org/pdf/2207.13838
[pr110]: https://github.com/cosmosapjw-quantum/bass_cr/pull/110
