# N5 H1 바닥상태 spontaneous RR의 기존 전자 사슬 결속

## 결과와 채택 범위

기존 C23B 광이온화 단면적과 REI PR151의 Milne 관계를 PR104의 저장된
전자 에너지 사슬에 결속했다. 선택한 세 광전자 pulse와 두 진입 경계에서,
첫 진입 또는 기존 H1 충돌여기보다 먼저 일어나는 H1 바닥상태 spontaneous
RR의 확률은 **활성 초기 전자당 1.26101–1.59845×10^-9**다. 이 RR 성분을
추가하면 평균 종료 시간은 **0.37017–0.45707 ms** 감소한다. 기존 CE 사건
확률의 절대 감소는 **3.81464–5.83787×10^-14**다.

채택 gate는 `NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_H1_SPONTANEOUS_RR_FINITE_CHAIN`이다.
독립 R6와 C9가 통과했고 blocking scientific finding은0이다. 이 판정은
명시된 고정 bath, source, ground spontaneous component와 유한 사슬을
소비하는 계산에 적용한다. 전체 `CR_N5_ATOMIC_ISOTOPE_COVERAGE` 및 N4는
PARTIAL/OPEN이며 N6/N7의 선행 gate는 유지된다.

## 입력과 선행 결과의 재사용

T=10000K, theta=0.8617333262145178eV, thermal ne=0.14cm^-3,
prescribed lnLambda=20, HI/HII/HeI/HeII/HeIII=(.9,.1,.07,.02,.01)cm^-3,
공통 온도의 정지·등방 bath와 closed box/no escape를 유지했다. H1/He4
배정은 기존 조건부 배정이다. Exposure10000 proper s는 impulsive 초기
population을 정의한다. 이후 연속 photoionization chemistry 적분은 없다.
초기0<W<10eV 선택과 이후 에너지 경로의 상단을 구분한다.

* PR104의8개 E/grid/pi/Q/K/source/RHS/old solution을 원 canonical ZIP에서
  회수했다. 481manifest 항목/482ZIP 멤버의 size/SHA/CRC 검증을 통과했다.
  기존 EE·EI·neutral generator, source projection과 primary는 재실행하지 않았다.
* 원 C23B `Verner96.sigma_cm2`를 그대로 불러 새 에너지에서 점평가했다.
  공식 원표17760bytes의 SHA256은
  `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`이다.
  사용 모듈의 SHA256은
  `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`이다.
* REI PR151 Unit8의6채널 thermal rates와18개 독립 detailed-balance 적분은
  완료된 선행 결과다. 저장된 H I10000K ground spontaneous coefficient
  `1.5893516133029456e-13cm3/s`를 회수했으며 새 thermal 적분은0이다.
  원 provider의 Li BDF kinetics HOLD는 별도 의무로 보존했다.
* C23E/VF total RR는 all-level closure다. Ground capture를 그 total에
  다시 더하지 않았다. 이번 성과는 기존 물리 공급자의 새로운 사슬 소비자다.

REI 원 provider의 m_e=9.1093837139e-31kg와 PR104의
9.1093837015e-31kg를 구분했다. 새 소비자는 PR104 질량을 유지한다.
같은 fit·threshold·온도 아래 alpha∝m_e^-3/2이므로 저장 reference를
`(m_REI/m_PR104)^1.5=1.0000000020418505`로 사상했다. 사상된 값은
`1.5893516165481638e-13cm3/s`이며 이는 새 적분 결과가 아니다.
원 저장행의 Tgamma=Te blackbody PI rate와 stimulated enhancement는
reference 조건이다. 현재 pulse에 그 방사장 조건을 부여하지 않았다.

## 계산식과 보존

원 fit의 I=13.60eV, electronic g_H=2, g_p=1,
d=2g_p/g_H=1을 유지했다. 자유전자 spin과 광자 polarization을 일관되게
포함하면 differential Milne 관계는 다음과 같다.

\[
\sigma_{\rm RR}(E)=\frac{(E+I)^2}{d\,m_ec^2E}\sigma_{\rm PI}(E+I),
\qquad \lambda(E)=n_{\rm HII}\sqrt{2E/m_e}\,\sigma_{\rm RR}(E).
\]

계산에서는 E를 eV, 속도를 cm/s, 단면적을 cm2로 변환한다. 태그된 전자
한 개의 target density는 n_HII=.1cm^-3이다. 기존 ne=.14를 여기에
곱하지 않는다. 이 RR 공급자는 stationary-heavy-target/zero-recoil
convention을 사용한다. 유한 질량 target Maxwell convolution은 별도다.
실제 photon occupation과 stimulated/total RR hazard는 null로 남는다.

기존 backward operator K0에 Lambda=diag(lambda)를 더해 K=K0+Lambda를
만들었다. 새 RR 확률·전자 제거 에너지·조건부 시간의 분자는 각각

\[
p_R=K^{-1}\lambda,\quad r_R=K^{-1}(\lambda E),
\quad v_R=K^{-1}p_R
\]

다. 기존 CE 및 종료 시간의 작은 변화는 다음 응답식으로 직접 계산했다.

\[
\Delta p_{CE}=-K^{-1}\Lambda p_{CE,0},\qquad
\Delta t=-K^{-1}\Lambda t_0.
\]

따라서 거의 같은 두 해를 빼서 작은 신호를 얻지 않는다. 과거 저장 벡터의
수치 불확실성은 상속한다. w=K0^-1 lambda, eta=max(w)라 하면 positivity와
`w-p_R=K^-1 Lambda w`에서 `w/(1+eta)<=p_R<=w`가 성립한다.
관측 eta의 최대는1.2703601756596394e-8이다. 이 비교는 명시된 유한
사슬에 대한 bound이며 연속 극한이나 전체 물리모형의 error bound가 아니다.

RR 사건의 population 변화는 (electron,HII,HI)=(-1,-1,+1)이고 전하와
H1 핵수는 보존된다. 에너지 변화는 electron -E, atomic internal -I,
retained photon +(E+I)다. 광자 reward `r_R+I*p_R`와 내부 reward
`-I*p_R`의 합이 제거된 전자 운동에너지 r_R다. Photon을 bath heat로
세거나 r_R를 제3의 최종 에너지 저장소로 다시 더하지 않는다.

전체 stopped ledger에는6bath, q-entry, inactive 초기 전자의 자체 에너지,
기존 CE outgoing kinetic/internal, RR photon/internal을 포함했다.
새 photon은 retained energy reservoir에 기록한다. 그 후의 재흡수·전리와
조성·온도 feedback은 N6의 입력 의무다. 첫 진입은 irreversible assimilation
또는 Maxwellization을 뜻하지 않는다.

## 실제 새 실행

입력 ID는 `n5_rr_milne_input_20261025_v1`이다.

| 실행 | 실제 수행과 판정 |
|---|---|
| controls_v1 | 표적19검사 PASS. Density/weights/단위/support/null/사건보존/작은 analytic chain/mutations |
| primary_v1 | 8사슬×20RHS=160. Physical136, response/diagnostic24. Source 적분행24 |
| c9_v1 | 독립 Decimal70, 최고해상도2사슬×20RHS=40, 원 fit의72개 에너지 점 검산 PASS |
| saved_plot_v1 | 저장된6행만으로4패널 PNG 생성·실제 이미지 읽기 PASS |
| kinetic_comparison_v1 | 완료된 own plot lease 때문에 child 시작 전 거절, workerCPU0. 실패 원문 보존 |
| kinetic_comparison_v2 | own lease의 완료 receipt와 PID 부재 확인 후 create-only 재개. 저장 kinetic-energy 비교18개 PASS |

원 primary의162개 scalar 비교는18개 grid/domain 쌍의9개 물리량이다.
누락됐던 conditional kinetic-energy 비교18개를 저장 결과에서 보완했다.
원 primary RESULT와 SOURCE_WEIGHTED_RESULTS bytes는 보존했다. 이를
180개의 독립 grid나 새 source 계산으로 세지 않는다.

새 ODE0, coupled/cosmological ODE0, source quadrature0, thermal quadrature0,
old generator call0, old source projection0, old primary replay0이다.

## 수치 근거

| 항목 | 관측 최대 | 동결 허용값 |
|---|---:|---:|
| Primary per-RHS scaled backward residual | 7.46590e-13 | 2e-12 |
| Primary probability partition maxabs | 8.87608e-11 | 2e-8 |
| Primary scaled energy residual | 4.09402e-11 | 2e-8 |
| C9 각 RHS 자체 norm 상대 차이 | 7.69509e-11 | 5e-10 |
| C9 intended real operator backward residual | 4.36605e-13 | 2e-12 |
| C9 native coefficient 상대 차이 | 3.13773e-15 | 5e-13 |
| C9 RR 자체 scale 사건 에너지 잔차 | 5.54759e-17 | 5e-13 |
| Regular grid 비교 | 1.14389e-4 | .005 |
| Regular domain 비교 | 3.60112e-11 | 1e-5 |
| Paired response grid 비교 | 3.63037e-5 | .01 |
| Paired response domain 비교 | 4.21520e-11 | 1e-5 |
| 추가 kinetic energy grid 비교 | 1.78051e-6 | .005 |

일부 binary64 diagonal 덧셈에서는 매우 작은 local lambda가 전부 반올림으로
사라졌다. 최대 손실률은2.7960656859617296e-15s^-1이다. 이 진단을 보존하고,
C9에서 정확히 변환한 K0와 lambda를 Decimal70으로 더해 intended real sum을
구성했다. 그 해와 primary의 각 column을 자체 norm으로 비교해 동결 기준을
통과했다. Rare probability에 unit absolute floor를 적용하지 않았다.
수치 반올림이0이라는 결론이나 continuum/global error certificate는 없다.

## 최고해상도 결과

R=80, nominalN=2048이다. q=chi*theta이며 probability의 분모는 원래
활성 초기 전자수다. q에 즉시 투영된 mass도 이 분모와 entry ledger에
일관되게 포함한다. Conditional RR 시간은 RR가 먼저 일어난 경우의 시간이다.

| chi | source z | P_RR / active | RR kinetic eV | RR photon eV | conditional time s | Delta mean stop ms |
|---:|---:|---:|---:|---:|---:|---:|
|1.5|2.316|1.5984493e-9|4.0334813|17.6334813|349854.16|-0.4570714|
|1.5|2.479|1.5974551e-9|4.0295314|17.6295314|349150.99|-0.4560438|
|1.5|2.649|1.5973198e-9|4.0258040|17.6258040|348467.13|-0.4552925|
|3|2.316|1.2673682e-9|5.2896932|18.8896932|340701.35|-0.3736137|
|3|2.479|1.2640347e-9|5.2848067|18.8848067|339896.23|-0.3718736|
|3|2.649|1.2610086e-9|5.2796040|18.8796040|339025.68|-0.3701726|

EE/EI/neutral energy diffusion과 기존 CE를 포함한 이 고정 bath 모형에서
ground spontaneous RR 성분은 q-entry 이전의 드문 경로다. 희귀하게 RR가
일어나는 경로는 평균 종료 경로와 조건이 달라 conditional time이 더 길 수
있다. 숫자를 전체 RR/모든 원자 과정의 누락 순위로 확대하지 않는다.

## 비용과 상태

실제 workerCPU4.843530s, 별도 charged compile/input preflight.01989341s,
이번 charged total4.86342341s다. 이전 known worker lineage34.234445114s와
합쳐 known lineage39.097868524s다. 이번60CPU ceiling 중 실제 잔여는
55.13657659s이며 globalremaining/전체 비용/금액은 null이다.
Coordinator CPU.028288232s와 복원·압축·네트워크 비용은 별도로 기록한다.
현재 host는 affinity0..8, quota8CPU, RAM8GiB다. Worker0/reviewer1,
coordinator8, native thread1을 적용했고 CPU55는 없다. 외부 NCP/lease는 UNOBSERVED다.

과학 채택과 Git publication/backup 상태는 별도 receipt에 둔다. 과거
PR104 terminal JSON의 업로드 거절과 pruning 후 local 부재는 독립 미완료
항목으로 유지한다. 그 payload를 이번 결과물로 재포장하지 않는다.

## 근거

1. [고정 PR104 handoff](https://github.com/cosmosapjw-quantum/bass_cr/blob/257007cc708d0db403ec2ff0c741e4a10b6207ab/research/cr_n5_neutral_elastic_20261025/delivery/HANDOFF_FINAL_WITH_LATE_OWNER_KO.md).
2. [REI PR151 Unit8 Milne 이론](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8a4f5df46f6e3058f5e685b85cc1cf3c20926368/research/microphysics_r9_20261015/unit8_remaining_bridges_20261016/spec/LI_THERMAL_THEORY.md).
3. [Verner 원 저자 표·fit 설명](https://www.pa.uky.edu/~verner/photo.html), Verner et al.1996, ApJ465,487.
4. [AtomDB RRC memo](https://www.atomdb.org/Physics/rrc-v2.pdf), Eq6–14, Milne/통계가중치/stimulation. Exa로 원문 확인; root web fetch502는 별도 실패 기록이다.
5. 로컬 `review/R6_THEORY.json`, `review/C9_INDEPENDENT_REVIEW.json`, 각 run의 실제 RESULT/DISPATCH_RECEIPT와 원 source/manifest.

Non-tilted LRS/fullFrobenius, signed amplitude/norm/cancellation 구분,
atomic isotropic closure와 nonbaryonic Vlasov stress 구분을 유지한다.
Full thermal/UV/stars/nuclear network의 완료를 주장하지 않는다.
Full high-energy nuclear 및 general triaxial/tilted/polarized CMB는 HOLD다.
원 nuclear-network PNG는 NOT_RECOVERED_NOT_READ다.
global_error_bound, global_model_error_bound, global_completion_percent는 null이다.
