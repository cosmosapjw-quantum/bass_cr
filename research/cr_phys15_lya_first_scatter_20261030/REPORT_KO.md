# BASS-CR PHYS15 과학 결과 및 판정 (2026-10-30)

불변 부모 PR139 HEAD `ae9aacd7ce93c28008d4e23c587cb2878e9adb45` SOURCE SHA256 `55c5b97d8bb59fa2f56fb0e07deef9bf43a328feb820cb8ea0bf6fabf2f8aefa`. 새로운 scope: **source-owned 2p excitation -> spontaneous Lyα -> first resonant HI scattering**, frozen same proper clock. 원 모델의 6400 원본 광자, 4 birth bins, 100 K, 138.6 m^-3.

- 전체 생성 원본 기반 numerical rows: **19,869**. 구성 {'by_source': 54, 'final_per_atom': 12800, 'frequency': 567, 'line': 21, 'micro': 6400, 'time': 27}.
- 원본 PHYS14 2p 첫여기 Pexc(T=1e10s, earliest) = **3.3158906934521573e-31 m^-3**, 부모 parity max 1.87e-16.
- Early Lyα 방출 에너지 장부 = **5.4182579246352516e-49 J m^-3** (2p excitation reservoir, not trapped/escaped intensity).
- 자연 수명 **1.5961946719021851e-09 s**; t=T까지 미방출 2p 상한 2.2074e-49 m^-3.
- 선중심 σ = 5.869766664794594e-17 m², λ=0.003983505 pc, t_first≈410010.737s. (All computed from NIST f and A and 100K Doppler+Voigt.)
- Earliest first scattering at T=1e10s: x=0 3.3153328914571752e-31, x=10 3.8395187106680519e-32, x=100 4.199071205158911e-34 [m^-3]. Entire x atlas is **conditioned**, not integrated over native unknown emission frequency PDF.
- Same-author blind referee: independent SciPy QUADPACK scalar first-scatter and Voigt normalization; one materially diagnosed boundary-layer quadrature defect in initial GL64 was **repaired** using Laplace endpoint Laguerre quadrature for q*T>200 and GL160 otherwise. Historical initial failed numerical expression retained as failure evidence; final corrected science uses new result files only.
- Parent original atomic support and all 27 parent time values remain exact to 1e-12; no native different-author R06/C09, no repo/main/parent mutations; no CI claim.

**Physical claim gate:** central DAG 28/88 (+0); extension 0/3; auxiliary 1/1 conditional review hold. physical_K, multi-scattering redistribution, emission recoil PDF, evolving n_e/T/gamma/background and global He exclusive event kernel remain unbound; native25/L4/production HOLD.
