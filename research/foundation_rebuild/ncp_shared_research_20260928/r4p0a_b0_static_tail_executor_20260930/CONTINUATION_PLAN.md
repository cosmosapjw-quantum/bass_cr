# B0 static-tail continuation implementation plan

Spec: user continuation handoff 2026-09-30 (archived in delivery evidence).
Authority: predecessor f7b5eef95895f299327562859ce0b278ffa8679c; verified successor 923f77de3028cd618509cc6553aea2f3d4044bf2 / tree 97656af696e644ae39888b0bc4e918a5e47889e9.
The local Git baseline is a partial source snapshot, NOT an execution identity. Publication uses the remote base tree and parent, preserving every unseen repository path.

Goal: preserve the existing executor and finish bounded pre-authorization hardening.
Architecture: reuse R4F worker/provider/ledger/budget and shared-host supervisor; amend only the static-tail binding directory.
Stack: Python, NumPy 2.3.5, SciPy 1.17.0, pytest.

Constraints: exactly eight independent signed B0 times; global 88 raw attempts; 1--8 workers, four proposed; no new native calls or authorization consumption in this session; no transport, N1536 rerun, b-grid or capture promotion. Delivered rate/plan modules and all native/bank/numerical dependency bytes remain unchanged.

## Tasks
- [x] Add RED regression tests: reject mismatched budget/worker scope before dispatch and native initializer; retain create-only conflicts without new work; directory-fsync new JSON; explicit unavailable-state labels.
- [x] Minimal GREEN binding repairs, with all original focused tests retained. Add passing boundary coverage for genuine consumed-ID fixtures, source/bank/build/plan tampering, signed independence and no ninth query.
- [ ] Instrument focused replay with native-loader and real-nonce tripwires; seal source/input/resource/plan identities mechanically; validate a fresh extracted package.
- [ ] Publish new child branch without merge/force; record R1; create-only dual backup and deliver exact Codex handoff + UNAPPROVED template.

Review focus: concurrent reservation semantics, failure-before-dispatch, durable publication, local rate not probability/error bound, host-bound approval never inherited from another package.
Ruling: successor already implements native binding, so do not reimplement it or discard its four commits. A portable UNAPPROVED template cannot attest live NCP resources; existing prepare_authority.py performs the future local binding without running native science.
