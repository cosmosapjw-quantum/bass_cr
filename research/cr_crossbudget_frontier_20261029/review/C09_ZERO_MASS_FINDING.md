# Independent review: zero-capacity dual extension

Separate agent frontier_code_review confirmed closure of the initial six findings using changed source and C06 logs. It found that zero-mass vertices were omitted from primal LP yet returned price0, while the theorem's dual applies to every original energy-eligible HL edge. Example: low(E0,w0,bin0), high(E3,w1,bin0), K4,c0. Returned price sum0<1; scalar M=d=0 remains correct. The reduced-support certificate did not satisfy the full-graph stated contract.

Actual targeted C07_ZERO_DUAL_RED reproduced this assertion failure. The repair extends zero-mass prices to1, adding zero objective cost, and checks every original energy-eligible HL edge. A valid extension and explicit rejection of the old zero-price certificate are now tested. Primary theorem and positive-mass optimizer are unchanged. Earlier PASS results remain bound to their original source hashes; fresh GREEN evidence follows.
