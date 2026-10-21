# C21N 미완료 offgrid4 실행 반환 계약

## 닫을 노드

이 단위는 이미 준비된 `OFFGRID4_EXECUTION`과 그 결과 분석·게시·백업을 닫는다.
새 연구 사이클이나 성능 벤치마크를 시작하지 않는다. 이전 C21N 정적 검증
단위의 신규 ODE 0회라는 역사적 기록과 source는 변경하지 않는다.
기존 C21L81 및 독립 125개(26+NCP98+원 중심1)는 재적분하지 않는다.

재개 기준 문서 HEAD는 `0f45d0a422d79ccead565a8abaab860fcc230687`이다.
실제 실행은 격리 checkout의 C21N content
`5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`를 사용한다.
물리 source는 REI `3b85dedce84d37b3e165da00685a8a984950aafe`다.
공개 코드·source·FP64·분포·solver tolerance를 바꾸지 않는다.

## 실행 입력과 환경

고정 grid SHA256은
`2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5`,
run ID는 `c21n_offgrid4_opposing_z20_z4_20261021`이다.
새 4개 입력은 signed full Frobenius 좌표
`S0=0`, `Pm0=±7.5e-5,±1.75e-4`, `Pr0=-Pm0`이다.
이들은 기존 125개에 포함되지 않는다.

실제 접근 가능한 외부 refs·백업에서 새 실행 반환을 먼저 확인한다.
직접 다른 대화에 접근할 수 없으면 `UNAVAILABLE`로 기록한다.
해당 4개 반환이 이미 존재하면 재실행하지 않고 source와 raw를 검증해 수용한다.

현재 지정 NCP SSH 키가 없어 이 환경의 NCP 접근은 확인되지 않았다.
따라서 새 반환이 없으면 현재 샌드박스에서 `--execution-site sandbox`로
실행한다. 새 run output은 create-only다. 현재 CPU affinity·cgroup quota·RAM·
load·공유 lease·disk·inode를 다시 관측한다. 최대 worker4, numeric thread1,
coordinator 비용과 CPU55 보호 정책을 포함한다. 다른 owner의 작업은 변경하지 않는다.
NCP actual execution은 이 로컬 실행으로 완료 처리하지 않는다.

고정 문제는 non-tilted collisionless LRS Bianchi I, z20→4,
40 FP64 상태·101개 저장점·DOP853 `rtol=3e-11`, `atol=3e-13`이다.
매 A마다 massive distribution weight와 reference normalization을 재생성한다.

## 후처리와 수용 범위

새 raw의 manifest·source·software·STARTED/RESULT/COMPLETE seal을 확인한다.
새 404개 저장 상태에 대해 component tensor·signed amplitude·norm·cancellation,
positivity·수·Hamiltonian 검사와 원 source의 정적 field/RHS 비교를 수행한다.
원 solver로 같은 4개를 다시 적분하지 않는다. 기존 125개는 저장된 분석값을
비교 문맥으로 재사용하며 새 combined129를 정규 3차원 격자로 부르지 않는다.

초기 mass-shell jet은 기존 C21N 유도와 코드를 재사용한다. 실제 작은 FP
offset과 이상적 상쇄 조건을 구분한다. 국소 Taylor 계수는 전 구간 근사나
오차 상계가 아니다. `global_error_bound=null`을 유지한다.

P0 또는 source identity 충돌은 해당 결과 promotion만 중단하고 원 실패를
보존한다. 상세 benchmark, speedup·memory improvement·64-core scaling은
수행·주장하지 않는다. General triaxial/full reionization/CMB는 HOLD다.

## 게시·백업

원 C21L/M/N 경로는 그대로 두고 새 경로에 실행 반환·분석·검증을 게시한다.
Content와 document commit을 구분하고 실제 ref 확인을 R1으로 기록한다.
새 ZIP은 create-only로 생성한다. 저장처별 object ID·size·ACK를 따로 보존하며,
이전 두 C21N Drive 업로드의 미확정 결과를 새 ACK로 소급 승격하지 않는다.
Provider ACK와 실제 다운로드 byte 검증은 구분한다.
