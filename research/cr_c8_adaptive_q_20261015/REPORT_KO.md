# R5 + C5/C7/C8: Shape-free moment envelope에 의한 q-energy 적응형 세분화

**관측 날짜:** 2026-10-15 KST. **선택 노드:** `CR_ADAPTIVE_Q_GRID_FROM_ENVELOPE_WIDTH`, 부모 `bass_cr` PR70 실제 head `6898f3dd0ab5acff066fb0239339ec44c8d70398`. 다른 개발 repo 원본 파일은 수정하지 않는다. 이번 새 코드는 독립 소스/실험 범위에 속하며 전체 `rei_bianchi` ion/electron/Tgas 역사나 Landau 전파자 문제와 혼동하지 않는다.

## 정확한 수학적 가정과 결과

한 q-cell `I=[a,b]`의 양의 photon 측도를 `mu`라 두고, 정확히 알려진 `N=∫dmu>0, U=∫Eref dmu`로부터 종별 H I, He I, He II 광이온화/광가열의 frozen-neutral one-step response `g_k(R Eref)`를 평가한다. 원 PR70 정리:

`N conv_I(g_k(R·))(U/N) <= ∫ g_k(R E)dmu <= N conc_I(g_k(R·))(U/N)`.

여기서 convex/concave envelopes는 실제 Verner photo-fit cutoff에서 좌우 값을 구별한다. 원 코드의 85자리 directed smooth-segment curvature bound와 mp.iv55·Fraction outer hull을 재사용한다.

**새 refinement의 필수 전제:** 부모 bin을 자식 `I_j`로 자를 때 실제 현재 positive measure의 `N_j,U_j`가 별도로 주어져야 한다. 이 값으로 정의한 admissible 측도의 집합은 부모 admissible 측도의 부분집합이므로, 수학적 정확 실수 범위에서 `Lparent <= Σ Lchild <= true <= Σ Uchild <= Uparent`이다. 구현은 두 수치 outer bounds의 **Fraction 정확 교집합**을 누적해 전 과정에서 monotonic enclosure와 positivity를 유지한다. source에서 자식 데이터를 알 수 없는 경우 부모 `(N,U)`만으로 분해를 발명하지 않는다.

`PositivePacketOracle`은 source-conditioned GL packet과 hardening 받은 둘 이상의 photon cohort라는 **추가 정보**를 실제 양의 packet 원본으로 받아, IEEE 저장 입력의 `Fraction` exact prefix `(count, energy)`를 구축한다. 자식 query는 `bisect_left` 2회와 prefix 차로 O(log P)이며 source packet 의미의 양성·모멘트 보존을 정확하게 검사한다. HEI priority는 `max_j(width_j/budget_j)`의 단순 충분 heuristic; 반복 선형 후보 스캔 대신 우선순위 heap을 사용하고 변경된 두 자식만 재평가한다. 현재 width-budget를 만족하지 못하면 `HOLD_PRECISION_TARGET`를 출력한다. 타겟 1e-10 count/H HeI는 이 제조 한 단계에 대해서만 의미를 가진다.

**이해해야 할 반례:** mass1, mean25eV의 두 packet 측도 `delta_25`와 `(delta_24.5+delta_25.5)/2`는 동일 부모 `(N,U)`이지만 HeI 문턱24.59eV의 아래쪽 자식 질량은 서로 다르다. 따라서 부모 moment만으로 사후 adaptive refinement가 실제 오차를 줄였다고 주장하는 것은 부당하다. 내장 test가 이 정확 dyadic 반례를 보호한다.

## 재현된 scientific input

- 최초 조건: BB 50,000K 원 MD14 z20 source native48 32-Simpson 분율, q-energy 13.6..433eV, 소스 통합 emission `4.298036114764196e-8` photon/original H, current physical ratio R=1, gas nHI=`0.0017575700008892194` cm^-3, nHeI=`0.0001429214010766023` cm^-3, nHeII=0, proper `dt=1e10s`.
- 별도 제조 hardened 2-age: old birth R=.98, new birth R=1, old packet preabsorption gas `(0.001,.00012,.00001)`, pre-dt2e9s, current R=.97, neutral `(.0008,.00009,.000005)`, current dt4e9s, each birth half source photons. This is **not owner SOURCE07 C7 z20/z4 actual two-epoch physical dataset**.
- Positive GL8 source packet measures are fixed once before refining. Both uniform and adaptive cases operate on EXACT same saved positive binary64 packet universe. Any more accurate full continuous source result is a separate layer from these *source-sample conditioned* exact dyadic comparisons.

### Measured HeI one-step shape-free interval widths

| physical packet corpus | bins | adaptive HeI width [count/H] | same-cell-count uniform HeI width | ratio uniform/adaptive |
|---|---:|---:|---:|---:|
| original z20 source | 96 | 1.67211982329e-10 | 1.17761487050e-9 | 7.04 |
| original z20 source | 128 | 5.48788129474e-11 | 6.73281121939e-10 | 12.27 |
| two-age attenuated manufactured | 96 | 3.50586027731e-11 | 7.32052270802e-11 | 2.09 |
| two-age attenuated manufactured | 128 | 3.26510158401e-11 | 4.10841976753e-11 | 1.26 |

At initial source adaptive N128 the HeI relative halfwidth is ~1.92% of true packet one-step event, compared to uniform128 ~23.57%. At the hardened two-age N96 it is ~4.28% vs uniform96 ~8.94%. This comparison assumes the additional **true child moments from the packet oracle**. It is NOT an error certificate for a real SOURCE07 stock whose only evolved state is original N,U. Other HI/heat components have separate widths and goals in machine-readable results; HeI-focused selection does not necessarily optimize all six components.

`HEI_FOCUS` scales `(.1,1e-10,.1,.1,.1,.1)` are explicitly chosen to drive the already-observed HeI issue. At original source N96 the selected HeI width target is not met -> **HOLD**. At N128 `5.49e-11 <1e-10` and the requested local target passes. The six-scale selection is a priority not a replacement of any canonical AXBI gate.

## Numerical algorithms, performance and reproducibility

1. True packet dyadic Fraction prefix reduces `N,U` query from O(P) scan to O(log P) without changes in exact values. Benchmark original binary64 5496 packet two-age stock, 150 interval requests, three repeats: native Python full scan median0.6833s vs prefix0.001725s (**396.1x** for packet-query kernel, not overall transport speed).
2. Adaptive heap refines only selected source-support intervals; `make_template` calculations are expensive and dominate. N128 original-source result took about3s starting N64; uniform128 roughly1.2s for whole shape-free bound, but the adaptive HeI width was12.27x narrower at matched state count. No identical-error speedup claim.
3. Four independent manufactured ray/source-gas tasks with `cached_template.cache_clear()` per job prevent **fork inherited warm cache** from inflating parallel benchmark: cold 1 worker8.229s, 2workers3.863s, 4workers2.182s, bit-identical returned values in all worker choices. This is process scheduling, NOT native subagent delegation, and does not imply Rust solver parallel efficiency.
4. Tests cover exact mass/energy identity, atom-threshold split, deliberate parent moment ambiguity, invalid corpus & source/clock, actual initial/hardened packet response inclusion for all HI/HeI/HeII and direct heats, nonincreasing global bounds, source and hardening monotone, and precision PASS/HOLD. Full 47 regressions include prior PR70 source envelope tests unchanged.

## Actual other-repo current result

As of 2026-10-15 ~12:56 KST authorized `rei_bianchi` HEAD `a950711f9cf57eea065d2ce30b15aba54b60bf53`: SOURCE07 C7 has a genuine z20/z4 two-emission Bianchi test, where pooled q N/U HI error -0.441% at nE256 despite retaining age-union support, and two **true** age lanes remove nearly all of it. C8 A/B now require actual bounded memory over continuous emission and opacity error budgets. Its signed AX08 remains IN_PROGRESS; AX11/12 PENDING. Existing source and source-order Jacobian are owned by this repo, not by the local adaptive supplier. The present mixed-age manufacture is a distinct, deliberately labelled test, NOT replacement of owner C7 history.

`BASS_HE` PR62 uses warm P01/HM12/FT03 6-cell bounds and does not contribute gas/opacity constants; `WU088_HH` PR77 cusp-shell electron scattering bound has no physical Verner source compatibility. No foreign numerical error estimate imported into this model.

## Scientific status and next C stage

- **Adopt for separate source/packet-refinement experiments:** true-child-moment adaptive q-bin `CR_ADAPTIVE_Q_GRID_FROM_ENVELOPE_WIDTH` pilot, conditional shape-free bounds, performance and negative controls completed.
- **Do not admit direct owner q-history from parent N/U:** no true child moment mechanism in current C7/C8 canonical grid; creating a finer grid by subdividing those two stored numbers without extra subcell information is not rigorous.
- **Owner C8 consumption:** source injection can obtain child moments from the real source quadrature; hardened current stock needs new finite age/subband state or verified packet oracle. Compare at same R*J, proper source/IC and per-ray direction, no cross-age/direction scalar mixing.
- **Separate later tasks:** apply true owner SOURCE07 C8 source/age state to the adaptive selector, true nonlinear gas/temperature trajectory, full EoR history, the separate bass_cr Landau kinetic fine constitutive adjoint. Original CR/RCT/HH OFF and original20 kBT/FR source scenarios preserved.

## Primary background

- G. Winkler, *Extreme Points of Moment Sets* (Math. Oper. Res. 1988), DOI 10.1287/moor.13.4.581: moment-constrained extrema and finitely supported measures; supports the parent PR70 two-atom convex envelope method.
- Mirocha et al. (2012), arXiv:1204.1944: reaction-weighted photoionization/heating source discretization as independent fidelity target.
- Baumschlager, Shen & Wadsley, (2024), arXiv:2310.16902: positive within-band spectral reconstruction and ionization-edge jump representations.

**No claim of new mathematical novelty for generalized moment extrema, global time evolution, or full astrophysical product.**
