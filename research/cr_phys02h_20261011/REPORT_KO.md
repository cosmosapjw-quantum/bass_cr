# PHYS02H 연구 결과: 정확 모멘트 인증과 열별 병렬 생성

## 이번 단계의 결론

이 단계는 `CR-PHYS02H-EXACT-MOMENT-CERTIFICATES-AND-PARALLEL-OPERATOR`다. 이전 G의 저장 모멘트를 정확한 십진 유리수로 읽어 20개 열 방출시간 구간을 인증했다. 생산 모듈을 사용하지 않은 독립 계산에서도 모든 끝점 조건과 모멘트 분포군의 비공집합성이 확인됐다. 새 열별 병렬 생성기는 여기서 수행한 24개 작은 전체 행렬·선택 열 생성에서 대응하는 직렬 배열과 정확히 일치했다. 전체 9600점 생성과 NCP 성능은 아직 실행하지 않았다.

짧은 계산과 검증은 이 환경에서 완료한다. NCP의 다음 계산은 저장된 전체 9600점에서 두 모델의 원본 직렬 생성과 열별 병렬 생성을 비교하는 유한 과제다. 실제 자원과 같은 입력을 사용해 정확성·시간·메모리를 측정하고 원시 CSC 값까지 보존한다. 별도의 실제 반환 독립 심사 전에는 전체 크기 동등성이나 성능 개선을 채택하지 않는다.

최종 준비 admission과 실행 파일 identity는 `review/ncp/INDEPENDENT_NCP_DECISION.json`, `ncp/NCP_READY.json`, `ncp/EXECUTION_SOURCE_MANIFEST.json`에 기록한다. 이 보고서 자체는 root의 연구 해석과 사실 집계이며 독립 판정 파일을 대체하지 않는다.

## 1. 이어받은 실제 상태

기준은 G 게시 커밋 `f5ac634e67ab17e8820eed8f53d625b6c230a252`다. 새 PR39와 PR40은 같은 기준에서 갈라진 형제 반환이다. 같은 상대 경로의 서로 다른 파일을 덮어쓰지 않고 `inputs/latest_returns/pinned/pr39/`와 `pr40/`에 나누어 보존했다.

- PR39: `0c1379efe9b60d70d9cdb69f447eeb62c8720d13`. 사실 기반 typed HOLD closeout이다. 관측하지 않은 실행 시간·조회 수를 새로 채우지 않았고, `OUTPUT_RECEIPT_MISSING`와 리뷰 프로세스 exit124를 보존했다.
- PR40: `839309f6f1edc69e3c24f4d34cc8adba4f7a161f`. 읽기 전용 intake는 87.078603초 창 안에서 완료됐다. 두 명령의 실제 wall 합은 약2.132871초이며, 창의 전체 경과시간과 구분한다. 원래 E 경로를 첫 선택자가 놓친 사실과 같은 창 안의 보충 조회도 보존했다.
- 관측한 E 원래 run에는 두 pulse NPZ가 있으나 CSC 값이 없었다. F 원래 `/tmp/...` run과 기록된 다른 호스트의 라이브러리 경로는 현재 NCP에서 없었다. 다른 호스트·전역 캐시의 부재까지 증명한 것은 아니다.

따라서 이전 F의 `OPERATOR_IDENTITY_MISMATCH`는 미해결이다. 원래 F의 fullBED G 예약/완료 1/1은 이미 소비됐고, solve·pulse·expm은0이었다. 과거 G.data 지문 차이를 CPU dispatch의 인과적 증거로 바꾸지 않는다. PR40의 Python·라이브러리 metadata 관측도 미래 실행의 런타임 인증을 대신하지 않는다. 완료된 PR39/40 intake를 NCP에서 반복하는 과제를 만들지 않았다.

## 2. 확률량과 정확 산술 인증

열 방출 커널을 총 eventual heat로 정규화한 확률법칙을 사용한다.

\[
dF(\tau)=K(\tau)\,d\tau/H_0,\qquad
Q_f=\inf\{t:F(t)\ge f\}.
\]

이는 열의 방출시간에 대한 측도다. 고정 bath·유한 격자의 의미를 유지하며 우주론적 production history로 승격하지 않는다. 시간 단위는 초, \(T=10^{10}\,\mathrm{s}\), 연 단위 변환은 정확히 \(31557600\,\mathrm{s/yr}\)다.

입력 모멘트는

\[
p=P(\tau\le T),\quad R=E[(1-\tau/T)_+],\quad
S=E[(1-\tau/T)_+^2],\quad \mu=E[\tau],\quad m_2=E[\tau^2]
\]

다. 초기·잔여 모멘트의 지지집합 조건을 검사하고, 그 모든 모멘트를 재현하는 유한 원자 분포를 유리수로 구성했다. 잔여 시간 \(X=\tau-T\mid\tau>T\)의 평균과 이차 모멘트는

\[
a=\frac{\mu-T(1-R)}{1-p},\qquad
b=\frac{m_2-2T\mu+T^2(1-S)}{1-p}
\]

이며 \(a>0\), \(b\ge a^2\)를 정확하게 확인했다. 이 증인은 허용 분포군이 비어 있지 않다는 수학적 증거다. 실제 cascade의 시간법칙을 유한 원자 분포로 근사했다는 주장은 아니다. 전체 유도는 `research/DERIVATION_KO.md`에 있다.

### 두 기록 표현을 구별하는 이유

`selected_record`는 저장된 합계 레코드의 숫자 토큰을 그대로 정확 유리수로 읽는다. `birth_defined`는 출생별 레코드와 \(H_{0j}/\sum_jH_{0j}\)를 정확하게 혼합하여 합계 모멘트를 다시 정의한다. 저장 FP64 기록들은 허용오차 안에서 일치하더라도 정확 유리수로는 서로 다른 제약일 수 있다. 실제로 두 모델 모두 여섯 기본량이 정확히 같지는 않았다.

예를 들어 fullBED의 selected-minus-birth 차이는 \(H_0\)에서 \(7.6\times10^{-17}\), \(p\)에서 약 \(-4.912\times10^{-18}\), 평균 시간에서 약 \(-2.3640\times10^{-5}\)초다. 이 작은 기록 차이를 물리적으로 큰 효과라고 해석하지 않는다. Birth 표현이 제공하는 더 세분된 조건부 모멘트가 경계를 강화한다는 점과 십진 기록의 미세한 차이를 구별한다.

Selected에서는 해당 합계의 전체·잔여 경계만 결합한다. Birth에서는 그 혼합 정의와 일치하는 전체·pooled residual·birth residual 경계를 결합한다. 서로 다른 정확 표현의 경계를 교집합하여 하나의 exact-input 인증이라고 부르지 않는다. 어느 표현도 기존 physical SSOT를 대체하지 않는다.

### 끝점의 의미와 결과

모멘트로 얻은 survival 하한 \(L\)과 상한 \(U\)에 대해 정수 초 끝점에서

\[
L(t_{\rm lo})>1-f,\qquad U(t_{\rm hi})\le1-f
\]

를 정수 교차곱으로 확인했다. 따라서 각 인증의 정확한 의미는

\[
\boxed{t_{\rm lo}<Q_f\le t_{\rm hi}}.
\]

아래 표의 정수 초가 인증값이다. 소수로 표시한 연 단위 수치는 편의를 위한 변환이며 끝점을 반올림한 새 인증이 아니다.

| 모델 | 표현 | 방출 비율 | 엄격한 하한, s | 닫힌 상한, s |
|---|---|---:|---:|---:|
| fullBED | selected | 50% | 10000000000 | 919739075485 |
| fullBED | selected | 90% | 256220647080 | 2500060257121 |
| fullBED | selected | 95% | 331279403159 | 3413718170062 |
| fullBED | selected | 99% | 423899905897 | 7165947575016 |
| fullBED | selected | 99.9% | 473257253827 | 21690635467976 |
| fullBED | birth | 50% | 10000000000 | 917880933713 |
| fullBED | birth | 90% | 276023440157 | 2491895434603 |
| fullBED | birth | 95% | 355863646994 | 3392946080840 |
| fullBED | birth | 99% | 453795567601 | 7085748659418 |
| fullBED | birth | 99.9% | 505839742403 | 21369474484276 |
| legacy | selected | 50% | 10000000000 | 942031665462 |
| legacy | selected | 90% | 260969663243 | 2571473057409 |
| legacy | selected | 95% | 338246295043 | 3512278044405 |
| legacy | selected | 99% | 433604757662 | 7376011870545 |
| legacy | selected | 99.9% | 484421445972 | 22332350968047 |
| legacy | birth | 50% | 10000000000 | 940176340129 |
| legacy | birth | 90% | 281127239336 | 2563231831818 |
| legacy | birth | 95% | 363328926061 | 3491220229835 |
| legacy | birth | 99% | 464159998233 | 7294455748646 |
| legacy | birth | 99.9% | 517745500019 | 22005382287290 |

예를 들어 fullBED birth의 90% 구간은 약8746.655년–78963.401년이고, 99% 구간은 약14379.914년–224533.826년이다. 두 모멘트만으로 허용되는 구간이 여전히 넓다. 정확 산술 인증은 구간을 실제 분위수의 정밀 추정으로 바꾸지 않으며, 유한 시간의 100% 방출을 증명하지 않는다.

이전 G-R01의 FP64 끝점과 정확 십진 토큰 사이 부등호 불일치 기록은 그대로 남는다. H는 정수 초의 별도 인증을 추가했다. 인증의 가정은 저장된 십진 모멘트가 정확한 입력이라는 것이며, 모멘트 자체의 전방 오차·물리 불확실성·격자 수렴·장시간 bath 타당성은 범위 밖이다.

## 3. 여기서 완료한 실행과 검증

| 작업 | 실제 수행 | wall 및 결과 |
|---|---:|---|
| 정확 산술 단위 검사 | 8개, 첫 실행 | 0.089659초, exit0 |
| 저장 모멘트 인증 | 1회, 20개 구간 | 0.291567초, exit0 |
| 독립 Fraction 참조 | 1회 | 0.074503초, exit0 |
| 병렬 생성기 표적 검사 | 4개, 첫 실행 | 2.039초, exit0 |
| 작은 전체 행렬·선택 열 파일럿 | 1회, 24개 논리 생성 | 66.284736초, exit0 |

독립 scalar 검증은 생산 모듈을 import하지 않았다. 모멘트 증인8개, 끝점 인증20개, 정수 증명240개, 끝점 성분 경계100쌍, 인접 정수 초 조건40개, 별도 유한분포의 strict survival226개를 확인했다. 판정은 `review/exact/INDEPENDENT_EXACT_DECISION.json`의 `PASS_SCOPED`다.

병렬 파일럿은 240점 작은 전체 행렬16개와 저장된9600점 에너지에서 고정 선택16열의 생성8개다. 실제 generator 진입은 원본 작은 기준4회, 선택 열 직렬4회, 부분 worker44회로 총52회다. 논리적 전체 생성 수와 worker 부분 호출 수를 구별한다. 전체9600 생성·pulse·expm·resolvent·선형계 풀이·F 재시도는 모두0회다. 검사 중 의도한 자식 실패는 별도 test evidence에 남고 실제 파일럿 성공 수에 합치지 않는다.

서로 다른 열은 원래 생성식에서 읽기 전용 에너지·원자 입력을 공유한다. AST 변경은 함수명·열 인자·바깥 열 iterator에 제한했고, 열 내부 부동소수 연산 순서를 유지했다. 각 열을 한 번 계산한 후 원래 열 순서대로 CSC data/indices를 이어 붙이고 indptr만 정수 offset으로 조립한다. Worker 간 부동소수 합산이 없다.

모든 대응 결과에서 data·indices·indptr·에너지·반응률 배열과 순서가 있는 normalization diagnostics가 정확히 같았다. 24개 payload 모두 실제 NPY 값과 dtype·shape·원시 및 파일 hash를 저장했다. 공유된 원래 생성식과 물리 입력은 독립적인 물리 oracle이 아니며, 이 검사로 원자 모델의 타당성이나 과거 operator 채택을 승인하지 않는다. 독립 local 병렬 판정은 `review/parallel/`에 별도로 보존한다.

### 경량 작업의 병렬 실행 비용

각 표는 같은 scope에서 두 반복의 평균 end-to-end 생성시간이다. 새 프로세스·import·조립 비용을 포함한다.

| 입력과 모델 | 직렬, s | 4-worker, s |
|---|---:|---:|
| 240점 전체, legacy | 1.485897 | 3.413700 |
| 240점 전체, fullBED | 1.065140 | 3.048610 |
| 9600점 중 선택16열, legacy | 0.541768 | 4.965598 |
| 9600점 중 선택16열, fullBED | 0.526971 | 4.809363 |

이 크기에서는 spawn 비용이 계산량보다 크므로 병렬화의 성능 이득이 없었다. 이 사실이 정확 산술·작은 probe·단위 검사를 여기서 처리하는 배치 결정의 근거다. 현재 호스트는 실제 cgroup quota8 CPU와 memory.max8GiB다. 관측된 최대 fresh worker lifetime peakRSS는132059136B, 약125.941MiB였다. Coordinator의 값은 누적 lifetime peak이며 동시 전체 RSS로 해석하지 않는다. 지원 프로세스 resource_tracker의 RSS는 그 수치에 포함되지 않았다.

## 4. NCP에 넘기는 무거운 부분

과제는 `CR-PHYS02H-NCP-FULL9600-COLUMN-PARALLEL-QUALIFICATION`이다. 원래 저장 에너지를 그대로 사용해 fullBED와 legacy의 전체 생성행렬을 현재 런타임에서 직렬·병렬로 만든다. 두 모델을 독립 lane으로 실행하며, 각 반복의 직렬 reference 다음에 병렬 candidate를 실행한다. 두 반복에 총8개 논리적 전체 생성, 총76800열 평가가 상한이다.

전체 coordinator 명령의 누적 시간 한도는900초다. 복구·전송 시간과 실패 후 증거 수집은 따로 기록하되 과학 실행의 시계를 초기화하지 않는다. 첫 실패 시 소유한 process group을 중단하고 예약·완료·부분 값과 실제 exit를 보존한다. 자동 재시도는0회다.

| 자원 항목 | 적용 기준 |
|---|---|
| CPU | 실제 affinity·cgroup quota·가용 topology로 결정, 최대64 logical CPU |
| 실제64 CPU에서 후보 배치 | 모델당29 workers, wrapper1 + root1 + lane2 + support2 포함 총64 슬롯 |
| worker 내부 thread | OpenBLAS/MKL/OMP/NumExpr 각1 |
| 메모리 reserve | 실제 한도 기준 max(16GiB, 한도의1/8) |
| paired 직렬 작업 여유 | 모델당12GiB, 합계24GiB + reserve |
| 후보 메모리 예산 | lane parents 합계4GiB + workers58×512MiB + support64MiB + wrapper64MiB, 실제 가용량에 따라 감소 |
| free disk | 실행 출력용 최소16GiB, 입력 백업 공간 별도 |
| 런타임 | 관측·검증한 Python3.12.3 / NumPy2.4.2 / SciPy1.17.0 |

CPU 지원 슬롯과 support 메모리는 실제 작은 파일럿을 반영한 `NCP_RESOURCE_AMENDMENT.json`으로 보완했다. 최종 wrapper 통합에서 watchdog 프로세스1개가 추가로 확인돼 `NCP_WRAPPER_ACCOUNTING_AMENDMENT.json`으로 고정6슬롯과 wrapper 메모리64MiB를 반영했다. 이전 계약과 최초 검사 소스를 보존했다. 128GB 표기를128GiB와 같다고 두지 않으며,64 logical CPU를64 physical cores라고 부르지 않는다. 모델당29는 실제 자원 조건이 충족될 때의 상한이다. 메모리를 불필요하게 채우는 것을 목표로 삼지 않는다.

성능 비교는 같은 모델·입력의 두 반복에서 build-and-persist 시간을 비교한다. 직렬 reference와 candidate 양쪽의 실제 원시 값을 저장하고, candidate의 worker 시작·부분 결과 수집 비용도 포함한다. 정확성 통과와 성능 개선은 별도 판정이다. 더 느리면 `PERFORMANCE_NOT_IMPROVED`로 기록한다. 아직 전체9600 실행이 없으므로64 CPU 가속률을 제시하지 않는다.

### 실패 수집과 프로세스 종료의 교정 기록

NCP 실행기의 첫 독립 심사는 HOLD였다. Qualifier가 이미 죽었을 때의 남은 worker 정리, 손상된 제어 JSON과 event line의 수집, 별도 session comparator의 소유권 기록,900초 deadline 직후 실제 계산 중단에 다섯 결함이 있었다. 최초 판정과 검사한 source/manifest를 `review/ncp/initial_manifest_hold/` 및 `evidence/ncp_validation/pre_cleanup_correction/`에 보존했다.

Root가 원래 계약을 충족하기 위한 구현 수정을 승인했다. 첫 교정의 영향 검사8개는6통과·1실패·1오류였으며 기록을 남겼다. 두 실패의 공통 원인은 이 호스트에서 시스템 호출의 PID namespace와 마운트된 `/proc`의 조상 namespace가 다르다는 것이었다. 동일 PID 숫자를 두 관측 범위에서 같은 프로세스라고 취급한 매핑 오류를 수정했다. 프로세스 소유권·parent route·session 기록·group 취소·RSS 조회에 같은 namespace 구분을 적용한다. 모호한 매핑을 다른 process group에 대한 종료 권한으로 바꾸지 않는다.

그 직접 영향만 확인한 마지막 batch는6개 모두 통과했다. 실제 exit0, wall1.725660511초다. 살아 있던 두 orphan session은 종료 후 GONE으로 관측됐고, watchdog fixture의 자식은 root의8초 정리 유예 전에 ZOMBIE로 관측됐다. 최초 실패 당시의 자식 상태는 관측하지 않았으므로 `NOT_OBSERVED`로 남긴다. 새 측정 방법이 이전 파일럿의 lifetime RSS를 동시 전체 메모리 측정으로 바꾸지는 않는다.

이 검사는 가짜 process/raw-value fixture에 한정되며 물리 생성·열 평가·기존 과학 검사 재실행은0이다. 고정된 최종 execution manifest의 SHA256은 `14f9ad1319146c72d13b1e30583dc27d3b9272c8d23913e63467782fa57b35ec`다. 후속 독립 판정은 그 새 identity에만 결속하며 초기 HOLD를 덮어쓰지 않는다. 실제 NCP qualification 결과의 독립 심사는 여전히 별도 의무다.

새 reference/candidate의 정확 일치는 현재 런타임의 새 구현 qualification이다. 과거 reference 및 실패한 F 지문과의 비교는 정보로 남긴다. 새 생성 결과를 원래 보관된 CSC의 복구라고 부르지 않으며, 옛 pulse·residence 결과를 자동 채택하지 않는다. NCP 실제 결과가 통과하더라도 다음 adjoint/frontier 계산에는 별도로 검토된 source/operator 결속과 예산 계약이 필요하다.

## 5. 보존하는 판정과 후속 의무

| Gate | 현재 상태 |
|---|---|
| F | HOLD_OPERATOR_BINDING_UNRESOLVED |
| G frontier | BLOCKED_BY_F_OPERATOR_BINDING_HOLD |
| PHYS02_DELAY | OPEN |
| production_history | HOLD |
| atomic_G02 | UNRESOLVED |
| b_grid | NO_GO |
| all_bound | OPEN |
| R17B2B | NO_CERTIFIED_SOURCE_SHARPENING |
| CCC_2026_exporter_identity | SOURCE_IDENTITY_UNRESOLVED |

최종 전달은 H source·정확 인증·24개 값 payload·독립 검토·실행 계약·NCP handoff와 byte-identical 기존 G 완전 백업을 한 outer에 포함한다. G 안의 F 완전 payload에는 기존 의존 데이터와 canonical Astra 하네스가 있다. PR39/40의33개 출처 파일을 분리된 경로로 포함했다는 범위를 명시하며 두 반환 archive 전체를 새로 복구했다고 주장하지 않는다. 추가 사용자 첨부 없이 정확한 입력과 새 launcher를 복구할 수 있어야 한다.

## 근거 파일과 원전

- `inputs/latest_returns/LATEST_INTAKE_KO.md`, `LATEST_INTAKE_REPORT.json`, `PINNED_FILE_IDENTITIES.json`: 실제 원격 intake와 출처.
- `evidence/exact/EXACT_CERTIFICATES.json`, `EXECUTION_RECEIPT.json`, `PROCESS_RECEIPT.json`: 정확 인증과 실제 실행.
- `review/exact/INDEPENDENT_EXACT_DECISION.json`, `INDEPENDENT_EXACT_REVIEW_KO.md`: 별도 산술·확률 검증.
- `evidence/parallel/SUMMARY.json`, `REPORT.md`, `pilot/RESULT.json`과 원시 payload: 실제24개 생성과 시간·자원.
- `review/parallel/`, `review/ncp/`: 각각의 고정된 독립 판정 범위.
- `ncp/NCP_EXECUTION_CONTRACT.json`, `NCP_RESOURCE_AMENDMENT.json`, `NCP_WRAPPER_ACCOUNTING_AMENDMENT.json`, `EXECUTION_SOURCE_MANIFEST.json`, `NCP_READY.json`: NCP 준비와 실행 범위.
- Bertsimas & Popescu, *SIAM Journal on Optimization*15(3),780–804(2005), https://epubs.siam.org/doi/abs/10.1137/S1052623401399903 — 모멘트 확률경계의 일반 틀. CR 초기·잔여 혼합 유도는 이번 작업의 직접 유도다.
- SciPy CSC 문서, https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csc_matrix.html — CSC 열 저장 구조. current 문서 버전을 실행 버전으로 대신하지 않는다.
- NumPy SIMD 문서, https://numpy.org/doc/stable/reference/simd/index.html — 런타임 kernel 선택의 일반 배경. F 오류 원인 확정 자료가 아니다.

## 최종 준비 판정

후속 독립 심사는 최종 v2 execution manifest에 대해 `PASS_SCOPED`, `ncp_preparation_admitted=true`를 기록했다. 독립 판정 SHA256은 `756eb62b0ec9ac2db5a470bf7eb6523af5ecf54d35ed7faa66f8bf990e7c2820`다. `NCP_READY.json`이 그 판정과 정확한 실행·입력 manifest를 결속한다. 이 승인은 준비 코드에 한정되며 실제 NCP 실행·전체 크기 parity·성능 승인은 아직 없다.
