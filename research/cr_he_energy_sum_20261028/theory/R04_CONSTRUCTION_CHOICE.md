# R4 Constructive choice

Three explicit candidates were compared. (A) Use the four-bin support solver: it loses within-bin energy exclusions and forbidden diagonals, so its feasible class does not compute the requested problem. (B) Materialize all O(n^2) allowed atom edges and solve a generic fractional matching LP: it is a valid small independent oracle, but unnecessarily expands the3201-atom production problem. (C) Split atK/2 and exploit nested low-high neighborhoods, retaining diagonal low residuals: it preserves every atom and admits a linear sweep after sorting. CandidateC is selected; candidateB supplies an independently authored small-graph check.

Concrete distinguishing case: energies1 and2eV, each leg mass1, K=3/2eV. No pair is allowed although an unrestricted diagonal construction would use both atoms. With K=3eV the1+2 cross pair becomes allowed and attains d=1. With K=4eV both diagonal pairs are also allowed, illustrating that maximumd alone does not determineC. These are exact algebraic examples, not source evaluations.

For distinct high levels h1>...>hm, accumulate Bj and eligible low massAj. A descending-high greedy has matched cumulativeQj=min(Qj-1+bj,Aj). Its deficit recursion identifies delta directly. A threshold dual assigns values0,1/2,1 and attains the same objective. This supplies both the algorithm and an independently checkable certificate.

The watchdog identified two useful distinctions: algebraic support versus native inventory acceptance, and full-supportp=0 versus partial-support p. R03 now records both; neither requires additional abstract layers or rerunning old science.
