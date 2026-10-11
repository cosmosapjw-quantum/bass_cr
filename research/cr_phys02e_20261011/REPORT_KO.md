# CR-PHYS02E — 저장 에너지 격자의 의미 보존과 새 NCP pulse 작업

## 이번 루프의 결론

실제 PHYS02D NCP 실행은 **fullBED G를 생성한 뒤 exact-grid 검사에서 실패했다**. 이에 이어 이번 루프는 저장 NPZ의 에너지 격자를 모든 격자 의존 연산 전에 설치하는 명시적 생성자를 구현했다. 두 저장 입력의 무물리 preflight, 생성자 결속, strict guard, 실제 종료 코드 보존과 완전한 반환 수집을 검증했다. 7개 saved-grid 시험과 8개 NCP plumbing 시험은 모두 exit0이며 최초 실패·repair는 없었다. 실제 물리 G 또는 pulse는 이번 준비 과정에서 실행하지 않았다.

독립 판정의 원본은 `review/INDEPENDENT_DECISION.json`이다. 이 판정이 고정 계약과 여섯 코드 파일의 bytes/SHA256을 실제로 결속해야 `state/NEXT_DAG.json`의 새 NCP 작업을 READY로 바꿀 수 있다. 최종 ZIP clean restore와 `--plan`은 science freeze 이후 별도 publication gate다. 실제 NCP에서의 수치 성공 또는 전역 물리 주장 승격은 이 준비 판정의 범위에 들어가지 않는다.

## 1. 출발점은 실제 실패 반환

출처는 [bass_cr PR33](https://github.com/cosmosapjw-quantum/bass_cr/pull/33)의 head `20c2e6de7c58c3690efca6322489b811c99f3e99`, tree `d47ad3e29b96953aae45570c6bdb6f4a71bfc7dc`다. 실제 ZIP을 정확 ID로 받아 5,350,251 bytes와 SHA256 `2400e9a4350d03379b12fdad00c8990c93099011dfc95530b02ae2c26e8dc4c5`를 확인했고,398개 entry와 내부 manifest 전체를 검증했다. 새로 올라온 PR33의49개 파일도 정확 Git blob에 맞춰 복구했다. 관련 원본과 검사 영수증은 `research/context/` 및409-file dependency payload에 포함한다.

| 관측 | 실제 값 / 해석 |
| --- | --- |
| 실행 시간 | 2026-10-11T00:27:45Z–00:29:29Z |
| launcher exit | **1** |
| launcher wall | 103.79789273899951 s |
| G | fullBED 생성자1회 반환; G 자체는 저장하지 않음 |
| pulse / legacy | pulse0, legacy 시작 전 |
| 실패 | `STORED_SOURCE_GRID_FIELDS_MISMATCH` |
| 차이 | 340/9600 energy nodes, 최대1 ULP |
| 최대 절대차 | 1.1368683772161603e-13 eV |
| 이전 독립 판정 | HOLD |
| wrapper exit0 | 실패 자료 수집의 성공이며 수치 성공이 아님 |

그 실행의 Python3.12.3/NumPy2.4.2/SciPy1.17.0 버전 문자열은 계약과 맞았지만 재생성 E는 저장 E와 exact 동일하지 않았다. 저장 격자의 raw C-order float64 SHA256은 `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`, 재생성본은 `870cfd5f3f2656371d5fad59e4b24f4b7aa051546b9d78f4f3a9de3197fcc0a4`다. CPU/SIMD/libm 중 무엇이 차이를 만들었는지는 현재 증거로 분해하지 못했으므로 UNRESOLVED로 유지한다. 1 ULP라는 사실만으로 물리적 허용성을 단정하지 않는다.

## 2. 왜 E는 단순한 표시 배열이 아닌가

부모 `causal_cascade.Cascade`의 활성 상태는 전자수 자체가 아니라 에너지 좌표다.

\[
U_i=E_iN_i.
\]

따라서 활성 에너지의 선형 함수는 가중치1을 갖고, cutoff 전자수와 이온화 생성 수를 보정한 전자수 함수는

\[
\ell_N(E)^TU=\sum_i\frac{U_i}{E_i}+N_{\rm cutoff}-I_{\rm H}-I_{\rm He}
\]

가 된다. 누적 이온화 수를 빼는 이유는 이온화가 자유전자를 추가로 만들기 때문이다. cutoff energy는 원래 모델의 별도 장부이며 heat로 임의 이동하지 않는다. `low_cross_*`는 내부 통과 진단량으로 전역 에너지에 다시 더하지 않는다.

`project`는 입사 전자수 p와 에너지 W를 이웃 격자점으로 나눌 때

\[
N_l+N_u=p,\qquad E_lN_l+E_uN_u=pW
\]

를 동시에 보존하는 barycentric 분할을 사용한다. 같은 E가 projection, drift 간격, 원자율 평가, 이온화 전자 분배의 반사 knots, 저장 source의 셀 좌표와1/E 장부에 들어가야 이 항등식들을 하나의 연산자에 대해 적용할 수 있다. 부모의 물리적 시간 generator를 A라 하면 G=T_END A는 u=t/T_END에 대한 시간 재척도화 생성자다. 에너지→수 장부 성분은 eV⁻¹ 등 혼합 좌표 차원을 유지한다. 원래 연산자 및 장부 가정 아래 정확 산술에서 두 전역 장부는 영이다.

\[
\ell_E^TG=0,\qquad \ell_N(E)^TG=0.
\]

### G 생성 후 E만 바꾸면 생기는 문제

G를 유지한 채 E만 E′로 바꾸면 새 장부 잔차는

\[
\ell_N(E')^TG(E)
=[\ell_N(E')-\ell_N(E)]^TG(E)
\]

다. 에너지 장부의 활성 가중치1은 E와 무관하므로 이 오류를 놓칠 수 있다.

정확 반례로 E1=1 eV, E2=2 eV, 위 상태의 drift rate d=1 s⁻¹을 잡자. 아래 활성 상태·위 활성 상태·heat 순서에서 해당 A의 열을

\[
A_{\cdot2}=\left(\tfrac12,-1,\tfrac12\right)^T{\rm s}^{-1}
\]

로 두면 두 보존식이 성립한다. 이제 E2만 2 eV+ε로 치환하면 에너지 잔차는 계속0이지만 수 장부 잔차는

\[
\ell_N(E')^TA_{\cdot2}
=\frac{d\epsilon}{(2\,\mathrm{eV})(2\,\mathrm{eV}+\epsilon)}
\]

가 된다. 2 eV 바로 위 binary64 한 ULP인 ε=2⁻⁵¹ eV에서는 정확히 `1/9007199254740994 (eV s)^-1`이다. Fraction만 쓴 해석 예제는13개 항등식을0.028147148초에 확인했다. 이 값은 실제9600점 G의 오차값이나 상계로 사용하지 않는다.

반대 방향의 한계도 남는다. E가 같더라도 drift rate만 바꾸면 두 보존식은 계속 영이며 transient response는 달라진다. 따라서 **exact E + 에너지/수 보존만으로 전체 G의 동일성이나 실제 pulse 정확성을 증명할 수 없다**. 자세한 유도·원본 메서드 identity·검산은 `research/theory_contribution/`에 보존했다.

## 3. 구현에서 고정한 것

`src/saved_grid.py`는 전체 파일 identity를 먼저 확인한 뒤 두 NPZ를 읽는다. energy_eV, state_normalized, source_vectors, terminal_yields, physical_energy_scale_eV_m3, time_s, birth_tags의14개 배열 identity를 기록하고, immutable bytes에 기반한 복사본을 반환한다. source의 cutoff·counter 행을 포함한9611×2 배열을 그대로 사용한다. source heat의 초기값은 정확0이어야 한다.

에너지 배열은 little-endian float64,9600점, strictly ascending, low/high3200/6400, CUT0.1/SPLIT10/UPPER900 eV와 raw SHA를 만족해야 한다. 시간은 정확 `[0,1e10]`, birth tags는 `direct_0p1_10`, `direct_10_900`이다. 두 번째 입력이 잘못되어도 첫 G 생성 예약 전 거부한다.

명시적 `SavedGridCascade`는 source-pinned 부모의 subclass이며, 격자를 재생성하는 부모 `__init__`을 호출하지 않는다. 검증한 저장 E를 먼저 설치하고 나머지 n·size·ledger index·atomic object·sharing_order4·quantum_constant0·mesh·normalization diagnostics를 원래 초기화와 같게 둔 뒤 inherited `_generator`를1회 호출한다. `_generator`, `project`, `_sharing`, `functionals` 등 수치 메서드는 부모의 같은 함수 객체다. 생성 후 strict `np.array_equal` guard도 유지한다. production monkeypatch, allclose 완화, G 뒤 E 치환은 없다.

NCP launcher는 동일한 무물리 numerical preflight를 별도 `--preflight`와 worker 진입점에서 사용한다. 두 입력 preflight를 마친 뒤 BUILD를 먼저 예약하고, 원자 모델 import/construct와 저장 격자 생성자 호출을 차례로 수행한다. 각 생성이 끝나고 exact guard를 통과하면 별도의 `G_COMPLETION_n.json`에 E identity, inherited method bindings, CSC shape/nnz/dtypes와 data/indices/indptr의 raw SHA를 기록한다. 큰 G를 다시 복사하거나 원본 G 동등성을 주장하지 않는다.

pulse 엔진과 resource adapter는 PHYS02D와 파일 전체가 byte-identical이다. launcher의 pulse 이후 SI 환산·저장 ramp 비교·terminal 비교·saved R,S 기반 CDF bound 검사 본문도 byte-identical이다. 기존1e-9 상대 비교와 물리적 허용오차를 변경하지 않았다.

`run_and_collect.py`는 execute를 한 번 호출하고 finally에서 반환을 수집한다. execute1+collect0이면 wrapper는1을 반환하고, execute0+collect1이어도 실패를 드러낸다. archive에는 실제 launcher `ACTUAL_EXIT.json`과 `WRAPPER_EXECUTE_EXIT.json`이 들어간다. 수집 후에야 알려지는 최종 wrapper/collection receipt는 archive SHA를 결속하는 외부 sidecar로 남긴다. archive에 자기 hash를 넣는 순환은 만들지 않는다.

## 4. 실제 검증과 그 범위

| 작업 | 실제 결과 | 물리 계산 범위 |
| --- | --- | --- |
| Fraction 해석 예제 |13 identities,exit0,0.028147148 s | 물리 import/G/pulse0 |
| SG01–05 |7 tests,exit0,0.678532955 s | 실제 saved arrays, mock generator, 작은 inherited projection probes |
| SG06–09 |8 tests,exit0,1.139337197 s | mock 이벤트·isolated admission·wrapper exit·409 dependency collector fixture |
| 독립 identity 확인 |5 계약,19 direct input,409 dependency, worker raw/source identities | 코드·증거 read-only, 물리 G/pulse0 |
| SG10 | 최종 freeze 후 receipt에 기록 | clean restore 및 stdlib `--plan`, 물리 G/pulse0 |

두 구현 시험의 첫 실행이 모두 성공해 repair0이다. 원래 suite를 다시 실행하지 않았다. local Python3.12.14/NumPy2.3.5/SciPy1.17.0은 시험 기록이며 NCP runtime 인증이 아니다. 실제 NCP는 Python3.12.3/NumPy2.4.2/SciPy1.17.0 및 모든 numerical pool1 thread를 별도로 확인해야 한다.

정확 source/manifest 확인은 연산자 재현을 위한 입력 admission이며 모든 물리적 근사의 인증은 아니다. 독립 리뷰는 구현·후보·수락 기준 작성에 참여하지 않은 역할이 담당한다. 요청한 lower-tier 구현 모델과 실제 노출된 host label은 별도 기록하고 비용·backend를 추측하지 않았다.

## 5. 다음 NCP 작업 하나

새 작업은 `CR-PHYS02E-NCP-SAVED-GRID-PULSE`다. 이전 PHYS02D 예약을 재사용하지 않으며, 현재 사용자 계속 요청과 새 고정 계약·독립 검토에 연결된 별도 bounded batch다.

| 제약 | 값 |
| --- | --- |
| 모형 순서 | fullBED → legacy |
| 격자 | 저장9600점, low/high3200/6400 |
| 실제 G / pulse 상한 | 모형별1회, 합계2회 /2회 |
| 전체 wall 상한 | coordinator 준비를 포함3600 s |
| pulse sample |17개, source birth column2개 |
| dtype / thread | 기존 FP64, BLAS 등1 thread |
| 자원 | 실제 affinity/cgroup의 가장 제한적인 가용량; reserve후 working memory≥12GiB, disk≥8GiB, effective CPU≥1 |
| 실패 대응 | first failure 보존·수집; 자동 재시도·대체 grid·old ramp/suite 실행 없음 |
| 실제 반환 판정 | 새 독립 Astra review 필수 |

`--plan`은 stdlib 전용이며 프로세스 exit0만 보면 안 된다. JSON의 admission_status와 resource_probe.admitted를 각각 확인한다. exact-runtime `--preflight`를 통과한 뒤 wrapper를 한 번 실행한다. worker 내부 preflight는 다시 필수로 수행하며 추가 물리 호출 예산이 아니다. 입력 preflight 실패 때는 G/pulse 없이 diagnostics를 보존한다.

## 6. 유지되는 미해결 항목과 전달

PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC exporter identity SOURCE_IDENTITY_UNRESOLVED를 유지한다. 실제 pulse/CDF, uncapped delay moments, full G parity 또는 NCP64 성능을 새로 주장하지 않는다.

완전한 인계 묶음은 새 단위,409개 정확 dependency, 이전 실제 실패 ZIP, 두 Astra harness를 포함한다. Git에는 PR33 head를 부모로 한 새 단위만 추가하고 draft PR을 만든다. 완성 ZIP과 standalone NCP 시작문서는 기존 Drive/Dropbox 백업에 create-only로 추가한다. 실제 science commit·archive SHA·Drive ID·Dropbox ID/rev는 freeze 밖 publication receipt에 고정한다. 업로드 확인과 원격 restore는 구분하며, 이번 완성 ZIP에 수행하는 복구 검사는 local clean restore다.

추가 사용자 첨부 없이 정확 백업본 하나를 복구해 시작할 수 있다. 상세 명령과 반환 정책은 `START_NCP_CODEX_KO.md`, `ncp/README_KO.md`, 이후 standalone backup-ID start를 따른다.
