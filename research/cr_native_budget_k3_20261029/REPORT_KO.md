# bass_cr CR_NATIVE_BUDGET_K3_FRONTIER_V1: source-pinned exact frontier

2026-10-29 KST. 연구 기준: `cosmosapjw-quantum/bass_cr`, predecessor Draft PR119 HEAD `25bc4d54df0e26ea2adf60ec012bc6b1a25caf95`. 별도 브랜치 `research/cr-native-budget-k3-frontier-20261029`. 기존 PR116–119, main, 타 owner 브랜치 및 중앙 DAG를 변경하지 않는다.

## 1. 핵심 물리·수학 결과

실제 PR116 PHYS02 He source NPZ SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`를 Wolfram remote kernel에서 HTTP200으로 가져와 파일 해시를 검증했다. 두 binary64 `.npy`를 bit-exact rational로 해석했다. 3200 active+별도 cutoff ghost=3201 양의 원자, K=3eV의 low453/high2748, high 중 K 이내 bin2 485, low bin2 162, cross low bin0/1 291을 확인했다.

기존 same-bin 최적 사건 S를 만드는 315개 양의 pair를 먼저 구성하고, 남은 high를 cross-bin low와 526개 pair로 추가 연결했다. 이 결합 witness의 전체 질량은 기존 독립 Hall upper M과 정확히 같다. 원자3201개 용량 검사, 사건841개 에너지/bin support 검사, same-bin/full primal-dual exact equality가 모두 통과했다.

따라서 **고정된 이 source와 K=3eV에 한해** cross-bin 예산 `C<=c`의 전체 high-low 최댓값과 double-event 최댓값은

`M_K3(c)=min(S+c,M)`, `dmax_K3(c)=(L+M_K3(c))/2`, `c>=0`.

전환점 `(M-S)/N=0.11103104037640514`, `dmax(0)/N=0.1358916404240498`, `dmax(M-S)/N=0.19140716061225238`. c<R에서 same-bin Hall dual과 lambda=1, c>=R에서 full Hall dual과 lambda=0이 각각 정확한 상계/하계 일치 증명서를 준다. 일반 finite source의 sufficiency나 고정 C=c polygon은 주장하지 않는다. 증명과 정확 유리수 원문은 THEORY.md 및 RESULTS.json 참조.

q_i(t)=t w_i, proper t in [0,1e10]s, W=5e19s²라는 **조건부** 역사와 PR116 chemical energy bookkeeping을 유지한다. 실제 physical K, exclusive He kernel, photon redistribution, RR, donor/partner work, stopping, temperature, full physical native25 및 production/L4는 null/HOLD다. 실제 He 재결합 예측으로 승격하지 않는다.

## 2. 코딩 및 독립 계산 엔진

`native_budget.py`는 original NPZ SHA와 3201-atom digest를 확인한 뒤 exact binary64->Fraction을 사용한다. 원자별 primal event, low diagonal, high single과 0/1 Hall dual, lambda를 반환한다. 원래 전체 그래프의 zero-mass vertex에 대한 dual cover를 비용0으로 확장한다. **일반 임의-bin two-pass greedy의 최적성을 가정하지 않고**, source별 S/M Hall dual 일치를 확인하지 못하면 계산을 거부한다.

현재 컨테이너: Python3.13.5, NumPy2.3.5, SymPy1.14.0. `python3 -m unittest -v test_native_budget` 10/10 PASS, 별도 full-event LP 48 사례 일치, synthetic 3201-atom topology PASS, `python3 -O -m unittest -q test_native_budget` PASS. 첫 검증에서 확인된 zero-mass dual 원래 그래프 누락을 표적 교정했다. 최초 native source NPZ는 현재 컨테이너에 마운트되지 않았고 직접 다운로드 DNS가 실패했다. **따라서 Python 코드를 원본 3201-atom NPZ로 실행한 적은 없다.** native K3 source의 exact numerical result는 독립적인 Wolfram 엔진의 결과이며, 동일 입력으로 Python/Wolfram native 결과를 교차 실행한 것으로 표현하지 않는다.

Wolfram source SHA 및 N/L/S/M exact equality, 315+526 pair, full marginal support는 실제 실행에서 확인됐다. Wolfram ExportString(JSON) witness SHA256 `f2260f69db5e5ae6b63c339ca1089d0baf9bf0f74328843a658e321e98ccd8ce`는 Wolfram 직렬화에 한정된 digest다. 실제 pair 원문 전체를 Git에 게시하지 않았으므로 이 SHA만으로 witness raw bytes를 복구할 수 있다고 주장하지 않는다. Python 코드가 원본 NPZ를 확보하면 해당 witness를 독립 생성할 수 있다.

저장된 FIGURE.png/SVG는 정확 유리수 계산을 표시용 binary64로 변환한 그림이며 실제 시각 확인을 마쳤다. 정확성의 근거는 그림이 아니라 유리수 증명서다.

## 3. 문헌 및 다른 저장소 영향

Exa/SciSpace에서 확인한 관련 이론 문헌은 fractional matching/weighted Hall, Kapoor–Sarwat (2013) budgeted transportation, 그리고 Switzer–Hirata (2008), Chluba–Fung–Switzer (2012)의 He line transfer다. 일반 LP duality를 신규성으로 주장하지 않는다. 직접 비교한 최신 관련 PR: BASS_HE#104는 조건부 D birth-bin 에너지, REC#154는 HD level interval, WU088_HH#155는 특정 HD 반응 state rate의 source 복구, BASS#239는 양의 angular source 인증, vigilode#102는 scalar-affine ODE certificate, REI#260은 UVB nuisance union이다. **이 중 어느 것도 실제 exclusive He kernel이나 현재 CR의 K를 공급하지 않는다.** 7개 repo 최신 PR 메타데이터와 선택 commit 일부를 조사했으며, 모든 비공개 대화/모든 ref/모든 원본 백업을 새로 전수 검증한 것은 아니다.

## 4. 단계·DAG·검증 판정

- 이론 R1–R5,R7–R10 완료 9/10. 서로 다른 작성자의 R6 심사는 NOT_RUN.
- 코딩 C1–C8,C10 완료 9/10 (C7은 Wolfram native + Python synthetic, Python native NOT_RUN). 서로 다른 작성자의 C9 심사는 NOT_RUN.
- 선택 워크플로 18/20, 새 extension DAG **0/3** (첫 노드 SCOPED_K3_EXACT_RESULT_HOLD), 중앙 **28/88**, delta0. 원래 PR119 보조 노드1/1은 역사적 완료로 유지한다.
- 이전 PR118 `>=20.45/20 CPU-s` RESOURCE_BUDGET_FAIL은 불변이다. 이번 실행은 첫 실행 전에 aggregate CPU cap을 고정하지 않았으므로 예방적 hard-budget PASS는 주장하지 않는다. 실제 두 번의 측정 테스트만 합산해 local CPU 최소44.07s이며 다른 Python/Wolfram/metadata/provider CPU는 UNKNOWN_NOT_ZERO.
- Git source checkpoint는 이론, 코드, 테스트의 실제 개별 커밋 3개로 게시됐다. 20개 단계별 Git commit을 했다고 주장하지 않는다. Google Drive 및 ChatGPT Library에 해당 파일 3개의 실제 완료 응답을 확인했다. Dropbox original upload는 connector fileParam object injection 문제로 BLOCKED다. Dropbox Paper가 있다면 text-only pointer이지 원본 binary backup이 아니다. 새로운 archive 원본의 원격 full GET/whole SHA 검증은 NOT_RUN.

다음에는 source NPZ 원본을 로컬 Codex에서 확보하여 `python native_budget.py /path/ATTRIBUTION_ARRAYS.npz --c 0 --c '<R>'`를 실행하고 3201 original capacities 및 Hall dual을 확인한 뒤, 독립 R6/C9와 자원/백업 조건을 닫는다. 별도의 일반 임의-bin cost-budget mincost flow는 현재 K3 특수해와 구분하여 후속 연구로 남긴다.
