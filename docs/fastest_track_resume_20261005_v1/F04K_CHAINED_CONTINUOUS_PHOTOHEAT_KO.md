# F04K: 두 accepted half의 연속 누적 광이온화 가열오차 연결

## 판정과 scope

Task=BASS-CR-CHAT-F04K_CHAINED_CONTINUOUS_PHOTOHEAT.
Status=SCOPED_FIRST_MACRO_CONTINUOUS_HEAT_BOUND__INHERITED_TWO_SLAB_PREMISES.

Actual F08 T0_FLRW 첫 macro [0,1.25e9] proper seconds의 연속 semidiscrete HI photoheat를 조건부로 감쌌다. F04J의 첫-half 가열 결과와 owner의 새 half2 tube/M/R를 그대로 계승했다. 새 기여는 half2 재구성 적분, 이전 상태오차가 후속 가열에 주는 기여, 이전 누적 goal error 및 새 residual 기여의 분리·합성이다. Owner의 state/tube/J/residual 인증을 독립 재발급하지 않았고 native/IVP/history/old suite를 재실행하지 않았다.

시작과 게시 직전 bass_cr HEAD=53b18f887cf85759d28669385e69a2b19a617689, branch=research/r4q-gap-closure-20261001. 같은 branch에 이 additive summary를 게시한다. 실제 code/tests/정확 JSON/전체 유도/로그의 정본은 아래 immutable ZIP이다. Receiver production source/runtime_returns/CODEX_SYNC와 원자 실행 권한은 변경하지 않았다.

## 실제 입력과 provenance

Receiver=cosmosapjw-quantum/rei_bianchi@a2bc41f848854e99e8eae9a3c5bfed06f14ccd43, branch=forward/rust-reion-kernels-20260922. 이전76be0902679f1e8b6446edf4d50294a27a9cc3df 이후 delta는 REI-CHAT-FLRW08-MACRO-20261005의 문서8개 추가다. 새 MACRO_CHAIN_CONTRACT.json blob=3cb734e95f37d64e9c4fa4f0ac34348bc80b7b50, README blob=6952632aa04f1b2e50b4a2115d8c6194e8a340a7. 게시 직전 receiver ref도 동일했다.

Drive object10RWZfDdi-by6cqUYDw5JI2CPDZHVm1mB에서 REI_CHAT_FLRW08_MACRO_20261005.zip을 실제 회수했다. bytes232307, SHA2566b85f159badd02a0eae8d69511c37f6a6199907e3327177712609cd76ba93a60,96entries/95payload size/SHA/CRC 검증. F04J ZIP은 bytes333748,SHA2562fdb3e29ce7085e92302a1ee906c98c38d91564d85877a3537bdb74382337585,64entries/63payload 검증. 필요한 파일만 inputs/f04j와 inputs/macro에 계승했으며 old suites를 실행하지 않았다.

양쪽 package의 첫-slab 입력/state certificate/slab_model.py가 byte-identical이다. Macro의 parent_certificate_sha256,parent_input_sha256,half2_input_sha256도 일치한다. Half1 endpoint gas=half2 start gas, H/fHe, node identity, 13변수 state scale, 시간 경계를 검사했다. Half2 시작 photons는 저장 half1 endpoint를 같은 active node에 매핑한 값이며 source를 또 주입하지 않는다.

실제 half2 state initial error는 owner의 first state certificate vector를 그대로 사용한다. F04J의 별도 comparison endpoint나 더 좁은 discrete root box로 대신하지 않는다. Owner uncertain-initial Picard의 radius=.02, inherited max≈1.01008491969085e-4, self-map lhs≈.00895353040053207, contraction≈.442863912442121 전제를 계승했다. 이 검사를 다시 계산해 새 인증으로 집계하지 않았다.

## 새 유도: 누적 goal와 상태오차의 구분

각 half h=625000000s, 두 번째 half t=t_a+h*s,t_a=h,0<=s<=1. 동일 z=(xHII,xHeII,xHeIII,w/w0,p16/P0,...,p24/P0),P0=.05/H이며 w0는 최초 scale이다. H=1e-14/s,nH0=1e-4cm^-3,c=29979245800cm/s와 같은 source realization을 유지한다. 가스는 H/He이며 selected photoheat만 HI다.

    q2(s,z)=h*c*nH0*exp[-gamma-alpha*s]*(1-xHII)
            *sum_j(Ej-chiHI)*sigmaj*pj,
    gamma=3H*t_a, alpha=3H*h.

Density absolute-time offset exp(-gamma)를 누락하지 않는다. Sigma는 F04J의 analytic-real Verner intervals이고 native rounded sigma와 구분한다. Physical chiHI와 fit cutoff13.6eV를 합치지 않는다. Counts는 per H, heat는eV/H이며 추가dt/nH/a^3/a^4를 곱하지 않는다. kB/hbar를1로 설정한 것이 아니다.

저장 native endpoints를 잇는 affine reconstruction에서는 q2=exp(-gamma)*exp(-alpha*s)*(c0+c1*s+c2*s²)다. F04J exact moment/exp helpers를 수정 없이 사용해 Qrec,2를 적분했다. Owner의 interval 중심과 radius로 구성한 같은 cube에서 새 ell2_j>=sup|dq2/dz_j|를 구했다. 이는 cube 좌표를 읽는 작업이지 donor RHS/J/tube/residual 재계산이 아니다.

같은 볼록 tube 위에서 |e2(0)|<=b1, residual |r2|<=R2와 signed-diagonal Metzler M2를 계승하면

    |e2(s)|<=exp(sM2)b1+integral_0^s exp((s-u)M2)R2du.

따라서

    a2,past=integral_0^1 ell2^T exp(sM2)b1 ds,
    a2,new=integral_0^1 ell2^T integral_0^s exp((s-u)M2)R2du ds,
    |Qmacro-Qrec,macro|<=a1+a2,past+a2,new.

a1은 첫-half 누적 goal radius다. Additive observable은 물리 상태에 되먹임되지 않으므로 a1은 단순히 더한다. 반면 b1은 M2를 통해 반드시 전파한다. 이전 goal error만 남겨도 b1를reset하면 잘못된 chain이다. 두 구간 오차의 상관/상쇄를 가정하지 않았다.

Augmented matrix [[M2,0,R2],[ell2^T,0,0],[0,0,0]]의 exp action을 exact rational positive Taylor32차와 명시적 tail로 감쌌다. F04J goal_bound.py는 원 bytes 그대로다. 전체/initial-only/residual-only 세 action을 별도 기록했고 독립 interval sum과의 overlap을 검사했다. 초기상태오차가0인 다른 IVP의 local-only 상계를 원 macro certificate로 부르지 않는다.

## 실제 결과

소수는 표시값이다. 정확 분자·분모는 results/final/GOAL_CHAIN_CERTIFICATE.json의 signed hexadecimal 문자열이다.

|양[eV/H]|표시값|
|---|---:|
|QBE,macro: 저장 사건 projection|1.1796163027788511e-5|
|Qrec,half2|5.898080287967954e-6|
|Qrec,macro|1.1811342545462812e-5|
|이전 goal radius a1|6.386388608457494e-10|
|이전 state error의 half2 goal 기여 a2,past|1.2756114004650146e-9|
|새 half2 residual 기여 a2,new|6.308848991478850e-10|
|macro 전체 goal radius|2.545135160458649e-9|
|연속 macro Q 범위|[1.1808797410302354e-5,1.1813887680623270e-5]|
|Q-QBE 범위|[1.2634382513842686e-8,1.7724652834759982e-8]|

바깥쪽으로 느슨하게 쓰면1.1808797e-5<Q<1.1813888e-5 eV/H,1.2634e-8<Q-QBE<1.7725e-8 eV/H다. QBE 대비 상대차는0.10710%보다 크고0.15026%보다 작다. 따라서 해당 두-slab 전제하에서 연속 가열량이 저장 BE 사건 projection보다 크다는 부호가 분리된다.

State error를reset한 부정 대조의 macro radius는1.2695237599936344e-9, 올바른 값보다 약2.004795배 작다. 이는 누락된 bound-budget 항을 보여 주며 실제 unknown error가 반드시 두 배라는 뜻은 아니다. 실제 true error가 우연히 local-only 범위 안에 있을 가능성은 배제하지 않는다. 별도 정확 합성계 b'=0,b(0)=2,ell=1,이전 goal error3에서는 올바른 누적 radius5와 잘못 reset한3을 비교해 구조적 결함을 직접 검출했다.

Q-QBE에는 transport/source 주입/밀도 시간처리/반응 coupling/analytic sigma와 저장 산술의 의미가 함께 들어간다. Pure chemical truncation, 실제 원자모형 정확성, continuum 스펙트럼 또는 BI신호로 해석하지 않는다. Native raw heat accumulator와 owner production import는 아직 미관측이다.

## 새 검증 및 실패 보존

최종 focused tests34 PASS, exact artifact conditions12 PASS, Python7파일 syntax PASS(빈 package markers2개 포함). 1 assertion RED→GREEN,33tests-after다. First-half 기존27시험과 owner macro suite는 재실행·합산하지 않았다.

독립 수치 경로는 mpmath1.3.0,160자리 작업정밀도로 새 half2 quadrature1건, matrix exponential1건의 세 action42성분, 8corner의 gradient104성분을 검사해 모두 상계 내 포함을 확인했다. 이는 finite implementation 대조이며 formal certificate의 근거를 수치해로 대체하지 않는다. 160자리 물리적 정확성을 주장하지 않는다. Independent human/agent reviewer 및 proof-assistant는 없다.

개발 중 inherited IV에 Fraction radius를 직접 넘겨 TypeError가 발생했다. IV의 지원 타입을 확인하고 원 owner의 exact Decimal 문자열을 전달하도록 새 caller만 수정했다. 실패 로그와 수정 전 caller를 보존했고 helper/source/입력/허용오차는 바꾸지 않았다. 수학적 bound 실패나 native runtime 실패가 아니다.

최종 3명령 argv/exit는 logs/FINAL_COMMANDS.json, source/test hashes는 VERIFICATION.json이다. 모두exit0이며 포장 시 같은 hashes를 확인했다. Final exact proof는 독립대조가 사용한 development proof와 byte-identical이므로 같은 수치대조를 반복하지 않았다. 정본은 results/final이다.

이번 native/IVP/root/history/geometry/oldchecker/tube/J/residual 재계산/원자적분/receiver수정은0이다. 새 exact matrix propagation 세 건과 quadrature를 실제 수행했고 development와 final 실행을 구분했다. Rust script/toolchain은 실행하지 않았다.

## 정본과 실제 이중백업

File=BASS_CR_CHAT_F04K_20261005_v1.zip.
bytes=1177269.
SHA256=bf70472e4a244849d6039586ddec622c66e46adaafa0649fd9ac25c1ca25be51.
ZIP69entries/68payload size,SHA256,CRC local검증.

Drive: upload success 및metadata readback,id1iy28_dujLz46fBHOh39cG08nVO5iwhXF,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size1177269일치.
Dropbox: completed,id:BSpOijBcT10AAAAAADzITA,size1177269,modified2026-10-05T09:58:17Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04K_20261005_v1.zip.

같은 immutable local ZIP을 두provider에create-only 저장했다. R1 UPLOAD_VERIFIED이며 remotechecksum은 응답에 노출되지 않았다. 새ZIP fullrestore/independent remotebytehash는 미수행이다. Incoming donor 복원검증과 outgoing R1을 구분한다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Git의 이 문서는 summary/provenance/backup pointer이고 full code/test/result는ZIP이다. 실제 publication commit/tree는 ZIP밖 detached DELIVERY_RECEIPT에 기록한다.

## 종료와 다음 조건

첫 macro의 이 단일 observable은 위 조건에서 종료했다. 실제 후속 slab 또는 BI counterpart의 동일한 관측량/시간/angle/state mapping이 반환될 때 차이만 연결한다. 다음에는 state-error vector와 accumulated goal radius를 모두 전달하며, scale/시간이 바뀌면 boundary map/jump도 명시한다. FLRW 각도합 닫힘을 BI에 자동 이식하거나 같은 macro를 동기화만을 위해 반복하지 않는다.

CR_OFF_FASTEST,precisionatomicPARKED,G02UNRESOLVED,physicalproductionHOLD,capture=false,all_boundOPEN,b_gridNO_GO,actualCRcounter=null 유지. 기존 원자실행승인/fullK/318patch/CR-on은 재사용하지 않았다. Owner import ACK와raw native heat는null이고 새mandatorygate가 아니다.

산술 근거는 Python 공식 fractions/decimal 문서이며, 비교원리와 누적 goal 연결식은 정본 REPORT_KO.md에서 직접 유도했다.
