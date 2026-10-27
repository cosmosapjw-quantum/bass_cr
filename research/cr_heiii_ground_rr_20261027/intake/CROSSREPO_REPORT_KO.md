# R1–R3 교차 저장소 조사 — 2026-10-27

## 실제 조사 범위

`cosmosapjw-quantum`의 접근 가능한 저장소 목록은 51개였으며 offset 0의 51개와 offset 100의 빈 페이지를 확인했다. 목록의 모든 항목을 관련성 기준으로 선별했다. 연구 의존성이 직접 있는 공개 8개 저장소에서는 브랜치, 열린 PR, 닫힌 PR을 각각 마지막 페이지까지 읽었다. 아래 수치는 목록 및 PR 제목·본문 조사 범위다. 모든 브랜치의 모든 파일을 읽었다는 주장이 아니다.

| 저장소 | 브랜치 | 열린 PR | 닫힌 PR |
|---|---:|---:|---:|
| rei_bianchi | 278 | 221 | 14 |
| WU088_HH | 159 | 150 | 0 |
| rec_bianchi | 156 | 104 | 34 |
| BASS_HE | 107 | 102 | 0 |
| bass | 277 | 162 | 30 |
| vigilode | 215 | 59 | 30 |
| bianchi_phase_r | 1 | 0 | 0 |
| MOSAIC-ODE | 1 | 0 | 0 |
| 합계 | 1,194 | 798 | 108 |

`bass_cr` 자체의 조사·복구는 부모 실행자가 별도로 맡았다. `CLASSIER`, `RABBIT_v1.0.5_PRODUCTION`, `HEP-ASTRO-COSMO`의 공개 metadata에서는 2026-10-25 이후 새 push가 없었다. `htt_base`는 2026-10-27 push가 있으나 최근 5개 열린 PR의 실제 제목·본문은 여섯 논문 관측/선택법칙 및 CAS 형식화 연구이며, 이번 HeIII 비열적 ground-RR 소비자의 새 공급 근거로 채택하지 않았다. 나머지 저장소는 이름·가시성·기본 브랜치 등 실제 metadata로 관련성을 선별했고, 본 작업의 공급망으로 편입할 직접 근거를 찾지 못했다. 전체 private/unrelated catalogue는 public Git이나 전달용 archive에 포함하지 않는다.

## 중앙 27/88와 미병합 개발 32/88

중앙 branch `research/orchestration-sandbox-20261022`의 실제 관찰 HEAD는 `a5db4bac9dafadae29685bbea3cec7f43ab990b2`다. DAG 원문 1,592,014 bytes를 회수했다(SHA256 `47d221f5596d21c7549ef1d51dc5fb76871350463fff2cecfad0786956404d81`). 노드 88개, 통합 edge 17개다. 문자 그대로 `COMPLETE`로 시작하는 status는 18개이며, 기존 선언된 산출물 기준의 scoped 9개를 더하면 27/88이다. 이 분류의 정확한 ID 목록은 `CROSSREPO_SUMMARY.json`에 있다.

PR236의 개발 branch `research/rei-lumina-benchmarks-20261027` HEAD는 `ee94bef85b56d879dc38f184856a5c613575e9e1`다. 실제 DAG 1,616,902 bytes(SHA256 `e4c30609e737318724877a10c1acb7f139b6dc521e3b207a9455cfe632613b1d`)와 대조하여, 원래 88개 ID 순서·17개 edge·모든 nested contract가 그대로임을 확인했다. 새로 완료로 분류한 5개는 `HE-EXP-SPECIES`, `REC-EXP-SPECIES`, `REC-FIELD`, `REC-EXP-SPECTRAL`, `REC-EXP-EXTERNAL`이다. 그래서 별도 개발 상태는 32/88이다. 여섯 번째 변경 `REC-COUPLED`는 `CONSTRUCTIVE_PARTIAL_SELECTED_NATIVE_PW19_PREASSIMILATION_SOURCE`이며 완료 증가 0이다. 중앙에 아직 병합되지 않았으므로 중앙 수치를 32로 바꾸지 않는다. 상세 대조는 `LATEST_DAG_COMPARISON.json`에 있다.

## 새 공급 근거와 재사용 한계

WU PR150/HEAD `87933da5654bb2e4d93f7de4341df5e0fa0f8716`는 26개의 primary source variant와 24개의 정확한 정수 projection을 제공한다. 원래 28개 방향 중 27개에 primary source reference가 있으며, He4(γ,dd) 직접 수치 입력은 남아 있다. 물리 rate/Q/deposition/consumer admission은 모두 false다. He4 beam-averaged 자료를 pointwise cross section으로, inclusive yield를 배타적 분기로 바꾸지 않는다. PHYS91 잔여 0을 보존한다.

REC PR138/HEAD `4a8e541030ee2cbd02e26ba671083b705d309d49`는 HD parser와 H5 input binding을 전달했다. HD 35 Hz 원 gate는 line 1 PASS, line 2–8 FAIL이며, 50/100/200 K와 collider 구분을 유지한다. H5는 313 query·626 endpoint 입력 연결을 완료했지만 물리 bound coverage는 0/313, physical epsilon은 null이다. 이 commit에서 root AGENTS.md 요청은 실제 HTTP404였으며 내용을 추정하지 않았다.

HE PR102/HEAD `ac6042a6b0610b09d0576538767ee0299389a5eb`는 supplied Qbar11에 대한 조건부 zero-drift heat/linear-drift drag와 count/energy 소유권을 구현했다. 유효 범위는 source Tstar 50–50000 K다. source isotope/mass/value/error의 실제 결합이 남아 있고 `physical_provider_admitted=false`다. HE101 C8 partial export, 과거 PASS/FAIL/FAIL, reserve 0은 그대로다.

REI PR233은 처방된 연속 photon history에서 307,200개의 H1 primary electron energy atoms를 노출했다. 이것은 후속 stopping 소비자의 실제 spectral input 후보지만 full stopping/heating은 승인하지 않았다. PR235는 normalized beta와 moving-reservoir component, PR236은 native PW19 photo source에 25좌표 number/energy/logT 연산자를 연결했다. 최신 결과는 기존 CR bath를 교체할 근거가 아니다.

## HeIII→HeII ground RR 다음 단위

중앙 `CR_HE4_GROUND_RR_CONSUMER_NEXT` 원문은 이미 끝난 He4+→He4 ground 결과를 재사용하고, 남은 N5 microscopic channel을 별도 named consumer로 진행하도록 명시한다. HeIII capture는 별도 미완료 dependency다. core 4개 repo의 전체 branch/PR metadata에서 같은 saved-chain nonthermal HeIII ground-RR 소비자의 별도 active owner는 관찰되지 않았다. 오래된 REI Case-A total RR/DR 및 HE 재결합 event bridge는 다른 범위다. 이 결론은 실제 조사한 metadata 범위의 관찰이며, 모든 대화나 미게시 파일의 부재를 증명하지 않는다.

PR236의 실제 `theory/GATE_INPUT_MAP.json`과 `theory/CONTRACT.md`에서 He3II/III 인덱스 8/9, He4II/III 인덱스 11/12, threshold 54.42 eV, photon support [54.42,50000] eV, primary support [0,49945.58] eV를 확인했다. isotope policy는 `ElementalElectronicEquality_He3_He4_conditional`이며 각각의 동위원소 abundance와 A를 구분한다. provider는 `blocker_closure_20261026/implementation/pw19_rec_callback.py`, SHA256 `5cb2601b98639345bca4f6f1a39536ed8924b1c6ad37cb109e974267a4705000`이다. 원 source/threshold/domain과 조건부 isotope mapping만 참고하고 PW19의 photoGamma, 최신 REI T=14919.863839279506 K·nb=10.669321142818111 m^-3를 저장된 CR bath에 이식하지 않는다.

새 ground-RR 소비자는 saved-chain identity, capturing HeIII density, bound/ion degeneracy, native PI source support, Milne convention, one-event energy owners, rare-response own-column 기준을 명시해야 한다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED와 원 H1/C23E 별도 예산 계보를 유지한다. retained RR photon energy와 first-entry/caloric partition을 실제 heating/assimilation으로 승격하지 않는다.

원래 88개 DAG 분모를 유지하려면 N5의 하위 결과/owner-return에 새 named consumer를 추가하는 방식이 적합하다. 실제 canonical node를 추가하는 선택도 중앙 `ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md`는 허용하지만, 원 contract·unique ID·typed dependency·구체적 PR plan·별도 예산을 갖춰야 하며 expanded denominator는 89가 된다. 원래 88 기준과 expanded 89 기준을 따로 보고해야 한다.

## 수행·보존 상태

이 작업은 원자료 조회·metadata pagination·DAG의 기계적 비교뿐이다. science solver, source quadrature, 과거 성공 suite, IVP를 실행하지 않았다. R1–R3 조사 지원이 완료되었으며 다른 R/C 단계의 완료를 주장하지 않는다. 실제 읽은 AGENTS·source·DAG snapshot과 SHA256 목록, pagination 결과, 한계는 `CROSSREPO_SUMMARY.json`에 저장했다. 원격 변경·게시·백업은 부모 실행자 소유다. branch가 다시 움직일 수 있으므로 노드 실행·게시 직전에 새 HEAD를 관찰해야 한다.
