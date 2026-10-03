# R4AM 실행 보고서: origin-safe cross weak-K와 명시적 cell remainder

2026-10-03. R4AL에서 이어진 원자 데이터 전용 연구다. 이번 결과는 **고정 geometry의 cross weak-K 참조 적분기와 나머지 상계가 구현·fixture 검증된 상태**다. 실제 원자 K 행렬 및 연속-z 정밀 오차는 미계산이다. production solver 전체나 원자 데이터 완성을 선언하지 않는다.

## 이번에 닫은 것

원 weak operator source에서 chi, grad chi, dot chi, Coulomb, kinetic의 계수와 ETF 부호를 회수했다. 원 파일·archive 경로를 보존했으며 과거 실행이나 시험을 재실행하지 않았다. Bianchi 동역학은 rei_bianchi 소유로 그대로다.

기존 S의 이차 각도 모멘트는 gradient 곱에 충분하지 않으므로 전체 사차까지의 entire 모멘트를 구현했다. target harmonic의 켤레는 상수 계수에만 적용한다. 복소 좌표를 켤레화하거나 sqrt(Q) branch를 도입하지 않았다.

두 원점의 첫 radial 패널은 r와 eta=(r_other-R)/r의 좌표로 바꾸고 r grad phi와 체적요소를 먼저 결합했다. 원점 slope가0이라고 가정하거나 작은 ball을 버리는 방식이 아니다. 첫패널 u/r의 정확한 다항식 소거와 r^2 gradient/Coulomb cancellation을 사용한다. 원점 외부 radial 분모에는 명시적인 nonzero/pole 검사를 둔다.

## 실제 candidate의 기하 검증

등록된 z∈[-2049/64,-2047/64]a0, b=2a0, 동일 candidate에서 원래 shell 삼각형1,229개 중2개를 원점chart2개로 정확히 대체했다. 나머지 일반삼각형1,227개를 유지했으며 누락영역0이다. 각 원점거리영역의 면적은 정확히 a^2임을 R 다항식 계수별로 확인했다. 상대핵의 [R-a,R+a]는 원 radial panel28 내부에 있다. 기하 검사의 wall2.081초는 전체 연구시간이 아니다.

이것은 실제 원자기하의 cover 근거이지 행렬원소 적분이 아니다. actual atomic K/H/D/S integral=0, radial integral=0, m64 prepare=0, central S/M9/old R8 replay=0이다.

## 실제 fixture 적분과 오차

새 analytic manufactured field u=r와 v=0, R=5에서 원점T, 원점P, 일반 삼각형 세 cell을 n=32,rho=2로 적분했다. 사전에 complex entry 반경1e-16, 총평가수3080, wall45초를 고정했다. 정확한 Coulomb/체적 답과 일치하는 구간을 얻었다.

|fixture|K/H 복소 성분의 L1 반경 상계(표시)|정확값 포함|
|---|---:|---|
|원점T|1.9032988172e-20|참|
|원점P|1.9032988172e-20|참|
|일반삼각형|2.8514309166e-17|참|

표시는 위쪽 반올림이다. 정본 유리수와 방향성 반올림 endpoint는 evidence/LIGHT_FIXTURE_RESULT.json이다. 실제Gauss node3,072개와 complex bound probe6개, wall14.015초를 기록했다. 이 local 제조함수는 normalized physical atomic state가 아니다. 위 목표 달성은 actual K matrix accuracy의 목표 달성이 아니다.

Gaussian remainder는 holomorphic ellipse 상계로 계산하며 quadrature order 차이를 error bound로 쓰지 않는다. floating/SciPy/mpmath는 root proposal에만 사용하고 부호 bracket을 exact rational로 확인한 불변 provider를 재사용한다. 적분 산술은 Python 정수/2^256이다. 이번에 native GMP/Fortran kernel을 빌드하거나 시험하지 않았다.

## 변경영역 검증

새 module/runner 시험153건 통과. 48개 Cartesian-angle 조합은 s,p(m=-1,0,+1)16조합×3chart를 별도 field/gradient 계산의4096점 원주합과 대조한다. 원점/collinear, 복소phase, 사차moment, 양·음m, analytic moment/volume/Coulomb fixture, complex pole, 잘못된 reference path, method/precision/단위/source/output/fixture/runtime identity와 예산조건의 거절을 검사했다.

runtime 성공경로의 resource observation은 시험용 subprocess/OS boundary fixture다. 실제 admission이나 실제 원자 적분을 했다는 증거가 아니다. production runner는 fixture context를 거절한다. 새핵심 행동의RED→GREEN 기록과 구현후추가시험을 구분했으며153개전부를TDD로부르지않는다.

독립 read-only 검토55조건은 production 모듈을 import하지 않고 origin Jacobian, scaled gradient, ETF kinetic/connection 부호, Bessel 생성급수 도함수, cover면적, exactfixture 포함성 및Gaussian error식의유리수부등식을 검사했다. 제삼자인간/에이전트검토 또는 proof-assistant 검증이 아니다. interval backend와 analytic majorant의 전체 형식검증을 했다고 하지 않는다.

개발 중 sparse polynomial 곱의 안쪽 반복문에서 RHS 변수명이 exponent에 의해 가려지는 구현오류가 있었다. 다항식 regression으로 실패를 재현하고 지표변수만 교정했다. 실패소스와 RED 로그를 evidence/implementation_failure_poly 및 RED_POLY_PRODUCT.txt에 보존했다. 이는 fixture 단계 오류이며 actual atomic attempt는0이다.

## 부분 완료와 다음 단계

등록 contact cell에서 정확 finite-candidate cross weak-K의 국소 real-analytic 성질은 이 원점/패널 결합으로 별도 유도했다. 그러나 현재 실행 가능한 provider는 고정 z에서 u,w의 복소근방만 검사한다. z-방향 numerical derivative bound나 uniform preciseK remainder를 아직 반환하지 않는다. S의 기존 M9를 K에 복사하지 않는다.

순수Python interval reference는 정확성 oracle이며 전체81entry/full18 matrix production속도를 보장하지 않는다. complete-cover single-entry runner는 유한wall/평가budget에서미해결이면실패와partialcheckpoint를반환한다. 실제NCP입력에대한완주와정확도는미검증이다.

다음 로컬 한 단계는 R4AN_WEAK_K_NATIVE_SINGLE_CELL_PARITY다. 이미 유도·구현한 식을 기존 directed-integer native backend에 옮기고 저장된 exactfixture/cellenclosure와 대조한다. 실제 원자 cell은 새scope/resource계약 전cap0이다. 이후실제Kcell및zuniformremainder,operator/state/bridge/couplingbasis/b/energy의과학gate를차례로닫는다. 모든로컬작업이끝났다는판정은아니다.

현재NCP에서필요한첫작업은여전히기존R4AH_m64한점이다. 여기서새원자적분을대신실행하거나memoryguard를다시시도하지않았다. 포함한원R4AHarchive는바이트동일하며첫점수락전remaining9는열지않는다.

DBv26에는4개scopedevidence와3개primarysourceaccess를추가했다. 기존15view와13current과학행은모두동일하다. G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. precise_K_cubature_error, physical_bridge_upper, K_window_derivative_bound는null이고두stenciltotal은[null,null]이다.

최종게시·백업의성공여부와실제coverage는별도DELIVERY_RECEIPT가정본이다. 원자료가이미클라우드에있다는사실로새백업완료를주장하지않는다.
