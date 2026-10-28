# C10 WU owner 변경 검토

**PASS_FIXED_CR_ENERGY_SUM_SCOPE_UNCHANGED — 15/15 metadata checks PASS.**

고정 비교: `0e6282010665bc9075e073cfd144c226d29e449b` → `bb960c3c293c34b4567873fb4328143b16301e59`. 한 commit의 R14 S01 등록이다. 변경은 AGENTS 및 새 `research/provider_registry_molecular_r14_20261028/` 파일 13개에 한정된다. 기존 과학 파일은 변경하지 않았다.

## 새 owner 단위와 현재 상태

- Identity: `WU_QUADRATIC_FORCING_R14`. R1/C1만 완료하여 **workflow2/20**, local DAG **27/44**이다. 새 theory/code 노드는 둘 다 OPEN이며 physical_admission=false이다.
- 실제 R14 DAG의 첫 42개 객체를 저장된 실제 R13 DAG와 대조하여 모두 동일함을 확인했다.
- 새 AGENTS blob은 `b69275210a3911564a746b3763e8f8cdfda6cef8`. 이전 `923a71ed8416d03077e0e22923512f2d9dc980ef` 본문 전체가 정확한 suffix로 보존되고 R14 안내만 앞에 추가됐다.
- 범위는 whole-domain pointwise-nonnegative quadratic forcing, exact rational preprocessing, positive cubic Bernstein convolution, global forcing memory와 signed scalar propagation이다. 실제 physical source binding은 별도 입력 전제이다.
- Primary/reference/CAS는 모두 **actual_runs0, NOT_RUN**이다. 각각 한 번의 새 allowance가 있으며 primary/reference는 각 CPU90s·wall120s·1GiB, CAS는 wall30s이다. 이는 **WU R14 자신의 새 계약**이다.
- 소스 publication index에는 completed dual backup0, actual ACK0이 기록된다. S01 자신의 ACK는 후속 외부 기록이므로 여기서 이후 전달 성공·실패를 추정하지 않았다.

## 물리·이전 예산·실패 경계

Actual HD reactive array와 named consumer/density/clock은 INPUT_PENDING, HH_R10 OFF, production NOT_ISSUED, L4false, central/physical delta0이다. Native v는 UNSPECIFIED, missingness는 MISSING_NOT_ZERO, TIQM/SQM 구분을 유지한다.

R13/R12/R11/R10/R9/R8/R7/R6/PHYS91의 primary/reference/CAS 잔여는 모두 0/0/0이며 old allowance increase0, old science replay0이다. Global remaining과 full historical CPU는 null이다. R13의 311/125/8408 및 CPU1.334749, qualified CAS25zero+Power::infy3/General::messages 원인 미확정, F01/F02 originalbytesNOT_PRESERVED/F03 최초 postprocessing 실패와 교정은 역사 그대로 남는다. R8의 726/727+1FAIL과 별도24/24, R10–R12의 기존 실패·qualified CAS·provider originalGET NOT_RUN 기록도 새 원장에 보존된다. 새 R14의 빈 scientific_failures 배열은 이 과거 실패를 지우지 않는다.

R13 scientific S09 `37db6e1fdb915b85d7547b77e3c01fa15218b193`, 57-file payload SHA256 `aed8a6d7e58889de248ee88f75c2a46a7418462f4e3908393d72b64e908c6563`을 입력으로 재사용한다. 새 실행 결과로 대체하지 않았다.

## CR에 대한 판정

이번 등록은 CR의 실제 energy cap K, exclusive atomic He kernel, C, 고정 source/state/clock/density, same-state consumer 또는 예산을 바꾸지 않는다. WU의 `A=K+wH`에서 K는 기존 generator이며 CR pair-energy cap K를 공급하지 않는다. 다른 owner의 새 허용치는 CR로 이관하지 않는다.

Root가 고정한 CR charge13.861533CPU-s와 science_closed=true, additional science allowance0을 보존한다. 이미 봉인되고 양쪽 original R3를 통과한 SOURCE는 열어 재생성하거나 변경하지 않았다. Central66ef 관측은 기존 검증을 재사용했으며 별도 query를 하지 않았다.

## 근거와 검토 범위

[고정 비교](https://github.com/cosmosapjw-quantum/WU088_HH/compare/0e6282010665bc9075e073cfd144c226d29e449b...bb960c3c293c34b4567873fb4328143b16301e59), [현재 AGENTS](https://github.com/cosmosapjw-quantum/WU088_HH/blob/bb960c3c293c34b4567873fb4328143b16301e59/AGENTS.md), 새 R14 CONTRACT/EXECUTION_LEDGER/WORKFLOW_RECORD/REPORT/DAG/PUBLICATION_INDEX의 실제 원문을 읽었다. 각 원문 URL·Git blob·bytes·SHA256과 실제 응답 pin은 `C10_WU_DELTA.json`에 있다.

이는 고정 head의 선택 변경 검토이다. AGENTS의 해당 owner 사용자 요청 서술을 개인 대화에 직접 접근한 증거로 취급하지 않는다. 전체 history 재감사, 새 global census, mutable-head polling, provider 또는 다른 owner query를 수행하지 않았다. 외부 mutation0, science execution0, metadata CPU null이다.
