# R3M12 controlled single-b local return

**반환 node: R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN. b-grid 판정: NO_GO.**

지정 입력 commit `77237751bdd2aed5934bf7fc3bc626d631a09058`에서 별도 worktree/branch를 만들고, 패키지의 addition-only 10파일 patch를 적용했다. 코드 commit은 `0b0090bc217ef62b27f709de803660b13bc64148`이다. 원 worktree와 옛 결과·실패 로그를 보존했다. 기존 인증으로 전용 branch push 및 remote SHA 확인을 실제 수행했다. main merge/force push는 하지 않았다.

패키지 SHA256SUMS 90/90 및 원 930,236,215-byte archive SHA `5af567f4be6f5dfd1dc9e7b42f24409a775de7f9bf776c3485303e6c306b9506`와 내부 manifest를 검증했다. 저장 baseline/dx03125 state를 먼저 재전파 없이 후처리한 뒤, 새 fixed-CAP lane에서 TDL 6개와 기존 AOCC lane에서 4개를 한 번에 하나씩 실행했다. 새 baseline은 128-step 완료 checkpoint를 검증하고 이어 실행했다. 총 11개 attempt의 stdout/stderr/config/environment/exitcode를 보존했다.

## 저장 상태 Gram 후처리

| 저장 run | 원 raw 합 | P_span(n<=3) | ||G-I||2 | condition | gap 잔차 |
|---|---:|---:|---:|---:|---:|
| tdl_baseline_retry | 0.00686622294942 | 0.00687087123066 | 0.00114115 | 1.001142771 | 3.47e-18 |
| tdl_dx03125 | 0.00758538896563 | 0.00758676150845 | 0.000272846 | 1.000273053 | 1.04e-17 |

Gram 보정 후 격자 간 변화는 **10.419207%**다(원 raw 10.473968%). Gram 보정만으로 공간 민감도가 해소되지 않는다. nested n=1,2,3, eigenvalues, 각 orbital norm, region-minus-span, eps와 cross term은 `postprocess/*_gram.json` 및 `report/ARCHIVED_GRAM_TABLE.csv`에 있다. eps_complement_inside는 미포함 bound/target 상태도 포함하며 continuum 확률이 아니다. 유한 sampled span을 all-bound capture로 승격하지 않는다.

## 새 TDL 제어 비교

상대 변화는 표의 reference에 대한 절댓값 비율이다. 사전 1% 선별 기준을 유지했다. PASS_PAIR_ONLY는 해당 한 쌍의 선별만 의미하며 수렴 차수·점근 수렴을 확정하지 않는다.

| Run | Reference | P_span(n<=3) | 변화 % | 초기 E+0.5 (Eh) | stationary residual (Eh) | 1% screen |
|---|---|---:|---:|---:|---:|---|
| tdl_cap_base | new reference | 0.00687085362816 | 0.000000 | 0.027893954 | 0.013656715 | REFERENCE |
| tdl_dt025 | tdl_cap_base | 0.00689884577346 | 0.407404 | 0.027893954 | 0.013656715 | PASS_PAIR_ONLY |
| tdl_imag025 | tdl_cap_base | 0.00686991214732 | 0.013703 | 0.027885218 | 0.0034901375 | PASS_PAIR_ONLY |
| tdl_imag025_long | tdl_imag025 | 0.00686941016751 | 0.007307 | 0.027885202 | 0.0034891211 | PASS_PAIR_ONLY |
| tdl_refined_dx03125 | tdl_imag025_long | 0.00758459465608 | 10.411148 | 0.018576234 | 0.0091343158 | FAIL |
| tdl_refined_dx025 | tdl_refined_dx03125 | 0.00775827737938 | 2.289941 | 0.012661223 | 0.021078203 | FAIL |

시간 비교는 CAP reference dt=.05를 고정한 새 대칭 propagation이다. 기존 checkpoint에서 새 dynamics를 시작하지 않았다. 초기 imaginary-time step 비교는 총 준비시간 15를 유지하고 .05×300→.025×600으로 바꾸었으며, 이어 .025×1200(총 30)과 비교했다.

공간 비교는 .025×1200의 초기 준비, physical dt=.05, CAP, box를 모두 동일하게 유지한 .4/.3125/.25 격자다. 원 matrix의 옛 초기 준비를 가진 dx 파일을 섞지 않고 `spatial_matrix/`를 파생했다. Coulomb potential 또는 grid phase를 결과에 맞춰 조정하지 않았다. .3125→.25도 2.289941%로 실패한다. 같은 imaginary-time step에서 finer-grid stationary residual이 증가하므로 이 표만으로 continuum 공간오차를 분리한 것은 아니다. E+0.5나 residual을 capture probability 오차로 등치하지 않는다.

## AOCC 한 변수 비교

| Run | P_projectile_bound | 기준 대비 변화 % | basis | metric norm | max anti-Hermitian defect | 1% screen |
|---|---:|---:|---:|---:|---:|---|
| aocc_base | 0.0101790845155 | 0.000000 | 52 | 1.00000000000001 | 6.32252e-07 | REFERENCE |
| aocc_dt025 | 0.0101801842387 | 0.010804 | 52 | 0.999999999999852 | 6.27383e-07 | PASS_PAIR_ONLY |
| aocc_radial_only | 0.00969734896482 | 4.732602 | 74 | 1.00000000000004 | 1.37408e-05 | FAIL |
| aocc_exponent_only | 0.0116559183262 | 14.508513 | 50 | 1.00000000000001 | 1.07763e-07 | FAIL |

기준은 ns=12/np=8, s-exponent .001..100, eps_max=5다. dt-only는 .05→.025, radial-only는 ns=16/np=12로만 변경하고, exponent-only는 기존 count에서 alpha_max=1000으로만 바꾸었다. radial-only는 확률이 감소하고 exponent-only는 증가한다. 두 변화의 상호작용을 이번 분리 비교만으로 가산 추정하지 않는다. metric norm 보존은 basis 수렴이나 generator 결함 해소가 아니다. 원 one-electron AOCC/vendor 코드를 수정하지 않았다.

AOCC s+p negative-energy aggregate와 d를 포함한 TDL n<=3은 같은 truncation이 아니다. AOCC state-resolved 공통 채널이 없어 cross-lane equality는 미평가다. d 추가나 two-electron W1R 물리는 실행하지 않았다.

## 검증과 미실행

제공 targeted pytest 35/35, 기존 TDL CPU/GPU parity 1개, 새 controlled TDL CPU/GPU parity를 통과했다(후자 최대 state 차이 3.1646e-16). 새 TDL seal 6개, complete/config identity, finite-span positivity/nesting/gap, single-variable 설정 차이를 검사했다. 전 suite 재실행과 독립 리뷰 완료는 주장하지 않는다. 별도 reviewer는 CLIENT_WORKTREE_MISMATCH로 실행 전 차단됐으며 Host의 제한된 diff 검토를 남겼다. 초기 해시 명령 cwd 오류와 Drive readback 403을 포함한 운영 실패는 `report/FAILURE_LEDGER.json`에 해결 여부와 함께 있다.

선택하지 않은 dt0125, dx020, AOCC window 및 plane 재전파는 NOT_RUN이다. 50/225 keV/u, b-grid/tail, 적분 단면적, physical rate, production central, P0 covariance, source-owned D102563 승격은 실행하지 않았다. H8 값이나 post-hoc margin을 calibration/UQ로 사용하지 않았다.

## 보존과 다음 최소 작업

전체 output archive에는 6개 production TDL state.npy와 seal, 소형 parity state, 모든 result/config/attempt 기록, source snapshot, 이 표와 실패 기록이 들어간다. AOCC CLI는 result만 반환하며 이번 AOCC에는 checkpoint/restart 지원을 주장하지 않는다. Git에는 큰 state를 넣지 않고 생략 파일의 SHA/size와 외부 archive 위치를 기록한다. Archive 자체의 SHA와 실제 cloud 업로드/readback 결과는 자기참조를 피하도록 archive 밖의 detached receipt에 기록한다. Drive는 기존 연결 도구, Dropbox는 기존 rclone dbx를 사용한다. 로컬 폴더 복사를 온라인 백업으로 세지 않는다.

다음 최소 수치 작업은 **dx=.25, physical dt=.05, 같은 CAP에서 imaginary dt=.0125×2400을 기존 .025×1200과 비교**하는 것이다. 총 준비시간 30을 유지하며 stationary residual과 finite-span 확률을 함께 점검한 후 추가 공간 정련을 판단한다. 이 다음 실행은 이번 반환에 포함하지 않았다. AOCC radial/exponent 수렴 문제도 별도로 남아 있다. b-grid NO_GO는 유지한다.
