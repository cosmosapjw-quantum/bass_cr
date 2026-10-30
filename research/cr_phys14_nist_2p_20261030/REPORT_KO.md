# PHYS14 | 원본 RR 광자에 대한 H 충돌 여기–이온화 경쟁 물리 보고서

## 새 연구 결과

원본 PHYS13 full source ZIP SHA-256 `fdae18068eb51ae7bdd0785efa371229aa15d33b6f040e0640e0bd65cc66d3a7`을 완전 복원하여 H/He 100K 중성 재결합 광자 6400개의 실제 E_gamma, w, birth proper clock, Verner first-photoabsorption hazards를 유지했다. NIST 원자 H(1s)->2p BE-scaled theoretical cross-section 12개 수치점(11..21 eV)과 Shah1987 원본 measured H ionization 26점(14.6..21.4 eV)을 단일 전자 첫 비탄성 사건 경쟁 모형으로 연결했다.

전체 source-qualified 신규 물리표: **6,595행**: {'by_source': 54, 'ccc_comparison': 4, 'energy_spectrum': 92, 'micro': 6400, 'nist_reference': 12, 'support_census': 6, 'time_total': 27}. 최초 H photoionization 다음에 H 추가 이온화 또는 1s->2p 여기가 우선하는 사건을 같은 source photon/proper clock에 연결했다.

## 최종 T=1e10s, earliest history

- 두 단면적 공통 영역 H second ionization only: `1.23437461610498315e-31 m^-3`.
- 2p competing with H second ionization: `1.23046609854223164e-31 m^-3`; suppression `0.3166394960%`.
- 2p competing with H second ionization: `3.31589069345215690e-31 m^-3`; 2p/ion ratio `2.6948249102`.
- First 2p excitation energy reservoir on same Shah measured support: `5.41825792463525084e-49 J m^-3`; H ionization binding `2.68113668353836649e-49 J m^-3`.
- NIST-only 2p over all published covered first-electron domain, no other processes: `8.17150076111856189e-31 m^-3` **model upper exposure**, not actual rate.
- NIST-only 2p where electron H ionization energetically impossible: `3.82510959004156063e-31 m^-3` (2s, n3 and elastic remain open).
- NIST-only 2p where H ionization is allowed but Shah data missing 13.6..14.6eV: `1.02659791975006435e-31 m^-3` **unknown H-competitor, not measured prediction**.

Source support census: `{'excitation_only_below_ion_threshold': 811, 'ionization_gap_unmeasured': 323, 'measured_overlap': 2066, 'outside_H_source': 0, 'uncovered_below11': 3200}`; 192 original energy atoms permit two 2p excitation energy payments, but the current NIST 11eV lower edge does not supply its second-event microscopic rate. A 2p excitation energy may become Lyman-alpha after decay, but neither radiative escape nor feedback is modeled. All outputs are static-conditional physical source quantities, not observations or completed closure.

## Verification and claim gate

26/26 normal + 26/26 optimized unit tests, independent SciPy QUADPACK first-inelastic integral comparison, Wolfram symbolic identities and 27/27 PHYS13 source-reused photon/ion-only parity. R06/C09 different-author and native subagent: NOT_RUN. Central DAG 28/88 delta0; extension 0/3 delta0; PHYS14 auxiliary 1/1 scoped REVIEW_HOLD. NATIVE25, L4, production HOLD, no merge/force-push.

This is actual common photon source + electron microscopic competition construction, not proof of common *evolving* gas/radiation/clock/geometry or physical K. Avoid conflating stage-note uploads with 20 independent scientific experiments.
