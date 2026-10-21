# 물리 source를 유지하는 최적화 판단

## 목적

목표는 첫 non-tilted LRS (Sigma,Pi_m,Pi_r) 과학 pilot와 재현 가능한 후속 실행이다. 최적화 후보의 타당성은 같은 초기 분포·방정식·FP64·quadrature·허용오차·출력 계약에서 판단한다. 이번에 새 속도 비교, 상세 benchmark, 64-core scaling 또는 memory 개선율 측정은 하지 않았다.

## 채택한 것

| 방법 | 실제 구현과 물리적 이유 | 확인 범위 |
|---|---|---|
| 저장 결과 재사용 | 원 C21L81의 full40 raw를 후처리; 27점 중심은 원 trajectory를 참조 | 원340파일·source9파일 hash, manifest, raw/receipt; ODE0 |
| worker별 immutable template | C21L adapter의 Legendre energy/number 연산행렬을 한 번 만들고 read-only로 보존 | 기존3 대표 full-trajectory bitwise 근거 및 새 초기조건/RHS 검사 |
| exact common-subexpression reuse | canonical moment의 동일 energy/weight 식을 같은 reduction 순서로 공유 | 원 계산식을 유지; 새 A에서 original RHS/fields를 확인 |
| 분포 재구성 | A별 원 CanonicalMomentumFV constructor로 weights·cell populations·정규화 갱신 | source weight/norm 비교, 비음성 domain, target mapping |
| case 병렬화 | 독립 초기조건 단위 multiprocessing, worker당 immutable builder, queue당1개 | 실제26case/4workers; 운영 test double에서 inflight bound와 부하 축소 |
| oversubscription 제한 | BLAS/OpenMP 등 thread 환경을1로 고정 | 실행 receipt의 환경값; process 보조 thread와 구분 |
| 동적 admission | 보이는 cgroup v1/v2 및 ancestor별 quota−외부usage, affinity, memory, per-CPU 부하 | synthetic nested quota·lease 테스트, 현재 sandbox 관측; NCP 미관측 |
| 결과와 재개 | case별 create-only raw/receipt/COMPLETE hash; 미시작 case만 재개 | 완료 raw 변조 거절, interrupted no-autoretry, 자기 worker cleanup 독립검토 |

고정 radial/angular grid는 원 source가 제공하는 canonical covariant momenta 구조를 활용한다. Heinzle–Uggla gr-qc/0512031의 Eq.(3) f=f0(v_i)와 Eq.(2d–f) moment 표현이 이를 뒷받침한다. 다만 현재 C21M builder는 A를 바꿀 때 원 constructor의 quadrature 설정까지 다시 만들며, 변형 가능한 weight와 불변 grid를 완전히 분리한 추가 buffer 구현까지 했다고 주장하지 않는다. 첫 pilot에서 검증되지 않은 allocation 재사용을 넣을 필요는 없었다.

## 외부 구현을 읽고 제한적으로 재사용한 것

REI PR198의 independent matter/radiation initial mapping 구조는 동일 물리 source를 사용하며, 성분 분리와 초기 A/k 역변환 설계에 활용했다. 원 vendor4개 SHA가 C21L과 일치함을 확인했다. 그러나 그 실행은 reduced8 state/65 saved samples/half convention이며, 이번 C21M은 원40 state/101 samples/full convention이다. 외부 완료606개의 count와 결과는 외부 provenance 아래 수용했다.

REC PR116은 같은 S slice에서 Fhat=F(S,m,0)+F(S,0,r)−F(S,0,0)라는 additive axis response를 재사용했다. 그 결과는 매우 짧은 warm UV/Thomson 구간의 retrospective 비교이며 긴 collisionless z20→4에 대한 정확성 근거가 아니다. C21M의 이미 계산된27점에서 같은 진단을 적용할 때도 exact coupled trajectories는 그대로 유지하며 mixed interaction residual을 따로 측정한다. 이 방법으로 실제 적분하지 않은 점을 완료 science로 표시하지 않는다.

REI213/BASS176의 bounded dispatch와 per-group immutable preparation, species work/cancellation bookkeeping은 운영 설계와 provenance 분리에 참고했다. 두 repo의729는 동일 실행이며 두 번 세지 않았다.

## 현재 채택하지 않은 변경

| 후보 | 판단 | 다음에 필요할 구체 근거 |
|---|---|---|
| reduced40→8 solver 직접 교체 | 별도 source lane로 보류 | 새 A/k domain에서 원40와 원하는 전체 출력 계약의 동등성; hidden state 재구성 검토 |
| SIMD/Numba/C++/GPU kernel 이식 | 현재 pilot 필수 아님 | reduction/FMA/함수평가 순서 변경의 물리·수치 영향과 실제 설치 환경 |
| FP32/mixed precision, tolerance 완화 | 미채택 | 원 accuracy contract를 바꾸므로 이번 최적화 범위에 부적합 |
| 분포 고정 후 A scalar만 변경 | 금지 | source packets와 normalization이 바뀌지 않아 다른 초기 물리를 계산하는 오류 |
| exact coupled dynamics를 axis surrogate로 치환 | 미승인 | local mixed residual 평가 및 별도 prospective 검증; 현재 retrospective 잔차는 global bound 아님 |
| 공통 reusable mutable RHS buffer | 미구현 | solver가 이전 배열을 참조하는지 확인하고 aliasing 없는 계약 보장 필요 |
| 64 worker 고정 발사 | 미채택 | CPU55·coordinator·quota·다른 owner lease·유휴load·메모리·남은 작업 수를 반영해야 함 |

## 자원 정책

한 worker의 계획 예산512 MiB는 quadrature buffers와 저장 trajectory의 명시적 크기 약1.43MB, Python/NumPy/SciPy 및 여유를 포함한 보수적 admission 값이다. coordinator256 MiB와 max(1 GiB, 관측 memory limit/8) reserve를 별도로 계산한다. 이는 강제 per-process limit이나 측정된 최악값의 증명이 아니다. 실행 중 실제 RSS high-water와 thread 설정을 receipt에 남긴다.

명목64 logical CPU가 모두 보이고 quota·memory가 충분하더라도 CPU55 하나와 coordinator 하나를 제외하면 science worker 상한은62다. 다른 작업이 있으면 그 안에서 줄여 실행한다. 공유 lease는 같은 directory를 쓰는 실행자 사이의 협조 장치이며, 관리되지 않은 프로세스를 종료하거나 스케줄을 바꾸지 않는다. 부하 증가 시 새 dispatch를 줄이고 완료된 결과를 보존한다.

현재 NCP는 접속하지 못했으므로 nominal 사양을 observed capacity로 기록하지 않는다. source/tested-content commit 고정, create-only output, explicit grid, site와 hostname 분리, known-unstarted-only resume까지 준비했다. 이 단위의 물리적 완료는 sandbox27 pilot으로 판정하고, 추가98 NCP refinement는 선택 후속 노드로 남긴다.
