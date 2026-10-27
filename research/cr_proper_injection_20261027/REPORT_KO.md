# 실제 proper-time injection/return contract — 저장 결과 보고

- 단위: **CR_PROPER_INJECTION_RETURN_V1**
- 경로: `research/cr_proper_injection_20261027`
- 작성 기준: 2026-10-27의 R1–R10 인계, C6 actual/control 결과, C8 독립 결과와 최종 비용 ledger.
- 상태: **C9 독립 검토 및 root의 scoped 과학 채택 완료**. 판정은 `PASS_SCOPED_CORE_NUMERICAL_AND_CONTRACT_WITH_PRESERVED_RUNTIME_FAILURES`이며 core blocking finding은 0개다. 모든 runtime attempt의 PASS를 뜻하지 않는다. 최종 source 백업·C10 문서·중앙 게시 identity는 후속 실제 receipt로 결속한다.

## 1. 이번 단위가 구성한 것

저장된 PHYS02 전자 source를 실제 source revision, 물리 상태, native energy support, frame, proper clock/volume 정의와 결속하고, 알려진 유한 시간 구간의 입자수·운동에너지 밀도를 계산했다. 일반 photon/electron/baryon 입력 계약과 조건부 RR/native25/retained-photon 연결은 구현했지만, 이번 **실제 입력은 PHYS02 electron source**다. Photon·baryon 입력과 호환 RR의 검사는 synthetic control이다.

저장된 변경 검사는 **103/103**, 실제 출력은 **18행**, 독립 Decimal80 검사는 **153/153 PASS_SCOPED**다. 실제 source에는 같은 donor/recipient 상태의 명시적 $n_b$가 없고, 기존 PR107 RR bath와 온도·target state가 맞지 않는다. 두 scalar gas-rest frame 자체의 불일치를 주장하지는 않으며, 실제 연결에는 명시적 frame 결속도 필요하다. C7의 frame mismatch는 `prescribed_gas_rest_frame_scalar`와 `bath_frame_rest_target`라는 기록 ID의 엄격한 동등성 gate를 뜻하며, 실제 상대속도나 boost가 확인되었다는 뜻은 아니다. 따라서 actual `nb`, `native25`, `rr_return`, `retained_photon_port`는 모두 `null`이다. 이는 필요한 입력이 없다는 판정이며, 미래의 명시적 transport/state 연결을 배제하는 no-go 주장이 아니다. [C6 요약](evidence/C06_RUN_SUMMARY.json), [actual 결과](runs/actual_v1/RESULT.json), [독립 결과](runs/independent_v2/RESULT.json), [물리 일관성 검토](evidence/C07_PHYSICAL_CONSISTENCY.md).

## 2. 실제 source의 identity와 적용 범위

재사용한 source snapshot의 retained revision은 `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`이며, 이 pin을 최초 생성 commit으로 주장하지 않는다. Retained lineage 조회 revision은 기존 D인 `ec463db0c7e5c7fb5070796071c926caa4db6445`다. 사용한 `SPECTRUM_fullBED_9600.npz`는 **217754 bytes**, SHA256은 `7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc`다. `energy_eV`는 9600개이며 `source_vectors`는 $9611\times2$다. 별도 legacy NPZ도 같은 energy/source 배열을 가지므로 fullBED와 legacy를 독립 주입원으로 합산하지 않는다. [source qualification](intake/SOURCE_QUALIFICATION.json).

| 항목 | 실제 채택 범위 |
|---|---|
| Source model | prescribed-gas leading-local PHYS02, $Q_e(W,\tau)=\tau A(W)$ |
| Bath | $T_{\rm gas}=100\,{\rm K}$, $n_H=140\,{\rm m}^{-3}$, He 질량분율 0.248, HII/HeII fraction 0.01, HeIII fraction 0 |
| Isotope | 원자료는 elemental H/He; **조건부 H→H1, He→He4**를 명시 |
| Frame | prescribed gas rest frame, angle-integrated scalar source |
| Native source support | proton source normalization 10 keV–1 PeV; 실제 사용 collision 1–4 MeV; electron births 0.1–900 eV |
| Birth partitions | `direct_0p1_10`, `direct_10_900`; split 10 eV |
| Clock/history | proper seconds, $0\le\tau\le T_{\rm end}=10^{10}\,{\rm s}$ |
| Volume | 고정 proper volume의 밀도 정의; 실제 cell volume 값은 미공급 |
| 없는 입력 | 명시적 same-state $n_b$, 기록 밖 history, 실제 photon 공급, bath 간 transfer 계약 |

이는 관측된 cosmological history가 아니라 이미 실행·저장된 prescribed-source 모델이다. 기록 끝 이후의 지속이나 영점 shutoff는 주어지지 않았으므로 둘 다 추정하지 않는다. Surface flux를 geometry 없이 volume source로 바꾸거나, 서로 다른 frame을 scalar 계수만으로 변환하거나, D/T/He3/Li로 isotope 범위를 넓히지 않는다. [계약](CONTRACT.md), [가정과 gate](CLAIMS_AND_ASSUMPTIONS.md).

## 3. 변환·적분·반환의 수학적 계약

같은 물리 worldtube와 frame의 native number measure를
$$
dN=q^{\rm nat}(t_n,\xi)\,dt_n\,dV_n\,d\xi
$$
로 쓰면 proper injection은
$$
j(E,\tau)=q^{\rm nat}(t_n(\tau),\xi(E))
\left|\frac{dt_n}{d\tau}\right|
\frac{dV_n}{dV_p}
\left|\frac{d\xi}{dE}\right|
$$
다. 각 인자는 한 번만 적용한다. 실제 PHYS02 source에는 $z=8$의 comoving→proper 계수 729, angle integration, neutral target density가 이미 포함되어 있다. 이들을 다시 곱하지 않았으며, 실제 adapter의 clock·volume Jacobian은 각각 1이다.

일반 구현은 고정 proper volume, 양의 상수 Jacobian, segment별 degree 0–2의 비음수 다항식 coefficient로 한정된다. Native elapsed clock의 coefficient $c_k$는
$$
c_k^{\rm proper}=c_k\,J_t^{\,k+1}J_V\,F_{\rm target}
$$
로 옮긴다. 한 $J_t$는 rate measure, 나머지는 다항식 argument에서 온다. 이미 proper seconds인 segment endpoint에는 이를 다시 적용하지 않는다. Unknown time gap이나 기록 밖 query는 거절하며, gap의 영점이 명시된 경우만 zero-gap 적분을 허용한다. History가 없는 입력의 rate/exposure/유한 적분량은 null로 두고, moment-only 입력에는 spectrum을 만들지 않는다. [유도](THEORY_KO.md), [계산·오차 정책](evidence/C03_ALGORITHM_AND_ERROR.md).

### 저장 배열의 의미와 공통 scale

Active $B_i$는 **energy coordinate**다. Number를 얻으려면 원래 저장된 양의 $E_i$로 나누어야 한다. 모든 birth tag에 동일한
$$
U_*=1.1242596728743301\times10^{-13}\ {\rm eV\,m^{-3}},
\qquad
S=\frac{U_*}{T_{\rm end}^2}
$$
를 사용하여
$$
A_{N,i}=S\frac{B_i}{E_i},\qquad A_{E,i}=SB_i
$$
로 정의했다. Low/high 각각을 다시 정규화하지 않았다.

0.1 eV cutoff의 energy/number는 9605/9608행으로 별도 포함한다. 9609/9610의 `low_cross`는 이미 투영된 입자의 중복 진단량이므로 source 합에서 제외한다. 실제 active grid는 약 0.10309375 eV에서 시작하며, 0.1 eV atom은 원 construction의 별도 boundary다. Low/high의 projected atoms가 10 eV node를 공유해도 native birth partition은 유지한다. 원 spectrum이나 time history를 moments에서 복원하지 않았다. Dense source record `runs/actual_v1/ACTUAL_SOURCE_RECORDS.json`은 archive 전용 payload로 canonical SOURCE ZIP에 수록하며, 경로·크기·hash는 C6 receipt에 기록했다. 최종 ZIP identity와 제공 receipt는 게시 절에서 확정한다. [표현 선택](REPRESENTATION_SELECTION.md), [source record receipt](evidence/C06_RUN_SUMMARY.json).

Known history 안의 $[a,b]$에 대해
$$
M[a,b]=\frac{(b-a)(b+a)}{2},
$$
$$
N[a,b]=SM[a,b]\left(\sum_i\frac{B_i}{E_i}+B_{N,\rm cut}\right),
\quad
U_{\rm eV}[a,b]=SM[a,b]\left(\sum_iB_i+B_{E,\rm cut}\right).
$$
$U_J=(1.602176634\times10^{-19})U_{\rm eV}$로 SI 변환한다. Factored difference는 짧은 window에서 큰 제곱수 두 개를 직접 빼는 것을 피한다. 여기서 $N,U$는 proper-volume **밀도 적분량**이다. 실제 volume 값이 없으므로 worldtube total count/energy는 `null`이다.

### Same-state $n_b$, RR horizon, photon ownership

Per-baryon/native25 연결에는 명시적이고 양수인 $n_b$, 동일 donor/recipient state, frame이 필요하다. 실제 baryon 유입이면 분모도 변하므로
$$
\Delta Y_i=
\frac{\Delta n_i-Y_i\Delta n_b}{n_b+\Delta n_b}
$$
를 사용한다. 단순 $\Delta n_i/n_b$는 baryon-conserving event 또는 별도로 명시한 reference normalization에만 해당한다. PR236/PW19의 $T$나 $n_b$를 현재 bath에 가져오지 않았다.

또한 유한 source history는 유한 RR return을 자동으로 주지 않는다. $K=-Q$, proper reward $r$에 대해
$$
f_h=\int_0^h e^{-Ka}r\,da,\qquad
C(T)=\int_0^Tj(s)^Tf_{T-s}\,ds
$$
와 eventual response $f_\infty=K^{-1}r$는 구분해야 한다. Conditional mean time을 exposure로 대입하지 않는다.

호환되는 He4III→He4II(1s) spontaneous ground, scalar, zero-recoil event에서는
$$
\Delta u_{\rm fast}=-E,\quad
\Delta u_{\rm binding}=-I,\quad
\Delta u_\gamma=E+I,\qquad I=54.42\ {\rm eV}.
$$
Retained photon은 별도 count/energy port이며 RR의 `w_ext=0`과 구분된다. 이 분할이나 frozen $\Delta\log T=0$을 physical heating 완료로 해석하지 않는다. 기존 photon support $\le50000$ eV 등 RR의 범위도 유지한다.

같은 event family의 overlapping native birth support **및** time window를 이중 claim할 수 없다. FullBED/legacy, selected-total/부분 tag, whole/split window, producer revision이나 finite/eventual label만 바꾼 중복은 injection·return registry에서 차단한다. RR 성공 경로는 approved He4 mapping, target isotope, final 1s state, spontaneous component와 scalar scope까지 검사한다. [구현](implementation/ports.py), [controls](runs/controls_v1/RESULT.json).

## 4. 실제 수치 결과와 독립 확인

세 tags에 다음 여섯 window를 적용하여 18행을 만들었다:
$[0,T]$, $[0,T/2]$, $[T/2,T]$, $[T/3,2T/3]$, $[T(1-10^{-6}),T]$, $[T,T]$.
Zero-width window의 적분은 정확히 0이고, 주어진 history의 left-limit endpoint rate는 별도 quantity로 유지한다.

아래는 [actual JSON](runs/actual_v1/RESULT.json)의 $[0,10^{10}\,{\rm s}]$ 저장값이다.

| Native birth tag | $N\,[{\rm m^{-3}}]$ | $U_J\,[{\rm J\,m^{-3}}]$ |
|---|---:|---:|
| 0.1–10 eV | $8.583703187582433\times10^{-16}$ | $5.470331428841687\times10^{-34}$ |
| 10–900 eV | $8.304211765519875\times10^{-16}$ | $8.459279749254506\times10^{-33}$ |
| Selected total | $1.6887914953102309\times10^{-15}$ | $9.006312892138676\times10^{-33}$ |

Selected total의 $T$에서 알려진 left-limit source rates는 $3.377582990620462\times10^{-25}\ {\rm m^{-3}s^{-1}}$, $1.801262578427735\times10^{-42}\ {\rm J\,m^{-3}s^{-1}}$다. 이 값들은 기록된 proper-volume injection rates이며 per-baryon rate, RR rate 또는 RR exposure가 아니다. Actual JSON SHA256은 `b1d6aed9f4db7ff5c968787c4291f2fd643b990b5263f527dda629fd16699bd6`다.

독립 reference는 원 NPZ의 represented binary64 값을 Decimal80으로 읽고 production module을 import하지 않은 채 source moments와 유한 적분을 확인했다. 아래 최대오차는 저장된 `check_groups`를 표시용으로 줄인 값이다. Exact-zero에는 임의의 absolute unit floor를 두지 않았다. [독립 결과](runs/independent_v2/RESULT.json).

| 검사항목 | PASS/전체 | 고정 relative 허용치 | 저장 maximum relative error |
|---|---:|---:|---:|
| 기존 저장 source moments | 6/6 | $2\times10^{-12}$ | $1.168955\times10^{-15}$ |
| 18행의 독립 5 fields | 90/90 | $2\times10^{-13}$ | $2.383239\times10^{-16}$ |
| Half-window 적분 가법성 | 9/9 | $2\times10^{-14}$ | $1.172623\times10^{-16}$ |
| Source-tag 가법성 | 30/30 | $2\times10^{-14}$ | $1.789262\times10^{-16}$ |
| eV/J energy-unit 연결 | 18/18 | $2\times10^{-14}$ | $1.313214\times10^{-16}$ |
| **전체** | **153/153** | 그룹별 원 허용치 유지 | **PASS_SCOPED** |

Decimal 정밀도는 원 source 모델이나 기존 quadrature/projection의 물리적 정확도를 높였다는 뜻이 아니다. 이번 검사는 저장 source와 새 adapter의 산술·ownership·단위·유한 history 일관성을 확인한다. Global physical error는 계속 `null`이다.

PNG `runs/plot_v1/INJECTION_WINDOWS.png`와 [SVG](runs/plot_v1/INJECTION_WINDOWS.svg)는 이 actual/reference JSON만 읽어 생성했다. PNG는 archive 전용 payload로 canonical SOURCE ZIP에 수록하며 최종 ZIP identity는 게시 절에서 확정한다. Count/energy 두 panel은 비교용이며 raw JSON이 수치상의 기준이다. 그림 파일은 생성·hash 확인되었지만 아래의 **plot runtime reservation 실패**도 함께 보존한다. [그림 manifest](runs/plot_v1/INJECTION_WINDOWS_MANIFEST.json).

## 5. 검토·실패 이력과 분리된 예산

이번 새 local cap은 **20 CPU seconds**다. 과거 HeIII의 **6.988054525/30**, 병렬 PR108 또는 다른 프로젝트의 잔여를 이월하지 않았다. 모든 invocation의 child/coordinator 측정치와 receipt-tail reserve를 보존하며, 같은 attempt의 정상 receipt와 amendment는 가장 큰 누적 debit을 한 번만 집계한다. [budget](EXECUTION_BUDGET.json), [최종 ledger](evidence/EXECUTION_LEDGER.json).

| Attempt | 저장 결과와 runtime 판정 | Charged CPU s |
|---|---|---:|
| `controls_v1` | 103/103, completed | 0.219374 |
| `actual_v1` | 18행, completed | 6.526079 |
| `independent_v1` | **preworker resource refusal**, 과학 worker 미시작 | 0.066297 |
| `independent_v2` | 153/153, completed | 0.355319 |
| `plot_v1` | 파일 생성, worker exit 0, **reservation FAILED** | 3.071350 |
| **전체** | **측정 CPU 10.190599 s; charged 10.238419/20 s** | **10.238419** |

`independent_v1`은 실행 당시 memory estimate가 원 worker+reserve 요구량보다 작아 outdir/worker 생성 전에 거절되었다. 측정된 child/startup overhead도 0으로 바꾸지 않고 포함했다. 이후 frozen 512 MiB 상한 안에서 per-attempt 256 MiB로 더 엄격한 `RLIMIT_AS`를 선택하도록 보완했고, 1 GiB reserve·memory 공식·host receipt pin·CPU cap은 유지했다. 원 runner와 실패 receipt는 보존했으며 `independent_v2`는 새 고유 attempt다. [거절 기록](evidence/C08_RESOURCE_REFUSAL.json), [변경 기록](review/RUNNER_C8_MEMORY_SELECTION_DELTA.json).

`plot_v1`의 aggregate child CPU **2.764225 s**는 예약 2 s를 넘었고, coordinator+tail **0.307125 s**도 예약 0.3 s를 넘었다. Per-process `RLIMIT_CPU`를 aggregate child 비용과 동일시할 수 없다는 실제 finding을 남겼다. 전체 unit cap은 충족하지만 해당 attempt는 FAILED이며, PASS 표시를 얻기 위한 재렌더링을 하지 않는다. 남은 **9.761581 s**는 이 단위 내부의 비이월 잔여다. [plot finding](evidence/C08_PLOT_RUNTIME_FINDING.json).

정적 검토에서 return overlap guard, 양쪽 metadata가 같이 잘못된 isotope mapping, preworker 비용 누락을 수정했다. 독립 reference의 최초 energy-coordinate 오해는 **실행 전** 수정하고 원 draft를 보존했다. C3에서 약속한 가법성 검사를 첫 독립 과학 실행 전에 추가한 이력도 남겼다. 과거 HeIII C9 v1 preworker 실패·owned stale lease·비용·unique v2 복구 및 다른 프로젝트의 `UNKNOWN_NO_ACK`는 수정하지 않았다. [C9 초기 검토](review/C9_STATIC.json), [reference 이력](review/REFERENCE_C3_ADDITIVITY_EXTENSION.json).

[C9 최종 독립 검토](review/C9_FINAL.json)는 scoped core numerical/contract를 수용했고 root가 실제 원문을 읽어 채택했다. Reviewer는 production 작성자가 아니며 초기 이론 memo와 독립 reference 작성자라는 관계를 공개했다. 별도 R6 이론 검토와 root의 실행 책임을 유지한다. 두 runtime 실패는 닫힌 성공으로 바꾸지 않는다.

## 6. 재사용 근거, 문헌 및 symbolic check

기존 PR107의 exact PR106 H1+HeI operator에 HeIII→HeII(1s) hazard 하나를 더한 결과는 원 범위에서 재사용한다. **8 cases, 224 primary RHS, 24 integrated exports, 36 controls, 252 grid comparisons, 56 independent RHS, 754 checks PASS**는 기존 결과다. 이번에 그 과학을 다시 실행했다고 쓰지 않는다. Old H1/HeI/C23E/source science replay, 새 source quadrature, 재projection, 새 ODE는 모두 0이다. 기존 T10000 K, $n_{\rm HeIII}=0.01\,{\rm cm^{-3}}$, conditional He4·ground·zero-recoil·scalar 범위는 현재 PHYS02 T100 K로 자동 이동하지 않는다. [이전 최종 handoff](https://github.com/cosmosapjw-quantum/bass_cr/blob/ec463db0c7e5c7fb5070796071c926caa4db6445/research/cr_heiii_ground_rr_20261027/HANDOFF_KO.md).

새 개념 근거는 SciSpace discovery 후 Exa와 primary source를 대조했다. Slatyer 2013/2016, Liu–Ridgway–Slatyer 2019의 history convolution, delayed deposition, propagating photon의 별도 취급을 참고했다. 이 문헌의 cosmology·$T$·density·spectrum·transfer 수치를 CR bath에 넣지 않았다. 추출문에 있던 불일치한 volume exponent와 잘못된 apparent publication date는 채택하지 않았다. [문헌 채택 기록](literature/EVIDENCE_ADOPTION.json), [유도와 원문 대조](THEORY_KO.md).

Wolfram은 한정 대수 검산 두 호출로만 사용했다. 첫 호출의 state ODE, count balance, finite capture, event energy, Jacobian integral 다섯 residual은 0이었다. Baryon quotient는 replacement precedence 문법 때문에 의도한 검사가 아니었으며 그 원출력을 보존했다. 괄호를 고친 두 번째 호출에서 quotient derivative와 finite $\Delta Y$ residual 두 개가 0이 되어 **올바른 distinct check는 7개**다. Time constraints는 20 s/5 s였고 provider CPU는 `null`로 유지한다. 이 값은 local CPU 0이나 actual RR activation 근거가 아니다. [symbolic 요약](evidence/R07_SYMBOLIC_SUMMARY.json).

## 7. 중앙 DAG와 공급자 경계

원 중앙 DAG는 계속 **27/88, 88 nodes/17 edges, 이번 집계 효과 0**이다. N4/N5는 `PARTIAL_OPEN`, N6/N7은 `PREDECESSOR_GATED`, L4는 false다. Global physical completion/error/budget remaining/currency는 모두 `null`이다. 별도 미병합 PR236의 32/88를 합산하지 않는다. [계약의 authority 경계](CONTRACT.md), [중앙 owner delta](intake/R02_R03_OWNER_DELTA.md).

최신 관찰 WU metadata pin은 `35bb7f296abc8ff6c8b38c2c08cc14dd498d4c99`다. Supplier scoped DAG **11/26**과 새 scoped 이론/코드 진전은 보존하되 physical rate admission은 false, HH_R10은 OFF, production은 NOT_ISSUED다. Primary reference 28/28 접근성은 rate/Q/state-branch-domain/deposition/consumer/activation 완료가 아니다. Git/native text 검증 진전과 **full ZIP·dual original-byte delivery pending**을 구분한다. WU의 숫자·$T$·$n_b$·clock·예산은 CR에 가져오지 않았다. [WU 최신 intake](intake/WU_DELTA_R09_METADATA_SUMMARY.json).

이 단위의 직접 관찰 REC pin `4a8e541030ee2cbd02e26ba671083b705d309d49`, HE pin `ac6042a6b0610b09d0576538767ee0299389a5eb`와 각각의 isotope mapping·유효범위·gate·별도 예산을 유지한다. 다른 공급자의 handoff에 적힌 더 늦은 참조를 직접 검증 없이 이 pin의 대체물로 쓰지 않는다. 개인 대화 전체 검색 unavailable, Drive partial inventory 한계도 그대로다.

## 8. 실제 과학 source 게시·백업과 최종 인계

과학 source S는 `022c163726b814885805bd9a7ab988fe963cda4a`다. [PR109](https://github.com/cosmosapjw-quantum/bass_cr/pull/109)에서19개 단계의 실제 expected-SHA/non-force 게시와 이중 checkpoint를 확인했다. 최종C10 문서D와 중앙M은 각각 실제 후속 receipt로 결속하며, 이 문서가 스스로 자신의 SHA나 미래 M을 만들어 쓰지 않는다. 최종S/D/M과20개단계완료는 PR109최종본문과 CLOSEOUT archive의 DELIVERY_AUTHORITY/HANDOFF를 읽어라.

Canonical source는 **BASS_CR_PROPER_SOURCE_20261027_022c163726b8.zip**,2737469bytes,SHA256 `d28fc2dc841e0b3804fa2ba47274113839b54868efa0d2c63f28b865a88b9c88`이다.242members/241payloads를 포함한다. Dropbox `id:BSpOijBcT10AAAAAAEDHZg`, [Drive 원본](https://drive.google.com/file/d/1hHv09ZI1-UIKklU4tGxEurxHMpIuVTfd/view)을 각각 실제 fullGET하여 전체archive와 모든payload SHA/CRC R3를통과했다. GitS164publicblobs의원격byte동등성도검증했다. [Source receipt](publication/SOURCE_RELEASE_RECEIPT.json), [dual rawR3](publication/SOURCE_REMOTE_R3.json), [Git R3](publication/S_GIT_R3.json).

S의과학내용을다시ZIP으로생성하지않고,D/M및후속영수증은별도closeout에담는다. 기존baselineS4e72c89b714431eb4c6ae07def777bbf72a5ae4c,D ec463db0c7e5c7fb5070796071c926caa4db6445,M5abe0d19df95db730e3e33bae0373c81ba37ce89 및기존canonicalsource/closeout은그대로보존한다.

다음물리연결은 [NEXT_UNIT_CONTRACT.json](NEXT_UNIT_CONTRACT.json)에고정했다. Same-state실제recipientresponse,유한returnhorizon과명시적nb가필요하며,절대volume값은worldtubetotal을요구할때만필요하다. 실제photon/baryon확장에는각source의revision/history/state-energyledger가필요하다. 새예산을따로고정하며현unit잔여를자동이월하지않는다. [다음인계](HANDOFF_KO.md)는C10preimage경계를표시하고,최종게시후복사용완결본은별도closeout및PR최종본문에결속한다.
