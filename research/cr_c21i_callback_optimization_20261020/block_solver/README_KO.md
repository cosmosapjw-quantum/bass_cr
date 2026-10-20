# C21I 구조화 JVP·Schur 선형대수 구현

이 디렉터리는 C21H의 실제 Jacobian 구조를 사용하는 **의존성 없는 Rust 선형대수 prototype**이다. 구조화 JVP와 Schur solve를 구현하고 제조 행렬에서 검증·측정했다. C21H의 VigilODE/Diffsol backend에는 아직 연결되지 않았다. `native_chemistry=NOT_RUN`, `native_performance=NOT_EVALUATED`, `global_error_bound=null`이다.

## 식과 구현

독립변수는 C21H와 같은 `x=ln(a)`이고, 상태 순서는 `(tau[M], gas[G], ledger[15])`다. 정확한 Y=0 축소에서는 G=2, 일반 H/He 상태에서는 G=4를 사용한다. 제공된 Jacobian의 구조는 다음과 같다.

\[
J=\begin{pmatrix}0&A&0\\B&C&0\\P&Q&0\end{pmatrix}.
\]

`BlockJacobian::new`는 row-major A/B/C/P/Q를 소유하고 차원·finite 값을 검사한다. 상태의 모든 M+G+15 성분을 유지한다. `jvp_into`는

\[
Jv=(Av_g,\;Bv_\tau+Cv_g,\;Pv_\tau+Qv_g)
\]

를 caller가 소유한 출력 배열에 쓴다. 성공 시 모든 성분이 갱신되며 passive ledger의 **입력 열이 0인 구조**와 장부 **출력 행**을 구별한다. `jvp`는 필요한 출력 배열을 할당하는 편의 함수다.

`solve_shifted`는 무차원 수치 shift σ에 대해 `(I−σJ)k=b`를 계산한다.

\[
S=I_G-\sigma C-\sigma^2BA,\qquad
S k_g=b_g+\sigma B b_\tau,
\]
\[
k_\tau=b_\tau+\sigma A k_g,\qquad
k_\ell=b_\ell+\sigma P k_\tau+\sigma Q k_g.
\]

`SchurFactor::new`는 G×G의 S만 조립하고 partial-pivot LU를 수행한다. 구현은 각 항 `(σ B_ik)(σ A_kj)`를 cohort 순서로 누적한다. `solve_factored`가 현재 RHS와 현재 P/Q로 tau·장부를 복원한다. 가스 Jacobian의 FD truncation error는 이 선형대수 변환으로 바뀌지 않는다.

`backward_error`는 **전체 M+G+15 공간**의

\[
\eta=\frac{\|(I-\sigma J)k-b\|_\infty}
{\|I-\sigma J\|_\infty\|k\|_\infty+\|b\|_\infty}
\]

를 계산한다. 기본 수용 기준은 `eta <= 1e-13`이다. 분모·잔차가 모두 0인 영문제는 η=0이다. 입력이 finite여도 중간 산술이나 분모가 표현 범위를 넘으면 명시적인 `NonFinite` 오류를 반환한다. 무한 분모로 나누어 잔차를 0으로 만드는 처리는 없다.

정확히 0인 pivot은 `Singular`다. 근접 특이 행렬에는 `schur_rcond_inf`를 반환하며, caller가 `minimum_schur_rcond`를 지정한 경우에만 그 기준으로 `IllConditioned` 오류를 반환한다. 이 값은 G개 단위벡터 solve로 계산한 `1/(||S||∞ ||S^-1||∞)`이고 **S의 condition 진단**이다. 작은 backward error가 ill-conditioned 전체 선형계의 작은 forward error를 보장하지 않는다. Regularization, clipping, floor, heuristic stale Jacobian, silent fallback은 구현하지 않았다.

## Exact factor cache의 의존성

`ExactFactorCache`는 S의 factor 하나만 보관한다. Key는 M/G/L, σ의 `to_bits()`, **A/B/C 모든 원소의 `to_bits()`**다. Hash collision에 의존하지 않고 전체 bit sequence를 비교한다. `+0.0`과 `-0.0`도 다른 key다. 저장량은 한 entry로 제한된다.

P/Q와 RHS가 key에 없는 이유는 factor 대상이 S이기 때문이다. S의 식에 이 값들이 나타나지 않고 `det(I−σJ)=det(S)`다. 각 호출은 현재 P/Q와 RHS로 장부를 다시 복원하고 전체 residual을 다시 확인한다. 따라서 P/Q 또는 RHS만 달라지면 **동일한 S factor**를 재사용할 수 있다. 이 cache는 원 RHS, 전체 Jacobian, 전체 해, provider/native 응답을 저장하지 않는다. 원 RHS cache에 필요한 source/epoch/cell/provider 의존성을 이 선형대수 artifact에 혼동해서 적용하지 않는다.

새 factor 계산이 실패하면 그 실패를 cache하지 않고 기존 정상 entry를 유지한다. 통계는 유효 factor 요청, hit, factorization 시도, factorization 실패를 구별한다. 여기서 유효 요청은 RHS·shift·옵션 검사를 이미 통과한 factor 요청이다. 해의 residual 실패와 factorization 실패는 서로 다른 단계다.

## Scaling과 실제 solver 연결 범위

고정 양의 D에서 `u=Dz`이면 각 블록은 행 scale의 역수와 열 scale을 적용한다. 예를 들어 `A_z=D_tau^-1 A_u D_g`, `P_z=D_ell^-1 P_u D_tau`다. `S_z=D_g^-1 S_u D_g`이므로 같은 선형계의 해는 `k_z=D^-1 k_u`로 대응한다. 이 대응을 G=2/4 및 전체 장부 성분에서 검사했다. Normwise backward error는 좌표에 따라 값이 달라질 수 있으며, C21H의 원 WRMS·accepted state·물리 수지는 그대로 별도 계약이다.

현재 `C21H_V1`는 dense Jacobian JSON을 전달하고, pinned backend는 자기 선형해법을 사용한다. 본 구현의 API를 그 경로에 넣는 작업은 별도다. 직접 연결하려면 A/B/C/P/Q 추출/전송, 호출자의 shift, 모든 stage RHS, 실패 반환, 원래 full-state error norm의 소유권을 실제 backend hook에 연결해야 한다. 현재 C21H ordering의 half-bandwidth25를 FixedWidth2로 대체하지 않았다. 새 VigilODE PR을 import하거나 C21H의 pin을 변경하지 않았다.

## 실행한 검증

실제 Rust1.94.1 release compile와 **12개 test 계약**이 첫 실행에서 통과했다. 최초 실행 로그는 `evidence/attempt_01/`에 있다. 기존 C21H 테스트는 실행하지 않았다.

- 해석적으로 정한 tau/gas/ledger 해와 모든 장부의 보존.
- 구조화 JVP와 전체 dense matvec, caller 출력 전체 갱신.
- G=2/4, M=0/1/9/64, 양·음·0 shift에서 full dense LU와 독립 augmented row elimination 비교.
- G=2/4의 여러 row pivot.
- RHS/P/Q 변경 시 factor reuse와 현재 장부 복원.
- A/B/C **모든 key 원소**의 1 ULP 변경, shift 1 ULP, signed zero, 차원 변경, clear.
- 정확한 singular rejection, 가까운 singular case의 condition 진단과 caller 지정 거절 기준.
- 전체 상태의 양의 대각 scaling 대응.
- 각각의 15개 장부를 고의로 손상했을 때 full residual 검출.
- Shape, finite 입력, arithmetic overflow, 잘못된 옵션의 명시적 오류.

서로 다른 floating-point 경로의 해 비교 기준은 `5e-13*(1+|dense_i|)`, scaling 대응은 `5e-12*(1+|expected_i|)`였다. 이 값은 본 선형대수 계약의 비교 기준이며 C21H의 native 적분 rtol/atol을 변경하지 않는다.

## 경량 benchmark 결과

입력은 LCG로 생성한 고정 제조 행렬 6개, M=9/64/256×G=2/4, L=15, σ=0.7이다. 각 입력의 원소별 binary64 bits를 CSV로 보존했다. 두 방법의 같은 입력·shift·full residual 기준을 사용하고 iteration마다 실행 순서를 교대로 배치했다. Worker1, CPU0 affinity였으며 독점 CPU 할당은 아니다.

`cold_factorization`은 매 호출에서 새 factorization을 한다는 뜻이며 CPU cache를 flush한 측정은 아니다. Structured 경로는 Schur 조립·factorization·condition 진단·solve·전체 residual을, dense 경로는 dense W 조립·scalar partial-pivot LU·solve·같은 전체 residual을 포함한다. `warm_reuse`는 동일 행렬의 factor를 재사용한다. Schur의 전체 bit key 검사는 시간에 포함되고 dense 쪽은 benchmark가 고정한 immutable factor를 직접 재사용한다. 입력 생성과 출력 파일 쓰기는 kernel 시간에서 제외했다. 첫 warm setup 비용은 따로 기록했다.

아래는 각 cold5회, warm20회의 **중앙값 [μs]**다. 전체 반복값·min/max·표준편차는 `evidence/BENCHMARK_SUMMARY.json`과 raw CSV에 있다.

| M | G | Schur cold | Dense reference cold | Schur warm | Dense reference warm |
|---:|---:|---:|---:|---:|---:|
| 9 | 2 | 1.252 | 8.813 | 0.511 | 0.892 |
| 64 | 2 | 2.835 | 161.815 | 2.414 | 6.134 |
| 256 | 2 | 12.059 | 6872.874 | 14.026 | 67.667 |
| 9 | 4 | 2.243 | 14.883 | 1.252 | 1.422 |
| 64 | 4 | 6.269 | 252.271 | 5.002 | 7.746 |
| 256 | 4 | 21.342 | 8632.595 | 18.133 | 69.480 |

이 dense comparator는 검증용 scalar 구현이다. Faer/LAPACK, VigilODE/Diffsol, 전체 ODE/native 실행의 speedup으로 옮기지 않는다. 작은 행렬의 0.1–1μs 측정과 scheduling outlier는 raw 분산과 함께 읽는다. M256/G2에서는 별도 phase의 cache warm 중앙값이 cold보다 컸다. Cache가 항상 이득이라는 결론을 채택하지 않는다. 실제 C21H의 Jacobian/shift 재사용 분포는 이 고정 행렬 실험에서 측정되지 않았다.

Preallocated JVP도 같은 6개 입력에서 각 방법20회씩 비교했다. Dense/structured 중앙값 비는 1.39–12.18이었다. 보존된 240개 JVP 출력은 각 입력 내에서 bitwise 일치했다. 312개 선형 solve 기록의 최대 보고 backward error는 `9.19443718189947e-16`, dense 대비 최대 성분 차이 `|difference|/(1+|dense|)`는 `7.178140495689429e-16`이었다.

분석기는 보존된 동일 출력 12개를 identity로 묶어 Python `math.fsum`으로 full residual을 독립 재계산했다. 일반 정리의 근거는 Schur 유도이며 이 유한 행렬 검사는 구현·부호·ordering에 대한 근거다. 전체 실행 process 시간은 약0.128s, 최대 child RSS는6996KiB였다. 이 peak는 방법별 독립 메모리 측정이 아니다.

별도 검토자는 Rust source와 기존 raw를 읽고 exact binary64 입력을 100자리 Decimal로 옮겨 full residual을 다시 계산했다. 최대 backward error는 `9.459365491798048e-16`이었다. 서로 다른 residual 산술에서 나온 이 값과 생산자 binary64 값은 구별한다. 검토자는 새 Rust/native/benchmark를 실행하지 않았고, 현재 source에서 수정할 결함을 발견하지 못했다. 검토 문서·계산 script·실제 raw는 `evidence/independent_review_01/`에 원 바이트 그대로 보존했다. Decimal 결과는 directed-rounding enclosure 또는 전역 오차상계가 아니다.

구조화 행렬의 원소 수는 `2MG+G²+15M+15G`이고 dense는 `(M+G+15)²`다. 예를 들어 M256/G2는4898 대74529개의 f64다. 이는 matrix payload 계산이며 cache key·factor·출력 scratch·allocator overhead는 별도다.

## 재현

Crate는 외부 dependency가 없고 Cargo.lock을 포함한다. 실제 현재 호스트에서는 bundled rust-lld의 executable mode 문제가 있어 `RUSTFLAGS='-C linker-features=-lld'`로 system linker를 선택했다. 환경 특이 수정의 원래 실패·교정은 상위 C21I runtime 기록에 있다. NCP에 같은 문제가 존재한다고 가정하지 않는다.

```bash
RUSTFLAGS='-C linker-features=-lld' cargo test \
  --manifest-path /ABS/PATH/block_solver/Cargo.toml \
  --target-dir /ABS/NEW/BUILD_DIR --release --locked --offline --jobs 1 \
  --test contracts -- --test-threads=1

RUSTFLAGS='-C linker-features=-lld' cargo build \
  --manifest-path /ABS/PATH/block_solver/Cargo.toml \
  --target-dir /ABS/NEW/BUILD_DIR --release --locked --offline --jobs 1 \
  --bin block-benchmark

taskset -c ADMITTED_CPU /ABS/NEW/BUILD_DIR/release/block-benchmark /ABS/NEW/OUTPUT_DIR

python3 /ABS/PATH/block_solver/analyze_benchmark.py \
  /ABS/NEW/OUTPUT_DIR /ABS/NEW/SUMMARY.json
```

`block-benchmark`는 새 output directory만 생성하며 기존 경로를 덮어쓰지 않는다. 분석기도 새 summary 파일만 쓴다. 현재 native pilot의 게시 guard, fixture별 예산, 보호 CPU55, worker1, parent receipt/source 검사는 기존 C21H 계약에서 유지한다.

## 완료 상태와 후속 경계

`evidence/THEORY_CODE_MAPPING.json`은 식·함수·검증을 연결하고, `evidence/IMPLEMENTATION_RECEIPT.json`은 실행 identity와 범위를 기록한다. `evidence/BLOCK_DAG.json`은 이 standalone kernel에 한정한 DAG다. 디렉터리의 `MANIFEST.json`은 자신을 제외한 모든 payload의 SHA256을 기록한다.

| 실행 | 게시 | 백업 | DAG |
|---|---|---|---|
| 새 Rust12계약 PASS; 제조 block benchmark312 solve/240 JVP; 독립 기존 raw 검토 완료 | 이 subtask의 GitHub write0; 상위 게시 영수증에서 실제 commit/ref/PR 확인 | 이 subtask의 provider ACK 없음; 상위 create-only 전달 영수증에서 확인 | 이론→구현→계약검사→kernel측정→독립검토 완료; C21H backend 연결·native 성능 미완료 |

이 표는 파일 제작 시점의 subtask 상태이며 상위 최종 게시·백업 영수증이 이후 전달 상태를 정한다.
