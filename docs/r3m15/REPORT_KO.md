# R3M15 controlled spatial matrix 반환

**Matrix 3/3 완료, scientific convergence NO_GO.** 새 충돌은 정확히 A/B/C 세 개다.
주 preparation 3개와 허용된 B preparation-only 정련 1개를 저장했다. 각 충돌 내부에서
v2 witness가 preparation을 다시 수행한 3회는 별도 충돌이 아니다. b-grid, 50/225 keV/u,
physical rate, 새 AOCC trajectory, main merge, force push는 실행하지 않았다.

## 실제 결과

| Job | h | P1 | P2 | P3 | P_region | norm | H residual (Eh) | Gram condition |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 0.25 | 0.0058154981459 | 0.00727202597424 | 0.00775738324065 | 0.0259051119957 | 0.978738989111 | 0.00137554975013 | 1.00021228294 |
| B | 0.2 | 0.00593687653324 | 0.00741615628062 | 0.00791125599245 | 0.0262160907373 | 0.971953800704 | 0.00319519969388 | 1.00019262976 |
| C | 0.3125 | 0.00567345621242 | 0.00710485208796 | 0.007584026106 | 0.0256525489625 | 0.978530789355 | 0.000581736784866 | 1.00027305292 |


모두 E=100 keV/u, b=2 a0, requested dt=.05, actual dt=0.049967825809688213,
z_start=-30, z_stop=60, box [-30,40]×[-30,30]×[-30,90], CAP width=4,
power=.125, reference dt=.05, project_nmax=3, slab_x=2이다. τ=.00625×4800을
세 격자에 동일하게 적용했다. 각 충돌은 897 step, 8 chunk, 7 sealed restart이다.
모든 내부 초기상태 binding은 PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED이다.

새 공간 pair 지표는 abs(P_B-P_A)/abs(P_B)다. P3 변화는
1.944985119%로 1% screen과 계획상 spatial .30%를 넘는다.
P1/P2 역시 약 2% 변한다. C→A와 A→B 차분은 같은 부호이고 감소하지만,
P3 observed order=0.534310107677와 Richardson 값=0.00912642528617818는
세 점의 경험적 single-power 적합일 뿐이다. fine 값에서의 보정은
15.36000472%로 크다. continuum 답이나 certified bound가 아니다.

## 충분조건과 직접 관측량

역사적 R3M14 FINAL_DECISION.json과 원 result/state/seal bytes는 그대로다.
새 CLAIM_GATE_ADDENDUM.json은 d>d_star를 INCONCLUSIVE로 분리하고,
직접 측정 0.009200678% 변화의 PASS_PAIR_ONLY와 구별한다. old R3M12 reference
initial.npy의 binding 부재는 여전히 false다. 과거 certificate의 소급 PASS는 없다.

A와 R3M14 τ=.0125 결과의 같은-grid P3 변화는
0.002324500%다.
분모는 실제 R3M14 P3이며, 과거 R3M12 denominator와 섞지 않았다.
historical backend request auto와 새 cupy는 실제로 모두 같은 CuPy backend였다.

B에서 추가한 τ=.003125×9600은 preparation-only다. 같은 grid/K/Q 설정의
initial pair 거리 d=4.2320694164499483e-05, 충분조건 threshold=0.00044361991675096629,
conditional relative upper=0.000951838719095 (0.095183872%)이다.
판정은 SUFFICIENT_CONDITIONAL_PAIR_ONLY이다. 실제 새 collision 확률은 측정하지 않았다.
이번 reference B의 초기배열 binding과 result SHA는 확인했지만, 이 조건부 floating
평가를 exact ground-state preparation/총오차/roundoff 인증으로 바꾸지 않는다.
역사적 old reference anchor의 미확인 상태도 바뀌지 않는다.
같은 B 공간의 정리를 통해 얻은 후보 확률 구간 전체가 A보다 높다. 이 floating
조건부 구간에서 τ-halving 이후 가능한 최소 A/B 지표도
1.851608120%다.
따라서 이 한 번의 preparation halving만으로 1% spatial screen을 닫을 수 없다.
이는 실제 추가 충돌 결과가 아니고, A/B 서로 다른 격자의 상태에 정리를 적용한 것도 아니다.

## 상태 후처리와 claim ceiling

기존 R3M14 final state를 read-only로 다시 투영한 P1/P2/P3는 게시값과 일치했다.
(P3-P2)/P3=0.06256732130553702는 n=3 nested-span increment이며 n>3 tail bound가 아니다.
모든 n≤3 Gram 검사는 rank 14를 유지했다. raw channel norms, CAP-layer channel norm,
최종 state의 CAP-layer norm, box와 Gram spectrum은 results/R3M15/*/support.json 및
MATRIX_ANALYSIS.json에 있다. rank loss를 epsilon floor로 숨기지 않았다.
nmax=4 후처리는 NOT_RUN이다. finite-span complement를 continuum이라고 부르지 않는다.
all-bound completion, b integration 및 전체 1% 오차예산은 OPEN/NO_GO다.

## 다음 하나의 canonical node

`N1_TDL_COULOMB_FFT_H_DT_REPRESENTATION_DECISION`.
A/B는 모두 transverse half-cell nuclear registration이지만 C의 projectile x offset은
0.1 cell이다. C의 차이는 3점 order의 가정을 제한하며 A/B 차이의 원인으로 쓰지 않는다.
한편 target-only real-time ray defect가 A→B에서 커졌다. 확인된 문제 범위는
고정 real dt에서 h에 민감한 point-Coulomb/FFT propagation representation이다.
공간 sampling과 real-time split 오차의 개별 기여는 아직 확정하지 않았다.
다음 실행 단위는 같은 grid/preparation/CAP에서 finite-time target-only dt=.05/.025를
비교하고, 필요한 matched collision dt cross-check로 h-dt 절차 유지 또는 핵 근방
representation 변경을 결정하는 것이다. 이번 실행에서 이를 추가하지 않았다.

## 소스·시험·재현·배송

반환 parent는 8c7bbfce157f17b85dc9082c62c63c05fef3b294, 역사적 실행 source는
0c068e902e59ad001c4a2ae1be4168d1d29907b8이다. cr_repro/*.py와 R3M13 helper/R3M14
witness를 바꾸지 않았으며 numerical source digest는 581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b다.
새 instrumentation digest와 source commit은 각 job start.json에 별도로 있다.
Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0, CUDA runtime 12090,
driver API 13020, NVIDIA driver 595.84, RTX 3090을 실제로 기록했다. 기존 scientific
interpreter를 재사용했고 패키지를 업그레이드하지 않았다.

필수 기존 4개 파일과 새 gate/coordinator 2개 파일의 최종 실행은 **85 passed**다.
초기 TDD의 두 module-missing 수집 실패는 gate-red/coordinator-red 로그에 보존했다.
역사적 52 PASS를 이번 시험 수로 재사용하지 않았다. full suite나 독립 리뷰 PASS를
주장하지 않는다. 구 manifest의 tdl.py 차이는 parent lineage에 이미 포함된 checkpoint
seal 수선으로 분류했고, 이번 source 및 historical state/result/seal의 고정 해시는 검증했다.

GPU 작업은 순차 실행했고 실제 FFT allocation preflight, live headroom과 job 예산을
검사했다. CPU fallback은 없었다. sampled GPU total-used peak와 각 예산은 job receipts에
있으며 샘플링 값을 엄밀한 peak 상한으로 부르지 않는다. A는 original outer coordinator,
B/C는 예산 delta guard를 추가한 coordinator를 썼으며 numerical interpreter/propagator는 같다.
MLflow는 outer command tracing에만 사용했다. trace 검증은 별도 receipt에 있고 agent
품질평가나 scientific admission으로 쓰지 않는다.

큰 배열은 /mnt/sn850x2t/bass_cr_r3m15_20260922에 보존한다. stage archive와 local
member manifest는 byte 검증했고, 원격은 selective provider metadata/manifest로 검증한다.
DELIVERY_RECEIPT.json이 provider별 실제 완료 범위와 R1/R2 수준을 기록한다.
UPLOAD_VERIFIED와 RESTORE_VERIFIED를 구별하며 원격 restore는 실행하지 않았다.
기존 R3M14의 완료된 백업과 R3M12 Drive 1/19 미완료 상태는 수정하지 않았다.
