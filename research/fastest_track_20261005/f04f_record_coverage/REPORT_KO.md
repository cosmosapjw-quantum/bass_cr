# F04F: 저장 이력 전체와 stage 관측의 읽기 전용 범위 연결

7,000개 F05 accepted 기록의 합산 25출력을 동일 source/parent/time/units 계약에 연결했다. 새 adapter 시험 20개와 stage coverage 시험 7개가 통과했다. Native·root·history·certificate checker 실행은 이번에 모두 0이다. F04E의 첫 accepted 기록 두 half native 관측은 검증된 정본에서 그대로 소비했다. 이것은 추가 uniform event enclosure나 실제 expanding stage 소비의 구현 검증이 아니다.

## 입력과 완료 범위

Dropbox에서 F04D ZIP 224,864 bytes/SHA14a076a223ad62a445149521ae00683b8b88ac23e26227b3e5a19f827fd17879와 F04E ZIP 404,871 bytes/SHAb88932c7a2337972df19231755491725b7090bab347d203fa514fce2717b7cdd를 회수했다. 각각 40/100 payload의 size/SHA, ZIP CRC와 경로를 검증했다. Mirror는 다운로드하지 않았다. 정확한 ID/path는 REMOTE_FETCH_RECEIPT.json에 있다.

Owner F04 정적 certificate와 F05 0..1e12 s whole-interval completed 상태를 수신했다. 옛 parent-not-frozen 또는 F05-not-completed 문자열을 현재 blocker로 쓰지 않는다. 기존 F04D 24시험, F04E 28시험, F05 MPFI200 검사와 native 실행은 반복하지 않았고 우리 새 시험 수에 합산하지 않았다.

F05 입력은 rei_bianchi@7c5469101f8d6ef027c8c3119cc5c053e15ba1d9의 정본 Git bytes다. SOURCE_LOCK의 20개 파일 size/SHA/Git blob을 확인했다. source_identity.dat의 byte-length framing으로 22개 compile-time source를 읽었다. Donor FT03/rates hash와 원 parent/model/compiled constants bits가 일치한다. b12를 b1+b2로 재계산하지 않았다. Compile-time 소스와 최신 owner F08 소스는 별도 lock으로 보존한다.

## 합산 기록 검사

Level 0/1/2 accepted 수는 각각 1000/2000/4000, rejected 수는 모두 0이다. 시간 연결, old→state와 parent→next box 연결, initial parent bits, HALF1/HALF2 순서·dt/2, 원 local <2e-4/public width <2e-3/ledger <1e-12 기준, 요약 수량·최종 상태·t_end=1e12 s가 일치했다. 이 검사는 저장값과 원 요약의 일관성 검사이며 residual/Krawczyk/Taylor 인증을 재실행하지 않았다.

상태 7개는 실제 HALF2 normalized center다. PI9/CI3/RR3/DR2는 native accepted half1+half2 합산 count를 nH로 한 번 나누며 dt로 나누지 않는다. Escape는 저장된 cumulative escaped state의 new-old 차이를 exact rational로 구한 뒤 nH*eV_erg로 나눈다. 이는 두 rounded cumulative 값의 차이이고, 기록되지 않은 각 stage의 정확한 적분값이나 outward enclosure가 아니다. Hex 값은 관측값/단위 변환의 binary64 표현이고 exact ratio는 그 관측값의 산술이다. 원 raw line SHA와 압축 원 journal SHA/Git blob을 남겼다.

Discarded full endpoint는 진단 identity만 검사하고 accepted 25출력에 넣지 않는다. Rejected flag는 출력을 만들거나 시간을 전진시키지 않는다. 원본 17 MiB journal 전체는 별도 intake와 receiver Git에 보존한다. 반환 capsule의 선택 행·생성 출력은 그 전체 원 증거의 대체물이 아니다.

evidence/binding/BINDING_RESULT.json의 missing_observations는 **F05 journal 자체에 없는 필드**를 뜻한다. 최신 F04E의 별도 first-record probe를 포함한 현재 범위는 evidence/STAGE_COVERAGE.json에서 읽는다. 첫 점의 25개 native bit 재현/14개 half center/20개 model bit는 F04E 보고의 상속 결과다. 그 비교나 실행을 여기서 반복하지 않았다. 첫 점의 F04D real-point 차이 파일은 finite diagnostic이며 새 parity tolerance나 enclosure를 발급하지 않는다.

## F04E 관측과 F08 owner 경계

F04E에서 제공한 parser를 원 bytes로 사용해 저장 CSV를 읽었다. Record/source/model identity를 연결한 stage view는 level0 첫 accepted record 한 점에만 존재한다. 나머지 999+2000+4000=6999개 기록에는 개별 half events/escape native 관측이 없다. 이 누락은 기존 F05 수락을 취소하지 않으며, 이력을 재실행하거나 6999개 새 probe를 승인하는 이유가 아니다.

Owner 최신 ref8e8ea0c664e2ba2f2f8560e0c64266d206fbd50f의 coupled_primary.rs::endpoint는 PrimaryEvents.photo_per_h[packet][absorber]를 반환한다. F04D PI_[absorber]_[group]와 축 순서가 반대다. 고정 3packet 정적 관측의 reference view에서 명시적으로 transpose하고 count/nH를 한 번만 적용했다. CI/RR/DR도 per-H count이며 escape는 eV/H increment다. Static BE endpoint 시각 5e8/1e9 s는 F05의 t0/dt에서 유도한 시각으로 표기했다.

이 view는 actual PrimaryStep이 아니다. F08 stage의 실제 nH/fHe/Hmean, packet ID/energy, transport와 accepted commit identity 및 팽창 clock/a/energy measure는 owner 영역이다. Actual stage/weights/thermal work를 null로 남겼다. 정적 escape에 임의 a^3/a^4를 곱하거나 전체 count를 최종 half weight로 처리하지 않는다. 실제 소비 API나 receiver 소스는 수정·실행하지 않았다.

F08 현재 상태는 CONDITIONAL_STAGE_ONLY_PASS, paired_history NOT_EXECUTED다. 저장 qualification은 conditional 4gas/eliminated-packet root 범위이며 F04의 정적 7D parent certificate와 서로 옮겨 쓰지 않는다. Source contract에 남은 과거 F05 validator-running 문장은 최종 F05 completed receipt보다 우선하지 않는다. 이번 ref delta의 FLRW06 native return도 읽기 전용으로 보존했으며 재실행하지 않았다.

## 실행·검토·반환

Python standard library만 사용했다. 전체 journal adapter wall4.85 s, max RSS40,084 KiB; 새 stage coverage wall0.12 s. 정확한 argv/exit/wall/RSS와 Python identity는 evidence 로그에 있다. 최초 adapter scaffold의 import RED와 실제 ledger dict를 list로 읽은 개발 중 실패를 VERIFICATION에 보존했다. 최종 관련 시험 모두 PASS다. F04E compiler/binary identity는 상속이며 이 호스트에서 새로 실행하거나 build하지 않았다. 독립 agent/human review는 NOT_PERFORMED다.

같은 BASS branch의 새 경로에 additive/non-force로 게시한다. 정본 ZIP은 두 기존 provider에 create-only 백업하고 이번 canonical tested release의 R3 raw restore SHA/payload 검증을 수행한다. 게시 ref·원격 ID·size/SHA와 tier는 detached delivery receipt와 BACKUP_RECEIPT에서 읽는다. 사용자 ChatGPT thread6abfa205-dbe8-83ee-969b-0e00111c9404의 직접 read/write ACK는 없으며 Git/cloud 동기화와 구분한다.

다음 optional 작업은 기존 source/root boxes를 그대로 소비하는 event+escape observable enclosure 또는 owner의 실제 stage-log/time/measure 계약이다. 새 mandatory gate를 만들지 않는다. CR_OFF_FASTEST, precision atomic PARKED, G02 UNRESOLVED, production HOLD, capture=false, all_bound OPEN, b_grid NO_GO와 actual CR-dispatch null을 유지한다.

## 재현 명령

새 adapter 시험: `python3 -B -m unittest -v test_binding`

새 stage-view 시험: `python3 -B -m unittest -v test_stage_coverage`

원 journal이 필요한 adapter: `python3 -B receiver_binding.py --capsule inputs --receiver /path/to/locked/receiver --output /absolute/new/output`

정본 capsule로 가능한 stage view: `python3 -B stage_coverage.py --root . --output /absolute/new/STAGE_COVERAGE.json`

출력은 create-only다. 원 executed evidence의 경로명이 초기 f04e_receiver_binding으로 기록된 로그는 이후 F04F capsule에 그대로 보존했다.
