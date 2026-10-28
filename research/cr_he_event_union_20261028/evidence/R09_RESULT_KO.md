# R9 — 재사용 가능한 정리와 계산 계약

단위 CR_PHYS02_HE_EVENT_UNION_V1. 현재 중앙 관찰 22a99cb9b1691274e74c122d54521be4f2f51ba5는 **28/88**, 88 nodes / 17 edges이며 이번 CR의 집계 효과는 0이다. 이 문서는 이론 결과를 구현이 소비할 수 있는 명시적인 계산 계약으로 정리한다.

## 유한 원자 event-union 정리

Ω를 유한 electron-label 집합, μ를 그 위의 nonnegative inclusive marginal이라 하자. S≥0와 symmetric D≥0가 μ=S+2π₁D를 만족한다. U=∪ᵢAᵢ는 서로 겹치지 않는 birth-energy 집합의 합집합이고

    nᵢ=μ(Aᵢ),  N=Σᵢnᵢ,  M=maxᵢnᵢ,
    C=2Σᵢ<ⱼD(Aᵢ×Aⱼ)

로 둔다. D의 총질량은 double 사건 수다. 각 A에 대해

    s_A=S(A),  d_A=D(A×A),  p_A=2D(A×Aᶜ),
    ν_A=s_A+p_A+d_A,  δ_A=p_A+d_A,
    G_A=(-ν_A, s_A, δ_A)

를 정의하면 G_A는 HeI, HeII, HeIII 순서의 source-parent density increment다. 정확히

    G_U = ΣᵢG_Aᵢ + (C,0,-C),
    0 ≤ C ≤ min(N/2,N-M).

고정 atomwise marginal을 보존하는 유한 원자 nonnegative family에서 양 endpoint와 모든 중간값은 달성 가능하다. Selected electron count와 kinetic marginal의 union correction은 0이고 ionic charge correction은 −2C다. 전체 double count는 d_U=Σᵢd_Aᵢ+C이므로 C와 구분한다. 증명과 퇴화 경우는 [THEORY_KO.md](../theory/THEORY_KO.md)에 있다.

## Source·state·단위 계약

| 항목 | 고정값 또는 규칙 |
|---|---|
| Retained revision | 4ca5a90de79c8fb82a25fd9e83615bec0dfa870b |
| 저장 source SHA256 | 8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf |
| Attribution NPZ SHA256 | 1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47 |
| Source support | direct_0p1_10, 3200 active atoms와 별도 0.1eV cutoff ghost |
| Birth partitions | ghost 0.1; active (0.1,1]; active (1,3]; active (3,10]eV |
| Model | Gas-rest scalar, nonrelativistic, zero recoil, frozen 100K, 기존 Coulomb 및 H/He ground spontaneous RR 유지 |
| Isotopes/state | H1/He4, CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1 |
| Inventory | 총 H nuclei 140m⁻³, He nuclei 1085/94m⁻³, xHII=xHeII=1/100, xHeIII=0 |
| Same-state densities | n_e=2849/1880m⁻³, explicit n_b=8750/47m⁻³ |
| Volume | Fixed proper-volume density, absolute proper volume=null |
| Clock/history | Proper qⱼ(t)=tAⱼ, 0≤t≤10¹⁰s; 밖은 unknown |
| Chemical convention | I1*=24.59eV, I2*=54.42eV는 recipient bookkeeping 상수 |

이 inventory는 조건부 선언이다. Source coefficient의 event weight 단위는 m⁻³s⁻²이고, proper window[a,b]의 F=(b²−a²)/2를 곱하면 event density m⁻³가 된다. Source normalization, target, angle, projectile speed와 proper729는 저장 A에 이미 포함되므로 재적용하지 않는다. Proper exposure를 conditional mean time으로 바꾸지 않는다.

## 명명된 consumer

검토 대상 API는 다음이다.

    consume_event_union(claims, source, *, nb_m3, previous_windows=())

source는 pinned NPZ의 atom content와 provenance를 보유한다. claims는 같은 binding·proper window의 서로 다른 selected birth partition들이며, 각 event ID는 동일 내용으로 일치해야 한다. 모든 selected incident partition이 그 event를 claim해야 하고, 전체 event incidence는 각 selected atom의 원 coefficient와 exact하게 같아야 한다. 기존 window와 겹치거나 replay한 반환은 거절한다. Event ID는 개별 electron atom ID와 다른 사건 식별자다.

출력은 조건부 source-ion density increment와 partition 합에 대한 correction이다. He4의 species21 좌표 10,11,12에 대응하며 baryon sum을 보존한다. Explicit n_b=8750/47m⁻³가 제공되면

    native_source_species21 = source_ion_density_delta21 / n_b,
    native_species_correction21 = correction21 / n_b,
    native_ionic_charge_correction = -2C/n_b.

nb_m3=null이면 관련 native fields도 null이다. 다른 nonnull n_b는 EXPLICIT_SAME_STATE_NB_REQUIRED로 거절할 계약이다. 이 API는 조건부 partial increment를 반환하며 actual coupled state를 직접 완결한 것으로 보지 않는다.

## 한 번만 조립하는 규칙

He source-ion 포트를 조립할 때 다음 두 표현 중 하나를 사용한다.

    He_source = G_union

또는 동치인

    He_source = sum(G_partition) + (C,0,-C).

그 뒤 같은 상태·history에 결속된 저장 RR increment를 한 번만 붙인다.

    He_return = He_source + saved_RR.

G_union과 corrected partition sum을 서로 다시 더하지 않는다. 기존 source 반환에 He source-ion 포트가 이미 있으면 이 포트를 교체하거나 그 포트에 correction만 적용한다. 완전한 He source contribution을 중복 추가하지 않는다. H1과 다른 이미 소유된 포트는 해당 계약에 따라 한 번만 유지한다. Retained photons는 별도 포트이며 RR 또는 source-ion correction을 이유로 w_ext/heating에 이동하지 않는다.

Chemical correction은−(I1*+I2*)C이다. 이는 partition 합에 들어 있던 중복 chemical storage를 제거하는 항이다. Selected birth electron ζ 및 kinetic wnt의 partition correction은 0이다. Ionic charge correction을 selected electron correction으로 사용하지 않는다.

## 이번 연구가 제공하는 것과 실제 열린 입력

완결된 결과는 고정 marginal에서 source-parent union을 정확하게 합성하는 규칙, 같은 marginal의 구성적 witnesses와 sharp mathematical interval이다. Inclusive electron source만으로 actual exclusive He distribution을 추정하거나 복원한 결과는 없다. Actual D와 actual C_cross는 null이다. 조건부 witness에서 나온 값에는 witness identity를 붙인다.

Actual outside-partner state·energy·history·response, residual excitation, proton donor debit, EOS/T와 full-source physical native25는 미공급 상태다. Named consumer의 구조적 존재와 partial native species는 이 입력을 대신하지 않는다. Full physical consumer activation은 false다. 실제 입력이 생기면 그 source/state/history/ownership을 새로 결속해 별도 범위에서 판단한다.

## 구현의 검증 목표

Atomwise exact rational marginal, event incidence, source-ion conservation, charge, chemical correction과 sharp witnesses를 검사한다. Selected source digest, complete claims, isotope/state/frame/clock, support, n_b와 nonoverlapping window를 검증한다. Independent report의 비교 허용치는 고정 계약의 1e-12이며 정확한 rational identity에는 exact equality를 사용한다. 기존 2e-11 atom tolerance의 채택은 원 결과 재사용에만 해당한다. 새 bounded runtime의 실제 PASS는 후속 단계 영수증으로 입증한다.
