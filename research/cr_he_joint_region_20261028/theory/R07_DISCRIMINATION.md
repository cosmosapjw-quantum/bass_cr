# R7 — Actual exact symbolic discrimination

The Wolfram evaluator executed runs/r07_wolfram/REQUEST.wl with requested timeConstraint=5 seconds. The actual request and returned output are preserved in RECEIPT.json. No floating tolerance was used. Provider CPU and kernel version are not exposed and remain null; elapsed connector time is not represented as CPU time.

For the three-atom K=3 example, the five allowed double variables are aa,bb,ab,ah,bh. Singles are eliminated as nonnegative marginal slack. Exact Maximize returned, for objectives d, C, 2d-C, C-d, -d and -C respectively:

    {5/2, 2, 4, 0, 0, 0}.

All match the independently derived facets. Direct substitution accepted all five declared event vectors and returned coordinates {(0,0),(2,0),(5/2,1),(5/2,2),(2,2)}. The feasible vertices and exact outer inequalities establish equality for this fixture. The equal-bin outside-domain example returned False for 2*1-0<=1, preserving the explicit scope counterexample.

This is one actual remote exact-algebra run on a discriminating synthetic fixture. It is not a native source computation or a substitute for the general R5 proof. The mathematical theorem passed R6 independently of this solver. Native source support, a new K6 primal and the original source consumer are coding obligations. The new local scientific budget remains unused at this point; remote CAS CPU is separately unknown and is not silently charged as zero.
