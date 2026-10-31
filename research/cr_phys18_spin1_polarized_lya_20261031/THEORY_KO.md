# PHYS18: 원본 2p 사건의 PSD 밀도행렬과 방향별 Lyα Stokes 방출

## 원래 source와 현재 새로운 물리적 범위

`cosmosapjw-quantum/bass_cr`의 부모는 PR #142 HEAD `b64d3a0e1895e004e89ea3ffc92ceb6aadd5c55c`. 원본 6,400 H/He RR photon source 중 원본 He-RR 기원 H 첫 광흡수 후 전자의 H(1s→2p) 첫 비탄성 여기 공통영역 2,066개만 사용한다. NIST BE-scaled *전체* 2p rate와 Shah H EII 경쟁 및 proper-time birth를 다시 정하지 않는다. 기준 E21=10.1988 eV, 중성 HI 100 K, 원본 t=1e10 s. 서로 다른 물리적 claim과 코드 검증을 별도로 평가한다.

Kingston–Fon–Burke (1976), J Phys B 9 605 (doi 10.1088/0022-3700/9/4/010), printed p.613 Table 5는 순수 1s→2p **unitarized-Born 계산 미분단면적**이다. Williams (1976) p.1526 Table 1은 *실측 n=2=2s+2p* 합이다. PHYS17의 원문 전사 `primary_tables.py`를 변경하지 않고, 원본 source event `SOURCE_UB2P_RECOIL_CROSSWALK.csv`의 정확한 2,066 event identity를 재사용한다.

**새로운 문헌으로 확인된 핵심:** Williams (1998), *Australian Journal of Physics* 51 633–643, doi:10.1071/P98023, 공식 원문 https://www.publish.csiro.au/ph/pdf/p98023 는 16.5 eV에서 2p 미분단면적(그림 6)과 2p angular/polarization correlation λ,R,I(그림 7)를 **실제 측정**했다고 밝힌다. Bray–Konovalov–McCarthy (1991), *Phys Rev A* 44 5586, doi:10.1103/PhysRevA.44.5586는 13.87/16.46/19.58 eV에서 λ,R,I를 **계산**했다. 두 원전의 정확한 실험/이론 데이터 숫자는 여기서 취득 또는 digitization하지 않았으므로 과학 CSV에 측정 2p density matrix를 만들어 넣지 않는다. Williams (1998)의 DOI와 원문을 직접 찾아 Fig.6/7을 수치화하거나 원저자 수치 파일을 확보하는 것이 다음 genuine source intake이다.

## Spin-1 positive-semidefinite density matrix family (모형 구성, 실측 아님)

전자 입사방향을 z축으로 고정한 **조건부** 충돌 좌표계를 사용한다. 산란전자 방향(μ=cosθ_e, φ_e)에서 원자 recoil q=p_i-p_f, |qhat|=1이며 PHYS17의 정확한 비상대론적 두 입자 에너지 보존을 사용한다. 전자충돌 원전각도 PDF는 

\[w(\mu|E)=D_{KFB,UB2p}(E,\arccos\mu)\Big/\int_{-1}^1 D_{KFB,UB2p}(E,\arccos\xi)d\xi.\]

신규 검증 가능한 일차 모델 family는 Cartesian electric-dipole 2p orbital basis에 대해

\[\rho_{\zeta}(\hat{\mathbf q})=\frac{1-\zeta}{3}I_3+\zeta\hat{\mathbf q}\hat{\mathbf q}^{\mathsf T},\quad -\tfrac12\le\zeta\le1.\]

Eigenvalues `(1+2ζ)/3,(1−ζ)/3,(1−ζ)/3` 및 trace=1. ζ=1은 전이 dipole이 momentum-transfer에 평행한 pure-state Born closure의 확장, ζ=0은 등방 2p 무정렬, ζ=−1/2은 q에 수직인 두 상태의 등혼합. **이것은 전체 물리적으로 허용되는 3×3 복소 밀도행렬 집합도, 측정된 λ,R,I의 재구성도 아니다**. 충돌 복소 위상/교환/미세구조 등에 의해 다른 coherence 및 V가 가능하다.

광자 관측 방향 n과 국소 transverse basis (e_theta,e_phi)에서 E1 coherency의 단위 입체각 확률은

\[J_{ab}(\hat n\mid\hat q)=\frac{3}{8\pi}e_a^i(\rho_\zeta)_{ij}e_b^j, \quad a,b\in\{\theta,\phi\}.\]

Stokes `I=Jθθ+Jφφ`, `Q=Jθθ−Jφφ`, `U=2 Re Jθφ`, `V=−2 Im Jθφ`. 구면 적분 ∫I dΩ=Tr ρ=1; 모든 주파수에서 Stokes cone `I²≥Q²+U²+V²`은 PSD의 결과. Source rate에 본 각도 분포만 곱하고 총 여기 개수는 원본 그대로다.

상대 전자 recoil 방향의 quadrupole은

\[A_2(E)=\int_{-1}^1w(\mu|E)P_2(\hat q\cdot\hat k_e)d\mu.\]

전자 scattering azimuth φ_e에 대해 축대칭 평균을 취하면 \(\bar\rho=\mathrm{diag}[(1-\zeta A_2)/3,(1-\zeta A_2)/3,(1+2\zeta A_2)/3]\). 관측 극각 θ에서

\[I(\theta|E,\zeta)=\frac{1-\zeta A_2(E)P_2(\cos\theta)}{4\pi},\quad Q(\theta|E,\zeta)=\frac{3\zeta A_2(E)\sin^2\theta}{8\pi},\quad U=V=0.\]

전자축이 완전히 등방이라면 다시 \(\bar\rho=I_3/3\)가 되어 단일 방향에 대한 전체 집단은 I=N/(4π), Q=U=V=0. **사용자가 제공한 RR photon source에는 2p를 여기하는 광전자의 공통 거시적 입사 방향 distribution이 묶여 있지 않다.** 따라서 본 스펙트럼은 기하학적으로 고정된 빔 관측조건의 진단이며 Bianchi/IGM observable을 주장하지 않는다.

## Recoil와 관측방향에 조건화된 line-centre 및 frequency Stokes

광자 방출의 photon recoil `η_em=hν0/(2M_H c v_th)`와 관측방향으로 투영한 들뜬 원자의 운동을 사용하여

\[x_\mathrm{centre}=\frac{|\mathbf q|}{M_H v_{th}} (\hat q\cdot\hat n)-\eta_{em}+x_\mathrm{thermal},\qquad v_{th}=\sqrt{2k_B T/M_H}.\]

`x_thermal`은 분산 1/2의 Gaussian, photon natural line은 정상화 Voigt φ_V(x)=Re wofz(x+ia)/√π. 따라서 방향별 Stokes frequency density는

\[J_{ab}(\theta,x|E)=\int_{-1}^1d\mu\,w(\mu|E)\int_0^{2\pi}\!\frac{d\varphi}{2\pi}\,J_{ab}(\hat n|\hat q)\,\phi_V\!\left(x-\frac{|q|}{M_H v_{th}}(\hat q\cdot\hat n)+\eta_{em}\right).\]

본 연구는 2,066 개 source별 에너지의 실제 가중치를 이용해 `earliest/latest`와 ζ={−0.5,0,0.5,1}에 대해 **각도적분 Stokes**, ζ={−0.5,0,1} 및 θ={0,90,180}에 대해 x∈[−12,12] 주파수별 Stokes를 계산했다. 선 중심 모멘트는 Lorentz natural broadening **이전의 centre**를 뜻한다. 자연선폭을 포함한 Voigt의 두 번째 모멘트는 유한하지 않다.

## 물리적 귀결과 엄격한 한계

- `derived`: ρ(ζ) PSD, source emitter counting conservation, axial Stokes formulas, q·n recoil correlation, equal-poles intensity, opposite-poles line-centre offset.
- `numerically_checked`: 원본 2,066 source energy 각각 KFB-UB2p original angular owner, 3,628 scientific CSV rows, 4 new figures. 38 physics/source/invariant tests; same-author, no fresh independent scientific author.
- `literature_supported`: Williams 1998 provides 16.5 eV distinct 2p DCS and λ,R,I **figures**, Bray/Konovalov/McCarthy 1991 gives model at 13.87/16.46/19.58 eV. The exact plotted numeric values have not yet been independently extracted into source-owned arrays.
- `conjectural`: ζ family, fixed beam common axis, KFB-UB model angular shape, q-aligned emitter part, spin/fine-structure neglected.
- `unresolved`: actual magnetic sublevel ρ(E,μ), true electron-ray directions at source, source-owned physical polarization, full detailed-balance RII, multiscatter, physical K, global He exclusive, common gas-radiation-clock-Bianchi geometry. Central DAG 28/88, extension 0/3 both Δ0; production/NATIVE25/L4 HOLD, NO_MERGE/NO_FORCE_PUSH.
