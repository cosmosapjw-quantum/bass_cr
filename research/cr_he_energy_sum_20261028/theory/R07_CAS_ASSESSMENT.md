# R7 Actual constrained Wolfram corroboration

One Wolfram Language evaluator call actually completed with `timeConstraint=8`. The submitted code and full unedited tool response are adjacent files. The tool returned `isError=false` and a single association, with no warning/message block. Remote CPU is unmeasured/null; the requested evaluation constraint is not a claim about total transport wall time or an independently measured CPU charge. This batch does not replay a source fit or evaluate a physical source model.

Four symbolic residuals are exactly zero: full-support species sum, full-support ionic charge minus electron legs, full-support chemical mapping and partial-support chemical mapping. The proper-time integral is `(b^2-a^2)/2`. The native chemical binding difference is `2983/100 eV`. The cutoff gap is exactly `1/90071992547409920 eV`, equal to `1/(5*2^54)`.

The five independent small linear programs returned `{0,1,3,0,1}`. They cover energies `{1,2}` with K=3/2 and K=3, the imbalanced `{0,1,3}` masses `{1,2,4}` with K=4, and one exact stored-cutoff atom of mass2 with K=1/5 versus K=2Eghost. Their LP variables are the explicitly enumerated unordered pairs and loops, with incidence2 for a loop. The LP code does not use the proposed tail formula or greedy implementation.

Thus 4 symbolic zero identities, 3 other exact identities and 5 LP objectives corroborate the adopted proof. These12 relations are scoped algebraic corroboration. They do not replace R5's proof, the independent R6 review, or the actual C-stage execution. No actual physical K/kernel or completion is inferred. The one initial CAS batch is consumed; no further CAS allowance is selected.
