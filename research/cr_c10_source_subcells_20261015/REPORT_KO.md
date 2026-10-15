# BASS_CR C10/R5: SOURCE07 C6의 HeI centroid 이온화 오차를 source-conditioned subcell 적분으로 분리·개선

**2026-10-15 KST.** 직전 저장소: `cosmosapjw-quantum/bass_cr` draft PR #68 head `5b5aa612be22072239392702548cd44f8ddce105`. 비교 대상: 실제 `rei_bianchi` SOURCE07 C5, head `e9c52f14e6ce50bb3b3924cda4ba34472caa28b4`에서 읽은 `axbi_q_grid.rs`, `NEXT_C6.json`, `independent_spectrum.py`, 물리 source code. 신형 source, full numerical EoR, 기존 AX08/AX11/AX12, 원본 q solver 등은 건드리지 않는다. Native subagent NOT_RUN(도구 없음), local Codex 미사용.

## 1. 선택한 해소 문제와 결과

기존 고정 reference-q grid는 정상적인 주입 photon count N과 reference energy moment U_*를 계산한 후, `E_cell = R U_*/N`에 적용한 Verner opacity로 각 셀의 frozen-neutral 광이온화를 수행한다. HeI fit cutoff 24.59 eV가 에너지 셀을 가로지를 때 단면적이 `E<chi_fit`에서 0, `E>=chi_fit`에서 양수이므로, q-grid centroid에서 단일값을 평가하면 두 moment의 보존에도 불구하고 **종별 reaction rate**가 틀릴 수 있다. C5 owner의 실제 N_E256, N_mu32, q0 결과는 HeI photoevent −1.21148%, photoheat +0.045094%였다.

이번 `source_subcells.py`는 원 **MD14_Z002_FESC_BB50K_13P6_100_V1** native source 48개 계수를 변형 없이 가져온다. Native Simpson32 photon fractions `f_c`와 온도 50,000K blackbody shape `S(E)=E²/expm1(E/k_BT*)`를 사용한다. 각 원본 native source cell의 연속 보간 `f_c S(E)/I_c`를 개별 고정-q spectral cell과 교차시키고 양의 Gauss–Legendre GL8 점을 만든다. 원본 native source cell 경계(13.60, 24.59, 54.42, 100eV)에서 **반드시** 나뉘므로 Verner HeI/HeII 문턱의 jump 위에서 매끄러운 적분이라고 가정하지 않는다. 각각의 native source cell 내 quadrature weights를 원본 `f_c`로만 정규화한다.

*결과*: 실제 동일한 z20 proper neutral HI=0.0017575700008892194/HeI=0.0001429214010766023/HeII=0 cm⁻³, source photons 4.298036114764196e−8/H, **dt=1e10 proper seconds**, q0, fixed shape 중 새 HeI species event는 C5 owner의 독립 SciPy source 연속 적분과 상대차 약 9.396×10⁻¹²다. 기존 centroid는 nE256에서 −1.2114770326%; nE1024에서 +0.40774395%로 부호가 바뀐다. GL4/8/12/16와 nE64/128/256/512/1024의 subcell event는 모두 owner source 연속 적분과 약 10⁻¹¹ 상대차였다. **이 정도의 일치가 EoR 방정식의 전 시간구간 error certificate는 아니다.**

## 2. 양의 원본 source weight, source rate, 실제 physical binding

Normal tetrad signature(-,+,+,+), rest-frame proper seconds. SOURCE07 physics에서 q ray의 순간 실제 에너지는 `E_phys=R E_*`, `R>0`; angular solid-angle Jacobian `J_Ω`와 emission weight `ω`의 적용은 owner만 담당하며 새 code는 이미 source-weighted per-ray photons를 입력받는다. Same-ray 또는 identical owner epoch/clock 이외 photon은 혼합하지 않는다.

원본 native source cell c의 방출 photon fraction은 `f_c`. 연속 interpolation `dμ_c=f_c S(E)dE/I_c`, `I_c=∫_c S(E)dE`로 정의한다. q-grid i에 대한 교차구간 `B_i∩c`에서 Gauss8의 **양의** 노드/weight `(E_j,w_j)`로

```
N_i = Σ_(j∈i) w_j,     U_i,* = Σ_(j∈i) w_j E_j/R,
λ_k(E)= c_cm_s × n_k,proper × σ_k,Verner(E),   Λ(E)=Σ_k λ_k(E),
p_k(E) = { (1-exp(-Λ(E)dt)) λ_k(E)/Λ(E) if Λ>0; 0 otherwise },
A_i,k = Σ_(j∈i) w_j p_k(E_j),
H_i,k = Σ_(j∈i) w_j p_k(E_j)(E_j-I_k,binding).
```

`σ_k`는 original `AtomicProvider` Verner fit, **fit thresholds** (13.60,24.59,54.42)eV, **distinct chemical binding** (13.598434599702,24.587389011,54.41776)eV. 지수감쇠는 source-owner C5의 `exp(-Λdt)`이며 직전 bass_cr의 backward-Euler 형태와 혼동하지 않는다.

동일 quadrature measure를 사용하는 한 **photons after** `N_i′=Σw_j exp(-Λ_jdt)`, `U_i,*′=Σw_j(E_j/R)exp(-Λ_jdt)`에 대해

```
N_i - N_i′ = Σ_k A_i,k,
R (U_i,* - U_i,*′) = Σ_k [H_i,k + I_k,binding A_i,k]
```

가 이론상 정확하다. 실제 nE256 q0 double 실행에서 전체 count ledger residual은 `~6.6e−24 photons/H`, energy ledger residual은 `~1.59e−22 eV/H`였다. Source nE256 q-grid stored N,U 두 f64 배열은 angle마다 4096bytes인데, source-conditioned GL8 nodal preview는 임시 ~81KB(에너지/count/reference/bin 및 3 fit arrays)다. **이를 매 시각의 영구 photon field로 쌓는 구조가 아니다.**

## 3. 아예 N,U만으로 전체 spectrum shape를 복원할 수 없음

HeI cutoff `χ=24.59eV`에서 `μ_A=δχ`, `μ_B=(δ_(χ−ε)+δ_(χ+ε))/2`는 동일 count `N=1`, 동일 first energy moment `U=χ`를 갖지만, HeI fit의 jump가 있으므로 반응률은 일반적으로 다르다. ε→0+에서 한쪽 weight의 HeI absorption이 0인 반면 다른 쪽은 양이다. **두 positive source가 동일 N,U인데 다른 HeI A,H를 낸다.** 이 범위의 no-go는 moment-only arbitrary-shape opacity를 사용할 수 없다는 뜻이고, 모든 photon compact representation에 대한 no-go가 아니다.

따라서 이번 개선이 바로 사용 가능한 범위는 `(1) known original fresh source injection` 또는 `(2) independent verified source-conditioned shape closure`다. 흡수와 반복 redshift를 겪어 hardened된 임의 stock은 원 stellar BB50K shape를 자동으로 되돌릴 수 없다. Owner C6의 실제 shape evolution은 separate construction이 필요하다.

## 4. 실제 Rust owner와 독립적인 수치 대조


a. 실제 `rei_bianchi` SOURCE07 C5의 q0 nE256 frozen-gas centroid event `3.12053792820337006e−8 photons/H`, heat `1.45995781352239345e−7 eV/H`를 Python에서 같은 q-edges·N,U·σ로 재현했다. 차이는 event `~2.25e−22`, heat `~2.04e−21 eV/H` (absolute)였다.

b. Owner의 별도 `independent_spectrum.py` reference는 continuous source total event `3.121739695857463e−8 photons/H`, heat `1.4592997571739564e−7 eV/H`, HI `2.978921350017158e−8`, HeI `1.4281834584030507e−9`. 새 q-grid source-subcell는 각각 해당 reference와 `~1e−11` 이하 relative difference로 일치한다.

c. nE별 HeI centroid error [%]: n64 −1.207477663, n128 −1.210669474, n256 −1.211477032, n512 −1.211679520, n1024 **+0.407743950**. 같은 source를 사용한 threshold-split GL8의 owner reference discrepancy는 각 nE에서 `+9.396e−10%` 정도다 (기본 상수/원본 Simpson32 차 포함). 이는 spectral-grid refinement가 centroid branch를 스쳐갈 때 nonmonotonic rate bias를 만들 수 있음을 보여준다. *C5 native Rust 직접 실행을 교체한 것은 아니며 저장된 native 결과와 독립 Python matched oracle 대조다.*

## 5. 최적화/경량화/병렬화

`SourceQuadrature`는 q-bin membership, 물리 E, 원본 weight, Eref를 binary64 numpy 배열로 갖는다. 연속 spectrum source quadrature는 emission 시에만 만들고 `CachedReactionKernel`에서 Verner σHI/σHeI/σHeII를 precompute한다. 최대16개 bounded LRU `ratio_R` spectrum identity에 대해, 동일 source·다른 proper neutral density/dt를 여러 ray로 받는 `batched_frozen_reactions`는 max16개 case씩 batched numpy broadcasting/einsum으로 species events/heat를 계산하며, independent rays를 섞지 않는다. Scalar uncached, scalar cached, vectorized 세 경로의 출력을 매 ray에서 비교한다.

ChatGPT Python 실행 환경, nE256, 128 independent frozen gas states, 같은 physical spectrum Verner coefficients: uncached scalar 대비 298.4×, cached scalar 대비 **216.6×**의 measured speedup; NumPy batch ~2.54 ms vs cached scalar ~549.39 ms였다. 이는 **one-shot source kernel build 비용을 제외하고** 같은 cached kernel의 반복 reaction readout을 측정한 것이며 원 Rust 전체 solver speedup도 CUDA 가속도 아니다. 1/2/4 Python process scalar 병렬 benchmark도 포함되며, process startup/IPC가 이 문제 크기에서 더 비싼지 실제 결과로 기록한다. 코드 및 test는 Python NumPy/SciPy, 외부 network 불필요.

동일 source `ratio_R`에서 Gaussian source native48 fraction은 owner 원본과 같은 배열로 정규화된다. 서로 다른 R이나 소유권/clock은 새로운 source transformation이 요구된다. Workstation performance는 별도 readback 후 비교하여 인증한다.

## 6. CAS, 이전 연구 재사용과 게시 계약

Wolfram Language15.0.1에서 photon count+energy first moment, exponential absorption number/energy/binding cancellation 등 5 scalar residual=0. Official-source SHA-pinned xAct/xTensor1.3.0에서 null photon, local projector, same-ray four-momentum and q-energy moment 등 5 residual=0. CAS와 Python은 같은 작성자의 다중 계산 경로이며 외부 peer review는 아니다. SciSpace/Exa 원문으로 Verner et al.(1996) astro-ph/9601009, Mirocha et al.(2012) arXiv1204.1944, Baumschlager et al.(2024) arXiv2310.16902, C2-Ray 원논문을 확인했다. 기존 G/RCT/HH atomic coefficients나 HE/HM12 warm source는 변경하지 않는다.

시스템은 SOURCE07 C6가 이미 가진 actual Rust q-grid plus frozen H/He owner를 읽었다. 본 result는 *보조적인 standalone source regression and positive threshold-resolved quadrature*, owner 코드나 production history를 자동으로 덮어쓰지 않는다. `next`는 SOURCE07의 별도 버전에서 source-conditioned quadrature와 time-evolved unknown spectral shape representation을 비교하는 C6 scoped native test, 실제 q-family의 R*J·성분별 source/clock·heating/opacity 수렴 test. bass_cr Landau fine kinetic constitutive/adjoint 작업은 별도 PENDING 그대로다.
