# CR 물리 provider 구현을 위한 atomic donor 최신 intake

확인 시각은 2026-10-10 19:17:12 KST이다. 새 사용자 목표는 실제 charged-particle 주입과 H/He secondary ionization·excitation·heat를 구현하여 관련 저장소에 반영하는 것이다. 이 intake는 읽기 전용이며 GitHub 변경과 과학 solver 실행은 없다. GPT-6 Astra 연구 하네스 v4.0.0을 적용했고 실제 실행 모델 식별은 UNKNOWN이다.

**실질 구현 소유자는 bass_cr의 새 외부 charged-source/deposition provider와 rei_bianchi의 실제 소비자이다.** BASS_HE·WU088_HH의 독립 원자 연산자를 바꿔야 이 provider를 붙일 수 있다는 의존성은 현재 읽은 근거에 없다. 이 두 저장소에는 필요한 경우 새 provider의 source pin과 소비자 상태를 연결하되, 기존 RCT/HH 물리 gate를 자동 승격하지 않는다.

## 최신 HEAD와 원문 확인

세 저장소의 default branch는 모두 main이다. 전체 branch 목록은 bass_cr 86개, BASS_HE 18개, WU088_HH 37개였고, 사용한 recursive tree는 잘리지 않았다.

| 작업선 | 실제 HEAD | 이번 결정과의 관련성 |
|---|---|---|
| bass_cr research/cr-r17-source-goal-20261010 | c200007f76376b0f9232c64d5bba76f86ec387c2 | R17 photon source-measure 증명 |
| bass_cr research/cr-r17-recovery-r17b1-20261010 | eb692c19c7cef3e3721f1e044ca3d41151d9309d | R17 복구와 R17B1 exact Peano 계수 |
| bass_cr research/cr-r17b2-source-kernel-20261010 | b5b81d0ec0b8eef6ff7f756615185aa4388f522a | 새 continuum photon response 구현 |
| bass_cr research/cr-r17b2a-physical-response-20261010 | eb692c19c7cef3e3721f1e044ca3d41151d9309d | 현재 R17B1과 같은 commit; 이름만으로 새 provider 존재를 추론하지 않음 |
| BASS_HE research/shared-c64-crossrepo-20260928 | 81c1dacc1439807d41dc2684619dee499f3e06b0 | E13C1 photon chronology/energy 검증 |
| WU088_HH research/ncp-energy06c-owner-birth-20261009 | 4071666330d46df1b1965465ae2697c3a10aeb01 | ENERGY06E source-bound receipt/certificate 계약 |

Git 파일 21개를 검색 결과가 아닌 실제 본문으로 회수하여 관련 계약·소스 부분을 읽고 보존했다. 동반 ATOMIC_CURRENT.json에는 정확한 URL·commit·Git blob SHA·크기·내용 표현 방식이 있다. 도구에서 의미 객체로 파싱된 JSON은 원본 바이트 복사로 주장하지 않는다. 게시 텍스트 3개도 실제 읽었으며 ZIP을 내려받거나 비공개 채팅에 직접 접근하지 않았다.

## 실제 CR 인터페이스: 어디까지 있고 무엇을 새로 구현해야 하는가

[현재 PHYSICS_CONTRACT.json](https://github.com/cosmosapjw-quantum/bass_cr/blob/eb692c19c7cef3e3721f1e044ca3d41151d9309d/docs/atomic_reionization_handoff_20261004_v1/threads/bass_cr/PHYSICS_CONTRACT.json)의 상태는 DERIVED_REFERENCE_IMPLEMENTED_NO_PHYSICAL_PROVIDER다. 명시적으로 미구현인 항목은 외부 단면적 intake, warm-target quadrature, interpolation, secondary cascade, CR transport, 실제 receiver binding이다.

[reference/cr_contract.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/eb692c19c7cef3e3721f1e044ca3d41151d9309d/docs/atomic_reionization_handoff_20261004_v1/threads/bass_cr/reference/cr_contract.py)는 p_fast, H_gas, H_fast, p_gas, e_free의 장부 참조 구현이다.

| 함수 | 실제 역할 | 새 구현에서의 취급 |
|---|---|---|
| event_delta(channel, events) | resonant CX, target ionization, stripping의 입자 장부 | 기존 p/H 의미를 보존 |
| number_rate(n_target, N, v, sigma, weights) | 주어진 quadrature의 n_target × 합 N v sigma weight | 실제 단면적·분포·tail 검증을 제공하지 않음 |
| cr_sources(enabled, event_rate_provider) | OFF이면 callback 전에 zero 반환 | 실제 receiver에서도 동일한 no-call 성질 검증 |
| close_energy(projectile_loss, ...) | 서로 겹치지 않는 에너지 항들의 잔차 | 잔차가 양수라는 이유만으로 물리 closure 성공이라 하지 않음 |

장부 계약의 단위는 gas rest tetrad의 proper second, N은 cm^-3 erg^-1 sr^-1, sigma는 cm², rate는 cm^-3 s^-1, 에너지율은 erg cm^-3 s^-1이다. j=vN 표현을 쓰면 속도를 다시 곱하지 않는다. 등방 4π는 실제 각도 적분을 한 경우에만 적용한다.

현재 p/H CX topology를 fast-electron H/He deposition이라고 이름만 바꾸면 안 된다. 새로 선택한 charged species와 별도의 process/domain 계약을 추가하고, 전자 한정 모델이면 proton·alpha·핵 cascade 및 MeV transport의 미지원 범위를 명시해야 한다. 외부 주입 spectrum/history와 문헌의 deposition kernel도 별도 입력이다. kernel 선택만으로 우주적 주입률이 정해지지 않는다.

공통 [AtomicProviderRecordV1 schema](https://github.com/cosmosapjw-quantum/bass_cr/blob/eb692c19c7cef3e3721f1e044ca3d41151d9309d/docs/atomic_reionization_handoff_20261004_v1/common/PROVIDER_CONTRACT.schema.json)는 deposition_fraction과 source_term을 이미 observable kind로 허용한다. source identity, units/frame, particle distribution, domain, 입출력 species, density prefactor, branches/floors, uncertainty, energy/photon closure owner, consumer admission, closure_id를 요구한다. 여기에 새 실제 provider를 연결할 수 있다. unresolved null을 consumer_admission=true로 바꾸는 것은 허용되는 구현이 아니다.

## R17·R17B1·R17B2를 새 CR 물리 입력과 구별

[R17 causal_source.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/c200007f76376b0f9232c64d5bba76f86ec387c2/research/cr_r17_20261010/src/causal_source.py)는 CDF moment와 외부 response bound를 사용하는 exact Fraction 계산이다. R17 handoff가 고정한 실제 대상은 FT03의 원 photon source S=f64(5e-15), 0..1.25e9 proper s, 여섯 birth와 가중치 family이다. HH/RCT/CR은 OFF이고 He photo가 비활성인 원 photon 에너지 범위다.

[R17B1 source_peano.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/eb692c19c7cef3e3721f1e044ca3d41151d9309d/research/cr_r17b1_20261010/source_peano.py)는 continuous-minus-discrete source measure의 moment defect와 jump-aware Peano 변환이다. kernel의 실제 물리 유효성이나 ODE solution을 이 모듈 자체가 인증하지 않는다.

새 [R17B2 source_kernel.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/b5b81d0ec0b8eef6ff7f756615185aa4388f522a/research/cr_r17b2_20261010/src/source_kernel.py)의 continuum_rhs, tangent_functional, photon_adjoint_rhs, adjoint_functional은 과거 광자 birth와 survival-memory를 포함하는 FT03 photon response이다. sigma는 H I photoionization 함수이고 gas heat는 흡수광자의 E−CHI_HI 항이다. charged injection callback이나 secondary-electron deposition callback은 없다.

R17B2는 full-eta common value tube와 coarse K0를 추가했지만 K1–K4, one-sided trace, complete partition 및 eta-integrated source error는 미인증이다. require_proof는 missing validated birth-resolvent jets를 명시하고 실패한다. 반환은 NO_CERTIFIED_SOURCE_SHARPENING, 새 source/combined interval은 null이다. 이 구현을 새 CR physical-provider 완료로 세면 안 된다.

기존 photon source와 새 charged source를 동시에 사용할 수는 있지만, 새 항을 넣으면 RHS와 초기값 문제가 바뀐다. R16/R17의 조건부 인증을 변경된 모델에 그대로 적용하지 않는다. 해당 증명을 반복하는 작업은 새 provider 구현의 선행 blocker가 아니다.

## HE·HH의 최신 결과가 제공하는 것과 제공하지 않는 것

HE E13C1은 여섯 frozen photon transaction에서 retarded absorption과 에너지 분배를 검증했다. 직접 읽은 RETURN의 actual RCT photon/heat/recoil moments는 null이고 baseline RCT OFF, owner adoption=false, physical/production HOLD다. photon count나 endpoint N/U만으로 누적 열을 정할 수 없고 birth/absorption chronology가 필요하다는 결과는 새 deposition ledger 설계에 유용하다. 기존 35 eV RCT 연구 closure를 실제 secondary-electron source로 사용하지 않는다.

HH ENERGY06E는 gas4·photon128×33·guard·interval·compensation·HH ledger를 포함한 exact accepted half1 predecessor receipt를 half2에 요구한다. weights-only를 receipt로 만드는 API는 없다. 실제 accepted half1 producer/permit, source-bound derivative producer, root/family certificate와 full C1 box는 여전히 OPEN이다. 새 scientific dispatch/root/integration은 0이다. 이것은 새 CR source를 실제로 소비하거나 인증했다는 증거가 아니다.

따라서 다음 변경 범위를 권고한다.

| 저장소 | 이번에 필요한 변경 | 바꾸지 않아도 되는 독립 연구 |
|---|---|---|
| bass_cr | 문헌에 결속된 실제 charged injection/deposition provider, 명시적 정의역·단위·에너지 분할 및 focused 검증 | 기존 FT03 photon source 증명, p/H 정밀 충돌 lane |
| rei_bianchi | 실제 H/He species·thermal RHS에 새 항 연결, CR OFF no-load/no-call, input/domain·보존 검증 | 새 source 없이 수행된 과거 인증 원본 |
| BASS_HE | 필요 시 새 provider·consumer source pin/status 연결 | RCT atomic moment를 임의값으로 채우거나 HE 연산자 변경 |
| WU088_HH | 필요 시 새 provider·consumer source pin/status 연결 | HH operator·root family·C1 certificate 변경 |

rei_bianchi의 최신 실제 코드와 API는 별도 intake의 소유자 검토를 따른다. 여기에서 읽은 HH의 original_owner_dependency 복제본을 현재 rei HEAD와 동일하다고 가정하지 않는다.

새 소비자는 ionization count와 threshold energy, stored excitation과 방출 광자의 중복, heat, continuum/escape/unallocated를 구분해야 한다. 외부에서 추가되는 charged particle과 이미 집계된 원자에서 생기는 secondary electron도 구분하고 charge-balancing reservoir/장부를 명시한다. source를 gas의 total energy와 photon heat에 두 번 더하는 연결은 피해야 한다.

## 게시·증거 해석

세 저장소 root AGENTS.md와 bass_cr READBACK_POLICY.md를 읽었다. 기존 frozen source·checkpoint·실패 기록을 보존하고 과학 gate와 publication gate를 분리한다. 새 사용자 지시의 관련 저장소 push 권한은 과거 donor 문서의 read-only 업무 분담과 별도로 적용된다. 이 intake 자체에서는 push하지 않았다.

bass_cr의 일반 additive push는 expected/observed ref SHA를 맞추는 R1을 기본으로 하되, 외부 자료 import나 trust boundary에 해당하면 해당 객체에 국한한 R3 근거가 필요하다. 원격 저장 성공과 물리 provider admission은 서로 다른 판정이다.

게시 파일에서 읽은 R17 초기 receipt의 NOT_PUSHED 상태는 뒤의 R17B1 recovery receipt와 현재 Git HEAD로 갱신되어 있다. HE 게시 파일에는 이전 PHOTON_HEATING pending receipt가 남아 있지만 최신 Git에는 다른 PHOTON_PHYSICS archive와 실제 publication receipt가 있다. 두 artifact의 이름·hash가 다르므로 같은 ZIP으로 합치거나 과거 pending 상태로 최신 Git을 덮어쓰지 않는다. R17B2·ENERGY06E의 좁은 게시 파일 검색은 추가 결과를 찾지 못했으며 이것을 미게시 증명으로 취급하지 않았다.

이 intake는 코드·문서 근거를 정리한 것이며 donor 과학 결과의 재실행 또는 독립 물리 승격 리뷰가 아니다.

