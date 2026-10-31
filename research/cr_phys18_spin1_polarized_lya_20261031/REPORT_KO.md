# BASS_CR PHYS18 | original source-weighted spin-1 PSD polarized Lyα emission (2026-10-31 KST)

## 이전 기준 / 원본 identity

- GitHub PHYS17 PR #142 HEAD `b64d3a0e1895e004e89ea3ffc92ceb6aadd5c55c` (parent source), `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false` 유지.
- Source-inclusive PHYS17 ZIP 23,698,810 bytes SHA-256 `5fc70cfa638f6b6fffbc61f05f46d28a9be1eefef43851a75bb175383d87666d`, nested as `sources/PR142_PHYS17_SOURCE.zip`.
- 원본 6,400 H/He RR source photons, 2,066개 유효 He→H→electron H(1s→2p) 행사, 네 개 proper-time birth bin, 100 K static HI, 10^10 s observation clock. Original NIST BE total rate/Shah measured EII 100% 재사용. 새 gas IVP, Bianchi background, full electron stopping K, He exclusive, full line transfer NOT RUN.

## 새 원전과 실제 새 물리

이전 1976 Kingston/Fon/Burke Table5는 2p *unitarized Born* 이론 DCS이고, Williams 1976 Table1은 n=2 inclusive. 이번에 확인한 J.F. Williams (1998) *Australian Journal of Physics* 51 633–643 DOI 10.1071/P98023, https://www.publish.csiro.au/ph/pdf/p98023 는 16.5eV에서 **별개 measured 2p DCS(Fig6)** 와 `lambda,R,I` **angular polarization(Fig7)** 를 발표했다. Bray/Konovalov/McCarthy (1991), *PRA* 44 5586 DOI 10.1103/PhysRevA.44.5586는 13.87,16.46,19.58eV의 λ,R,I 계산을 수행했고, Wang/Callaway/Unnikrishnan (1994), *PRA* 49 1854 DOI 10.1103/PhysRevA.49.1854는 16,20eV에 pseudostate close-coupling 값을 제공한다. 그러나 **1998 측정 Fig6/7 수치형 배열과 실험 공분산은 이번 산출물에 미포함**. 다른 결과와 혼합하지 않음.

선형 편광을 실제 계산한 새 모델은 H 2p spin-1 Cartesian substate density-matrix family `rho_xi=(1-xi)I3/3+xi|q><q|`, `-1/2<=xi<=1`, 고윳값 `(1+2xi)/3, (1-xi)/3, (1-xi)/3`, trace=1, PSD. 전자 입사 방향은 전 source에서 **공통 z축으로 조건화**됨. 2,066개 각 e 에너지는 genuine PHYS17 source csv이며, Kingston 1976 2p UBorn 미분각도 pdf 및 고전 운동학 recoil을 사용했다.

Emitted Stokes coherency `J_ab(n,q)=3/(8π) e_a·rho·e_b`, `I=J_tt+J_pp`, `Q=J_tt-J_pp`, `U=2ReJ_tp`, `V=-2ImJ_tp`. 전자 산란 azimuth를 평균하면 `A2(E)=<P2(qhat·zhat)>`; `I(n)= [1-xi*A2*P2(cosθ)]/(4π)`, `Q(n)=3xi*A2*sin²θ/(8π)`, `U=V=0` (이 한정 family에서). 전 하늘 적분 광자수 보존. `xi=0` 정렬 없음 → isotropic unpolarized. 입사 전자축이 원천적으로 등방이라면 모든 출생 사건의 global Stokes polarization은 사라진다.

100 K Doppler+Voigt frequency model은 `x=(ν−ν0)/Δν_D`, `x_c=v_rec*(qhat·n)/v_th−eta_em+thermal`, `eta_em=hν0/(2M_Hcv_th)` and `thermal variance=1/2`. Natural Lorentz convolution 전의 line-centre mean/variance만 보고한다. 진짜 Voigt second moment는 발산한다.

## 실제 새 물리적 데이터

| Numeric output | Rows | Scientific unit |
|---|---:|---|
| `SOURCE_2P_ALIGNMENT_MOMENTS.csv` | 2,066 | source index, electron Ee, KFB2p q-axis A2, rate weights, mean recoil |
| `SOURCE_DIRECTIONAL_STOKES_ATLAS.csv` | 104 | 2 birth×4 PSD xi×13 observer theta, Stokes per sr, Q/I, pre-Voigt center moments |
| `SOURCE_DIRECTIONAL_STOKES_FREQUENCY_ATLAS.csv` | 1,458 | 2 birth×3 xi×3 observer theta×81 Doppler x; Stokes I,Q,U,V per sr and x |
| TOTAL | **3,628** | 원본 계수 재사용, 복사수송/산란 미결합 |

`Ee=14.6014..20.99 eV` 유효 원본 source에서 `A2=0.545847526..0.755302421`. 실제 original excitation earliest `3.3158906934521573e-31 m^-3`, latest `9.85567761064524e-32 m^-3` 그대로.

Early birth source-weighted A2=`0.662630296046`, latest=`0.662336543215`. Observed θ=90° source-integrated `Q/I` as a function of model xi:

| xi | earliest Q/I | latest Q/I |
|---:|---:|---:|
| -0.5 | -0.5956459920 | -0.5953295338 |
| 0 | 0 | 0 |
| +0.5 | +0.4263453806 | +0.4261832262 |
| +1 | +0.7465891495 | +0.7463405161 |

For xi=+1 earliest observer θ=90°, `dN_I/dΩ=3.51294390787511e-32 m^-3 sr^-1`, `dN_Q/dΩ=2.62272580439549e-32 m^-3 sr^-1`. θ=0/180°, I equal `8.902181e-33 m^-3 sr^-1`, Q=0, but line centers in Doppler units are +0.536443497627 and -0.538979 (offset sum -2eta_em). θ=90° mean center `-0.0012677447247`. Finite frequency window [-12,12] captures >0.999748 of each angular source photon probability, *numerically verified*; no directed interval. Full natural-Voigt second-moment not finite. Polarization Q/I range is **not** global bound over all quantum density matrices or a measured real telescope signal; it is within precisely this family under fixed-axis condition.

## 검증과 적대적 재검토

Physical source identity/recoil residual max `6.04906556e-16`; Stokes cone per frequency; ∫Ω I=1, χ(P2) bounds; axial U=V=0; q-direction symmetry; poles equal intensity but photon center opposite with recoil; isotropic rho ρ=I3/3; phi16 versus phi32 max diff under 5e-13; all tests performed.

1. Local initial run generated 3,628 rows. Normal 38/38 PASS; optimized 38/38 PASS; eight original data+figure SHA exact.
2. An attempted full scratch `bash REPRODUCE.sh` hit execution time limit **after generating physical output, four figures and normal 38 PASS**. It was `RUNTIME_TIMEOUT` not PASS.
3. A subsequent clean scratch `bash REPRODUCE.sh` finished **EXIT0** with 38 normal +38 optimized PASS and `BYTE_EXACT 8/8`. The earlier timeout remained a separate execution record.
4. Same-author one-pass hostile referee found invalid use of nonraw LaTeX ξ plot string; repaired; verified plots. Other high-risk issues are **claim limitations**: no measured λ/R/I arrays, no electron-axis owner, no full 2p complex density matrix, no single or multiple full RII, natural spectral variance not finite. See `BLIND_REFEREE_EVIDENCE.json`. No actual independent human/agent R06/C09 review.

## DAG and admission

CENTRAL **28/88 +0**, EXTENSION **0/3 +0**, NEW PHYS18 auxiliary **1/1 CONDITIONAL_REVIEW_HOLD**. R/C scoped **18/20**, distinct-author R06/C09 NOT_RUN; native subagent NOT_RUN; `NATIVE25=L4=PRODUCTION=HOLD` and `NO_MERGE=NO_FORCE_PUSH=true`. **Science progress** is source-owner preserved deterministic *conditional* 2p spin-1 polarization and 3,628 new rows, not global physical DAG completion.

## Next constructive source and exact access

Obtain the numerical values and error bars behind Williams 1998 Fig.6+7 via official original PDF `https://www.publish.csiro.au/ph/pdf/p98023` or publisher/author numerical files, with angle axes, DCS units, Stokes λ/R/I normalization and covariance. When digitizing figures, include pixel/axis registration error plus printed uncertainties; do not assert exact table readings from an image. Compare with Bray et al 1991 and Wang et al 1994 at respective actual energies. Construct rho(E,theta_e) from validated parameters using correct collision-frame basis and quantum positivity, then remap every 2,066 source event without silently reweighting NIST total or inventing electron axes. Keep exact physical radiation owner separate from first scattering transport and Bianchi IVP.
