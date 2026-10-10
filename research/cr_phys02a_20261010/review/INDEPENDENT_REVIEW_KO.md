# CR-PHYS02A 독립 최종 판정

**판정: PROMOTE_SCOPED.** 고정된 PHYS01 source가 직접 생성하는 0.1–10 eV 전자에 대해,
classical superthermal leading-log Coulomb-only 감속을 prescribed electron bath에서 계산한
성분을 **derived / numerically checked / implementation-verified** 연구 결과로 승인한다.
문헌은 선택한 closure의 근거와 한계를 제공한다. 이 판정은 전체 secondary cascade,
near-thermal equilibrium, 물리 정확도 인증 또는 IGM 이력의 승인이 아니다.

상위 **CR-PHYS02-DELAY = OPEN**, **production history = HOLD**를 유지한다.
차단 결함은 없다. 아래의 두 작은 구현·기록 문제는 owner의 제한된 수정 후 해소되었다.

## 1. 검토자의 역할과 고정 대상

검토자는 별도 agent `/root/phys02_decision_review`이다. 이 후보의 생성, 구현,
기존 검증 설계 또는 최초 문헌 감사에 참여하지 않았다. 고정된 후보와 원 증거를 읽고
최종 decision gate만 수행했다. 검토 중 source/test를 직접 수정하거나 별도 물리
대안을 만들지 않았다. owner가 수정한 domain guard와 실행 기록만 추가로 확인했다.

호스트 선언 모델은 GPT-6 Astra Pro이며 모델·effort override는 요청하지 않았다.
실제 runtime model/effort는 별도로 관측하지 않았으므로 UNKNOWN으로 남긴다.
같은 호스트와 parent의 입력자료를 공유한다는 한계는 독립성의 범위에 포함한다.

적용 지침은 research harness `PROJECT_INSTRUCTIONS.md`,
`prompts/phases/08_external_decision_gate.md`, coding harness `AGENTS.md`다.
harness의 RESEARCH_STATE는 미실행 템플릿임을 확인했으며 연구 증거로 사용하지 않았다.

부모 commit은 `e41e18873af438ef989ff44f505fe2665118fdec`,
tree는 `1cf4f13e561f30e0418a50342b3a58c8917fa4ff`다.
parent materialization의 관련 source/packet에 대해 실제 byte size, SHA-256 및
git blob SHA를 import manifest와 대조했다. reviewer가 원격 checkout을 새로
수행한 것은 아니다.

최종 scientific payload의 핵심 SHA-256은 다음과 같다.

| 파일 | SHA-256 |
|---|---|
| src/causal_subthreshold.py | 2259506b74c16027fda69b479cb1039b0888e19c5f8dcf400273892aba6f39f9 |
| tests/verify_causal.py | 86e3a10cabfb490cd81053902c464042557897f04e6ffce8b0e5d5d249f17075 |
| evidence/NUMERICAL_RESULT.json | 4e210fb042c8b4d92fd8577b30af78686500de8d7b7ea89be5baeea6564ee1f8 |
| research/DERIVATION_KO.md | 28c10b0c6e1c0b349c62cb6f2bd84680e9e904bff83dfe556d7320515850a88a |
| state/SCIENTIFIC_CONTRACT.json | 125effef877f952499cb9f15b7655c51644c1221bdc07bcd7c58f60a7d25922a |
| inputs/PARENT_CR_PACKET.json | bb62be7ede32d43ece48d119903b542b2fc32f5be839cf40842ea559d02f0755 |

읽은 전체 대상과 로그의 identity는 `INDEPENDENT_DECISION.json`에 기록했다.
REPORT의 pending-review 문구를 본 판정에 맞게 확정하는 편집은 새 과학적 주장의
변경이 아니므로 추가 과학 리뷰를 요구하지 않는다.

## 2. 물리·수학적 판정 근거

### Terminal yield와 causal response

\(Y_c=\int_0^\infty k_c(a)\,da\)를 보존하는
\(k_c(a)\mapsto\lambda k_c(\lambda a)\)는 첫 시간 모멘트를 \(1/\lambda\)배 바꾼다.
따라서 terminal yield만으로 지연이 식별되지 않는다는 논증은 성립한다.
ramp source에 대한 terminal–causal 차이를 \(\min(a,t)\) 가중 적분으로 표현한
식도 부호와 적분범위가 일치한다. 양수 kernel과 고정 매질이라는 조건이 필요하다.

### 원 source와 시간 가중치

\[
A(W)=\sum_s n_{s,0}\int q_p(K)v_p(K)
             \frac{d\sigma_s}{dW}\,dK
\]

는 \({\rm m^{-3}\,s^{-2}\,eV^{-1}}\) 차원을 가진다. 초기 proton population이
0인 경우 \(N_p=tq_p\)가 leading local term이므로 \(Q_e=tA\)이며 상수 source가
아니다. 원 q의 전체 10 keV–1 PeV 정규화는 유지되고, 1–4 MeV는 실제 충돌
부분적분이다. Rudd 계수 분리와 직접 SDCS 적분의 연결, neutral target의
0.99 인자와 eV→J 변환을 확인했다. primary binding cost를 이 전자 kinetic
input 또는 bath heat에 중복 합산하지 않는다.

### Coulomb 계수와 감속 시계

Khrapak 원문 pp.1–3의 Eq. (6), cutoff 정의와 FS10 §§5–6의 Eq. (5)를 별도로
열어 대조했다. \( \mu=m_e/2\)이면
\(\rho_0=\kappa/\mathcal E\)이며 에너지율은

\[
b_{\mathcal E}=\frac{4\pi\kappa^2n_e}{m_ev}
 \ln\frac{v\mathcal E}{\kappa\omega_p}
\]

이다. SI 차원은 J/s이고 선택한 구간에서 로그와 감속률이 양수다.
binary momentum-transfer의 \(8\pi\)를 에너지율 계수로 곧바로 옮기지 않는
처리도 맞다. 동종 정지 target의 운동학
\(\Delta E=(v/2)\Delta p_\parallel\)와 일치한다.
[Khrapak (2020), Eq. (6)](https://arxiv.org/pdf/2006.00128),
[FS10, §§5–6](https://arxiv.org/html/0910.4410v1).

\(b(w)=\mathcal A\ln(Bw^{3/2})/\sqrt w\)에 대해 제시한 Ei primitive를
미분하면 \(T'(w)=1/b(w)>0\)가 된다. \(T(w_c)=0\),
\(w(a)=T^{-1}(T(w_0)-a)\), cutoff 도달 이후 별도 잔량 ledger라는 경계조건이
코드와 일치한다. FS10의 \(E>13.7\) eV 식을 현재 구간에 외삽하지 않는다.

### 순간 power, 누적 에너지와 cutoff

\[
P/A=\int_0^{\min(t,\tau_0)}(t-a)b[w(a)]\,da,\qquad
H/A=\frac12\int_0^{\min(t,\tau_0)}(t-a)^2b[w(a)]\,da
\]

에서 에너지 좌표로 변환하면 유도의 식 (5)–(6)이 나온다. \(dH/dt=P\)이고
\(P\,t\)를 누적 에너지로 사용하지 않는다. 초기 극한의
\(P/A\simeq b(w_0)t^2/2\), \(H/A\simeq b(w_0)t^3/6\)도 맞다.

cutoff에 대해 \(N_c/A=(t-\tau_0)_+^2/2\),
\(U_c=w_cN_c\), \(\dot U_c/A=w_c(t-\tau_0)_+\)를 확인했다.
\[
U_{\rm inj}=H_{\rm stop}+U_{\rm active}+U_c
\]
가 코드에 보존되며 \(U_c\)는 열이 아니다.

production 함수의 active energy는 subtraction으로 계산된다. 따라서 그 함수의
에너지 ledger만으로 독립 검증을 주장할 수는 없다. 그러나 제공된 테스트는
별도 forward ODE 궤적에서 storage를 직접 시간 적분하여 네 경우에 대조한다.
이 독립 수치 경로와 기록된 결과를 함께 고려하면 현재 bounded claim에는
충분하다. 두 방법이 같은 물리 closure·상수를 공유한다는 한계는 남는다.

## 3. 실제 읽고 대조한 실행 증거

reviewer는 신규 science suite나 기존 PHYS01 suite를 재실행하지 않았다.
읽은 실행 증거는 owner가 실제 실행한 최종 검산의 결과·stdout/stderr와
`EXECUTION_RECEIPT.json`이다. receipt에 보존된 실제 tool acknowledgement는
chunk `4e806a`, exit code 0이며 파일 SHA/size가 현 대상과 모두 일치한다.
따라서 이것은 reviewer 자신의 과학 실행이 아니라 검토한 owner 실행 증거다.

| 신규 검산 | 기록된 결과 |
|---|---:|
| Ei clock / adaptive 에너지 적분 | 최대 상대차 \(1.6078\times10^{-14}\) |
| ramp 응답·storage / forward ODE | \(1.3133\times10^{-13}\) |
| 분리 source / 직접 SDCS | \(3.5255\times10^{-16}\) |
| 64→96 source·kernel quadrature | \(1.2388\times10^{-12}\) |
| selected energy ledger | \(7.8498\times10^{-16}\) |
| local ramp / 정확 Bianchi source 세 표본 | \(6.9300\times10^{-7}\) |
| invalid input / zero·OFF / source partition | 기록된 기준 통과 |

9개 항목의 PASS_SCOPED, stdout와 결과 JSON의 endpoint·check 동일성, empty
stderr를 확인했다. 최초 cutoff-flux 추가 전과 fixed-density guard 추가 전의
결과도 남아 있다. guard 제거와 test 한 줄 제거로 과거 검토된 SHA를 정확히
재구성할 수 있어, 마지막 변경은 domain guard·거부 검사에 한정됨을 확인했다.
과학적 endpoint 값은 이전 결과와 동일하다.

\(10^{10}\) s에서 승인 가능한 정량 결과는 현재 stopping power
\(2.4153106338\times10^{-44}\ {\rm J\,m^{-3}\,s^{-1}}\), 선택 구간의 즉시 열화
proxy에 대한 비 \(0.2207645611\), 누적 주입 에너지에 대한 bath 전달
\(0.1557633959\), active kinetic \(0.8388935287\), cutoff 잔류
\(0.0053430754\)다. 모두 위 closure의 결과다.

보고서의 약 7.05% 규모 비교도 별도로 산술 확인했다. parent packet의
\(1.2093044642\times10^{-42}\ {\rm J\,m^{-3}\,s^{-1}}\)를 분모로 쓰면
\[
\frac{P_{\rm term,selected}-P_{\rm stop}}
 {P_{\rm heat,parent}}=0.07049798025544476.
\]
원 packet의 bytes와 import manifest의 SHA-256/git blob SHA가 일치한다.
이는 전체 heating suppression이나 엄밀한 하한을 의미하지 않는다.

## 4. 검토 중 해소한 두 문제

1. **고정 상태 밖의 전자밀도 허용.** 원 constructor가 임의의 양의 \(n_e\)를
   받아 fixed-study 계약보다 넓은 API를 제공했다. 고정 결과를 무효화하는
   결함은 아니었으나 오용 가능성이 있었다. owner가 canonical \(n_e\)만
   허용하도록 제한하고 \(n_e=1.0\) 거부 검사를 추가했다. 변경분과 최종
   실행 결과를 확인하여 닫았다.

2. **종료코드의 durable evidence 누락.** 원 보고서는 exit 0 기록을 언급했으나
   당시 전달된 파일에는 process acknowledgement가 없었다. owner가 command,
   cwd, 실제 tool 결과, exit 0과 최종 SHA를 receipt로 보존했다.
   reviewer는 그 기록과 실제 현 파일의 연결을 확인했다.

추가 blocking correction은 요구하지 않는다.

## 5. 승격 후에도 유지할 한계

- **고전적 조건:** 10 eV에서 \(\kappa/(\hbar v)=1.1664\)이므로 강한
  classical/quantum scale separation을 주장할 수 없다. leading-log 식의
  수치 적분 정확도가 실제 물리 오차를 보증하지 않는다.
- **열평형:** 0.1 eV에서도 \(E/(k_BT)=11.6045\)다. cutoff 도달은
  thermalization 완료가 아니며 residual을 heat로 전환할 수 없다.
- **bath closure:** stopping energy를 prescribed electron bath에 전달하는
  모형이다. neutral energy transfer, electron-ion exchange, energy diffusion,
  자기장, 실제 bath evolution 또는 전체 gas equilibration은 계산하지 않았다.
  \(\nu_{\rm neutral}<\omega_p\)도 실제 neutral-rate 측정·계산으로 인증한
  조건이 아니라 현재 Coulomb-only closure의 적용 전제다.
- **국소 전개:** \(Q_e=tA\)와 fixed bath는 \(H t\ll1\)의 새 근사다.
  \(6.93\times10^{-7}\)은 세 source-coefficient 표본의 비교이며 연속구간
  오차 인증이나 정확한 Bianchi electron history가 아니다.
- **소스 범위:** 직접 태어난 0.1–10 eV 전자만 포함한다. 더 높은 전자의
  cascade 유입, photon reservoir, near-thermal matching은 미완료다.
  full proton spectrum을 재정규화하거나 그 미모형 에너지를 heat로 채울 수 없다.
- **검증 범위:** 테스트가 공유하는 closure와 inherited inputs는 독립적인
  실험·관측 검증 대상이 아니다. 구현 일치와 문헌 근거를 물리 정확도 인증으로
  합산하지 않는다.

## 6. Decision gate

증거, 수학·물리의 내부 일관성, 시험 가능성, bounded robustness와 계산
가능성은 선언한 연구 성분의 승격에 충분하다. CR source에서 실제 시간응답을
얻으려는 원 동기도 보존되었다. 연구적 novelty는 여기서 확립하지 않았고
그 주장도 승인하지 않는다.

owner는 본 결과를 제한된 PHYS02A 성분으로 확정하고 선언된 PHYS02B의
absolute rates·branching·하향 flux 작업으로 진행할 수 있다. 상위 PHYS02,
receiver와 production history의 gate는 그대로 남는다. 이 scientific decision은
별도의 merge·외부 게시 권한을 생성하지 않는다.

