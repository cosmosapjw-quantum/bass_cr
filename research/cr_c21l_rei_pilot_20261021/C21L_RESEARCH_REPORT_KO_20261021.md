# C21L 연구·구현·실행 보고서: REI 초기 전단–응력 pilot

작성일: 2026-10-21 UTC. 저장소: `cosmosapjw-quantum/bass_cr`.

## 1. 이번에 얻은 결과

**non-tilted LRS Bianchi I의 초기 전단–비등방 응력 격자 81개를 실제 적분했고, 첫 preliminary plot 두 장을 만들었다.** REI PR147의 고정 Einstein–Boltzmann–Vlasov source를 재사용했다. 적분 상태는 case마다 40성분이고 101개 시점의 전체 배열을 저장했다. 81개 모두 완료됐으며 실패·미완료 case는 없다.

이 결과는 전체 non-tilted Bianchi I 가운데 축대칭 LRS 부분계, collisionless 가정, 아래에 고정한 초기 분포족에 대한 첫 pilot이다. 일반 삼축 계, H/He·전자 donor·UV·별 생성의 완전한 피드백은 포함하지 않았다. 기존 과학 HOLD와 `global_error_bound=null`을 유지한다. 샌드박스에서 실제 계산했으며 NCP 실행·NCP 성능은 각각 `NOT_RUN`, `NOT_EVALUATED`다.

실행한 v1 code와 이후 운영 수정한 v2 code를 구분했다. 원래 81개 결과·manifest·source는 그대로 보존했다. v2는 실행 장소 기록과 미시작 queue 재개를 수정한 실행기이며, 물리 adapter와 원본 방정식은 같다. v2로 81개를 다시 실행하지 않았다.

| 산출물 | 위치 |
|---|---|
| 최종 전단 크기 그림 | `runs/pilot81/plots/initial_norms_final_Sigma_F.png` 및 PDF |
| 최종 응력 크기 그림 | `runs/pilot81/plots/initial_norms_final_Pi_F.png` 및 PDF |
| 81개 endpoint | `runs/pilot81/endpoints_20261021T003909_5.csv` |
| 모든 raw 이력 | `runs/pilot81/cases/*/history.npz` |
| 초기조건·수치설정·실행 identity | `runs/pilot81/MANIFEST.json`, 각 `RESULT.json` |
| 직접 유도 | `THEORY_KO.md` |
| 판정과 독립 검토 | `SCIENCE_ADMISSION.json`, `review/` |
| 저장된 결과의 선형 응답 분석 | `SAVED_PILOT_RESPONSE_ANALYSIS.json` |
| 게시·백업의 최종 실제 영수증 | 별도 `C21L_PUBLICATION_CLOSEOUT_RECEIPT_20261021.json` |

## 2. 먼저 확인한 최신 외부 상태

연구를 시작하기 전에 다른 대화의 관련 기록, 7개 저장소의 branch metadata, 최근 PR와 고정 source/return, Library·Dropbox·Drive를 조사했다. branch 수는 bass_cr166, rei_bianchi253, BASS_HE86, WU088_HH135, bass260, vigilode183, rec_bianchi132로 합계 **1,215개**다. 이는 조사 시점에 API가 반환한 전체 branch metadata의 범위이며, 모든 오래된 PR의 본문과 모든 비공개 작업 디렉터리를 열었다는 뜻은 아니다. 상세 출처와 관측 시점은 `CROSS_PROJECT_STATUS.json`에 있다.

| 프로젝트 | 새로 확인·종합한 상태 | 이번 계산에 적용한 판단 |
|---|---|---|
| bass_cr C21K / PR89 | content `bab323983dad5206e162dbfdaefc167f2fabea45`, document `dc1c0c0721b74454958e5d16264c24ec465ba1d8`; 구현·검증·게시 완료 | 기존 연구를 미구현으로 되돌리지 않고 새 C21L의 부모로 사용 |
| REI PR198 | 최신 head `3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8`; native131 등의 반환과 전체 DAG246 중144완료/100cap-unrun/2blocked 구분 | 기존 실행을 중복하지 않고 오늘 그림에 필요한 실제 물리 계를 별도로 선택 |
| REI PR199 | 문서 `964b2e3c098f6e475999a4eddc7a6aa0f8f053cc`, 실행 source `4f13648985e417028c530892ea02be4f56018a31`; 시간8/16/32 실행 완료, convergence HOLD | 별도 수치 경로의 결과를 이번 물리 pilot의 정확도 근거로 혼합하지 않음 |
| WU PHYS73 / PR126 | head `367db1f18ed9e6ad5cd680e3dbd2a37ecdb0f049`; raw ZIP·ACK와4,681payload 확인,15완료+15재사용, 새 child0 | 오래된 ‘raw 미검증’ 기억을 갱신; 해당 과학 HOLD 유지 |
| REC U4B / PR114 | head `df95a074730ea0d13d609cf88d448f01f4a47ef1`;74,443→74,475의32 accepted steps, numerical restart scoped PASS | U5/U6·REI 활성화로 확대하지 않음 |
| HE | 고정 실행 source `802a32361288bf5aa0e0d1f63c912768f1a1d407`;4reference pairs+1canary 완료,182,280 native, queue empty | 완료 항목을 새 NCP backlog로 재등록하지 않음 |
| BASS S12 / PR174 | 최신 NCP 반환 ZIP metadata157,420,884bytes 확인 | 본 대화에서는 metadata-only;17개 작업 재실행이나 raw 과학 검증 완료로 승격하지 않음 |
| VigilODE | 실행 source `45a1a418bcee767da982b0283016d786cd4eab07`, 문서 `de4c10a9f41321beef2313a3d7fb503bab35d714`; N01–N08 변경 및 기록된 focused tests | 오늘 SciPy pilot에 대규모 backend 교체를 선행시키지 않음 |

Drive의 전역 검색은0건이었지만 알려진 WU ZIP·ACK의 직접 ID 조회는 성공했다. 따라서 이를 ‘새 백업 없음’으로 해석하지 않았다. 다른 세션의 미게시 raw, 접근 불가능한 대화·worktree, NCP의 현재 실행 프로세스는 이번 조사 범위에 포함됐다고 주장하지 않는다.

기존 C21F 게시, C21G 독립 실행 계약, C21H/I 완료, 원 실패/raw/역사적 NOT_PUBLISHED, CPU55 보호, create-only 백업, 기존 과학 HOLD를 유지했다. C21I의 제조 RHS 감소와 일관된 전체 시간 가속 미확립 판정도 바꾸지 않았다.

## 3. 실제 사용한 물리와 정규화

원본은 `rei_bianchi@3b85dedce84d37b3e165da00685a8a984950aafe`의 `CanonicalFVSpecies`이다. `SOURCE_MANIFEST.json`의9개 고정 파일을 byte 단위로 보존했다. 여기에는 물리 모듈·cosmology lock·참조 response·원본 정책 파일이 포함된다. `canonical_fv.py`의 SHA256은 `91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5`다.

LRS metric에서 (a_\perp=ae^{-b}), (a_\parallel=ae^{2b}), (s=\dot b), (H=\dot a/a)로 둔다. 정규직교 공간 기저의 텐서는

\[
\sigma^i{}_j=\operatorname{diag}(-s,-s,2s),\qquad
\pi^i{}_j=\operatorname{diag}(-p,-p,2p).
\]

직접 수축하면 (\sigma_{ab}\sigma^{ab}=6s^2), (\pi_{ab}\pi^{ab}=6p^2), (\sigma_{ab}\pi^{ab}=6sp)다. Wolfram Language의 실제 반환으로 이 수축과 초기 변환을 검산했다.

사용자가 제시한 막대의 관례를 명확하게 하기 위해 이번 그림은 Frobenius norm을 쓴다.

\[
S=\sqrt6\,s/H,\quad\Sigma_F=|S|,\qquad
P=\frac{8\pi G}{c^2}\frac{\sqrt6\,p}{H^2},\quad\Pi_F=|P|.
\]

H는 proper-time 단위 s⁻¹이고 p는 J/m³다. (\kappa_4=8\pi G/c^4)를 쓸 때 같은 표현은 (\Pi_F=\kappa_4|\pi|/(H/c)^2)다. 원래 REI의 half-contraction norm과는 (\Sigma_F=\sqrt2\Sigma_{REI})이고, 대응하는 stress norm도 (\Pi_{half}=\Pi_F/\sqrt2)다. 두 관례와 signed S/P를 모두 raw에 저장했다.

PR147의 `Pi_gamma_J_m3`, `Pi_nu_J_m3`, `Pi_matter_J_m3`는 각각 (p_i=(P_{\parallel,i}-P_{\perp,i})/3)다. 총 p는 이 **signed 값들을 먼저 더한 값**이다. 오래된 다른 branch에서 Pi가 압력차 자체를 뜻한 경우와 혼용하지 않았다.

초기 S₀에 대응하는 원본 매개변수는 `Sigma_ref=abs(S0)/sqrt(2)`와 `orientation=sign(S0)`다. 원래 `initial_state()`를 그대로 호출한다. 초기 복사 분포는 공통 (k_\gamma=k_\nu=k), (W(\mu)=1+kP_2(\mu))로 정했다. 실제 초기 fields의 k=0,.5를 이용한 affine map

\[
k=\frac{P_{target}-P(0)}{2[P(.5)-P(0)]}
\]

으로 실제 H와 massive quadrature의 작은 잔차를 포함했다. 목표 값으로 solver 출력을 덮어쓰지 않았다. 실측 최대 초기 mapping discrepancy는 (1.3877787807814457\times10^{-17})이다.

## 4. 계산한 격자와 결과의 해석

초기 격자는 다음 signed 값의9×9 조합이다.

```text
S0 = [-.04, -.02, -.01, -.005, 0, .005, .01, .02, .04]
P0 = [-.001, -.00075, -.0005, -.00025, 0, .00025, .0005, .00075, .001]
```

적분 구간은 z=20→4, (a=1/21\to0.2)다. photon·massless neutrino의 energy/number hierarchy는 ell8, massive fraction=.1, mass/Tref=30, massive A=0,24×12 canonical cells, Gauss3이다. Tcmb0=2.7255K, donor=None이며 모든 case에서 나머지 초기 자유도는 고정했다. DOP853 설정은 원본 그대로 `n=101, rtol=3e-11, atol=3e-13`이다.

그림은 네 sign(S₀)/sign(P₀) panel로 나눴다. 가로·세로 축은 실제 초기 norm, 색은 각각 z=4의 최종 norm이다. 영점 case는 여러 panel에 공유되며 distinct case 수는81개다. 이 두 norm만으로 모든 텐서 형태나 초기 분포를 지정할 수는 없으므로 이 그림은 고정된2차원 초기 분포족의 응답이다.

| S₀ | P₀ | S(z=4) | P(z=4) |
|---:|---:|---:|---:|
|0|0.001|0.000241821442|0.000234437247|
|0.01|−0.001|0.000902547958|−0.000248142438|
|0.01|0|0.001143825511|−0.0000144090893|
|0.01|0.001|0.001385054150|0.000219230354|
|0.04|−0.001|0.004336510450|−0.000288735358|
|0.04|0|0.004576062244|−0.0000573381021|
|0.04|0.001|0.004815566220|0.000173966985|

이 표가 보여 주는 첫 관찰은 세 가지다. 초기 전단이0이어도 응력이 전단을 생성한다. 같은 초기 norm이라도 상대 부호에 따라 최종 전단이 다르다. 초기 총 응력이0인 경우에도 비등방 팽창에 따라 응력이 생긴다. 이 해석은 이번 source·구간·초기 분포족에 묶인 수치 관찰이다.

이미 저장된81개 결과만으로 원점 근처의 centered finite difference를 만들었다. 추가 ODE는 없다. 간격 ΔS=.005, ΔP=.00025에서

\[
\begin{pmatrix}S_4\\P_4\end{pmatrix}\simeq
\begin{pmatrix}
0.1143802264&0.2418460776\\
-0.00144343831&0.2344844869
\end{pmatrix}
\begin{pmatrix}S_0\\P_0\end{pmatrix}.
\]

간격을 두 배로 했을 때 행렬의 최대 성분 변화는 약7.07×10⁻⁷이었다.81점 전체에 대한 선형화의 최대 절대 residual은 S에서3.15×10⁻⁶, P에서3.66×10⁻⁶이다. 원점 근처의 최종 stress cancellation 방향은 (P_0\simeq0.00615579S_0)로 관찰됐다. 이는 인증된 미분·전역 오차 bound나 PR147의 별도4입력 degeneracy 결과가 아니다.

## 5. 최적화·경량화·벡터화·병렬화의 구체적 기여

가장 직접적인 비용은 각 case가 같은 이산 연산자와 momentum grid를 다시 만드는 일이었다. worker마다 immutable `CanonicalFVSpecies` template를 한 번 만들고 case마다 얕게 복사한다. 달라지는 것은 Sigma_ref, orientation, k_gamma, k_nu, _nfev이며, 실제 초기 상태 배열은 매번 독립적으로 만든다. 연산자·Thomson 계수·momentum 배열은 read-only다.

K개 case와 W개 worker에 대해 두 Legendre operator 생성 횟수는2K→2W, canonical grid 생성은K→W로 줄어든다. 이번 K=81,W=4에서 각각162→8,81→4라는 구조적 작업 수 감소다. 이것은 wall-time speedup 측정값이 아니다.

moment kernel은 `(r*q)**2`를 한 번 구해 두 운동량 성분에 재사용하고 `1-mu²`, immutable cell population의 최솟값을 캐시한다. NumPy array 연산을 그대로 사용하며 큰 case×time×packet 배열을 새로 broadcast하지 않는다. `(r*q)**2`를 `r²*q²`로 재결합하거나 reduction 순서를 바꾸지 않았고 FP64와 원래 RHS를 유지했다.

각 trajectory는 독립 process에서 원래 DOP853을 실행한다. `solve_ivp(vectorized=True)`를 ensemble 병렬 solver로 해석하지 않았다. persistent process는 template를 재사용하고 case가 끝날 때마다 JSON/NPZ를 즉시 남긴다. BLAS/OpenMP thread를1로 제한해 case 병렬화와 중첩되는 thread 폭증을 피한다.

| 후보 | 판정 | 근거와 후속 조건 |
|---|---|---|
| immutable template·정확한 moment CSE | 구현·실행 채택 | 물리·상태·합산 순서 보존, 대표3 trajectory bitwise 일치 |
| 독립 process·incremental output | 구현·실행 채택 |4workers 실제81완료; 부분 실패가 다른 성공 결과를 없애지 않음 |
| canonical momentum의 보존 구조 | 원본 구현 재사용 | collisionless Bianchi I의 특성 표현; scattering 추가 시 재검토 |
| gamma/nu 동일 hierarchy의 상태 축소 | 후속 후보 | adaptive error norm이 달라질 수 있어 이번 source-preserving 경로에서 제외 |
| GPU/JAX/Numba·새 Schur/backend 통합 | 오늘 pilot의 선행 과제에서 제외 | compiler·자료 이동·solver 정확도 대응이 별도 작업; 현재 목표는 이미 달성 |
| 기존 HE/WU/REC/S12 실행 일괄 재수행 | 중복 실행하지 않음 | 새 반환·완료 상태를 재사용하고 아직 없는 의존성만 별도로 처리 |

## 6. 실제 수행한 검증과 정확한 범위

focused 검증7개가 exit0으로 통과했다. source9파일 identity, norm·단위·signed cancellation, template 독립성,4개 대표 moment의 bitwise parity,3개 전체 trajectory pair의 모든 저장 배열 bitwise parity, CPU55/quota/memory/lease, 결과 재개·identity·손상 검사를 포함한다. trajectory pair 검증에는6회 IVP, 본 pilot에는81회 IVP가 있었으므로 이 연구 단위의 실제 새 IVP는87회다.

| 관측 | 실제 값 |
|---|---:|
| distinct physical pilot 완료 |81/81|
| worker exit codes |0,0,0,0|
| 저장된 시점 합계 |8,181|
| case별 RHS 평가 |92–224|
| 총 RHS 평가 |14,421|
| 초기 common k 범위 |−0.33501982430636024…0.3350198243063604|
| 최대 Hamiltonian 대수 상대 residual |2.220446049250313×10⁻¹⁶|
| radiation number monopole 최대 편차 |0|
| massive cell 최소 population |1.491026203638869×10⁻³⁰|
| massive comoving number 최대 상대 편차 |4.440892098500626×10⁻¹⁶|
| 최종 ΣF 범위 |1.70×10⁻²⁰…0.00481987955610218|
| 최종 ΠF 범위 |5.71×10⁻²⁰…0.00029587955662661403|

Hamiltonian 항은 fields에서 대수적으로 구성되므로 작은 residual은 내부 일치 검사다. angular truncation, momentum quadrature, ODE global error, 적용하지 않은 feedback을 합친 오차를 인증하지 않는다. 새 해상도 수렴·성능 benchmark campaign은 사용자 요청에 따라 수행하지 않았다.4worker campaign wall3.577104197초는 관측 telemetry이며 serial 대비 가속률·NCP scaling을 뜻하지 않는다.

독립 검토자는 구현을 작성하지 않은 별도 agent이며,81개 NPZ의8,181시점과 source/hash를 읽어 물리적 norm을 확인했다. 새 적분 없이 scoped scientific acceptance를 내렸다. 운영 finding 두 건은 한 번의 bounded repair episode 안에서 수정했다.

1. 실행 장소를 명시적 `--execution-site` 선언과 관측 hostname/platform으로 기록한다. 기본은 unspecified, NCP_execution=null이다. NCP라는 표시는 사용자의 선언이며 자동 호스트 인증이 아니다.
2. v2 reservation에 QUEUED를 기록하고 worker가 실제 solve 전 STARTED marker를 fsync한다. MISSING/known-NOT_STARTED만 재개하고 STARTED/INCOMPLETE·FAILED·옛 v1 미완료는 보존한다.

표적 repair 검증3그룹은 실제 worker process를 사용했다. 중단·재개 시험의 solve는 명시적으로 표기한 test double이며 물리 ODE0회다. 원81결과를 다시 계산하지 않았다. 부모가 정확한 diff와 raw 보존을 확인해 같은 검토 episode의 R1/R2를 닫았다.

## 7. NCP 자원을 함께 사용하는 실행 준비

64CPU/128GB라는 사양을 현재 할당으로 가정하지 않는다. 실행기는 실제 affinity, cgroup-v2 cpuset·모든 보이는 ancestor quota/memory, MemAvailable, 짧은 CPU 부하 관측과 공동 lease를 교차해 배정한다. CPU55를 제외하고 coordinator를 포함한다. memory reserve=max(1GiB, effective limit의12.5%), coordinator256MiB, worker512MiB 예산이다.

NCP에서는 `--workers 63`을 요청하되 실제 자원 상한이 적용된다.64개 CPU가 모두 허용되고 CPU55가 포함된 경우에도 coordinator까지 세면 worker 최대62개다. 다른 세션이 실행 중이라는 이유만으로 전역 중지하지 않는다. 같은 `/tmp/bass_cpu_leases`의 `cpu_N.lock`을 사용하는 세션과 협력하고 관측상 여유 있는 CPU를 사용한다. unmanaged 작업은 관측만 할 수 있으며 lease가 그 작업을 통제하지 않는다. 다른 process를 종료하지 않는다.

이번 실제 sandbox에는 affinity0–8, quota8CPU, effective memory8GiB가 관측됐고 coordinatorCPU0, workerCPU1–4를 사용했다. NCP 쪽 readonly remote probe는 응답하지 않아 중단했다. 그 조회로 현재 NCP CPU·메모리·실행 작업을 확인했다고 말할 수 없다. NCP 실행은 남아 있으나 오늘 첫 그림은 이미 만들어졌다.

현재 v2는 새 output directory를 써야 한다. 완료된 v1 raw를 v2 `--resume`에 넣으면 identity mismatch로 거절한다. 기존 v1 runner의 원형과 vendor closure를 `archived_execution_v1/`에 보존했다. 원본 결과의 집계·그림은 저장된 데이터를 재사용한다. v2의 새 실제 NCP run은 handoff에 명시한 별도 bounded 실행으로 구분한다.

## 8. physmath-research-loop 단계와 DAG

이론 R1–R10과 코딩 C1–C10의 실제 작업을 아래처럼 대응시켰다. 각 번호를 별도 문서 수로 늘리지 않았다. C8의 수치 판정은 이번 사용자가 요청한 preliminary scope에 한정되며 새 convergence나 성능 측정은 수행하지 않았다.

| 이론 단계 | 완료 근거 |
|---|---|
|R1 연구 위치·계약|최신 외부 결과 먼저 조사, 오늘81점 pilot으로 현재 단위 확정|
|R2 근거·재사용|PR147 고정 source·lock, Einstein–Vlasov 원전 Section2, 기존 반환 재사용|
|R3 주장·전제 정렬|LRS/collisionless, Frobenius/half, c², signed total stress 구분|
|R4 가설·표현 탐색|S/P 초기 mapping, 네 부호 branch, exact reuse 후보|
|R5 구성적 유도|텐서 수축, q변환, affine k변환, canonical momentum 보존과 작업 수 유도|
|R6 독립 검증|CAS 대수 확인+별도 구현 reviewer의 raw/source 검사|
|R7 판별 검증|대표 bitwise trajectory, 실제81 IVP, 저장 데이터 응답행렬|
|R8 결과 판정|scoped preliminary 채택; global bound·full physics·speedup은 미채택|
|R9 정식 결과·코딩 연결|THEORY_KO, IMPLEMENTATION_CONTRACT, source/input/runtime manifest|
|R10 종료·재개|고정 source·raw·인계문·최종 게시/백업 영수증으로 마감|

| 코딩 단계 | 완료 근거 |
|---|---|
|C1 목표·baseline|PR147 source와 물리 단위·기존 solver 허용오차 고정|
|C2 식–데이터–코드|fields의 p=ΔP/3 확인, initial_state/adapter/plot 연결|
|C3 수치 설계|같은40state·quadrature·DOP853, expression/reduction order 보존|
|C4 실행 DAG·자원|부모 작업들과 분리, CPU55·quota·memory·공동 lease|
|C5 구현|adapter/runner/resources/plotter와 완전한 결과 경로|
|C6 구현 검증|focused7PASS, repair3그룹PASS, raw/exit code 보존|
|C7 과학 검증|초기 mapping·tensor norm·number·positivity·Hamiltonian 일치|
|C8 수치·재현성|3개 full trajectory bitwise 재현, 자원과 scoped residual; 새 convergence/benchmark NOT_RUN|
|C9 독립 검토|별도 reviewer 한 번, R1/R2 최소 수정 후 같은 episode 마감|
|C10 판정·인계|v1실행/v2운영 수정 분리, Git push·create-only backup·NCP/다음-thread handoff|

현재 DAG는 `최신결과 조사 → 정규화·입력계약 → exact reuse 구현 → focused 검증 → 실제81개 → 독립검토·표적수정 → 게시·백업`이다. 원81개 결과는 운영 수정 이전 실행 identity에 묶인다. `NCP 새 실행`은 현재 host 관측 뒤에만 이어지는 별도 node다. H/He/full feedback과 다른 프로젝트의 완료된 작업을 이 pilot의 선행 조건으로 다시 연결하지 않았다.

| 구분 | 이 문서가 고정된 시점의 상태 |
|---|---|
|실행|81/81 실제 physical pilot 완료, 추가 repair physical run0|
|게시|고정 content와 draft PR 게시 준비; 실제 완료는 별도 closeout receipt 참조|
|백업|create-only 세 저장처 백업 준비; 실제 완료는 별도 closeout receipt 참조|
|DAG|오늘 첫 그림 완료; NCP 실제 실행 미수행; 기존 과학 HOLD 유지|

게시·백업은 과학적 검증과 별도다. 최종 commit/PR, archive size/SHA, provider ID와 실제 acknowledgement는 closeout receipt가 권위 기록이다. 이 보고서의 연구 결과를 뒷받침하는 실행 identity는 `0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a`다.

## 9. 문헌·도구의 사용과 재사용 범위

- Heinzle & Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein–Vlasov equations*, CQG23(2006)3463, [DOI10.1088/0264-9381/23/10/016](https://doi.org/10.1088/0264-9381/23/10/016), [arXiv gr-qc/0512031](https://arxiv.org/abs/gr-qc/0512031). Section2의 stress moment·covariant momentum·expansion normalization을 읽었다. SciSpace의 초기 두 검색 결과에 잡음이 있어 정확한 제목/DOI로 보완했고 Exa로 원문을 읽었다.
- [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html): 기존 array kernel과 메모리 사용 설계에 적용했다.
- [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html): 원래 DOP853 state/오차 계약을 유지했다.
- [Python process executor 설명](https://docs.python.org/3/library/concurrent.futures.html): process 단위 독립 실행과 재사용의 근거로 읽었다. 실제 구현은 `multiprocessing` spawn을 직접 사용한다.
- WolframContext 요청은 internal error였으나 Wolfram Language evaluator의 대수 확인은 실제 반환됐다. 검색과 CAS 반환은 물리 IVP 실행 증거와 구분했다.

새 외부 solver 코드를 도입하는 비용을 지불하기 전에, 이미 소유한 REI source와 NumPy/SciPy를 source identity가 유지되는 형태로 재사용했다. 오늘 결과를 해석하고 이어 쓰는 데 필요한 이론·코드·raw·그림·남은 의무는 이 unit과 두 handoff에 모두 포함된다.
