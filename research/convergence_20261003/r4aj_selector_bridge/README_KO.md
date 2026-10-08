# BASS_CR R4AJ

이곳의 새 결과는 selected-1s와 옛 rank5 관측량의 차이, 저장된 단일중심 행렬의 gap≥0.373Eh, 동일한 두 중심 reference의 1s 공진, 그리고 공진쌍을 유지한 조건부 bridge-error 구현이다. 실제원자bridge오차상계는아직null이다.

먼저 REPORT_KO.md와 FINAL_STATE.json, 다음 DERIVATION_KO.md 및 NEXT_DAG.json을 읽는다. 직전보고전체한국어판은 docs/R4AI_PREVIOUS_REPLY_KO.md다. CODEX_HANDOFF_KO.md에원격전달및외부실행절차가있다. `python verify_release.py .`는파일bytes만검사하며과학계산을하지않는다.

새시험72건,새read-only검토33조건을완료했다. oldscientificsuite/shifted/memoryprepare/M9/center/oldR8재실행0이다. 로그를다시돌려완료횟수를늘리지않는다. 소스함수는재사용가능하나새scientificscope에는별도계약이필요하다.

parent/R4AI.zip은불변이전전체결과와m64runtime을자급한다. 통합patch는R4AI기존85개와새R4AJ파일을한번만추가한다. 원R4AIpatch와중복적용하지않는다. 현재정확Git전체history없이가짜bundle을생성하지않았다.
