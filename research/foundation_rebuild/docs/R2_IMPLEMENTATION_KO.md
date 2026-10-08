# FND R2: 연구 인계의 실행 가능한 구현

## 범위와 구분

CP3 연구에서 선택한 two-center cusp-adapted radial Galerkin 경로의 첫 bounded S/H/D 구현이다. 기존 cr_repro는 변경하지 않는다. 전체 two-center production collision engine이나 all-bound cross section을 완성했다는 주장이 아니다. Local Codex 역할을 구현자에서 고정 test operator로 바꾼다.

Atomic units(a0, Eh, t_a)를 사용한다. 단일 전자, 두 점 Coulomb source, 지정된 직선 궤적, survival renormalization 없는 finite-span observable를 유지한다. Cusp를 soft-core로 바꾸지 않는다.

## 식과 코드

중심 A의 기저는 chi_A=exp(i v_A.r-i |v_A|²t/2) [u_jl(|r-R_A|)/|r-R_A|] Y_lm이다. 복소 Condon-Shortley solid harmonic r^l Y_lm를 l<=3 전 m에 대해 직접 다항식으로 구현하여 축에서 각도 미분의 좌표 특이점을 피한다. 핵 자체에서 classical cusp gradient를 요구하면 오류를 내며 epsilon floor를 넣지 않는다.

S_ab=integral chi_a* chi_b, H_ab=(1/2) integral grad chi_a* . grad chi_b - integral chi_a* [1/r_T+1/r_P] chi_b, D_ab=integral chi_a* dot chi_b를 공통 양의 quadrature weights로 조립한다. Kinetic은 weak form이다. D는 dot S로 복원하지 않고 dot chi=phase[-v.grad(phi)-i v² phi/2]를 직접 평가한다. 코드와 유한 차분은 고정된 lab points에서 비교한다. 적분격자 자체를 미분해 D를 만드는 것이 아니다.

핵간 거리가 R일 때 rho=(r_T+r_P-R)/2>=0, eta=(r_T-r_P)/R, phi를 사용한다. mu=1+2rho/R, dV=R²(mu²-eta²) d rho d eta d phi/4. Laguerre 가중치를 exp(x)로 보상하여 원래 적분을 계산한다. 이 보상은 물리 potential 변경이 아니다. 동일 핵 위치는 별도 spherical chart가 필요하므로 지금은 명시적으로 거절한다.

radial_bank는 CP3 hp-FEM H_l,M_l를 직접 diagonalize한다. 선언한 negative/positive mode 수를 얻지 못하면 실패하며 조용히 줄이지 않는다. 양에너지 mode는 finite-domain pseudostate이지 continuum measure나 all-bound tail이 아니다. 각 l의 m degeneracy는 full-m channels로 표현하고 별도 angular oracle로 검사한다.

## 독립 검사

정지 1s pair의 S=exp(-R)(1+R+R²/3), H_TT=-1/2-[1-(1+R)exp(-2R)]/R, H_TP=-S/2-exp(-R)(1+R)를 사용한다. v!=0 overlap은 azimuth를 J0로 적분한 별도 adaptive quadrature와 비교한다. S,H를 symmetrize해서 시험을 통과시키지 않는다. 임의 anti-Hermitian D 오염은 dot S 검사에 안 보이지만 direct-basis derivative 검사에 걸리는 negative control을 둔다.

새 tests는 원자 spectrum, full-m/positive-mode selection, FEM radial derivative, FEM-to-analytic 1s cross-center bridge, center exchange, rigid translation phase covariance, frozen generalized-H exponential, Gram projection, input/resource/rank guards를 포함한다. CP3의 exact moving-Coulomb negative control도 유지한다.

고정 operator case의 마지막 quadrature pair 변화 S/H/D는 별도 진단이며 원래 spatial 0.30% capture budget으로 승격하지 않는다. General high-n/positive radial-FEM cross-center quadrature의 전체 수렴은 아직 승인하지 않았다.

## 실행/보존

Source/test manifest, CP3 import mapping, stage receipts, 실제 테스트 logs 및 first failure를 보존한다. Runner는 직접 source 수정/패키지 설치/추가 LLM/전체 collision을 하지 않는다. 로그를 subprocess 실행 중 파일로 남기고 timeout/interruption은 생성한 process group에만 종료 신호를 보낸다. 성공/실패와 무관하게 새 return report/manifest/ZIP을 만든다.

직접 git clone은 이번 컨테이너 DNS 제한으로 실패했다. 신규 sidecar 전체 시험과 고정 수치 사례는 여기서 실행한다. 기존 전체 repository suite는 실행하지 않았다는 사실을 기록하며, PR workflow와 local profile에서 원 source 그대로 검사하도록 구성한다. 결과를 보기 전 그 시험을 PASS로 재사용하지 않는다.

## 다음 과학 단계의 위치

COMMON_CAPTURE_PILOT_CONTRACT.json은 미래의 별도 작은 capture 연구에 대한 고정된 초기 사양이다. 이번 validator가 자동 실행하지 않는다. S/H/D가 구현되었다는 사실은 high-n continuum/CAP/finite-time/b-grid 문제를 닫지 않는다. Production HOLD, all-bound OPEN, b-grid NO_GO.
