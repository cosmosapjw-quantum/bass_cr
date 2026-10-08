# CR R3M11: 로컬 single-b 반환의 수용과 제어변수 분리

## 판정

`IMPORTED_LOCAL_NO_GO__FIXED_CAP_AND_FINITE_SPAN_CONTROLS_IMPLEMENTED__POSTPROCESS_FIRST__NO_BGRID_OR_PHYSICAL_RATE`

기준 저장소: cosmosapjw-quantum/bass_cr
입력 main SHA: `77237751bdd2aed5934bf7fc3bc626d631a09058`.
현재 판단의 원본은 `results/R3M10_LOCAL_RETURN_20260921/report/DECISION.json`이다.
옛 루트 R3M10_STATUS.json을 현재 판정으로 사용하지 않는다.

## 1. 실제 반환으로 확인한 것

TDL 6개와 AOCC 2개 single-b 실행이 완료되었다는 원본 보고·JSON을 읽었다.
이는 새로 수행한 실행이 아니라 사용자의 local 결과를 import한 것이다.
기준은 100 keV/u, b=2 a0이며 old/new 상대 변화는 |variant-baseline|/|baseline|이다.

TDL dx 0.4 -> 0.3125 a0: 10.473968315683176%.
AOCC supplied baseline -> large: 9.068769566743899%.
사전에 정한 1% screening을 둘 다 넘으므로 b-grid NO_GO를 수용한다.

TDL dt 변화 0.41323%, 종단 위치 변화 0.12319%, 넓은 상자 변화 0.01457%는
보존한다. 그러나 dt마다 동일 mask를 한 번 곱했으므로 dt 변화는 흡수 강도까지
바꾼다. 원 보고서가 이미 이 혼입을 지적했다. 이번 작업은 그 지적을 독립 재발견으로
세지 않고 실제 제어 코드로 옮긴 것이다.

기준 초기 에너지는 -0.4721060456 Eh, 세밀한 격자는 -0.4813887527 Eh다.
-0.5 Eh 대비 편차는 각각 5.57879088%, 3.72224946%이다. 이는 진단량이지
capture probability의 오차 추정식이나 전체 공간 오차 원인의 증명은 아니다.

## 2. 고정 감쇠율과 새 propagation lane

실수 mask 0<M<=1를 step마다 곱하면 V_abs=-iW에 대응하는
W=-hbar log(M)/dt를 갖는다. 같은 M에서 dt를 반으로 줄이면 W가 두 배다.
따라서 M_ref와 dt_ref를 먼저 고정하고

M(dt)=exp[log(M_ref) dt/dt_ref]

를 사용해야 같은 흡수 profile을 비교할 수 있다. 실제 코드는 atomic units다.
새 ControlledTDLRunner는 V-iW의 반 step, kinetic FFT, V-iW의 반 step을
대칭 배치한다. 시간 의존 V는 midpoint에서 평가한다.

이는 새로운 reference discretization이다. 옛 결과를 새 scheme의 결과로 재명명하지
않고, 옛 runner도 고치지 않는다. dt_ref=0.05 a.u.는 명시적으로 고정한 새 reference
parameter이며 옛 dt_actual의 유효 CAP와 정확히 같다고 주장하지 않는다.
고정 CAP와 Strang 구성이 boundary reflection 또는 Coulomb spatial convergence를
자동으로 보증하지는 않는다.

## 3. 유한 격자 channel span과 continuum의 구분

격자 적분 가중치 W_g와 sampled orbital 열행렬 B에 대해
G=B†W_g B, c=B†W_g psi 이다. 실제 유한 span projector의 확률은

P_span=c†G^{-1}c

이다. 단순 sum |c|^2는 G=I일 때만 같다. Wolfram의 정규화된 비직교 두-state
예에서 naive sum=26/25이지만 올바른 projection은 1이다.

새 후처리는 n=1,2,3의 nested spans, Gram condition/eigenvalues/identity defect,
raw overlap sum을 동시에 남긴다. singular/ill-conditioned Gram은 몰래 상태를
삭제하거나 pseudoinverse tolerance를 조절하지 않고 실패한다.

b=Q psi, c_perp=(I-Q)psi, R=공간 영역 projector로 놓고
p=||b||², eps_b=||(I-R)b||², eps_c=||R c_perp||²라 하면

Delta=<psi|R|psi>-p=-eps_b+eps_c+2 Re<Rb,Rc_perp>,
|Delta|<=eps_b+eps_c+2 sqrt((p-eps_b)eps_c).

이 식은 정확한 대수식이다. 코드의 부동소수점 평가는 interval certificate가 아니다.
여기서 c_perp에는 target bound와 미포함 projectile bound 등도 들어간다.
따라서 continuum_probability는 null이고, eps_c를 continuum contamination으로
보고하는 것은 금지한다. sampled analytic span도 정확한 continuum-Hamiltonian의
spectral bound projector와 동일하지 않다.

원 local return의 n=1 supplementary audit는 이미 정규화한 rank-one projector를
사용했다. 새 코드는 그 원칙을 n<=3까지 확장하며 과거 raw 결과를 덮어쓰지 않는다.

## 4. 다음 실행은 재전파보다 저장 상태 후처리가 먼저

원 repository의 RELEASE_ASSETS.json은 930,236,215-byte 전체 archive와 여섯
state.npy의 SHA를 제공한다. 이번 환경에서는 이 큰 archive를 내려받지 않았다.
기존 local archive가 있으므로 Codex는 먼저 그 SHA를 확인하고 baseline과 dx03125의
state.npy를 slab 방식으로 후처리한다. 원 result/state/config/hash를 대조하고 새 sidecar만
생성한다. capture_plane run과 baseline의 state SHA가 동일한 것도 원 provenance에
명시되어 있다. 공간영역 후처리를 위해 propagation을 다시 할 필요가 없다.

그 다음 14-job matrix에서 선택한 한 job만 실행한다. 자동 full-matrix 실행은 없다.
- TDL: 새 fixed-CAP baseline; dt/.5/.25; 고정 imaginary-time 총길이에서 tau/.5;
  다음 총길이 연장; dx=.3125,.25,.2를 필요할 때 순서대로 검사한다.
- AOCC: 기존 single-electron runner를 변경하지 않고 dt, radial count, s-exponent
  상한, positive-energy cutoff를 각각 분리한 설정을 생성한다.

s+p AOCC의 finite negative-state 합과 d 상태를 포함한 TDL n<=3 합은 같은 truncation이
아니다. 현재 두 raw total을 cross-lane equality gate로 사용하지 않는다. d 채널을 나중에
추가한다면 s/d의 겹침까지 처리한 전체 atomic generalized eigensystem이 필요하며
Cartesian d orbital을 독립 block처럼 덧붙여서는 안 된다.

b=2에서의 안정성은 모든 impact parameter와 b-tail의 인증도 아니다. 여기서는 NO_GO를
자동으로 해제하지 않는다. 양 lane은 독립적으로 계산할 수 있지만 cross-lane 해석은
일치한 observable/support와 각자의 내부 안정성을 먼저 요구한다.

## 5. 원본 보존·restart

cr_repro의 기존 10개 .py와 vendor primitive 1개는 remote Git blob identity로 대조했다.
새 파일만 addition-only patch에 포함한다. full repository clone/전체 tree 인증은 아니다.
역사적 result, 원 manifest, 실패 로그와 private Nichols code의 부재 상태를 보존한다.

새 runner의 checkpoint seal은 config/source/state/meta를 연결한다. 정상 chunk 완료 후
resume은 bit-identical 검사를 통과했다. 중단 중 두 파일이 불일치하면 fail-closed하며,
이를 crash-proof transactional checkpoint라고 부르지 않는다. 원 checkpoint를 새 dynamics에
resume하지 않는다. source 변경 시에도 새 output path를 사용한다.

## 6. 타 스레드 sync

HOST4 H8 원 ZIP을 Drive에서 raw로 회수했다.
SHA256: 8d9b3565f278f07f8d1aaa103910725bca6df4ce252247208e7492aff601ebd8.
2,788,902 bytes; ZIP CRC 및 28/28 payload manifest 일치.
H8는 BDSCx 1s reference와 PCHIP 재현을 확보했지만 source-owned continuous D102563
또는 physical UQ로 승격하지 않았다. CR에는 출처/상태만 import한다.
H8에 보존된 P0 R20은 native N38=38/38이지만 physical P0와 source anomaly가 남는다.
H-H R5의 method-freeze-only 상태는 numerical authority가 아니다.
이들을 TDL/AOCC source calibration으로 사용하거나 8% post-hoc margin을 CR gate로 쓰지 않는다.

## 7. 실제 수행한 검증과 미수행 사항

새 controls 17개, job matrix 6개의 RED 실패를 먼저 확인한 뒤 구현했다.
마지막 bounded suite: 35 PASS, 1 SKIP(CuPy 없음). 기존 local 20/20을 여기서 모두 재실행한
것이 아니다. 원 AOCC reference-loop를 포함한 전체 suite 시도는 실행 budget timeout을
만났고 그 로그를 보존했다. 이를 수학/물리 실패로 분류하지 않는다.
새 controlled CLI와 저장-state sidecar CLI는 작은 격자에서 각각 exit 0이었다.
production-sized state 후처리, GPU, 100-keV/u production 재전파는 이번에 하지 않았다.

## 8. 온라인 배포 상태

이번 session은 GitHub/Drive/Dropbox 읽기는 성공했지만 push/upload action은 노출되지 않았다.
직접 git 접속도 DNS 실패했다. 따라서 새 remote push와 새 online dual backup은 NOT_EXECUTED다.
로컬 전달물의 apply_and_push.py는 기존 authenticated clone에 새 worktree/branch를 만들고
테스트 후 branch-only push와 remote ref 확인을 수행한다. 기존 rclone remotes를 이용하는
r3m11_dual_backup.py는 immutable copy와 양쪽 raw SHA readback 후에만 COMPLETE를 기록한다.
실제로 이 도구들을 local에서 실행하기 전까지 그 성공을 주장하지 않는다.

## 원전·SSOT

- bass_cr commit 77237751bdd2aed5934bf7fc3bc626d631a09058, local return README_KO.md,
  report/DECISION.json, cr_repro/tdl.py, cr_repro/aocc.py, provenance/RELEASE_ASSETS.json.
- De Giovannini, Larsen & Rubio, EPJB 88, 56 (2015), DOI 10.1140/epjb/e2015-50808-0,
  arXiv:1409.1689. SciSpace discovery 후 primary abstract로 흡수 경계의 오차 분류를 확인했다.
- 위 mask scaling, finite-span projection, gap identity는 이번 직접 유도와 Wolfram 검산이다.
