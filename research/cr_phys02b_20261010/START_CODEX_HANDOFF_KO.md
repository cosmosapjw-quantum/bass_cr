# 다음 `bass_cr` 물리 연구 루프 시작점

## 1. 채택할 기준과 목표

현재 물리 단위는 **CR-PHYS02B-CAUSAL-CASCADE**다. 부모는 PHYS02A 최종
`58c8e1cda5c8f8ca8b83269cb89899ea40ab91fe`이며, 신규 연구 브랜치 이름은
`research/cr-phys02b-causal-cascade-20261010`이다. 실제 출판 commit/tree/PR 및
백업 확인 수준은 이 폴더의 `publication/` 영수증을 읽어 확인한다. 이 문서 안의
예정 브랜치 이름 자체를 원격 출판 성공의 증거로 삼지 않는다.

먼저 `REPORT_KO.md`, `DERIVATION_KO.md`, `review/FINAL_DECISION.json`,
`state/RESEARCH_STATE.md`, `state/HYPOTHESIS_GRAPH.md`를 읽는다. `HANDOFF.json`과
실제 실행 매니페스트를 통해 정체성을 확인한다. 현재 실제 호스트 모델은 GPT-6 Astra Pro,
적용 연구·코딩 하네스는 각각4.0.0이었다. 다음 세션은 그 세션의 실제 모델을 확인하고
physmath-research-loop 라우터가 정한 하네스를 사용한다. 하네스 버전을 모델 성능의
검증으로 취급하지 않는다.

원래 목표는 하전입자 에너지 전달의 물리적인 시간 의존 응답이다. 이번 해는
0.1–900eV 전자에 대한 **명시된 조건부 원자 혼합 모형과 고정 bath**의 인과적 분기 계산이다.
계산된 유한시간 열률과 종단 비교의 차이를 전체 역사나 모든 상태에 대한 배율로 사용하지 않는다.

## 2. 이미 실제 실행한 것

- 소스 정체성을 확인한 뒤, 부모의 `Q=tA(E)`를900eV까지 지정 범위에서 연장했다.
- HI/HeI 이온화 두 딸전자, CCC27개 여기, leading-log Coulomb 감속, disjoint 에너지·수 장부를 구현했다.
- R001 실제 exit1의 경계 수렴 실패를 보존했고, 동일 식·기준의 추가 격자 배증으로 R002 실제 exit0,13/13 PASS_SCOPED를 얻었다.
- 독립 exact toy, 독립 시간 적분(DOP853, G는 공유), 독립 장부 좌함수와 부모 연속 저에너지 해를 비교했다.
- 최종4800nodes: 선택 입력73.55293%, active98.29509%, 누적열1.32307%, 현재열률3.44099538e-44Jm^-3s^-1.
- 같은 고정 연산자의 terminal immediate proxy 대비 현재열률3.41089%. 별도 postprocessing에서 출생 구간과 열 발생 구간을 분리했다.
- 부모 과학 테스트 묶음 재실행0. SHA/파일/manifest 검사 자체를 새 물리 계산으로 세지 않았다.

정확한 source/test/output identity와 실제 process receipt는 `evidence/runs/`에 있다.
R001을 지우거나 통과 실행으로 바꿔 쓰지 않는다. 추가 진단은 `evidence/diagnostics/`에 있고
G를 한 번 구성했으나 저장된 trajectory를 다시 전파하지 않았다.

독립 최종 판정은 `PROMOTE_SCOPED`(2026-10-10 12:30:02 UTC)다. 후보 생성·구현·검증에
참여하지 않은 검토자가 원27개 고정 파일과 후속14개 환경 보완 파일을 확인했다.
DOP853의 독립 시간 적분 비교는 활성240개 격자에서 같은 G를 사용한다.
후속1thread 계산은 최종4800개 노드의 endpoint만 실제 재현했고 비교한 최종 관측량은
R002와 같았다. 원 R002의 thread 수는 `NOT_RECORDED`로 유지한다.
명시적 재현 명령의 환경 설정은 README/REPORT와 thread_control supplement에 있다.

## 3. 해석에서 유지할 경계

1. He 총률의 NIST `Q=.8841`과 채택한 인쇄 BED 계수의 `Q_df=.9130416667`은 다르다.
   raw BED를 정상화한 에너지 공유와 BEQ 총률을 결합했다. 이것은 명시된 hybrid이며
   완전한 NIST CGI·실험·원래 논문의 수치 재현이 아니다.
2. CCC 파일의 첫 zero marker를 여기 유효 비용으로 사용했다. He2¹P21.1156eV는
   NIST 분광값21.2180eV와 다르다. 에너지 보존은 채택 비용에 대한 항등식이다.
3. NIST CGI 원래 비교는 HTTP500/폼 부재로 NOT_EVALUATED다. 수치 실행 전 addendum의
   대수 적분 비교가 이 미실행 항목을 닫지는 않는다.
4. 여기 에너지는 저장고이며 방사 분기·광자 수·재흡수는 없다. 이온 결합·cutoff 운동
   에너지를 열로 더하지 않는다. low-cross는 내부 통과 진단이므로 총에너지에 더하지 않는다.
5. 고에너지 출생 성분의 전체 열을 모두10eV 아래 캐스케이드 열이라 부르지 않는다.
   현재 고에너지 출생 열률의5.5363%만10eV 이하에서 발생한다.
6. 이 모형에 없는900eV 위 직접 전자 에너지26.445974%와 그 유입을 무시할 수 있다고
   결론내리지 않는다. 선택 원천 분모를 전체 양성자 손실의 분모와 섞지 않는다.

불변 gate: PHYS02-DELAY OPEN, production history HOLD, atomic_G02 UNRESOLVED,
b_grid NO_GO, all_bound OPEN. 별도 R17B2B photon lane의
NO_CERTIFIED_SOURCE_SHARPENING과 xi=.1 knot branch는 이 xi=.01 계산에 의해 바뀌지 않았다.

## 4. 다음 최소 물리 단위: CR-PHYS02C-ATOMIC-CONSISTENCY

큰 parameter sweep나 전체 역사를 먼저 돌리지 않는다. 같은 시나리오에서 원자 입력의
일관성을 닫거나 정확한 source blocker를 확인한다.

**질문:** 같은 물리 원천에 속하는 HI/HeI 총이온화율·진동자 세기·딸전자 공유와,
CCC의 실제 표적 상태 에너지를 함께 고정했을 때 PHYS02B의 시간 의존 관측량이 얼마나 바뀌는가?

사전 계약에는 채택 원자 표현, 표적 준위 에너지의 권위 있는 출처와 CCC 계산 에너지와의
관계, 이번 기준 해와 비교할 관측량, 수치/물리 차이의 분리, 접근 실패 시 제한을 적는다.
먼저 공개 primary paper/배포 문서/실제 데이터가 충분한지 확인한다. 원저자에게 메시지를
보내야만 얻을 수 있는 정보가 있다면 초안을 준비할 수 있지만 사용자 명시 권한 없이 보내지 않는다.

구체적 시작 항목:

- He2000/2009/NIST의 `df/dw`, `Ni`, `Q`, `K` 관계를 원문과 계산으로 대조하고,
  raw BED와 generalized BEB/BEQ 총률의 차이를 명명한다. 임의로 한 표의 수치를 고쳐 맞추지 않는다.
- CCC의 final-state energy/threshold가 native marker·spectroscopy 중 어느 것인지
  배포 문서 또는 직접 제공 데이터로 확인한다. 모든 선택 채널을 동일 정책으로 처리한다.
- 그 정책에서 충돌의 에너지·입자 항등식과 양성이 성립하는지 유도한 뒤 코드를 수정한다.
- 동일 source/bath/time에서 PHYS02B canonical과 직접 비교한다. 기존 수렴 실패 때문에
  최소한 경계 유량에 충분한 에너지 해상도를 사용한다. 물리 차이를 numerical tolerance로 흡수하지 않는다.
- 구현·검증에 참여하지 않은 실제 독립 최종 판정자가 좁은 채택 여부를 정한다.

900eV+ source tail, HeII/high-n, photon cascade, thermal matching, gas feedback은 그 다음
의존 노드다. 이 항목들을 한 번에 닫았다고 주장하지 않는다. 필요한 원자 source가 없으면
그 경로는 BLOCKED이며 확보한 일관된 부분과 보류한 부분을 명시한다.

## 5. 재현과 증거 보존

패키지의 `research/` 구조를 유지하면 PHYS02B는 부모4개 파일을 runtime hash 검사 후 사용한다.
실행 명령과 버전은 README/REPORT에 있다. 기존 R001/R002를 출력 폴더로 재사용하지 않는다.
권한·입력·환경 변화가 없으면 과거 suite 전체를 의례적으로 다시 실행하지 않는다.
새 물리 차이가 요구하는 판별 검증만 설계하고, 실제 command/exit/stdout/stderr/result hash를 남긴다.

진단 그림에는 Matplotlib도 필요하다. 사용 버전은 진단 execution record에 있다.
과학 NPZ는 `numpy.load(..., allow_pickle=False)`로 읽을 수 있다. 원자 단위/열/상태
매핑은 source audit가 기준이다. 원본문헌 전체나 인증정보는 이 인계에 포함하지 않는다.

## 6. 권한과 마감

현재 연속 연구 요청과 앞선 인계는 가산적인 연구 branch/draft PR 및 새 이름의
GoogleDrive/Dropbox 이중 백업을 이미 허용한다. main merge나 다른 사람에게의 메시지는
포함하지 않는다. 위임된 백업 위치는 기존 연구 dossier 폴더다. 실제 위치·ID는 publication
receipt에서 확인하며 단순히 예상 파일명을 만들어 저장 성공이라 쓰지 않는다.

기본 백업 확인은 R1: 업로드 완료 acknowledgment와 ID/path/size 등의 메타데이터 읽기다.
이를 UPLOAD_VERIFIED라고 기록할 수 있지만 RESTORE_VERIFIED로 올리지 않는다. 제공되지 않은
원격 checksum을 만들어내지 않는다. 새 부여된 사용자 지시가 있으면 그 지시를 우선한다.
