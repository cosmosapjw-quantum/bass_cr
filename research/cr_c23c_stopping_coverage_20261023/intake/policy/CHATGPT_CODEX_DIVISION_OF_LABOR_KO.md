# 연구 코드 분업: ChatGPT 구현, 클라우드 Codex 점검·수정·실행

사용자 지시 적용일: 2026-09-28. 이 문서는 bass_cr 프로젝트의 앞으로의 작업 기본값이다. 새로운 과학 계산/비용/권한을 승인하지 않는다.

## ChatGPT의 기본 책임
현재 source와 evidence를 직접 읽고, 승인된 범위의 제품 코드·회귀 수정·테스트·실행기·복구/패키징 코드를 여기서 완성한다. exact source/tree 및 artifact identity, 실제 신규 검증 결과, 최소 cloud 명령을 함께 GitHub에 게시한다. 계획만 넘겨 Codex가 처음부터 주요 기능을 다시 구현하게 하지 않는다.

## Cloud Codex의 기본 책임
전달된 수정본의 관련 diff와 핵심 계약을 집중 검토한다. 실제 환경의 문제나 재현된 결함은 scope 안에서 수정하고 영향을 받는 신규 테스트를 수행한다. 준비된 실행기를 승인된 조건에서 실행하고 결과·수정 diff·receipt를 GitHub로 반환한다. 기존 로직을 이유 없이 재설계하거나 미완성 기능을 전부 떠맡지 않는다. 중요한 결함 때문에 변경 범위가 커지면 최초 실패와 최소 수정 필요사항을 반환한다.

## 비용과 정확성
완료된 source/test가 그대로이면 같은 suite를 반복하지 않는다. 환경 최초 확인은 작은 environment/CLI/cache smoke로 하며 새 과학 계산 승인과 분리한다. 실제 코드/환경이 변한 영향 범위에서는 focused validation을 생략하지 않는다. 큰 read-all/review-of-review 루프는 금지한다. 이미 소비된 one-shot authorization은 새 코드로 재사용하지 않는다.

독립 review가 수행되지 않았으면 미수행으로 표시한다. 이 분업은 capture, production, all-bound, b-grid의 claim gate를 완화하지 않는다. 다른 저장소나 전역 harness 설정은 이 문서로 변경하지 않는다.
