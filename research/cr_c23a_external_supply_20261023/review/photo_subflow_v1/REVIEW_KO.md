# C23A photo_subflow v1 독립 검토

**판정: CHANGES_REQUIRED.** 283개 rate case / 1,915개 operator 호출 중 1개가 사전에 정한 population 절대 오차 기준을 넘었다. 기존 기준은 변경하지 않았다. 28개 invalid-input fail-closed 검사는 모두 통과했다. 새 ODE와 역사적 ODE 재실행은 각각 0회다.

## 고정 구현과 독립 기준

검토 source SHA256: `669b6f85f3046118032fab9b75154ca9ccecf6bcdbab75d5be6e40e075203735`.

oracle은 별도로 구성한 8×8 population/event generator에 mpmath 1.4.1의 80자리 `expm`을 적용한다. production의 uniformization, divided difference, event 계산 공식을 oracle에 재사용하지 않았다. H/He의 다섯 basis inventory와 두 혼합 inventory를 검사했다. 0/equal/nearly-equal/zero/extreme rate ratio와 theta 1e-14–1e6, 단위 변화, inventory scale, 실제 P19 table의 입력 규모를 포함했다. 상세 기준과 실행 자료는 PLAN.json, EXECUTION.json, OPERATOR_RESULTS.json에 있다.

## F1: HeIII 흡수 확률의 반복 제곱 반올림 오차

P19v1 row40(z=5.81)의 Gamma=(6.09e-13, 2.97e-13, 9.88e-18) s^-1, 동결 duration=1e17 s, HeI=1인 numerical stress case에서:

- HeIII computed: 0.62766702591859
- 80-digit reference: 0.6276670259206363307408193
- absolute/inventory error: 2.0463038291606273e-12
- predeclared limit: 2e-12
- He inventory and charge/event residual: approximately -2.04631e-12

실제 source의 rate를 사용했지만 이 장시간 동결 stress test를 실제 IGM 이력으로 해석하지 않는다. positive Poisson tail의 6.109e-35 진단은 명시한 exact-arithmetic truncation에만 해당한다. 이 실패는 series truncation보다 반복 제곱의 rounding에서 발생하며, 별도 analytic entries 교체 후 K20과의 열 보존 일치가 손실된다. population clipping이나 normalization은 관찰되지 않았다.

## 최소 교정의 독립 대수 확인

두 waiting time의 convolution에서 a,b>=0에 대해 K20=1-(b exp(-a)-a exp(-b))/(b-a), a=b에서는 1-(1+a)exp(-a)이다. m=min(a,b), d=abs(a-b)를 대입하면:

`K20 = F(m) + m exp(-m) G(d)`

`F(x)=1-(1+x)exp(-x)`

`G(d)=1-(1-exp(-d))/d`, `G(0)=0`.

F의 양의 급수는 exp(-x) x^2 sum(k>=0) x^k/(k+2)!이다. G의 양의 급수는 exp(-d) sum(n>=1) n d^n/(n+1)!이다. 따라서 두 극한과 0 rate를 포함하는 양의 평가가 가능하다. 제안식과 독립 80-digit matrix exponential의 15쌍 비교 최대 절대차는 1.05421979432e-81이었다. 해당 비교는 새 production 코드의 채택 판정을 대신하지 않는다.

## 물리 범위 검토

고정 z/proper volume의 외부 조절 rate-moment source라는 해석은 코드와 일치한다. 에너지와 population은 caller의 고정 reference당 값이다. N_particles=sum(nuclei)+free electrons를 사용한 T=2U/(3 k_B N)는 선언한 비상대론적 단원자 이상기체 열 에너지에 맞는다. 광이온화 event마다 전자 하나가 생기고, 외부 에너지=caller binding registry+지정 excess-heat moment라는 장부는 조건부로 일관된다.

source 수치 threshold convention은 미확정이며 코드가 이를 표시한다. 5개 H/He 명시 입력만 허용하고 21종 네트워크나 finite photon reservoir, secondary degradation, radiation injection/transport, 전체 IGM 이력을 완료했다고 주장하지 않는다. 독립 재구성한 binding-state ledger도 검사했으며 F1의 rounding 영향이 나타난다.

## 상태

- EXECUTION: scoped review 완료, v1 numerical FAIL 보존.
- PUBLICATION: 부모 통합 대기.
- BACKUP: 로컬 create-only 검토 자료. reviewer의 외부 backup은 NOT_RUN.
- DAG: C9 v1 완료; 구현 교정 및 v2 검토가 다음 의존 단계.

자원: CPU4, native thread1. main audit wall 11.074991981 s / CPU 11.035756485 s. global_error_bound=null.
