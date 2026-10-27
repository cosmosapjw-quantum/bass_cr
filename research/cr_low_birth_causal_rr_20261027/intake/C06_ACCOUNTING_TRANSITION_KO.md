# C6 중앙 집계 관찰의 전환

R01–C05의 실제 게시·백업 당시 중앙 programme은27/88이었다. 이15개 영수증은 당시 관찰 그대로 보존한다. C06 최초 실행 전 preflight도152b82cac23f에서27/88을 관찰했으며 C06_INITIAL_27OF88_PRESERVED.json으로 남긴다.

C06 repair 직전 중앙 HEAD가74aff0740d1812c732466563a9c66108a3a4d8fd로 변경되었다. 실제 DAG의 기존 B3h node40이 COMPLETE_SCOPED_NATIVE_EFFECTIVE_H_FINITE_TRANSACTION으로 바뀌었고 해당 owner-return original_DAG는27→28/88, foreign effect+1을 명시한다. 다른87nodes와17edges는 그대로다. 이번 CR의 효과는0이며 PR236의32/88을 더하지 않는다.

첫 C06_REPAIR_V2 probe에는 최신 HEAD를 읽고도 helper의 고정27 상수가 남은 metadata 오류가 있었다. 해당 raw receipt를 C06_REPAIR_V2_STALE_FIXED_COUNT_PRESERVED.json에 보존했고, helper를 실제 HEAD+DAG SHA에 결속한 count baseline을 요구하도록 교정했다. 같은 단계의 수정 preflight와 최종 C06 preflight는 실제28/88을 기록한다. 이전 과학·실행·백업 결과의 의미는 바뀌지 않는다.

C06_REPAIR_CONTEXT.json의27은 새 중앙 변경을 읽기 전의 계획 metadata이며, 최종 단계 current count의 권위는 수정 preflight와 게시 영수증이다. 최신 HEAD 또는 DAG hash가 다시 바뀌면 count review 없이 다음 preflight가 통과하지 않는다. 이 전환은 과학 결과나 global physical completion의 승격이 아니다.
