# BASS_CR PHYS16 | 다음 연구 스레드 인계 (2026-10-31)

```
PROJECT=cosmosapjw-quantum/bass_cr
PARENT_PR=140
PARENT_HEAD=db650261fca9be5be62505233eadad0d74e6d20d
UNIT=CR_PHYS16_CONDITIONAL_EMITTER_ANGULAR_SPECTRUM_AND_ONE_SCATTER_RII_LIKE
PARENT_SOURCE_BYTES=9325625
PARENT_SOURCE_SHA256=48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316
ORIGINAL_SOURCE_PHOTONS=6400
FIRST_H_2P_EXCITATION_VALID_ATOMS=2066_HE_ORIGIN
SOURCE_QUALIFIED_NEW_CSV_ROWS=5207
EMISSION_MODELS=BORN_DIPOLE,ISOTROPIC_IMPACT_DIPOLE,BORN_ISOTROPIC_EMISSION
EMISSION_PDF=MODEL_CONDITIONAL_NOT_EXPERIMENTAL_DCS
FIRST_SCATTER_SPECTRAL_INTEGRAL=SCOPED_100K_STATIC_HI
ONE_SCATTER_REDIS=RII_LIKE_STATIC_ABSORPTION_SELECTED
MULTI_SCATTER=NOT_RUN
PHYSICAL_K=UNBOUND
GLOBAL_HE_EXCLUSIVE=UNBOUND
COMMON_EVOLVING_GAS_RADIATION_CLOCK_GEOMETRY=UNBOUND
CENTRAL_DAG=28/88_DELTA0
EXTENSION_DAG=0/3_DELTA0
PHYS15_AUXILIARY=1/1_CONDITIONAL_REVIEW_HOLD
PHYS16_AUXILIARY=1/1_CONDITIONAL_REVIEW_HOLD
R06_DISTINCT_AUTHOR=NOT_RUN
C09_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
NATIVE25=HOLD
L4=HOLD
PRODUCTION=HOLD
AUTO_NEXT_NODE=false
NO_MERGE=true
NO_FORCE_PUSH=true
```

**이번 완료 범위**: 2,066개 실제 원본 사건을 보존한 3개의 조건부 recoil emission PDF, 100 K HI first-scatter spectrum, absorption-selected 단일 Rayleigh+recoil 재분배 커널의 3개 입사 주파수 atlas. 원본 PHYS15+PHYS14 완전 SOURCE ZIP은 PHYS16 archive 속 `sources/PR140_PHYS15_SOURCE.zip`으로 포함. ZIP만 복원해 `bash REPRODUCE.sh` 실행.

**NEXT_CANDIDATE_ONLY**: Kingston, Fon & Burke (1976) DOI `10.1088/0022-3700/9/4/010` 1s→2p 13–300 eV low-energy DCS의 원표를 확보하고, Williams (1976) DOI `10.1088/0022-3700/9/9/017` 13.87/16.46/19.58 eV 저에너지 측정과 비교. 물리적으로 실제 측정/CCC 다중 상태별 DCS + upper 2p density matrix를 결합할 때까지 source-owned *unique* PDF는 UNBOUND. 이후 Hummer1962+Rybicki2006 recoil/detailed-balance RII exact 및 photon transport/multi scatter를 새 연구 단위로 진행. N5/C21 REI 외부 공통 clock geometry K 통합은 별도 owner 동일성을 증명한 뒤.

**Blind referee 핵심**: PWBA 근접 threshold 미검증, 2p alignment closure 임의성, 단일 산란 근사의 detailed-balance 차이, source-specific external geometry 미결합, tail bound excludes interior quadrature. 현재 모델 결론만 조건부 인정. 외부 R06/C09는 실행하지 않았고 직접 재실행 test와 구분.

**Reproduce**: `bash REPRODUCE.sh`; `python verify_archive.py <zip>`; full python deps numpy/scipy/matplotlib.
