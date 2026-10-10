# Decision log

## D01 — 실제 복구와 채택 권위

현재 실행 환경에서 이전 파일을 찾지 못해 RUNTIME_INTERRUPTION_RECOVERY로 분류했다. 내구 백업 ZIP의 실제 bytes와 내부 124개 payload를 크기·SHA256으로 검증해 복구했다. 과학 권위는 PHYS02B science `929abd7f`, 운영 최종 head `b5b0f224`다. 별도 branch의 PHYS02C 표·kernel·convolution은 1–3 keV 및 다른 하류 모형으로 정의되어 있어 이 연구의 0.1–900 eV 연산자에 혼합하지 않았다.

## D02 — 새 후보의 물리 정의

동일 진동자 세기에서 BED 분포와 총률을 함께 유도한다. H는 양의 analytic Coulomb oscillator, He는 Kim2000의 원래 인쇄 계수를 채택했다. 원문 및 독립 모멘트 계산을 먼저 읽고 계약을 고정했으며, 수송 결과를 보고 계수를 선택하지 않았다. NIST Q만 다른 숫자로 바꾸는 방식은 full BED와 동일하지 않으므로 사용하지 않는다. 기존 NIST hybrid는 공식 정규화 설명과 관련된 별도 근사로 유지해 비교한다.

## D03 — 비교에서 고정하는 물리

source, bath, CCC27 native effective costs, Coulomb 항, 0.1–900 eV 경계, birth tag, 최종시간을 고정한다. CCC spectroscopy 해석은 독립 source audit로 분리한다. 근거 없는 에너지 비용 교체나 입사 에너지축 이동을 수치 비교에 끼워 넣지 않는다.

## D04 — 수치 판정의 범위

2400·4800 node 새 계산을 실제로 실행하고, 복구된 이전 같은 격자 결과와 짝지어 비교한다. 두 격자 차이와 paired model delta의 상대 변화는 경험적 지표이며 물리 오차 상계가 아니다. 기존2%/3% 및 보존·적분 허용값은 유지한다. 의미 있게 미분리된 결과는 미분리 상태로 보고한다.

## D05 — 작업 분담과 실제 모델

2026-10-10 owner tier-routing 정책을 새 작업에 전향적으로 적용한다. Astra가 과학 계약·모형·독립 판정을 맡고, 구현·시험·NCP 기계 절차는 명시적 `fork_turns=none, model=gpt-6.1-sol` 도구 인수로 요청한 작업자에게 맡겼다. 도구는 이 요청을 수락했지만 하위 작업자의 host 자기표시에는 GPT-6 Astra Pro가 남아 있어 실제 backend 모델을 독립적으로 확정하지 못한다. `requested_model_route=gpt-6.1-sol`, `actual_runtime_model=UNVERIFIED_CONFLICTING_METADATA`를 함께 보존하고, 측정된 lower-tier 실행 또는 성능 절감이라고 주장하지 않는다. 작업 권한은 동결 계약의 기계적 구현으로 제한된다. 병렬 branch의 과학 권위는 이 정책 적용으로 가져오지 않는다.

## D06 — NCP 전달 설계

사용자가 추가 전달 파일 없이 시작하도록 요청했으므로 시작 prompt, 계약, 코드, raw atomic 입력과 parent 코드, 저장된 비교 결과, resource admission, 결과 수집기를 하나의 완결 ZIP에 넣는다. 새 source-defined 모형이 독립 검토를 통과하면 NCP의 다음 단위는 두 모형의 matched9600 격자 비교다. 현재 NCP 하드웨어·접속·실행은 관측하지 않았으며 PREPARED_NOT_EXECUTED로 기록한다. 광고상64CPU를 그대로 rank 수로 쓰지 않는다.

## D07 — 독립성과 publication

최종 decision reviewer는 소스 후보 설계·구현·검증 실행에 참여하지 않은 별도 Astra로 지정한다. 모든 global gate는 이 국소 비교에서 바꾸지 않는다. 사용자에게 이미 허용된 연구 branch·draft PR·additive dual backup을 완료하고 정확한 파일 위치를 전달한다.
