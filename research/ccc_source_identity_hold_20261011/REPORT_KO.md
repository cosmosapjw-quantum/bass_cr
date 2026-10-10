# CCC source intake closeout

판정은 `SOURCE_IDENTITY_UNRESOLVED`다. Astra source intake의 판정을 기록한 additive closeout이며 새로운 원자물리 채택 또는 transport 실행은 없다. 기준은 PR30 commit `55a97935c5f589e1857e0de595263c94dc52ce53`, tree `77e7e4a64bb19415a401df2bec147d8653ea58dc`다. 기존 감사·manifest·실패·수치 결과를 수정하지 않았다.

공식 CCC Chapter 8은 Temkin–Poet의 `Etotal=eps_n+k_n²/2`와 ENERGY의 ground-state incident eV 의미를 설명한다. 이 설명은 frozen 2026 ZIP exporter의 state/eigenenergy identity를 확정하지 않는다. 공식 index는 계보 근거만 제공한다. 1992 논문 fulltext는 APS 401/Murdoch PDF 403, 1995 fulltext는 APS/harvest 401로 접근하지 못했다. 본문을 읽었다고 주장하지 않는다. 이 접근 결과는 controller가 전달한 Astra intake에서 재사용하며 이번 게시 작업이 새로 접근한 결과가 아니다.

raw marker `HI2P.1S 10.2043500` 및 `HeIs2P.s1S 21.1156000`을 보존한다. marker, 첫 zero, 실제 계산 에너지 및 rounding/offset 관계를 source 없이 동일시하지 않는다. NIST 또는 spectroscopic energy를 CCC state에 대입하거나 incident-energy axis를 이동하는 것은 승인되지 않았다.

최소 다음 조치는 대응하는 frozen HI/HeI ZIP에 결속한 네 가지 upstream 정보를 받는 것이다.

1. state label/eigenenergy/energy zero/unit/eV constant.
2. Hamiltonian convention, nuclear mass, He configuration/basis/shift, experimental substitution 및 energy-specific mapping.
3. first-zero exporter generation, marker와 actual calculation 및 rounding/offset/axis 관계.
4. 위 정보와 exact 2026 ZIP을 연결하는 generation record.

CR-PHYS02C representation은 기존 독립 판정 범위에서 `DONE_SCOPED`다. `physical_atomic_G02`와 spectroscopic replacement는 `HOLD`다. Source intake만 닫았으며 global physical admission은 `HOLD`를 유지한다. 코드 변경, solver 실행, 새로운 science validation 및 merge는 0회다. 네 입력이 확보되면 Astra가 source-specific contract를 결정하고 하위 tier가 그 계약에 따라 후속 작업한다.
