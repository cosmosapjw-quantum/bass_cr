# PHYS02G — 두 모멘트가 제한하는 열 방출 시각과 frontier 후처리

## 핵심 결과와 현재 상태

PHYS02E 실제 9600점 반환과 PHYS02F의 독립 검토된 저장 scalar 자료를 이용해, 열 방출 지연의 평균·2차 모멘트·출생 구분이 허용하는 survival 범위와 분위수 범위를 계산했다. fullBED의 90% 방출 시각은 약 8.75천–7.90만 년, 99%는 약 1.44만–22.45만 년 범위로 제한된다. 기존 평균 지연 약 1.47만 년을 방출 완료 시각처럼 해석할 수 없는 이유를 수치로 드러낸다.

여기서 범위는 **기록된 모멘트를 정확한 값으로 간주할 때 성립하는 수학 부등식의 FP64 평가**다. 물리 파라미터의 신뢰구간, 수치 전진 오차의 인증 구간, 에너지 격자 수렴 구간이 아니다. 엄밀한 입력 오차 전파나 directed rounding을 수행하지 않았다. 그 차이를 유지한 상태에서 평균만 사용하는 해석보다 강한 정보를 얻었다.

현재 queried GitHub 및 지정 백업에 새 PHYS02F actual return은 관측되지 않았다. 마지막 실제 물리 계산은 PR35의 PHYS02E이고, PR36의 PHYS02F는 준비·직접 유도·저장 scalar 분석의 검토 결과다. 미게시 NCP 실행과 현재 F 예산 소모 여부는 UNKNOWN이다. G는 F 실제 반환을 기다리는 동안 독립적으로 실행 가능한 저장 자료 분석을 완료했다. F의 `q0,q1,q2,xT`를 사용하는 상태별 후처리는 준비된 별도 단계이며 실제 frontier 결과를 계산했다고 주장하지 않는다.

최종 독립 판정은 `review/INDEPENDENT_DECISION.json`, 실제 gate/DAG는 `state/RESEARCH_STATE.json` 및 `state/NEXT_DAG.json`, 게시 완료 여부는 `publication/PUBLICATION_STATUS.json`을 참조한다. 본 보고서의 과학 내용은 그 판정의 검토 대상이며 보고서 자체가 자기 승인을 대신하지 않는다.

## 1. 데이터와 질문

출발 측도는

\[
 dF(\tau)=\frac{K(\tau)}{H_0}\,d\tau,\qquad H_0=\int_0^\infty K(\tau)\,d\tau>0
\]

다. 이는 최종적으로 열로 들어오는 에너지로 정규화한 지연 확률이다. 입자 수의 생존율이나 전체 주입 에너지에 대한 지연 비율과 구별한다. 시간 원점은 source birth이며, 동일한 고정 bath와 truncated finite operator를 계속 적용한다는 조건 아래 uncapped moments를 해석한다.

기존 실제 관측 창은 `T=10^10 s=316.8808781402895 yr`이고 1년은 31,557,600초다. 기록된 요약은 다음과 같다.

| 항목 | fullBED | legacy |
|---|---:|---:|
| T까지 방출한 열의 비율 p | 0.06390638043 | 0.06376934057 |
| T 이후 남은 열 비율 q=1−p | 0.93609361957 | 0.93623065943 |
| uncapped 평균 지연 μ [yr] | 14,719.99389 | 15,073.22046 |
| T 이후 조건부 잔여 평균 지연 [yr] | 15,397.97468 | 15,772.98338 |

입력 파일은 `inputs/F_CACHED_NUMERICAL_ARTIFACT.json`이며 원본 F `evidence/analysis/NUMERICAL_ARTIFACT.json`과 동일 바이트다. SHA256은 `dfdca59ca0b4131c6143fe3cf0e402a7b18efb113a9af9bcc82a66696f5ec6f5`다. source commit은 `b21009893b93ed9b7e4af22ac4f480fe4b8e5c4b`, source tree는 `63cd76b80393f3d9c506dec7c80eda8925df39e3`다. 원본 F 판정은 SHA256 `46a432333374b85a77cfd5bd1d4c266123c2188335f4621549fdbdbad80870c2`에 결속되어 있다. 기존 E 실제 결과와 실행 로그는 byte-identical F 의존 ZIP에도 포함되어 있다.

이번 질문은 두 가지다. 첫째, 전파를 연장하지 않고 현재 모멘트만으로 열 방출 시각을 어느 정도 제한할 수 있는가. 둘째, 추가로 상태별 조건부 모멘트가 주어지면 어떤 정보가 더해져 그 제한이 좁아지는가. 지수형·로그정규형 등 꼬리 분포를 가정하지 않는다.

## 2. 비음수 확률변수의 두 모멘트 부등식

`X>=0`에 대해 `a=E[X]`, `b=E[X²]`, `v=b−a²`라 하자. `a>0,v>0`이면 strict survival `P(X>x)`에 다음 범위가 성립한다.

\[
 L(x)=\begin{cases}
 \dfrac{(a-x)^2}{v+(a-x)^2},&0\le x<a,\\
 0,&x\ge a,
 \end{cases}
\]

\[
 U(x)=\begin{cases}
 1,&0\le x\le a,\\
 a/x,&a<x<b/a,\\
 \dfrac{v}{v+(x-a)^2},&x\ge b/a.
 \end{cases}
\]

따라서 `L(x)<=P(X>x)<=U(x)`다. 상한의 첫 구간은 확률의 자명한 상한, 중간 구간은 Markov, 마지막 구간은 one-sided second-moment 부등식이다. 분기점 `b/a=a+v/a`에서 Markov와 마지막 상한이 일치한다. 하한은 평균보다 작은 threshold에 대한 one-sided second-moment 부등식을 여사건에 적용해 얻는다.

`v=0`인 generic 법칙은 `X=a`이고 strict survival은 `x<a`에서 1, `x>=a`에서 0이다. `a=b=0`은 generic δ0로 허용되지만 `a=0,b>0`은 비음수 변수의 모멘트가 될 수 없다. 실제 residual 및 finite-rate heat-conditioned frontier 법칙은 양의 heat weight를 가지면 지연과 평균이 엄밀히 양수이므로 generic δ0를 그 물리 adapter에 그대로 적용하지 않는다.

각 generic 부등식의 sharpness는 **모든 비음수 확률분포**라는 큰 클래스에서의 infimum/supremum에 관한 것이다. 특히 strict `>` 사건 때문에 어떤 상한은 경계에 원자를 둔 분포가 그대로 달성하지 못하고, 유한 원자분포의 극한으로 접근한다. 본 루프의 직접 유도와 exact Fraction witnesses는 `research/theory/`에 있다. 모멘트 문제, polynomial majorant와 tight supremum의 개념은 Bertsimas–Popescu의 원 논문과 저자 소속 기관 working paper를 참고했다. 이 보고서의 piecewise 결합식과 물리 residual/frontier 적용 전체를 그 문헌의 동일한 정리라고 인용하지 않는다.[1,2]

## 3. 알려진 censoring과 출생 정보를 사용하는 방법

F의 기록 `p=F(T)`, `R=E[(1−tau/T)_+]`, `S=E[(1−tau/T)_+²]`, `μ=E[tau]`, `m₂=E[tau²]`를 쓰면 residual 변수

\[
 X_T=(\tau-T)\mid\tau>T
\]

의 모멘트는

\[
 a_T=\frac{\mu-T(1-R)}{q},\qquad
 b_T=\frac{m_2-2T\mu+T^2(1-S)}{q},\qquad q=1-p
\]

다. `q>0`일 때 `t>T`에서 전체 survival에 `q L(t−T;a_T,b_T)`와 `q U(t−T;a_T,b_T)`를 적용할 수 있다. `q=0`은 zero-tail로 명시하고 조건부 나눗셈을 하지 않는다.

`t=T`는 별도로 다룬다. 조건부 변수는 엄밀히 양수이므로 `P(X_T>0)=1`이다. 따라서 그 지점의 전체 survival은 정확히 `q`다. generic nonnegative 하한 `a_T²/b_T`로 이 정보를 버리지 않는다. T의 오른쪽에서 bound의 하한이 떨어지는 모습은 제한된 모멘트 정보로 만든 envelope의 성질이며 물리 CDF의 불연속이 아니다.

출생 에너지 범위 `direct_0p1_10`, `direct_10_900`의 eventual-heat weights를 `w_j=H0_j/ΣH0`라고 하면, 두 출생별 residual 상·하한을 `Σw_j q_j L_j`, `Σw_j q_j U_j`로 합한다. 최종 lower는 unconditional selected, pooled residual, birth-stratified residual lower의 최댓값이고, upper는 해당 세 upper의 최솟값이다.

정확한 모멘트와 가중합에서는 출생별 제약이 pooled 두 모멘트 제약을 포함하므로 stratification은 generic envelope를 넓히지 않는다. 그러나 여러 정보를 교차한 최종 envelope가 공유된 물리 연산자 클래스에서 전역 최적인지까지 증명한 것은 아니다.

## 4. 실제 저장 자료 결과

`Q_f=inf{t:F(t)>=f}`로 분위수를 정의했다. 하단 bracket은 `L(t_lo)>1−f`를, 상단 bracket은 `U(t_hi)<=1−f`를 만족하도록 원시 FP64 끝점과 bisection 이력을 저장했다. 하한에서 equality만으로 `Q_f>t`를 주장하지 않는다. 다음 표는 읽기 편하도록 년 단위의 바깥 정수로 넓혀 표시한 수치 범위다. 정확한 작업 산술 값과 `1−f`의 FP64 값은 `evidence/analysis/NUMERICAL_ARTIFACT.json`에 있다. 이 표의 반올림이 입력 오차 인증을 만들어 주지는 않는다.

| eventual heat fraction f | fullBED 분위수 범위 [yr] | legacy 분위수 범위 [yr] |
|---:|---:|---:|
| 50% | 316–29,086 | 316–29,793 |
| 90% | 8,746–78,964 | 8,908–81,224 |
| 95% | 11,276–107,516 | 11,513–110,631 |
| 99% | 14,379–224,534 | 14,708–231,148 |
| 99.9% | 16,029–677,158 | 16,406–697,309 |

50% 하한의 실질적 정보는 `Q_0.5>T=316.880878...yr`다. 이후 모멘트 하한만으로 중앙값 위치를 충분히 좁히지는 못한다. 90% 및 99%에서는 남아 있어야 하는 꼬리의 최소량이 더 강한 하단 제한을 준다. 높은 f일수록 상한이 크게 증가하는 것은 허용한 분포 클래스가 넓기 때문이다. 이 상한 자체를 실제 99% 방출시간의 예측값으로 쓰면 안 된다.

고정된 몇 시각에서의 남은 열 비율 범위는 다음과 같다. 아래 수치는 비교용 근삿값이며 더 많은 유효숫자를 보증하지 않는다.

| 시각 [yr] | fullBED survival 범위 | legacy survival 범위 |
|---:|---:|---:|
| 1,000 | 0.290565–0.916916 | 0.288971–0.917086 |
| 10,000 | 0.073676–0.873496 | 0.077550–0.873743 |
| 30,000 | 0–0.484602 | 0–0.496503 |
| 100,000 | 0–0.058804 | 0–0.062680 |
| 300,000 | 0–0.005409 | 0–0.005752 |
| 1,000,000 | 0–0.0004514 | 0–0.0004792 |

예를 들어 fullBED에서는 기록된 모멘트에 조건부로 10만 년 이후 남은 열 비율의 상한이 약 5.88%다. 30만 년에서는 약 0.541%다. 이 평가는 해당 시각까지 새 pulse를 전파한 결과가 아니다.

fullBED와 legacy의 구간은 크게 겹친다. fullBED가 대체로 더 작은 높은 분위수 상한을 가지는 것은 저장된 모멘트 차이와 일관된다. 하지만 두 envelope의 겹침으로 두 커널이 같다고 결론 내릴 수 없고, empirical 모델 차이를 uncertainty distribution으로 바꾸지도 않는다.

그림 `evidence/figures/SURVIVAL_ENVELOPES.pdf`는 log 시간·선형 확률축에 상·하한과 교집합을 표시한다. 확률 clipping이나 log-plot floor를 쓰지 않았다. `QUANTILE_BRACKETS.pdf`는 점 분위수 대신 bracket을 보여 준다. 원시 plot data도 함께 보존했다.

## 5. F adjoint가 제공할 추가 정보

active block을 `A=−G_active`, 열 행을 `h`, dimensionless 시간을 `u=t/T0`로 두면, F가 준비한 adjoint는

\[
 A^Tq_0=h,\qquad A^Tq_1=q_0,\qquad A^Tq_2=q_1
\]

다. 상태 i에서 출발한 heat kernel을

\[
 k_i(r)=T_0^{-1}h^T e^{-Ar/T_0}e_i
\]

로 정의하면 그 0·1·2차 적분은 각각 `q0_i`, `T0 q1_i`, `2T0² q2_i`다. 따라서 `q0_i>0`에서 heat-conditioned residual law의 모멘트는

\[
 a_i=T_0q_{1i}/q_{0i},\qquad
 b_i=2T_0^2q_{2i}/q_{0i}.
\]

T에 남은 active state가 `xT_ij`일 때 semigroup 선형성으로

\[
 K_j(T+r)=\sum_i xT_{ij}k_i(r),\qquad
 P_j(\tau>T+r)=\sum_i\alpha_{ij}P_i(X_i>r),
 \quad \alpha_{ij}=q_{0i}xT_{ij}/H0_j
\]

를 얻는다. `Σ_i alpha_ij=q_j`다. 상태별 일반 부등식의 가중합은 상태별 모멘트가 없는 birth/pool bounds보다 많은 제약을 쓴다. 정확한 산술에서 state→birth→pool의 범위 포함관계가 성립하며, 구현은 부호 있는 차이를 검사한다.

이 가중치는 T 시각 active energy가 앞으로 만들 열에 대한 것이다. residence contribution `q0_i*w_ij`, 단순 active population, local heat deposition energy와 같은 양이 아니다. 어떤 출생 구간이 평균에 기여하는지와 어떤 현재 에너지 상태가 앞으로 늦게 방출할지를 함께 읽을 수 있게 된다.

F가 필요한 배열을 이미 저장하도록 준비되어 있으므로 G는 배열 로딩·가중합·범위 평가만 추가한다. **추가 G 구성 0, 선형계 풀이 0, pulse 0, expm 0**이며 NCP 후처리 1회·90초로 제한했다. 실제 F 반환·runtime·source parity가 확인되지 않았으므로 현재 frontier 수치는 없다.

## 6. 검증 범위와 보존한 반대 증거

저장 scalar 분석은 두 모델을 묶어 정확히 1회 실행했고 실제 exit 0, wall 약 2.496초였다. 각 모델에서 Decimal80 독립 산술 비교 2,077개가 고정 기준을 통과했다. 비교는 `2e−14 + 2e−12 relative`의 확률/무차원 기준을 사용하며, 가장 큰 tolerance fraction은 fullBED 약 0.000264, legacy 약 0.000402다. 새로운 물리 연산 호출은 없다.

첫 cached targeted run에서 7개 중 1개가 실패했다. 구현식이 아닌 synthetic expected second moment의 산술 오류였고, `(24−8+0.95)/0.8=21.1875`로 test oracle만 수정했다. 최초 stdout/stderr·실제 exit·수정 후 7/7 통과를 모두 보존했다. 실제 저장 자료 분석을 재실행하여 실패를 숨기지 않았다.

NCP 준비 검증은 작은 kernel과 실제 운영 경계에 한정한다. 실제 9600-state F frontier 입력과 NCP runtime 자원 측정은 현재 실행되지 않았다. 검증 과정에서 발견한 durable failure-log 누락과 최종 review/DAG binding의 coverage gap은 `state/VALIDATION_COMPLETION_AUTHORIZATION.json`에 원인을 적고 해당 검사만 보완했다. 이어 root 통합 검토에서 발견한 horizon output·schema·intersection·source-path 경계의 구현 누락은 `state/CONFORMANCE_CORRECTION_AUTHORIZATION.json`에 고정 계약과의 차이로 기록했다. 이전 코드·로그와 수정 후 직접 영향을 받은 검증을 함께 보존하며, 변경으로 실제 F/G 예산을 다시 발급하지 않는다. 이 보완의 첫 검사 명령은 운영 검사 4개 통과 후 새 frontier test의 import 순서 오류로 exit 1이었다. import 위치만 고친 뒤 아직 평가되지 않은 frontier 검사 4개만 실행해 통과했다. 원래 통과한 운영 검사는 반복하지 않았고 첫 실패 로그·수정 전 source·수정 후 결과를 모두 남겼다.

독립 reviewer는 후보 생성·acceptance·구현과 분리되어 있다. 직접 유도의 정확성, Decimal/FP64 결과, 증거의 원본 identity, 준비 코드의 의미와 운영 경계를 검토한 최종 판정을 별도 파일에 남긴다. root의 이 보고서는 그 판정을 대체하지 않는다.

## 7. 다음 실행과 연구 판단

다음 실제 계산은 기존 F 예약/반환의 현재 상태를 확인한 뒤 이어진다. 실행 중인 F는 기존 로그를 이어 보고, 완료된 F는 원본 family를 읽고, 실패한 F는 이미 소모한 예산과 최초 실패를 보존한다. 실제 호스트 증거로 미예약·미실행을 확인한 경우에만 원래 F의 최초 한 번을 실행한다. G 프롬프트 자체는 F 재시도 승인이 아니다.

F와 G가 실제로 완료되어 새 independent Astra review를 통과하면, 상태별 모멘트가 시간 범위를 얼마나 줄이는지와 그 상태들이 어느 에너지 구간에 있는지 판정할 수 있다. 실제 범위가 여전히 넓으면 그 사실을 다음 질문의 근거로 삼는다. 장시간 pulse를 무작정 추가하거나 source-history production을 즉시 승격하지 않는다.

유지되는 gate는 PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED다. 유한 mesh의 수치 노드, 고정 bath의 물리 타당성, 원천 원자/모델 identity, 실제 host/runtime 승인, continuum tail claim을 분리해 보존한다.

완전한 시작 절차는 `START_NCP_CODEX_KO.md`다. 완성 G ZIP은 이전 F의 완전한 ZIP을 의존 파일로 내장한다. 외부 시작 파일에는 실제 게시된 G ZIP와 Drive/Dropbox의 exact IDs가 들어가므로 추가 첨부 없이 다음 NCP 세션을 시작할 수 있다.

## 문헌과 1차 증거

1. D. Bertsimas and I. Popescu, “Optimal Inequalities in Probability Theory: A Convex Optimization Approach,” SIAM Journal on Optimization 15(3), 780–804 (2005), DOI: https://doi.org/10.1137/S1052623401399903 . Publisher page read: https://epubs.siam.org/doi/abs/10.1137/S1052623401399903 . 일반 모멘트 제약 최적화 문맥에만 사용했다.
2. 같은 저자들의 INSEAD working paper 2002/01/TM: https://flora.insead.edu/fichiersti_wp/inseadwp2002/2002-01.pdf . Definition 2의 supremum/attainment 구별과 polynomial-majorant 접근을 확인했다. Working paper와 출판 논문의 identity를 구별한다.
3. 실제 PHYS02E return: https://github.com/cosmosapjw-quantum/bass_cr/pull/35 , commit `459018cffc3d57dcf8670997b4029fb6891e8101`.
4. PHYS02F 저장 분석과 준비 판정: https://github.com/cosmosapjw-quantum/bass_cr/pull/36 , head `b21009893b93ed9b7e4af22ac4f480fe4b8e5c4b`.
5. G 직접 유도·exact witnesses: `research/theory/`; G 실제 저장 분석·실패 및 종료 로그: `evidence/analysis/`; 준비 코드 검증과 원인 기록: `evidence/ncp_validation/`; 새 독립 판정: `review/INDEPENDENT_DECISION.json`.
