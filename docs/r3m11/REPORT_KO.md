# BASS CR R3M11: local return intake and controlled refinement repair

## 결정

입력 정본은 `cosmosapjw-quantum/bass_cr@77237751bdd2aed5934bf7fc3bc626d631a09058`이다. `results/R3M10_LOCAL_RETURN_20260921/report/DECISION.json`의 `NO_GO`를 유지한다. TDL 공간 변화 10.4739683%, AOCC 기저 변화 9.0687696%는 내부 수렴을 통과하지 못했다. 이 단계는 새 단면적, 50/225 keV/u sweep, CR gas-frame rate 또는 production central을 계산하거나 승인하지 않았다.

현재 source 10개는 Git blob SHA와 대조했다. 저장소를 직접 clone한 것이 아니라 회수된 패키지와 connector 원문을 이용해 byte identity를 확인한 실행 사본이다. GitHub release의 큰 state.npy 6개를 새로 내려받아 검사하지 않았다. 따라서 과거의 n<=3 overlap sum을 Gram 결과로 재계산했다고 주장하지 않는다.

## 1. TDL: dt와 absorber의 혼입을 분리

기존 코드는 매 step에 같은 mask M을 곱한다. 원 실행 보고서도 dt 변경이 absorber를 바꾼다고 명시했다. 이번에는 그 지적을 실행 가능한 별도 경로로 구현했다.

차원이 있는 식은 `W=-hbar*log(M_ref)/dt_ref`, `H_eff=H-iW`다. `M(dt)=exp[-W dt/hbar]=M_ref^(dt/dt_ref)`로 정하면 순수 흡수 연산의 총 시간 의존성이 time-step 분할과 무관하다. 새 실행기는 양쪽 half damping을 사용하는 대칭 split이며, 고정한 reference dt는 0.05 atomic time이다. kinetic/potential과의 비가환 splitting error는 여전히 별도 dt 정련 대상이다. 이 경로는 원 baseline과 동일한 실행이라고 주장하지 않는다.

선택된 analytic hydrogen 상태를 B, 이산 적분 metric을 Wq라 두고 `G=B^dagger Wq B`, `c=B^dagger Wq psi`를 계산한다. 확률은 `c^dagger G^{-1} c`이며 기존 raw overlap sum도 별도 반환한다. 큰 N x k 배열 없이 chunk별 Gram을 누적한다. 결과는 유한격자 n<=nmax 선택부분공간이지 all-bound continuum-limit capture가 아니다.

`r=psi-B G^{-1}c`는 **omitted bound + target bound + continuum**을 포함한다. 그래서 `eps_selected_complement_inside_raw`를 pure continuum으로 부르지 않는다. region과 이 truncated bound 확률이 같아야 한다는 조건을 capture 수렴의 필수조건으로 두지 않는다.

## 2. 초기상태: 에너지 근접성과 이산 고유상태 수렴은 다르다

[-6,6]^3 a0의 작은 원자 상자, imaginary time 총15에서 실행한 진단:

| dx | imaginary dt | E / Eh | ||(H-E)psi|| / Eh |
|---:|---:|---:|---:|
| 0.5 | 0.05 | -0.4609153220 | 0.0056223045 |
| 0.5 | 0.025 | -0.4609176587 | 0.0014298666 |
| 0.4 | 0.05 | -0.4724388198 | 0.0136264100 |
| 0.25 | 0.05 | -0.4874991808 | 0.0758766360 |
| 0.25 | 0.025 | -0.4876099865 | 0.0210416391 |

공간 격자를 좁힐수록 정확한 -0.5 Eh에 가까워져도, 고정 imaginary dt의 stationarity residual은 커질 수 있다. 따라서 spatial ladder에 앞서 imaginary dt/total imaginary time을 분리한다. 이 작은 상자 결과는 collision run이나 continuum spatial error bound가 아니다. Coulomb singularity를 grid node에서 피하는 것만으로 cusp 해상도가 인증되지는 않는다.

## 3. AOCC: raw-H 결함을 complex Boys evaluation까지 추적

기존 Cholesky generator에 대해 `Ggen+Ggen^dagger=-i(Htilde-Htilde^dagger)`가 대수적으로 성립한다. 전파 단계에서 iG를 Hermitian화하므로 norm 보존은 원 H 적분의 Hermiticity를 인증하지 않는다.

실제 큰 기저의 한 primitive에서 Boys 인수는
`z=-3.3168887925160937 + 21.984297833631878 i`이다.
기존 SciPy 1.17.0 경로의 F0 값은 `-0.19723933899616974-0.47445793690959853 i`였고, mpmath 70자리와 독립 Wolfram 값은 `0.0479360953134310622-0.759399120263105791 i`였다. 상대 차이는 0.4940162822이며 켤레대칭도 깨진다. 라이브러리 전체나 모든 버전의 결함으로 일반화하지 않는다.

`F0(z)=sqrt(pi)*erf(sqrt(z))/(2 sqrt(z))` 및 `F_(n+1)=((2n+1)F_n-exp(-z))/(2z)`를 이용해 기존 large-|z| branch를 Re(z)<=0까지 확장했다. 작은 |z|는 기존 hypergeometric 표현을 유지한다. 48개 복소/실수 n=0,1,2 test cases의 70자리 기준 최대 상대 차이는 5.653e-14다. overflow는 fail-closed이며 225 keV/u 전체 argument domain을 인증하지 않았다.

같은 61개 시각, b=2 a0, 100 keV/u에서 generator defect 최대값:

| basis | 기존 | opt-in 수정 |
|---|---:|---:|
| 52 states | 5.936585842e-7 | 1.543737757e-13 |
| 72 states | 9.096271753e-6 | 3.303076354e-13 |

이는 sampled matrix repair이며 collision trajectory 재실행이나 basis convergence 완료가 아니다. vendor bytes와 기존 runner를 수정하지 않고 별도 모듈 namespace로 함수를 주입한다. H를 평균내어 이 결과를 만든 것이 아니다. 다음 local run은 수정된 두 기저 및 dt/2에서 P를 다시 계산해야 한다.

## 4. 범위와 동기화

HOST H8 보고서를 읽어 BDSCx2012 독립 quantum reference 및 P0 R20 38/38 완료 **보고 상태**를 동기화했다. H8 raw archive/38-energy data를 여기서 검증하지 않았고 수치값/UQ를 CR solver에 넣지 않았다. D102563 native 1s authority와 all-state 재현을 혼합하지 않는다.

새 코드는 `cr_repro/r3m11.py`, 회귀시험은 `tests/test_r3m11_controlled.py`, local configuration 생성기는 `scripts/r3m11_plan.py`다. 기존 source/config/results 및 실패는 변경하지 않는다. 상세 증거와 raw logs는 이중백업 패키지의 `r3m11_evidence/`에 있다.

다음은 `R3M12_CONTROLLED_SINGLE_B_REPLAY`이다. fixed-CAP + 초기상태 + Gram TDL, fixed-Boys AOCC를 각각 정련하고 기존 baseline denominator의 1% screening을 유지한다. s+p AOCC 전체와 n<=3 TDL 전체는 서로 다른 observable truncation이므로 일치를 강요하지 않는다. all-bound/tail/physical rate gate는 별도다.

## 근거

- Current repository local return and exact source at the pinned SHA.
- De Giovannini, Larsen & Rubio (2015), DOI 10.1140/epjb/e2015-50808-0: absorbing mask/CAP context. The fixed-time scaling used here is directly derived; no entire paper implementation claim.
- Gordon, Jirauschek & Kaertner (2006), DOI 10.1103/PhysRevA.73.042505: Coulomb cusp discretization caveat. Their ABC method is not implemented here.
- SciSpace discovery, actual Wolfram algebra and independent high-precision function evaluations, bounded CPU tests/probes.
