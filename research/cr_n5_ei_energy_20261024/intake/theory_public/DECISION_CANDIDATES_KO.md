# N5 다음 구성 단위의 판별과 이론 연결

관측일 2026-10-24. 이 파일은 R1–R6 사전 연구 선택/유도 산출물이다. 새 과학 실행은 0이다.
사용자가 제공한 physmath-research-loop 내장 규약 1.0.0과 R/C·근거·런타임 참조를 읽었다.
Root가 실제 HEAD/AGENTS/병렬 owner/예산/자원을 결속한 뒤 실행 계약을 정한다.

## 선택: 질량 의존 electron–ion 에너지 교환

현재 PR102 coverage의 실제 공백인 charged-ion 에너지 drift/diffusion을 표준 선형 Landau–Rosenbluth 연산자로 연결하는 단위가 가장 직접적이다.
PR59의 기존 코드는 같은 질량 Maxwell 전자 bath이다. PR60–64는 네 label의 전자 Coulomb Landau, 유한 bath·연속체 tail·경계 trace 및 photon source projection 연구다.
따라서 그 정리/계산을 재실행하지 않고 질량 의존 EI 입력과 실제 C23D source 관측량만 추가할 수 있다.
PHYS84와 HE-ANG, 새 PHYS87 nuclear owner의 범위를 중복 구현하지 않는다.

### 판별한 세 후보

| 후보 | 새 과학 내용 | 입력/소유권 상황 | 결정 |
|---|---|---|---|
| 질량 의존 EI 에너지 교환 | 기존 equal-mass EE에 실제 H+/He+/He++의 drift/diffusion·상대 크기·first-entry 효과와 반대 bath energy 장부 추가 | 표준 Landau 원전과 C23D 수밀도 계약 존재. H1/He4 질량 선택은 새 명시적 conditional closure | 우선 |
| PI–RR Milne pair | same-source ground-state PI로 tagged RR capture kernel과 photon-energy moment 구성 | C23E는 H-equality/VF 총 RR 조건부 모형이며 실제 isotope Milne pair open. 원자 state/degeneracy/fit validity/owner boundary 조사 추가 필요 | 후속 source 입수 단위 |
| CE 이후 반복 jump/reward | E→E−Δ 양의 jump를 붙여 다중 CE·원자 내부에너지·stop 관측량 연결 | PR102 first mark는 완료, PHYS83 frozen atomic star도 완료. 고정 target/decay/재충돌 owner를 새로 분명히 해야 하며 EI 공백보다 간접적 | 보류 대안 |

PHYS81 finite CI 경쟁은 tabulated floor와 chemical threshold gap의 unknown을 그대로 처리해야 한다. 그 gap을 0으로 채우는 새 consumer는 채택하지 않는다.

## 고정된 실제 입력

원 C23D science
d04b2a56adb4a5d55b901420aa544332b41f6dbb,
research/cr_c23d_finiteT_source_bridge_20261024/FROZEN_CONTRACT.md,
Git blob 5cd596b8ddd3e0878bd612d300673c522311eebb를 실제 조회했다.

- HI=.9, HII=.1, HeI=.07, HeII=.02, HeIII=.01 cm^-3.
- 초기 thermal ne=.14 cm^-3와 total ne=.14 cm^-3의 구분된 필드.
- T=10000 K, prescribed lnLambda=20, proper seconds, bath rest frame, no escape.
- 원 자료는 elemental H/He label이다. H1/He4라는 질량 해석을 채택한다면 이번 새 조건부 resolution으로 명시해야 한다. 기존 source가 isotope abundances를 공급했다고 쓰지 않는다.
- D/T/He3/Li6/Li7 density는 원 C23D에서 미공급이다. 그 total contribution은 null이다. 매개변수/단위밀도 kernel을 제공하는 것과 실제 구성 기여를 분리한다.
- C23D 저장된 384 source atoms ×3z와 PR102 저장된 chain 결과를 재사용한다. 이미 완료한 EE/CE 실행은 다시 호출하지 않는다.

원 기준은
Gamma_ee=4 pi ne [e²/(4 pi epsilon0)]² lnLambda/m_e²,
b_ee(E)=m_e Gamma_ee/(epsilon_eV v(E)).
PR59 loss_anchor는 E=theta의 동일 b다.
Gamma는 고정 prescribed leading log이고 self-consistent screening 산출물이 아니다.

## 표준 Rosenbluth 식에서의 직접 유도

전자 질량 m=m_e, 이온 species b의 질량 M_b, 전하 Z_b e, 밀도 n_b, bath 온도 theta_b=k_B T_b/epsilon_eV를 둔다.
r_b=M_b/m, s_b²=2 epsilon_eV theta_b/M_b, x_b=v²/s_b²=r_b E/theta_b.
A(x)=erf(sqrt(x))−2 sqrt(x) exp(−x)/sqrt(pi)=P(3/2,x).
A'(x)=2 sqrt(x) exp(−x)/sqrt(pi).

Rosenbluth 원전의 velocity drift/covariance는 다음 convention으로 쓴다.

H_b(v)=n_b erf(v/s_b)/v,
g_b(v)=integral f_b(v') |v−v'| d³v',
tr Hess g_b=2H_b,
g_b''(v)=n_b s_b² A(x_b)/v³.

gamma_b=4 pi Z_b² [e²/(4 pi epsilon0)]² lnLambda_eb/m²는 밀도를 제외한다.
mean(dv)/dt=gamma_b(1+m/M_b) grad H_b,
Cov(dv)/dt=gamma_b Hess g_b.

E=m v²/(2 epsilon_eV)에 Itô 공식을 적용한다.

mu_b(E)
= gamma_b m/epsilon_eV [ v(1+1/r_b)H_b'(v)+(tr Hess g_b)/2 ]
= b_b(E)[erf(sqrt(x_b))−(1+1/r_b)A(x_b)]
= b_b(E)[A'(x_b)−A(x_b)/r_b],

D_b(E)
= m² v² gamma_b g_b''(v)/(2 epsilon_eV²)
= theta_b b_b(E) A(x_b)/r_b,

b_b(E)=gamma_b n_b m/(epsilon_eV v(E))
=b_ee(E) (n_b Z_b²/ne) (lnLambda_eb/lnLambda_ee).

현재 convention은 Var(dE)=2D_b dt이다. mu는 eV/s, D는 eV²/s다.
마찰의 (1+1/r_b)는 에너지 변환에서 수직 diffusion heating과 결합하므로 최종 D에 잘못 붙이면 안 된다.

## 구조와 극한

C_b F=-partial_E(mu_b F)+partial_E²(D_b F)
=partial_E{D_b[partial_E F+(1/theta_b−1/(2E))F]}.

따라서 p_b(E) proportional sqrt(E)exp(−E/theta_b)는 zero-current stationary density다.
이는 mu_b=D_b'+D_b(1/(2E)−1/theta_b)로 직접 확인된다.
같은 T의 이온과 전자는 동일 p_theta를 가지므로 D_total=D_ee+sum D_b로 양의 common-weight generator를 구성한다.

- r_b=1이면 같은 density/charge/log에 대해 PR59 계수와 일치한다.
- n_b=0 또는 Z_b=0이면 그 정의된 Coulomb contribution은 정확한 0이다. 미공급 n_b=null과 별개다.
- E≫theta_b/r_b에서 mu_b≈−b_b/r_b, D_b≈theta_b b_b/r_b.
- 고정 E>0,T에서 M_b→infinity이면 energy exchange→0. 각 산란은 남으므로 angular scattering이나 momentum-transfer frequency를 이 energy loss와 같은 rate로 쓰지 않는다.
- 작은 x는 erf−exponential 직접 뺄셈 대신 positive gammainc/series를 사용한다. A(x)=4x^(3/2)/(3sqrt(pi))[1−3x/5+3x²/14−x³/18+...]. r가 크다는 이유로 모든 E에서 A=1로 두면 원 source의 극저에너지 heating 영역을 지울 수 있다.

원자 전하/핵종/자유전자수는 elastic EI에서 변하지 않는다.
에너지 owner는 같은 순간 electron kinetic drift와 반대 ion bath energy이다.
fixed bath를 실제 온도 feedback 또는 N6 활성화로 해석하지 않는다.

## 새 물리 관측량과 비교 식

가장 작은 유용한 구현은 per-species/source-atom mu_b,D_b, source-weighted initial pulse ion heat,
same-grid common-conductance EI generator와 q-first-entry mean/reward이다.
완료된 EE 결과를 저장된 기준으로 읽고, 새 combined EE+EI만 새 run ID로 계산한다.
CE first-mark 확률을 함께 바꾸는 경우에도 PHYS83 cross section과 PR102 baseline bytes는 재사용한다.

같은 theta에서 q=chi theta, E≥q라면
D_EI/D_ee = sum_b [eta_b/r_b A(r_b E/theta)]/A(E/theta)
≤delta_max=[sum_b eta_b/r_b]/A(chi),
eta_b=n_b Z_b²/ne (동일 prescribed lnLambda일 때).

MFPT의 기존 양의 표현
T(E)=integral_q^E dz [D(z)p(z)]^(-1) integral_z^U p(u)du
를 재사용하면
T_ee(E)/(1+delta_max)≤T_ee+EI(E)≤T_ee(E)
가 같은 finite interval/BC에서 성립한다.
원 active source 가중 평균에도 동일하다.
같은 p_i를 사용하는 reversible birth-death chain에서는 edge conductance에 같은 bound를 적용해 정확한 유한-chain 버전을 얻는다.
이는 old EE science를 재실행할 필요 없이 새 species contribution의 효과를 제한한다.
이 MFPT 단조성을 CE killed-resolvent 확률에 그대로 전용하지 않는다.

선택 CE stopping까지 bath reward를 계산한다면,
Q_b가 q를 포함하는 full generator일 때 transient state의 물리 에너지 drift는
d_b=(Q_b^T E)_transient이다.
K=diag(h_CE)−G_total에 대해 K H_b=−d_b를 풀면 stop 이전 ion bath reward다.
q 경계 이동의 실제 에너지 E_q를 누락하지 않는다.
CE 전 energy를 terminal로 쓰면 E_initial=E_terminal+sum bath H;
CE 후 terminal을 쓰면 internal Delta*P_CE를 추가한다.
두 convention을 혼합하거나 cut-entry에 별도의 heat를 다시 넣지 않는다.

## 위험에 맞춘 검증 계약 제안

1. 원 C23D anchor 및 source bytes identity, ion composition/charge sum와 mass convention.
2. r=1 환원, Maxwell zero-current, density/charge scaling, 고정 E heavy-ion limit, analytic high-energy limit, 작은 x positive diffusion.
3. source initial energy ledger와 각 이온의 반대 bath reward; 독립 algebra/80-digit reference.
4. 기존 saved grid/source projection을 읽는다면 byte/array identity 확인, 새 combined-chain residual·확률·경계·수치 비교만 계산.
5. MFPT positivity/conductance bound와 observed refinement. 수치 convergence를 continuum/global bound로 확대하지 않는다.
6. Missing species/rate remains null, angular/momentum/energy quantity kinds separate.
7. 독립 R6/C9는 원문 정의와 raw new matrix/output에 대해 수행한다. 완료된 EE/CE 원행렬의 반복 검산은 새 차이를 검증하는 데 필요한 부분으로 제한한다.

## 읽은 원전과 한계

SciSpace 1회, Exa search 1회, Exa batch read 1회, web equation-source search 1회를 실제 수행했다.
원 응답·질의는 이 디렉터리 JSON에 보존했다.
Rosenbluth, MacDonald, Judd, Phys. Rev.107,1(1957), DOI10.1103/PhysRev.107.1,
원 논문 Eq(18–20)의 arbitrary-mass drift와 Hessian covariance를 읽었고 위 식은 그 표준식의 Maxwellian/energy-coordinate 유도다.
UC/LBNL 원 report: https://escholarship.org/uc/item/2gk1s1v8 .
Exa가 읽은 원 논문 복사본: https://www.ammar-hakim.org/sj/_static/files/RMD-1957-FPO.pdf .
OCR 식 일부의 가독성이 낮으므로 implementation admission 전에 원 PDF 그림 또는 다른 공식 식으로 factor/convention을 확인하는 것이 적절하다.
SciSpace의 다른 논문은 배경 후보이며 이번 계수의 수치 source로 채택하지 않았다.
primaryliterature novelty는 이 고전 계수에 주장하지 않는다. 새 strong no-go는 없다(NG1–NG7 not applicable).

## 현재 상태

EXECUTION: theory intake/derivation complete; new science not run.
PUBLICATION: local create-only intake only; root future branch pending.
BACKUP: inherited PR102 receipts preserved; new intake save delegated to root checkpoint.
DAG: proposed selected EI child under CR_N5_ATOMIC_ISOTOPE_COVERAGE; full N4/N5 PARTIAL/OPEN, N6/N7 predecessor-gated.
global_error_bound=null; global_completion_percent=null.

