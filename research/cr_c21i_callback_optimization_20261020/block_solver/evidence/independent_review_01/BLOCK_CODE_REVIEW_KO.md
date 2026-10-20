# C21I Rust block companion 독립 source·raw 검토

2026-10-20. 판정은 **PASS_SCOPED: standalone 제조 선형대수 source와 저장 raw**다. 새 Rust/native/benchmark를 재실행하지 않았다. C21H bridge의 실제 linear solver에 이 companion을 연결한 결과로 해석하지 않는다.

## 검토 대상과 근거

block_solver의 Cargo.toml, Cargo.lock, src/lib.rs, src/bin/benchmark.rs, validation/reference.rs, tests/contracts.rs 및 완료된 benchmark_01 raw를 읽었다. runtime source 6개의 SHA는 기존 BENCHMARK_RUN_RECEIPT.json의 before/after와 일치하고 독립 읽기 전후에도 변하지 않았다. 그 전체 identity와 새 독립 계산은 raw/BLOCK_INDEPENDENT_RAW_REVIEW.json에 있다.

핵심 src/lib.rs SHA256은 82ed908a32e0c9d2d57decdcfbda8c05241f6f176b533f6ae6fd455ebff5ac67이다. benchmark binary SHA256 e0059fe109f9e99189a6048575f688c10fd1b7e6536e8840b663087adb89f41e는 생산자 영수증의 실제 바이너리이며 이 검토에서 다시 실행하지 않았다. 생산자의 12개 Rust 계약 검사와 신규 312 solve/240 JVP row를 분리해 읽었다. 독립 검산을 생산자의 Rust test count에 더하지 않는다.

## 1. 구현은 유도된 블록식과 연결된다

상태 순서는 tau M개, gas G개, ledger 15개이고 G는 2 또는 4다. source의 BlockJacobian은 A, B, C, P, Q를 소유하고 모든 입력의 길이·finite 값을 확인한다. 다음 행렬식을 구현한다.

$$
J=\begin{pmatrix}0&A&0\\B&C&0\\P&Q&0\end{pmatrix},\qquad W=I-\sigma J.
$$

JVP의 tau 결과는 Av_g, gas 결과는 Bv_tau+Cv_g, ledger 결과는 Pv_tau+Qv_g다. ledger 입력의 미분 열이 0이라는 사실과 ledger 출력이 존재한다는 사실을 구별한다. jvp_into는 caller가 제공한 전체 출력 버퍼를 모두 갱신하며 입력의 ledger 값도 finite/shape validation을 지난다.

SchurFactor::new는

$$S=I_G-\sigma C-\sigma^2 BA$$

를 G×G 배열에 만들고 partial-pivot LU로 분해한다. 코드에서는 각 항을 (σB_ik)(σA_kj) 순서로 계산하며 σ²를 먼저 만드는 underflow/overflow 경로를 피한다. 이것이 모든 유한 입력에서 연산 가능하다는 보장은 아니며, 표현 불가능한 intermediate는 오류다.

solve_factored는 S k_g=b_g+σ B b_tau를 푼 뒤 k_tau=b_tau+σ A k_g, k_ledger=b_ledger+σ P k_tau+σ Q k_g를 계산한다. 모든 ledger 행과 full-space residual을 복원한다. SmallLu는 factor 단계의 전체 행 교환을 기록하고 RHS에 같은 순열을 적용한 뒤 forward/back substitution을 수행한다. 읽은 다중 pivot 검사와 별도 augmented elimination 비교가 이 위험을 직접 다룬다.

이 구현은 gas 미분을 새로 근사하거나, error norm에서 ledger를 빼거나, photon/gas clipping을 넣지 않는다. 현재 companion에는 시간 적분기·accepted trajectory·event controller가 없다. 따라서 전체 ODE의 가속률·수렴·정확도는 이 source만으로 정해지지 않는다.

## 2. Factor cache에서 P/Q를 제외한 이유는 타당하다

캐시는 **S의 factor**만 저장한다. S는 M/G, σ, A/B/C의 함수이며 P/Q나 현재 RHS는 의존성이 아니다. FactorKey는 M/G/L, shift bit pattern과 A/B/C의 모든 binary64 bit pattern을 비교한다. 이 조건은 같은 factor를 재사용하기에 충분하고 signed zero도 구별한다.

P/Q 또는 RHS가 바뀌어도 현재 값을 solve_factored의 reconstruction과 full residual에 사용한다. source의 exact_cache_reuses_factor_with_new_rhs_and_current_pq 검사는 이 변화가 실제 ledger 해를 바꾸며 현재 dense reference와 일치하는지 확인한다. 이 경우 owner/fixture/time 등의 상위 과학 identity를 factor key마다 다시 넣을 필요는 없다. 이미 전달된 A/B/C/shift의 완전한 값 동일성이 저장 artifact의 실제 수학 의존성을 결정하기 때문이다. 이것을 Python RHS cache나 full Jacobian cache의 느슨한 key에 대한 근거로 확장하면 안 된다.

새 singular/nonfinite factor가 실패하면 성공한 이전 entry를 유지하지만, 이후 요청은 반드시 이전 exact key와 일치해야 hit가 된다. 실패 후보를 이전 factor로 푸는 fallback은 없다. options의 최소 rcond 조건은 hit에서도 다시 적용된다. 실패·요청·실제 factorization 시도 counter가 분리된다.

## 3. Full-space residual과 conditioning의 의미

backward_error는 tau/gas/ledger 모든 행에 대해 다음 값을 계산한다.

$$\eta=\frac{\|Wk-b\|_\infty}{\|W\|_\infty\|k\|_\infty+\|b\|_\infty}.$$

0/0은 residual도 0인 영 문제일 때만 0으로 반환한다. denominator 또는 중간 연산이 무한대가 되어 인위적으로 오차가 0이 되는 경우를 거절한다. 모든 ledger를 개별적으로 오염시킨 focused test는 해당 full residual이 이 오류를 감지하는지 확인한다. default gate는 η≤10^-13이다.

schur_rcond_inf는 G개의 단위 RHS solve로 계산한 S 역행렬의 infinity norm에서 나온다. 이것은 **S의 condition 지표**이며 W의 condition number나 solution forward error를 뜻하지 않는다. source는 근특이지만 유한한 solve를 기본적으로 보고하고, 사용자가 정한 최소 rcond 정책이 있으면 별도로 거절한다. singular pivot에 floor를 더하지 않는다. 이 범위를 유지하는 문서 표현이 적절하다.

## 4. 저장 출력에 대한 독립 계산

review_block_raw.py는 Rust 생산자 solver를 호출하지 않고 raw CSV의 binary64 hex와 십진 문자열이 같은 입력을 나타내는지 확인한다. 312개 solve row와 solutions.jsonl의 식별자·크기·순서를 대조한 결과 같은 M/G/method의 반복 출력은 bit pattern까지 동일했다. 서로 다른 출력은 12개였다. 따라서 12개만 재계산하여 동일 출력의 312개 row를 포괄했다.

독립 residual은 binary64 J와 shift를 정확한 실수 입력으로 옮긴 뒤 **100자리 Decimal**로 전체 W를 따로 조립해 계산했다. candidate의 순차 binary64 residual 코드를 복사하지 않았다. 모든 tau/gas/15 ledger 행을 포함했다.

| 항목 | 실제 관측 |
|---|---:|
| 저장 solve row | 312 |
| 독립 residual을 다시 계산한 고유 출력 | 12 |
| 최대 Decimal normwise backward error | 9.459365491798048×10^-16 |
| 실제 gate | 10^-13 |
| 저장 JVP 비교 row | 240 |
| paired JVP 최대 수치 차이 | 0 |
| 이 검토의 새 Rust/native/benchmark 실행 | 0 |

생산자 binary64 residual의 최대 9.19443718189947×10^-16과 독립 Decimal 값은 서로 다른 residual 산술에서 나온다. 두 값을 동일하다고 주장하지 않는다. Decimal 계산도 directed rounding으로 만든 검증 enclosure가 아니므로 전역 오차상계가 아니다. 다만 해당 저장 solution이 동일 입력 블록 선형식을 만족한다는 별도 수치 근거다.

M=9/64/256, G=2/4는 **제조 block matrix**다. M=256을 C21H 원 reference의 cohort 지원 범위가 확장됐다는 주장으로 옮기지 않는다. C21H backend에 대한 actual sparse-block extraction과 native RHS source 검증은 아직 별도 작업이다.

## 5. Benchmark 비교 범위

bench는 worker 1, 같은 제조 입력과 shift 0.7, paired alternating method order를 사용한다. cold는 매 solve의 조립·factorization 재실행이며 CPU cache flush가 아니다. warm은 같은 고정 matrix factor 재사용이고 Schur exact key 비교 비용을 포함한다. 양쪽 full residual을 timing에 포함한다. dense reference는 명시적인 scalar partial-pivot 구현이며 Faer/LAPACK 비교가 아니다. JVP는 양쪽 preallocated full output을 사용하고 비교 자체는 timer 밖이다.

원시 반복값·setup·출력·입력 hex·source/binary 영수증이 남아 있어 prototype 내 timing 비교는 가능하다. ODE/native 속도 우열, nonlinear trajectory의 cache hit율, stage 병렬 가속률은 여기서 측정되지 않았다. 작은 timing의 통계적 불확실성과 실제 환경의 비독점 CPU 조건은 별도 성능 보고에서 유지한다.

## 6. 독립 판정

현재 읽은 source와 raw에서 수정이 필요한 block 선형대수 결함은 발견하지 못했다. 채택 가능한 주장은 정확한 블록 구조를 전제로 한 standalone JVP/Schur solve 구현, 해당 제조 입력의 full residual scoped PASS, 그 artifact에 한정한 exact factor reuse다. 실제 C21H backend 통합과 native 성능은 NOT_RUN/NOT_EVALUATED로 유지한다.

| 실행 | 게시 | 백업 | DAG |
|---|---|---|---|
| 독립 source 검토와 기존 raw residual 재계산 완료 | 이 검토에서 GitHub write 0 | 새 검토 파일의 parent 전달 대기 | 이론→standalone 구현→생산자 제조 raw→독립 residual 확인 완료; backend/native 통합 노드는 미승격 |

global_error_bound=null.
