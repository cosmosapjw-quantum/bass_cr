# D5A 전면 재감사: 원인 수정 및 한정된 적분 교정

감사 입력 commit: `8b7fef411ebca8dcdbfb45de542690c821fd7826`
입력 tree: `e17782911caad0af599715f37ac497639bf9e312`
날짜: 2026-09-25.

이 문서는 새 감사 결과의 별도 기록이다. 역사적 D1-D5A 결과와 원본 scientific branch/main을 수정하지 않는다. 수정 수치 코드는 아래 별도 전달 패키지에 있으며 아직 원본 production 코드에 통합하지 않았다.

## 실제 감사 범위

2,482 tracked files / 18,409,854 bytes의 SHA256와 Git blob identity를 확인했다. Python157개(고유139개),22,968줄의 syntax/static catalog, JSON1,243개 및 NPZ65개를 검사했다. 입력 commit에서 reachable100개/first-parent98개 history를 복원했다. 전체 byte inventory와 focused semantic audit이며 모든 줄의 과학적 정확성이 증명됐다는 뜻은 아니다. D5A raw matrix에서 최종 refinement 수치를 최대2.2e-19 차이로 재계산했다. 큰 B3/A3 production endpoint 배열은 복원하지 않았다.

## 기존 원인 주장의 정정

- D5A가 eta192->256에서 실패했다는 관측은 유효하다. 그러나 이를 순수 longitudinal ETF의 미분해로 확정한 이전 설명은 지지되지 않는다. q=126.7623인 exp(i q eta)의 독립 적분은 Gauss-Legendre96부터 절대오차 약1e-15다.
- 실제 finite-box FEM은 연속 piecewise quartic이지만 도함수가 내부 요소와 box 끝에서 불연속이다. positive s/p의 u'(64-)는 약 -0.0388033/-0.0491409이고 바깥에서0으로 뛴다. S와 달리 H,D는 이 도함수를 포함한다.
- 같은 rho192와 같은 eta192/256에서 TP support 경계만 정확하게 clip하면 S/H/D successive change는 2.9473e-8/1.2121e-6/2.2125e-6으로 감소한다. 원래 값은3.9321e-5/1.4333e-3/2.7737e-3다. 이는 basis 변경 없이 수행한 통제된 수치 개입이다.
- eta만 통과해도 globalrho192의 편향은 남는다. 수정 독립 기준 대비 H약0.266%,D약0.510%다. 한 축의 pair PASS는 전체 적분오차상한이 아니다.
- D3 full-matrix element-pair runner는 TP 교집합 support를 TT/PP에도 적용했다. 이는 구현 오류이며 pseudostate의 물리적 실패가 아니다.
- D4C는 cross support와 geometry breakpoints는 적절하지만 요소 내부의 ETF phase span을 제한하지 않았다. 낮은 polynomial quadrature order만 늘리는 것으로는 충분하지 않다.

## 수학과 구현

현재 continuous zero-extended FEM의 gradient weak kinetic form은 유효하다. 분포론적으로 두 번째 도함수에 interface/boundary delta가 나타나지만 현재 weak H에 delta를 다시 더하는 수정은 잘못이다. 다른 중심 bra에 대해 H phi=epsilon phi를 전공간 strong identity로 바꾸는 shortcut도 허용되지 않는다.

수정 cross-only kernel은 기존 basis_values, FEM 사양, Coulomb 및 ETF 부호를 보존한다. 알려진 ETF를 amplitude에서 분리하고 finite angular Fourier polynomial을 Fourier-Bessel moment로 적분한다. l<=1에는9개의 amplitude sample을 사용하지만 고진동 ETF를9점으로 직접 근사하는 것은 아니다. FEM/geometry 분할과 phase-span<=2pi subpanel, compensated summation을 적용했다. TT/PP나 collision은 이 모듈의 범위가 아니다.

100keV/u,b=2,z=-12,total18channels의9x9 TP matrix 상대비교:

| 비교 | S | H | D |
|---|---:|---:|---:|
| corrected q8->q12 |1.09496e-9|2.63259e-10|1.86239e-9|
| corrected q12->q16 |6.12225e-15|2.73821e-15|9.30741e-15|
| independent target-spherical q12 vs focalq16 |7.85796e-8|6.57644e-6|1.67338e-7|

기존 global D5A 및 phase-subdivision 없는 D4C도 다른 phi 적분 표현으로 absolute 약5e-15 안에서 재현했다. 별도 s-sector J0/J1 구현은 basis_values/phase_weights를 공유하지 않고 q20에서 S약3.01e-12,H약2.66e-6,D약3.87e-12 relative로 일치했다. 외부 blind reviewer는 없으며 서로 다른 수치 경로로의 검증이다.

## 실제 시험과 한계

- 신규36 tests PASS.
- 기존 FND84 tests PASS.
- 수동 실행기 tests+고정cross mode 전체 실행 PASS_BOUNDED_CHECKS; GPU0/collision0.
- legacy full suite 재실행은45초 도구 제한으로 중단돼 새 PASS가 아니다. 역사적492pass/3skip 결과는 과거 증거로 보존한다.
- original tracked input2482개는 감사 뒤에도 byte-unchanged.
- 사용한 환경 Python3.13.5,NumPy2.3.5,SciPy1.17.0 CPU. fresh radial bank를 저장했으며 과거 bank byte restore라 부르지 않는다.

판정체계에서도 D1의 과도한 capture admission, D2의 미적용 screen, full/cross norm 분모 변경, 구조적인 Hermitian pair를 독립 정확도로 해석한 문제를 기록했다. R2 SOURCE_MANIFEST는 후속7개 runner를 실제로 fail-closed하므로 이를 silent-pass로 비난하지 않는다.

## GPU 재실행과 FEM 대안

현재 CPU FND 적분 결함 때문에 기존 B3/A3 GPU run을 처음부터 전부 다시 실행할 필요는 없다. cr_repro Python numerical source는 R3M29에서 입력backup까지 변하지 않았다. projection만 바꾸면 동일 endpoint의 재분석, runtime만 바뀌면 작은 parity 확인이 우선이다. 다만 H/grid/CAP 또는 초기psi0를 바꾸면 해당 새 trajectory는 초기시각부터 새로 계산해야 한다. 기존B3를 새H의 결과로 재표기하거나 시간수렴 판정을 이전하지 않는다. 원래3%capture gap은 여전히 별개로 unresolved다.

비-FEM 대안으로 hard-wall 없는 global Laguerre L2 atomic Galerkin을 구현했다. beta=.75/1/1.5,N=16/32/48,l=0/1/2의27cases를 검사했고 N48의n<=3 energy오차는8.3e-14Eh이하다. 이것은 continuum/cross/capture검증이 아니다. Coulomb wave packets, higher-continuity B-splines, 기존GaussianAOCC, GPUgrid를 비교했고 repairedFEM을 회귀reference로 유지하면서 Laguerre를 첫 독립대안으로 선택했다. B-spline만 바꾸고 같은 hard-wall zero-extension을 유지하면 endpoint derivative jump는 남는다.

## 다음 하나의 작업

FULL_BLOCK_SUPPORT_CORRECT_S_H_D_ADAPTER_AND_FIXED_BASIS_CPU_PROPAGATION.

TT/PP는 자기 중심 support전체,TP/PT는 이번 검증kernel을 사용한다. 기존pilot(-12,+12,n<=2)와B3(-30,+60,n<=3)는 같은 문제가 아니므로 initial/horizon/common Gram observable을 먼저 맞춘다. 또 다른 임의order-only discriminator나 GPU전체 replay를 선행조건으로 만들지 않는다.

## 전달 패키지

- `BASS_CR_D5A_FULL_REAUDIT_20260925.zip`: 16,627,941 bytes; SHA256 `b8d0cbfaacf46b18075947e9a274a77330d40db406d1092f3e12377ff93d6069`. 보고서,FINDINGS14개,원자료tar/bundle,증거,코드,tests,CP0-CP2 포함.
- `BASS_CR_D5A_REAUDIT_CODE_20260925.zip`: 40,934 bytes; SHA256 `0c78614ac0097c8129bc7ea67fc6b4e0b436cf5ce02d209e53f3bfa36d388f68`. source lock,수동검증runner,tests,referencefixtures 포함.
- 전체 패키지는 기존 Drive+Dropbox destination에 create-only 업로드했고 양 provider 성공/ID/16,627,941bytes를 확인했다. R1 metadata verification이며 이번 업로드의 raw restore시험은 아니다.

Production HOLD / all-bound OPEN / b-grid NO_GO / original capture gap unresolved / capture_execution_allowed=false.
