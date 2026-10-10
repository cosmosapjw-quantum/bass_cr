# CR-PHYS02A 이후의 물리 연구 인계

작성일: 2026-10-10. 프로젝트: `cosmosapjw-quantum/bass_cr`.

## 현재 결과부터 읽기

이번 work unit은 **CR-PHYS02A-CAUSAL-SUBTHRESHOLD**다. PHYS01의 실제 양성자
source를 이어 받아, 직접 생성된 0.1–10 eV 전자가 고정 electron bath에 전달하는
인과적 Coulomb stopping 응답을 유도하고 계산했다. 상위 PHYS02-DELAY 전체는
아직 열려 있다. 최종 scoped 판정은 `review/INDEPENDENT_DECISION.json`, 정확한
publication commit과 원격 백업 상태는 `publication/`의 별도 영수증을 따른다.

읽는 순서는 다음과 같다.

1. `REPORT_KO.md`, `state/SCIENTIFIC_CONTRACT.json`, `state/CLAIM_GATE.json`.
2. `research/DERIVATION_KO.md`, `review/INDEPENDENT_REVIEW_KO.md`.
3. `evidence/NUMERICAL_RESULT.json`, `evidence/EXECUTION_RECEIPT.json`.
4. `inputs/PARENT_SOURCE_MANIFEST.json`, `DAG.json`, `state/NEGATIVE_RESULTS.md`.

PHYS01 parent commit은 `e41e18873af438ef989ff44f505fe2665118fdec`다. 새 연구는
별도 branch `research/cr-phys02a-causal-subthreshold-20261010`의 additive folder다.
이 branch에서 `publication/PUBLICATION.json`의 scientific commit/tree를 기준으로
소스를 고정한다. 나중에 추가된 delivery receipt commit과 구분한다.

## 이미 구현·검증된 것

- `src/causal_subthreshold.py`: 원 Rudd SDCS의 저에너지 계수 분리, 실제 ramp
  source, Ei 감속 시계, birth-time convolution, active/cutoff 에너지 ledger.
- `tests/verify_causal.py`: 독립 adaptive 적분, forward ODE, source 적분,
  quadrature, 에너지 보존, OFF/domain 및 원 Bianchi 계수의 세 시점 비교.
- 실제 final 실행: 9/9 PASS_SCOPED, exit 0. 코드·입력·환경·stdout/stderr의
  identity는 실행 영수증에 있다. 이전 PHYS01 science suite 재실행은 0회다.
- 10^10 s에서 stopping power/selected terminal proxy = 0.220764561.
  누적 selected injection의 15.5763%가 stopping heat, 83.8894%가 active
  electron kinetic storage, 0.5343%가 cutoff residual이다.

코드나 환경이 바뀌지 않았다면 완료한 검사를 반복하지 않는다. 변경분이 생기면
새 source identity를 기록하고 영향을 받는 검증만 실행한다. 위 기능을 새로
구현하는 작업으로 되돌아가지 않는다.

필요한 신규 검증의 실행 위치는 저장소 루트다.

```bash
python3 research/cr_phys02a_20261010/tests/verify_causal.py
python3 research/cr_phys02a_20261010/tests/render_results.py
```

ZIP도 동일한 `research/` 상대 구조를 제공한다. 원 dependency는 sibling
`research/cr_phys01_20261010/src/injection.py`, `rudd.py`이며 실행 때 SHA-256을
확인한다. 현재 실행 환경은 Python 3.12, NumPy 2.3.5, SciPy 1.17.0, FP64다.
환경 재현은 실제 패키지 버전 기록을 기준으로 하며, 다른 환경에서의 실행이나
NCP64/MPI 성능은 검증했다고 주장하지 않는다.

## 다음 최소 물리 work unit: CR-PHYS02B

**10–1000 eV electron-impact H/He ionization/excitation의 absolute rates와
branching을 source-pinned 상태로 확보해 시간 generator를 구성한다.** 이 구간은
active 1–4 MeV proton impacts가 직접 생성하는 전체 전자 운동에너지의 약
71.07%를 차지한다. 가장 큰 세부 구간은 100–1000 eV의 42.35%다. 이 수치는
우선순위 근거이며 10–1000 eV만으로 전체 PHYS02를 닫는다는 뜻은 아니다.

다음 실행 계약을 먼저 고정한다.

1. 실제 원천 cross section의 version/bytes, target별 문턱·단위·에너지 범위,
   total/SDCS consistency, ionization energy sharing 및 excitation 채널을 정한다.
   문헌의 이름이나 FS10 terminal 표를 absolute clock 대신 쓰지 않는다.
2. 현재 nH/nHe/ionization/T 상태에서 `n_target v sigma`의 절대 collision rates와
   연속 Coulomb drift를 결합한다. 임의의 exponential lag를 도입하지 않는다.
3. 전자 수·에너지, 새 secondary branching, binding cost, excitation/photon
   reservoir를 분리한다. 0.1–10 eV로 들어오는 시간별 경계 유량을 계산하고
   본 모듈의 저에너지 Green response와 연결할 인터페이스를 명시한다.
4. positivity와 disjoint energy ledger, source OFF/초기시간 극한, energy/time
   resolution 비교 및 같은 operator의 terminal limit를 검증한다. FS10과의
   비교는 같은 조성·threshold·채널 계약에서만 해석한다.
5. helium excitation에서 생긴 ionizing photons는 재흡수되기 전의 별도
   number/energy reservoir로 추적한다. FS10 terminal 재흡수분을 다시 더하지 않는다.

CCC/NIST는 `research/literature/SOURCE_AUDIT.md`에 적힌 **후속 자료 확보 경로**다.
이번 루프에서 그 numerical cross-section bytes를 확보하거나 채택한 것은 아니다.
현재 CCC 배포물을 FS10 원 Monte Carlo의 exact input으로 간주하지 않는다.

## 계속 열린 조건

`CR-PHYS02A-THERMAL-MATCH`는 0.1 eV 이후의 kinetic/thermal matching,
electron-neutral/electron-ion 에너지 교환, energy diffusion 및 실제 bath response를
요구한다. 10 eV에서 classical cutoff의 asymptotic separation도 약하다.
ν_neutral<ω_p는 채택한 Coulomb-only closure의 조건이며 이번에 neutral rates로
검증한 사실이 아니다. physical uncertainty certificate는 없다.

`CR-PHYS02C-HIGH-ENERGY`는 ≥1 keV의 직접 전자 input 약24.46%와 각 proton
ejection endpoint까지의 수송을 요구한다. 원 proton source의 1–4 MeV 밖 loss
coverage는 별도 `CR-PHYS04-LOSSES`다. 둘을 같은 tail로 합치지 않는다.

`CR-PHYS03-COMPOSITION`은 independent H/He fractions와 T/abundance 지원을
별도로 닫아야 한다. PHYS05 receiver는 PHYS02/03 뒤에, PHYS06 history는
PHYS04/05 뒤에 진행한다. delayed receiver에서는 suprathermal free electron
number와 thermal pressure에 참여하는 electron number를 구분한다.

## 보존할 의미와 권한

CR을 photon/heat/CX source로 바꾸거나 full 10 keV–1 PeV 정규화를 1–4 MeV
구간에 맞추어 바꾸지 않는다. 미구현 tail과 cutoff 잔량을 heat로 채우지 않는다.
7.05% 규모 비교를 전체 CR heating suppression 또는 엄밀 하한으로 승격하지 않는다.

상위 PHYS02 admission=false, production history HOLD, 원 atomic G02 UNRESOLVED,
b_grid NO_GO, all_bound OPEN과 각 원 실패는 유지한다. R17B2B photon lane의
NO_CERTIFIED_SOURCE_SHARPENING을 이 결과로 변경하지 않는다.

현재 모델의 host identity에 따라 physmath-research-loop router를 적용한다.
이번 실행은 GPT-6 Astra Pro, research/coding harness v4.0.0이었다. 하네스 선택은
모델 성능 증거가 아니며 스스로 모델을 전환했다고 주장하지 않는다.

기존 승인 범위의 research branch publication과 create-only Drive/Dropbox backup은
계속 가능하다. 일반 검증은 R1이며 `UPLOAD_VERIFIED`와 `RESTORE_VERIFIED`를
구분한다. main merge, 원본 덮어쓰기, 별도 사람에게 메시지 전송은 이번 범위에 없다.
