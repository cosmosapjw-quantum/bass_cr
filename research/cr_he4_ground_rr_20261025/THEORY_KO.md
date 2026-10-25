# 저장된 H1 RR 사슬에 He4 ground RR를 결합하는 소비자

## 1. 선택한 모형과 자료 대응

새 소비자는 `He4+(1s)+e -> He4(1s2, singlet)+photon`의 spontaneous
성분을 기존 H1 RR와 같은 정지 문제에서 계산한다. 원 미시 식은 C23B
Verner96 HeI fitted photoionization과 REI151의 Milne 관계다.
이 노드의 기여는 기존 식을 저장된 비열적 유한 사슬의 경쟁·시간·에너지
보상에 결속하는 것이다. 새로운 원자 단면적 측정이나 isotope-resolved
미시 공급자를 주장하지 않는다.

전자와 광자의 spin/polarization을 포함한 convention에서
`d=2*g_ion/g_bound=2*2/1=4`다. Fitted threshold `I=24.59 eV`와
photon maximum `50000 eV`를 그대로 쓴다. `sigma_PI`의 매개변수와
원본 파일 해시는 `CONTRACT.json` 및 `inputs/INPUT_MANIFEST.json`에
결속되어 있다. 전자 에너지 `E>0`에서

\[
\sigma_{\mathrm{RR}}(E)=\sigma_{\mathrm{PI}}(E+I)
\frac{(E+I)^2}{d\,m_ec^2E},\qquad
\lambda_{\mathrm{He}}(E)=n_{\mathrm{HeII}}
\sqrt{\frac{2E}{m_e}}\sigma_{\mathrm{RR}}(E).
\]

위 식의 에너지를 모두 같은 물리 단위로 넣는다. 구현은 source-native eV와
cm²를 보존하므로 `m_ec²/eV_J`를 eV로 계산하고, 속도를 `100*sqrt(2*E*eV_J/m_e)`
cm/s로 변환한다. 따라서 cm⁻³·cm/s·cm²=s⁻¹이다.
포획 target `n_HeII=0.02 cm^-3`를 한 번 곱하며 thermal `ne=0.14 cm^-3`는
이 tagged-electron hazard의 target density가 아니다.

이 식은 stationary-heavy-target/zero-recoil의 adopted smooth ground-channel
모형이다. Verner–Ferland의 ground-recombination 용법과 REI151 관례를 재사용하되,
정확한 residual-ion-state별 실험 분해는 조건부 모형 가정으로 남긴다.
지정된 HeII density 전체가 ground1s target이라는 population 가정도 명시한다.
scalar cross section에서 emitted-photon angular distribution이나 recoil
momentum을 추론하지 않는다. `HeIII -> HeII`는 이 노드의 채널이 아니다.

## 2. 보존된 사슬과 단일 경쟁 연산자

PR105의 저장된 binary64 대각·상하 대각을 정확한 수치 baseline `K_H`로
정의한다. 이는 H1 RR가 이미 포함된 transient killed backward operator다.
새 의도 연산자는 실수 합

\[
K=K_H+D_{\mathrm{He}},\qquad D_{\mathrm{He}}=\operatorname{diag}
(\lambda_{\mathrm{He}})
\]

이다. 원 EE/EI/neutral generator, source projection, CE hazard, 최초 진입
경계와 reflecting 상단은 다시 생성하지 않는다. 저장 H1 hazard를 RHS로
재사용하면서 `p_H=K^{-1}lambda_H`와 `p_He=K^{-1}lambda_He`를 같은 `K`로
계산한다. 서로 다른 연산자로 독립 계산한 두 capture probability를 더하는
방식은 같은 사건의 경쟁을 표현하지 못한다.

한 사슬에서 16 physical RHS는 CE 두 개·entry·stop time·CE kinetic 두 개,
H1의 probability/kinetic, He의 probability/kinetic, 여섯 bath gain이다.
네 conditional-time RHS, 세 paired response, 한 bound diagnostic을 더하면
24 RHS다. 8개 저장 사슬에서 새 primary RHS는 192개다.

`K_H`가 nonsingular M-matrix이고 added hazard가 비음이면 `K`의 역행렬은
비음성이다. 따라서 확률과 positive kinetic rewards가 비음이며, active
endpoint에는 entry, CE_s, CE_p, H1 RR, He RR의 확률 분할이 성립한다.
`q`에 투영된 source mass는 즉시 entry에 계상하며, 시작부터 inactive인
source는 원래 kinetic energy를 보존한다. sub-q continuation을 추가하지 않는다.

## 3. 희귀 사건의 유한 사슬 bound와 안정된 차이

`w=K_H^{-1}lambda_He`, `p=K^{-1}lambda_He`, `eta=max_i w_i`로 둔다.
Resolvent identity와 양성성에서

\[
w-p=K^{-1}D_{\mathrm{He}}w,\qquad
0\le w-p\le\eta K^{-1}\lambda_{\mathrm{He}}=\eta p
\]

이므로

\[
\frac{w}{1+\eta}\le p\le w.
\]

이는 single added hazard의 유한 사슬 관계다. continuum discretization이나
미시 모형 오차를 bound하지 않는다. 이번에는 새 He 채널이 하나이므로 이
곱셈 bound를 사용할 수 있다. 여러 added species를 넣는 확장의 각 개별
채널에 이를 자동 적용하지 않는다.

기존 보상 `u_H=K_H^{-1}b`가 주어지면 같은 RHS의 변화는

\[
K^{-1}b-u_H=-K^{-1}D_{\mathrm{He}}u_H.
\]

CE probability, mean stop time, H1 RR probability에 이를 적용한다.
거의 같은 두 숫자의 subtraction을 primary observable로 사용하지 않는다.
저장된 기존 해의 수치 불확실성은 원 H1 검토 근거로부터 상속한다.
새 계산은 그 입력에 대한 response이며, 별도 Decimal70 검토도 같은 저장
입력과 정확한 새 대각 합을 사용한다.

`v_c=K^{-1}p_c`는 채널 c의 joint first-event time moment다.
source weight `s`에서 conditional time은 `(s·v_c)/(s·p_c)`이고,
분모가 0이면 null이다. Energy moment도 같은 방식으로 조건부 평균을 구한다.

## 4. 입자수와 에너지의 소유권

He capture 한 건의 변화는 electron−1, HeII−1, HeI+1, photon+1이다.
He 핵수와 전하를 보존한다. 전자 kinetic removal `−E`, atomic internal
`−I`, retained photon `+(E+I)`의 합은 0이다. H1에는 별도의 native
`I_H=13.60 eV`를 사용한다.

He probability `p_He`와 kinetic moment `r_He`에서 photon 보상은
`r_He+I_He*p_He`, internal 보상은 `−I_He*p_He`다.
H1도 자기 binding value로 같은 두 성분을 가진다. 최종 ledger는 여섯
signed bath gains, entry kinetic, CE outgoing/internal, H1 photon/internal,
He photon/internal, unchanged inactive kinetic을 한 번씩 합산한다.
Diagnostic electron-removal reward를 세 번째 deposit으로 넣지 않는다.

Retained radiation, thermal kinetic energy, binding energy와 particle-number
변화는 각각 다른 field다. 이 작업은 frozen bath와 최초 사건을 계산한다.
열용량·온도 feedback, post-capture PI, photon escape/reabsorption,
irreversible thermal assimilation은 N6/N7의 남은 결합 의무에 속한다.

## 5. 구현과 검증의 범위

`he4_engine.coefficients`는 native source domain과 target convention을
검사하고 point coefficient를 계산한다. `consume`은 shared operator를
조립하고 24 RHS 및 event/bath ledger를 계산한다. `source_average`는
저장 source projection을 그대로 소비한다. `primary.py`는 8개 case와
24개 source row 및 원 acceptance에 따른 216개 비교를 기록한다.

아주 작은 hazard는 binary64 대각 addition에서 일부 또는 전부 손실될 수 있다.
그 사실을 별도 진단으로 보존하며, 원소별 상대 addition loss를 observable
오차로 오인하지 않는다. Independent reference는 stored baseline coefficient와
new hazard를 Decimal70에서 더한 의도 연산자를 사용하고 각 RHS의 자기
infinity norm으로 비교한다. 원 H1의 intended-vs-rounded diagnostic은
역사적 근거로 유지한다.

이 문서는 source-qualified conditional model의 정의와 유도다. 실제 primary,
independent review, resource 비용과 publication/backup 상태는 각각의
원 실행 JSON과 루트 delivery 기록에서 확인한다. 새로운 strong no-go의
채택은 없으며 NG1–NG7은 해당하지 않는다.
