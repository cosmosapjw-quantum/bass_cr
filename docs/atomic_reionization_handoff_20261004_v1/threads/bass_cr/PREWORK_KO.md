# bass_cr 선행 연구: CR-off 종결과 CR-on 재사용 계약

기준일 2026-10-04. 상태: 아래 대수·규약은 `derived`; 원격 상태는 `source-reported, file-identity-verified`; 참조 회계는 `implementation-verified`; 외부 단면적 연결·CR 이력은 `not-executed`이다.

## 1. 최신 근거와 달라진 상태

branch `research/r4q-gap-closure-20261001`의 확인 HEAD는 `b263cbe3b7ab10e1a5fee919def22938ab7515cd`, tree `912771a38b225f98819d6cce9459acc65decf36d`다. R4AO가 실제 finite candidate의 `origin_P(28,0)` cell, T mode4/m=+1 및 P mode3/m=-1 한 쌍을 256-bit native 1회/1024 node와 analytic majorant 2회로 계산했다. `SCOPED_RESULT.json`의 K 복소 L1 반경은 약 2.436×10^-26 Eh이며 전체 K 호출은 0이다. 이는 원문 보고를 확인한 것이며 이번 채팅에서 원자 계산을 재실행하지 않았다. 이전 보고의 R4AN/actual integral=0은 해당 과거 snapshot에만 맞는다.

전역 `G02=UNRESOLVED`, `production=HOLD`, `capture=false`, `all_bound=OPEN`, `b_grid=NO_GO`는 그대로다. 원자 lane의 다음 노드는 R4AP 단일 K entry의 complete-cover·cell error allocation이다. 원문9개는 `legacy_sources/`에 원 Git blob과 동일하게 보존했다. 옛 roadmap의 R3M29 또는 R4AJ handoff의 m64 지시를 최신 NEXT_DAG보다 우선 실행하지 않는다.

## 2. CR-off 제거 논증

R1 소비자 계약은 photon/H-He solver를 CR보다 먼저 닫는다. 물리모형 선택 `CR.enabled=false`는 CR source를 근사적으로 작다고 주장하는 것이 아니라 독립된 비교모형에서 명시적으로 제외하는 것이다. 분포를 `N_CR=0`으로 두면 원자 충돌 event functional

\[
R_r=n_t\int N_p(E,\Omega)\,v_{\mathrm{rel}}\,\sigma_r(E_{\rm CM})\,dE\,d\Omega
\]

가 정확히 0이다. 따라서 해당 CR source의 전자·열·종별·운동량 기여 역시 0이고, σ provider를 로드할 이유가 없다. 이 말은 현실의 CR 효과가 무시 가능하다는 정량적 bound가 아니다. 전형적인 CR-free photon reionization 모형에 해당하며, CR 효과 자체를 연구하는 후속 계산과 비교해야 한다.

`cr_sources(False, provider)`는 provider를 호출하지 않고 다섯 reservoir의 0을 반환하도록 구현했다. 이 분기 시험은 '누락된 CR 단면적 때문에 CR-off 기준 계산이 중단되지 않는다'는 소프트웨어 의미를 확인한다. 원자 weak-K, full-K, physical bridge는 이 baseline의 dependency에서 빠지지만 실패 기록 자체는 바뀌지 않는다. rei_bianchi의 실제 nonlinear enclosure와 시간적분 gate는 계속 필요하다.

## 3. 과정 식별과 정수 회계

종 순서는 `(p_fast,H_gas,H_fast,p_gas,e_free)`다. H nuclei 가중치는 `(1,1,1,1,0)`, 총 전하/e 가중치는 `(1,0,0,1,-1)`다.

| ID | 반응/의미 | event당 변화 | baseline |
|---|---|---|---|
| resonant_cx_1s | p_fast+H_gas(1s)→H_fast(1s)+p_gas | (-1,-1,+1,+1,0) | CR-off=0 |
| target_ionization | fast projectile에 의한 H_gas→p_gas+e | (0,-1,0,+1,+1) | CR-off=0 |
| fast_neutral_stripping | H_fast→p_fast+e; 충돌 상대 변화는 별도 채널 | (+1,0,-1,0,+1) | CR-off=0 |
| target_excitation | H(1s)→H(nl), 동일 charge bin | (0,0,0,0,0) | excited-state/광자 회계는 추가 필요 |
| elastic | charge/species 보존 | (0,0,0,0,0) | 운동량/열이 0이라는 뜻 아님 |

각 열은 nuclei 및 charge dot product가 0이다. resonant CX는 gas HII를 +1, fast proton을 -1 바꾸지만 총 HII와 자유전자 변화는 0이다. `formation_count_1s`를 총 gas+fast 이온화 생성률로 사용하는 것은 잘못이다. target ionization/stripping은 각각 전자 +1이다. 공급자가 둘을 합친 inclusive 단면적만 주면 다시 각각 더하지 않는다. 동반 target ionization이 있는 stripping은 분리 채널의 결합 회계가 필요하며 위 minimal stripping으로 대체하지 않는다. 여러 초기 n,l의 total CX를 1s formation으로 대체하지 않는다.

CR beam에 net charge/current가 있으면 gas 전자밀도와 gas proton만으로 전체 중성을 자동 주장할 수 없다. return current/CR electron 등 전하 보상과 transport는 실제 CR-on 모형의 별도 명세다. 원자 자료의 서명만으로 해당 closure가 결정되지 않는다.

## 4. 분포·단위·에너지 frame

NR 국소 gas tetrad와 target at rest에서 `E_CM=m_t/(m_p+m_t) E_lab`; proton-H는 약 E_lab/2다. 자료가 `keV/u`면 먼저 `E_lab=A_p ε`로 바꾸되 물리 질량과 정수질량 근사를 manifest에 구별한다. α projectile/수소 target의 예에서 A_p=4 근사를 쓰면 E_CM≈(4/5)ε다. 따뜻한 target은 단일 frame 변환 대신 상대속도를 적분한다.

정규화된 f_p(v), f_t(w), ∫f d³v=1의 경우

\[
k_r=\iint f_p(\mathbf v)f_t(\mathbf w)g\sigma_r(\tfrac12\mu g^2)d^3v\,d^3w,\qquad R_r=n_p n_t k_r.
\]

f의 단위는 (cm/s)^-3, k는 cm³/s, R는 cm^-3/s이다. `N(E,Ω)`는 이미 밀도를 포함한 cm^-3 erg^-1 sr^-1 분포로 정의하며 추가 n_p를 곱하지 않는다. `j(E,Ω)=vN`인 differential intensity를 쓸 때는 R=n_t∫jσ dE dΩ이고 v를 다시 곱하지 않는다. 4π는 isotropic j의 angular integration을 실제 수행할 때만 붙인다. E 대신 momentum을 입력하면 d³p=p²dp dΩ 및 dE/dp Jacobian을 명시한다. 이 규약 중 하나만 provider contract에 사용한다.

`reference/cr_contract.py:number_rate`는 이미 주어진 고정 양의 quadrature의 합만 구현했다. 실제 분포 선택, warm-target 평균, interpolation, tail 인증은 구현하거나 실행하지 않았다. 중간에 에너지 단위를 eV와 erg로 바꾸면 분포와 dE가 역으로 변해야 하며 scalar σ는 cm²를 유지한다.

## 5. stopping·전자 cascade·열의 분리

단위길이당 energy loss S(E)=-dE/dx[erg/cm]라면 power density는 ∫N v S dE dΩ [erg cm^-3 s^-1]이다. 이미 target density를 포함한 S와 per-target loss cross section L(E)[erg cm²]는 구별한다(S=n_t L인 단순 모형에서만 등가). total σ만으로 S나 momentum-transfer σ_mt=∫(1-cosθ)dσ를 복원하지 않는다.

각 event 또는 같은 volume/time-bin에서 CR kinetic loss를 열, ionization potential, 아직 저장된 excitation, radiation, nonthermal/recoil storage, escape로 서로 겹치지 않게 배분한다. 여기서는 `close_energy`가 그 합과 loss의 잔차를 반환하며 음의 잔차를 거절한다. 양의 잔차는 미회계 에너지이고 성공을 뜻하지 않는다. excitation의 이후 de-excitation photon을 세는 시점에는 저장 excitation을 감소시켜 중복 계산을 막는다. σ_CX×E_projectile을 그대로 gas heat로 넣지 않는다.

Primary ionization electron의 kinetic energy가 immediate heat인지 secondary ionization/excitation인지에는 별도 deposition/cascade 모델이 필요하다. FS10 같은 electron-deposition 표는 projectile proton cross section을 대신하지 않는다. CR ionization/heating을 이미 포함한 tabulated stopping+deposition과 같은 primary/secondary channel을 다시 더하지 않는다. anisotropic momentum source는 scalar rate만으로 닫히지 않으므로 이번 baseline에 포함하지 않는다.

## 6. 외부 자료와 호출 순서

문헌조사 완료 자료의 좁은 선택지는 FIDASIM atomic_tables의 공개 Fortran fit, CollisionDB의 process/state별 표, UGA의 proton-H elastic/CX 자료다. 출처는 아래 원 URL 및 함께 게시되는 공통 source registry에 기록한다. FIDASIM MIT는 코드에 적용되며 ADAS 유래 표의 재배포 권리를 자동 부여하지 않는다. UGA 2023 elastic 업데이트가 CX/ionization 전체 갱신이라는 주장은 하지 않는다.

- https://d3denergetic.github.io/FIDASIM/module/atomic_tables.html
- https://d3denergetic.github.io/FIDASIM/sourcefile/atomic_tables.f90.html
- https://github.com/D3DEnergetic/FIDASIM/blob/master/LICENCE.md
- https://db-amdis.org/collisiondb/ 및 https://db-amdis.org/collisiondb/licence/
- https://sites.physast.uga.edu/amdbs/elastic/index-h%2B%2Bh-2023.html
- Schultz et al. 2016 DOI https://doi.org/10.1088/0953-4075/49/8/084004

이번 연구는 이 자료를 실제 provider로 admit한 것이 아니다. 현재 첫 목표는 CR-off이므로 actual CR distribution/energy range/observable을 발명해 provider를 선택하지 않는다. CR-on 결정이 내려진 뒤 해당 질문에 필요한 단일 source를 pin하고 domain/tail/license를 닫는다. 기존 HOST H16의 4–81 keV/u는 역사 모형의 영역이며 현재 rei_bianchi의 입력이라고 가정하지 않는다.

## 7. 오차의 의미와 연결

양의 weighting W에서 |δR|≤∫W ε_σ dE + tail + quadrature는 ε_σ가 해당 domain의 실제 bound일 때만 rigorous bound다. 문헌간 차이·fit residual·실험 uncertainty·numerical enclosure를 분리한다. 같은 nominal source로 FLRW/Bianchi를 짝지어 계산한 후 source를 공통 perturb하여 관측량 차이의 감도를 구한다. 원자 절대불확실성보다 작다는 이유로 우주론적 차이를 자동 배제하지 않는다.

포획 selected-state 관측량·미지원 에너지·momentum 또는 새 coherence가 실제 중요해지면 legacy lane의 완료 단면적을 동일 provider interface로 연결한다. 소비자/단위/채널 계약을 공유하므로 fastest와 원자 lane의 결과가 비교 가능하다. 기저 K 자체와 외부 σ는 서로 다른 object다.

## 8. 이번에 실제 완료한 범위

원격 최신 commit/ref 및 선택 문서9개 읽기, 원 Git blob identity 확인, CR-off 논증·반응 회계·rate/energy 정의, 휴대형 회계 reference와 독립 예상값 기반 unittest10건을 완료했다. 최초 import 실패 후 구현을 추가하고 10건이 통과했다. 실제 단면적 fetch/adoption, 원자 native, full-K, b-grid, CR propagation, cosmological history는 0회다. `VERIFICATION.json`이 정확한 실행 명령과 source/test SHA를 제공한다.
