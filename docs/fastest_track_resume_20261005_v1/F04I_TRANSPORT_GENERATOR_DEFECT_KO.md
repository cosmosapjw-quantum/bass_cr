# F04I: 고정 에너지 remap의 경계 표현·생성자·재구성 잔차

## 판정과 범위

Task=BASS-CR-CHAT-F04I_TRANSPORT_GENERATOR_AND_DEFECT.
Status=SCOPED_EXACT_REAL_TRANSPORT_INTERFACE__COUPLED_TIME_CERTIFICATE_OPEN.

새 FLRW08 계약의 fixed spectral/angular generator와 continuous reconstruction defect 의무 중 순수 광자 transport 성분을 정식화하고 exact-rational reference로 구현했다. 이는 owner의 실제 import 요청이나 ACK를 받았다는 뜻이 아니라, 새 공개 계약에 맞춰 선택한 제한된 보조 연구다. 화학 반응·source injection·팽창 가스·전체 coupled time-error certificate는 완료하지 않았다. F04H 가열량, 기존 F08 history/FLRW08 campaign 및 old checker를 반복하지 않았다.

시작·게시 직전 bass_cr HEAD=fd306c6402d0e4b3dfe074222136e51f50e52975, tree=6d6b099c6de409f349583addaefccfa451940e0d. 같은 research/r4q-gap-closure-20261001 branch의 새 문서다. Receiver=cosmosapjw-quantum/rei_bianchi@8629a63059597d4fdd01be0f4e3c8b120a7766d0, branch=forward/rust-reion-kernels-20260922. e63ca073 이후 변경은 FLRW08 문서8개이며 production source delta는 없다. FLRW08의 유한 정밀화 목표 통과와 auxiliary escape 상대진단 FAIL, 열린 continuum certificate를 함께 수신했고 재실행하지 않았다.

## 입력과 provenance

읽은 새 계약: docs/fastest_track_chat/REI-CHAT-FLRW08-20261005/PAIRED_TIME_CONTROL_CONTRACT.json, bloba45c006761c34404b6015e52fd01f6fcc4fdd047; README_KO.md blob4aedead457146e0e1210bd24a1923c8229db8615.

실제 source rust/rei_microphysics/src/paired_runtime.rs의 Dropbox bytes를 회수해 Git blob70eed18b07b6dd4297d8ef8da6d7e1be8e44456e와 일치시켰다. 23810bytes, SHA256b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7. energy_nodes/hat/endpoint의 redshift와 guard·deposition 구간을 읽었다. 현재 conservative helper 포함 source 전체를 과거 T0 실행 bytes와 같다고 표현하지 않는다.

T0_FLRW-header.jsonl의 energy_nodes33개는 connector에서 선택 전사했다. Header blob5afeefd1dc730e5058fd3759558b67608bd6a5f2이며 full header raw restore는 아니다. 실제 F04H prefix의 모든 대응 node/energy/sigma_bits를 검사했다. F04H ZIP SHA256d0a6357578fa14b9810e1397dce83c7980bc9afdba4ff2d43d341cc0b44d987e와 선택 payload만 검증해 입력을 계승했다. Prefix SHA256354b8bd39bc6fc1a06caf4c7d60ec7af6e2f4ef5f99315b9955656ad5697ef7c. 이전 과학 결과나 시험의 재실행은 없다.

## 경계 원자의 실수 remap과 보조 좌표

Source의 fixed energy nodes를 E0=10eV<E1<...<Em, per-H counts를 pj라 쓴다. Redshift ratio0<r<=1에서 rEj를 인접 node에 선형 hat으로 분배하고 rEj<E0이면 count와 energy 전부를 guard(GN,GU)에 넣는다. 이미 guard에 있던 energy는rGU로 변한다.

경계 원자 p0>0에서 임의의 r<1은 p0를 전부 guard로 옮긴다. 따라서 r→1-일 때 raw storage는 원 상태로 수렴하지 않는다. 반면 r=1의 source map은 identity다. 즉 이 전체 저장공간의 실수 해석은 그대로 strongly continuous ODE flow가 아니다. 이는 허용된 합성 boundary atom 반례이며 실제 S0가 그 상태를 거쳤다는 관측·native bug·history FAIL 판정이 아니다. Hq=0인 정적 극한은identity다. Binary64에서 작은 redshift가r=1로 반올림되는 경로의 무한소 미분을 구한 것이 아니다.

증명용 보조 quotient를

    Pi(p,GN,GU)=(p1,...,pm,BN=GN+p0,BU=GU+E0*p0)

로 정의했다. N=sum pj+BN, U=sum Ej*pj+BU를 유지하며 순수 단조 redshift에서 Pi*R(r)=Rbar(r)*Pi다. 이 보조 공간은 BU=E0*BN인 boundary trace를 허용한다. Native guard validator는 그 등호를 배제하므로 Pi 출력을 실제 PairedState에 주입하면 안 된다. Runtime converter를 만든 것이 아니고 blue shift/guard 재흡수로 확장하지 않았다.

## 고정 격자의 생성자

모든j>=1에서 rEj>=E(j-1)인 같은 cell branch에서는

    Rbar(r)=I+(1-r)*K,   kj=Ej/(Ej-E(j-1)).

K의 active columnj는 diagonal-kj와 바로 아래 node의+kj를 가진다. j=1은 BN에+k1,BU에E0*k1을 넣는다. BU diagonal은-1이다. 서로 다른 count/energy 단위는 해당 고정 에너지 단위와 함께 취급한다.

처방된 Bianchi I의 고정 ray label qi에 대해

    gq(t)=sqrt(sum qi^2*exp(-2Hi*t)),
    Hq(t)=sum Hi*qi^2*exp(-2Hi*t)/sum qi^2*exp(-2Hi*t),
    r'= -Hq*r,   Lq(t)=Hq(t)*K.

t는proper seconds,Hi는s^-1다. Count sector는 양의 생성자를 가지며 nK=0,uK=-u이므로 N'=0,U'=-Hq*U, radiation work'=+Hq*U다. c,hbar,kB를1로 설정하지 않았다. 이 L은 고정 spectral grid의 시간간격0 극한이고 continuum frequency transport와 같다는 인증은 아니다.

Guard outflow가 없는 내부 column의 second moment에는

    M2'=-2Hq*M2 + Hq*sum Ej*(Ej-E(j-1))*pj

가 들어간다. 추가 양수 항은 characteristic의 단순 E'=-HqE에 없는 grid spreading이다. Guard second moment를 복원하거나 continuum/model error를 인증한 결과가 아니다.

## 정확한 합성 defect와 연속 재구성 residual

r1*r2까지 같은 cell 조건이 유지되면

    Rbar(r2)*Rbar(r1)-Rbar(r1*r2)
       =(1-r1)*(1-r2)*(K+K^2).

n(K+K^2)=u(K+K^2)=0이다. 그러므로 N/U 장부가 정확히 같아도 energy-node 분포는 다를 수 있다. Source functional도 일반적으로 같지 않다.

한 cell의 재구성 ytilde(t)=Rbar(r(t))*y0와 고정-grid generator에 대해

    d_tr=ytilde'-Lq*ytilde
        =-Hq(t)*(1-r(t))*(K+K^2)*y0.

xi=int Hq dt=-ln(r)로 쓰면

    int ||d_tr||count,1 dt
       =(xi-1+exp(-xi))*||(K+K^2)*y0||count,1.

Count norm은 BN을 포함하지만 단위가 다른 BU는 제외한다. 이것은 transport reconstruction residual 적분이지 propagated endpoint error나 paired contrast bound가 아니다. Node crossing은 해당 공식을 적용하지 않고 거절한다. Finite remap의 branch 경계 등호는 허용하지만 residual API는 미분 kink를 거절한다. 전체 coupled proof에는 실제 공통 state scaling, source/chemical defect, splitting, jump, verified tube와 stability/Jacobian 차 상계가 더 필요하다.

## 실제 source grid의 새 제한 진단

33개 저장 energy nodes, 첫 HALF1의 tau=6.25e8s 및 H=1e-14/s를 고정했다. Source-defined 초기13.7eV node24에0.05/H를 둔 순수 transport algebra 비교이며 native angular population 재관측이 아니다. 두 transport 사이에 반응/source injection을 수행하지 않았다.

r=exp(-H*tau)는 H*tau∈[0,1]의 exact rational 교대 Taylor 급수20차와21차로 감쌌다. Exp/Decimal 라이브러리 평가가 아니며 bracket 폭의 표시값은1.0118973361425182e-129이다. 두 tau까지 모든 column의 같은-cell 조건이 성립하며 최소 node 여유는2.567609974628172e-5eV다.

|항목|표시값|
|---|---:|
|두half-remap minus 한full-remap의 count L1 차이|9.375878900604668e-6/H|
|전체 photon number 차이|정확0|
|전체 photon energy 차이|정확0 eV/H|
|고정 가스 HI photoheat-rate 차이|-2.6590479355928296e-22 eV/H/s|
|첫tau의 count-sector residual 적분|4.687958983413897e-6/H|
|내부 원자의 M2 추가항|8.562499999999513e-17 eV^2/H/s|

Defect의 지지집합은 원 node22,23,24다. 가열률의 고정 가중치는 psi_j=c*nH*(1-xHII)*(Ej-chiH)*sigmaHI,j로, 실제 첫HALF1 old gas/density와 해당 세 node의 sigma bits를 사용했다. Gas에서He를 제거하지 않았으며 선택 node의He 광흡수만0이다. 이 값은 새 화학 step·누적 heat·관측 신호·시간수렴 인증이 아니다. 정확 endpoints는 results/final/EXACT_RESULT.json의 분자/분모이며 소수 양끝 표시값이 같아도 구간 폭0으로 읽지 않는다.

## 실제 검증

32focused tests PASS,6symbolic conditions True,6Python파일syntax PASS(빈package marker2개 포함). Boundary merger누락과 residual kink허용을 각각 assertion RED→GREEN으로 기록했다. 나머지30시험은tests-after다. 별도40합성 positive-state 검사는 quotient와N/U항등식을 검사한 것이며40물리history가 아니다.

최종argv/exit/source hashes는 VERIFICATION.json과 logs/FINAL_COMMANDS.json이다. 07_FINAL_TESTS,08_SYMBOLIC,09_FINAL_DIAGNOSTIC 모두exit0이다. Source 변경 없이 packaging에서 hashes를 다시 확인했다. 독립human/agentreview와proof-assistant검증은없다.

새native/root/ODE/geometry trajectory/history/oldchecker/oldscience/원자적분/receiver mutation은0이다. Direct source download DNS실패는 logs에 보존했고 Files회수로 해소했다. 첨부Rust script의prefix를 이번runtime에 복원하거나 실행하지 않았으며 이전실행성공을 현재설치완료로표현하지 않는다.

## 정본과 실제 이중백업

파일=BASS_CR_CHAT_F04I_20261005_v1.zip
bytes=96509
SHA256=ab1e422c49ce680f615a1dace64426d375ab01f2bf5a654bfd2c927906e114e5
ZIP49members/48payload의size,SHA256,CRC를local검증했다.

Drive upload success 및metadata readback:id1M2McW8-ep6jj3EZoxQ_4xGsMgh-ZySHs,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size96509일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzGpw,size96509,modified2026-10-05T09:01:05Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04I_20261005_v1.zip.

같은immutableZIP을두provider에create-only로저장했다. R1 UPLOAD_VERIFIED이며remotechecksum은응답에노출되지않았다. 새ZIP의fullrestore/독립remotebytehash는미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이Git문서는summary/provenance/backup pointer이고code/tests/전체유도/exactJSON/로그의정본은ZIP이다. 실제게시commit/tree는detached DELIVERY_RECEIPT에기록하며sealedZIP에는미래성공을쓰지않았다.

## 종료와 다음 연결

FLRW08의연속defect의무중순수transport성분은위범위에서완료했다. 다음실제소비에서Pi/K/residual을공통상태scale과chemical/source/splittingdefect에연결해야하며, 전체coupledtimecertificate는OPEN이다. Owner source수정,새mandatorygate,같은firstrecord/diagnostic반복은없다. 새로운node/transport/guard재흡수/blue-shift/실제import가있을때그차이만다룬다. Consumer import ACK는null이다.

CR_OFF_FASTEST,precisionatomicPARKED,G02UNRESOLVED,physicalproductionHOLD,capture=false,all_boundOPEN,b_gridNO_GO,actualCRcallbacknull을유지한다. CR-on/fullK/318patch/소비된원자승인은재사용하지않았다.
