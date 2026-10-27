# 다음 BASS_CR 단위: 읽기 전용 구현 가능성 조사

## 1. 판정과 현재 작업 범위

실제 PHYS02의 **low native birth partition 0.1–10 eV**를 그대로 소비하고, 같은 100 K·H/He 밀도에서 원래 Coulomb 하강 이동과 새 HII/HeII ground RR을 결합하는 작은 새 recipient를 구성할 수 있다. 3200개 active state와 cutoff/반환 ledger면 충분하다. 원래 전체 9600점 행렬을 복구하거나 다시 생성한 것으로 취급하지 않는다.

이 문서는 root의 다음 R/C 단위 범위 선택을 위한 구현 intake다. 과학 코드 import·실행, 배열 적분·새 coefficient 계산, old suite replay, Git mutation, 이전 연구 단위 수정은 **0**이다. 이번 agent는 파일·원문·저장 JSON·해시만 읽고 이 조사 폴더에 기록했다. 새 scope·허용치·별도 CPU 예산·C4 admission은 root가 고정한다.

현재 local HEAD와 PR109 D는 8482ed83b14517b709ba6e801f6714cc333e720f, AGENTS SHA256은 929ca5596e5bd5c84176ca82be80030cfabd08e81848e4ba40ef48a3c2529c45다. e1 physmath-research-loop의 내장 1.0.0, 승인 설계 v0.2와 공통 정책·R1–R10·C1–C10·근거/인계·runtime 참조를 읽었다. 현재 조사는 실행 단계 완료를 주장하지 않는다.

## 2. 병렬 CR 작업과 실제 보관 범위

[PR108](https://github.com/cosmosapjw-quantum/bass_cr/pull/108)은 열린 draft이며 HEAD는 2776752de6952f60d8d690a128f33fec4df2c57b다. 저장된 LOOP_LEDGER는 R1–R10/C1–C8 complete, C9/C10 pending이다. bath는 T10000 K, HI/HII/HeI/HeII/HeIII=(.9,.1,.07,.02,.01) cm^-3, explicit nb null이다. 실제 source는 PR104의 세 독립 pulse 대안이고, PHYS02의 100 K 연속 주입과 같지 않다. 유한 clock 수학·구현은 비교 대상으로 사용할 수 있지만 이 bath의 숫자 응답을 새 PHYS02 recipient로 가져오지 않는다. PR108의 별도 60 CPU envelope와 보관된 실패도 새 단위에 합산·이월하지 않는다.

실제 updated>=2026-10-27 PR 조회는 109,108,107을 반환했다. CR 이름 branch 조회는 100개와 다음 빈 terminal page를 반환했다. 이는 조회 조건의 범위이며 모든 비공개 대화·미게시 worker의 부재를 증명하지 않는다. root의 최신 전체 refs preflight를 다음 node 진입에 재사용·갱신해야 한다.

동일 PHYS02 bath의 full cascade는 실제 존재했던 계산이다. [PHYS02E 원 G 완료 기록](https://github.com/cosmosapjw-quantum/bass_cr/blob/2776752de6952f60d8d690a128f33fec4df2c57b/research/cr_phys02e_ncp_return_20261011/actual_run/G_COMPLETION_1.json)은 9611×9611 CSC, nnz36193027을 기록한다. 그러나 [PHYS02H historical identities](https://github.com/cosmosapjw-quantum/bass_cr/blob/2776752de6952f60d8d690a128f33fec4df2c57b/research/cr_phys02h_20261011/inputs/HISTORICAL_OPERATOR_IDENTITIES.json)는 원/reference 및 실패한 F의 raw CSC 값이 당시 조사 범위에 없었고, 해시는 값의 복구나 재구성 권한이 아님을 명시한다. 이번 E/G/H recursive tree에서도 E의 pulse NPZ·해시와 H의 작은 pilot 값만 확인했다. H 저장 SUMMARY는 full9600_complete_builds=0이다.

원 fullBED G.data SHA256은 6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd, indices는 13881363c7ce7d2681ed95092b846995aaa26197e1b03fdc4ae7c3a1ad10bd5c, indptr는 4eacd54fb6d36009fb56694c3061ccb50e2fcf5148ed4d8d4ac3e70ad596225a다. 이 fingerprint로 행렬을 복원할 수는 없다. 저장 pulse samples나 열 지연 모멘트로 새 RR history를 만들어내지도 않는다. 다른 호스트·전역 archive에 값이 전혀 없다는 주장은 하지 않는다.

## 3. 실제 source 재사용과 조건부 baryon inventory

PHYS02 source의 retained snapshot은 4ca5a90de79c8fb82a25fd9e83615bec0dfa870b, 이번 보관 retrieval은 ec463db0c7e5c7fb5070796071c926caa4db6445다. 최초 생성 commit이라는 주장은 없다. 원 fullBED NPZ SHA256은 7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc다. accepted source adapter 결과는 PR109 S=022c163726b814885805bd9a7ab988fe963cda4a에 결속되어 있다.

다음 입력은 새 계산에서 다시 만들지 않고 저장값을 읽는다.

| 재사용 파일 | SHA256 |
|---|---|
| runs/actual_v1/ACTUAL_SOURCE_RECORDS.json | 8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf |
| runs/actual_v1/RESULT.json | b1d6aed9f4db7ff5c968787c4291f2fd643b990b5263f527dda629fd16699bd6 |
| 원 energy array raw C bytes | 6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292 |
| 원 source B 전체 array raw C bytes | 07dd0fa81154f5aecaf262b00c2adfada21ebc9b2a2dba59703e03e3f5dab609 |

ACTUAL_SOURCE_RECORDS는 source ZIP 내부의 archive-only payload다. canonical SOURCE ZIP은 BASS_CR_PROPER_SOURCE_20261027_022c163726b8.zip, 2737469 bytes, SHA256 d28fc2dc841e0b3804fa2ba47274113839b54868efa0d2c63f28b865a88b9c88, 242 members다. publication/SOURCE_RELEASE_RECEIPT.json과 SOURCE_REMOTE_R3.json에 실제 Dropbox/Drive full GET 및 member hash/CRC PASS가 있다. 이 조사에서는 그 보관 영수증을 읽었고 재다운로드 R3를 수행했다고 주장하지 않는다.

**태생 tag를 선택해야 한다.** low는 active atoms3200+cutoff atom1, high는 active atoms6401이다. high source projection도 현재 E=10 노드에 일부 무게를 갖기 때문이다. selected_total에서 E<=10을 고르는 방법은 high-born 성분을 섞는다. 입력은 tag=direct_0p1_10, native birth support=[.1,10]으로 고정하고 저장 energy와 coefficient를 그대로 읽는다. 새 source quadrature·projection·729·4π·중성 target-density 곱셈은 없다.

저장 low 요약은 A_N=1.7167406375164867e-35 m^-3 s^-2, A_E=6.828624650684661e-35 eV m^-3 s^-2다. cutoff B_N=4.579701473759296e-6, B_E=4.579701473759296e-7다. 이 숫자는 이전 RESULT의 전사이며 새 배열 합산 결과가 아니다. 알려진 시간은 Q=tA, 0<=t<=1e10 proper s이며 이후 history는 unknown이다.

원 [PHYS02B source](https://github.com/cosmosapjw-quantum/bass_cr/blob/4ca5a90de79c8fb82a25fd9e83615bec0dfa870b/research/cr_phys02b_20261010/src/causal_cascade.py)에는 N_H=140, N_HE=N_H*.248/(4*(1-.248)), N_E=.01*(N_H+N_HE), neutral targets .99*N_H/.99*N_HE가 실제 들어 있다. 원 코드 SHA256 d87a9cc122125b2d37b47f261f57eab698baa59e07a6b21723860f39313c7b72다. 기존 PHYSICAL_SCALING_CANDIDATE.json은 같은100 K nH=140, nHe=1085/94, ne=2849/1880을 exact rational 입력으로 명시한다(SHA c9db56c26f64117cb6e117ecb36700cc7dce66a403b7b01024abfb058a889571).

그러므로 **새 조건부 H1/He4 inventory**를 명시하면 nb=nH+4nHe=8750/47 m^-3를 정의할 근거가 있다. 이는 elemental source를 isotope-resolved 관측으로 바꾸는 일이 아니다. H1/He4만의 귀속, xHII=xHeII=.01,xHeIII=0, 불변 proper-volume bath, 같은 frame을 새 inventory identity로 고정해야 한다. exact rational 의미 입력과 원 binary64 constructor recipe를 구별하고, 새 runtime에 사용한 density/constant의 실제 float 값·hex·해시를 보존한다. source A를 새 nb나 반올림에 맞춰 재정규화하지 않는다. PR109의 nb/null 결과도 수정하지 않는다.

## 4. 원 low-grid 및 Coulomb 정의

원 grid는 np.linspace(.1,10,3201)[1:]이다. 첫 active E=.10309375000000001 eV, 마지막10.0 eV, ghost boundary .1 eV다. 구현은 linspace를 다시 호출하지 않고 저장 source record의 energy와 stored_node_index를 사용한다. native support와 현재 energy support를 별개 필드로 보존한다.

원 PHYS02B stopping 정의는 다음과 같다. chi=1.602176634e-19 J/eV이며 kappa=chi^2/(4 pi epsilon0), v=sqrt(2 E chi/me), omega_p=sqrt(ne chi^2/(epsilon0 me))다.

b(E) = 4 pi kappa^2 ne/(me v chi) *
       min(log(v E chi/(kappa omega_p)),
           log(2 E chi/(hbar omega_p))+quantum_constant)

단위는 eV/s이고 실제 paired9600은 quantum_constant=0이다. PHYS02A의 별도 classical 표현만으로 B의 min prescription을 조용히 대체하지 않는다. 기존 source contract의 frozen100 K, superthermal·weak-coupling·비상대론 조건을 유지한다. 저에너지 경계에서도 near-thermal diffusion, electron-neutral elastic transfer, electron-ion exchange, bath feedback, subcutoff 열화는 완결되지 않았다. 기존 문헌 근거는 PHYS02A DERIVATION_KO.md §4에 있다.

원 actual runtime은 SciPy1.17.0이다. 공식 [SciPy v1.17.0 _codata.py](https://github.com/scipy/scipy/blob/8c75ae75176236f233824e9a0483c26a69e6dfec/scipy/constants/_codata.py)와 [_constants.py](https://github.com/scipy/scipy/blob/8c75ae75176236f233824e9a0483c26a69e6dfec/scipy/constants/_constants.py)를 실제 읽었다. tag object e2f9e521194c114923a9ec47409c14ff1898334a는 commit8c75ae75176236f233824e9a0483c26a69e6dfec를 가리킨다.

| 원 SciPy1.17.0 상수 | 코드 정의 |
|---|---|
| me | CODATA2022 9.1093837139e-31 kg |
| epsilon0 | 8.8541878188e-12 F/m |
| e 및 eV in J | 1.602176634e-19 |
| h | 6.62607015e-34 J s |
| hbar | h/(2*pi), exact2022=exact2018 helper |

PR107 RR config의 me=9.1093837015e-31은 다른 상수판이다. 새 recipient는 하나의 명시적 상수판을 고정하고 새 RR coefficient를 계산해야 한다. 원 SciPy package 파일 자체의 runtime hash나 저장 b-vector는 없으므로 새 b값이 과거 fullG의 비트 복구라고 주장하지 않는다. 공식 원문 파일은 remote/에 보존했고 각각 SHA005317bcd5e11a7cf5c51420a0027399a5c6e39149f3a124e22382dc384cd102 및 d4188ff2b4fb05d680c02a4b6e95d0ceb09509c2093e699ce288757e0e561cea다. 최초 web raw 요청의 DisabledError와 GitHub 읽기 복구도 보존했다.

## 5. 새 recipient의 최소 방정식과 반환

E0=.1, r_j=b(E_j)/(E_j-E_(j-1)), lambda_cj=n_ion,c v_j sigma_RR,c(E_j)로 두면 number-coordinate 저에너지 연쇄는

dn_j/dt = -(r_j+lambda_Hj+lambda_Hej)n_j
          + r_(j+1)n_(j+1) + t A_j

다. j=3200에는 incoming 항이 없고, 초기 n=0이다. 원 PHYS02 count/energy projection의 low block을 새 명시적 generator로 구성한다. inherited fullG 값의 재사용이라고 부르지 않는다. CCC input의 가장 낮은 adopted excitation marker10.20435 eV와 ionization threshold13.6 eV보다 선택 상단10 eV가 낮으므로 해당 **기존 truncated model**의 HI/HeI excitation/ionization은 이 low branch에서 없다. high-born descendant 유입도 이 단위에는 포함하지 않는다.

별도 ledger는 다음과 같다.

- cutoff count: dCcut/dt=r_1 n_1+t A_cut. cutoff kinetic Ucut=.1*Ccut.
- Coulomb caloric transfer: dHC/dt=sum_j b_j n_j. 이는 기존 stopping closure의 에너지 항이다.
- channel c RR count: dNc/dt=sum_j lambda_cj n_j.
- capture kinetic: dUc/dt=sum_j E_j lambda_cj n_j.
- retained photon count Nc, photon energy Uc+Ic Nc; binding change -Ic Nc, fast kinetic change -Uc.

직접 주입된 .1 eV cutoff atom은 즉시 cutoff ledger로 들어간다. 이 truncated boundary의 후속 RR reward는 0으로 정의하며 실제 subcutoff 재결합 부재를 뜻하지 않는다. RR energy는 **capture 현재 energy**로 계산하고 birth energy를 대신 쓰지 않는다. Rare RR count를 total injection-active-cutoff의 작은 차로 계산하지 말고 양의 RR reward를 직접 누적한다.

Verner source helper SHA71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d, 공식 table SHAa53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389는 restored/old_source에 실제 있다. 정확한 tuple 순서는 `(I_eV,Emax_eV,E0_eV,sigma0_Mb,ya,P,yw,y0,y1)`다.

| Source channel | 정확한 fit tuple | g_bound / g_ion | d=2g_ion/g_bound |
|---|---|---|---|
| HI, (Z,N)=(1,1) | (13.60,50000,.4298,54750,32.88,2.963,0,0,0) | 2 / 1 | 1 |
| HeI, (Z,N)=(2,2) | (24.59,50000,13.61,949.2,1.469,3.188,2.039,.4434,2.136) | 1 / 2 | 4 |

epsilon=E+I, x=epsilon/E0-y0, y=hypot(x,y1)로 놓으면 sigma_PI_cm2=1e-18*sigma0*((x-1)^2+yw^2)*y^(P/2-5.5)*(1+sqrt(y/ya))^(-P)다. Milne 식은 sigma_RR=sigma_PI(E+I)*(E+I)^2/[d*(me*c^2/chi)*E]다. E>0과 I<=epsilon<=50000 eV를 검사하고, fit의 threshold를 다른 spectroscopic/reduced-mass 값으로 바꾸지 않는다. 새 target density HII=.01*nH, HeII=.01*nHe로만 tagged-electron hazard를 구성한다. SI 사용 시 sigma_cm2에1e-4를 한 번 적용하고 n_m3와 v_m/s를 곱한다. thermal ne를 추가 target 인자로 사용하지 않는다.

H1II+e->H1I(1s), He4II(ground1s)+e->He4I(1s^2 singlet)를 명시한다. HeII target 전부의 ground1s 귀속은 새 고정 모델의 level-population 선택이다. HeI의 smooth fit을 Milne 역산하는 것은 기존 REI151/C23B adopted smooth ground-channel model이며 residual-ion state resolution은 조건부다. 원 fitted elemental label 자체가 isotope 관측이나 모든 에너지에서의 정확한 residual-state 분해를 보장하지 않는다. 기존 source audit의 이 조건을 지우지 않는다. spontaneous ground·stationary heavy target·zero recoil·scalar 조건을 유지한다. PW19Spectrum 생성이나 photon/source 재적분은 필요 없다. HeIII target density는 이 bath에서 명시적으로0이다.

이전 H1 CONFIG/engine의 SHA는 88fdca65935c33a90e047e2286d045bdd2433793087678c98ffb499c7adee7d2 / ab8aaa7f51a499ced7f759d16e50db076de47d65e083339a18f3ee1fca2d6005, HeI CONFIG/engine은 f4364e23d087f951e8b0d96ce98e27b86321fa25454161a743a8979f2962b099 / 4d96b4ab15bf3e2e514f2abe7e634a8bbfd1facbf30a6ae6c8725a72f7bae229다. 실제 읽은 HeI SOURCE_REVIEW SHA는 efc6e41502a2825d2ff11216f8fdb7ccdfbf5b8f0acc566e7fce2c58f9f04c8f다. 이 파일은 원 bath10000 K의 수치 응답을 수입하는 근거가 아니라 fit·가중치·조건의 재사용 근거다. 파일별 Git blob과 고정 ref는 RR_SOURCE_BINDINGS.json에 기록했다.

RR native25 반환은 H1I(index1)+NH/nb, H1II(index2)-NH/nb, He4I(index10)+NHe/nb, He4II(index11)-NHe/nb, zeta=-(NH+NHe)/nb, w_nt=-(UH+UHe)*chi/nb, w_ext=0, logT=0이다. Δnb=0이다. 이는 같은 새 inventory에 대한 **integrated RR event return**이며 thermal population 또는 coupled T 상태를 적용한 결과가 아니다. 원 source의 parent-ion chemistry가 주어지지 않았으므로 source 전체의 중성·전하 native25 closure를 구성하지 않는다. source injection, active/cutoff number·energy, RR event와 retained radiation을 각각 기록하고 radiation을 heating/w_ext로 넘기지 않는다.

## 6. 유한 인과적 계산안과 수치 의무

원 source record의 A를 그대로 넣는 ramp convolution은
n(t)=integral_0^t exp(L(t-s))*s*A ds
다. t<=1e10만 질의하고 source 바깥의 shutoff를 가정하지 않는다.

3200-state 하강 연쇄는 O(n) 저장과 O(n) matrix-vector 적용으로 구현할 수 있다. nu>=max(r+lambda_H+lambda_He), P=I+L/nu로 count-conservative active+cutoff+RR absorbing chain을 만들면 x=nu*T에 대해

y(T)=T^2 sum_(k>=0) w_k(x) P^k A,
w_k(x)=x^-2 sum_(n>=k+2)(n-k-1) Pois_x(n)

이다. 양의 Poisson terms를 n<=M에서 자르고, backward cumulative sums로 w_k^M를 만들면 k<=M-2까지만 필요하다. 이 경우 sum w_k^M=.5*Pr(Pois(x)<=M-2), missing source fraction=Pr(Pois(x)>=M-1)다. 이는 exact w_k를 단순히 k에서 자르는 방법과 다른 truncation이다. 별도 theory agent가 이 식을 독립 대수로 확인했다. bounded path-energy reward는 Emax 또는 Emax+Ic를 사용해 같은 누락 count 질량에서 tail bound를 얻는다.

희귀 RR에는 total-count bound만 사용하는 대신 channel hazard를 이용한다. active source 계수 합을 Aactive, Ninj,active=Aactive*t^2/2, lambda_c,max=max_j(lambda_cj)라 하면 Poisson-n cutoff의 channel 누락은

Bc(t) <= min(Ninj,active*Pr(Pois(nu*t)>=M-1),
             Aactive*lambda_c,max*t^3/6*Pr(Pois(nu*t)>=M-2))

로 제한된다. P^k의 capture 확률이 min(1,k*lambda_c,max/nu) 이하이고 sum_k k(n-k-1)=n(n-1)(n-2)/6이라는 양의 합에서 따른다. cutoff source의 RR contribution은0이다. 초기 RR absorber0, absorber에서 복귀 없음, count-conservative P의 조건에서 theory agent가 지수와 M-2 shift를 독립 확인했다. kinetic·photon reward bound는 각각 Emax*Bc와 (Emax+Ic)*Bc다. 두 prefix 차로 얻는 observation bin은 양쪽 prefix 오차 bound의 합을 사용한다.

추후 capture relative1e-9, count/energy closure relative1e-11을 수용치 후보로 고정할 수 있다. 다만 양의 계산값 Nc를 곧바로 certified lower bound라고 부르지 않는다. 수학 tail과 별도 arithmetic 오차 검산을 결합해야 한다. lambda_max=0은 exact zero지만 lambda_max>0인데 계산된 capture가0이면 relative-zero 검사가 아니라 absolute enclosure가 필요하다. 현재 이 값은 제안이며 root가 C4 전에 error-budget 분배·실행 허용치를 동결한다.

실제 complexity는 O(n*M) 시간과 O(n+M) 저장이며, M은 nu*T와 선택한 tail tolerance에 의존한다. 여러 prefix는 같은 P^k A sweep과 각 prefix의 weight를 공유할 수 있다. 현재 숫자 stiffness나 runtime을 계산하지 않았으며 40 CPU cap 안에서 충분하다고 측정 주장하지 않는다. 작은 changed-coefficient/stiffness probe는 root가 frozen C4 예산에 넣은 뒤 수행할 수 있다. exp(-x) underflow를 피하는 Poisson 평가, tail의 산술 오차, primitive coefficient 오차, binary64 generator 보존 defect를 수학 truncation bound와 별도 검사해야 한다. Decimal/interval weight 준비 또는 mode-centered recurrence를 택할 수 있으며 raw mass defect를 조용히 재정규화하지 않는다.

실용적 독립 검산은 같은 입력 배열의 별도 sparse augmented exponential action이다. 두 source clock states u'=1, source scalar'=u를 붙여 ramp와 count/energy ledgers를 한 번에 적분한다. 생산 uniformization과 다른 알고리즘·별도 코드를 사용하고 희귀 RR reward의 상대 정확도가 전체 source absolute tolerance에 묻히지 않도록 ledger scaling과 수용 기준을 미리 고정한다. 정확 represented finite operator와 grid/closure 물리 오차를 구별한다.

각 observation bin은 이전 source-born population을 계속 포함한다. [T/2,T] 반환은 R(T)-R(T/2)이며 T/2에서 초기0으로 재시작한 계산이 아니다. T/4,T/2,3T/4,T의 네 prefix를 쓰면 전체 구간을 덮는 disjoint return bin도 네 개다. source injection은 family/birth partition/history 한 번만 claim한다. cumulative prefixes는 diagnostic/nonadditive, 실제 return registry는 family+channel+native birth partition+observation bin 중첩을 검사한다. PR109의 injection-window-only return guard를 그대로 호출하면 합법적인 disjoint observation bins가 거절되므로 새 causal adapter가 필요하다. 기존 ports.py는 변경하지 않는다.

## 7. 재사용 구현과 새 실행기에서 필요한 변경

재사용 가능한 것은 PR109의 source 검증·once-only normalization·physical family identity와 fixed-nb generic projector 계약이다. accepted103 controls/18 source rows/153 independent checks를 동일 해시로 다시 실행할 이유는 없다. attach_rr_return는 He4III→He4II hardcoded하므로 새 H1II→H1I·He4II→He4I causal adapter를 별도 구성해야 한다. 원자 isotope/state, matching inventory/frame, native support, event ownership과 horizon을 새 양성/거절 control로 검증한다.

old runner SHA724f816a9a90edbf8cfd9b582a0c12570aaf65cfecc80583e10f709cf1e5a56f는 unit_id와20 CPU cap가 고정되어 있다. 새 파일에서 새 unit_id·새40 CPU 후보·새 frozen C4 receipt를 결속하고 old ledger를 읽지 않는다. 보존할 장치는 create-only attempt debit, preworker 실패 비용, max-per-attempt 중복 제거, reservation/NO_ACK 차단, 실제 owner process group, affinity1/native thread1, initial/final memory admission, host receipt hash, tighter per-attempt cap<=frozen upper다.

이전 independent_v1 메모리 refusal .066297과 plot_v1 reservation FAILED3.07135는 그대로 남는다. plot의 worker exit0·생성된 파일과 reservation PASS는 다른 축이다. 새 plot을 필요로 하면 saved new result만 읽고 실제 관측된 2.764225 child CPU 및 coordinator/tail 비용을 참고해 새 예약을 따로 책정한다. 과거 plot 재렌더는 없다. Per-process RLIMIT_CPU를 aggregate child CPU의 hard preventive proof라고 부르지 않으며, 새 supervisor의 aggregate monitoring/자식 정책을 실행 전 명시해야 한다. Cgroup clean-inactive estimate는 admission 추정이지 보증이 아니다.

원 중앙27/88,88nodes/17edges,이번 후보 count effect0을 유지한다. N4/N5 PARTIAL_OPEN,N6/N7 PREDECESSOR_GATED,L4false,global completion/error/budget remaining/currency null이다. WU/REC/HE의 최신 provider 변경은 root와 source 담당자의 별도 intake가 authority를 갖는다. 개인 대화 전체 검색 unavailable·Drive partial inventory 한계도 유지한다.

## 보존한 증거

PR108_CURRENT.json, RECENT_PRS_CURRENT.json, TREE_*.json, remote/PR108_*, remote/PHYS02H_HISTORICAL_OPERATOR_IDENTITIES.json, remote/PHYS02E_G_COMPLETION_*.json, remote/PHYS02G_REPORT_KO.md, remote/PHYS02H_REPORT_KO.md, remote/PHYS02H_PARALLEL_SUMMARY.json, remote/PHYS02B_CCC_USED_CHANNELS.json, CR branch 양쪽 page, 공식 SciPy source/tag/최초 web 실패를 이 조사 폴더에 보존했다. 이 문서의 제안은 root의 frozen scope와 독립 이론 검토를 거쳐 production으로 옮긴다.

