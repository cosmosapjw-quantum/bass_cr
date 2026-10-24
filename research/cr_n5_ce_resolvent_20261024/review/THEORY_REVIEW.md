# 독립 R6 이론·계약 검토

**판정: PASS_SCOPED_R6. 현재 blocking finding 0.**

검토자 `/root/provider_returns`는 provider raw intake와 독립 검토만 담당했다. 이 단원의 이론·구현을 작성하거나 새 과학 실행을 수행하지 않았다. 이 판정은 고정 이론과 실행 전 계약에 한정되며 준비된 구현 및 실제 primary 수치 결과의 C6/C9 승인을 대신하지 않는다.

## 검토한 고정 파일

| 파일 | SHA256 |
|---|---|
| FROZEN_CONTRACT.md | `44b43c42eff4b67a9d3c8ed4d49e53f3cb91c9c29b2413cca2a1761632215d2b` |
| THEORY_KO.md | `f98660d8288f54248016d1ecdf01627a9162fe99c9b55b924e68910585d971f0` |
| 저장 Wolfram two-state raw | `ec213fb1cfdde90c9bc3c43b3e8466f0682ab032a15738dcd096b17e8713eb57` |
| 이전 PR101 theory/THEORY_REVIEW.md | `9485079b4b269f7ff8bf2a5ce8de102260a97bef47cb23c85f0b59d85201dc4c` |

나머지 owner evidence·중복 조사 파일의 정확 경로와 hash는 동반 JSON에 있다. PR101 §4의 기존 survival/Feynman–Kac 유도를 다시 읽었으며 새 두 문서는 재사용을 명시한다. 새 기여는 채널별·source 조건부 유한-chain 수치값과 사건 에너지·시간 보상의 결속이다.

## 수학과 물리 판정

Q가 column population에 작용하므로 q 상태를 제외한 A의 transpose G가 backward generator다. A의 대각을 유지하면 q로의 손실이 남고 `a=-G1=Q[0,1:]`이다. 연결된 유한 birth-death chain과 비음성 hazard에서 `K=diag(h)-G`는 invertible M-matrix다. `K u_c=h_c`, `K u_abs=a` 및 `K1=h+a`는 비음성과 세 결과의 합1을 준다. 희귀 CE를 `1-u_abs`로 계산하지 않고 양의 RHS로 직접 푸는 계약이 적절하다.

`K r_c=E h_c`는 mark 직전 에너지의 비정규화 모멘트다. Laplace-resolvent의 미분으로 `K v_c=u_c`가 채널에 속한 사건시간의 비정규화 모멘트임을 확인했다. `K t=1`은 mark 또는 첫 진입까지의 시간이다. `(-G)w=h`는 unmarked 경로의 integrated hazard이고 `1-exp(-H)≤H`에서 total CE probability≤w가 따른다. 각 결과의 분모가0이면 conditional mean은 null이다.

원 W>q active mask와 가중치를 유지한 양의 두-node 투영은 count와 초기 kinetic energy를 보존한다. q,10eV,Delta를 grid에 넣어 최초 source를 CE-active node로 잘못 보내지 않는다. q에 투영된 질량은 즉시 진입하여 CE/time0이지만 원 active denominator에는 남는다. 이는 유한-grid 표현이고 continuum의 원 초기 위치에 대한 정확한 결과라는 주장을 하지 않는다. R40/R80의 새 행렬 조립과 기존 저장된 R40 population 또는 continuous MFPT 자료도 구분되어 있다.

물리는 T=10000K,ne0.14,n1s0.9,lnLambda20,stationary-heavy H1의 고정 bath다. 선택 source의10000proper-s exposure는 impulsive population 정의다. 초기 W<10eV가 경로의 상한은 아니므로 이후 EE 확산을 통한 CE가 허용된다. CE에서 electron kinetic energy Delta가 H1 internal energy로 옮겨가고 전하·핵종·전자수는 보존된다. mark에서 멈춤은 진단 종료이며 소멸, 영구 편입 또는 최종 가열이 아니다. 다른 CI/RR/DR/CX/EI/neutral 및 고차 채널, isotope transfer와 전체 first-event 경쟁률은 null을 유지한다.

## 실행 전 finding의 최소 교정

세 요청은 현재 고정 파일에서 모두 닫혔다.

1. **잔차 정의:** rowwise denominator `|K||x|+|b|`가 명시됐다. 정확히0인 denominator는 residual도0일 때만 ratio0이며 임의 양의 floor를 쓰지 않는다. generator conservation도 같은 convention을 사용한다.
2. **lambda controls:** toy a2,b3,c5,x7,y11, 공통 lambda0/1e-8/1과 한 absent-channel case, 허용오차 및 test budget이 고정됐다. 물리 primary는lambda1만 실행한다. 단조·오목성 일반 주장은 total CE에 대한 것으로 한정했다. 두-state의 rational formula, small-lambda slope와 저장된 다섯 True witness가 서로 맞는다.
3. **자원 한계 표현:** Linux에서 실효성이 없는 RSS-limit 주장 대신512MiB RLIMIT_AS와 측정 peakRSS를 구분했다. CPU0worker/thread1,CPU8coordinator, lease,실제cgroup/proc검사,create-only run과CPU/wallcap을 유지한다.

확률·partition·source conservation·에너지 장부·grid·boundary consistency 허용오차가 실행 전에 고정됐다. 비교 실패를 보존하며 허용오차를 자동 완화하지 않는다. 이 비교는 certified continuum/global error bound가 아니다.

## 비차단 주의와 다음 gate

사건 후 운동에너지 모멘트를 incident moment−Delta probability로 정의한 장부의 잔차는 산술 항등식의 검사다. 이를 독립 원자물리 검증이나 이후 radiation/bath heat의 계산으로 부르지 않아야 한다. 현재 계약의 first-event 범위는 이 구별에 맞는다.

이 R6는 실제 numerical admission이 아니다. 계획된 targeted controls와 독립 C9가 실제 코드·원 raw arrays·direct/adjoint/reference 일치를 확인해야 한다. source interpolation의 물리 오차, finite-mass 보정과 누락 채널의 오차는 알려져 있지 않다. 전체 N4/N5는 PARTIAL/OPEN이고 N6/N7은 미활성이다. `global_error_bound=null`, `global_completion_percent=null`을 유지한다.

EXECUTION | 독립 정적 R6 PASS; 새 science/provider constructor/moments/evaluate/ODE/quadrature/CAS0. PUBLICATION | 검토자 수행0. BACKUP | root 소유, 검토자 업로드0. DAG | R6 닫힘; 동결된 targeted 구현 검증과 root 승인 bounded primary로 진행 가능, 실제 결과 C9는 대기.
