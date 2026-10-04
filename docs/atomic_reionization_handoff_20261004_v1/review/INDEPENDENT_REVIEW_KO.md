# 독립 검토 — 원자 입력 외부화와 재이온화 실행 handoff

검토일: 2026-10-04. 결론: **검토한 계획·물리 인터페이스·작업 의존성 범위에서 남아 있는 차단급 오류를 발견하지 않았다.** 아래 네 수정이 반영된 게시용 handoff를 확인했다. 원자율의 물리 정확도, 실제 Rust 구현, 비선형 구간 인증 또는 재이온화 이력의 PASS를 뜻하지 않는다.

## 검토 범위와 실제 확인

공통 계약, 네 스레드 PREWORK/TASKS/CODEX_START/legacy 계약, 외부 source lock, GLOBAL_DAG/PROGRAM/task selector를 읽었다. 원자 원계산·전체 저장소 suite·과학 runtime은 재실행하지 않았다. 네 스레드의 실행 기록은 해당 레코드의 범위만 인정했다.

- 31개 전역 노드의 ID가 유일하며 모든 선행 ID가 정의되어 있고 DAG가 비순환임을 독립 검사했다.
- REI-F08 baseline의 선행 집합에 HH/HE/CR 원자 task가 들어 있지 않다. 이 baseline의 수치 인증 자체는 여전히 필요하다.
- HH-F2와 HE-F2 공급 결과를 REI-F09의 한 감도 campaign이 소비한다. HH-F3와 HE-F3는 그 결과를 검토·수락하며 같은 이력을 별도로 재실행하지 않는다.
- REI-L01은 명시적 trigger로 호출할 수 있고 F09를 보편적인 선행조건으로 요구하지 않는다. parked 확장은 task selector가 자동 실행하지 않는다.
- Grackle 선택 원본 4개는 source lock의 SHA-256/크기와 일치했다. 원문 LICENSE가 함께 있으며 reference-only와 build-not-run 상태가 명시된다.
- Verner H/He 3종 계수에는 단위, 식, below-threshold/above-domain/error 동작이 있다. fit threshold 반올림값과 physical threshold의 선택은 여전히 소비자 계약에 명시해야 한다.
- low-cost selector는 카드만 출력하고 명령·과학 상태를 실행하거나 변경하지 않는다. 완료 상태의 추가는 반환 증거와 acceptance를 검토한 조정 담당의 책임이다.

## 확인한 물리 경계

CR-off에서는 CR 분포를 0으로 정의하므로 충돌원을 정확히 소거한다. 이는 현실 CR 영향의 작은 오차 상계와 구별되어 있다. 핵수·전하 반응 벡터, resonant CX의 aggregate 자유전자 0, He²⁺–H CX의 직접 자유전자 0도 일관적이다.

proper thermal density의 팽창항 −5Hu와 extensive energy의 −2HU는 구별된다. 이온화 threshold, 재결합 전자 냉각, 방출 결합에너지, 광가열의 소유권을 분리한다. scalar RCT k(T)만으로 방출 스펙트럼·열침적을 복원하지 않으며 mono-Q는 명시적인 별도 근사로 남는다.

GM25/W82와 KF96의 17배 차이는 문헌 선택 감도이며 엄밀한 상·하한이나 신뢰구간이 아니다. 공통 온도 영역 밖의 clamp를 허용하지 않는다. mixed H/He OTS를 종별 Case-B 호출만으로 완성 처리하지 않고, secondary ionization을 X-ray 유무만으로 면제하지 않는다.

homogeneous bound-free opacity와 기존 effective-MFP 모형은 별도 model ID로 분리된다. 같은 rate choice를 FLRW/Bianchi에 함께 적용하되 모형 spread와 수치 enclosure를 합치지 않는다. Grackle k57에 추가 1/2를 붙이지 않으며 3000 K의 불연속 floor를 smooth cutoff로 취급하지 않는다.

rei의 implicit-map recipe는 선언된 매끄러운 domain 및 uniform contraction/interval 가정 아래 parametric root inclusion, implicit Jacobian/Hessian, sparse Taylor remainder, augmented-coordinate composition을 일관되게 연결한다. point AD나 작은 Newton 잔차를 uniform enclosure로 승격하지 않는다. 실제 R_y, 도함수 상계, residual certificate는 아직 계산할 작업이다. 선택적 SymPy 검사는 환경 부재로 미실행된 것으로 기록되어 있으며 이 검토는 그 실행 성공을 주장하지 않는다.

## 발견하여 수정한 사항

| ID | 문제 | 확인한 수정 |
|---|---|---|
| R01 | 새 homogeneous map에 46,080-node inherited parent를 자동 강제할 여지 | successor parent/state/lane 의미를 별도로 고정. 46,080은 해당 inherited 구조에만 적용하며 과거 실패를 승격하지 않음 |
| R02 | shell 문자열 끝의 괄호 설명이 실행 시 syntax error를 일으킬 수 있음 | bass_cr command와 실행 조건을 분리. 명령 문자열에는 shell만 유지 |
| R03 | 스레드별 반환 envelope 및 HH 상대 schema 경로 불일치 | 공통 RETURN_CONTRACT envelope로 통일하고 repo 상세는 부가필드로 유지. HH 경로의 실제 파일 존재 확인 |
| R04 | REI-L01의 F09 강제 선행조건이 앞선 REC/secondary 필요와 즉시 재호출을 막음 | 명시 trigger와 선택 확장 자체의 prerequisite으로 분리. GLOBAL_DAG에서 F09 의존성 제거 확인 |

## 종료와 한계

이 검토는 여기서 종료한다. 문서·게시 receipt만 추가되면 동일 과학 감사를 반복할 필요가 없다. 실제 source, process, domain, energy closure, map topology가 바뀌면 바뀐 부분만 검토한다. 기존 원자 gate와 소비자 실패는 모두 원래 상태로 보존되어야 한다.

검토 시점의 핵심 파일 identity는 `REVIEWED_CONTENT_IDENTITIES.json`에 있다. 이후 GitHub 게시 ACK·Drive/Dropbox 백업 ACK·복구 검증은 별도 publication receipts의 근거를 따르며, 이 리뷰가 그것들을 대신하지 않는다.
