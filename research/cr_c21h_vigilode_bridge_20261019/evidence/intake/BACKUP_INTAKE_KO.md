# C21H 연구 전 백업 인계 조사

조회 기준은 PR84 문서 head `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5`, 마지막 게시 시각 2026-10-19T09:26:28Z이다. 실제 백업 조회는 2026-10-19T12:29:28Z 이후 수행했다. GitHub와 NCP 조회는 부모 실행자가 별도로 담당한다.

## 판정

- **bass_cr C21G 새 native/NCP 반환은 직접 열거한 관련 저장 범위에서 발견하지 못했다.** C21G 최신 백업은 기존 389239-byte ZIP이며, 그 존재를 새 실행으로 세지 않는다.
- **VigilODE의 새로운 실측 결과와 VODE/Diffsol 비교가 존재한다.** 새 보고서와 필요한 작은 자료를 읽었고, 오래된 벤치마크 실행을 반복하지 않았다.
- **rei_bianchi BR05는 별도 native 실행을 완료했다.** 이는 C21G의 fixture/source/native 실행 상태를 대체하지 않는다.
- 모든 외부 작업은 읽기였다. 기존 ZIP, 이전 분기, 데이터와 영수증을 수정하거나 덮어쓰지 않았다.

## 실제 열거 범위

| 저장처/범위 | 항목/페이지 | 완료 근거 |
|---|---:|---|
| Drive bass_cr | 46 + 유일한 자식 폴더 1 | top_k1000 직접 목록; 한도 미만, 하위 폴더도 읽음 |
| Drive 이전 BASS_CR_NCLOUD_F1 폴더 | 1 | top_k1000 직접 목록 |
| Drive REI BASS hierarchy 백업 | 112 | 최초 fetch100의 부분 목록을 list_folder1000으로 보완; 자식 폴더 없음 |
| Dropbox bass_cr dossier | 14 | recursive, has_more=false, cursor 빈 값 |
| Dropbox REI BASS hierarchy | 27 | recursive, has_more=false |
| Dropbox VigilODE v3.5 bootstrap | 5 | recursive, has_more=false |
| Dropbox ode_solver | 3 | recursive, has_more=false |
| Dropbox REI sync의 bass_cr | 2 | recursive, has_more=false |
| Library bass_cr dossier | 70 | recursive, next_cursor=null |
| Library bass_cr 제목 전역 | 620 / 7 | 모든 실제 cursor 후 마지막 null |
| Library VigilODE 제목 전역 | 194 / 2 | 모든 실제 cursor 후 마지막 null |
| Library NCP 제목 전역 | 145 / 2 | 모든 실제 cursor 후 마지막 null |
| Library C21F/C21G 제목 | 14 / 1 | 각 next_cursor=null |
| Library 전역 새 수정분 | 45 / 1 | 09:26:28Z 이후, recursive, next_cursor=null |

검색은 추가 발견용이다. Dropbox C21/bass_cr/NCP/VigilODE 전역 제목 검색은 66/100/100/2개를 반환하고 모두 has_more=false였으나, 정확히100개인 검색에는 내부 결과 한도 가능성이 남는다. 직접 폴더 열거를 부재 판정의 근거로 삼았다. 각 원본 항목의 정확한 ID, 경로, 크기, 시각과 조회 범위는 `BACKUP_INTAKE.json`에 보존했다. 다른 프로젝트의 NCP 제목 검색 항목은 개수만 남기고 상세를 제외했다.

## 새 VigilODE 자료

### 실측 비교 보고서

`COMPARISON_REPORT.md` (Library file `libfile_226b74072c60819182faa0c2d7d704b2`, 7174bytes, modified 2026-10-19T12:00:43.394566Z)을 전체 읽었다. Library 이름 `VigilODE_VODE_Diffsol_Comparison_20261019.zip`은 18869bytes이며 file ID는 `file_00000000a85481fa93ca908c8586085f`다. 새 ZIP은 이번 조사에서 다운로드하지 않았다.

보고서는 A07의 동일 Robertson 101점 출력 격자, rtol1e-8/atol1e-11에서 VigilODE native fast의 R=0.337530(경험적 spread를 더한 상단0.338608), Diffsol0.16.1 BDF의 R=3.302699(상단3.303777), 새 SciPy1.17 VODE BDF의 R=128.500351(별도 Radau/LSODA 차이0.001978 추가)를 기록한다. 이는 보고서와 그 출처를 읽은 결과이며, 이 agent가 새 수치 실행을 한 값이 아니다. VODE의 정상 반환과 요청 정확도 실패를 구분해야 한다. 세 solver의 **동일 달성 정확도 속도 순위는 UNRESOLVED**다. A07 paired within-host Diffsol/native warm 시간비1.4194는 진단 자료이며, 다른 호스트에서 얻은 VODE 시간을 나눠 속도비를 만들지 않는다.

`vode_bdf_targeted.csv`는 Library에서 표 파서 형태로 읽혔다. 생성된 `vode_bdf_targeted.parsed.txt`는 그 **표 파서 표현**이며 원시 CSV 바이트가 아니다. 파서는 index 열과 숫자 표기를 추가/변환하므로 원본 CSV SHA, 원래 부동소수 비트 또는 원시 파일 동등성의 근거로 사용할 수 없다.

### V2 벤치마크

`VigilODE_V2_Benchmark_a21d573_KO.md` 전체642행(85658bytes)을 두 번의 연속 read로 읽었다. Library ID `libfile_3c52f0d88a788191bb00d87d3b0576ed`. 최신 확인 head `a21d573980f66fe02891bd216153443b5352f921`와 실측 Rust 빌드 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`를 보고서가 구별한다. 새 CT2700조건 중2639정상 종료,2329조건의 측정 격자 R_up<=1 통과가 보고돼 있다. 정상 종료만으로 정확도를 인정할 수 없다.

최신 도구의 남은 반례는 mass 지원 가능성을 필수조건처럼 다루는 적용성 판정, 101시간에 상태1개만 남긴 합성 행을 R_up0으로 받아들이는 길이 검사 누락, 실제 Rust가 출력하는 추가3키를 거부하는 schema 불일치다. 보고서에 정확한 GitHub 소스 경로와 보존 원자료 위치가 있다. 이는 현재 GitHub source를 별도로 확인한 후 적용 여부를 결정할 입력이다.

큰 `VigilODE_V2_Evidence_a21d573.zip` (183583031bytes, `file_00000000567081f4888c4353f729e457`)이나 CT CSV1005255bytes를 다시 복원하지 않았다. 필요한 소스는 GitHub에서 직접 읽도록 부모에게 전달했다.

## native owner의 별도 새 실행

`REI_BASS_REACTIVE05_GITHUB_FINAL.json`, `REI_BASS_REACTIVE05_ARCHIVE_IDENTITY.json`, `BR05_NEXT_HANDOFF.md`를 전체 읽었다. PR206은 보고 시점 open Draft이며 head `00e89bce3060516083d63edb857f1294ee560ea0`, source commit `3588027e41937f331680ab3e5c09de2f327db524`다. SIGNED_MINUS, Nt16, birth refinement r8, T8e12s native history 한 번이41.917961863초에16/16단계 완료됐다고 기록된다. 이전5개 비교 history는 재사용됐다. C21G의 새 실행이 아니다.

원본 ZIP `REI_BASS_REACTIVE05_NATIVE_MONITOR_20261019_53fa8c74_FULL.zip`은76033888bytes, 기록된SHA256 `53fa8c74664213b369449b9676c41969f0dda9ff6f22e3d738a24ebf59dc42bd`. 실제 Drive metadata ID `1ZUwhKjkBe6mYy34QywzHTjh5Hm4E5SOh` 및 Dropbox metadata ID `id:BSpOijBcT10AAAAAAD_QzQ`를 새로 조회해 각 크기를 확인했다. Library 새 수정 목록에도 동일 이름/크기가 존재한다. 이번 agent가 ZIP 원시 바이트를 받아 다시 SHA/CRC를 검사한 것은 아니다.

Drive 관련 폴더에는 REI AGE ENVELOPE v5 문서/코드/실행준비 ZIP 및 NATIVE_COUNT_ENERGY checkpoint도 새로 나타난다. 작은 AGE ENVELOPE receipt를 fetch했지만 텍스트가 비어 있었고, 반환된 파일 참조의 로컬 다운로드는 네트워크 Operation not permitted로 막혔다. 따라서 그 후보의 native 결과 의미는 **UNCLASSIFIED_UNREAD_CONTENT**다. 문서 제목만으로 새 native 성공/실패를 주장하지 않는다.

## 관측한 도구 한계와 최소 보완

Drive 전역 modifiedTime 검색은 새 BR05 ZIP을 누락했으며 직접 metadata와 폴더 목록은 그것을 반환했다. item_type=document는 ZIP 등 binary 자료를 포괄하지 않는다. Dropbox last_modified_after 필터 요청은 이전10/16자료도 반환하여 로컬에서 timestamp를 비교했다. Library 여러 제목을 한 번에 검색한 첫 호출의 경고/100개 결과는 완전성 근거로 쓰지 않고 각 제목을 따로 페이지 종료까지 조회했다.

과거 Dropbox `/bass_cr/C21`에 대한 현재 list/metadata 요청은 INVALID_ARGUMENT를 반환했다. 과거 백업의 실재 기록을 취소하지 않았고 그 폴더를 만들거나 움직이지 않았다. 공개되지 않은/이동된/색인되지 않은 다른 저장 위치까지 모든 새 데이터가 없다고 증명하지 않는다.

## 단계 상태

| 단계 | 연구/DAG | 게시 | 백업 |
|---|---|---|---|
| 새로운 결과 사전 조사 | COMPLETE_WITH_DISCLOSED_CONNECTOR_LIMITS | 부모의 C21H 게시에 포함 가능 | 새 조사 기록/읽은 보고서 create-only 보존 |
| C21G native 판정 | NOT_DISCOVERED_IN_ENUMERATED_SCOPES | 기존 PR84 상태는 별도 GitHub 조회 | 기존ZIP유지 |
| VigilODE intake | 새 실측과 도구 반례를 읽어 코드 선택에 인계 | 기존 source/benchmark PR을 부모가 조사 | 큰 기존ZIP복원 반복 없음 |
| BR05 native intake | 별도lane의 새 native 반환 | PR206 정보 인계 | 세 저장처metadata 확인, 원시SHA재검증은미수행 |

이 문서와 JSON은 이번에 수행한 조회/읽기의 근거다. 실행 상태, 과학적 수지, 수치 수렴, 원시 바이트 검증을 서로 대신하지 않는다.
