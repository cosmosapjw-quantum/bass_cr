# R4P0 문헌 및 provenance

## 문헌

N. Toshima, *Convergence and completeness of the pseudostate expansion for proton-hydrogen collisions in two-center close-coupling calculations*, Physical Review A **59**, 1981 (1999), [저자 논문의 APS 원문 페이지](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.59.1981).

논문의 초록은 symmetric two-center pseudostate expansion의 수렴 및 completeness와 asymmetric expansion의 수렴 문제를 다룬다. 이는 symmetric basis 사다리를 별도의 수렴 축으로 등록할 문헌 근거다. 이 논문이 본 계산의 수치 오차, all-bound completeness 또는 capture를 인증하지는 않는다. 논문의 세부 방법을 이 backend와 동일하다고 가정하지 않는다.

## 고정된 계산 근거

- 완료 A3 commit/tree와 sealed science archive: CONTRACT.json의 byte-backed identity.
- R4O 연구 결과: 연구 commit `ef7468d65aa8a27815fd547694be6665ed5d1a87`의 R4O_EVIDENCE.json을 R4O_PRERECORDED_EVIDENCE.json으로 byte-preserving 회수했다.
- R4A negative-energy finite-span selector: projectile indices `[9,10,12,13,14]`. Positive pseudostates `[11,15,16,17]` 제외. 수치 identity와 입력 파일 SHA/size는 CONTRACT.json에 기록한다.
- 기존 채널 정렬은 center → radial bank(ascending l, bound principal n, positive rank) → ascending m이다. semantic nesting과 실제 coefficient identity는 구별한다. RadialSpec 변경은 새 radial identity를 요구한다.
- source/library/BUILD와 기존 numerical dependency manifest는 FROZEN_DEPENDENCY_PROVENANCE.json에 실제 재계산한 SHA256으로 기록한다. 라이브러리를 로드하거나 rebuild하지 않았다.

## 수식 및 제한

`Q=S J solve(J† S J, J† S)`는 고정된 S-metric에서 선택한 span으로의 Gram observable이다. `v=(S c)[indices]`, `P=real(v† solve(G,v))`로 평가한다. 역행렬은 구성하지 않는다. Q의 Hermiticity, metric idempotence, PSD 및 S−Q PSD를 검사한다.

이 finite-span 값은 NOT_ALL_BOUND, NOT_ASYMPTOTIC_CAPTURE, NOT_PRODUCTION_CAPTURE이다. Temporal gate는 기존 B0, b=2, 100 keV/u, z∈[−12,+12]에만 닫혔다. Finite-window, basis omission, all-bound truncation, b integration은 별도 오차 축이다.

터미널 cross-block norm과 generator 비율은 진단값이다. 유한 지점의 작은 norm만으로 무한 tail의 적분 오차 bound를 만들지 않는다. 미래 full-window 계획은 각 window에서 원래 initial state로 시작하고 독립 temporal qualification을 요구한다. nstep/reference/tolerance/cost/deadline은 미승인이다.

## Higher-l backend blocker

고정 `EXACT_SP_MOMENTS_CXX_V1`은 s/p 전용이다. `tp2a_perf_20260926/fast_cross.py::_validate`는 l>1을 거부하며 `tp2a_analytic_pruning_20260926/code/exact_cross.py::cross`가 이를 호출한다. 그 파일의 SHA는 provenance receipt에 고정한다.

B1–B3는 d/f를 포함하므로 현재 backend로 native admission 불가하다. 이 작업에서는 symbolic registry의 counts/order/symmetry/classification 정책만 준비한다. B0 representative final Gram은 stored bytes로 확인했다. B1–B3 실제 radial eigenvalues/coefficient identity와 representative full two-center Gram은 NOT_MEASURED이며, 더 높은 l을 지원하는 별도 구현/qualification 및 승인이 필요하다. Reference backend로의 자동 fallback은 없다.
