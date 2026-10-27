# REI selected finite-cohort information enclosure

## 목표와 완료 기준

기록된 유한 주입 cohort의 반환량을 기존 cumulative-response 정보집합에서 정확히 둘러싸는 식과 exact-rational 구현을 만든다. 기존 convolution과 causal-prefix closure는 재사용한다. 새 기여는 부호가 바뀌는 F-integral weight를 Stieltjes kernel로 바꾸고, cell extrema와 cumulative-chain LP를 유한 수준 DP로 구현하는 연결이다.

시작 HEAD fbb55bcd0c77990b62470862a9f4a70647d0c5c9; branch research/rei-causal-prefix-consumer-20261027; draft PR240. AGENTS blob6464cd96b7023e3e91e30246bc93650d4e435a10. 내장 physmath operating1.0.0과 사용자 현재 전체 R/C 요청을 적용한다.

이론의 완료 기준은 명시적 정의, sharp inf/sup 증명, 해석적 판별 사례, 독립 검토와 코드 계약이다. 코딩의 완료 기준은 구현, 실제 targeted tests, 독립 scientific/code 판정이다. 현재 실행 예산 HOLD로 남는 C6–C8 의무를 체크포인트 전달 완료와 구별한다.

## 정의

0=t0<...<tm, F(0)=0. F는 [0,tm]에서 비음수·비감소·우연속이다. 기존 closed bounds l/u를 받으며 l0=u0=0, 0<=l<=u<=cap, l/u 비감소다. all-time cap은 기존 계약대로 포함하고 tm 이후 constant extension이 가능하다. m=0이면 A=B=0이다.

선택된 주입 cohort의 h(s)는 [0,S]의 연속한 유한 partition에서 piecewise affine이다. segment마다 h(s)=beta+alpha*s; 양 끝 값이 비음수이면 충분하고 alpha<0도 허용된다. gaps는 명시적 zero segment로 제공한다. zero-length segment, overlap, implicit gap은 거절한다. 빈 segment tuple은 zero cohort다.

cohort 밖 h의 수학적 zero extension은 선택 연산이다. 전체 physical source가 S 이후 shutoff했다는 뜻이 아니다. 전체 source 반환량이라고 쓰려면 별도의 완전한 source history가 필요하다. CR109 실제 history는 [0,1e10]s에만 알려졌으며 이후 continuation/shutoff는 미정이다.

F는 같은 spectral template과 동일 frozen linear stationary response를 나타내야 한다. 같은 bath/state, frame, proper clock, fixed proper volume 또는 이미 공통-volume로 pullback한 조건을 유지한다. actual PHYS02 source100K와 CR108 response10000K는 아직 결속되지 않았다.

0<=A<=B<=tm. G(x)=integral_0^clamp(x,0,S) h(s)ds,
K_AB(tau)=G(B-tau)-G(A-tau).
C_cohort(T)=integral_0^min(T,S)h(s)F(T-s)ds,
D_AB=C_cohort(B)-C_cohort(A)=integral K_AB dF.

## 구현 계약

모든 numeric input은 type Fraction 자체여야 한다. float/int/bool/string 자동 coercion은 하지 않는다. 단위는 [h]=s^-1,[G]=[K]=1,[D]=[F]이며 F는 count 또는 kinetic-energy proper density다. 두 scalar를 별도로 계산한다.

cell(t_i,t_i+1]의 질량 m_i=x_i+1-x_i를 사용한다. q_i-/q_i+는 closed cell 위 K의 min/max다. 정확한 scalar 하한/상한은 feasible monotone x-chain 위 sum(q_i m_i)의 min/max다. 원래 F-space에서는 INFIMUM/SUPREMUM이며 달성은 자동 보장하지 않는다.

유한 수준 V={0,모든 l_k/u_k}에서 prefix min/max DP를 사용한다. DP만 O(m|V|) exact arithmetic이고 kernel extrema 전처리 및 정수 bit complexity는 별도다. cell candidate는 endpoints, shifted source breakpoints, piece 내 K'=0 rational root다.

여러 창의 목적함수는 K_comb=sum(weight_j K_j)를 먼저 구성한 다음 cell extrema/chain DP를 수행한다. 개별 sharp 상한 또는 개별 cell extrema의 합은 joint sharp 결과가 아니다. 하나의 chain과 cell 내부 atom 위치를 공유한다.

code: implementation/cohort_bounds.py; tests: implementation/test_cohort_bounds.py.
Frozen dataclasses와 deterministic witnesses를 반환한다. witness chain과 closure atom location은 finite LP witness이며 실제 attaining F라고 표시하지 않는다. 음수 weights의 combined kernel도 허용하되 단일 positive window와 해석을 구분한다.

## 보호하는 기존 과학

raw4/PREEXEC/큰 정수는 읽어 재직렬화하지 않는다. 기존 causal3189/3189PASS와 FD잔차2.7094758927889796e-10/기준2e-8을 재사용한다. 기존 affine16tests는 미실행으로 유지한다. source 대안은 합산하지 않고 N/E product는 outer information set이다.

actual recipient nb 미제공은 proper-volume와 null native projection을 유지한다. b=1.4e6m^-3 fixture는 actual nb가 아니다. SI 변환은 한 번, native25와 photon port는 별도, 변하는 b의 endpoint correction과 양쪽 quotient JVP를 유지한다. ddt/ddeta는 별도 인자이며 integrated event에1/H를 곱하지 않는다. 단일 event/energy 소유권을 유지한다.

## 자원과 게시

Planning 누적15.077490885,원 cap10,HOLD; 새 local scientific execution은 별도 예산 승인 전0이다. Main595.225063/600 NO_MORE_IVPs와 타 owner 예산·기존 예약을 유지한다. 이번 일반 실행 요청은 수치 cap16의 명시적 별도 승인을 제공하지 않았으므로 기존 제안을 자동 승인으로 기록하지 않는다.

Presentation inherited43.787562494,원 cap30,이번 bounded text/ZIP job 임시44.99,총 새 reservation1.0CPU s. 첫 helper가 stdin EOF로 종료한.053216를 포함한다. 첫 두 helper 누적.114047를 보존한다. 새 helper cap.65,최종 tail.10을 포함하고 측정값으로만 새 예약을 정산한다. 원래 누적/예약을 해제하지 않는다. UNKNOWN_NOT_ZERO 유지. 과학 실행을 presentation으로 분류하지 않는다.

각 단계 전 실제HEAD/AGENTS/반환/직전ACK 확인, independent review,expected-SHA/nonforce push,stageZIP,Drive/Dropbox completed ACK를 기록한다. 원래 DAG 작업32/88·중앙27/88·증분0,88IDs/17edges,기존 계약/status,L4false,globalphysicalcompletionnull을 유지한다.
