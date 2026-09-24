# BASS_CR 기초 재감사 및 재구축 연구 결과

기준일:2026-09-24. 기준 repository commit:8e1d49e5ef6af70bb47d9238e64cda68ea0f5c4f. 이 문서는 원래 R3M30 외부 감사와 별개의 후속 연구 분기다.

## 결론
단순 cell-average patch를 production 주경로로 선택하지 않는다. 기존 모형을 폐기할 근거는 없지만, point-Coulomb/FFT collocation의 공간 표현, finite-imaginary-step 준비, moving-basis 검증과 all-bound extraction을 서로 분리하고 operator-consistent하게 재구성할 필요가 있다. 이번에는 실제 단일 원자/유한 기저 계산과 실행 가능한 독립 코드로 그 근거를 만들었다.

원래3.03–3.29% capture gap이 해결되었다고 주장하지 않는다. Production HOLD, all-bound OPEN, b-grid NO_GO는 그대로다. R3M27의 fixed-h selected-span 시간 추정은 보존하며 이것을 무효화하거나 새 모형에 자동 승계하지 않는다.

## 1. 참조한 권위 자료
Dropbox의 R3M9 원본 archive 추출 본문에서 공통 물리계약, keV/u, Galilean factor, Gram projection 및 두 중심 pseudostates 요구를 확인했다. Google Drive의 R3M27 작은 증거 archive를 이번 turn에서 실제로 받아 SHA c15388cb9237737dcb0f2249890e1c1fdd5f986a6b04701e2ed52ecc433e21a2와55289 bytes를 확인했다. 이 안의 raw B3 result SHA는7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce다. 큰 state.npy는 들어 있지 않다.

이전 turn의 R3M26/27/28/29 작은 증거 및 감사 패키지를 byte-backed 입력으로 확인했고, 입력 identity는 inputs/INPUT_IDENTITIES.json에 있다. 실제 GitHub source도 다시 읽었다. 특히 scripts/r3m17_aocc_metric.py가 이미 독립 metric/Cholesky derivative를 검사함을 확인했다. 해당 검사를 '없다'고 재발견하거나 과거 claim scope를 승격하지 않았다.

SciSpace 검색과 primary source 조회, Wolfram symbolic evaluator를 사용했다. SkillQuiver 조회는 실행할 기능을 반환하지 않아 사용했다고 주장하지 않는다. 상세 서지는 SOURCES.json, 수학 유도는 docs/MATHEMATICAL_FOUNDATIONS_KO.md에 있다.

## 2. 구조적 원인으로 강하게 좁혀진 것: 준비 고정점
반복하는 연산자 Sτ=exp(-τV/2)exp(-τT)exp(-τV/2)의 고유벡터와 실제 H=T+V 고유벡터는 다르다. 같은 τ에서 iteration을 늘려도 이 차이는 남는다. 여기서는3D H와 Sτ 양쪽의 고유벡터를 직접 계산하여 iteration-length 불확실성을 제거했다.

| h/a0 | 원래 A3/B3 초기 H residual/Eh | 별도 L=16 원자 Sτ 고정점 residual/Eh | relative difference | true H eigen residual/Eh |
|---|---:|---:|---:|---:|
|.25|.001375549750126|.001375456058107|.006811%|2.38e-11|
|.20|.003195199693883|.003195010595682|.005918%|1.57e-11|

τ=.00625 t_a. box가 다르므로 완전한 원 실행 reproduction이나 byte parity가 아니다. 그러나 residual magnitude를 거의 그대로 설명하므로 finite-τ split bias가 잔차의 바닥값이라는 강한 증거다. 새 true-H residual-stopped LOBPCG 준비 후보를 구현하고 ARPACK 독립해와 비교했다. Preconditioner는 H를 바꾸지 않는다.

동시에 state L2 차이는 각각3.79e-5와5.65e-5에 불과하다. H residual 자체를 capture relative error로 읽어서는 안 된다. 이번 probe에서 얻은 state difference를 다른 box의 B3에 직접 적용하지 않았으며 preparation production budget은 아직 OPEN이다.

## 3. Cell averaging은 필요조건도 충분조건도 아니었다
같은 FFT kinetic을 사용한 true H 고유해를 hydrogen exact ground energy -0.5Eh와 비교했다. L=24는 L=16 대비 boundary 영향을 따로 확인하기 위한 추가 run이다.

| representation | nominal resolution | L/a0 | E/Eh | relative ground-energy error |
|---|---:|---:|---:|---:|
|point collocation|h=.25|24|-.487347481786|2.530504%|
|cell-average collocation|h=.25|24|-.490548987827|1.890202%|
|point collocation|h=.20|24|-.491491651083|1.701670%|
|cell-average collocation|h=.20|24|-.493785197809|1.242960%|
|Fourier-Galerkin cutoff|63 modes, L/N=.253968|16|-.499496366333|.100727%|
|Fourier-Galerkin cutoff|79 modes, L/N=.202532|16|-.499736273695|.052745%|

위 마지막 두 줄은 Rc=7의 구면 cutoff/periodic 진단 모형이다. 앞의 collocation과 물리적 boundary model이 같지 않고 kmax도 약간 다르므로 같은-H 오차/성능비로 취급하지 않는다. Rc=6→7과 L16/Rc7→L20/Rc9 control도 수행하여 cutoff 영향을 보존했다. 그럼에도 비슷한 momentum bandwidth의 benchmark에서 operator integration을 바꾼 효과가 cell 평균만 바꾼 효과보다 훨씬 컸다. 이는 공간 수렴 전략을 바꿀 근거이지 capture 오류3%의 정확한 분해는 아니다.

핵 위치를 z 방향으로 h/2 이동한 L=24 시험에서 ground E 변화는 h=.20 point2.16003e-3Eh, cell3.79041e-4Eh였다. L16에서도 거의 같은 변화였다. FFT kinetic+diagonal sampled V의 연속 translation symmetry가 깨진다. RSC/Octopus 원문에서 설명하는 grid egg-box와 같은 종류의 현상이지만 해당 문헌의 pseudopotential filtering을 여기 물리모형에 이식한 것은 아니다.

## 4. 왜 알고리즘 뼈대를 바꿔야 하는가
(1) Potential의 정확한 cell 평균은 Fourier basis의 정확한 <k|V|l>와 다르다. Cell averaging은 Fourier에서 sinc filter를 추가하지만 circular aliasing을 모두 제거하지 않는다.
(2) Coulomb cusp에서 [V,[T,V]]의 형식적 expectation은1s에서도 발산한다. fixed-h의 시간수렴을 h-uniform smooth-potential theorem으로 승격할 수 없다. Strang 자체의 수렴 실패나 물리 H의 부정합을 증명한 것은 아니다.
(3) 1s Fourier amplitude는 k^-4, kinetic tail은 K^-3로 감소한다. 따라서 FFT라는 이름만으로 exponential spectral convergence를 기대하면 안 된다. Wolfram에서 prefactor16/(3π),32/(5π)를 확인했다.
(4) 유한 Fourier-Galerkin에서는 H_R=D_RH0D_R†가 exact identity다. 작은 독립 dense/action 시험에서 energy translation difference<=9e-16Eh를 확인했다.

기존 raw-point solver는 회귀자료로 보존하고, 같은 basis에서 T,V,mass,prep,observables를 함께 정의하는 새로운 operator path를 구성하는 것이 낫다. Local cell correction을 production까지 계속 밀어붙이는 것보다 검증할 질문이 더 명확하다.

## 5. 실제로 만든 code와 radical 구성품
src/bass_foundations/kernels.py에는 fast finite Coulomb cell integral, high-precision oracle adapter, FFT H action, true-H preconditioned 준비, split-fixed-point 진단, exact Toeplitz Coulomb Galerkin action, 작은 dense oracle, minimal circulant embedding, radial hp-FEM, moving-potential exact benchmark와 connection negative control이 들어 있다.

Radial FEM은 p=4,60 graded elements,239 DOF/l,R=128에서 n<=3의 여섯(n,l) 에너지를 최대1.73e-10Eh 차이로 계산했다. n=3,l=2의 차이는1.22e-11Eh다. 그러나 R=64,n=5,l=2는 eigenresidual이 작아도 E 오차1.01e-4Eh가 남았다. R를 늘리면 이 차이가 사라졌다. 즉 높은 n의 box/completeness는 eigensolver residual과 독립이다.

이1D 원자 비용을3D 두 중심 충돌의 비용으로 비교하지 않는다. 다음 구현은 두 중심 S,H,D와 angular/positive-pseudostate completeness다. 기존 AOCC는 실제 source상 s+p-only이며, n<=3 TDL에는 d channels가 포함된다. radial Gaussian 개수만 늘려 이 차이를 없앨 수 없다.

## 6. Norm preservation을 통과하는 틀린 동역학
R3M17의 dotS=D+D† 검사는 유지해야 하지만 D의 anti-Hermitian 부분을 결정하지 못한다. 회전 basis에서는 D를0으로 잘못 넣어도 metric identity 잔차~1e-11, skew-generator 잔차0인 반면 direct basis derivative residual은.98995다.

더 물리적인 translating-Coulomb finite-basis benchmark도 구현했다. H(t)=D(vt)H0D†(vt)의 exact moving-frame 해에는 -vKz가 필요하다. 이를 빼면 norm error1.3e-15인데 state error1.0285, translated-ground projection은 exact.22624 대신 거의1이다. 바른 lab-frame midpoint는 steps8→128에서 state error.00188847→7.33e-6으로2차 수렴했다. 이는 기존 AOCC가 그 결함을 가졌다는 증거가 아니라, 새로운 기저/프레임 구현이 반드시 통과해야 하는 비자명한 benchmark다.

## 7. 선택과 미수행 사항
Surgical S1 true-H 준비 후보는 구현되었다. Surgical S2 exact Galerkin은 원자 oracle와 소규모 candidate이며 현재 cutoff를 원래 full Coulomb 충돌에 적용하지 않는다. naive B3 padding은 embedding3개만22.53GiB이고 다른 physics/FFT buffers는 미포함이라 resource redesign이 필요하다.

Radical R1 two-center cusp-adapted Galerkin prototype을 다음 우선 경로로 선택한다. Two-center radial/B-spline states+pseudostates+ETF+직접 D+common Gram observable를 하나의 설계로 묶는다. Alternative atom-patch/interstitial Fourier 및 separable weak Coulomb quadrature도 열어 두되 아직 구현하지 않았다. 세부 인터페이스/실행 순서/stop conditions는 docs/REBUILD_ARCHITECTURE_KO.md.

이번 작업은42개 신규 패키지 tests를 통과했다. 원 repository 전체 테스트, GPU parity, B3 대형 checkpoint, full collision, full all-bound/b-grid/cross-section은 실행하지 않았다. GitHub 원본 변경/push/merge도 하지 않았다.

이전의 B3 cell-average4-step 창은 폐기된 증거가 아니라 선택적 sensitivity test로 남긴다. 다만 더는 이를 유일한 다음 canonical 연구 경로로 강제하지 않는다. 새로운 proposed next node는 FND_R2_TWO_CENTER_OPERATOR_PARITY_AND_BOUND_SPECTRUM이다.

## 8. 체크포인트와 복구
CP0 입력/가정, CP1 static/준비 연구, CP2 operator/moving/radical 구성품, CP3 최종종합을 각각 별도 immutable ZIP로 만든다. 각 단계는 Google Drive+Dropbox의 기존 BASS_DERIVATION_DOSSIERS_20260912에 create-only 업로드한다. receipts/에 실제 provider ID와 size/ack grade를 기록한다. 역사적 manifest는 해당 stage ZIP를 대상으로 검증해야 하며 최신 파일에 적용하지 않는다.

백업의 raw readback/restore는 upload와 별도다. 큰 original states가 없는 작은 checkpoint를 full collision restore라고 부르지 않는다. 처음 실패한 radial-domain tests, 두 ARPACK runtime timeouts, 그림 디렉터리 permission error, CLI parent-directory failure를 results/FAILURE_LEDGER.json 및 첫 로그에 보존했다. Threshold 완화나 실패 로그 덮어쓰기는 하지 않았다.
