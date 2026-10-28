# 조사 자료의 원본과 게시 경로

이 디렉터리는 새 단위 CR_PHYS02_HE_EVENT_UNION_V1의 실제 조사와 재사용 근거를 보존한다. 이전 전체 목록의 원 tool 응답은 호스트 리셋으로 손실됐다. 그 관찰은 HISTORICAL_SURVEY_RECONSTRUCTED_KO.md에 복원했고, 리셋 뒤 새로 읽은 응답은 fresh/에 구분했다. 복원 파일의 새 SHA는 손실된 파일의 SHA가 아니다.

CURRENT_OWNER_SUMMARY_KO.md는 관련 7 owner와 중앙의 현재 선택 재조회를 설명한다. PRIMARY_SOURCE_MAP_KO.md는 리셋 전 실제 읽은 primary 자료의 범위를 복원하며, 이번 게시 문서 준비 중 새 문헌 검색은 하지 않았다. 수학 전체는 ../theory/THEORY_KO.md에 있다.

RECOVERED_SURVEY_RECEIPT.json과 RECOVERED_INTAKE_FILE_MANIFEST.json은 복원 당시 원 위치인 /workspace/scratch/d85f8e5ba8ad/next_work/intake/의 경로 체계를 그대로 보존한다. 게시 경로와의 대응은 RECOVERY_COPY_RECEIPT.json에서 읽는다. 그 대응표는 실제 현재 로컬 파일을 byte-identical하게 복사한 결과이며, 역사적 손실 응답의 identity를 대체하지 않는다.

fresh/CENTRAL_DAG.json은 중앙22a99cb9b1691274e74c122d54521be4f2f51ba5의 실제 original full GET이다. 중앙28/88, 88 nodes/17 edges, CR delta0을 유지한다. Preflight·단계 Git 게시·backup 영수증은 root의 각 단계 기록에 별도로 결속한다. 이 디렉터리의 문서 작성이나 파일 복사 자체는 Git 게시 또는 backup 완료를 뜻하지 않는다.
