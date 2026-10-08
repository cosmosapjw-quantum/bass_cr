# 원자물리 전용 범위와 원자 데이터 완료조건

사용자의 최신 지시를 적용한다. Bianchi 배경·shear/tilt·우주론 수송·재이온화/열 이력·실제 host 진화 검증은 `rei_bianchi`가 담당한다. 이 스레드는 BASS_CR의 원자 충돌·선택상태 포획 데이터와 그 수학·수치 오차를 완성한다. 이전 R4AI에서 만든 Bianchi-I 참조 모듈은 삭제하지 않고 역사적 read-only 자료로만 둔다. 이를 다음 연구 필수항으로 확장하지 않는다.

## 원자 데이터의 우선 산출물

`H+ + H(1s) -> H(1s) + H+`의 selected-1s 확률 `P_1s(E,b)`를 먼저 자격검증하고, 필요한 impact-parameter 적분과 에너지 영역을 닫아 `sigma_1s(E)`를 제공한다. 상태·spin/degeneracy 규약, 에너지 변수(E_lab/E_CM/keV/u)와 질량, 단위·문턱·유효범위·보간/외삽 정책·수치오차·물리모델/source 오차 및 정확한 출처/코드 identity를 함께 낸다. 고정 b 한 점을 단면적으로 바꾸거나 1s 결과를 total capture로 읽지 않는다.

정의된 분포에 대한 local rate coefficient가 실제 데이터 요청에 필요하면 원자 데이터의 파생항으로 계산할 수 있다. 그러나 CR 스펙트럼·우주론 밀도·배경·x_e(z)·열이력은 이곳에서 모델링하지 않는다. Formation count만으로 자유전자 source, 운동량전달 또는 heating을 만들어 내지 않는다. 그 출력이 필요할 때에만 적합한 differential kernel/moment와 별도 오차가 필요하다.

## 선행조건의 분리

원자 source의 정확도 검증은 소비자 repo의 first-step 실행을 기다릴 필요가 없다. 반면 실제 `rei_bianchi` 연결 완료를 주장하려면 소비자 측 실제 수락이 필요하다. 이곳은 입출력 데이터 규약까지만 맡으며, 최신 rei_bianchi 코드나 host를 이 변경에서 읽거나 검증했다고 하지 않는다. 기존 C0/B2 host 결손은 삭제하거나 CLOSED로 바꾸지 않고 consumer 소유의 후속 통합문제로 위임한다.

## 지금 진행할 원자 단계

다음 로컬 작업은 `LOCAL_RESONANT_PAIR_WEAK_BRIDGE_ENVELOPE`다. 측정은 P1s로 유지하고, T1s/P1s 공진쌍을 내부 동역학에 남긴 상태에서 제거공간 coupling·도함수·connection 및 내부 전이 항을 구분한다. 저장 9x9 행렬의 gap >=0.373Eh를 실제 유한거리 bridge 상계로 상속하지 않는다. 원기저·weak operator·초기상태와 연결된 실제 연속 bound가 필요하다.

외부 첫 작업은 기존 코드의 `R4AH_m64`뿐이다. 자원 승인 후 별도 one-shot 계약에서 실행하고, 정확한 반환이 수락될 때에만 remaining9를 별도 batch로 연다. 원 R4AF 중심점과 M9/window jet, 옛 R8 및 완료된 과학 suite는 반복하지 않는다.

## 상태

R4AJ의 선택자/공진 판별은 완료된 유한 행렬/reference 결과다. 실제 physical bridge, shifted stencil, 산란창, coupling basis, b 적분과 물리 반응률은 별도다. G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. 이 범위 수정은 새로운 과학적 PASS를 만들지 않는다.
