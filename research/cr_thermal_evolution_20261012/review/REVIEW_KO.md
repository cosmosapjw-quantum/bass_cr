# BASS_CR 다음 이론 루프 독립 검토

## 판정

**PROMOTE_SCOPED — TH1–TH7을 명시된 가정 아래 완결된 조건부 이론 결과로 승인한다.** 검토 대상은 이동 cutoff의 moment 수지, thermal/all-free 표현의 정확한 동치, 공통 충돌시계의 재사용, 실제 Coulomb 식의 밀도 보정, 비가환 잔차와 에너지 장부의 오차한계, 허용 구간 안의 충돌시계 선택, 누적 열침적에서 팽창하는 열에너지와 온도로 이어지는 오차증명이다. `receiver_interface.py`의 네 순수 함수와 이번에 실행된 좁은 검산 범위도 함께 수용한다. 열린 과학적 차단 사유는 없다.

검토자는 후보 유도와 소유자 검산의 설계에 참여하지 않았다. 후보의 최종 식을 별도로 유도하고 실제 코드·출력과 대조했다. 검토자 자신의 과학 실행은 **0회**이며, 소유자의 15개 검산과 후보 저자의 21개 Wolfram 기호 검산은 실행 기록을 읽어 평가했다.

## 고정된 검토 대상

후보 manifest는 `review/CANDIDATE_MANIFEST.json`, SHA-256 `f63c832e8b9ab2e40092cc2d0c0f2b27c4a10448e925754febd9b845afbc9eb2`이다. 13개 파일의 byte 수와 SHA-256이 모두 일치함을 확인했다. `latex/manuscript.md`는 검토한 보고서와 세 유도 문서를 지정 순서대로 연결한 내용과 정확히 같다. 각 파일의 전체 해시는 `DECISION.json`에 복제했다.

이전 과학 결과는 science commit `5fc11143679fe1950133b1e268ac3dd248f6429b`와 결과 SHA-256 `dd4ed10b5ecd3aea8a8710b5190c9d7da4085834713bc72ae2cc37915cc97f27`에 묶인 근거를 재사용했다. 이전 유도의 §6·§8, 계약·판정, 현재 소스의 stopping·projection·generator 관련 부분을 읽었다. 이번 판정은 기존 실행의 재현 실행을 요구하지 않는다.

## 핵심 심사 결과

| 주장 | 독립적으로 확인한 핵심 | 판정 |
|---|---|---|
| TH1: 이동 cutoff | Heaviside 경계 미분으로 ​`dot W_c − b` 부호를 확인하고, 수·실제 에너지·운동량 moment에 적용했다. 연속 경계 이동, jump daughter, 직접 source를 구별하고 anisotropic pressure work를 유지했다. | 조건부 증명 승인 |
| TH2: thermal/all-free 동치 | `u_ex = u_A − (3/2) k_B T n_A`의 미분에 포함되는 `−(3/2) k_B n_A dot T`를 보존하면 정확히 thermal 수지로 되돌아간다. Primary birth만 있는 판별 예에서 온도 변화가 0인 것도 일치한다. | 정확한 변수 표현으로 승인 |
| TH3: 공통 충돌시계 | `X = Vx`, `dτ = a dt`에서 변환 source가 `Vs/a`, 물리적 열률이 `a h_0 X/V`임을 확인했다. 누적 comoving 열 장부와 SI 수 출력 단위도 일관된다. | 정해진 유한 연산자와 공통 계수 아래 승인 |
| TH4: 밀도/Coulomb 보정 | 실제 stopping 식의 두 logarithm이 모두 `−log(d)/2`만큼 이동하므로, 양의 log 영역에서 `G(d) = dG(1) − d log(d) C_0/2`가 정확하다. | 고정 grid·조성·재분배 영역에서 승인 |
| TH5: 비가환 잔차 | 실제 propagator를 쓴 Duhamel 식과 양의 가중 column 수지로 상한을 얻었다. 완전한 열에너지 장부를 붙이면 에너지 norm의 contraction으로 누적 침적도 제어된다. | stated passivity 가정 아래 승인 |
| TH6: 충돌시계 선택 | 표시된 계수 잔차 상한의 scalar 최소화는 가중 중앙값 문제이며, 허용 구간에 대한 clipping과 영 가중치 경우가 필요하고 반영되어 있다. | 해당 상한의 최소화로 승인 |
| TH7: 열침적→온도 | 공통 팽창에서 적분인자와 Stieltjes 부분적분을 사용하면 시간 전체의 누적 침적 오차가 종점 열에너지 오차를 제어한다. 이어 정확한 EOS 차이식이 온도 상한을 준다. | 양의 thermal 수 하한과 완전한 열 source 아래 승인 |

### Exact kinetic 분할과 thermal closure

동일한 kinetic 분포를 cutoff 위·아래로 정확히 나누면 내부 경계의 수·에너지·운동량 항이 상쇄된다. 그 아래 부분을 단일 온도의 이상기체로 치환하는 단계에는 문서에 선언된 thermal closure가 들어간다. 두 단계의 성격이 최종 원고에서 구별되어 있다. Cutoff가 감소하여 역방향 전이가 생기면 아래쪽 upwind trace를 지정해야 한다. 저장된 cutoff 출력에 처음부터 cutoff 아래로 주입되는 source가 포함되는 실제 `project()`의 ghost 동작도 MC37에서 직접 연결되어 있다.

### All-free 표현을 닫는 항

`n_all = n_th + n_A`의 `n_th`는 thermal 핵과 thermal 전자를 모두 센다. Excess 상태는 부호가 가능한 기준 에너지이며, positive energy norm에 추가할 독립 에너지 장부로 해석하지 않는다. T.9의 곱 미분을 T.7에 대입하면 열용량은 정확히 `(3/2)k_B(n_all − n_A)`가 된다. 따라서 활성 전자가 새로 생겼다는 이유만으로 그 전자를 thermal 열용량에 포함하는 오차를 피한다. Active stress에는 상대론적 운동량 moment를 유지하고, thermal bath에는 선언한 비상대론적 EOS를 적용한다.

### 누적 침적에서 팽창하는 thermal energy로

T.19–T.22에서 `μ = (V/V_0)^(2/3)`와 완전한 누적 thermal deposition `H`를 쓰면 `U(t) = μ(t)^−1[U(0)+∫μ dH]`이다. 두 해의 공통 `V(t)`를 고정하고 `|δH(s)| ≤ B_H(s)`를 적용한 부분적분은 T.21을 직접 준다. 팽창하며 `B_H`가 비감소하면 T.22의 계수 `2 − 1/μ`가 따른다. 여기에 T.18의 열에너지·입자 수 오차식을 적용하는 연결은 완결되어 있다. 실제 관측량 허용오차를 나중에 선택하더라도 이 조건부 정리의 성립에는 영향이 없다.

## 실행 근거와 그 범위

소유자의 `results/THEORY_CHECKS.json`은 **15/15 PASS**이다. Exact rational 판별식, 실제 소스에서 분리한 stopping 함수의 30개 계수, 하나의 8-state 무차원 비가환 IVP를 포함한다. Stopping 밀도 분해의 최대 상대 잔차는 `2.6866 × 10^−16`, IVP의 정확한 기준 해와의 최대 차이는 `1.1155 × 10^−12`였다. 비가환 toy의 상태+열 장부 오차 `0.069916`은 상한 `0.264241` 아래이며, 최종 온도 오차 `0.0052483`은 전파된 상한 `0.161141` 아래이다. 이 수치들은 코드·결과에서 읽은 무차원 판별 사례의 값이다.

후보 저자가 실행한 `results/CLOCK_SYMBOLIC_CHECKS.json`은 **21/21 PASS**이며 원시 성공 응답과 스크립트까지 읽었다. 강화된 두 단계 정확해는 시간에 따라 달라지는 `V`, `a`, `q`를 사용하므로 source Jacobian과 물리적 열률 prefactor를 각각 판별한다. 이 검산의 실행 주체는 후보 저자이며, 이번 독립 심사의 근거는 앞 절의 별도 해석적 유도와 코드·증거 읽기이다. 기존 suite, 전체 generator, transport, NCP를 새로 실행하지 않았다.

## 제기한 사항과 해소

| ID | 확인이 필요했던 사항 | 최종 반영 |
|---|---|---|
| TR-01 | `P_h`의 연속 손실과 직접 jump heat 범위 | T4와 T.2 설명에서 heat와 나머지 매질 손실의 소유권을 명시했다. |
| CR-01 | 에너지 좌표에서 SI 수 출력으로의 변환 | 1.2a와 `D_SI` similarity/source 변환에 `epsilon_eV` 인자를 명시했다. |
| CR-02 | 허용 구간 밖의 weighted median | CC6에서 구간 clipping과 전체 영 가중치 경우를 명시했다. |
| CR-03 | 정규화 source 모양의 잔차 부등식 | `b, b_hat ≥ 0` 가정을 명시했다. |

네 사항은 모두 닫혔다. 새로운 broad no-go를 제안하지 않는다. 다음 이론 구성은 고정 event matrix와 비음수 계수, thermal/active/원자 에너지·수의 공통 event increment를 사용해 `T`·H/He feedback을 포함하는 양의 보존적 한 step을 만드는 작업으로 진행할 수 있다. 새 DAG의 여덟 노드와 이 다음 연결은 현재 승인 범위와 맞으며, 실제 선택 시나리오를 적용하는 기존 downstream 노드는 유지되어 있다.

## 기존 문헌과 기여의 해석

운동론 moment, 공통 계수의 시간변환, variation of constants와 양의 계의 가중 norm, 가중 중앙값 최소화는 알려진 수학적 방법이다. 승인한 기여는 이 방법들을 BASS_CR의 실제 상태·event·cutoff·source·단위와 연결한 완결된 구성, 이전 all-free 표현에서 빠져 있던 기준 에너지 미분의 복구, 실제 Coulomb 식의 정확한 분해, 그리고 thermal EOS까지 이어지는 조건부 오차증명이다.

참조한 primary 문헌의 읽기 범위는 다음과 같다. [Sarbach–Zannias, arXiv:1303.2899](https://arxiv.org/pdf/1303.2899)의 p.3 convention, pp.20–21 Proposition 6와 식 62–63, p.24 식 76; [Thomas–Pfrommer, arXiv:1805.11092](https://arxiv.org/pdf/1805.11092)의 §6.3 식 125–131과 thermal EOS 식 7을 읽었다. [Söderlind 2006, DOI 10.1007/s10543-006-0069-9](https://link.springer.com/article/10.1007/s10543-006-0069-9)는 공식 metadata·abstract·references와 저자 저장소 metadata만 확인했다. 해당 논문의 읽지 못한 정리에 판정을 의존하지 않으며, 필요한 유한차원 부등식은 직접 심사했다.

## 판정 뒤의 최종 조판 연결

이 판정은 위 frozen manifest를 유지한다. Root의 figure width 조정, 중복된 수동 subsection 번호 제거, 표의 `독립적인 정확 기호 대수`를 `정확 기호 대수`로 고치는 attribution 정정, 그리고 승인 상태를 반영하는 metadata 변경은 과학 내용 변경 없이 적용할 수 있다. Root는 정확한 차이와 최종 byte identity를 `review/POST_REVIEW_BINDING.json`에 연결한다. PDF의 시각 검토는 root가 맡는다. 식·가정·과학 코드·실행 결과가 바뀌면 그 변화에 대한 한정된 추가 검토가 필요하다.
