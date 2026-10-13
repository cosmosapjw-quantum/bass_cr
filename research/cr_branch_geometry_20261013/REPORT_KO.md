# 이번 루프에서 확보한 결과

이번 연구는 직전 KC1–KC7에서 열린 두 작업을 실제 구성으로 진전시켰다. **실제 kernel의 조성·전자밀도 feedback을 닫은 fixed-branch endpoint**를 구했고, **반응이 새로 만든 저에너지 원자가 cutoff에 들어가는 교차**를 정확하게 만들었다. 병렬로 massive 전자의 Bianchi 에너지식을 공변적으로 유도하고, 지정된 Bianchi I 이동 뒤 실제 HI·HeI kernel을 새 parent energy에 다시 결속했다.

이 연구 단위의 독립 심사 상태는 **<!-- REVIEW_STATUS -->**다. 개별 주장과 가정은 CLAIMS/CONTRACT, 정확한 원 출력은 results, 재개 위치는 HANDOFF/NEXT_DAG에 연결한다. 여기서 얻은 endpoint와 교차는 명시한 초기 재고를 구성하여 만든 이론 사례다. 실제 선택된 cosmological history, 관측량 또는 물리 오차 예산을 대신하지 않는다.

## 핵심 결과

| 주장 | 완성한 구성 | 확인할 핵심 수치 또는 식 |
|---|---|---|
| BG1 | 실제 HI contribution + stopping의 자기일관 branch | $T_*\simeq100.35047955672445$ K, $n_{e,*}\simeq1.559603257090728$ m$^{-3}$ |
| BG2 | Self-map 및 엄밀한 finite-model residual bound | $q\le0.00031$; temperature endpoint error $\le8.11\times10^{-26}$ K |
| BG3 | 반응으로 가중치가 변하는 원자 prefix의 유한 scan | $\chi\ge3/2$, $N_B,U_B>0$에서 최대 $M$회 추가/제거 |
| BG4 | 실제 생성 원자의 cutoff 편입 | 정확히 $s=1/4$, 동일 raw state에서 $299.0883\to306.7483$ K |
| BG5 | Massive Bianchi work law와 Bianchi I map | $\dot W=-c^2K_{ab}q^aq^b/E$; $q_i^+=a_i^-q_i^-/a_i^+$ |
| BG6 | 실제 moved-energy HI/HeI 사건 재결속 | $30.00977\to36.67837$ eV; 새 8개 사건의 네 invariant residual 0 |
| BG7 | 양의 energy projection과 실제 scalar rate 오차 | HeI cell의 $C^2$ weak bound $2.4280\times10^{-20}$ m$^3$/s |

BG2의 작은 수는 **정확하게 선언한 유한 입력 모델의 algebraic endpoint 오차**다. 원 kernel의 실험적/이론적 물리 오차, source quadrature 오차, finite time-step 오차, FP64 geometry 오차는 이 수에 포함되지 않는다. BG4의 온도 jump는 유한 sharp-cutoff EOS에서 branch를 선택하며 생기는 값이다.

이 endpoint certificate는 `examples/COUPLED_BRANCH_ENDPOINT.json`에 저장한 **exact rational 근삿값**에 대한 것이다. 표에 반올림해 표시한 소수값 자체의 오차 상계로 읽지 않는다.

## 두 반응 사례의 입력을 구별한다

두 사례는 같은 실제 HI quadrature contribution을 재사용하지만 초기 재고와 cutoff parameter가 다르다.

| 항목 | Fixed-branch endpoint | Reaction-driven crossing |
|---|---|---|
| 목적 | branch 내부의 존재·유일성·error certificate | 생성 atom의 threshold 교차와 선택 규칙 |
| $\chi$ | 20 | 4 |
| 초기 온도 | 100 K | 294.6991929990844 K |
| HI 초기 count | source bath 값 138.6 | 구성한 7 |
| 초기 total thermal count | 155.05797872340426 | 10 |
| 실제 추가 사건 | 1.00028125 eV stopping edge | 선택 HI contribution 하나 |
| step/extent | $h=10^{14}$ s | $0\le s\le1/2$, $h(s)$를 정확히 구성 |
| 물리 volume | 1 m$^3$ | 1 m$^3$ |

Raw reference, initial donor mask, thermal-owned lower atoms, unresolved base reservoir를 trial마다 동일하게 유지한다. 같은 전자를 raw atom과 base에 두 번 넣지 않는다. Rate의 $n_e$는 thermal electron density이고, EOS의 $N$은 nuclei도 포함한다.

# 실제 endpoint와 branch 교차의 의미

첫 사례는 두 extent $(x,s)$의 닫힌 map을 구성한다. $x$가 HI depletion과 thermal electron 생성에 들어가고, 그 thermal electron density가 stopping rate를 바꾼다. 실제 cutoff는 모든 trial에서

$$0.1723466652429\le E_c\le0.1729952378230\ {\rm eV}$$

로 제한되어 동일한 두 node $(0.17115625,0.17425)$ eV 사이에 남는다. 따라서 branch 내부 미분과 수축 증명을 쓸 수 있다. 최종 $(x_*,s_*)\simeq(0.04417772518,0.99999991266)$는 이 box 안의 유일한 endpoint다.

두 번째 사례는 반응으로 새 첫 node의 가중치가 $a_1(s)=as$로 커지는 상황이다. Branch 0의 upper condition이 $s=1/4$에서 정확히 등호가 되고, 그 순간의 실제 atom energy로 thermal count와 energy를 옮긴다. $s=1/5$에서는 두 consistent EOS root가 존재하므로, 동일 extent의 유일성과 cutoff root의 유일성은 서로 다르다. 지정한 inherited branch 0은 상단 교차까지 유지되고 그때 branch 1로 이동한다.

![반응 extent에 따라 바뀌는 두 EOS branch. 굵은 선은 지정한 inherited-branch continuation이며, 음영 구간에서는 두 root가 모두 일관적이다.](../figures/reaction_branch.pdf)

# Geometry 이동과 실제 kernel 연결

Massive electron energy는 일반적으로 photon의 $a^{-1}$ 법칙을 따르지 않는다. 지정된 Bianchi I에서 직교 frame의 운동량을 각 방향의 scale-factor ratio로 옮긴 뒤, mass shell에서 kinetic energy를 계산한다. 모든 방향이 같은 비율로 두 배 팽창한 사례에서는 약 $30.00977\to7.50261$ eV가 되어 HI/HeI impact threshold 아래로 내려간다. 한 방향이 수축하는 anisotropic 사례에서는 volume이 늘어도 선택한 각분포의 energy가 $36.67837$ eV로 증가할 수 있다.

![기록된 geometry 사례의 이동 후 에너지와 원 HI/HeI threshold. 방향별 수축을 포함한 경우의 blue shift와 isotropic expansion의 redshift를 구분한다.](../figures/geometry_energy.pdf)

실제 kernel 재결속은 anisotropic 사례의 moved energy에서 수행했다. HI 17,564개, HeI 13,888개의 새 sharing quadrature가 각각 계산되었고, 각 species에서 actual-subcut·ghost·중간·끝점을 대표하는 4개 contribution을 새 energy row와 함께 구성했다. 이 8개 사건의 수·전하·에너지 장부는 유한 rational arithmetic에서 정확히 보존된다. 전체 sharing을 재평가한 사실과 8개 열을 직접 검사한 사실을 구별한다.

HeI rate $\kappa(W)=v_{\rm NR}(W)\sigma_{HeI}(W)$의 한 실제 cell에 대해 분석적인 derivative bound를 세웠다. 현재 cell에서 계산한 $C^2$ weak bound는 $2.4279822340661305\times10^{-20}$ m$^3$/s, 관측한 FP64 source interpolation error는 $2.5759954265704087\times10^{-22}$ m$^3$/s다. Bound는 frozen finite source parameter를 가진 ideal real scalar 함수의 정리이며, FP64 오차나 전체 branching operator 미분을 대신하지 않는다.

# 가정·증거·문헌의 연결

## 재사용한 근거

직전 branch HEAD는 `c450b00108dc05885a25d0d9c042cdcfe41bd659`이며, 직전 science commit은 `a5c29ad4070acb931d92d2bec42a927a57f479ca`다. Copied predecessor source/evidence의 상대경로, bytes, SHA256는 `inputs/PRIOR_REUSE.json`에 있다. Accepted event-capacity 보존 증명, 원 kernel, saved energy grid, cutoff의 공통 inventory 정의를 재사용했다. 변경되지 않은 이전 suite를 실행하지 않았다.

## 새로 실행한 확인

| 방법 | 실제 새 확인 | 지지하는 범위 |
|---|---|---|
| Exact-rational reference | coupled endpoint, reaction path, finite ledger | 선언한 finite-input algebra와 domain |
| 원 source 함수 | 새 moved HI/HeI sharing, rate, daughter projection | 선택한 energy 및 원 source support |
| Wolfram scalar | 24개 residual 0, 부등식 4개 true | 기재한 scalar 정의와 전제 |
| 실제 xAct/xTensor | tensor residual 8개 0 | normalization·spatial constraints 아래 공변 algebra |
| 독립 심사 | 후보 proof/code/input/output와 exact identity | 해당 seven scoped claims |

Wolfram 15.0.1 및 xTensor 1.3.0/xPerm 1.2.4의 원 출력이 있다. 공식 xAct 소스의 SHA256를 비교한 후 패키지를 실제로 불러 계산했다. 본문의 수식을 실행하지 않은 notebook으로만 제공한 것이 아니다. Full generator, nonlinear physical ODE integration, NCP job은 이번 단위에서 각각 0건이다.

## 원전 대조

SciSpace와 Exa를 모두 실제 사용했다. 새 원전 네 편의 관련 절을 읽고, 다음을 비교했다: 상세평형 reaction trajectory scheme의 조건부 유일성; Patankar 계열에서 positivity와 vanishing-component accuracy의 구분; Bianchi I의 covariant momentum과 proper-volume measure; positive conservative characteristic remapping. 원전 정리를 이 후보의 cutoff branch·massive stress 보존에 자동 적용하지 않았다. 완전한 비교와 원 URL은 뒤의 문헌 장에 있다.

# 전체 유도와 구현 계약

이후 네 절에는 새로운 유도, 비자명한 전이의 증명, 실제 입력·계산·오차 해석과 코드 interface를 모두 수록한다. 각 주장에는 식 번호와 결과 파일이 연결된다.

<!-- DERIVATIONS -->

\clearpage

# 다음 연구 DAG와 재개 지점

직전의 35개 node 중 33개는 원 object를 그대로 보존했고, 선택한 2개만 이번 결과에 연결했다. 기존 65개 edge와 19-node global overlay를 보존했다. 다음 이론 node 3개와 edge 4개를 더한 현재 DAG는 38개 node, 69개 edge이며 acyclic이다.

| 다음 node | 실제 다음 유도 | 완료 판별 |
|---|---|---|
| Full-family branch continuation | HI/HeI 전체 sharing families와 stopping의 branch별 rate feedback을 결합한다 | 서로 다른 adjacent branch domain과 crossing compatibility를 실제 한 사례에서 닫는다 |
| Geometry–collision composition | geometry map, kernel rebind, collision, cutoff 분류의 합성 오차를 유도한다 | threshold-separated commutator 또는 event-aware 대안, 하나의 refinement 비교와 work ledger |
| Angular moment remap | raw angular packets의 양의 convex moment constraint를 구성한다 | count/energy 외 momentum·stress의 feasibility 또는 observable error bound |

첫 두 node는 selected cosmological scenario 없이 수행 가능한 일반 이론 작업이다. 실제 application에는 선택한 source/history, observable과 tolerance, receiver call-site가 필요하다. 기존의 F binding/G frontier, PHYS02 delay, production, G02, all-bound, b-grid 상태는 이 이론 구성으로 바꾸지 않았다.

# 재현 및 파일 안내

핵심 derivation 4개, reference module 3개, 실제 result JSON, Wolfram/xAct script, source binding과 preserved DAG를 source bundle에 담는다. README의 command는 어떤 실행이 계산 결과를 쓰는지와 문서만 다시 빌드하는지를 구분한다. 기존 통과 suite는 필요 없이 반복하지 않는다.

분포된 외부 논문 초록·본문 cache는 원문 재배포를 피하기 위해 source archive에서 제외한다. 외부 URL, query, 반환 건수, 조회 envelope의 bytes/SHA256를 index로 제공한다. Script와 그림, 한국어 폰트 및 license를 포함하므로 LaTeX 문서를 재빌드할 수 있다. 최종 archive identity와 Dropbox/Google Drive receipt는 HANDOFF에 연결되며 archive snapshot 뒤의 전달 기록이라는 의미를 보존한다.

\clearpage

# 원전과 적용 범위

<!-- LITERATURE -->
