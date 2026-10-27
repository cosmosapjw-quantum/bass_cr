# R6 독립 이론 심사

판정: **PASS_SCOPED_AFTER_TARGETED_REPAIR**. 새 THEORY를 처음 받은 별도 source-reader/reviewer가 1차 심사했고, 작성자가 고친 두 항목만 같은 repair episode에서 재확인했다. 현재 범위의 미해결 material finding은 없다.

## 고정한 검토 대상

- 최종 THEORY SHA256: `3e5f31d271c32efcd1ee9a1eb23625c2ead0dc0b6c4a78732de34ef4a696ceae` (10092 bytes).
- 첫 R6 읽기 SHA256: `d990ac67b8732a5485780e5cb9fdce8b73bc03d1898b34c97fdb8526774361c0` (9912 bytes).
- 실제 원격 branch HEAD: `030c532936281f4112d3b8aad1406837bc1cb60f`. 로컬 과학 원본 checkout HEAD는 고정 D `b11b2e9255f2b10fb5582376412e045bd1e9151c`이며, 위 최종 THEORY는 R5 게시 뒤의 두 작성자 수정을 포함한다.
- 현재 bass_cr AGENTS SHA256: `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`.

## 확인 결과

원전의 HeII ground row·Milne 관계·통계무게는 d=1과 HeIII target density를 지지한다. K0는 저장된 HeI 대각의 정확한 수치 피연산자이며 과거 intended-real-sum을 재구성하지 않는다. 이 선택 아래 M-matrix 역행렬 순서, 단일 추가 hazard의 양쪽 bound, 안정 응답, 저장 열의 residual identity와 양의 시간 벡터를 이용한 bound가 대수적으로 성립한다.

Partition과 energy defect는 기존 저장 행렬의 결함을 정확히 운반한다. Conditional moments는 공통 event measure의 비이며 zero-event는 null이다. Signed bath reward에 비음성 단조성을 적용하거나 conditional 비의 단조성을 주장하지 않는다.

실제 HeI NPZ의 header, 원래 16열 생성문, input manifest 및 PR236 native21/25 source 코드를 대조했다. Native He4III index12→He4II index11과 fast-electron 제거는 charge-derived electron과 thermal count를 일관되게 보존한다. 내부 에너지는 native ionization vector가 소유하고 retained photon은 별도 port로 나간다. 기존 w_ext를 retained photon으로 재해석하지 않는다.

## 두 finding과 최소 수정의 종료

| ID | 실제 결함과 영향 | 확인한 작성자 수정 |
|---|---|---|
| R6-001 | cm⁻³/eV cm⁻³ 적분값을 native SI nb로 나누는 식에 SI 표지가 빠져 literal 구현에서 10⁶ 및 eV→J 변환을 누락할 수 있었다. | N3^SI=10⁶N3, Ue/γ^SI=10⁶eV_J Ue/γ, nb[m⁻³]를 정의하고 a와 retained ports 모두 SI 변수를 사용했다. |
| R6-002 | physical18의 inherited reward 문장이 실제 16열 구조와 불명확하게 대응했다. | 0–5 first6, 6–7 H1, 8–9 HeI, 10–11 새 HeIII, 12–17 bath6를 명시했다. |

두 수정은 단위·열 결속을 명확히 했으며 고정 acceptance를 바꾸지 않았다. 수정 전후 identity와 object/evidence/consequence/minimum-repair는 R6_THEORY.json에 기록했다.

## 검토 범위

R2 문헌 지원에 참여했지만 새 R3–R5 이론이나 native25 사상을 구성하지 않은 agent의 독립 심사다. R4 유리수 예제는 손 대수로 확인했다. 과학 Python suite, CAS, 기존 solve/projection 재실행, producer 수정, 원격 변경은 모두 0이다. Root가 별도로 실행한 R7 CAS를 이 심사의 독립 근거로 계산하지 않았다. 읽기·해시 비용은 미계측이며 과학 실행 비용 0과 구별한다.

N6/N7, 과거 UNKNOWN_NO_ACK와 예산, WU/REC/HE 유효범위·isotope mapping 및 caloric partition과 실제 heating의 구분을 유지한다. 새 strong no-go가 없으므로 NG1–NG7 신규 채택은 해당하지 않는다. 실제 수치 실행·C9 검증·publication은 별도 단계이며 이 R6 결과가 대신하지 않는다.

