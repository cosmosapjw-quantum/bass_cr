# CR-PHYS02E 독립 심사

판정은 **PASS_SCOPED**다. 이 판정은 저장 격자 경로의 물리·수학적 일관성 유도와 준비 코드의 제한된 검증을 수락한다. 실제 NCP pulse는 **NOT_EXECUTED**이며 새로운 과학 수치 결과를 승인하지 않는다. SG10의 최종 ZIP clean restore 및 stdlib plan은 root가 science freeze 뒤 별도 영수증에 완료해야 한다. 실제 NCP에서는 정확한 runtime/resource/preflight를 모두 통과한 별도의 새 2G/2pulse/3600초 작업만 가능하다.

## 독립성과 읽은 근거

심사자는 `/root/phys02e_remote_intake`이며 앞선 역할은 최신 PR33와 Drive/Dropbox의 읽기 전용 source intake였다. 후보 생성·설계, acceptance 구성, 구현 및 후보의 local test 실행에 참여하지 않았다. 이론 기여자와 두 구현자 및 계약 owner는 별도다. 초기 intake의 사실 확인은 독립 검토를 위한 source 복구였고 새 생성자 경로를 선택하거나 수락 기준을 만들지 않았다.

호스트가 제공한 라벨은 GPT-6 Astra Pro다. 실제 backend를 독립적으로 확인했다는 주장은 하지 않으며 요청된 lower-tier backend와 상속된 호스트 라벨의 차이를 보존한다. 비용·모델 성능 절감은 평가하지 않았다. physmath-research-loop의 Astra v4.0.0 연구 및 코딩 하네스 core와 현재 SCI/NCP/validation/input/dependency 계약을 읽었다.

직접 검토 범위는 부모 Cascade 초기화·projection·sharing·generator·functionals, 새 saved_grid 및 launcher/collector/wrapper, SG01–09 시험 코드와 원 실행 영수증·stdout/stderr, 이론 유도·exact toy 소스/결과, 최종 README/REPORT/NCP 시작 절차 및 관련 state/입력 문서다. 실제 19개 direct input과409개 dependency의 bytes/SHA256/Git blob을 확인했다. 5개 계약과 6개 핵심 코드 identity, 원 worker source 및 evidence binding도 확인했다. 세부 bytes는 동반 판정의 `reviewed_files`에 결속된다.

## 1. 출발 실패의 의미

PR33 head `20c2e6de7c58c3690efca6322489b811c99f3e99`의 실제 launcher는 1로 종료했고 wall은103.79789273899951초다. fullBED constructor는 반환했지만 exact-grid guard가 실패했고 pulse 호출0, legacy 미시작이다. G 실물은 저장되지 않았다. 원래 wrapper exit0은 실패 수집을 마친 결과다. 이 실패와 원 독립 HOLD를 이번 준비 판정으로 소급 승격하지 않는다.

두 저장 NPZ에서 E 재생성의 차이는340/9600개, 원 independent probe상 최대1 ULP다. 버전 문자열 일치에도 exact E가 맞지 않았다는 것이 관측 사실이며 SIMD/libm 원인, 실제 G 원소 차이, 1 ULP의 물리적 허용 여부는 미해결이다. 기존 예산의 남은 수량을 재사용하지 않는다.

## 2. 물리·수학 검토

활성 상태는 $U_i=E_iN_i$다. 에너지 선형함수의 활성 가중치1과 보정 수 함수의 활성 가중치$1/E_i$, cutoff_number의+1 및 이온화 counter의-1은 원본과 맞는다. low_cross 장부를 전역 합에 중복 가산하지 않는 점도 맞다.

Barycentric count 투영에서 $N_l+N_u=p$ 및 $E_lN_l+E_uN_u=pW$가 성립한다. CUT 이하의 실제 에너지와 첫 활성점 사이 cutoff ghost의 에너지를 구분한 설명은 원 `project`와 일치한다. drift·이온화·여기 열의 정확산술 에너지 및 보정 수 장부 소거도 해당 source의 식에서 직접 성립한다. 이 등식은 현재 실제 FP64 G 잔차를 측정했다는 뜻이 아니다.

이미 만든 G와 상태 수치를 유지한 채 E만 바꾸면 새 수 장부가 $[\ell_N(E')-\ell_N(E)]^TG(E)$를 갖는 반례가 타당하다. 2 eV 노드의 상향 한 ULP인 $\epsilon=2^{-51}\,\mathrm{eV}$ 예에서 $d\epsilon/[(2\,\mathrm{eV})(2\,\mathrm{eV}+\epsilon)]$는 정확히 $1/(9007199254740994)\,(\mathrm{eV\,s})^{-1}$이다. 에너지 장부는 계속 영일 수 있다. 이 작은 값은 실제9600점 G의 오차나 상계가 아니다.

시간 변수 $u=t/T_0$에 대한 $G=T_0A$는 시간 재척도화이며, 에너지 좌표에서 수 장부로 가는 항목은 $\mathrm{eV}^{-1}$의 혼합 차원을 유지한다. 같은 E에서 rate를 바꾸어도 두 장부가 영이 될 수 있으므로 exact E와 장부 보존은 모든 G항목 동일성이나 물리적 정확성의 충분조건이 아니다. root 요약의 무차원 표현은 이 정확한 내용으로 정정됐다.

Fraction oracle의13개 항등식은 별도 기여자가 한 번 실행했고 exit0,0.028147148초를 기록했다. 소스·stdout·stderr identity를 확인했으며 reviewer가 그 계산을 반복하지 않았다. 수식 delimiter 정정 외 수학·수치 계산 변경은 없다.

## 3. 저장 격자 구현의 수락 범위

새 subclass는 부모 initializer를 호출하지 않고 검증한 immutable saved E를 먼저 설치한다. 그다음 n/size/ix, 실제 atomic object, sharing_order4, quantum_constant0, mesh(3200,6400), normalization_diagnostics를 원래 값과 순서로 설정하고 상속 generator를 한 번 호출한다. 다른 수치 메서드는 parent method object 그대로다. E를 G 뒤에 바꾸거나 grid factory를 전역 monkeypatch하지 않는다.

preflight는 양쪽 NPZ 파일의 전체 identity를 모두 확인한 다음에만 NPZ를 load한다. 14개 배열의 원 bytes를 보존하며 dtype·shape·finite·단조성·경계/분할·고정 raw digest·time/tags·heat0·scale를 검사한다. 완전한 source_vectors의 cutoff/counter 행을 버리거나 재투영하지 않는다. 두 번째 파일이 틀린 경우도 어느 G 예약보다 먼저 종료한다. immutable bytes를 기반으로 하므로 원 반환 배열의 writable flag를 다시 켜는 것도 허용되지 않는다.

SG01–05의7개 실제 시험은0.678532955초에 exit0이며 첫 실패·repair0이다. 원 generator는 mock으로 대체한 독립 모듈 fixture에서만 호출했고, 실제 부모의 project/functionals는 작은 경계·cutoff·에너지/수 보존 probe로 확인했다. 이것은 실제 full G 생성이나 NCP runtime 검증이 아니다.

## 4. NCP 실행·반환 구현 검토

worker는 독립 심사·입력·의존 파일·DAG admission, exact numerical runtime, 양쪽 저장 입력 preflight를 거친다. 이후 각 모형에서 resource 검사 → BUILD reservation → atomic import/construct → saved-grid constructor → strict postconstructor E guard → completed-G receipt → PULSE reservation → pulse 순서를 따른다. preflight 실패와 postguard 실패는 pulse에 도달하지 않는다. SG06의 mock event 검사가 이 순서를 검증한다.

coordinator는 한 개의 새 run과 private inherited pipe capability를 사용하며 준비부터3600초의 전체 deadline을 둔다. fullBED 다음 legacy, 모형별 한 G와 한 pulse로 범위를 고정한다. 예약 수와 완료 G 수를 구분하고 생성 완료 뒤 CSC/E/method identity를 기록한다. G identity를 과거 G와의 parity로 읽지 않는다.

pulse_response.py와 ops.py는 D와 전체 bytes가 동일하다. launcher의 pulse 이후 SI 환산·saved ramp/terminal/CDF 경계 비교 계산 본문도 동일하며 기존1e-9 gate 및 수치·물리 허용값은 유지됐다. inherited reference는 대수적 same-operator 점검이고 독립 물리 검증이 아니다.

wrapper는 execute를 한 번, collect를 한 번 호출한다. execute1/collect0은1이며 execute0/collect1도 실패다. 원 실제 exit와 wrapper execute receipt는 archive에 들어간다. collection 및 최종 wrapper receipt는 archive가 만들어진 뒤 알 수 있으므로 ZIP 밖에 있으며 최종 handoff는 이2개 sidecar와 외부 로그·setup 기록까지 return family로 요구한다. 이 제한이 문서에 명시되어 있고 자기 archive hash를 넣는 순환을 만들지 않는다.

SG06–09의8개 시험은1.139337197초에 exit0, 실패·repair0이다. isolated READY fixture는 live DAG를 바꾸지 않는다. collector fixture는 현재 unit·409 dependency·이전 실제 실패·restore metadata를 포함한 정확한 entry 집합과 모든 byte/hash를 확인했다. 그 실행을 실제 NCP 물리 결과로 승격하지 않는다.

## 5. 발견 사항 및 해결

- **D1 — 수식 delimiter:** 98개 inline span의 표시를 문서 owner가 정정했다. 수학 본문·display 식·toy 소스/결과는 유지됐다. 최종 DERIVATION SHA256은 `e5f303912f43100952facfce0d19ea78c06de91f04855dfa156fb453471f8044`다.
- **D2 — 혼합 차원:** root 보고서의 G 무차원 표현을 시간 재척도화 생성자 및 에너지→수 성분의 잔존 차원으로 정정했다.
- **D3 — 예약 순서:** 보고서를 양쪽 preflight → BUILD 예약 → atomic import/construct → saved-grid constructor의 실제 순서로 정정했다.

세 항목은 모두 닫혔고 구현·계약·허용값 또는 과학 계산을 바꾸지 않았다. 새로운 material blocker는 없다. 최초 구현 시험의 성공 기록과 별개의 문서 정정 중 첫 regex guard 실패 기록도 보존되어 있다.

## 6. 최종 판정과 남은 gate

SG01–09와 한정된 유도·exact toy 및 source binding을 **PASS_SCOPED**로 수락한다. 이 판정은 root가 여섯 코드와 계약을 결속하여 새 NCP task를 준비할 수 있게 한다. 현재 실제 물리 G/pulse는0/0이며 reviewer도 물리·과거 suite·새 과학 probe를 실행하지 않았다. 여기서 수행한 별도의0.12328초 작업은 파일 identity 비교뿐이다.

**SG10은 이 판정 시점에 미수행이다.** Root는 frozen 최종 ZIP을 새 위치에 한 번 복원하고 exact entry/manifest 및 stdlib plan을 확인한 실제 영수증을 ZIP 밖에 발행해야 한다. 현재 호스트의 resource HOLD를 NCP 자원 PASS로 바꾸어 읽지 않는다. 실제 NCP 실행에는 Python3.12.3/NumPy2.4.2/SciPy1.17.0·실제 threadpool1·자원 admission·두 입력 preflight가 필요하다. local 시험환경3.12.14/2.3.5/1.17.0은 그 인증이 아니다.

그후의 실제 반환은 새로운 독립 과학 심사를 받아야 한다. PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED를 유지한다. 원인 미확정, full G parity, 실제 CDF/uncapped moments, production/cosmic history/NCP64 성능에 대한 새 주장을 하지 않는다.
