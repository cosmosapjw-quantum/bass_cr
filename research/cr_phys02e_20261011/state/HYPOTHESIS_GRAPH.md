# PHYS02E 가설과 분기

원자료: PR33 `INDEPENDENT_ACTUAL_RETURN_DECISION.json`과 `GRID_DIAGNOSTIC.json`.

| 가설 / 후보 | 현재 판단 | 결정 근거 |
| --- | --- | --- |
| 버전 문자열이 같으면 재생성 E도 exact 동일 | 실제 반환으로 기각 | Py3.12.3/NumPy2.4.2/SciPy1.17.0에서도 340/9600 nodes 1 ULP 차이 |
| 원인은 특정 SIMD/libm 구현 | UNRESOLVED | 진단은 차이를 측정했으며 저수준 원인 비교를 수행하지 않음 |
| E 불일치를 allclose로 허용 | 이번 계약에서 제외 | 저장 b와 G 및 1/E 장부의 좌표 결속을 느슨하게 함 |
| G 뒤 self.E만 치환 | 기각 | 에너지 장부가 영이어도 보정 수 장부가 깨지는 정확 반례 |
| 저장 E를 생성자 계산 전에 설치 | 채택, 독립 검토 대상 | 원래 수치 메서드·원자 모델·b·허용오차를 보존하는 명시적 생성자 |
| exact E이면 실제 pulse 정확도도 보장 | 기각 | 같은 E에서 rate만 달라도 보존식은 영이며 시간 응답은 달라짐 |

다음 분기 하나만 준비한다: 새로운 독립 검토를 통과한 PHYS02E 코드에서 fullBED→legacy 순서, 각 G/pulse 1회. 실패하면 현재 반환을 보존하고 다음 Astra 판정을 기다린다. 이전 PHYS02D 예약의 남은 수량을 합산하지 않는다.
