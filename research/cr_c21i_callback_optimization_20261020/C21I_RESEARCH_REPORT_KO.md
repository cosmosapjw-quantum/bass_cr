# C21I: 원 광학깊이 방정식의 callback 비용 축소

## 결과와 적용 범위

이 단위는 C21H의 원 RHS·event driver·정확한 Y=0 축소·15개 장부·오차 척도를 그대로 사용하면서, cohort Jacobian의 Python 반복과 중복된 원 RHS 계산을 줄인다. 실제 구현은 `optimized_adapter.py`, native 성공값 재사용의 출처·수명 계약은 `native_cache_contract.py`, 실행 연결은 `run_optimized_pilot.py`다. 별도 `block_solver/`에는 구조화 JVP와 Schur 선형해법을 구현했다. 이 Rust 커널은 현재 C21H backend에는 연결하지 않았다.

현재 게시 상태의 권위는 `PUBLICATION_RECEIPT.json`, 보존 상태는 `BACKUP_RECEIPT.json`과 최종 외부 delivery receipt, 연구·실행 상태는 `DAG_C21I.json`이다. 로컬 commit과 원격 GitHub content commit을 구분한다. 현재 C21H/PR85 content `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`와 C21I/PR86 content `fe6bbaec2de5032b938aed0713623b9618ba70e6`의 실제 게시를 확인했다. 이전 `user rejected MCP tool call`과 미게시 기록은 해당 시점의 역사이며 유지한다. 새 C10은 문서 호환·게시·보존 마감만 수행했고 runtime 및 과학 실행을 추가하지 않았다.

`native_chemistry=NOT_RUN`, `native_performance=NOT_EVALUATED`, `global_error_bound=null`이다. Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity의 HOLD를 유지한다.

## 1. 기준점과 새 결과 회수

C21G PR84의 현재 확인 head는 `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5`, tree는 `6d04c1d1f33b2f54b9cf8186de0a81ed059cf54d`다. C21H의 8개 runtime 파일은 manifest SHA256 `7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb`에 묶여 있고 이 작업에서 변경하지 않았다. C21F의 복구·게시와 그 이후 PR82/83의 native 결과, C21G PR84의 게시·백업은 완료된 근거로 재사용했다. C21G의 새 reference ladder는 마지막 범위 한정 조회에서 NOT_RUN이다.

이번 환경에서는 원 과학 ZIP을 정확한 바이트로 복원하고, 후속 delta의 base hash가 일치하는 문서에만 변경분을 적용했다. 원 science ZIP과 기존 test/raw를 덮어쓰지 않았다. 새 Rust1.94.1에서 공개 Git pin과 고정 Cargo.lock을 유지한 실제 locked build도 완료했다. 현재 bridge SHA256은 `202f4d93b94602f6649f427237afd6513b8fd933ae828cbd7a3cc1e90f7af934`이며, 이전 제조 검증의 binary `a11d3ab0…`와 별도다. 현재 환경의 rust-lld 실행 mode 문제는 system linker 선택으로 교정했고, 원 실패 로그를 보존했다. 이 환경 수정을 NCP 기본 설정으로 옮기지 않는다.

2026-10-20 06:03–06:09 UTC 새 조회에서는 REI PR198·199의 실제 최적화 source와 측정이 추가됐다. PR198 head `33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1`은 Jacobian 안의 photon cell 준비를 재사용하며, 받은 15 paired observations에서 실제 RHS와 node visit 수는 유지되고 preparation 작업량이 줄었다. 해당 최적화의 NCP는 NOT_RUN이다. PR199 head `cf00684741eb612e35f987713c28937513d44d57`은 고정 57,344-node 선형 endpoint/age 모델이다. 비선형 ODE나 cosmological history 실행이 아니며 새 age32 native가 아니다. 새 primary 19개 수신 파일의 Git blob이 일치했다. 전체 이전 raw의 재분석으로 확대하지 않았다.

VigilODE production과 PR73/74/75의 head는 이전 관측 그대로였다. PR73의 FixedWidth2·exact LU cache, PR74/75의 supplied JVP·residual-first·stage 병렬 조건을 검토했으나 C21H의 pin `8a8bd409b1d96c7b7421f496d229e119fd3d284e`는 유지했다. source mapping은 `evidence/current_intake/addendum_20261020T065246Z/SOURCE_OPTIMIZATION_MAPPING_KO.md`에 있다. Drive의 정확한 folder 목록은 알려진 항목이 있는데도 빈 결과를 반환했으므로 부재 근거로 사용하지 않았다. Dropbox·Library의 조회 범위와 페이지 종료, Drive의 직접 ID metadata를 따로 보존했다.

## 2. 식에서 직접 연결한 최적화

독립변수는 \(x=\ln a\), 상태는 \(u=(\tau,g,\ell)\)다. \(N_i=A_i e^{-\tau_i}\), \(\tau_i'=\lambda_i/H\)를 유지하며, Y=0일 때만 두 He unknown을 제거해 gas 차원이 2가 된다. Y>0이면 4다. 장부 15개는 물리 상태와 accepted output에 모두 남는다.

원 callback은 tau 열을 cohort마다 조립한 뒤 full 행렬을 축소한다. 새 경로는 같은 \((M,3)\) species와 길이 M heat 배열을 사용해 축소 행렬에 직접 쓴다. species 축의 합산은 원래와 같은 길이 3의 순서를 유지한다. 고정 양의 대각 \(u=Dz\)의 \(J_z=D^{-1}J_uD\)에서도 원 곱셈 후 나눗셈 순서를 유지한다. matrix scratch는 cell이 소유하며 매 요청에서 전체를 0으로 초기화한다. 반환값은 독립 사본이므로 다음 요청이 이전 결과를 덮어쓰지 않는다.

가스 열과 시간 편미분은 원 RHS의 실제 표현 가능한 허용 노드를 그대로 쓴다. gas simplex·cell corner·clamp 규약을 변경하지 않는다. Clipping, floor, zero-derivative fallback, stale Jacobian은 추가하지 않았다. 기존 population 대조 경로와 log-survivor·underflow 기록도 유지한다.

## 3. 정확 RHS 재사용의 조건

cache는 한 cell callback 수명에 한정한 최대 16-entry LRU다. key는 **실제 t와 physical u 전체의 little-endian binary64 바이트**다. signed zero와 1 ULP 차이를 구별한다. source·provider·fixture·birth·active set·cell·D·dynamic ordering은 생성 시 고정한 scope에 묶는다. 다른 cell이나 바뀐 fixture에서 같은 cache를 쓰지 않는다.

성공한 finite 결과만 소유 사본으로 저장한다. 예외·timeout·부분 결과를 저장하지 않는다. Hit도 물리 영역·one-job deadline·provider 생존·고정 scope 검사를 통과해야 한다. `original_rhs_requests`, hit, miss, 실제 원 RHS 평가, 실제 native calls를 구분한다. hit에 대해 native 로그나 call count를 만들어내지 않는다.

제조 provider는 고정 source의 정확한 stateless class만 자동 허용한다. Native 경로는 고정 owner `cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`의 실제 소스에서 같은 EVAL 입력이 fresh state와 결정적 상수 계산으로 연결됨을 읽고, 실제 provider class/instance/process/config/binary provenance를 admission에 묶는다. Admission SHA 검사, 매 guard의 파일 metadata·path lease, 종료 전 전체 SHA 재검사는 서로 다른 검사다. 매 callback마다 binary 전체를 hash했다고 표시하지 않는다.

실제 call cap의 N번째 성공은 허용한다. `calls==max_calls`의 exact hit는 새 native 실행이 아니므로 허용하고, N+1 miss는 원 NativeMicro가 거절한다. One-job wall deadline과 폐쇄·종료 process 검사는 hit에서도 유지한다. 이 native guard의 비용은 가벼운 제조 provider benchmark에 포함되지 않으므로 native 가속률은 별도 실제 실행에서 측정해야 한다.

## 4. 비용 구조와 새 cache가 줄이는 것

전체 비용은 원 RHS/native 계산, Jacobian·시간 편미분을 위한 추가 RHS, 배열 조립/복사, JSONL 변환·왕복, 선형 factorization/solve, rejected step·fallback, 프로세스 준비·종료로 나눈다. 일부 callback의 시간 counter를 합해 전체 wall time의 완전한 분해라고 부르지 않는다.

보존된 H 제조 trace에서 VigilODE는 RHS RPC216, Jacobian27, 시간 편미분27을 요청하고 실제 원 RHS423회를 계산했다. 27개 shared base의 중복을 정확 재사용하면 51회를 줄일 기회가 있다. Diffsol은 실제 원 RHS74회 중 3회의 shared base 기회가 있었다. 이는 보존된 원 trace에서 도출한 예측이며, 이번 같은 binary의 32개 전체 제조 실행에서 같은 step/grid와 실제 감소량을 확인했다. Jacobian RPC나 dense JSON 전달 자체는 이 cache로 줄지 않는다.

원 RHS 한 번의 비용을 \(c_F\), 실제 절약 횟수를 \(h\), 새 guard·lookup·copy 비용을 \(C_{new}\)라 하면, 다른 경로가 같을 때 순 절약은 \(h c_F-C_{new}\)다. 이 식의 부호는 관측으로 정한다. 제조 RHS가 싸거나 hit가 적으면 cache가 느릴 수 있다. 프로세스/JSONL 비용이 우세하면 kernel 가속이 전체 시간에 작게 반영된다.

Allocation counter는 callback에서 명시적으로 만든 scratch·반환 사본·cache payload의 범위다. Python·NumPy 내부 임시 배열·allocator·전체 RSS의 완전한 계측이 아니다.

## 5. 구조화 JVP와 Schur 커널

제공된 Jacobian의 구조는

\[
J=\begin{pmatrix}0&A&0\\B&C&0\\P&Q&0\end{pmatrix},\qquad
Jv=(Av_g,\;Bv_\tau+Cv_g,\;Pv_\tau+Qv_g).
\]

\((I-\sigma J)k=b\)에서

\[
S=I_G-\sigma C-\sigma^2BA,\quad
Sk_g=b_g+\sigma Bb_\tau,
\]
\[
k_\tau=b_\tau+\sigma Ak_g,\qquad
k_\ell=b_\ell+\sigma Pk_\tau+\sigma Qk_g.
\]

직접 역대입과 \(\det(I-\sigma J)=\det S\)를 유도했고 Wolfram으로 검산했다. Wolfram의 context 오류와 evaluator의 `FullSimplify::cas` 경고도 원문으로 남겼다. 별도 stdlib 유리수 계산은 부호·shift·G2/G4·scaling·singular case를 확인했다. 이 검산은 수식의 전제를 대체하지 않는다.

Rust 구현은 G×G partial-pivot LU, 모든 tau·장부 복원, 전체 공간의 backward residual을 사용한다. S에만 의존하는 factor cache의 key는 M/G/L·shift bits·A/B/C 전체 bits다. P/Q/RHS는 S의 인자가 아니므로 key에서 제외하되 매번 현재 값으로 장부를 복원하고 전체 잔차를 검사한다. 이 범위가 전체 RHS cache나 전체 Jacobian cache와 다름을 명시했다.

G≤4와 장부15를 고정하면 저장·JVP·Schur 조립/복원 비용은 M에 선형이다. 작은 26차원 C21H에 실제 이득이 생기는지는 backend hook·JSONL·실제 shift 분포에 달려 있다. 현재 n=26 trace의 half-bandwidth가25이므로 FixedWidth2를 직접 적용할 수 없다. 현재 prototype을 NCP에 새 solver 구현 과제로 넘기지 않는다. 이후 실제 프로파일이 요구하면 여기서 backend 연결·검증을 별도 수행한다.

## 6. 실제 경량 검증과 관측

| 대상 | 완료 근거 | 정확한 해석 |
|---|---|---|
| Optimized callback | 18개 고유 계약 scoped PASS | 수정된 영향 범위 재검사 포함; 최종18개 한 번의 새 전수 실행으로 표시하지 않음 |
| Native cache admission | 현재14/14 focused stub PASS, 독립 source/raw review | 실제 native 실행0 |
| Rust block | 실제 release build,12/12 contracts PASS | standalone 제조 선형대수 |
| Block benchmark | 312 solve records,240 JVP records | scalar dense reference와 비교; Faer/LAPACK/backend 속도로 전용하지 않음 |
| 독립 block residual | 12개 unique 출력의100자리 Decimal 재계산 | 최대 backward error9.459365491798048e−16; directed bound 아님 |
| Callback components | 216 batches,432 independent tasks,3,888 outputs | 실제 원 RHS closure 사용, 모든 출력과 FD노드순서 bitwise 일치; ODE/native0 |

빈 cache에서 서로 다른 세 점을 쓰는 serial component batch의 paired 배속 중앙값은 다음과 같다.

| M / gas | vectorized | vectorized_exact |
|---|---:|---:|
| 9 / 2 | 1.005 | 1.257 |
| 9 / 4 | 0.855 | 1.250 |
| 64 / 2 | 1.223 | 1.403 |
| 64 / 4 | 1.153 | 1.250 |
| 128 / 2 | 1.189 | 1.487 |
| 128 / 4 | 1.133 | 1.487 |

같은 점을 반복한 warm exact의4.82–11.19배는 timed RHS 실제 호출0인 의도적 최선 조건이다. 실제 trajectory의 hit율로 채택하지 않는다. Threadpool 생성·제출·join·종료를 포함한2-worker 비교에서는36묶음 중31묶음이 느렸다. 108개 batch 중99개는 실제 worker2개,9개는 lazy scheduling으로1개가 처리했다. 따라서 병렬 worker 자동 증설은 채택하지 않았다. 상세 원시와 읽기 전용 재계산은 `evidence/component_benchmark_01/`, `evidence/component_analysis_01/`에 있다.

### 같은 새 Rust binary의 전체 제조 적분

같은 새 binary에서 두 backend×네 mode×네 순서 교대 관측의 **32 jobs가 모두 COMPLETE**였다. source 전후 identity, 원 H 대비 accepted trace·물리량·독립 수지·FD 노드·Rust 작업 counter의 binary64/구조 비교가 전부 일치했다. 전체 process wall 합은35.485946871초다. 실제 적분 CPU2·monitor CPU3,worker1이며 독점 할당은 아니다. 최초 관측1회와 이후 fresh process3회는 OS cache를 flush한 cold/warm 실험이 아니다. 원 H와 I instrumented baseline을 구분했다.

| Backend | accepted steps/job | 원 H 실제 RHS | I exact 실제 RHS | 후반3 paired process 배속: vectorized | 후반3 paired process 배속: exact |
|---|---:|---:|---:|---:|---:|
| VigilODE Rodas5P |27|423|372|0.845647|0.920985|
| Diffsol BDF |53|74|71|1.045230|0.985440|

배속은 같은 round의 원 H process wall을 해당 I process wall로 나눈 비율의 중앙값이다. Exact cache의51회/3회 실제 RHS 감소는 모든 반복에서 관측했다. **이 작은 문제에서 일관된 전체 가속은 확립하지 못했다.** 시작·source 검사·JSONL·guard·scheduler 비용과 작은 반복 표본을 포함한 결과다. Callback 성분의 이득으로 이 표의 음성 결과를 대체하지 않는다. 실제 source/명령/모든 반복 raw와 실패 회계는 `evidence/paired_pilot_final/`, 별도 읽기 전용 분석은 `evidence/paired_pilot_analysis_01/PAIRED_PILOT_REPORT_KO.md`에 있다.

새 실행기의 실제 FD 부모 연결은 matching exact-mode base에서 backend별 한 번씩, **2/2 COMPLETE**였다. 두 explicit derivative probe만 절반으로 줄였고 rtol/alpha는 유지했다. 양쪽 gas와 temperature endpoint 차이는0; VigilODE의 최대 안정적인 photon 차이는6.166244974933198e−22/H, log-survivor 차이는4.404571325722362e−20, Diffsol은 둘 다0이었다. 이는 짧은 제조 fixture의 차분 민감도이며 정확도 상계가 아니다. 부모의 source/receipt/raw를 실행 전후 확인했고 I source3/manifest는 변경되지 않았다. 해당 기록은 `evidence/optimized_fd_followup_01/`이다. 새34개의 실제 적분에서 native chemistry 호출은0이다.

## 7. 채택 판단과 다음 단계

벡터화와 정확 성공값 재사용은 서로 구분되는 실행 옵션이다. Default는 vectorized이며 exact mode는 명시적 선택이다. 현재 변경은 원 함수를 유지하는 callback 구현 후보로 채택한다. 모든 입력의 배속, native 수렴, 전역 오차를 주장하지 않는다. 실제 측정에서 느린 범위는 raw와 함께 유지한다.

VigilODE PR74/75의 autonomous fixed-step 경로로 가려면 clock 상태 \(\xi'=1\)와 \((0,F_xv_\xi+Jv_z)\) JVP의 사상이 필요하다. 물리 n차원 WRMS를 n+1로 바꾸면 clock 오차0이어도 척도가 변하므로 원 norm을 보존해야 한다. Adaptive trajectory·event landing·dense output을 구현하지 않은 상태에서 기존 API의 대체로 사용하지 않는다. 원 채널의 mutex 아래 stage thread만 늘려도 Python/native 호출이 병렬화되지는 않는다.

NCP에는 현재 자원·기존 결과 조사, 실제 배정 CPU, 정확한 published content checkout, locked compile, 관측된 작은 호환 수정, bounded native 실행을 남긴다. NCP가 새 Schur solver·physics 기능을 처음부터 구현하도록 하지 않는다. 원 H native4base+성공별fd_half 및 기존 G ladder의 계약은 독립적으로 유지한다. C21I의 명시적 mode는 source identity에 포함되므로 다른 mode의 base를 FD 부모로 쓰지 않는다.

## 8. 원전과 코드 위치

- Steinebach, *Construction of Rosenbrock–Wanner method Rodas5P and numerical benchmarks within the Julia Differential Equations package*, BIT63(2023),27, DOI[10.1007/s10543-023-00967-x](https://doi.org/10.1007/s10543-023-00967-x): 비자율 \(F_x\) 항과 method 조건.
- Tranquilli–Sandu, [Rosenbrock–Krylov Methods](https://arxiv.org/abs/1305.5481): Krylov 근사와 시간적분 차수 조건의 결합.
- Curtis–Niemeyer–Sung, [SIMD/SIMT chemical Jacobians](https://arxiv.org/abs/1809.01029): 독립 계산 축·배열 배치·실제 vector width의 측정 방법. 논문의 배속을 이 fixture로 이전하지 않았다.
- [NumPy2.3 ufunc](https://numpy.org/doc/2.3/reference/ufuncs.html), [thread safety](https://numpy.org/doc/2.3/reference/thread_safety.html), [SciPy1.17 BDF](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.BDF.html): allocation/worker 소유권과 작은 문제의 vectorization overhead.

SciSpace·Exa의 실제 응답, 원전/공식 source 읽기, Wolfram 코드/응답, 수식과 source/raw 독립 검토는 `theory/`에 보존했다. 문서·포장 상태와 수학·실행 결과를 별도 receipt로 연결한다.
