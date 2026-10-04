# R4AN 실행 요약: native cell fixture 검증

2026-10-04. CLOSED_NATIVE_THREE_CHART_FIXTURE_PARITY. 이 파일은 Git용 실행 요약이며 전체 상세 보고서·원시 input/output·계약·실패기록·DB는 동일 이름의 R4AN complete package에 보존한다.

## 계승
R4AM 원점 정칙화·사차 각도 모멘트·weak S/H/D/K 참조식을 새 C++17 GMP 정수 구간 kernel로 이식했다. parent/는 원 R4AM Git subtree 3f62a03a88dbd91845429643ac845918f8c15413을 재사용한다. 기존 source를 수정하지 않는다. R4AH 10점 S-only/두 window·M9·중심점·이전 science suite·전달복구는 다시 실행하지 않았다.

## 실제 수행
새 native build 1회: g++ Debian14.2.0, -std=c++17 -O2 -fno-fast-math -ffp-contract=off, -lgmpxx -lgmp. Source SHA256 8f871fccbbdb21168b732af948f43c248ced6b0e80843bd88722abb40e3285b0. 이 환경 native SHA256 b23d3c8854dae348409669c9dc9477b00872477cb367c714fab229ae0a9479be.

새 변경영역 시험 74건 통과. 비영 ETF의 3chart x 16 s/p 조합, 원점 r=0, malformed 입력, source/출력경로/소비된 계약, fixture 범위 거절을 포함한다. Native 부재와 actual-candidate profile 거절은 실제 RED→GREEN 기록이 있다. 다른 시험은 tests-after이며 모두 TDD로 세지 않는다.

통합 fixture 3cell x 1024node=3072node. Target origin와 projectile origin의 H/K 복소 L1 반경은 각각 1.9032988171286315e-20 이하, 일반 삼각형은 2.8514309165931967e-17 이하로 사전 1e-16 기준을 통과했다. Parent n=32 root bracket와 analytic error를 동일 fixture에 한해 재사용했다. Parent rootfinder/majorant/integral 재실행은 0이다.

저장 R4AM 수치 결과와 S/H/D/K의 실수/허수 24개 interval pair가 endpoint까지 정확히 같다. 3개 fixture에서 중점차이 0. Native process wall은 약 0.170/0.166/0.310초, runner0.91076초, outer process1.51초와 peakRSS97928KiB다. 포함되는 wall/RSS를 합하지 않고 실제 원자/64코어 speedup을 추정하지 않는다.

독립 읽기 전용 검토 75조건 통과. Exact integral을 별도 유리수·기호식으로 확인하고, 6개의 비영ETF point case를 Cartesian gradient 및 80자리 각도quadrature로 대조했다. 최대 native midpoint 차이는 6.238e-78 미만이다. 이 수치oracle은 interval증명이 아니며 독립 인간/agent/proof assistant 검토도 아니다.

## 수락범위
Native는 실제 node 합만 계산한다. 적합한 analytic remainder를 더해야 cubature enclosure다. 통합 fixture는 u=r인 상수s-field와 v=0이며 물리 원자상태가 아니다. Nonlinear radial 및 비영ETF s/p는 별도 point test다. 공개 adapter는 SYNTHETIC_FIXTURE만 허용하며 FINITE_CANDIDATE를 거절한다. Raw protocol을 source admission으로 사용하지 않는다.

Actual candidate integral=0; full-K=0. precise_K_cubature_error=null; K_window_derivative_bound=null; physical_bridge_upper=null. G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO.

기존 S-only totals H=1/64:5.599633283869504e-17, H=1/128:7.49726779045559e-17 ta^-1은 수락된 값으로 유지한다. 두 window의 과거 null 상태로 되돌리지 않는다.

다음은 R4AO_WEAK_K_FINITE_CANDIDATE_SINGLE_CELL_PILOT. 실제candidate/cell/entry/majorant/source-native/resource의 새 계약 전에 actual call cap=0. 전체cell/81성분/full-K/scattering은 자동 개방하지 않는다. 현재 추가 NCP 과학실행 큐는 비어 있다. Bianchi 물리와 재이온화 동역학은 rei_bianchi가 맡는다.
