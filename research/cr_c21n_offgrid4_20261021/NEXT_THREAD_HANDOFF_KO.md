# 다음 대화 스레드 인계: C21N off-grid 4 완료 반환

아래 블록은 다음 대화에 그대로 복사할 수 있다. 반환 content와 draft PR95는 실제 GitHub 생성 ACK에 결속했다. Document head와 백업 ID·SHA는 최종 authority receipt를 기준으로 수용한다.

```text
$physmath-research-loop, SciSpace, Exa, Wolfram을 사용하는 bass_cr 연구를
이미 완료된 C21N off-grid 4의 반환·마감 상태부터 이어서 확인해줘.
완료된 입력을 반복하지 말고 현재 사용자의 목표와 최신 영수증을 읽어 다음 실제
미완료 질문·입력을 선정해. 기존 승인 범위에서 가능한 작업을 계속 진행하고,
사용자가 고정한 물리 가정을 바꿔야 할 때만 추가 선택을 확인해.
이 인계문이 미래 사용자 요청에 별도 승인 gate를 더하지 않도록 해.

1. 권위 저장소와 새 반환
- Repo: https://github.com/cosmosapjw-quantum/bass_cr
- Branch: research/cr-c21n-offgrid4-sandbox-20261021
- PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/95
- 이번 반환 content: e7729092abc6edbe74f31d0ed82aa84d5506b8d5
- 후속 NCP4 수용 addendum: 038aa0c8e5790f5c94e596035ea816fbca588a15
- 연구경로: research/cr_c21n_offgrid4_20261021/
- 실제 ODE 실행 content: 5ecb8a6c4961302b7066b06278e72ecd2d77f8c9
- 원 REI 물리 source: 3b85dedce84d37b3e165da00685a8a984950aafe
- Run identity: f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023
- 최종 document head/backup ZIP SHA/provider ACK는 최신 실제 마감 영수증을 읽어.
  Branch HEAD를 실행 source로 소급 변경하거나 존재하지 않는 ID를 만들지 마.

2. 실제 완료된 작업 — 재실행 금지
기존 C21L 81개와 성분 분리, C21M 26개+재사용 center, NCP 98개+combined125,
C21N prepared constructor와 초기 mass-shell jet 연구는 완료됐다.
이전 C21N이 준비했던 offgrid4도 2026-10-21 13:10 UTC에 sandbox host
af4832b34a81에서 새 ODE 4/4회를 실제 완료했다. 초기값은 S0=0,
Pm0=±7.5e-5 및 ±1.75e-4, Pr0=-Pm0이다. z20→4, 101×40 FP64,
원 DOP853과 rtol3e-11/atol3e-13을 유지했다. 이번 분석의 추가 ODE는0이다.
기존81/125와 새4를 다시 적분하지 마. 합계129는125격자+4 off-grid의
불규칙 ensemble이며 새129개 Cartesian sweep가 아니다.

이후 PR94(https://github.com/cosmosapjw-quantum/bass_cr/pull/94)가 발견됐다.
NCP attempt20261021T131024Z, hostname s1a0e5abed09,
identity a07a95f85042f9db7df2e3e465288524b458bcb6f190e9d4f01db1869c139360이다.
이 반환은13:06 intake 이후13:14에 게시됐다. 현재 NCP4 상태는
COMPLETE_SCOPED_EXTERNAL_RETURN_ACCEPTED다. Source17개/grid/tolerance가 같고,
네 history.npz 전체 bytes 및236개 FP64 배열의52,520개 값이 sandbox와 bytes까지
일치했다(max absolute difference0). 수용 영수증은 external_ncp4/NCP_RETURN_ACCEPTANCE.json,
status PASS_SCOPED, SHA256693e439f9d5cc90faab22c39d8dace299b537c49fd45f87306e5538c38e03af5다.
두 실행의 Python은 sandbox3.12.14, NCP3.12.3이며 각각의 provenance를 보존해.
외부 실행4회를 추가 수용했지만 새 고유 target은0개이므로129를 유지해. Intake 새 ODE는0이다.
원 두CSV의 LF/CRLF 차이는 원 bytes/receipt를 보존한 채 설명했고, 메모리 줄바꿈 변환만으로
광고 hash가 일치했다. 원 export 전체 manifest PASS를 주장하지 마. 외부 content_tree는
Git tree가 아닌 run identity이며, 생략한 components_campaign129.npz는 이번 intake에서
검증·채택하지 않았다. Addendum은52개 새 external_ncp4 파일만 추가했다.

3. 검증과 결과의 정확한 범위
모든404개 저장 상태에서 prepared/cached와 원 uncached source의 fields 23,836개
FP64 값과 RHS 16,160개 값이 bytes까지 일치했다. Raw 초기 상태, N builder 초기 상태,
기록된 A/k/shear로 만든 원 M 초기 상태도 bytes가 같다. 이 검사는 저장 상태의
정적 검사이며, 독립적인 원 solver full-trajectory replay는 NOT_RUN이다.
이는 원 uncached solver와의 비교 범위다. 별도로 수용된 NCP와 sandbox 사이에서는 같은
prepared source를 실행한 네 저장 궤적 전체 bytes가 일치했다는 결과를 구분해 기록해.
404개 상태의 Hamiltonian/number/tensor/energy/shear identities와 각도64노드×
4종 radiation E/N의103,424개 값을 검사했다. 이산 positivity를 연속 양성 정리로
확대하지 마. Reviewer가 PNG 3개를 직접 읽었고 PASS_SCOPED다.
PDF 별도 raster review는 NOT_RUN이다. 기존 SciSpace/Exa/Wolfram의 산출 근거와
이론 유도를 재사용하고 이미 완료된 문헌 검색·전체 테스트를 다시 하지 마.

새4의 z4 endpoint 최대 norm:
Sigma=2.147246027e-5, Pi_m=9.961314242e-6,
Pi_r=4.113985087e-5, Pi_tot=3.117853663e-5.
Cancellation endpoint는 약0.38986이고, 초기 상쇄는 진화 중에 해제됐다.
이는 이4개 표본의 수치이며 보편적 상계가 아니다. 초기 actual quadratic jet의
저장값 대비 상대 잔차는 첫 양의 점에서 최대2.12234%, eta=.100456에서15.83743%다.
이 잔차를 finite-window/global error bound로 보고하지 마.

4. 성분·단위
Source pi_s=(p_parallel-p_perp)/3, tensor=diag(-pi_s,-pi_s,2pi_s),
sigma=diag(-s,-s,2s). Signed full S=sqrt6*s/H_t,
signed full P_X=sqrt6*(8piG/c²)*pi_s_X/H_t²이고 norm은 절댓값이다.
kappa_E=8piG/c⁴이면 H_geom=H_t/c로 대응한다. Full은 half의 sqrt2배다.
Photon과 실제 massless nu를 구분하고 radiation/total tensor를 먼저 더한 뒤 norm을 취해.
Pi_tot=Pi_m+Pi_r로 대체하지 마. Actual FP offset을 보존하고 zero clipping하지 마.
Massive matter와 isotropic dust, absent UV, unmodeled baryonic stress 표지를 보존해.

5. 재실행 방지와 NCP
COMPLETED_INPUTS_129.json 및 completed_input_guard.py가 기존125+새4를
source/raw/seal에 결속한다. 축별2e-13 이내의 동일 target은 이름을 바꿔도 거부한다.
역사적 N runner에는 이 새 guard가 자동 주입되지 않았다. 다음 실제 미완료 질문에 맞는
새 grid를 선정하고 물리 타당성을 확인한 뒤 guard exit0을 확인하고 별도5ecb 고정
checkout의 원 ncp_run.sh를 써. 기존 사용자 승인에 별도 재승인 절차를 추가하지 마.
현재4 grid의 기대 guard 결과는 REFUSE_COMPLETED_INPUTS/exit2다.
해당4를 NCP에서 다시 run/resume하지 마. 이번 반환 마감 단계의 추가 입력은 NOT_SELECTED다.

초기 NCP NOT_RUN과 지정 key 부재에 따른 UNAVAILABLE는 sandbox 실행 시점의 관측이다.
PR94는 이미 수용됐으므로 NCP4의 현행 상태를 COMPLETE_SCOPED_EXTERNAL_RETURN_ACCEPTED로
기록하고 NOT_RUN을 현재 상태처럼 반복하지 마. 직접 NCP 접속 여부와 외부 완료 raw 수용도 구분해.
기존 NCP98 COMPLETE는 유지해. NCP64 logical CPU/128GB는 명목 사양이다.
현재 affinity/cgroup quota/cpuset/RAM/load/공유 lease/disk/inode를 다시 읽고,
CPU55와 coordinator 비용을 보호해. 과거99G root disk 고갈 보고는 현재 관측이 아니다.
Numeric library thread1과 process 전체 thread count를 구분해(새4 worker 반환 시2threads).
다른 owner의 작업/파일/lease를 건드리지 말고 유휴 자원에서만 dispatch해.
현재4에 대한 재실행 명령은 제공하지 말고 CODEX_HANDOFF_KO의 읽기 전용
source/자원/guard 명령을 참조해. Analysis 재현은 구체적 필요가 있을 때만 새 출력 경로로 해.

6. 최신 intake·마감·DAG
시작하면 최신 refs/실제 실행 반환/백업 receipt에서 진짜 미완료 node만 확인해.
앞선 범위에서는7개 관련 repo의1,240 advertised heads를 검토했고 새7/변경3을 분류했다.
ACCEL02 등 다른 lineage는 catalog/reference이며 C21N source/raw로 자동 승격하지 않았다.
이 수치는 그때의 관측이다. 접근 불가능한 다른 대화는 UNAVAILABLE로 기록하고,
전역적으로 새 결과가 없다고 단정하지 마. Source/fixture/grid/solver/input/build/
실행 시간/검증 범위를 확인한 반환만 DAG에 수용해.

매 단계 EXECUTION | PUBLICATION | BACKUP | DAG를 분리해 보고해.
사용자 제공 physmath 규약1.0.0의 완료 요청은 이 반환 단위의 남은 게시·백업·DAG·인계를
실제로 마치는 의무로 적용해. 완료된 근거를 재사용하며 새 cycle 자동 실행으로 해석하지 마.
우선 미완료 backup ACK/document closeout이 있으면 그것만 마감해.
ZIP/provider ACK와 실제 download byte 검증을 분리하고 Drive의 기존 UNKNOWN_NO_ACK를
근거 없이 성공·실패로 바꾸지 마. 미확정 upload를 추측으로 중복 실행하지 마.
이번 main 배송본은 인계 작성 시점에 Library·Dropbox2 ACK, Drive UNKNOWN_NO_ACK다.
PR94의 별도 Drive·Dropbox ACK/readback은 외부 작성자 영수증으로 수용했고 이번 intake의
직접 provider 재검증은 아니다. 과거 미확정 Drive 업로드를 해결한 것으로 해석하지 마.
후속 document/addendum 배송본의 실제 ZIP/ID/SHA/ACK는 최종 authority receipt를 따라.
Content 파일/원 science/raw/실패/과거 NOT_PUBLISHED와 C21F~K의 HOLD를 변경하지 마.
이번 반환이 마감됐으면 완료 상태를 보고해. 이후 실제 사용자 목표에 따른 미완료 질문·입력의
선정을 막지 말고, 완료 입력 재실행이나 이름만 바꾼 반복 cycle을 만들지 마.

항상 global_error_bound=null. 범위는 preliminary non-tilted collisionless LRS
Bianchi I다. General triaxial/full reionization/CMB는 HOLD다.
Speedup·memory improvement·64-core scaling·새 대규모 benchmark는 주장하거나 수행하지 마.
마지막에는 실제 publication commit/document head/PR, 백업 ZIP SHA와 provider별 ACK,
DAG 완료·미완료·HOLD와 다음 인계문을 한국어로 보고해.
```

## 파일 탐색 순서

1. 최종 document publication/backup receipt로 현재 게시·백업 상태를 확인한다.
2. `RESEARCH_DAG.json`의 content 시점 상태와 이후 document closeout의 갱신을 구분한다.
3. `REPORT_KO.md`, `OPERATIONS_KO.md`, `ANALYSIS_METHOD_KO.md`를 읽는다.
4. `execution_checks/EXECUTION_RECEIPT.json`, `analysis/SUMMARY.json`, `checks/INDEPENDENT_REVIEW.json`에서 실행·분석·독립 검토 범위를 확인한다.
5. `CODEX_HANDOFF_KO.md`의129 guard와 고정 실행 checkout 분리를 따른다.

`analysis/SUMMARY.json`의 `PNG_visual_review=PENDING_INDEPENDENT_REVIEW`는 producer가 출력을 만든 당시의 불변 값이다. 이후 완료된 `checks/INDEPENDENT_REVIEW.json`이 독립 PNG검토를 결속한다. PDF별도raster검토는 수행되지 않았다. 기존 source/산출manifest를 현재 상태로 덮어쓰지 않는다.

원 content manifest의 모든 payload는 고정 `e7729092...` Git blob으로 검증하고, 현재 working tree의 `RESEARCH_DAG.json`·`STAGE_LEDGER.json` 두 상태 문서만 실제 게시·백업 갱신을 담은 별도 document receipt로 결속하며 나머지 science/source/raw의 byte 대조는 유지한다.
