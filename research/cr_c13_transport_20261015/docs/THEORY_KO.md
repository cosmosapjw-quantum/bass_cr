# C13 구성적 유도: born-age Bianchi-I photon stock + 국소 H/He

## Source binding과 계산 영역

기준 owner rei_bianchi commit 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
C11의 세 소스 파일 SHA-256 검사를 그대로 재사용한다.
실제 Rust igm_rates.rs source의 Case-A RR 계수는 Python으로 전사하고
T=100,2000,4000,5500,5501,10000,200000 K에서 직접 Rust 컴파일 결과와
검산했다. 기본 signature (-,+,+,+). c=29979245800 cm/s, kB는 eV/K,
proper particle densities cm^-3, photon counts are per original H nucleus.

실험 구간은 a=0.10->0.11 (z=9->8.09...), shear q=-.01,0,+.01.
가스 초기조건 xHI=.9, (xHeI,xHeII,xHeIII)=(.85,.15,0), Tgas=4000K.
이것은 임의의 control state이므로 관측 이온화 역사로 읽지 않는다.
고정된 comoving H 원자 수에 대해 proper nH(a)=nH0/a^3,
nHe(a)=y nH(a), y=const. 실제 owner Scenario.rate(a)로 광자 생성을
dN/H=[rate(a)/H(a,q)]d ln a 로 환산한다.

## 방향 photon redshift와 전파

Source packet은 태어날 때 orthonormal tetrad µ_birth 및 E_birth를 기록한다.
Owner b(a,q)에 대해 횡/종 에너지 비는
  U_perp(a_b->a)=(a_b/a)exp[b(a)-b(a_b)],
  U_parallel(a_b->a)=(a_b/a)exp[-2(b(a)-b(a_b))].
따라서 E(a)=E_birth sqrt[(1-µ_birth²)U_perp²+µ_birth²U_parallel²].
Birth 순간 1, q=0에서 a_b/a를 만족한다. 각도 적분은 birth 방향의
양의 isotropic dµ_birth/2다. 방향성 photon number는 각 source cohort의
원 original-H당 수를 추적하므로 owner 현재-frame intensity의 R*J를
중복 적용하지 않는다. SOURCE07 현재-frame R*J와 수학적 동등성은
아직 원래 transport identity/observer 계약을 통해 검사하지 않았다.

한 시간구간마다 midpoint 또는 2점 GL에서 실제 photon이 생성된다.
이전에 태어나지 않은 광자를 초기 stock에 선주입하지 않는다.
방출 E_birth=13.6..100eV, 원래 50000K BB, H/He ionization-edge
13.60/24.59/54.42eV 분할의 양의 GL 적분을 재사용한다.
Born cohorts는 현재 redshift와 opacity를 계속 겪으며 photon 수는
comoving original-H 정규화이므로 기하학적 부피 희석을 두 번 넣지 않는다.

## 광자-이온화-재결합

HI/HeI/HeII j에 대해 sigma_j(E) Verner 적분:
  tau_kj=c delta_t n_j(a) sigma_j(E_k);
  dA_kj=N_k (1-exp(-sum_l tau_kl)) tau_kj/(sum_l tau_kl).
tau=0 극한 0을 쓰고 expm1 구현으로 오차를 줄인다. Photon 생존 수
N'_k=N_k exp(-sum_l tau_kl)이므로 N_k-N'_k=sum_j dA_kj>=0.

H: dxHI=-dAHI, xHII=1-xHI.
He: dxHeI=-dAHeI/y, dxHeII=(dAHeI-dAHeII)/y,
dxHeIII=dAHeII/y. x_e=1-xHI+y(xHeII+2xHeIII).
Total binding plus heat from absorption:
  dB_ion=sum_j I_j dAj,
  dUth=sum_j dAj(E_k-I_j).
I_j는 physical binding energy이며 Verner fit threshold와 구분한다.

재결합 경로는 owner RR subset alpha_HII/alpha_HeII/alpha_HeIII만 사용한다.
HII->HI exact exponential. HeIII->HeII->HeI는 동결 n_e,T인
단방향 Markov 계의 exact finite-time 해이며 SciPy expm으로 교차검산.
상세 DR/CI, photon OTS feedback, secondary ionization, full Grackle cooling,
Ly-alpha radiation are NOT implemented. Recombination photon은 외부로
escape된 것으로 기록하고 새로운 photon stock에 추가하지 않는다.
재결합 thermal closure는 사라진 free electron 하나당 (3/2)kB T의
translational energy가 escape된다고 가정한다. 이는 원본 igm_thermal.rs
냉각식과 다르므로 Tg의 물리적 정확도는 아직 unresolved다.

## Ledger identity와 Wolfram

광자 최종 stock E_gamma=sum_k N_k E_k와 초기/최종
gas Uth=(3/2)kBT[1+y+x_e], source photon E_src를 기록한다.
광자의 energy redshift에 따른 signed geometric work W_geom,
gas adiabatic loss W_ad, ionization binding B_photo,
recombination binding release B_rec, electron translational escape Q_rec를
각각 기록한다. 이 discrete model에서
 E_src = E_gamma_final+(Uth_final-Uth_initial)
         +W_geom+W_ad+(B_photo-B_rec)+(B_rec+Q_rec).
Photon-number: Nsrc=N_gamma_final+sum_j A_photo,j.
He nuclei, H nuclei, electronic neutrality are algebraic invariants.
Wolfram으로 absorption probability sum + survival=1을 직접 검산하고
q small anisotropic energy ratio의 angular first derivative 평균
integral_-1^1(1-3mu²)dmu/2=0을 확인했다.

## Numerics, limits and scientific decision

Source-born midpoint quadrature는 정확 source photon count에 대해
O((d ln a)^2) 수렴했다. 2점 source GL는 midpoint보다 emitted photon
count 오차를 크게 줄인다. 그러나 coupled gas xHI,T에 대한 16,32,64,
128 step 비교에서 numerical convergence가 아직 명확한 2차가 아니고
대략 1차에 가깝다. Source quadrature만 고쳐 이 문제가 사라지지 않는다.
이는 solver numerical gate HOLD (stiff opacity, chemistry splitting,
piecewise owner K2 coefficient 5500K switch 등을 분리 검토할 의무).
광자수와 위 discrete energy ledger의 machine-size 잔차는 전체
물리 time-accuracy 합격을 뜻하지 않는다.

그 외 spatial streaming, true external-source radiation R*J, anisotropic
ray/flux transfer, helium OTS, full Grackle cooling, clumping/MFP, source
feedback, cosmological ion/electron/temperature histories는 absent다.
본 결과는 현재 owner SOURCE07 C8/AX08 production closure가 아니다.

관련 원전: Friedrich et al. (2012) MNRAS 421 2232 H/He C2-Ray,
https://academic.oup.com/mnras/article/421/3/2232/1077406 .
Norman et al. (2015) ApJS 216 16 fully coupled radiation and chemistry,
https://doi.org/10.1088/0067-0049/216/1/16 .
Baumschlager, Shen and Wadsley (2024) A&A spectral reconstruction
and HeII edge sensitivity,
https://www.aanda.org/articles/aa/full_html/2024/11/aa48164-23/aa48164-23.html .
