# bass_cr 2026-10-29 연구 재개: 원본 native K3 검증 + 일반 cross-budget min-cost flow

## 요약 및 권위

기준은 `cosmosapjw-quantum/bass_cr` Draft PR120, HEAD `5a8e4ac85a19151a3f9625c91d8e87b38f7a32e7`. 새 독립 브랜치는 `research/cr-generic-budget-ssp-20261029`이며 부모·main·타 소유자 저장소는 변경하지 않는다. 기존 PR119의 finite cross-budget frontier는 재검증 없이 재사용했다. 원본 PR116의 조건부 PHYS02 He 원자 source를 다시 확보한 뒤, PR120에서 미실행이던 **Python native** 계산을 실제 수행했다. 추가로 임의의 bin 배치에서 exact-rational min-cost flow로 전체 cross-budget frontier를 구성하는 새 이론과 reference code를 작성했다.

**중앙 DAG 28/88, delta0; 확장 DAG 0/3.** 새 작은 정확 reference 보조 결과 1/1 (제한적), 이번 R/C workflow 18/20. R6/C9의 서로 다른 작성자 심사는 도구가 노출되지 않아 NOT_RUN이다. 새 산출물의 보존/게시 여부는 별도의 실제 영수증을 따른다.

## 원본 입력 복구와 실행

Drive에서 PR116 SOURCE ZIP `BASS_CR_HE_JOINT_REGION_SOURCE_20261028_98174c29b984.zip` 4,690,891 B, SHA256 `87ddb7718d37895c3842b710a2af4f6419ffbc8ea38d0a55e0b1093217876311`를 받아 266 ZIP members CRC PASS. 내부 원본 `ATTRIBUTION_ARRAYS.npz` 233,050 B, SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`를 정확하게 추출했다. Python `load_pr116_npz`가 확인한 3201원자 digest `2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690`는 이전 결과와 동일하다. 생성 source로 대체하지 않았다.

Python3.13.5/NumPy2.3.5/SymPy1.14.0의 `native_budget.py`를 원본 NPZ에 직접 실행했다. 315 same-bin, 526 cross-bin, 합계841 positive HL event; 정확한 N,L,S,M,R 및 c=0,R/2,R의 dmax와 primal-dual gap0가 이전 Wolfram source-pinned 결과와 일치한다. Native CLI measured CPU user6.82+sys0.07=6.89초, peak101028KB, exit0. 기존10/10 native tests CPU11.80초 PASS. 독립 구현 `verify_compact_witness.py`는 compact source-locked primal의 3201원자 marginal, 841 energy/bin supports, 두 0/1 Hall dual의 102831개 허용 HL edge 제약을 모두 검사하고 exact objective S/M 일치를 확인했다. 측정 CPU4.08초. `NATIVE_WITNESS_COMPACT.json`과 원본 raw NPZ를 함께 보존한다.

## 새로운 일반 정리

정확한 source-independent 조건부 finite high-low matching에서 cross-bin edge cost를 1, same-bin을 0으로 둔다. 고정된 high-low 총 사건량 m에 대한 최소 비용 C_min(m)을 min-cost flow로 구하면 M(c)=max{m:C_min(m)<=c}. C_min은 연속·비감소·볼록 조각별 선형이고, 정확 SSP의 잔여 최단 augmenting path 비용 k는 비감소 정수이므로 M(c)의 양의 증가 구간 기울기는 1/k이다. 이 문제의 전체 double-event 상부 frontier는 dmax(c)=(L+M(c))/2로 환원된다. 증명, 경계조건, 단위 및 원래 모든 atom에 대한 LP dual은 `THEORY_GENERIC.md`를 따른다.

10-atom K=10 합성 예제의 비용/최대 HL 질량 절점은 (c,M)=(0,5),(3/2,13/2),(5/2,7),(4,15/2). 기울기 1,1/2,1/3,0. c=5/2에서 과거 필요조건 상계 M<=15/2는 실제 M=7보다 1/2 느슨하다. 전체 dmax의 차이는 1/4. Wolfram 독립 18-edge exact LP에서 c={0,1,3/2,2,5/2,3,4} 모두 일치했다. 기존 PR119 4-atom 반례의 Wolfram 6-point LP도 일치했다. 일반 LP/min-cost flow 알고리즘의 신규성을 주장하지 않는다.

## 코딩과 실제 테스트

`generic_budget_flow.py`는 exact Fraction residual graph, Bellman-Ford shortest augmenting path, negative reverse costs, convex budget interpolation, original atom/zero-mass 포함한 SymPy exact LP dual을 구현한다. 기존 12-atom small SymPy primal을 확대하는 방식이 아니라, **독립적인 exact SSP primal**을 구성했다. 원래 전체 사건을 직접 변수로 둔 다른 SymPy LP와 75개 무작위 사례, 10-atom 4사례, 기존4-atom 6사례를 비교했고 정확 일치했다. Generic 6/6 unit methods, native 10/10, combined python -O 16/16 PASS. 합성 3201-atom topology는 이전 PR120 테스트를 새 환경에서 통과했다.

구현 한계: 현재 Bellman-Ford SSP reference는 최대14 atom, 100 HL edge, O(A V E) 정확 연산 및 모든 증분 flow snapshot 저장. 이는 **일반적인 3201-atom 생산 solver가 아니다**. K3 native special case는 원본 source에 대한 빠른 독립 경로로 유지된다. 원래 source로 새 general SSP를 실행하거나 production performance 개선을 주장하지 않는다. 관측량/He 실제 물리율 계산도 미실행이다.

## 관련 저장소 최신성 범위

이번 턴에서 7개 관련 저장소의 최신 PR 6건씩(최대42건)과 선택 커밋 메타데이터를 조회했다. BASS#240/241, BASS_HE#105, REC#155, WU#156, REI#261, vigilode#103/104를 추가 확인했다. BASS_HE#105는 EXFOR angular conditional envelope이나 실제 exclusive He event normalization을 공급하지 않는다. WU#156은 HD 반응 특정 상태의 105K rate이며 이 CR He source에 직접 주입할 수 없다. REI#261의 UVB derivative, vigilode#104의 quadratic stage solver, BASS#240/241의 tabulated geometry certificate도 CR의 실제 K/kernel/donor를 채우지 않는다. 모든 비공개 대화와 모든 branch의 모든 파일을 열람했다고 주장하지 않는다. 연결된 과거 bass_cr 대화의 이전 handoff와 이번 현재 GitHub/백업 원본을 분리했다.

## 자원·검토·보존

이번 턴 Python/C++ 실행 프로브: `PYTHON_PASS`, `CPP_PASS`. 사용자 요청에 따른 새 범위에서 실제 유한 명령 실행과 명령별 timeout을 적용했으나 **첫 실행 이전에 aggregate hard cap을 고정하지 않았으므로 전체 CPU 예산 PASS는 주장하지 않는다**. 기록된 여러 명령의 local CPU 합계는 최소93.12초이며, 그 외 보고서/메타데이터/원격 Wolfram·provider CPU는 UNKNOWN_NOT_ZERO다. 이전 PR118 >=20.45/20 CPU-s resource FAIL은 그대로 보존한다.

Native subagent 도구는 현재 목록에 노출되지 않아 R6/C9 distinct-author NOT_RUN. Wolfram은 독립 계산 엔진이고, 독립 LP/검증 스크립트는 서로 다른 알고리즘이지만 **다른 작성자 심사를 대신하지 않는다**. 이론·코딩 18/20, 새 auxiliary small-reference 1/1 PASS_SCOPED, extension0/3, 중앙28/88. 물리 K, exclusive He kernel, donor/partner work, stopping, physical native25, L4 및 production 모두 HOLD.

개별 단계의 게시/백업은 과학 실행 뒤에 생성한 retrospective stage records다. 단계별 실시간 저장이 있었던 것처럼 소급 표기하지 않는다. `STAGE_LEDGER_GENERIC.json`, `stages/*.json`, detached `POST_PUBLICATION_RECEIPTS.json`에 실제 Git/Drive ACK와 실패를 구분한다. 원본 SOURCE ZIP의 이중 원격 바이트 검증은 각 provider의 실제 ACK와 GET이 확보된 경우에만 별도 표기한다. Dropbox Paper 텍스트 인계는 binary archive 이중백업으로 계산하지 않는다.

## 다음 조치

원본 NPZ Python native 부재는 이번에 해소했다. 다음 실질 연구는 (1) 다른 작성자의 R6/C9 심사, (2) 일반 cost-budget flow의 scalable potentials/cost-scaling solver와 원래 atom 증명서, (3) 실제 exclusive He kernel/physical K/clock/energy-owner의 소스 확보를 병렬로 다루는 것이다. 소규모 일반 SSP의 성과를 물리 production으로 승격하지 않는다. 전체 재현 명령은 `REPRODUCE.sh`, 재개 프롬프트는 `HANDOFF_KO.md`를 따른다.
