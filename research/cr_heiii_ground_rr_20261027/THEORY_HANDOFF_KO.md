# R1–R10 완료: HeIII ground RR 이론 → 코딩 인계

## 현재 선택

`CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1`을 구현한다. 정확한 이전 PR106 HeI 저장 operator에 He4III + fast electron → He4II(1s) + retained photon의 ground spontaneous hazard 하나를 추가한다. R1–R10 이론 단계는 완료했고, 이 문서 시점에 C6–C9 실제 수치 실행은 시작하지 않았다. 중앙 scoped DAG는 **27/88**, 별도 미병합 PR236은 **32/88**이다. 새 child는 기존 N5 wrapper에 연결하므로 원래 88-node 분모와 parent 상태는 바뀌지 않는다.

## 재사용할 근거

고정 최초 인계서 `8d0a5c375589fbddadc2bb90c8117311c80bad09`와 직전 S=`4caf4273eefd51f2c605a8667c3533d8489dd0f5`, D=`b11b2e9255f2b10fb5582376412e045bd1e9151c`를 실제로 읽었다. 직전 source ZIP SHA256 `7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa`를 실제 복원하여 198개 payload의 hash와 CRC를 확인했다. 완료된 H1, HeI, C23E, source projection 및 bath generator는 재실행하지 않는다.

R2는 SciSpace·Exa discovery 결과를 primary 원문과 대조해 Verner96 HeII row, ground-level Milne relation, NIST J를 확인했다. Native row support는 photon 54.42–50000 eV이고 이 소비자의 electron energy는 양수이며 E+54.42가 그 범위 안에 있어야 한다. Elemental-He→He4 조건부 mapping과 stationary-heavy/zero-recoil 가정을 보존한다. WU/REC/HE의 현재 source scope와 미완료 rate·deposition·physical-error 의무는 intake에 별도 기록했다.

## 재사용 가능한 이론 결과

`THEORY_KO.md`의 §2–§7을 그대로 구현한다. G0≥G1≥0, 기존 비음성 reward의 감소, single-added-channel bound, stable stored-column response, inherited partition/energy defect, integrated event/native25 map이 핵심이다. Conditional ratios의 단조성이나 전체 물리 오차 bound는 주장하지 않는다.

R6는 별도 agent의 1회 독립 검토와 동일 repair episode의 수정 확인으로 종료했다. 실제 두 finding은 SI 단위와 physical18 열 매핑이었다. 최종 THEORY SHA256 `3e5f31d271c32efcd1ee9a1eb23625c2ead0dc0b6c4a78732de34ef4a696ceae`에 결속되어 있고 미해결 material finding은 없다. R7의 Wolfram 유리수·보존식 검산은 실제 19/19 PASS다. CAS의 provider CPU는 제공되지 않았으며 0으로 적지 않았다.

## 다음 실행 계약

`FROZEN_CONTRACT.md`와 `RESOURCE_SCOPE.json`을 먼저 읽고, C1에서 baseline/acceptance identity를 확인한다. `intake/DESIGN_MAPPING_KO.md`와 `INPUT_ARRAY_HEADERS.json`은 C2의 실제 입력–식–코드 대응 근거다. C3는 roundoff, solver residual, finite grid 및 upper-domain 차이를 분리하고, C4에서 실제 resource admission과 create-only run leases를 준비한다. C5는 runnable implementation을 완성한다. C6는 changed controls, C7는 8-case224 RHS/24 rows, C8은 저장 결과의 grid/domain 비교 및 figure, C9는 finest2의 독립 Decimal70 56 RHS와 source exports를 검사한다.

새 local science 상한은 failed attempts와 coordinator를 포함해 30 CPU-s이며 세부 예약은 5/8/10/5/2다. 과거 예산을 이동하거나 합산하지 않는다. 현재 local scientific workers started=0이다. Create-only lease와 previous-attempt receipt가 없거나 유효하지 않으면 진행하지 않는다. 실행에 사용된 source/config/input hash, 실제 command/affinity/thread/RAM/exit 및 output identity를 기록한다.

적분 event count·energy에는 SI 변환을 한 번 적용한다. Actual nb_m3는 null이고 positive-nb control만 per-baryon map을 검증한다. Rate/exposure/instantaneous RHS는 null, retained photon은 별도 port, native w_ext=0이다. Caloric partition을 physical heating으로 바꾸지 않는다.

## 게시와 상태 보존

현재 작업 branch는 `research/cr-heiii-ground-rr-20261027`, draft PR은107이다. 각 R 단계는 expected-parent non-force commit과 ZIP, Library·Dropbox·Drive 영수증을 갖는다. Checkpoint backup은 R2 metadata tier이며, 최종 source release 및 authority 변경은 실제 R3 raw readback으로 검증한다. 현 단계 receipt는 커밋 이후 생성되어 다음 checkpoint에 포함되는 방식으로 자기참조 hash를 피한다.

중앙 관찰 HEAD는 `12f6007a83a40d76f80574e41a5402676e81fc7a`다. 병렬 BASS 세 partial 관측을 보존한다. 최종 중앙 변경은 실제 C9와 S/D/ZIP/backup receipt가 나온 후 5개 owned path만 수정한다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, global physical completion/error null, L4=false, 과거 UNKNOWN_NO_ACK를 유지한다. 과거 UNKNOWN_NO_ACK에 대한 10/26 backfill은 새로운 저장 증거로만 덧붙인다.

접근 가능한 공개 branch/PR와 백업 inventory는 survey에 기록한 범위까지 조사했다. 개인 대화 검색은 unavailable였고 일부 Drive 목록은 끝 페이지를 확인할 수 없어 전체 대화·모든 비공개 blob을 읽었다고 주장하지 않는다. 이 접근 제한은 선택한 source-qualified unit의 입력 복원·구현을 막지 않는다.
