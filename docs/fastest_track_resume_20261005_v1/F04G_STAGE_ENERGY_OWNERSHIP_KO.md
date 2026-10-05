# F04G: 실제 accepted-stage 에너지 배분과 보존식의 식별성 한계

## 판정과 범위

Task: BASS-CR-CHAT-F04G_ACCEPTED_STAGE_ENERGY_OWNERSHIP.
Status: SCOPED_SOURCE_STAGE_ENERGY_BRIDGE_COMPLETE__STATIC_ENVELOPE_NOT_TRANSFERABLE.

F04F2의 정적 첫 record를 반복 계산하지 않고, 새 FLRW07의 저장된 공통격자 F4_COMMON/B4_COMMON 출력을 read-only 소비했다. 각12개, 총24개 source stage와216개 packet-stage 관측을 PI 흡수·결합·가열 및 gas/radiation work 계약에 연결했다. 새 native 실행·root/ODE solve·geometry 진화·owner checker·history replay는0이다. Production native 소비기가 이번 Python adapter를 실제 호출한 것은 아니며 owner load/ACK는 미관측이다.

시작 및 게시 직전 bass_cr HEAD=8dc57b8f0c9bb6cb85193f1c324555936c7c7979, tree=aa21738d237a7ef504c4f7c9706583d6cb8d0c37. 같은 research/r4q-gap-closure-20261001 branch의 새 문서만 추가했다. F04/F05/F04E/F04F2의 제한된 완료, concurrent7000record coverage를 계승했으며 같은 검사를 재실행하지 않았다. Receiver source/runtime_returns/CODEX_SYNC는 변경하지 않았다.

## 실제 source·contract intake

Receiver=cosmosapjw-quantum/rei_bianchi@840d5bd0270c653f138183125a1235c8257696ae, tree=dd5ca97f723a2f7ca2a9639764ae23d89dc0605b, branch=forward/rust-reion-kernels-20260922. 이전8e8ea0c 이후 변경은 FLRW07 문서8개 추가이며 production Rust 변경은 없다.

읽은 계약은 docs/fastest_track_chat/REI-CHAT-FLRW07-20261005/SPLIT_COMPOSITION_CONTRACT.json(blob37be9146cddefcd93204a6c4580a7ab8fdfe668d), README_KO.md(blob9a03e526a0b07360f6570e81552bd89c21522863)다. coupled_primary.rs::endpoint 원문과 로컬 full bytes는 blob09bb770a30c6605348e78106faa4b278fd5c3c13, SHA25685434c2c6257ce197c4c928d01c2095f83fc3cbac1c421e367c95fdafae46585로 일치한다.

Drive id1-tzETqoiEHZwIhWyhFp18doyYdQbjfZ0의 REI_CHAT_FLRW07_20261005.zip을 실제 회수했다. bytes1408512, SHA25624a4927211ddb6a5130e2f9e2ef5b50c21f15a082739fec6ad1484b3d34862b9. 72members/71payload의 size/SHA/CRC·경로를 검증하고 필요한 source/caller/기록만 inputs/flrw07에 계승했다. 원 archive 전체나 binary는 새 결과ZIP에 넣지 않았다.

Source stdout SHA256=4ee7e9085884c9fd0b4182b44039f1d9a0ca133ef7a64f545853e0b2f384ab57. Caller native/split_probe.rs SHA256=c79de945f0f5983086a34902abe6786122493b7976e860c539ab73f66792948a. 원 stdout의6run 중 이번 새 projection은 공통격자2run만 사용한다. 원50root/24continuous solve 등의 campaign은 보고로 수신했을 뿐 반복·합산하지 않았다.

첨부 F04F2 ZIP의63payload도 identity만 확인하여 scope·summary를 계승했다. 기존 interval 결과를 다시 계산하지 않았다. 입력 복원의 content 검증과 outgoing ZIP의 cloud upload 확인은 별개다.

## 시간·단위·사건 identity

실제 scheme은 G(t0,mid) -> BE source(nH(mid),E(mid)) -> G(mid,t1)이다. Proper time은 초, density는proper cm^-3, photon/reaction count는 보존되는 H핵당 수, thermal/escape/work는eV/H다. Source PI 배열은 photo_per_h[packet][absorber]이며 F04D의 absorber-major와 무표기 혼용하지 않는다.

원 caller는8개 초기packet에 pulse2개를 append하고 subthresholdpacket을 유지한다. run_id:append-slot:k는 이 source의 append-only 규칙으로 유도한 식별자이며 provider UUID가 아니다. provider_packet_ids=null을 유지한다. Birth0/2e10s와 injected flag를 연결했으며 source old_p에 이미 포함된 pulse를 장부에 다시 추가하지 않는다.

Hmean과 dt는 원 caller의 binary64 연산 결과를 복원한 값과 정확 실수 시간차를 구별한다. Gas work는2*Hmean*dt*w_endpoint를 source에서한번, radiation work는 두 geometry의 에너지 차이를 각각 적용한다. c,kB,epsilon_eV는 source에 유지하며 count를nH로 다시 나누거나 per-H변수에-3Hp를 추가하지 않는다.

## 새 에너지 projection과 정확 항등식

각packet의 geometry 전/중간/후 에너지를 Eminus,Emid,Eplus, count를 pminus,pplus, integrated PI count를 C_ka라 쓴다. 같은 stage에서

    A = sum_ka Emid_k*C_ka
    B_PI = sum_ka chi_a*C_ka
    Q_PI = A-B_PI
    Wrad_formula = sum_k [(Eminus_k-Emid_k)*pminus_k
                         +(Emid_k-Eplus_k)*pplus_k].

두 번째 geometry에는 흡수후 살아남은 pplus가 들어간다. rp_k=pplus_k-pminus_k+sum_a C_ka이면

    DeltaUgamma + Wrad_formula + A = sum_k Emid_k*rp_k.

저장 binary64의 정확 Fraction상으로 위 항등식을 확인했다. 실제 rp나 원 recorded Wrad와 formula의 차이를0으로 없애지 않았다. A/Q_PI는 저장된 rounded integrated count의 exact projection이지 원 source의 dt*photo_heat(rate) 중간값을 intercept한 것이 아니다. Source raw absorption/heat accumulator는 기록되지 않아null이다.

Ig=w+chiH*xH+fHe*[chiHeI*xHeII+(chiHeI+chiHeII)*xHeIII]라고 놓으면

    Rg = DeltaIg + escape_increment + Wgas - A
    Rr = DeltaUgamma + Wrad_recorded + A.

Escape는 source의 incremental eV/H이며 관측시점의 redshift된 escaped radiation energy로 재해석하지 않는다. 임의a^3/a^4 가중치를 붙이지 않았다.

## 새 결과: 두 부분 장부도 구별하지 못하는 배분 방향

상태·사건이 고정된 경우(A,Wgas,Wrad)가(Rg,Rr)에 들어가는 행렬은

    M = [[-1,1,0],[1,0,1]], rank(M)=2,
    M*(1,1,-1)^T=0.

그러므로

    A' = A+delta
    Wgas' = Wgas+delta
    Wrad' = Wrad-delta

는 gas/radiation residual을 각각 그대로 유지한다. 총장부만이 아니라 두 부분 장부를 함께 검사해도 이1차원 방향은 식별되지 않는다. 이 nullspace는 직접 유도·symbolic 및 정확 유리수 검산한 결과이며 production bug 발견이 아니다. Source-mid PI energy, actual gas work, actual geometry work의 독립 정의가 있어야 배분을 고정할 수 있다.

부정 대조는 각 source Emid 대신 해당segment의 Eplus를 가중치로 사용한다. D=sum(Emid-Eplus)*C이면 Q_PI,end=Q_PI,mid-D다. delta=-D와 보상 work를 함께 적용하면 두 장부가 정확히변하지 않는다. 원 기록·원 source를 실제변경하거나 다른 물리해를 계산하지 않았다.

|새 저장값 projection [eV/H]|F4_COMMON|B4_COMMON|
|---|---:|---:|
|정의된 source-mid PI heat|0.008593242267362638|0.008618522296552855|
|segment-end 에너지 대체시 누락량D|0.00010047293444323675|0.00007297533349631375|
|PI heat 대비누락|1.1692086795%|0.8467267472%|

B-F의 이산 PI heat contrast는2.528002919021638e-5 eV/H다. 같은 사건을 segment-end energy로 가중하면5.277763013713937e-5 eV/H로 약2.0877203배가 된다. +108.77203%의추가contrast편향이며 새물리신호나시간수렴결과가아니다. Supplier의시간정확성/physical HOLD를유지한다. 소수는표시용이고정본분자·분모는results/final에있다.

24stage의exact분해항등식과보상shift잔차변화는0이다. 실제record의combined energy residual최대는F/B각각5.861780551411815e-15/6.9965146620934315e-15 eV/H다. Gas work assembly차이최대3.614934116557509e-17, radiation work assembly차이최대2.3814042246082285e-17 eV/H를별도보존했다. 이는finite저장값산술차이이며uniformbound가아니다.

## 기존 enclosure의 직접 이식은 불가

관측된24stage 모두에서밀도·current photon energies/packet topology·gas work·source map및parent/root membership이F04F2의정적정의와달라NOT_APPLICABLE을반환했다. 이것은기존staticcertificate의FAIL이나취소가아니다. 필요한정적조건만맞아도IDENTITY_BINDING_STILL_REQUIRED를반환하며자동PASS를발급하지않는다. 정확한regrouping/새ownerbox를통한후속증명의가능성은배제하지않는다.

Parent-dependent가중치E(q)와사건C(q)의곱에는

    H_(E*C)=E*H_C+C*H_E+gradE outer gradC+gradC outer gradE

가필요하다. 동일parent frame을요구하는exact product_jet helper와교차항시험을구현했다. 실제팽창root/geometryderivatives나새intervalremainder를계산한것은아니다. 정적eventHessian만가져와동적에너지미분을0으로둘수없다.

## 실제 실행과 검증

새focused tests27 PASS, symbolic5조건True, Python5파일syntax PASS. 1시험은assertion RED->GREEN,26시험은tests-after다. DuplicateJSONkey/NaN/음수event/PI축전치/birth/시간및state연결/escape누락/null/단위중복변환/survivorwork/parent혼합/create-only/보상work반례를검사했다.

최종argv/exit는logs/FINAL_COMMANDS.json,테스트와symbolic출력은logs/05_FINAL_TESTS.*,06_THEORY.*,07_FINAL_BRIDGE.*다. 모든exit0이고VERIFICATION.json은testedsource5개의SHA를고정한다. 개발projection bridge01후finalprojection을한번더수행했으며두물리campaign으로세지않는다. 최종canonical결과는results/final/SUMMARY.json,STAGES.json이다.

Native/root/ODE/history/geometry/oldchecker/oldscience/원자적분/ownerbox확장/receiver수정은모두0이다. Pythonstandardlibrary기본경로와선택SymPy검산만실행했다. 독립human/agentreview및proof-assistant검증은없다.

## 정본과 실제 이중백업

파일=BASS_CR_CHAT_F04G_20261005_v1.zip
bytes=175094
SHA256=3317393be95a0e476bb7d587594bc62c8e8997871abf7d7279fa5c5c96814e2a
ZIP50members/49payload의size,SHA256,CRC를local에서확인했다.

Drive upload success와metadata readback:id1k1x-q8q4Q6vh4ULcbWv3OiTjrv4jbZpn,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size175094일치.
Dropbox completed:id:BSpOijBcT10AAAAAADzBrA,size175094,modified2026-10-05T00:34:25Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04G_20261005_v1.zip.

동일immutableZIP을두provider에create-only로저장했다. R1 UPLOAD_VERIFIED이며remotechecksum은응답에노출되지않았다. 새ZIP의fullrestore/독립remotebytehash는미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Incoming FLRW07archive의실제복원/hash검증과outgoingZIP의R1을혼동하지않는다.

이Git문서는summary/provenance/backup pointer다. 실제code/tests/전체한국어보고서/exactJSON/로그의정본은ZIP이다. ZIP안에미래upload성공을쓰지않았으며실제publicationcommit/tree는별도detached DELIVERY_RECEIPT.json에기록한다.

## 종료와 다음 조건

이보조lane은SCOPED_COMPLETE_WAIT_NEW_CONSUMER_INPUT으로종료한다. 실제새coupled root/parent domain또는explicitconsumerimport가생길때그차이만연결한다. 같은24stage및기존firstrecord를반복감사하지않으며6999stage누락을메우기위한history재실행을요청하지않는다. UUID/rawenergyaccumulator는owner의새기록이있을때만null을갱신한다. 다음time-error/F08과학코드변경은owner영역으로남긴다. 현재productionload/ACK는미관측이다.

CR_OFF_FASTEST,precisionatomicPARKED,G02UNRESOLVED,physicalproductionHOLD,capturefalse,all_boundOPEN,b_gridNO_GO,actualCRdispatchnull을유지한다. 새mandatorygate·원자실행승인재사용·fullK·318patch·CR-on은없다.
