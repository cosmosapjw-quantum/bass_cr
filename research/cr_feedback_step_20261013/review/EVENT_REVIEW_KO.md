# 사건 갱신 분과 독립 심사

연구 단위: CR-THEORY-FEEDBACK-20261013. 검토자: /root/feedback_literature_review.
판정: **ACCEPTED_CONDITIONAL_DERIVATION — event branch**. 차단 지적: **0개**.
통합 고정점·기하학·실행 검토는 별도 최종 판정에서 합친다.

## 심사 독립성과 실제 근거

검토자는 후보 수식 작성, 구현 작성, 작성자 검산 설계에 참여하지 않았다.
완성된 유도, reference module, 사건 JSON, 검산 프로그램과 실제 결과를 읽었다.
독립 방법은 재고 감소량의 직접 상계, 사건별 보존 행의 수기 대입,
EOS의 유한 차분 역대입, 코드의 support·분모·출력 순서 대조다.
작성자가 수행한 정확 유리수 9개 검산은 기존 실행 근거로 재사용했고,
이 검토에서 과학 검산을 재실행한 횟수는 0이다.

## 1. 공유 소비량 상계

S의 음의 부분을 C, 양의 부분을 P라 쓰면 실제 감소량은
D_i=Σ_r C_ir ξ_r이고, 실제 생성량은 P_i=Σ_r P_ir ξ_r다.
초기 재고 y_i^n>0를 감소시키는 모든 사건의 분모에는 같은
c_i/y_i^n 항이 들어간다. 다른 감소 재고에서 온 항들은 비음수다.
따라서

$$
D_i\le \frac{h\sum_r C_{ir}f_r}{1+h c_i/y_i^n}
=\frac{h c_i}{1+h c_i/y_i^n}<y_i^n
$$

이며, 마지막 부등식은 c_i=0일 때 D_i=0으로 읽는다.
생성항을 더하면 문서 ES.16의 양의 하한이 그대로 나온다.
초기 0인 행을 감소시키는 사건을 먼저 비활성화하고 c_i를 계산하므로,
0 재고에서도 나눗셈과 음수 출력을 피하면서 관련 없는 사건들은 작동한다.
이는 여러 반응이 같은 thermal energy와 종을 공유하는 경우를 포함한다.
유한한 비음수 proposal과 유한 h≥0의 전체 범위에서 증명이 닫힌다.

## 2. 물리적 사건과 불변량

ES.7의 active impact는 active count 변화가 0, thermal electron 변화가 +1,
ionic charge 변화가 +1이다. Parent–daughter energy 차이는 I_r+ε_s이고,
chemical energy와 thermal energy에 각각 I_r, ε_s를 더해 합을 보존한다.
ES.8은 active 전자 하나의 E_L 전체를 thermal 에너지에 전달하면서
같은 전자를 thermal count로 옮긴다.
ES.9는 thermal electron 수를 하나 늘리고 U에서 I_r를 빼며 chemical
energy에 I_r를 더한다. 순 stoichiometry에 남지 않는 입사 thermal electron의
존재는 proposal의 초기 질량작용 인자에 포함된다.
ES.10은 thermal electron과 높은 이온화 단계의 수를 줄이고,
U에서 ε_rℓ, chemical energy에서 I_r를 제거해 R에 I_r+ε_rℓ를 더한다.
세 이온화 단계의 chemical energy 행, 특히 HeIII의 I_HeI+I_HeII가 맞게 들어 있다.

모든 event column에 Ls_r=0이 성립하므로 한 번 계산한 extent를 모든 행에
동일하게 쓰는 ES.15는 모든 후보 평가에서 Ly를 정확히 보존한다.
R는 방출 당시의 유출 에너지 누적 장부라는 정의에 따라 해석했다.
고정 부피·고정 에너지 channel 및 thermal closure의 범위가 명시되어 있다.

## 3. EOS와 정확도

N_th=N_H+N_He+N_e에서 원자핵 수가 보존되므로 ΔN_th=ΔN_e다.
T=U/(c_vN_th)를 전후 상태에 적용해 공통 분모를 취하면 ES.19가 나온다.
초기 U>0와 양의 총 원자핵 수에서 새 T>0이며, signed U_ex를 양수성 재고에
넣지 않고 최종 상태에서 재구성하는 연결도 이전 TH2와 일치한다.

ES.21의 일차 정합성은 f(y^n;y^n)=R_event(y^n), 국소 유계·Lipschitz,
z_h=y^n+O(h)에서 직접 나온다. 이는 정칙 branch의 O(h²) local error다.
전체 구간의 일차 오차에는 문서가 명시한 안정성 조건을 함께 사용한다.
ES.22–ES.23의 A+B 사례는 k h/(1+2kh)와 k h/(1+kh)의 차를
직접 통분하여 제시한 O(h²) 표현과 일치한다.

## 4. 구현과 작성자 실행 기록

capacity_step은 음의 순증분 C를 만들고, zero-donor support를 적용한 rates에서
공유 loads를 계산한 뒤 각 사건 분모와 extent를 계산한다. 모든 출력은 그 extent
하나로 갱신한다. 구현의 retained_lower_bounds는 증명 ES.16과 같다.
base_mass_action_proposals는 고정 초기 재고와 전달된 후보 계수를 분리한다.
thermal_count와 temperature는 ES.5와 일치한다.

EVENT_CHECKS.json의 입력 manifest 3개는 실제 파일의 크기와 SHA-256에 모두 일치했다.
작성자 결과는 9/9 PASS이며, 예제 문턱·단위는 무차원 유리수 판별 입력으로 명시돼 있다.
대표 실제 결과: 10개 사건×4개 불변량의 40개 정확 영잔차,
h=10^12의 공유 재고 갱신, 0 H·0 U 경계의 사건별 locality,
6개 흡열 채널의 공통 U 제약, ionization·capture EOS, binary local error,
h=0 및 음의 입력 거부.

## 5. 검토 대상 identity

| 파일 | bytes | SHA-256 |
|---|---:|---|
| derivations/EVENT_STEP_DERIVATION_KO.md | 15774 | 3c74e7af3aa29403753259bbe8902324c97bb811f4304716b9c1820a3a75bb9f |
| event_capacity_step.py | 8935 | 3683f0577263c2c7113593f6e3085b886b65b44101d438f6dd53f9762848e85c |
| examples/H_HE_EVENT_FAMILY.json | 6648 | 93353e1d2d26bac5706daac597cda5108358aff7b2ed46dc0b62373f59e6e965 |
| checks/run_event_checks.py | 8173 | 8421de464decc2c3c42d8293196d9571da8dcd6c675f8d68e8b7c1ddf1302c08 |
| results/EVENT_CHECKS.json | 3979 | e8f732fb26b73a15ddd995533e68e70866fcfb33d4b7531d26071c2ea4e6c2f4 |

문헌 적용 범위는 ../LITERATURE_KO.md와 ../SOURCES.json에 기록했다.
이 사건 갱신의 직접 상계는 선행 PMPRK 논문의 일반 비선형 존재 추측을 의존성으로 사용하지 않는다.

