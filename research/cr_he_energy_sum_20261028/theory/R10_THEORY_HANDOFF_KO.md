# R10 이론 → 구현 인계

## 고정 결과

단위는 `CR_PHYS02_HE_ENERGY_SUM_V1`, 경로는 `research/cr_he_energy_sum_20261028`, PR114다. PR112 D729cb95164697d8122b0a85ae6e403b57392e724를 기준으로 별도 branch를 사용한다. 진행 중인 PR113의 four-bin full-Cartesian 지원 문제, 예산, 코드를 이식하지 않는다.

명시한 조건부 cap K에서 L={E<=K/2}, H={E>K/2}와 high complete-level tail B(h), eligible low prefix A(h)를 사용한다. delta=max(0,max_h[B(h)-A(h)]), dmax=(N-delta)/2, d의 대수적 구간=[0,dmax], 부모 coefficient=N-d다. 내림차순 high greedy와 residual low diagonals가 최대값을 달성하고, threshold dual이 exact certificate를 준다. 중간 target은 maximum doubles 축소와 residual singles로 구성한다.

## 구현이 보존할 의무

R09의 exact core/API와 byte-attested native adapter를 구현한다. 일반 정리의 E>=0 정의역과 retained PHYS02의 cutoff..10eV/3200active+ghost 정의역을 구분한다. cutoff equality는 stored binary64를 exact Fraction으로 lift하며 decimal1/5와2Eghost의 cap을 별도 처리한다. K와 assumption/source/state/unit digest를 묶고 stale binding을 거부한다.

Full selected support에서 p=0, species coefficient=(-N+d,N-2d,d), chemical=24.59N+29.83d다. Original consumer가 W와 nb를 각각 한 번만 적용한다. Native inventory gate W(N-d)<=Hneutral와 window/state/source/nb/replay 검사는 유지한다. 계산된 C는 해당 witness의 값이다.

R6의 수학적 finding은 모두 반영됐으며 C단계에서는 실제 positive/negative controls, 독립 generic oracle, 모든 saved native certificate 및 그림의 원문 검증이 남는다. R7 one8-second constrained CAS batch는 실제 완료했고 추가 CAS0, remoteCPU null이다. 새 Python40CPU-s budget은 C4 probe부터 실제 runner로 계측한다. 이전 단위 및 다른 owner의 예산은 이전하지 않는다.

ActualK/kernel/C/D/outside/donor/EOS/T/absolutevolume/fullphysicalnative25와 globalphysical/error/budget/currency는 null이다. 이론10/10과 전체workflow20/20은 별도 상태다. 이 단위의 C10 실제 전달까지 끝난 뒤 science_closed, 추가scienceallowance0, automatic_next_node=false로 닫는다.
