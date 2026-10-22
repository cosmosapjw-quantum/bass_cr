# C23A photo_subflow v2 독립 검토

## 판정

**PASS_SCOPED.** 변경된 v2 source의 283개 rate case, 1,915개 operator 호출과 28개 fail-closed 입력 검사가 같은 사전 기준으로 통과했다. v1에서 확인한 F1은 양의 해석적 K20 표현으로 교정되었다. v1 원본·실패·기준을 별도 디렉터리에 보존했다.

검토 source SHA256:

`36af631c24b3d1a2c34c9d7a4f470cbe85334a505e3cbad9ea3228d862c95079`

`REPAIR_COMPARISON.json`에서 v1/v2의 모든 1,915개 입력과 수용 기준이 동일함을 확인했다. 다른 입력으로 실패를 회피하지 않았다. source snapshot과 검토 종료 시 원본의 hash도 일치한다.

## 독립 검증 구성

5개 population과 3개 누적 event count를 state로 둔 8×8 생성행렬을 별도로 만들고 mpmath 1.4.1, decimal precision 80에서 `expm`을 적용했다. oracle은 production의 K20 표현, uniformization, event 계산 공식을 재사용하지 않는다. H I/H II와 He I/He II/He III의 각 basis inventory, 중성 혼합 및 부분 이온화 혼합을 포함한다.

검사 범위는 theta=0 및 1e-14–1e6의 20점, zero/equal/nearly-equal/1e-14–1e14/무한 rate ratio, 1e-200–1e200 inventory scale, 서로 다른 rate/time 단위 규모와 실제 P19 표 4개 행 × 3개 duration이다. 이 자료는 동결 source operator의 수치 검증이며 cosmological evolution을 적분한 자료가 아니다.

| 검사량 | 실제 최대값 | 사전 기준 |
|---|---:|---:|
| Population 절대오차 / 전체 nuclei | 2.192625732136094e-16 | 2e-12 |
| Event 절대오차 / 전체 nuclei | 9.214070151849478e-17 | 5e-12 |
| Population qualified 상대오차 | 3.699735553221784e-16 | 1e-10 |
| Event qualified 상대오차 | 3.124212898037843e-16 | 1e-10 |
| He nuclei 잔차 / inventory | 2.192625748406113e-16 | 독립 보존 진단 |
| Charge–event 잔차 / inventory | 2.192625748406113e-16 | 독립 보존 진단 |
| Binding-state 잔차 / energy scale | 1.511779679397002e-16 | 독립 에너지 진단 |
| Total-state energy 잔차 / energy scale | 2.164638841164576e-16 | 독립 에너지 진단 |
| Temperature 상대오차 | 3.801505968548345e-16 | 독립 열역학 진단 |

qualified 상대 기준은 oracle 값/전체 nuclei가 1e-10 이상일 때 적용했다. energy scale은 inventory × max(1 eV, caller binding, 각 H/Gamma)이다. 모든 검사에서 음수·비유한 population/event/energy 출력은 없었다. 28개 잘못된 입력은 명시적 오류로 거부되었다. 추가 zero-duration 검사는 v1에서 수행했고 v2에서는 해당 함수 부분이 바뀌지 않았다.

## 두 단계 확률의 독립 유도

상수 rate의 He I→He II→He III 두 waiting time을 적분하면, a=Gamma_1 dt, b=Gamma_2 dt에 대해

\[
K_{20}=\int_0^1 a e^{-as}\left[1-e^{-b(1-s)}\right]ds
=1-\frac{b e^{-a}-a e^{-b}}{b-a}
\]

이다. equal-rate 한계는 1-(1+a)exp(-a)이다. m=min(a,b), d=|a-b|를 대입하면

\[
K_{20}=1-e^{-m}\left[1+m\frac{1-e^{-d}}d\right]
=F(m)+m e^{-m}G(d),
\]

\[
F(x)=1-(1+x)e^{-x},\qquad
G(d)=1-\frac{1-e^{-d}}d,\qquad G(0)=0.
\]

두 함수의 작은 인자 표현은

\[
F(x)=e^{-x}x^2\sum_{k=0}^{\infty}\frac{x^k}{(k+2)!},\qquad
G(d)=e^{-d}\sum_{n=1}^{\infty}\frac{n d^n}{(n+1)!}.
\]

따라서 production 코드의 F n=2..33, G n=1..32 양의 항 계산은 유도와 일치한다. 0≤x≤1에서 F의 마지막 항 다음 비율은 x/34이며 이후 비율은 x/35 이하이므로 코드의 기하급수 tail 식이 성립한다. G는 t_(n+1)/t_n=x(n+1)/(n(n+2))이고, n=32 다음 항을 명시적으로 만든 후 이후 비율을 x/33으로 상계한 tail 식이 성립한다. x>1에서는 안정적인 expm1 표현을 사용한다.

이 tail은 정확한 산술에서 series truncation을 다루는 식이다. float 필드의 rounding/underflow와 물리적 closure 오차를 포함하는 인증서는 아니다. 코드가 해당 범위를 표시하고 global_error_bound=null을 유지한다.

제안식의 별도 80자리 matrix-exponential 15쌍 비교와 작은 인자 양의 급수 6점 검사는 v1 디렉터리의 `ANALYTIC_ALTERNATIVE_CHECK.json`에 있다. 최대 절대차는 1.05421979432e-81이었다.

## 입자·전하·열 장부

각 채널의 event count를 C_H, C_HeI, C_HeII라 하면 자유 전자 증가는 세 count의 합이다. 독립 oracle은 event를 population 방정식과 함께 적분한 augmented matrix에서 구한다. 별도로 최종 population에서 n_e=HII+HeII+2HeIII를 계산하여 event 증가량과 비교했다.

열 에너지 증가는 constant rate moment 조건 아래 sum_i (H_i/Gamma_i) C_i이다. binding state는

\[
B=\chi_H X_{\mathrm{HII}}+\chi_{\mathrm{HeI}}X_{\mathrm{HeII}}
 +(\chi_{\mathrm{HeI}}+\chi_{\mathrm{HeII}})X_{\mathrm{HeIII}}
\]

로 별도 재구성했고, ΔB와 sum_i chi_i C_i를 비교했다. `ΔU+ΔB−E_ext`도 최종 population에서 확인했다. 따라서 반환된 heat+binding−imported만 대입하여 항등적으로 0이 되는 검사에 의존하지 않는다.

T=2U/(3 k_B N)는 선언한 단원자 비상대론 이상기체의 translational thermal energy와 일치하며 N은 nuclei+free electrons이다. 모든 값은 caller의 고정 reference당 값이다. 이 component에서 nuclei의 외부 수입은 없으며 광이온화로 charge state와 자유 전자수가 변한다.

## source 채택 범위

검토한 구현은 고정 z/proper volume, 외부 조절 rate moments의 5개 명시적 H/He population source subflow다. source 수치 threshold convention은 caller registry와 동일하다고 확인되지 않았고 코드가 이 미해결 상태를 표시한다. 외부 에너지는 해당 모델 registry와 제공된 heat moments로 정의한 장부다.

주어진 excess-heat moment를 국소 thermal energy에 넣는 가정을 사용한다. 에너지별 secondary partition을 새로 추가하려면 그 몫을 열에서 배분하는 계약이 필요하다. 내부 유한 photon reservoir, cosmological photon transport, emissivity injection, 21-population 전체 source coverage, nuclear/stellar/CR closure는 이 component의 채택 범위 밖이다. 입력 mapping에서 누락되거나 추가된 종·채널을 0으로 채우지 않고 거부한다.

코드에서 population/probability clipping이나 column normalization을 사용하지 않는다. 양의 항 평가와 정확히 고정된 absorbing state를 사용한다. 검토한 범위의 추가 critical 이론·생성·에너지 장부 결함은 발견하지 않았다.

## 실행과 보존

CPU4, native thread1. v2 main audit wall=8.626641883995035 s, CPU=8.610990611999998 s. 이는 oracle을 포함한 검토 실행 시간이며 kernel speedup의 측정값으로 사용하지 않는다. 새 ODE0, 기존 ODE 재실행0, 외부 실행0.

| 축 | 상태 |
|---|---|
| EXECUTION | 독립 v2 operator audit COMPLETE_SCOPED / PASS_SCOPED |
| PUBLICATION | 부모 repo/PR 통합 대기; reviewer의 repo 변경 없음 |
| BACKUP | create-only 로컬 증거 보존; reviewer의 외부 backup NOT_RUN |
| DAG | C9 v2 완료. 부모 source campaign, 게시, backup은 별도 후속 node |

다음 검증을 위해 기존 v1을 다시 실행할 필요는 없다. 부모의 새 59×2×7 source campaign과 semigroup 비교는 별도 입력·run ID·자원 기록에 묶어 진행한다.
