# BASS_CR 논문·코드 DB 및 연구 DAG 감사 / Codex 이전 작업 재조정

2026-10-03. 결론: **여기에서 진행 가능한 일이 모두 끝난 상태가 아니다.** R4AH의 자원 차단은 그 한 native pilot의 차단이다. C0/B1/B2와 G03–G06/G11의 이론·참조 구현 전체를 차단하지 않는다. 이번 산출물은 가능한 독립 reference work를 실제로 실행하고, 남은 이론/실행/권위 결합 문제를 분리한 checkpoint다. 전체 연구 종결 선언은 하지 않는다.

## 1. 조사한 권위와 범위

DBv20 exact SHA db7ba67773b40af1f623faea5096551d75b6102761a4f8b7aeb27a876cb1f21b를 읽었다. current_research_gap_status는v19 view를 참조하며v20은 runtime 기록만 추가했다. 원 requirements72개 중 BASS_CR47개(37sections+10steps), BASS_HE25개를 분리했다. 재이온화의 selected1s 목적에 반영하되 HE·H-H/H2+ 전체 연구를 이 스레드의 새 필수과제로 가져오지 않았다.

31개 works,68개 versions,32개의 selected-version file record,4개 고정 code repository를 대조했다. 모든 selected_version_id가 실제 version row에 연결된다. 이것은 DB 관계 검사이며31개 원문을 이번에 다시 내려받아 검증한 것이 아니다. 원문의 선택본 상태는 published15, institutional1, book edition1, book reprint1, legacy fulltext13으로 기록돼 있다.

옛 sources.status에는18개의 NOT_ACQUIRED가 남아 있지만 후속 works 선택본 상태가 이를 갱신한다. gaps table의 acquisition failures 역시 역사다. 이를 새로운18건의 결손으로 오인하면 불필요한 문헌 재수집 루프가 된다. DBv21에 effective literature inventory view를 추가하고 원래 실패 기록은 지우지 않았다. 원문 실제 파일의 추가 복구는 해당 계산에 필요한 정확한 manifestation이 없을 때만 한다.

코드 snapshot은 SciPy, Reference-LAPACK, SLEPc, Iterative_Volterra_Propagator 네 개다. DB에는 source archive 수집이 기록돼 있지만 해당 다운로드 source build/test는0이다. 현재 환경의 설치 SciPy 사용과 DB에 pin된 SciPy source tree의 구현검증은 다르다. 독립 propagator를 시험할 목적 없이 네 패키지를 전부 build하는 일은 우선순위에서 제외한다. 작은 현재행렬에 SLEPc 설치를 의무화하지 않는다.

원 G01–G13의 상태는 CLOSED3, RESOLVED_WITH_LIMITATION6, UNRESOLVED4다. CLOSED에도 실제 적용 조건이 남을 수 있다. 오래된 requirement matrix의 'G02 미실행' 등은 그 cutoff의 역사이며 최신 R4Z–R4AH와 연결한 새47행 crosswalk로 읽는다. 기존 matrix를 소급 편집하지 않는다.

## 2. 이번에 실제로 처리한 일

새 cr_reion 모듈군은 이산 MODEL count provider, Maxwell scalar-kernel 진단 및 core reference quadrature, H5 radial dp 측도, CX reservoir 보존, Bianchi-I collisionless reference, 이동 metric defect 진단, 조건부 residual/state/probability bound, 진동상쇄 IBP 상계, 공통 observable chain을 구현한다. actual host나 physical source를 만들지 않았다.

새 단위/통합 시험137건이 통과했다. 테스트는 scalar·unit·domain·hash·profile·capability·missing/negative bound·경로·fixture 거절을 포함한다. 일부 동작은 RED→GREEN, 나머지는 추가 검증이며 전부를 TDD로 부르지 않는다. 기존R4Z–R4AH suite 재실행0, 새shifted 적분0, 메모리admission 재시도0, M9/center/oldR8/D/V 재실행0이다.

별도 경량 계산은6개 drift에서 Maxwell normalization/mean/second moment,3개 drift에서 원 target-speed/angle 적분과의 비교,2×2 symbolic metric identity와 작은 이동기저 ODE를 수행했다. 최대 mean 상대 수치차이는 약 floating 수준이며 ODE norm drift는5.06×10⁻¹² 이하(계약1e-9)다. synthetic/reference 실험이며 실제 BASS state trajectory가 아니다. 세부값은 local_theory/evidence/LIGHT_REFERENCE_RESULTS.json.

NCP에서 m64와 이후9점을 서로 다른 승인batch로 실행할 경우를 위해 runtime_tools/merge_returns.py를 추가했다. original R4AG verifier로 각각의 native/source/geometry/epoch/seal/cell/소비계약을 검사하고, 중복node는 거절하며, 기존1점을 재실행하지 않고 exact stencil을 조립한다. 현재 버전은 같은 native bytes와 원 runtime 경로가 살아 있는 NCP 안의 수집에 한정한다. cross-ABI·재배치 archive의 완전 과학검증은 지원한다고 주장하지 않는다. 실제10개 결과가 없으므로 end-to-end physical merge는 미실행이다.

## 3. 여전히 가능한 로컬 연구와 아직 안 한 일

| 묶음 | 여기서의 상태 | 아직 필요한 것 |
|---|---|---|
| G02 shifted S | 코드/계약 준비, 실제표본0 | m64와 나머지9점 native; 이후 정해진합산. full D/H와 연속operator는 별도 |
| G03–G05 tail/bridge | 기존 conditional theorem과 새 IBP reference 있음 | 현재1s selector/기저에서 phase gap·도함수·연속 weak residual을 실제 bound로 연결. raw bridge504.54의5e-6실패 미해결 |
| G06/G11 상태/공통오차 | exact conditional bound와 chain 구현 | 실제same-endpoint 초기state, 연속ρ/operator오차, projector/embedding오차. helper만으로 닫히지 않음 |
| G12 시간/창 | 기존 국소same-IVP를 보존 | authentic incoming preparation, continuous time residual, nested window. 새scope의코드설계는 여기서 가능 |
| G09/G10/G13 coupling basis | 기존 selector/rank policy 보존 | 현재1s에 필요한 최소 결합기저, 실제radial/Gram, higher-l필요성, 누락공간 bound. 무조건 all-bound 완성을 요구하지 않음 |
| C0 consumer | H5 보고서의측도/상태의미론 회수; typed MODEL 계약 구현 | H5 raw state SHA3f0e3541…의실제bytes, 최신host commit/tree/entrypoint/첫step/source signature 및 fast acceptance |
| B1 rate | discrete exact MODEL, Maxwellcore floatingreference 구현 | source-owned σ1s continuum 또는 명시적모델을 위한 verified rate quadrature 및rate-tail bound. continuum physicaltruth 없음 |
| B2 interface | gas-local bookkeeping/Bianchi-I reference 구현 | actual BASS host binding, 일반배경/tilt가필요한 adapter, actual restart/firststep test |

즉 **이론이 전부 완료되고 NCP 계산만 남은 것은 아니다.** 이번 reference code는 위입력을 받는 계산을 가능하게 만든 것이며, 물리적 미지수를 메워 넣은 것이 아니다. G04/G05와 source continuum은 실제 이론/알고리즘 작업이 남아 있다.

## 4. 문헌을 어떻게 사용할지

G02는 Runge–Micha/Thorson–Delos의 이동기저와ETF, G03–G05는 Dollard/Enss/Yafaev/Kadyrov 및 Burgarth의 장거리·진동상쇄, G06/G11은 Martinazzo–Burghardt와 기존 finite-metric theorem, G07/G09는 Stewart/Mathias/Li+erratum/Lehtola, G12는 Alvermann–Fehske/ITVOLT/Al-Mohy–Higham/Hochbruck–Lubich, G13는 Toshima/Kuang–Lin/Errea의 수렴문헌을 조사 경로로 연결했다. 이매핑은 '모든문헌을다읽었음'이나 '문헌의정리가현재코드를인증함'이 아니다.

이번 외부확인은 Artacho–O'Regan의 이동비직교기저 논문, 기존 Burgarth/Martinazzo의arXiv identity, Git bundle/apply 공식설명, Dropbox download/content-hash 공식설명에 한정했다. 새 source record는 별도 table로 저장한다. sourceDB전체최신성이나Fachin2026의현재revision을확인했다고하지않는다.

## 5. 재조정한 실행 순서

다음 **로컬** 우선노드는 LOCAL_BRIDGE_SELECTOR_AND_PHASE_GAP_DISCRIMINATOR다. 현재candidate와현재목적1s selector를 기존fixed-J/reference와 비교하고, 그에맞는 isolated leakage·phase-gap·transfer의가정을동일화한다. 실제연속bound를만들수없으면 빠진항을정확히정의한다. fullsource나ODE실행을무조건기다릴필요는없지만, 그결과를physicaladmission으로쓸때는G02를기다린다.

동시에 **외부** 첫노드는여전히 R4AH m64다. 새메모리관측과native빌드/승인에서시작한다. m64가수락되기전에는나머지9점을시작하지않고, 기존중심/M9를반복하지않는다. 이후별도remaining9batch를준비하고승인한다. 두batch는읽기전용merge로합친다. m64의승인파일을all10으로고쳐쓰지않는다.

다음 로컬계열은 LOCAL_CONTINUOUS_RATE_ENVELOPE와 ACTUAL_CONSUMER_STATE_BINDING이다. 전자는 이번Maxwellcore코드에 rigorousquadrature/tail을붙이는작업이고,후자는실제object를찾거나새model-profile host를명시적으로선정해야하는권위/구현작업이다. 최근H19보고서에는productionfield가null이며이번검색에서도해당보고서·H5가회수됐을뿐새hostobject는확인하지못했다. 이를최신host가어디에도없다는증명으로쓰지않는다.

그뒤qualifiedstate/window, 필요한couplingbasis, b적분/에너지coverage, selected1s source admission, actualBianchi host replay를수렴시킨다. 이순서는각scientificgate를보존한다. MODELresult를중간산출물로허용하되strict/source/hostgates를닫지않는다.

## 6. 범위 정리와 종료 규칙

기본최종물리량은H0_CR_1s_FORMATION_COUNT이며전체자유전자/HII/열원과다르다. 범용원자엔진,모든원소/He,전체H-H/H2+재개발,HyRec/Lyα,Einstein배경재작성,CMBlikelihood는이계획에추가하지않는다. 그러나selected1s amplitude의누락채널영향은basis오차로여전히통제한다. momentum/heating이실제reionization에중요하면필요한최소moment/closure만conditionalbranch로연다.

local_work_exhausted=false, scientific_program_complete=false. 이checkpoint를RESEARCH_LOOP_CLOSEOUT=COMPLETE또는post-gapcanonicalcoordinator활성화근거로쓰지않는다. G02UNRESOLVED/productionHOLD/capturefalse/all_boundOPEN/b_gridNO_GO를그대로유지한다.

## 7. 전달 방법

직접git접속은현재DNS실패다. 그래서실제로적용시험한create-onlypatch를Dropbox와Drive의전체release에포함한다. 외부Codex는기존branch의실제HEAD와patchbase를비교하고신규경로만적용한다. fullgitobjecthistory를보유하지않았으므로가짜parent나syntheticancestry의bundle을실제repo bundle로제공하지않는다. Gitbundle은검증가능한commitobject와prerequisite가있을때만만든다.

이번release는현재R4AH/R4AG의전체실행archive와새reference코드/도구/DB21을자급한다. 과거R4AA379, R4AD안전성차단, R4AE/AF/AG의개별미게시mapping은이전기록으로보존하고자동우회/소급완료하지않는다. 모든새내용은새 r4ai_local_pre_codex 경로에만추가한다. 오래된runtime코드자체는그archive의기존원상태다.
