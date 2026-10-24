# R1–R10 / C1–C10 실행 장부

이 표는 선택한 C23E 한 연구 단위에 대한 완료도다. 전체 물리 목표의 백분율은 정의하지 않았고 global_completion_fraction=null이다. 과학 완료와 외부 게시/보존은 독립 축이며, 최종 provider identity는 PUBLICATION.json/BACKUP_RECEIPTS.json의 실제 영수증으로 갱신한다.

현재 과학 판정: COMPLETE_SCOPED; 독립 PASS_SCOPED; delivery repair1회 CLOSED. 표의 PENDING_S는 출판 전 checkpoint 의미이며 원 raw의 과학 상태를 바꾸지 않는다. B_LOCAL은 로컬 create-only 보존과 기존 C23D R3 영수증 재사용이다.

| 단계 | EXECUTION 및 실제 근거 | PUBLICATION | BACKUP | DAG/완성도 |
|---|---|---|---|---|
|R1 위치·계약|7repo1310heads/845PR,AGENTS·actualrefs·budget,V2동결|PENDING_S|B_LOCAL|C23E 범위 확정 COMPLETE_SCOPED|
|R2 근거·재사용|C23B/C22A/C23C/REI180–181/WU79 원문, SciSpace·Savin·VF·Grackle 비교|PENDING_S|B_LOCAL|중복V1 실행 전 취소; source map COMPLETE_SCOPED|
|R3 주장·전제|실증D와H-equality·RR조건부근사·기존결과 구분|PENDING_S|B_LOCAL|fullN5/Milne OPEN 유지|
|R4 표현 탐색|전체재적분/oldatomfilter/positiveboundaryupdate를 식으로 비교|PENDING_S|B_LOCAL|boundaryupdate 선택 COMPLETE_SCOPED|
|R5 구성적 유도|Gamma/K/A transfer, 동일potential energycycle, pool방정식|PENDING_S|B_LOCAL|THEORY 및 CAS COMPLETE_SCOPED|
|R6 독립 검증|FreshAstra 정적식·단위·경계·raw·identity 검토|PENDING_S|B_LOCAL|PASS_SCOPED; material0|
|R7 판별 계산|Wolfram residual0;3z band/새Dquad/18point상태|PENDING_S|B_LOCAL|104checks PASS;ODE0|
|R8 판정|root NUMERICALLY_CHECKED_SCOPED; strongno-go 주장없음|PENDING_S|B_LOCAL|C23Echild COMPLETE_SCOPED;parent PARTIAL|
|R9 정식 연결|THEORY,FROZEN,결과/claim 및 source interface|PENDING_S|B_LOCAL|구현과식 결속 COMPLETE_SCOPED|
|R10 종료·재개|다음Dsource qualification,별도stopping,누적예산 인계|PENDING_S|B_LOCAL|배송 진행;physics loop 종료|
|C1 baseline|실제4a0bbc0e,저장Hmoments,새D목표·허용오차|PENDING_S|B_LOCAL|기존campaign 미재실행|
|C2 식–코드|d_binding 및 pinned source/rate/data 연결|PENDING_S|B_LOCAL|입력 identity PASS|
|C3 수치 설계|positiveB band GL,독립logE quad,사건별fsum|PENDING_S|B_LOCAL|수치/원전/모형오차 구분|
|C4 자원 DAG|actual8CPUquota,worker8/coordinator0,thread1,lease/create-only|PENDING_S|B_LOCAL|실행 admission 기록;NCP0|
|C5 구현|source/validator/dispatcher 및 exactrelativeinputs|PENDING_S|B_LOCAL|완결된 local adapter|
|C6 구현 검증|104primary 및29deliverytargeted,영입력/누락/불일치거부|PENDING_S|B_LOCAL|PASS;수치반복0|
|C7 과학 검증|8핵종/전하,PI/RR/CX potential,두전자pool 보존|PENDING_S|B_LOCAL|COMPLETE_SCOPED|
|C8 수치·재현성|band5.63e-16,Dquad1.75e-15,원raw보존,CPU2.161932s|PENDING_S|B_LOCAL|pairedspeedup/globalbound 없음|
|C9 독립 검토|freshAstra1pass,R1경로/import수정1회,재검토CLOSED|PENDING_S|B_LOCAL|PASS_SCOPED;추가review없음|
|C10 판정·인계|실행/배송source분리,source_snapshot,canonicaldelivery 계획|PENDING_S|B_LOCAL|과학완료;게시/백업영수증 진행|

## 유지한 범위

C21O prescribedUV/T/photo+CaseA→ne→Thomson, REI220/BASS180 mirror PASS_SCOPED raw4, 최초127JSON실패/재적분, VigilODEP02C6FAIL, HE85/REI219미완료campaign을 보존한다. Full conversations UNAVAILABLE, 접근발췌AVAILABLE_PARTIAL, 외부live runtimeUNOBSERVED, 원핵반응PNG NOT_RECOVERED_NOT_READ. Drive의 기존UNKNOWN_NO_ACK를 재시도 성공으로 간주하지 않는다.
