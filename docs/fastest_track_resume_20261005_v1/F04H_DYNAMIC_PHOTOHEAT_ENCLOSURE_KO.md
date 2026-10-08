# F04H: 실제 F08 source box에서 HI 광이온화 가열량의 조건부 상계

## 판정

BASS-CR-CHAT-F04H_DYNAMIC_HI_PHOTOHEAT_ENCLOSURE.
SCOPED_DYNAMIC_HI_PHOTOHEAT_ENCLOSURE__INHERITED_MEMBERSHIP.

새로 반환된 actual F08 T0_FLRW의 첫 네 macrostep에서 한 observable인 PI 가열량을 계산했다. Full/half1/half2 총12개 source stage,64개 energy-node/stage 조합을 읽고 accepted8개 half만 누적했다. 기존 F04G의 FLRW07 F4_COMMON/B4_COMMON이나 F04F2 정적 record를 반복 계산한 것이 아니다. Actual input/root membership은 owner의 독립 인증을 전제로 계승하며, 여기서 root 존재·유일성을 재인증하지 않았다.

시작 및 게시 준비 시 bass_cr HEAD=38d9a4b4eae3075df633f29744ca33ebc1cf22bc, tree=59552ea51b6d55540ee52c26ffca947de502186b. 같은 research/r4q-gap-closure-20261001 branch의 새 문서만 추가한다. 새 native/root/ODE/history/geometry/owner checker/과거 science suite/원자 적분/영역 확장/receiver mutation은 모두0이다. 실제 코드·시험·정확 결과의 정본은 아래 ZIP이며 Git에는 이 요약·provenance·정본 위치를 게시한다.

## 새 owner 입력과 상태 계승

Receiver snapshot=cosmosapjw-quantum/rei_bianchi@e63ca0735a3e3e7eebbf4498c697d806d375e191, tree=47b2243a54d49df2df4f47170b54dc119f0d5f55, branch=forward/rust-reion-kernels-20260922. 이전840d5bd0270c653f138183125a1235c8257696ae 이후 새 F08 완료·후속 입력을 읽었다. 큰 commit 비교의 제한된 파일 목록을 전체 diff 검토로 주장하지 않는다.

Owner README는 처방된15개 paired history의 제한된 완료와 선택248000 accepted trials를 보고한다. 이는 외부 결과 수신이며 이 호스트의 새 실행 수가 아니다. T0_FLRW independent receipt(blob461cf73f3a87c5d6abfd5f883559161c7679509a)는 WHOLE_HISTORY_COMPONENT_INDEPENDENT_PASS를 기록하고8000trial 이후 checkpoint의 compensated/naive source-U 비교 실패와 별도 closeout을 함께 보존한다. Trial engine exit1을 소급0으로 바꾸거나 기존 checker를 재실행하지 않았다. 원래의 연속시간·continuum·physical HOLD도 유지한다.

F08_successors/ 아래 네 JSON을 Dropbox mirror에서 실제 회수하고 고정 GitHub blob과 대조했다.
- FLRW07_ACTUAL_F08_PREFIX.json: bytes91254, bloba9af816937792a8fdebcc637fc2fb512431835c6, SHA256354b8bd39bc6fc1a06caf4c7d60ec7af6e2f4ef5f99315b9955656ad5697ef7c.
- U_EDGE_WORK_CONTRACT.json: blob88efea559a1c3c998e730d745ba869beef55fe64.
- CR_F04E_ACCEPTED_F05_STAGE_INPUT.json: blobb1302232ca8ecfa89240c4548219588a3bd59e27.
- CR_OFF_DISPATCH_OBSERVATION.json: blob94fba57c366203924d2bba6a808360d57ae6c473.

Prefix의 실제 run source identity SHA256=f14cbf9ae79cb8acffd6dde7338ec652d1329865b9e0cdf7b70164253d93cdf5. 원 T0_FLRW8000trial raw journal SHA256=cd985bb09c6cce51f0c049421be027399f97c62a257d8a6bc3c9eee0a978d2a3. 전체 journal을 새로 회수하거나 replay하지 않았다.

원 실행 source 두 파일을 이전 검증 패키지에서 읽어 source_parts와 SHA를 맞췄다. coupled_primary.rs는85434c2c6257ce197c4c928d01c2095f83fc3cbac1c421e367c95fdafae46585, hhe_events.rs는c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290다. 현재 canonical helper 버전을 과거 실행 bytes 대신 사용하지 않았다.

## 물리·수치 범위

가스는 H와 He를 모두 포함한다. 선택64개 node/stage 조합의 HeI·HeII 광흡수 sigma는 모두 저장 비트상0이므로 HI-only photoabsorption specialization을 사용했다. Pure-H gas로 바꾸지 않았다. RR/CI/DR와 thermal feedback은 owner가 구한 HII root 범위를 통해 들어간다.

각 audit의 tau,nH,energy,sigma와 parent_photons,out_gas,out_photons를 그대로 사용했다. Photon parent는 transport와 해당 stage의 source 주입을 거친 per-H 값이다. Macrostep 이전 photons로 대체하거나 source를 두 번 더하지 않는다. Energy는 해당 F08 audit의 고정 physical-energy node이며, 이전 G-BE-G의 중간 에너지 규칙을 자동 이식하지 않는다.

c=29979245800 cm/s, chi_H는13.598_434_599_702 eV literal의 binary64 값, tau는s,nH는proper cm^-3,sigma는cm^2다. chi_H와 fit cutoff13.6eV를 구별한다. kB나hbar를1로 설정하지 않았으며 이 PI observable에 직접 나타나지 않을 뿐이다. Counts는 per H, heat는eV/H다. 모든 source realization은 고정하며 새 uncertainty나 box를 추가하지 않았다.

## 직접 유도와 exact rational enclosure

a_k=tau*c*nH*sigma_HI,k, x=xHII, P_k=incoming photons per H이면

    P'_k=P_k/[1+a_k*(1-x)]
    C_k=P_k*a_k*(1-x)/[1+a_k*(1-x)]
    Q_PI=sum_k (E_k-chi_H)*C_k.

0<=x<=1, P>=0, a>=0, active E>=chi_H에서 분모>=1이다. C_P=a(1-x)/(1+a(1-x))>=0, C_x=-P*a/(1+a(1-x))^2<=0, C_xx=-2P*a^2/(1+a(1-x))^3<=0.

x∈[xL,xU], P_k∈[PL_k,PU_k]의 독립 직사각형 relaxation에서는

    QL=sum (E-chi)*PL*a*(1-xU)/(1+a*(1-xU))
    QU=sum (E-chi)*PU*a*(1-xL)/(1+a*(1-xL))

가 정확한 hull이다. 실제 implicit root manifold의 코너 달성 가능성을 주장하지 않는다. 실제 의존관계가 이 사각영역 안에 있으므로 조건부 안전 범위다. 별도로 C=a(1-x)*P'의 양수 곱 범위와 incoming-minus-outgoing 범위를 계산해 세 유효 범위를 교차시켰다. 비음수 성질과의 교집합은 음수 물리해 clipping이 아니며 빈 교집합은 실패한다.

고정 z=a(1-x)>0에서 incoming 폭을 dP라 하면 직접 소거식의 사건 폭은 z*dP/(1+z)지만, incoming/outgoing을 독립 구간으로 빼면 (1+1/(1+z))*dP다. 폭의 비는1+2/z. 작은 흡수량의 의존관계를 보존하여 subtraction의 과대폭을 제거한 것이다. 실제12stage의 독립 photon-loss 차분 대비 최종 heat 폭은 약856.8–1716.5배 좁다. 물리 모델이나 시간 정확도가 그 배수만큼 개선된 것은 아니다.

범위 연산은 JSON binary64 숫자를 Fraction(float)로 정확 유리수화한 뒤 정수 사칙연산으로 수행했다. 표의 소수는 표시값이고 정본은 HEAT_ENCLOSURES.json의 분자/분모다. Exp/log/원자fit 재평가나 root 탐색은 없다.

## 실제 가열량 결과

각 macrostep은1.25e9s, half는6.25e8s다. HALF2 parent_gas=HALF1 out_gas를 검사했고 photon parent의 중간 transport/source 변화를 reset하지 않았다. Accepted 누적에는 두 half만 사용한다.

|macrostep|accepted heat 표시 범위[eV/H]|폭 표시값|
|---|---|---:|
|1|[1.17961630264567635e-5,1.17961630291279006e-5]|2.67114e-15|
|2|[1.17356963319388704e-5,1.17356963382970233e-5]|6.35815e-15|
|3|[1.16755758503069943e-5,1.16755758603176363e-5]|1.00106e-14|
|4|[1.16157991302653244e-5,1.16157991438972796e-5]|1.36320e-14|

[0,5e9]s의 accepted 누적량을 바깥쪽으로 느슨하게 표시하면

    4.6823234338e-5 < Q_PI_cumulative < 4.6823234372e-5 eV/H.

정본 끝점의 표시값은4.68232343389679510e-5와4.68232343716398414e-5다. 기존 native event counts의 정확 heat projection 합은 표시값4.68232343552901065e-5 eV/H이며12stage projection이 각각 범위 안에 포함됐다. 미기록 native raw heat accumulator의 bit identity나 전체 FP rounding 인증은 아니다.

Full-minus-twohalf는 네 macrostep 모두 음수로 범위가 분리된다. 첫 차이는 약[-1.5123452574,-1.5123448159]e-8 eV/H. Full/half의 transport/source 주입·밀도·중간 node projection도 달라지므로 pure chemical BE truncation error 또는 continuous flow error로 명명하지 않는다. 새로운 heat acceptance tolerance는 지정하지 않았다. 여덟 stage 범위의 합은 실제 상관을 상쇄에 쓰지 않는 보수적 합이다. 이 결과를 전체8000step,15history,continuum spectrum 또는 physical fitting error로 확대하지 않는다.

## CR 반환 ACK와 미관측 상태

새 CR_F04E 입력의 accepted_record는 기존 F04E inputs/F05_FIRST_TRANSACTION.json과 모든 JSON 필드가 같고 raw record SHA183497b5496c9b8269a45111c35935f4bda8a4dcfac2dbc48cff58739d182c41도 일치했다. 이를 수신 ACK로 기록했고 기존25bit 관측·F04F2 계산은 반복하지 않았다.

Owner external_CR25_output_map_executed=false는 owner production의 외부 adapter 호출 여부다. 이전 read-only 연구 결과를 취소하거나 이 값을 true로 바꾸지 않았다. CR_OFF 반환은 실제 선택 entrypoint를 명시하지만 loader/provider/callback seam과 동적 counter가 없어blocked다. OFF 선언을 관측된0이나negligibility로 바꾸지 않는다. Runtime counts=null, baseline_validity_blocked=false를 구분한다.

## 새 검증

Focused tests27 PASS, symbolic6조건True, Python syntax6파일 및 시험 당시 source hashes 일치. 6파일 중2개는 빈 package marker다. Exact 합성 사각영역40개에서320개 corner와40개 interior를 별도 incoming-minus-surviving 정의로 대조했다. 우주론 history나 물리 초기조건360개를 실행한 것이 아니다.

최초 exact-corner 시험1개는 assertion RED→GREEN,나머지26개는tests-after다. Competing He absorber, wrong sigma bits/axis, inactive PI, negative/NaN/duplicateJSON, accepted-only aggregation, half2parent reset, observed value diagnostic 분리,create-only를 검사했다. Final stdout/argv/exit는logs/FINAL_COMMANDS.json과04_FINAL_TESTS,05_THEORY,06_FINAL_HEAT에 보존했다. 모두exit0이며 이전 suite를 합산하지 않았다. 독립human/agent reviewer와proof-assistant 검증은 없다.

초기 direct network DNS 실패와 선택적 skill helper Resource-not-found는 환경 기록으로 보존했고 수학·native 실패로 분류하지 않았다. 실제 source/data는 connector와Files materialization으로 읽었다. 시험 뒤 scientific code hash가 변하지 않았음을 packaging에서 확인했다.

## 정본과 실제 이중백업

File=BASS_CR_CHAT_F04H_20261005_v1.zip
bytes=105225
SHA256=d0a6357578fa14b9810e1397dce83c7980bc9afdba4ff2d43d341cc0b44d987e
ZIP40members,39payload size/SHA256와CRC를local에서검증했다.

Drive success ACK 및metadata readback:id1MVy9JEzeKOb6ktL4QyvQDkIqNEC0H8Y_,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size105225일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzFog,size105225,modified2026-10-05T06:10:54Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04H_20261005_v1.zip.

동일 immutable archive를 두 provider에create-only로 저장했다. R1 UPLOAD_VERIFIED(ID/name/size/path또는parent),remotechecksum은응답에노출되지않았고새ZIP의fullrestore/독립remotebytehash는수행하지않았다. Incoming source/data bytes 검증과 outgoing R1을 구분한다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. ZIP 안에 미래 게시·업로드 성공을 쓰지 않았고 실제 commit/tree는 별도 detached DELIVERY_RECEIPT에 기록한다.

## 종료와 다음 조건

이 새 prefix의 단일 HI-photoheat observable은 위 조건에서 종료했다. 다음 actual consumer import 또는 새 source/parent 범위가 오면 그 차이만 연결한다. 같은12stage나기존firstrecord를반복감사하지않고나머지7996record를얻기위해history재실행을요청하지않는다. Competing He photoabsorption이나 variable node/source parameter는 별도 owner scope다. 새로운 mandatory gate가 아니다.

CR_OFF_FASTEST,precision atomic PARKED,G02UNRESOLVED,physicalproductionHOLD,capture=false,all_boundOPEN,b_gridNO_GO,CRcounter=null을유지한다. CR-on/fullK/318patch/소비된 원자 실행 승인은 재사용하지 않았다.

산술 계약의 원전은 Python 공식 fractions 문서 https://docs.python.org/3/library/fractions.html 이며 float를 같은 정확한 유리수 값으로 읽는 계약이다. 소거식·단조성·폭비는 보고서에서 직접 유도했다.
