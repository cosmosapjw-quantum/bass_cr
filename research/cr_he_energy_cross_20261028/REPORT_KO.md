# bass_cr 재개 결과: 에너지 조건 아래의 출생 구간 간 중복 사건 상계

## 결과

이번 독립 단위 CR_PHYS02_HE_ENERGY_CROSS_V1은 고정 PHYS02 He 출생 전자 marginal에서, 서로 다른 birth-energy bin에 걸친 동일 부모 사건의 중복 계수 C를 직접 최적화했다. 에너지 조건 E_i+E_j<=K 아래의 정확한 상계, 원자별 marginal을 보존하는 달성 구성, 기존 같은 상태의 source-union consumer 연결을 완성했다. 과학 판정은 PASS_SCOPED_EXACT_CROSS_ENVELOPE다.

이전 대화와 실제 원격 저장소를 함께 확인했다. PR112는 완료돼 있었고, 후속 PR113과 PR114가 별도로 진행 중이었다. PR114의 C08 snapshot c87c50208a7585ff1713bd54303e1a1e29c962cf를 읽었으며, 이후 owner head3230790ebeb2657c3a222a2bdc1d043b7d745492도 관찰했다. 두 owner branch는 수정하지 않았다. 이번 결과는 별도 research/cr-he-energy-cross-envelope-20261028에 보존한다.

PR114는 전체 내부 double 수 d를 최적화하며 C는 선택된 한 witness의 값이다. 이번 단위는 C 자체의 최댓값을 계산한다. 두 목적량의 joint fixed-d feasible region은 별도 문제다.

## 고정 자료와 단위

Retained PHYS02 revision4ca5a90de79c8fb82a25fd9e83615bec0dfa870b의 direct_0p1_10 source를 재사용했다. 원 NPZ SHA256은1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47이다. 기존 SOURCE ZIP의 실제 bytes를 복원해 대조했다. source-fit, projection, transport, RR 재실행은0이다.

원자는3,200개 active atom과 별도 cutoff ghost 하나다. 네 분할은 cutoff ghost,active(0.1,1],(1,3],(3,10]eV다. 저장 binary64 값을 정확한 Fraction으로 올렸다. 원 target·clock·proper-volume·정규화 인자를 다시 곱하지 않았다.

기존 conditional100K H1/He4 inventory,nb=8750/47m^-3,gas-rest 비상대론적 scalar,zero recoil,고정 proper volume을 유지했다. q_i(t)=t A_i의 history는 proper[0,10^10]s이며 밖은 미공급이다. A_i와 C의 단위는m^-3s^-2,W=(b^2-a^2)/2의 단위는s^2다. 전체 prefix의 출생 전자 밀도는 WN=7.943146027889112e-17m^-3다.

## 정확한 최적화와 유도

유한 atom의 에너지·질량·bin을 E_i,w_i,b_i라 한다. 허용 edge는 i<j,b_i!=b_j,E_i+E_j<=K를 만족하는 쌍이다. x_ij>=0,sum_j x_ij<=w_i를 요구하고 잔여 legs는 singles로 둔다. 목적량은 C=sum_edges x_ij다.

N=sum_iw_i,독립집합 I와 열린 이웃 Gamma(I)에 대해

    Delta=max_(I independent)[w(I)-w(Gamma(I))],
    Cmax(K)=(N-Delta)/2.

빈 집합도 포함한다. 일반 fractional matching/weighted vertex-cover 쌍대성은 기존 정리다. theory/SOURCES.md의 Nemhauser–Trotter1975,Chlebík–Chlebíková2008 원전과 직접 유도를 대조했다.

이번 graph에서는 독립집합의 최소 에너지 e를 갖는 bin을 r,그 밖 최소 에너지를 h라 두면 h>=e,e+h>K다. 밖의 원자가 없으면 h=infinity다. 독립집합을

    {b=r,E>=e} union {b!=r,E>=h}

로 늘려도 이웃은 늘어나지 않고, 그 이웃은 정확히

    {b!=r,E<=K-e} union {b=r,E<=K-h}

다. 따라서 두 문턱과 bin별 누적질량으로 Delta를 계산한다. h>=e는 inclusive,h>K-e는 strict이며 동률 에너지 전체 level을 보존한다.

구현은 suffix maximum과 이분검색을 사용한다. 비용은 O(k n log n) 비교·유리수 산술 연산이고 bit cost는 별도다. 명시적인 primal은 bipartite flow를 x_ij=(f_ij+f_ji)/2로 대칭화해 얻는다. 완전 cross support의 K20은 PR112 half-shift를 사용하고 같은-bin pair를 제거한 직접 구성으로 완성했다. 원자별 marginal·허용 support·feasible dual과의 objective equality를 검사한다. 전체 증명은 theory/THEOREM.md에 있다.

## 실제 저장 source의 결과

정확한 유리수 결과의 표시용 반올림이다. Chemical 열은 보정 구간의 하단이며 상단은0이다.

|조건부 K[eV]|Cmax/N|W Cmax[m^-3]|chemical 보정 하단[eV m^-3]|
|---:|---:|---:|---:|
|0|0|0|0|
|1/5|0|0|0|
|2×stored ghost energy|0|0|0|
|1|0.000244557200547336|1.942553556119252e-20|-1.534811564689821e-18|
|2|0.123021871571740|9.771806905185497e-18|-7.720704635787061e-16|
|3|0.135346102595452|1.0750738572213353e-17|-8.494158545905770e-16|
|6|0.345345499798891|2.7431297349769416e-17|-2.1673468036052815e-15|
|10|0.394559816720470|3.134046240947860e-17|-2.4762099349729043e-15|
|20|0.394559816720470|3.134046240947860e-17|-2.4762099349729043e-15|

K를 키우면 허용 pair만 늘어나므로 Cmax는 단조 증가한다. K10에서 이미 PR112의 무제약 cross 상계에 도달한다. 이는 이 고정 marginal의 결과이며 실제 물리 K=10을 뜻하지 않는다.

K=2Eghost는 동일 atom의 diagonal 문턱이다. 이번 cross graph에는 loop가 없으므로 그 문턱만으로 사건이 추가되지 않는다. 1/5와2Eghost의 decimal/binary64 차이를 보존한 채 둘 다 Cmax=0을 확인했다.

## 같은 상태의 consumer

구간별 source 반환을 합하면 서로 다른 bins의 동일 double event에서 부모 사건을 중복 계산할 수 있다. 정확한 union 보정은

    Delta(He4I,He4II,He4III)=W(C,0,-C),
    Delta Q_ion=-2WC,
    Delta U_chem=-(24.59+54.42)WC.

전자 수·선택된 운동에너지·RR·retained-photon의 보정은0이다. Source union 또는 corrected partition sum 중 하나를 한 번 사용하고 savedRR을 한 번 붙인다. Native species correction은 W(C,0,-C)/nb다.

이 chemical correction은 이중 계산을 제거하는 저장 에너지 보정이다. 실제 가열·냉각량,EOS/온도,projectile donor debit 및 full-source physical native25는 기존 입력 의존성을 유지한다.

전체 double 수 d와 cross C를 구별했다. Inventory 제약 W(N-d)<=Hneutral을 일반적으로 C의 하한으로 바꾸지 않았다. 현재 source는 all-single endpoint조차 neutral inventory 아래임을 실제 값으로 확인했으므로 이 조건부 C 구간에서는 inventory가 제한으로 작동하지 않는다.

## 검증

|근거|실제 결과|
|---|---|
|독립 일반 small-graph oracle|116/116(named20+seeded96)|
|기본 domain/certificate 거부 controls|20/20|
|정적 감사 뒤 표적 repair|8/8+positive exact case|
|원 NPZ와 atom 대조|3,201atoms,12,804fields 정확 일치|
|Native cap dual|9개,모든 허용 edge를 prefix minima로 완전 검사|
|허용 관계 coverage|cap별 총4,960,229; 개별 edge list 생성 주장은 하지 않음|
|명시적 primal attainment|K0,3,20의3개|
|Primal marginal|9,603개 정확 일치|
|독립 저장 consumer|3개 main-window 결과 정확 일치|
|추가 primary check|K3 인접 proper windows additivity와4개 native 거부 gate|
|그림|저장 결과만 렌더링,root의 실제 PNG inspection PASS|

Primal-dual gap과 marginal residual은 정확히0이다. 나머지6개 native cap은 exact upper certificate와 완결된 sharpness theorem으로 판정하며 각 explicit primal을 실행했다고 주장하지 않는다.

독립 evaluator는 원 NPZ를 직접 읽고 production solver·source loader를 import하지 않는다. Reviewer와 code author는 별도였지만 문제 문맥을 공유했으므로 blinded review로 표시하지 않았다.

## 실패와 표적 복구

native_v1은 K20의 일반 prefix-chain flow 중 exit-9로 종료됐고 charge23.924732CPU-s로22CPU-s reservation을 넘었다. 외부 종료 원인은 별도 kernel 로그로 확정하지 않았다. 긴 chain의 실행 비용과 reservation 초과는 관찰된 사실이다. 완료된 앞8개 cap은 원본으로 보존하고 독립 검증에서 같은 bytes를 확인했다.

K20에서는 완전 cross support를 먼저 검사하고 직접 half-shift 구성으로 한 점만 완성했다. 이전 cap의 solver는 반복하지 않았다. 최초 recovery는 syntax error로0.069671CPU-s를 사용했고, 수정된 recover_v2는1.414403CPU-s로 성공했다. 두 실패의 source snapshot,stderr,command,receipt는 남겼다.

정적 감사에서 발견한 mincut-dual 검증 누락과 nb=None 경로를 수정하고 좁은 검사로 닫았다. 최적값의 증명과 추가 certificate metadata의 검사 범위를 구별했다.

## 비용·단계·다음 연구

최종 own-unit charge는28.653943/40CPU-s다. 실패·worker·coordinator·plot·tail을 포함한다. 잔여11.346057은 NONTRANSFERABLE이며 science_closed=true,additional science allowance0,automatic next node=false다. Metadata/provider/publication CPU는null이다. 예방적 총량 hard-cap 증명은false로 유지한다.

중앙 같은 HEAD66ef9a0147a0573b77e74e151dc280ba2bd4b64c의 qualified 기록은28/88,88nodes/17edges다. 이번 scoped child1/1의 중앙 count effect는0이며 중앙 owner repository에는 쓰지 않는다.

R1–R10/C1–C10의 단계별 근거를20개 stage에 대응시켰다. 이번 재개에서는 실행과 독립 검증을 먼저 마친 뒤 stage-labelled checkpoint를 게시한다. 이를 실행 전마다 순차 게시한 기록으로 서술하지 않는다. 실제 성공한 commit/backup/R3 상태는 publication 영수증이 권위다.

다음 연구는 실제 exclusive He event 입력 또는 source에서 정당화되는 pair 제약을 같은 state/history에 결속하는 일이다. 전체 source chemistry와 cross correction을 함께 제한하려면 (d,C) joint feasible region을 별도 scope·예산에서 다룬다. Actual K,exclusive kernel,C/D,outside partner,donor work,EOS/T,absolute volume,full physical native25는null로 유지한다.

## 검증된 배포와 재개 위치

초안 PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/115

과학 S=9ec654379074b731ce20f0b7dbae05077ddf4d4b. 실제 문서 D와 최종 closeout 상태는 publication/FINAL_DELIVERY.json 및 C10_RECEIPT.json으로 결속한다.

SOURCE는 BASS_CR_HE_ENERGY_CROSS_SOURCE_20261028_9ec654379074.zip,1553470bytes,SHA256 e606aea543f2dbf66832a549f4010ecb5cb51f642b45d6293ce1fd1b077f2a11이다. Dropbox와 Drive의 실제 원본 전체 GET에서 전체 SHA256,179개 payload SHA256 및 ZIP CRC가 모두 일치했다. SOURCE를 나중 영수증으로 다시 만들지 않는다.

PR114의 후속 head3d9818b4b91d00beef946aa88540d73c33e51dac까지 바뀐43개 파일은 모두 cr_he_energy_sum 경로이며 이번 경로와 겹치지 않는다. 중앙 HEAD도 같은66ef9a0147a0573b77e74e151dc280ba2bd4b64c임을 다시 확인했다.
