# He4 ground RR 및 외부 source 인터페이스 — 고정 인계

이 문서는 source S 이후의 문서 D snapshot이다. 이 파일의 containing commit을 D로 사용한다. 중앙 M의 실제 게시 receipt와 최종 closeout artifact ID는 PR106의 최종 게시 기록 및 별도 `BASS_CR_HE4_EXTERNAL_CLOSEOUT_20261025_4caf4273eefd.zip`에 결속한다. 문서 내부에 자기 commit/hash를 만들지 않는다.

## 완료한 두 단위

Source S는 `4caf4273eefd51f2c605a8667c3533d8489dd0f5`, 기준 expansion은 `8d0a5c375589fbddadc2bb90c8117311c80bad09`다. `research/program-expansion-20261025` / draft PR106에 expected SHA와 `force=false`로 게시했고 실제 `git ls-remote`가 S와 일치했다. 공개 148개 파일의 Git tree는 `361b8e3222687f03ddedc0b4045d5cdc903db3cd`다.

1. `CR_HE4_GROUND_RR_CONSUMER_NEXT`: He4⁺ ground 1s + e → He4 ground singlet + spontaneous photon 한 채널을 저장 PR105 H1 체인에 추가했다. Native I=24.59 eV, d=4, capturing-ion density=0.02 cm^-3를 고정했다. He4 mapping과 smooth ground-channel/residual-state assignment는 조건부이며 stationary heavy target/zero recoil이다. 31 controls, 8 cases/192 primary RHS, 24 source-weighted rows, 216 grid/domain comparisons와 독립 Decimal70 48 RHS/72 coefficients/6 rows가 PASS했다. Gate는 `NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_HE4_SMOOTH_GROUND_RR_ON_SAVED_H1_CHAIN`이다.
2. `CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE`: photon/electron/baryon 측도·분포·주입·frame·clock·volume·isotope mapping, 공통 사건 extent, 에너지 소유권, EOS derivative 및 cutoff flux 경계를 구현했다. 26 controls와 C23B 32,592 atoms/9 cases, C23E 18 points/90 events를 실제 소비했고 독립 검토가 PASS했다. 마지막 runner budget-history guard 변경은 별도 기계적 검사 및 C9 supplement로 검증했다. Gate는 `IMPLEMENTATION_VERIFIED_SCOPED_SOURCE_AND_EVENT_CONSUMER`다.

R1–R10/C1–C10의 scoped 활동과 근거는 `LOOP_LEDGER.json`에 있다. 전체 물리 프로그램의 완료율을 뜻하지 않는다. 계산·독립 검토를 복구 목적으로 반복하지 않는다.

## 핵심 결과와 수치 해석

Finest R80/N2048의 두 χ와 세 저장 z에서 He 포획 확률은 활성 초기 전자당 3.28466398e-10–3.90541038e-10, 조건부 photon energy는 28.8109669–30.0327994 eV, 평균 first-stopping-time 감소는 0.102482–0.120377 ms다. 독립 최대 열별 상대차는 4.243216244181207e-11로 고정 기준 5e-10을 통과했다.

일부 국소 diagonal에서 새 He hazard가 binary64 반올림에 묻힌 진단은 보존했다. 독립 기준은 `Decimal(stored PR105 H1 diagonal)+Decimal(new He hazard)`다. H1과 He4는 같은 새 연산자에서 계산했으며, 거의 같은 두 결과를 빼는 대신 안정적 resolvent response를 사용했다. 단일 추가 hazard의 multiplicative bound를 다중 신규 채널의 개별 bound로 자동 일반화하지 않는다.

RR 사건의 signed energy는 fast=-E, internal=-I, photon=E+I다. 이번 retained photon과 C23E Case-A escaped photon을 각각 보존한다. Caloric partition, first entry, retained radiation을 physical heating 또는 irreversible assimilation 완료로 승격하지 않는다.

## 실제 복원용 소스 ZIP과 백업

- 파일: `BASS_CR_HE4_EXTERNAL_SOURCE_20261025T131931428504Z_4caf4273eefd.zip`
- 크기: **29,763,489 bytes**.
- SHA256: `7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa`.
- 구성: manifest payload 198개 / ZIP member 199개. 공개 S bytes, private 재사용 입력 21개, 새 NPZ 8개, 독립 dense Decimal CSV 2개, 외부 SOURCE_MANIFEST 원본 9개를 포함한다.
- Library: `libfile_181838c1e8f081918832f8eddfdf1ac1` — 실제 whole-file materialization, size/SHA256/CRC/전 payload 검증 **R3 PASS**.
- Dropbox: `id:BSpOijBcT10AAAAAAEAbFw` — completed ACK, 실제 GET 및 전 payload 검증 **R3 PASS**.
- Drive: `1OZ8LmMbUlbR2VHSxWXp35yjIAL7MPHMK` — 단일 업로드 성공 ACK, actual raw fetch/transfer 및 전 payload 검증 **R3 PASS**.

상세 실제 receipt는 `publication/CANONICAL_BACKUP_RECEIPTS.json`과 `publication/CANONICAL_R3_READBACK.json`에 있다. Dropbox content hash는 같은 알고리즘끼리 비교했다. Drive metadata 도구가 반환하지 않은 MD5/SHA256은 UNAVAILABLE로 기록하고, 실제 내려받은 bytes의 SHA256과 구분했다.

Canonical은 S snapshot을 고정한다. 이후 D/M 내용과 actual publication receipt는 별도 final closeout에서 보존한다. 새 성공은 이 파일에만 적용한다. H1 canonical의 과거 Drive UNKNOWN_NO_ACK, terminal NOT_ATTEMPTED와 소실·차단된 PR104 terminal은 복원하거나 성공으로 승격하지 않았다.

## 전체 DAG와 다음 실행

전체 위치는 WU/REC/HE 공급자 → CR source·stopping/원자 coverage·외부 interface → N6 보존적 결합 → N7 새 parcel → REI scenario 조립이다. **N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED**, global physical completion/error bound=null, L4=false를 유지한다. HE101 C8 OPEN/reserve0/PASS-FAIL-FAIL, PHYS91 소진 예산 및 원 공급자 유효범위를 보존한다.

중앙 target은 `rei_bianchi:research/orchestration-sandbox-20261022`, 현재 확인한 parent는 `78f7ac5864d5817ceb79b48cb5e298cc30006510`이다. 이번 문서 D 다음 단계에서 두 소유 CR node와 대응 contract만 갱신한다. 다른 85개 node와 17 integration edge, top-level authority 및 parent gate는 보존해야 한다. 해당 M의 실제 ref 확인은 최종 closeout 기록을 따른다.

다음 우선 후보는 별도로 source-qualified한 HeIII→HeII ground capture 소비자 또는 평가된 외부 spectrum/history 한 공급자의 결속이다. HeIII는 이번 계산에 포함되지 않았다. β에는 WU의 evaluated Q/spectrum/branch/mass/clock, 일반 cascade/stopping에는 REC/HE의 필요한 spectral/differential export를 명시해 연결한다. 빠진 공급자는 null/pending이며 실제 0 rate로 바꾸지 않는다. 각 node 전 최신 AGENTS·HEAD·병렬 변경과 해당 공급자 입력을 확인한다.

## 비용과 재개 규칙

He4 새 worker 4.189415 + coordinator 0.018524602 = **4.207939602 CPU s / 새 단위 cap 30 s**다. 입력 복구의 mechanical 0.039411097 s는 별도다. 외부 interface 첫 실행 0.145485309 + runner guard 기계적 검사 0.001943521 = **0.147428830 CPU s / 새 단위 cap 30 s**다. 다음 단위로 미사용 상한을 자동 이전하지 않는다.

과거 H1 known lineage **39.097868524 CPU s**와 별도 C23E **15.493261114 CPU s**는 중복 근거 없이 합산하지 않는다. global remaining/currency는 null이다. 첫 He4 memory-admission 거부는 worker 시작 전 실패로 보존했고, 실제 clean-cache 자원 추정 교정과 후속 controls_v2를 구분했다. 포장 중 Git에 없는 `.codex/readback-policy.json`을 요구한 선택 오류는 archive 생성 전 거부됐으며, 실제 AGENTS 및 `docs/READBACK_POLICY.md` bytes를 포함하고 부재를 명시하는 기계적 교정만 수행했다.

## 다음 대화에 붙여 넣을 지시

```text
$physmath-research-loop로 cosmosapjw-quantum/bass_cr의 PR106 연구를 이어가라.
먼저 이 HANDOFF_KO.md의 containing D commit, PR106의 최종 S/D/M 기록,
별도 BASS_CR_HE4_EXTERNAL_CLOSEOUT_20261025_4caf4273eefd.zip을 읽어라.
Science S=4caf4273eefd51f2c605a8667c3533d8489dd0f5.
원 source ZIP SHA256=7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa.
완료한 H1/He4/C23E 계산·검토를 재실행하지 말고 정확한 저장 입력과 결과를 재사용하라.
다음은 source-qualified HeIII ground capture 또는 입력이 확보된 외부 spectrum/history
한 공급자의 소비 계약을 구체화하라. WU/REC/HE의 유효범위·isotope mapping을 보존하라.
각 node 전 최신 AGENTS·HEAD·병렬 변경을 확인하고 새 입력·예산·run ID를 결속하라.
N4/N5 partial, N6/N7 gate, 과거 UNKNOWN_NO_ACK·소진/미확인 예산을 유지하라.
caloric partition을 physical heating 완료로 승격하지 마라.
```
