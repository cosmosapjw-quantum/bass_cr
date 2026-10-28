# Exact same-bin high–low capacity (conditional finite marginal)

## Scope and source
Given nonnegative rational weights w_i (units m^-3 s^-2), exact rational energies E_i in eV, a birth-bin label b_i, and conditional cap K >=0, define low L_K={i:2E_i<=K} and high H_K={i:2E_i>K}. A permitted high–low pair (h,l) has E_h+E_l<=K. The *same-bin* capacity S requires b_h=b_l. No physical exclusive kernel, actual K, rate, or actual native numerical capacity is supplied by this theorem. PR117 previously proved the corrected necessary facet 2d-C<=L+S. Here we add an explicit threshold-flow construction and exact dual cut for the special energy-sum graph, not polygon sufficiency.

## Finite weighted-Hall theorem
For each bin b let H_b=sum_{h in H_K,b_h=b} w_h. For every energy threshold t drawn from the high atoms in b, define
U_b(t)=sum_{h:b_h=b,E_h>=t}w_h
and
V_b(t)=sum_{l:b_l=b,2E_l<=K,E_l<=K-t}w_l.
Set delta_b=max(0,max_{t in high energies of bin b}[U_b(t)-V_b(t)]) (max(empty)=0). Then the exact finite fractional matching optimum is

S_b = H_b - delta_b, and S = sum_b S_b.

Proof: Give source->high capacity w_h, admissible high->low edges infinite capacity, low->sink capacity w_l. For any source-side set I of high vertices, the minimum finite cut including I contains all neighboring lows N(I), so the cut is H_b-w(I)+w(N(I)). Its minimum is H_b-max_I[w(I)-w(N(I))]. Since high neighborhoods are nested by energy, any nonempty I with lowest high energy t has N(I)=N({h:E_h>=t}); enlarging I to the entire suffix only increases its weight. Thus the maximum deficiency is attained by one of the thresholds above. Max-flow/min-cut gives S_b.

## Explicit attaining primal
Within each bin sort highs in descending energy and lows in ascending energy. Match each highest-energy remaining high to the lowest-energy feasible available low, using min(remaining high, remaining low) as the exact rational flow. Its pair records give a finite primal. This greedy procedure attains the cut optimum by the standard nested-neighborhood exchange: in any optimal flow, reassign a low unit held by a lower-priority high to a feasible higher-priority high whenever the latter is unmatched; if a higher-priority high uses a higher-energy low than the greedy choice, swapping low allocations preserves feasibility because the lower-priority high accepts at least the same low set. Iterate lexicographically to the greedy flow. The implementation also checks exact primal=dual, pair support, and every atom capacity, so an exchange-proof error would be detected on finite controls.

For n atoms and k bins, sorting and threshold scanning take O(n log n) rational comparisons/additions and the explicit flow has at most O(n) positive edges, apart from bit-complexity growth.

## Necessary event bounds only
Write L=sum_{low}w_i, let M be the unrestricted (cross-bin plus same-bin) high–low matching capacity, D=(L+M)/2 (previously established with low diagonals), d total double-event mass and C cross-bin double-event mass. Let m_s be the same-bin high–low contribution, and m_c the cross-bin high–low contribution of a feasible event measure. Low consumption gives 2d=m_s+m_c+low_consumption <=m_s+m_c+L. Since m_s<=S and m_c<=C,

2d-C <= L+S, hence d<= min(D,(L+S+C)/2).

This is a NECESSARY OUTER BOUND, NOT a sufficient joint (d,C) polygon. S=0 recovers PR116 2d-C<=L. Same-bin pair availability does not determine an actual exclusive kernel, thermalization, time-dependent rate, or attainment.

Full-window selected conditional bookkeeping: W=integral_0^1e10 t dt=5e19 s^2; parent number density W(N-d) and chemical energy W[(24.59 eV)N+(29.83 eV)d]. Retained photon and RR once-only ports remain separate; no thermal energy inference.

## Native K3 input holds
The archived PR116 K3 domain report has 3201 positive atoms, 453 low and 2748 high, same-bin permitted pair (active_0291,active_0453), bin 2, pair energy 11266880367774139/4503599627370496 eV <3. Its source NPZ SHA256 is 1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47, atom digest 2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690. The original NPZ binary was NOT available inside this execution environment; therefore numeric S(K3) is NOT_RUN, NOT zero. The old parent K3 N,L,D and M=2D-L can be reused for future source identity checks. All physical promotion gates remain HOLD.

Literature: weighted Hall/max-flow min-cut is classical and the nested-neighborhood simplification is a direct specialization, not asserted as novel general graph theory. Consult e.g. https://wwwmayr.informatik.tu-muenchen.de/lehre/2011WS/ea/split/sec-Weighted-Bipartite-Matching.pdf .
