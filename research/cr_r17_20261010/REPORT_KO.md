# R17A 이론·증거 위치

이 Git 경로의 README_KO.md는 전체 유도의 축약이며, src/causal_source.py와 inputs/R17_COMPACT_INPUT.json은 실제 검증한 경량 계산을 독립 실행하는 정본이다. 실행 명령은 python -B research/cr_r17_20261010/portable.py --output NEW_RESULT.json이다. core Git blob a5381e42966ed849f09b550bde894dfb901f8d08,7430bytes; portable blob65f198c7acdf6bf59681ed0a0afcbe79a0806bf7,1774bytes다.

전체 상세 유도·선택 원문·manifest·23개 시험·독립 검산·실패 로그는 BASS_CR_R17_20261010_v2.zip의 REPORT_KO.md 및 inputs/,tests/,logs/,results/에 보관한다. 실제 원격 object와 ZIP hash/size는 이 Git 경로의 DELIVERY_RECEIPT.json을 따른다. 선택 입력 전체나 ZIP 바이너리까지 Git에 게시됐다고 주장하지 않는다. Compact JSON은 같은 정확 유리수 값의 재배열이며 whitespace byte identity와 numerical identity를 구분한다.

## 핵심 조건부 정리

D*(b)=max(Sb−L(b),U(b)−Sb)는 원 여섯 birth의 모든 허용 weight에 대한 CDF 차이의 envelope다. 원 positive gas tube에서 누적흡수 kernel A(t,b)=1−exp(−∫b^t κ)는 A(t,t)=0과 |∂bA|≤k+(t−b)kb를 만족한다. Stieltjes 부분적분으로 B(t)=∫0^t D*(b)[k+(t−b)kb]db가 직접 normalized gas source차를 감싼다. Thermal derivative/W0가 k 이하임을 원 상계의 비음수 다항식으로 확인한다.

부모 full-window gainγ의 각 항은 prefix t에서 nonnegative t 또는 t²에 비례하므로 gain(t)≤γt/T이다. E∞≤B(T)/(1−γ), E(t)≤B(t)+γtE∞/T를 얻는다. 따라서

    |τS−τQ| ≤ CT*nH0*(1+3fHe)*∫0^T exp(−3Ht)[B(t)+γtE∞/T]dt

이다. 원 정확 birth boxes, density의 degree5/6 exp brackets와 Fraction moment 계산으로 상단2.125533135951863662132892058883214693751…e-18을 얻었다. 이는 actual source차의 부호 판정이 아니라 절댓값 상계다. Common tube/커널 상계/구간산술은 부모 증거에 조건부다.

R16B time interval에 source상계를 한 번만 합치면 [1.726968178866034690190055439800249300664…e-17,2.219287238809879417339730677747077477803…e-17]이다. 기존 source radius 대비79.1975993%, 결합 구간 폭은76.6757270% 개선됐다. 새로운 native/IVP/원자 계산은0이며 원 source/physics/admission을 바꾸지 않았다.

R17B의 signed kernel/θ-family 검증은 아직 수행하지 않았다. NCP_HANDOFF_PROMPT_KO.md가 해당 중량 후속 실행 계약이다. 물리적 승인·관측자 tail·G02 등 기존 제한을 유지한다.
