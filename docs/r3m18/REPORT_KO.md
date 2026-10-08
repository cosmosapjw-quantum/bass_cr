# R3M18 B2 단일 충돌 시간 수렴 판정

## 범위와 authority

이 work unit은 `07a2ba92d3622831a959a57c7ff142fd1977908a`에서 시작한
`N1_TDL_B_DT0125_SINGLE_COLLISION_TEMPORAL_RESOLUTION` 하나만 수행했다. 새 full
collision은 B2 한 번뿐이다. 수치 source digest
`581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`와
R3M17의 B2 config를 유지했다. A2, 더 작은 dt, 더 미세한 h, representation 변경,
AOCC trajectory, b-grid, 50/225 keV/u 및 physical rate는 실행하지 않았다.

시작 시 원격 ref와 로컬 대형 디스크에서 physics/config/source/initial identity가 맞는
완료 B2를 한 번 검색했으나 없었다. 원 checkout의 미추적 파일과 과거 R3M14–R3M17
result/state/seal은 수정하지 않았다.

## 실행과 binding

canonical runtime은 Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0,
CUDA runtime 12090, driver API 13020, NVIDIA driver 595.84, RTX 3090 24 GB였다.
package upgrade와 CPU fallback은 없었다. resource probe는
`PASS_RESOURCE_PREFLIGHT`였고 FFT 포함 추정 peak는 13,690,021,888 bytes,
probe 뒤 free VRAM은 17,856,987,136 bytes였다.

fresh B2 preparation은 `imag_dt=.00625`, 4800 steps로 완료됐다. 초기 배열 SHA256은
`ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa`로 B0/B1과
byte-identical이다. R3M14 v2 witness가 충돌 내부 초기 배열, preparation receipt,
source/config/runtime을 다시 binding했다.

실제 시간간격은 `0.01249892352238994`, 총 step은 3586이었다. 128-step 상한의
29 chunks를 순차 실행했고 마지막 chunk는 2 steps였다. 매 successful chunk 뒤
R3M17 guard가 다음 chunk 전에 immutable generation을 게시했다. 29개 generation의
state hash는 모두 다르고 논리 배열 총량은 29,232,003,712 bytes다. 첫 실패, retry,
손상 경로 overwrite, restore는 모두 0회다.

## B0/B1/B2 관측량

| run | requested dt | actual dt | P1 | P2 | P3 | final norm |
|---|---:|---:|---:|---:|---:|---:|
| B0 | .05 | 0.04996782580968821 | 0.0059368765332443235 | 0.007416156280617876 | 0.007911255992446844 | 0.9719538007036279 |
| B1 | .025 | 0.02499784704477988 | 0.006068282194867191 | 0.007562290857479282 | 0.008063449050040342 | 0.9787299101287787 |
| B2 | .0125 | 0.01249892352238994 | 0.00608524131220836 | 0.007581938013116333 | 0.008084190148156251 | 0.9786935443969073 |

세 channel 모두 signed 변화가 양수이고 B1→B2 차이는 B0→B1보다 작다.

| channel | B1-B0 | B2-B1 | `abs(B2-B1)/abs(B2)` | observed p | conditional fine remainder/B2 | 판정 |
|---|---:|---:|---:|---:|---:|---|
| P1 | 1.3140566162286784e-4 | 1.695911734116845e-5 | 0.2786926018% | 2.9566247563 | 0.0412080852% | EMPIRICAL_CONTRACTION_ONLY |
| P2 | 1.4613457686140589e-4 | 1.964715563705123e-5 | 0.2591310507% | 2.8975976407 | 0.0401638688% | EMPIRICAL_CONTRACTION_ONLY |
| P3 | 1.521930575934978e-4 | 2.0741098115908962e-5 | 0.2565637094% | 2.8780182899 | 0.0403948516% | EMPIRICAL_CONTRACTION_ONLY |

세 fine pair 모두 사전 등록된 real-time 0.10% screen을 넘는다. 관측차수도
R3M17의 clean second-order 범위 1.5–2.5 밖이다. 세 점 single-power 모델의 조건부
Richardson 잔여치는 0.10%보다 작지만, 같은 세 점이 그 모델의 잔여 가정을 독립 검증하지
못한다. 따라서 이 값을 certified error나 real-time budget CLOSED로 쓰지 않는다.

## norm, CAP, projector 진단

B2 final wavefunction norm은 0.9786935443969073이고 CAP layer의 norm은
0.003861411089940187이다. sampled analytic n≤3 channels의 최대 CAP fraction은
0.0008739175405814191이다. raw channel norm 범위는
0.999853224197343–1.0000000047590676이다. Gram rank는 14/14, condition은
1.000192629763871이다. P_region은 0.02645604705419993이다.

이 CAP/support 수치는 geometric support diagnostic이다. n>3 tail bound 또는 continuum
probability가 아니다. finite selected-span complement도 continuum으로 명명하지 않는다.
all-bound completion은 OPEN이다.

## 과학 판정과 claim ceiling

최종 판정은 `TIME_REFINEMENT_STILL_OPEN`이다. 이는 물리적 charge-transfer model 실패가
아니다. 현재 h=.20의 point-sampled Coulomb+FFT 충돌에서 requested dt=.0125까지도
fine pair screen과 사전 등록 clean-order 기준이 닫히지 않았다는 수치 진단이다.

A2가 없으므로 dt=.0125의 spatial gap은 `NOT_MEASURED`다. B2-A1을 h 효과로 계산하지
않는다. N1_TDL, spatial .30%, preparation, box/CAP/finite-time, all-bound, N2–N5,
b-grid와 physical rate는 모두 OPEN/HOLD를 유지한다.

다음 canonical node는
`N1_TDL_MOVING_TWO_CENTER_FULL_H_TEMPORAL_REFERENCE_DIAGNOSTIC` 하나다. 작은 고정
grid에서 동일한 움직이는 두 중심 `H_h(t)-iW`의 non-Hermitian-capable full-H exponential
action reference와 현재 split propagator를 공통 horizon에서 비교해, 관측된 p>2.5가
시간표본화·splitting·cancellation 중 어디에 민감한지 분리한다. 이 node는 새 production
collision이나 representation 변경을 자동 승인하지 않는다.

## 검증과 증거

canonical 환경에서 기존 R3M11–R3M17 통합 회귀 246개가 통과했다. 독립 diff 리뷰에서
resume 시 기존 generation의 전체 inventory를 재검증하도록 outer coordinator를 한 번
수리하고 회귀시험을 추가했다. 실제 29 generation 재검증이 통과했으며 최종 통합 시험은
250 passed였다. 수치 결과는 `results/R3M18/B_TEMPORAL_ANALYSIS.json`, support 진단은
`results/R3M18/B2_SUPPORT_AUDIT.json`, generation 및 large-array pointer는 같은 디렉터리의
manifest에 있다. 대형 배열의 원본은 `/mnt/sn850x2t/bass_cr_r3m18_20260923/B2`에 보존한다.

