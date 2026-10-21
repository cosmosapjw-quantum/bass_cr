# Matter/radiation을 분리한 non-tilted Bianchi I 첫 pilot

## 결과와 판정

사용자가 요청한 π_ab의 matter/radiation 분리를 코드·원자료·그림·초기조건 sweep에 반영했다. 기존 625개 history를 재실행 없이 분해했고, 초기 matter 응력을 독립적으로 바꾸는 새600개와 초기 성분 응력이 상쇄되는 mixed6개를 실제 coupled ODE로 계산했다. **새606개 모두 완료, 실패0**이며 구현하지 않은 별도 Astra 검토의 판정은 **PASS_SCOPED_PRELIMINARY**다. 기존625의 판정은 유지한다. NCP는 실제 접속 수단이 없어 NOT_RUN이고 production은 NOT_ISSUED다.

이번 결과는 자체 중력·충돌 없는 reflection-even LRS Bianchi I, zbar20→4의 고정 모델이다. 두 응력의 크기만으로 일반 Bianchi I 텐서의 상대방향이나 모든 initial distribution을 지정할 수 없으므로, 두 signed LRS 응력을 구분한 유한 slice와 여섯 mixed 조건이 정확한 연구 범위다.

주요 그림:

- [초기 matter 응력과 Σ의 네 부호 panel](results/new_sweep/plots/matter_sigma_end_heatmaps.png)
- [초기 상쇄 후 성분과 Σ의 실제 진화](results/new_sweep/plots/mixed_cancellation_components_sigma.png)
- [기존 history의 matter/radiation 분해](results/new_sweep/plots/old_history_component_decomposition.png)
- [기존 radiation-stressed Σ sweep](../results/pilot/plots_v3/sigma_end_heatmaps.png)

PNG, PDF, 정확한 plot CSV를 함께 제공한다. Raw 전체 위치와 완전한 archive identity는 FINAL_DELIVERY.json이 연결한다.

## 1. 어떤 π를 분리했는가

모든 성분을 같은 comoving orthonormal normal frame과 같은 순간 H에서 정의한다:

\[
\pi^{(m)}_{\hat a\hat b}=\mathrm{diag}(-p_m,-p_m,2p_m),\quad
\pi^{(r)}_{\hat a\hat b}=\mathrm{diag}(-p_r,-p_r,2p_r).
\]

Matter의 비영 stress는 fm=.1의 massive collisionless canonical component에서 온다. 나머지 pressureless dust의 anisotropic stress는0이다. Radiation은 photons+exactly massless neutrinos이며 공통 초기 brightness와 충돌 없는 동일 evolution을 사용한다. Native baryonic H/He stress나 Thomson/stellar feedback를 추가했다고 주장하지 않는다.

기존 half-contraction norm을 유지한다. p는 J/m³, H와 s는 proper-second 역수이므로 K=8πG/c²로

\[
\Sigma=\sqrt3|s|/H,\quad
\widetilde\Pi_m=\sqrt3Kp_m/H^2,\quad
\widetilde\Pi_r=\sqrt3Kp_r/H^2,
\]
\[
\Pi_m=|\widetilde\Pi_m|,\quad\Pi_r=|\widetilde\Pi_r|,\quad
\Pi_{tot}=|\widetilde\Pi_m+\widetilde\Pi_r|.
\]

Einstein 계수κ_E=8πG/c⁴를 쓰면 같은 무차원 성분은 κ_E|π_X|/(H/c)²이다. full Frobenius norm을 택하면 Σ,Π_m,Π_r가 각각√2배가 된다. 기존 convention을 몰래 바꾸지 않았다.

총 tensor는 성분 tensor의 합이고, 총 magnitude는 signed sum의 절댓값이다. 특히 성분 응력의 부호가 다르면 총 응력은 두 magnitude의 합보다 작다. 데이터에는 signed 성분, 각 magnitude, total, 압력 scalar J/m³와 성분별 anisotropic work `-6(s/H)p_X`를 모두 기록했다. 일반 텐서의 교차 contraction과 constraint 전파는 [THEORY_KO.md](THEORY_KO.md), 실제 Wolfram 결과는 WOLFRAM_SPLIT_ALGEBRA.json에 있다.

## 2. 초기조건과 실행 수

기존 cosmology lock, m/Tref=30, fm=.1,24×12 Gauss3 cells,L8 even energy block,rtol3e-11/atol3e-13,65 saved samples를 유지했다. 기본적으로Σ0∈[0,.004]의13개 크기와 비영±sign을 사용한다.

| 자료 | 수행 내용 | 실행 수의 의미 |
|---|---|---|
| 기존 radiation-stressed625 | 40,625개 저장 sample에서 matter/radiation 분해 | 새ODE0 |
| 새 matter slice | Pi_m0∈(0,.0004]의12크기×±sign, initial radiation k=0 | 새600 |
| neutral zero axis | 기존25의 actual k/source/case/hash/axes를 유지 | REFERENCE_REUSE25, 새실행 아님 |
| mixed cancellation | S0=0,±.004; signedPi_m0=±.0004,Pi_r0=−Pi_m0 | 새6 |

따라서 matter 그림의625행은600새+25참조이며, 새 trajectory 총수는606이다. 이전76/57/84/19 및 AGE 실행을 여기 합산하지 않는다. 두 성분의 완전한3차원 Cartesian sweep을 완료했다고 부르지 않는다.

Matter의 초기 분포 W_m=1+A_m P2에서 positivity가 허용하는 범위는−1≤A_m≤2다. 실제 helper 평가에서Σ0=.004의 signedPi_m0 범위는 약[−.0004833821888780,+.0009667643777560]이다. 그러므로 고정된 matter 모형에서 symmetric±.001은 불가능하다. 선택한±.0004의 최대|A_m|=.8275025625756662이고 모든새초기축의최대실현오차는4.336808689942018e-19다. 실제 원본 helper에 대한 bracketed inversion으로 타깃을 실현했다.

## 3. 성분을 분리해 얻은 물리적 결과

초기Σ=0, signedPi_m0=+.0004,signedPi_r0=−.0004인 실제 mixed history는 처음 total signedPi가−2.17e-19다. zbar=4에서는

\[
\widetilde\Pi_m=+2.27695063798\times10^{-5},\quad
\widetilde\Pi_r=-9.40362719772\times10^{-5},
\]
\[
\widetilde\Pi_{tot}=-7.12667655974\times10^{-5},\quad
S=\sqrt3s/H=-4.90804115649\times10^{-5}.
\]

**초기 total stress의 상쇄는 계속 유지되지 않는다.** 이 결론은 실제 mixed coupled solve에서 나온다. 별도 matter/radiation trajectory를 선형 합성하지 않았다. 반대부호 mixed history의Σ_end는4.90789487279e-5다. 부호반전의 완전한 대칭을 가정하지 않는다.

실제 각 초기/최종 saved field를 사용하여 기존radiation625+새matter600의 서로 다른1,225조건에 zero-intercept descriptive fit을 적용했다. Mixed6은 fit에서 제외했다:

\[
S_{end}\approx0.11438019419S_0
+0.11914730407\widetilde\Pi_{m0}
+0.24184661411\widetilde\Pi_{r0}.
\]

학습 격자 최대절대잔차3.70676127742e-7,RMS9.02595754393e-8이며, fit에 쓰지 않은 mixed6의 예측차 최대는5.95005728505e-8이다. Radiation/matter 응답계수의 비는2.0298118871이다. 이는 선택한 조성·시기·범위에서 같은 초기 무차원 응력을 주었을 때의 유한 empirical response 비교다. 일반적인 선형 superposition 법칙이나 continuous interpolation certificate가 아니다. 실제 source/data 기반 분석과 독립 재계산은 [response_analysis.json](response_analysis.json), [독립 addendum](evidence/RESPONSE_FIT_ADDENDUM.json)에 있다.

Matter-dominated, prescribed dilution 근사에서는 비상대론적 matter stress~a^-5,radiation stress~a^-4이므로 normalizedPi_m~a^-2,Pi_r~a^-1이다. 이에 따른 해석용 reference는 S_end≈.11617858S0+.11897848Pi_m0+.24383332Pi_r0를 준다. 이 근사는Λ와 geometry-induced stress response를 무시한다. 실제solver를 이 근사로 교체하지 않았으며, 근사식을 검산한 Wolfram 결과와 한계는 THEORY_KO.md에 있다.

## 4. 구현한 경량화·병렬화와 보존 범위

원본PR147의40-state 시스템에서 이 고정 범위의 invariant structure를 이용해8-state로 줄인 parent solver를 재사용한다. 동일한γ/ν energy vector, reflection-even multipoles, 수동적으로 보존되는 number sector를 중복 적분하지 않는다. 새로운 성분 분리는 저장 diagnostics를 늘리지만 ODE state를 늘리지 않는다. 독립 trajectory는 process pool로 나누고, 저장 history의 source moments는 원본 bounded NumPy moment_batch를 사용한다. SciPy의 vectorized flag를 ensemble integrator로 오인하지 않는다.

Worker의 energy matrix와 basis는 재사용한다. **새 A_m inversion의 각 trial에서는 원본 CanonicalMomentumFV와 quadrature를 재구성한다.** 따라서 quadrature 구성 자체를 cache했다고 보고하지 않는다. 고정 contract의 helper 재사용 설명은 같은 원본과 해상도를 사용한다는 뜻으로 적용했고, 실제 구성 행동은 본문과 ROOT_ADMISSION.json에 명확히 남긴다. 기존 parent의 source 6개와 625×4개 raw, 총 2,506개 파일은 이전 manifest와 byte-identical하다. Native Rust/default/provider/pin/lock/허용오차/이전 campaign은 바꾸지 않았다.

실제 local worker 수는 6, 7, 8이었고 상한 8을 지켰다. 새 sweep의 trajectory-batch wall time은 14.977557074초, aggregate child task wall time은 16.523054625초, CSV 증거 조립을 포함한 outer command는 58.906940554초다. 이는 실제 budget receipt이며 벤치마크 비교·speedup·peak RSS 감소의 증거가 아니다. NCP wrapper는 관측한 affinity/cgroup/spare CPU/memory에 따라 최대 64개 worker를 선택한다. BLAS/OpenMP thread 1개, nice 10, 명목 256 MiB/worker와 reserve, wall 900초/aggregate child 3,600초를 유지한다. 다른 작업의 존재만으로 중단하거나 관련 없는 프로세스를 종료하지 않는다.

## 5. 검증과 독립판정

새 물리에 필요한 원본 40-state/reduced 8-state 비교 4개와 signed-A energy check 2개를 실행했다. 이전 6-case/L8–L12/tolerance campaign을 반복하지 않았다.

| 검사 | 실제최대값 |
|---|---:|
| 4개source/reduced65시점비교 | 1.70319487782e-11 |
| sourceH²constraint상대잔차 | 2.22044604925e-16 |
| 2개massive방향미분energyidentity상대잔차 | 1.48106087727e-10 |
| 기존component합 대 원래signedPi | 4.33680868994e-19 |
| 독립review의새dimensionlesscomponent재구성차 | 2.16840434497e-19 |
| 새초기축실현오차 | 4.33680868994e-19 |

모든 새 sample의 H와 E0는 유한한 양수다. 최소 massive cell population은 5.48518700294e-31이고, 샘플링된 massless brightness의 최솟값은 .8020344325다. 이는 65개 시점 × 128개 angular node의 진단이며 global positivity 증명은 아니다. 작은 표적검사 3개도 PASS다. 독립 review는 새 606개 raw의 39,390개 sample, 기존 625개 분해의 40,625개 sample, 25개 참조의 identity/hash, 그림/plot CSV/NCP wrapper를 읽었다. 실제 수치 검토와 fit addendum은 모두 닫혔으며 추가 ODE 검증이 요구되지 않는다.

## 6. 최신 자료 조사, 게시와 남은 경계

이전 단계에서 접근 가능한 REI branch 253개, PR 211개, owner repository 51개의 목록을 확인하고 관련 source와 새 receipt를 읽었다. Dropbox의 관련 40개/38개 목록은 끝까지 확인했으며, Drive는 반환된 141개 및 기존 LRS 하위 폴더 13개 범위다. 다른 대화 검색은 unavailable이었다. 새 첨부에서는 관련 text 5개와 archive 10/12/17의 선택한 convention/contract를 읽었다. 전체 첨부·모든 repository 파일·모든 대화의 전수검증을 완료했다고 주장하지 않는다. ATTACHMENT_INTAKE.md와 parent intake에 정확한 coverage를 남겼다.

계약은 43988c7244ebe8fc43e05ea23348fa944f8c0a7f, source/새 검증 checkpoint는 34f93a48778a2d8a36b058e33de5302732752bae에 기존 PR198 branch로 게시했다. 각 checkpoint는 Drive/Dropbox upload ACK와 크기를 확인했다. 최종 source/results/backup/DAG는 FINAL_DELIVERY.json에서 확인한다. PR은 open/draft로 유지한다. Workspace CI의 cargo fmt 실패와 cargo test skipped는 이 Python pilot의 실제 scoped PASS와 구분하며, CURRENT_SOURCE_CI.json에 source별 관측을 기록한다.

NCP key `/home/cosmosapjw/.ssh/ncp_key`는 현재 sandbox에 없었고 연결된 remote 실행 도구는 월 사용량 소진을 반환했다. NCP 인증/실행을 한 것으로 기록하지 않는다. 실제 인증 가능한 Codex에 전달할 완성 명령은 CODEX_NCP_EXECUTE_KO.md에 있다. 기존 625개 NPZ 전체가 없어도 게시된 reference_controls/old_representative table로 새 606개 실행과 그림을 만들 수 있다.

과거 V12 cap 180초/debit 200.39897231891518초와 남은 100개의 NOT_AUTHORIZED는 유지한다. AGE time8/16/32는 이미 완료된 자료이며 다시 실행하지 않았다. Native age/time convergence HOLD, nonlinear Grackle bound NOT_ESTABLISHED, full native H/He와 일반 Bianchi I/continuous certificate 등의 HOLD, production NOT_ISSUED는 변하지 않는다.
