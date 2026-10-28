# bass_cr 교차-bin 예산 frontier: 중단 노드 마감

2026-10-29 KST. Unit CR_HL_CROSS_BUDGET_FRONTIER_V1. 원본 bdc7bf6f4e9cc94d68c32e1752c62de5f809b0bf의 미완료 연구를 별도 브랜치 research/cr-crossbudget-closeout-20261029에서 마감했다. 과학 수용 범위는 유한 유리수 모형의 C<=c 상부 frontier 및 완전한 primal-dual 증명서다. 독립 최종 검토 PASS_SCOPED, 잔여 지적0.

## 결과와 의미

낮은 에너지 원자 총 marginal을 L, cross-bin 예산 c 이하에서 허용된 high-low 최대 pairing 질량을 M(c)라 하면 정확한 총 double-event 상부 frontier는 d_max(c)=[L+M(c)]/2다. 최적 high-low flow 뒤의 각 low 잔여를 대각 사건 r_l/2로 채우고, 각 high 잔여는 single로 남기면 모든 원래 marginal을 보존하면서 상계를 달성한다. THEORY.md와 PROOF_AND_CONVENTIONS.md에 증명, dual, 차원, c>=0 및 경계 조건을 담았다.

K=4eV, 네 marginal이 각각1인 예제에서 0<=c<=2이면 M=1+c/2와 dmax=3/2+c/4다. c1에서 이전 necessary upper bound는2이고 실제 최대는7/4이므로 차는1/4다. 이 결과는 이전 outer facet만으로 충분성을 주장할 수 없는 구체적 사례를 준다. 일반 LP duality의 신규성을 주장하지 않는다. 문헌 원전 비교는 LITERATURE.md를 따른다.

## 구현과 실제 검증

수정한 API는 모든 경로에서 HL 사건, low diagonal, high singles 및 원자별 dual 가격/별도 budget multiplier를 반환한다. 타입검사 순서, 이름 충돌, hard size ceiling, 직접 테스트 수집, python-O에서도 살아 있는 증명서 검증을 교정했다. 추가 독립 검토에서 발견한 질량0 원자의 전체 그래프 dual 문제도 가격1의 비용0 확장으로 수정했다.

| 검증 | 실제 결과 |
|---|---|
| 별도 agent의 구성적 증명 검토 | 수용 |
| Wolfram의 별도 full-event 정확 LP | 5 budgets 모두 일치 |
| 최종 직접 Python 테스트 | 15/15 PASS |
| 독립 full-event LP formulation | 16/16 fixtures 일치; primary와 SymPy backend 공유 |
| python-O adversarial/zero-dual 검사 | 2/2 PASS |
| 의도한 사전 교정 실패 | 2건 실제 재현·원본 로그/비용 보존 |
| 최종 별도 code-review agent | PASS_SCOPED, 잔여0 |
| 저장된 정확 결과 그림 | 생성 후 직접 시각 검사 완료 |

최종 실행 source SHA256: frontier.py833978bc2c7b8a1a69955643aa461e2c52625dba206a943f6f931fb3a0aef46d; test_frontier.py8eee8f1f1bcbdc6479b10e826965f748991cca2dffcdcc51c1f8b738d62d575e. 실제 명령/환경/종료코드/각 버전은 evidence/EXECUTIONS.json이 관리한다. Python3.12.14, SymPy1.14.0, mpmath1.3.0이다. 기존 sympy PACKAGE_MISSING과 설치 회복, 게시 도구의 syntax/output 및 Dropbox source-fetch 오류는 별도로 보존했다.

## 진척도와 조사 범위

중앙 정본은28/88, 별도 REI working33/88이다. 이번 보조 노드는1/1이며 중앙 증가분0이다. 이론 R1-R10 및 코딩 C1-C10의 현재 receipt/완료 수는 STAGE_LEDGER.json과 publication/FINAL_RECEIPTS.json을 따른다. 마지막 단계의 자체 ACK는 postcommit 근거라 해당 stage ZIP에 소급 삽입하지 않는다.

관련6repo의 조사 당시1,275 branch refs, 최신 관련 PR50개, 필요한 원문 및 bass_cr 대화 단서/백업 검색을 대조했다. 모든 branch의 모든 파일·과거 PR 전체·비공개 대화 전체를 열람한 것은 아니다. 조사 중 새 REI figure STATE까지 갱신했다. 중앙 DAG blob이 유지되어 기존 과학 완료 수와 SHA256 근거를 재사용했다. 이번 결과에 필요한 실제 물리 kernel/source 입력을 새로 공급하는 변화는 확인하지 못했다.

## 자원과 백업

새 local scientific allowance60CPU-s 중 실제 기록9.071556933CPU-s를 사용했다. 실패2건을 포함한7회 과학 실행이며 native/새 ODE 실행0이다. remote Wolfram kernel 보고 CPU0.035589s는 별도다. metadata/package/provider/원격 CPU는 UNKNOWN_NOT_ZERO이며 전체 서비스 hard cap을 주장하지 않는다. PR118의 기존>=20.45/20CPU-s 실패와 HOLD를 그대로 보존한다.

각 단계의 실제 Git commit 및 Google Drive/Dropbox 응답, archive 크기/SHA256/CRC/member 검증을 publication에 남겼다. R05 Dropbox 첫 FETCH_FAILED는 같은 불변 원본의 재시도로 회복했으며 성공 ACK는 R06 이후이므로 모든 백업이 다음 단계 전에 끝났다고 표현하지 않는다. 이번 checkpoint의 원격 원본 전체 재다운로드 검증은 NOT_RUN이다. 과거 PR116/118 백업을 이번 단위의 백업으로 세지 않는다. SVG는 Git에, PNG는 ZIP에 포함한다.

실제 physical K, exclusive He kernel, donor/partner work, stopping 및 full physical native25는 여전히 별도 입력·연구 의무다. 중앙 N4/N5 partial 및 N6/N7 predecessor gate는 유지한다. 다음3개 확장 노드와 의존성은 NEXT_DAG.json, 복사 가능한 재개 지시는 HANDOFF_KO.md다.
