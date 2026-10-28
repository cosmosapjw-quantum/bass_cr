# C6 — Actual exact implementation verification

controls_v1 passed117/117 checks under the bounded runner. The independent oracle enumerated479 candidate exact bases across12 fixtures, including empty/all-zero support, one low/high atom, M=0, X=M=X=D, exact edge equality and just-below equality, a nondegenerate pentagon, rational capacities and a zero-mass forbidden-bin endpoint. Its complete projected hull matched the constructed polygon in every case. Each selected boundary/interior target was constructed and verified atomwise.

The four-atom forced-exchange fixture entered assemble with a cross optimum having HL0 while the certified maximum HL is1. It executed one residual augmentation and returned F with d3,C2,HL1. Thus the generic exchange path was actually used; testing only the native equality shortcuts would not have established that implementation path.

The C++ path preserved an exact cross value2^64 and directed flow2^65. Python refused unsupported2^126 capacities before launching the backend; a direct malformed-range request to the C++ parser returned its expected overflow error. A deliberately plausible all-zero flow from a fake successful backend was rejected by residual mincut verification, and the original Python method was restored after that error. These are expected control rejections, not failed scientific jobs.

The actual job exited0, measured0.202852CPU-s and charged0.302852CPU-s. Source, input and all reused dependency hashes were unchanged. Current total charge is1.838983/40CPU-s. RESULT.json, CHECKS.json, CASES.json, actual command, source snapshots and resource receipt are in runs/controls_v1. No native source calculation ran in this stage.

This closes the implementation-obligation checks for the selected exact finite model. The full native3201-atom witnesses and original source-return correspondence are the remaining C7 scientific obligations. The single prior build-controller failure remains recorded and resolved; no new failed attempt occurred in C6.
