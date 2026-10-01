# R4R: 정확 reference 인증과 더 강한 점근 확률 상계

이번 후속 연구는 기존의 조건부 정리를 실제 저장 계수에 연결했다. 새 conforming reference와 원래 선택 projector의 차이를 엄밀하게 제한했고, 에너지 간격을 이용해 먼 꼬리 population remainder의 차수를 O(Z⁻¹)에서 O(Z⁻²)로 개선했다. 실제 B0의 기존 전파 상태를 새 reference로 이전하거나 capture gate를 닫은 것은 아니다.

## 1. 실제 입력 기반의 정적 인증

저장 binary64 계수와 radial edge를 정확 유리수로 해석했다. 각 내부 절점의 양쪽 trace를 평균내고 양 끝 trace를0으로 고정한 뒤, 각 셀에 선형 보정을 적용했다. 이로써 compact support a=64, C0·H1_0 조건과 전체 l=1 multiplet을 유지하는 별도 수학적 reference를 정의했다.

질량·미분 다항식 적분은 유리수로 정확하게 계산했다. Coulomb 항의 로그는 atanh 급수의 증명된 나머지 상계와 바깥 방향 dyadic rounding으로 감쌌다. Decimal 두 정밀도의 일치나 float64 eigenvector를 인증 근거로 쓰지 않았다.

| 양 | 보수적인 인증값 |
|---|---:|
| 선택 음의 블록 margin a | ≥0.12499999996 |
| 보완 양의 블록 margin d | ≥0.0005525039691 |
| 선택/보완 residual r | ≤2.20011×10⁻¹⁵ |
| 원래 선택 projector → 새 음의 spectral projector | **≤2.76856×10⁻¹⁴** |

정확한 유리수 endpoint가 권위이며 표는 그보다 보수적으로 표시했다. projector bound는 같은 Hilbert 공간의 **같은 상태**에 대해 확률 차이≤Nδ를 준다. 이를 무한시간에 걸쳐 적분하지 않아도 된다. 음의 spectral rank는5, 양의 rank는4이며 대상은 유한9채널 weak-Galerkin 연산자다. 전체 Coulomb 연산자의 무한차원 spectral projector나 strong-operator residual을 인증한 것은 아니다.

새 reference의 canonical identity는 `85166a5812f6c9bb09f7389e1eb73019b48ea530058e37e9abdd2f11b05da6ee`, selector identity는 `2df8fd41703e3075c837e0e576ff34ec26d38f5b83d04066f1d9ec7b805e7150`이다. canonical identity와 JSON 파일 자체의 byte hash는 구별한다. 실제 인증 파일 SHA256은 `7005abab64da711aad03614e00819548b9a04138f9ef2fdc76cad2a7a305f8f2`이다. reference는 아직 물리 계산에 채택하지 않았다.

## 2. O(Z⁻²) population remainder

고립된 projectile 연산자 H0의 순서가 분리된 spectral cluster와 gap Δ를 사용한다. 먼 거리에서 Coulomb monopole을 scalar로 제거한 섭동을 W라 하면, support로부터

\[
\epsilon_Z=\frac{qa}{Z^2+b^2-a^2},\qquad
\|W\|\le\epsilon_Z
\]

를 얻는다. 순간적인 같은-rank projector E(z)를 따라가면 [H,E]=0이므로 그 population의 변화에는 E의 미분만 남는다. Sylvester 식으로

\[
\|E-E_0\|\le\frac{\epsilon_Z}{\Delta-\epsilon_Z},\qquad
\|E_z\|\le\frac{\|(I-E)W_zE\|}{\Delta-2\epsilon_Z}
\]

를 증명했다. 궤도 방향의 변화까지 포함한 Coulomb 미분을 scalar modulo로 제한하면 다음의 유리수 상계가 나온다.

\[
B(Z)=N\min\!\left\{1,
\frac{\epsilon_Z}{\Delta-\epsilon_Z}
+\frac{qa}{(\Delta-2\epsilon_Z)(Z-a)^2}\right\}.
\]

조건은 Z>a, R(Z)>2a, 2ε_Z<Δ이다. v와 hbar가 식에 없는 것은 commutator가 정확히0이고 dt=dz/v가 projector 미분의 v를 상쇄하기 때문이다. 느린 운동을 추가 가정한 것이 아니다. 순간 projector는 고정 separator로 이어가는 rank5 cluster이며 단순한0-energy cut을 사용하지 않는다. 이 논증은 disjoint-support 이후 projectile block에 적용한다. 표적/입사체 에너지의 축퇴가 있는 전체 두 중심 공간에 잘못된 global gap을 가정하지 않았다.

실제 새 reference의 gap 하한 Δ≈0.1255525039332252를 넣으면 첫 정수 cutoff는 **Z=14312 a0**, B≈**4.999662185996589×10⁻⁶**이다. 같은 상태의 selector mapping을 더해도 정수 cutoff는 동일하다. 같은 위치에서 기존 절댓값 rate 적분 상계는 약0.002227로, 새 상계보다 약445배 크다.

이 수치는 **먼 꼬리만으로 한쪽 연구 목표5×10⁻⁶을 사용하는 비교 기준**이다. 유한 중간 구간과 상태/동역학 이전 오차가 포함되지 않았다. Z=14312까지의 실제 전파 계획이나 승인이 아니다. gap과 O(t⁻²) 진폭만으로 개선을 주장할 수도 없다. 공명 회전 섭동의 정확 반례에서는 O(t⁻¹) remainder가 남으며, 이번 정리의 도함수 제어가 필수다.

## 3. 중첩 구간: 존재 증명과 오차 목표는 다르다

먼저 exclusive spherical cap과 정확 radial mass 적분으로 모든 R≥32에서 정확 L2 Gram의 양의 정부호성을 구성적으로 증명했다. 이 최초 bound는 약2.22×10⁻⁵⁵로 매우 보수적이었다. Hardy form bound를 결합해 얻은 최초 reference bridge 적분 상계6.26927×10⁵⁷도 유한하다는 사실만 보장한다. 목표5×10⁻⁶을 만족하지 못한다. 이 결과와 원래 인증 파일을 보존했다.

후속 ETF 개선은 별도의 `ETF_*` 인증 및 검토 파일에 기록했다. 핵심은 두 중심의 상대 위상 exp(ivz)에 적분 부분적분을 적용하는 것이다. 각각 L2-정규직교화된 중심 공간에서 ||∂z U||≤Lz이면 cross Gram은 ||C||≤2Lz/v를 만족한다. l=0/1의 derivative Gram 교차항은 parity로 사라지고 l=0에서는 방향 미분 에너지가 전체 gradient 에너지의1/3이다. 이는 고유한 ETF 구조를 사용한 bound이며, old literal 비연속 함수를 H1로 간주한 논증이 아니다.

정확한 유리수 비교로 Lz≤67/100, 실제 상대 속도2≤v≤3을 확인했다. 따라서 모든 중심 변위에서 **0.33I≤Scc≤1.67I**, 조건수≤167/33을 얻었다. 이는 각 중심을 따로 L2-정규직교화한 좌표의 Gram이며, 원래 계수 좌표에서는 한 중심 mass 행렬과의 congruence를 포함해야 한다. 같은 보수적인 Hardy 식의 bridge 상계는 **55408/11≈5037.09**로 줄었지만, 목표5×10⁻⁶은 여전히 인증하지 못한다.

이 개선은 조건수 때문에 발생한 극단적인 보수성을 줄인다. 그래도 Hamiltonian·connection의 cancellation을 충분히 보존한 probability bound와 실제 상태 비교가 추가로 필요하다. 기존 N1536 ±12 temporal 결과는 그대로이며 새 basis/model로 상속하지 않는다.

## 4. 원래 선택량의 극한과 시간평균

정확 reference에서 scalar long-range phase를 먼저 제거하면, 적분가능한 나머지 상호작용은 interaction-picture 상태의 극한을 준다. 고정된 관측량의 점근값은 이 상태와 H0로 만드는 유한 Bohr-frequency 합이다.

- 특정 상태에서 보통 극한이 존재할 필요충분조건은 모든 비영 주파수의 합쳐진 계수가0인 것이다. [A,H0]≠0만으로 그 특정 상태의 비수렴을 단정할 수 없다.
- 시간평균은 항상 energy-dephased 관측량으로 수렴한다. 정확 degeneracy 안의 coherence는 남긴다.
- 원래 물리 projector를 새 reference 공간에 압축하면 일반적으로 projector가 아니라 Hermitian contraction이다. 같은 상태에서의 δ mapping과 위 정리를 결합해 일정한 오차 띠와 최대2Nδ의 limiting oscillation diameter를 얻는다.

실제 B0의 asymptotic state가 없으므로 그 보통 극한이나 평균값을 수치로 결정한 것은 아니다. 시간평균이라는 새 observable을 과학적으로 채택한 것도 아니다.

## 5. 갭과 다음 단계

G04는 RESOLVED_WITH_LIMITATION을 유지하지만 reference 정의·conformity·isolated gap·selector map·연속 bridge 존재의 하위 장애를 해소했다. G05는 **UNRESOLVED→RESOLVED_WITH_LIMITATION**으로 갱신했다. 이름 붙인 정확 reference의 far-tail 정리와 계산은 완료됐고, 원래 B0의 전체 tail certificate는 여전히 미완료다.

전체 분류는 CLOSED3(G01/G08/G10), RESOLVED_WITH_LIMITATION6(G03/G04/G05/G07/G09/G12), 미종결4(G02/G06/G11/G13)다. G02는 새로운 물리 FD 실행 승인이 필요한 RESOURCE_POLICY_BLOCKER이며 G06/G11/G13의 기존 경계도 유지한다.

다음 수학적 목표는 ETF로 얻은 안정된 metric에서 overlap 연산자의 cancellation을 보존하는 상계와, 명시된 reference dynamics와 기존 상태 사이의 비교다. G02의66신규/726최대와 G03의±48 두 query/22최대 실행 계약은 앞선 패키지에 완성되어 있으며 승인 범위를 변경하지 않았다. 새 native 실행은 사용자 계약 §7/§27의 별도 경계를 따른다.

새 테스트는 **30개 통과, skip0**이며 기존114개는 반복하지 않았다. exact certificate·정리·ETF 증명에 독립 검토를 적용했다. 신규 native 호출·물리 operator query·물리 전파는 모두0회다.

DB v5는 v4를 보존한 새 버전이다. 기존30개 문헌·획득 테이블은 바꾸지 않고 연구 갭·claim·event를 갱신했다. 모든 인증, proof, 새 테스트와 독립 검토는 같은 연구 브랜치에 게시한다. 최신 검증 수와 정확한 게시 HEAD/tree·백업 수준은 종결 기록 및 별도 전달 영수증을 따른다.

`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`, `continuous_trajectory_error_bound=false`를 유지한다. 현재 B0 총 오차 예산은 계속 null이다. 새 reference의 같은-state map과 far bound를 기존 B0 오차 예산에 조용히 더하지 않는다.
