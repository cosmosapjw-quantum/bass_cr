# R5 Exact atomwise pair-energy support theorem

## Statement

For the finite nonnegative atom data and closed support E_i+E_j<=K defined in R03, let

delta=max(0,max_{h in high levels}[B(h)-A(h)]).

Then the exact feasible interval of internal double mass is

0<=d<=dmax=(N-delta)/2=(Lmass+Hmass-delta)/2.

A maximum witness has at most n_positive event records, counting residual singles and low diagonals. A witness at any targetd has at most2n_positive records. Sorting costsO(nlogn) comparisons and the matching sweepO(n) arithmetic operations; exact-rational bit costs are not claimed constant.

## Lemma1: the support split

Every pair of low atoms is allowed because each energy is at mostK/2. No pair of high atoms is allowed because each is strictly greater thanK/2. A high atom at energyh can pair only with low energies<=K-h. Descending high levels therefore have nested, expanding low neighborhoods. The equality convention includes low atoms atK/2 and permitted diagonal2E=K.

## Lemma2: the high-tail upper bound

Take all high atoms of energy>=h. Their total mass isB(h), and their partner capacity is no greater thanA(h). Thus at leastB(h)-A(h) legs from this high tail remain unpaired when positive. At leastdelta of allN legs remain unpaired. Any double uses exactlytwo legs, including a diagonal double, so2d<=N-delta. This holds without assuming a particular allocation among allowed pairs.

## Lemma3: exact greedy attainment

Let b_j be the total mass at descending distinct high levelh_j, B_j=sum_{k<=j}b_k, andA_j=A(h_j). Process high levels in that order. Match each high residual to the lowest-energy available low atom whenever its energy is<=K-h_j. Earlier consumed low mass is all within the current eligible prefix. The maximum newly assignable mass is therefore min(b_j,A_j-Q_{j-1}), and

Q_j=min(Q_{j-1}+b_j,A_j), Q_0=0.

Subtracting from B_j gives

B_j-Q_j=max(B_{j-1}-Q_{j-1},B_j-A_j).

Induction yields B_j-Q_j=max(0,max_{k<=j}(B_k-A_k)). Hence final low-high mass is m=Hmass-delta. All residual low mass Lmass-m admits same-atom diagonal doubles of half its leg mass. Residual high massdelta becomes singles. The total double mass is m+(Lmass-m)/2=(N-delta)/2, reaching Lemma2's bound. Every original atom marginal is preserved, not merely each birth-bin total.

Zero-weight atoms are skipped. The empty high set gives delta=m=0 and low diagonals; the empty low set gives delta=Hmass=N and all singles. E=K=0 belongs to the general low domain. These general examples need not be accepted by the native PHYS02 support adapter.

## Lemma4: explicit dual certificate

For every allowed unordered pair require y_i+y_j>=1, including2y_i>=1 for a permitted diagonal, and require y_i>=0. Ifdelta=0 take y_i=1/2. Otherwise choose a complete high-energy tailh_* attainingdelta. Set y=0 on high energies>=h_*, y=1/2 on other high atoms, y=1 on low energies<=K-h_*, and y=1/2 on the other low atoms.

A zero-weighted high dual vertex has allowed partners only in the y=1 low prefix. Every other allowed low-high pair has both dual weights>=1/2. All low-low pairs and permitted loops have total dual weight>=1. Thus the dual is feasible. Its weighted objective is

sum_i w_i y_i = A(h_*) + (Lmass-A(h_*))/2 + (Hmass-B(h_*))/2 = (N-delta)/2.

For any feasible primal, d=sum_pairs x_pair<=sum_i y_i used_i<=sum_i y_i w_i. The sparse primal of Lemma3 and this dual have identical exact objective. Acceptance can therefore check the primal/dual identities without trusting a solver success flag.

## Lemma5: every intermediate value and sparse size

Ifdmax>0, scale every double in a maximum witness bylambda=d/dmax. At each atom, assign a single of weight w_i-lambda*(maximum double incidence at i). These residual weights are nonnegative, and the full marginal is unchanged. Ifdmax=0 onlyd=0 is admissible and the witness is all singles without division. Every positive low-high assignment exhausts at least one residual atom, so the count of these assignments plus final residual atom records is at mostn_positive. The scaled double set and atomwise singles together have at most2n_positive records.

## Consequences and physical mapping

EnlargingK only adds allowed pairs, so dmax(K) is nondecreasing. A finite support changes only at pair sums E_i+E_j, including diagonals2E_i; because equality is included, dmax(K) is right-continuous. No continuous physical correlation law is inferred.

On a full selected-support witness p=0 and s=N-2d. The source He4I/II/III increments at coefficient level are(-N+d,N-2d,d); parentsnu=N-d. Nuclear count is preserved and ionic charge isN, equal to the selected electron count. Chemical reference storage is I1*N+(I2-I1)*d, with I1=24.59eV,I2=54.42eV. These witness formulas are distinct from the previous partition-union correction(C,0,-C), whose chemical correction is-(I1+I2)C. In a partial selection p can be nonzero and storage instead reads I1*N+I2*p+(I2-I1)*d.

Multiply coefficient measures byW exactlyonce through the unchanged consumer. The native species divide by the explicit same-state nb8750/47. Native acceptance also intersects the algebraic interval with d>=max(0,N-Hneutral/W); if that lower endpoint exceedsdmax the finite inventory consumer rejects this window. Existing time/state/provenance/support/nb/replay guards remain.

The theorem is a concrete specialization of finite weighted matching/coupling, with its own direct proof. It supplies no actualK/exclusivekernel, donor work, outside response, EOS/T or full physical native25. No new global strong-no-go or general matching novelty is admitted.
