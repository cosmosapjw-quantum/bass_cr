# physmath-research-loop: C21N 수행 기록

현재 사용자 요청의 경계는 최신 반환 수용 → 다음 이론·경량 코딩 → 가능한 구현 게시 → 백업·실행 인계다. 기존 81/125 science를 재실행하거나 별도 대규모 benchmark를 시작하지 않는다. 다음 표는 실제 수행 내용을 skill의 단계 지도에 대응시킨 것이며, 모든 단계의 가능한 범위를 전부 수행했다고 선언하는 체크리스트가 아니다.

실행 초기에 읽은 사용자 skill과 정책을 적용했다. 게시 준비 중 runtime catalog에 physmath-research-loop 1.3.0이 새로 노출되어 main, STAGE_SELECTION, POLICY_INTEGRATION, STAGE_GUIDE_KO, SUBAGENT_MODE를 읽었다. 이 버전 변경은 연구를 다시 시작할 이유가 아니다. 현재 단위의 R10/C10 마감만 계속하고 새 cycle은 시작하지 않는다. 원 C21F–K 역사와 HOLD는 보존한다.

## 이론 지도 R1–R10과 실제 근거

| 단계 | 이번 단위에서 수행하거나 재사용한 범위 | 근거 |
|---|---|---|
| R1 목표·계약 | non-tilted collisionless LRS, 원40상태, 초기 상쇄 응답 | RESEARCH_CONTRACT_KO.md |
| R2 문헌·기존 성과 |7repo refs·NCP98·백업 intake, SciSpace/Exa 원전 식과 서지 | intake/, theory/evidence/ |
| R3 정합성 |Frobenius/half, signed Delta p/3, H_t와 κ 단위, 서로 다른 source family | theory/MASS_SHELL_DERIVATION_KO.md |
| R4 후보 탐색 |기존 shear-memory, finite-L8 표현, 직접 mass-shell derivative, 설명용 β표현을 비교해 현재 국소 응답을 선택. 별도 발산 탐색 campaign 없음 | EXTERNAL_REUSE.json, 이론 §2·5 |
| R5 구성적 유도 |conserved packet 도함수, 직접 mass-release 합, actual-epsilon 초기 shear jet | 이론 §4–6 |
| R6 독립 심사 |source/algebra를 별도 agent가 검토; 동일 source를 새 독립 모델로 세지 않음 | checks/INDEPENDENT_PHYSICS_REVIEW* |
| R7 경량 검산 |실제 CAS2건,12packet/3direction/7jet focused,기존125 정적 적용 | checks/, analysis_mass_shell125_v2/ |
| R8 결과 판정 |첫 저장점2.12%,표시창끝15.84%로 1%/전체창 대체 주장 미채택 | theory/RESULTS_KO.md |
| R9 계산 연결 |직접 합 구현, 부호 보존, zero-norm derivative 회피, 새4입력 준비 | mass_shell_derivatives.py, prepared_offgrid4/ |
| R10 정리·체크포인트 |보고서·DAG·게시·백업·다음 인계. publication/backup는 실제 ACK로 확정 | REPORT_KO.md, 후속 closeout |

새로운 strong no-go theorem은 제출하지 않았다. 지정된4case의 이산 저장점에서 관측한 counterexample가 지지하는 제한만 기록했다. 연속 시간 remainder, 전역 정확도, 장기 안정성의 증명은 미확립이다.

## 코딩 지도 C1–C10과 실제 근거

| 단계 | 이번 단위에서 수행하거나 재사용한 범위 | 근거 |
|---|---|---|
| C1 기준 설정 |원PR147/C21M source·FP64·출력·tolerance 고정 | RESEARCH_CONTRACT_KO.md |
| C2 코드·수식 조사 |고정 constructor/RHS/분포·실제 raw binding, 외부ACCEL01·HH75 차별성 | intake/, EXTERNAL_REUSE.json |
| C3 알고리즘 설계 |A-independent constructor 준비, 연산·reduction 순서 보존, 직접 derivative | OPTIMIZATION_DECISIONS_KO.md |
| C4 병렬화·실행 설계 |worker-local 준비, 기존 bounded dispatcher 재사용, disk/inode와 completed125 guard | OPERATIONS_KO.md |
| C5 구현 |factory·builder·derivative·새runner·후처리·입력준비 | 새 C21N source files |
| C6 소프트웨어 검증 |constructor4그룹, fake3case의 새 운영3그룹, 변경wait분기 추가검사. 실제 오류·실패 source 보존 | checks/prepared_momentum_v2.json, ops_final_scope.json |
| C7 물리 검증 |원 moment/fields/RHS 동등성, energy identity, 실제 offset, initial positivity/normalization/constraint | checks/, analysis_mass_shell125_v2/, prepared_offgrid4/ |
| C8 수치 정확도·성능 |375저장상태의 source bytes·국소도함수 residual을 검증. 시간/격자 수렴 campaign와 performance benchmark는 NOT_RUN; global bound null | scoped receipts, REPORT_KO.md |
| C9 독립 코드 심사 |준비 계층 AST·source·FP순서, 운영 delta와 두 그림의 별도 검토 | INDEPENDENT_*REVIEW* |
| C10 배포·인계 |offgrid4 certificates와 실제plan-only, content/doc분리,3providerACK와 실행명령 | prepared_offgrid4/, 후속 closeout |

기존 자원 suite나 전체 ODE를 반복하지 않았다. 반복 quadrature 호출 제거는 구조적으로 확인했지만 elapsed/RSS 향상은 미측정이다. 첫 test manifest 오류와 그림 label 오류는 구체적인 수정 한 번과 좁은 재검증으로 닫았다. 최종 운영코드의 wait guard3줄도 그 분기만 검사했으며 첫3그룹을 최종 source에서 재실행했다고 쓰지 않는다.

## 실제 delegation과 종료 경계

Native collaboration의 backup_intake, external_results, theory_literature 세 task를 사용했다. Intake/원전/구현의 파일 소유권을 나누고, 검토는 준비 계층·물리·운영·그림의 서로 다른 질문으로 한 번씩 나눴다. Parent는 결과 파일과 원 식을 읽고 source hashes·실제 그림을 확인하여 수용했다. Review-of-review나 새 recursive audit tree는 만들지 않았다. 이 실행을 후반에 추가된1.3.0의 별도 skill-bound capability probe를 수행한 것으로 소급해 기록하지 않는다.

국소 이론·구현·scoped 검증·기존125 분석을 마감하고 publication/backup evidence를 추가한다. Off-grid4의 실제 실행은 NOT_RUN이며 새로운 NCP 반환이 먼저 오면 원 source/input/raw를 수용하여 중복 실행하지 않는다. NCP에는 host별 절대경로·현재 공유 자원 확인과 명시적 새 입력 실행만 남긴다.
