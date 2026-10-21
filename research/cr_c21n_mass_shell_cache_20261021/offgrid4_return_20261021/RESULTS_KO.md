# C21N offgrid4 NCP 반환

## 실행 범위

고정 과학 content `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`, REI source
`3b85dedce84d37b3e165da00685a8a984950aafe`, 그리고
`prepared_offgrid4/grid_offgrid4.json`의 신규 4개 좌표만 실행했다. 완료된
81/26/98/125 ODE는 재실행하지 않았다. solver는 FP64, 40-state DOP853,
101 saved samples, `rtol=3e-11`, `atol=3e-13`, z=20→4다.

네 좌표는 `(S0,Pm0,Pr0)=(0,±7.5e-5,∓7.5e-5)` 및
`(0,±1.75e-4,∓1.75e-4)`이다. 각 case raw, RESULT, COMPLETE, reservation,
run manifest, resource/storage record와 stdout/stderr 반환을 보존했다.
모든 worker exit code는 0이며 네 건 모두 `COMPLETE`다. CPU 1–4를 썼고
CPU55는 실행기 보호목록에서 제외됐다. host `s1a0e5abed09`, platform
`Linux-6.8.0-124-generic-x86_64-with-glibc2.39`, Python 3.12.3,
NumPy 2.3.5, SciPy 1.17.0이다. 네 worker 합산 wall duration은 약 2.18 s;
보고된 process high-water RSS는 112,197,632 bytes다. 이는 성능 벤치마크가
아니다.

## 검산 및 성분

네 raw는 모두 유한한 FP64 `Y(40,101)`이며 saved scale factor는 1/21에서
0.2까지 단조 증가한다. 초기 target 좌표 최대 차이는 `2.31e-19`다.
Hamiltonian 상대잔차 최대 `2.23e-16`, massive comoving-number 상대잔차
최대 `4.45e-16`, radiation-number 잔차 0, 최소 massive cell population
`1.20e-30`이다. photon과 massless-neutrino radiation을 분리하고 matter,
radiation, total signed full-Frobenius 성분을 보존했다. 초기 상쇄율 약 1은
z=4에서 약 0.389864–0.389866으로 풀린다. 방향을 반전한 두 쌍에서 shear와
total-stress endpoint 부호가 반전한다. 수치 endpoint는 `analysis/`의 CSV와
129점 component archive에 수록됐다.

새 후처리는 ODE를 호출하지 않았고, 기존 125-point component NPZ의 앞부분을
array-equal로 검증한 뒤 새 4점만 덧붙였다. 총 129개 실제 좌표는 불규칙 집합이며
보간·Cartesian grid 완성·수렴 판정이 아니다. 독립 read-only 검토에서 raw,
seal, coordinates, source/code hashes와 성분 부호를 확인했고 P0는 없었다.

## 범위 한계

`global_error_bound=null`; finite-window remainder도 확립되지 않았다. 이번
실행은 오직 offgrid4 stress-coordinate 응답이다. general triaxial,
full reionization, CMB 및 full cosmological accuracy는 계속 HOLD다.

기계 판독 가능한 원시 실행·검산 자료는 같은 디렉터리의 `raw/`, `analysis/`,
`RETURN_TO_CHATGPT.json`, `DAG_OFFGRID4.json`에 있다.
