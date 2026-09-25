# FND R2 repository integration plan

Goal: CP3 기반 구성품을 보존하고 FND_R2_TWO_CENTER_OPERATOR_PARITY_AND_BOUND_SPECTRUM의 한정된 구현을 제공한다. Local Codex는 validator이며 추가 구현/설계가 아니다.

Architecture: frozen cr_repro와 별개인 research/foundation_rebuild. AtomicRadialBank, complex solid-harmonic angular functions(l<=3), two-center prolate quadrature, weak kinetic/Coulomb S,H,D, fixed test runner.

Spec: REBUILD_ARCHITECTURE_KO.md. 사용자 2026-09-25 구현 및 GitHub 게시 승인.

Tasks
1. CP3 code/test byte identity를 보존하고 42 baseline tests를 다시 실행한다.
2. tests/test_r2.py에 정지 1s overlap, direct D skew defect, ETF, weak kinetic, radial spectrum/positive pseudostates, general basis mapping, preflight rejection 시험을 먼저 둔다. RED 후 radial_basis.py와 two_center.py를 구현한다.
3. 같은 테스트 집합을 고정 contract로 실행하는 run_validation.py를 구현한다. 새 output, 단계별 receipt, subprocess timeout, dependency/identity/source guard, first failure 보존. Local profile는 legacy suite도 별도 subprocess로 실행한다.
4. code/docs/provenance 및 실행증거를 Git tree로 게시하고 새 branch를 생성한다. 기존 main/연구 branch와 numerical source 변경 없음.

Constraints: internal atomic units, no potential softening, no hidden channel dropping, no symmetrization to hide defects, no production admission, no collision/b-grid or GPU automatic launch. Finite quadrature/finite basis observations are not continuum certificates.

Review focus: l,m invalid; rank loss; nonfinite geometry; missing dependencies; output overwrite; timeout/interruption preservation; basis identity mismatch. Each is tested.

Ruling: direct clone DNS fails; use connector Git tree base and record local full legacy suite as not run. New package standalone tests run here; local validator also runs existing repo tests without source editing.
