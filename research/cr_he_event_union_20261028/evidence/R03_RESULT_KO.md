# R3 — 정의와 주장 종류의 정렬

단위 CR_PHYS02_HE_EVENT_UNION_V1. 중앙은 현재 고정 관찰22a99cb9b1691274e74c122d54521be4f2f51ba5에서 **28/88**, 88 nodes/17 edges이며 이 단계의 중앙 집계 효과는 0이다. 저장 source의 실제 bytes, 수학적 직접 증명, 조건부 모델과 외부 실측을 구분한다.

## Claim table

| 주장 | 근거 종류 | 채택 범위와 남은 입력 |
|---|---|---|
| Retained PHYS02 source와 NPZ의 실제 입력 identity | 실제 original archive 복구·입력 bytes·SHA/CRC 기록 | 기존 저장된 모델 입력의 identity다. 외부 관측으로 승격하지 않는다. |
| Rudd source의 one-electron inclusive convention | 이전 primary text 읽기와 PR111의 채택 근거 재사용 | Electron marginal이며 exclusive parent event 또는 two-electron joint FDCS가 아니다. |
| Double-ionization 문헌에 electron-pair correlation이 등장함 | 이전 실제 APS/기관 manuscript 읽기 | Projectile energy·support·acceptance·normalization이 현재 source와 같다는 주장은 없다. |
| μ=S+2π₁D | 명시적 사건 측도 정의 | S는 single 사건, D는 symmetric double 사건 측도이며 D의 총질량이 double 사건 수다. |
| Disjoint birth partition의 parent union correction | 직접 유도 | C=2Σᵢ<ⱼD(Aᵢ×Aⱼ)일 때 species correction=(+C,0,−C). |
| 0≤C≤min(N/2,N−maxᵢnᵢ) | 유한 원자 측도에서 직접 증명 | Nonnegative S,D와 고정 atomwise marginal의 mathematical envelope다. Physical cross-section error radius가 아니다. |
| 상한·하한과 모든 중간값을 달성 가능 | 직접 구성 | All-single, diagonal-double, half-shift 및 convex mixing witness. 실제 산란 joint kernel을 측정한 결과가 아니다. |
| qⱼ(t)=tAⱼ, proper [0,10¹⁰]s | 기존 실제 source 계약 재사용 | 구간 밖 history는 unknown. Conditional mean이나 photon moments로 exposure/history를 만들지 않는다. |
| 100K, H1/He4, n_b=8750/47m⁻³ | 명시적인 같은 상태의 조건부 선언 | 외부 관측값이나 REI/BASS의 실제 bath가 아니다. |
| ΔY=(C/n_b)(e_HeI−e_HeIII) | 조건부 per-baryon 표현의 직접 유도 | 같은 state의 explicit n_b가 있을 때만 적용한다. 다른 n_b나 missing n_b는 수치 native 반환을 거절하거나 null로 둔다. |
| Chemical correction=−(24.59+54.42)C | 고정 recipient binding convention의 직접 유도 | 중복 chemical storage 제거다. Actual proton work 또는 heating이 아니다. |
| Selected electron marginal·kinetic return은 partition에서 additive | 직접 유도 | Electron labels가 disjoint일 때의 성질. Parent event의 중복 보정과 구분한다. |
| 기존 RR·retained photon port | identity가 맞는 기존 계산 재사용 | Once-only 별도 ownership이다. Source-ion 보정에 다시 더하거나 w_ext/heating으로 옮기지 않는다. |
| Actual exclusive S,D, outside partner state/energy/history/response | 실제 필요한 입력 미확보 | null. 이번 mathematical witness가 실제 입력을 대신하지 않는다. |
| Actual donor work, EOS/T, full-source physical native25 | 실제 필요한 입력 미확보 | null. Named same-state consumer의 구조적 수신 가능성과 physical activation을 구분한다. |
| 실측으로 검증된 새 He kernel 또는 새 physical closure | 이번 단계의 실측 근거 없음 | 주장하지 않는다. 실측 오차·관측 일치율도 만들지 않는다. |
| 새 independent code/runtime PASS | 후속 bounded 검증 필요 | Static review와 runtime 결과를 구분하고 C9의 실제 반환으로 판정한다. |

## 사건·단위·지원 영역

Ω는 저장 electron atom labels의 유한 집합이다. D의 unordered pair record(x,y,w)는 사건 밀도 w다. x≠y이면 symmetric matrix entries는 각각w/2이고 x=y이면 diagonal entry가w다. 대각 사건도 electron leg는 두 개다. Species는 H1/He4에 고정하고 He nuclear photodisintegration의 alpha/daughter state를 이 atomic He channel로 매핑하지 않는다.

Birth support는 3200 active atoms의 0.1<E≤10eV와 별도 0.1eV cutoff ghost다. Ghost는 미지의 subcutoff spectrum을 생성하지 않는다. 네 birth-energy partitions와 기존 네 observation-time bins는 서로 다른 축이다. Proper-volume density이며 absolute volume은 null이다. Gas-rest scalar, nonrelativistic, zero recoil, frozen 100K를 유지한다.

## Physical consumer의 명명과 범위

구현 대상으로 명명한 consume_event_union은 같은 source/state/frame/clock의 complete event claims를 모아 source-ion union increment를 반환하는 조건부 consumer다. 검토 대상 구현은 source payload, atomwise marginal, event ID, partition claim completeness와 same-state n_b를 검사하도록 작성됐다. 이 함수의 실제 runtime acceptance는 후속 단계가 입증한다. Actual exclusive event measure가 없으므로 함수 이름이나 species vector가 있다는 이유만으로 full_physical_consumer_activation을 true로 올리지 않는다.

## Novelty와 strong no-go

이 결과는 현재 저장 marginal의 명시된 finite-atomic family에 대한 구성과 정확한 bound다. 문헌 전체의 최초성이나 실제 He FDCS를 유일하게 복원할 수 없다는 전역 no-go를 주장하지 않는다. 현재 조사에서 필요한 실제 joint 입력 bytes를 확보하지 못했다는 범위만 보고한다. 자세한 primary 읽기 범위는 ../intake/PRIMARY_SOURCE_MAP_KO.md에 있다.
