# F04J: 첫 accepted half의 연속 누적 광이온화 가열량

## 판정과 범위

Task: BASS-CR-CHAT-F04J_CONTINUOUS_PHOTOHEAT_GOAL_BOUND.
Status: SCOPED_FIRST_HALF_CONTINUOUS_HEAT_BOUND__INHERITED_TUBE_AND_DEFECT.

Actual F08 T0_FLRW의 첫 committed half, proper time0..625000000s에서 누적 HI photoheat를 계산했다. 새 FLRW08-SLAB의13변수 연속 semidiscrete 목표, Picard tube, signed-diagonal Metzler majorant M과 재구성 잔차 R를 전제로 추가 observable을 감쌌다. Root/tube/잔차 인증을 독립 재발급하거나 이산 F04H 상계를 연속 오차로 바꾸지 않았다. Half2, 전체 macro/history, BI counterpart, paired contrast, spectral/angular continuum, 원자율 physical accuracy는 미완료다.

시작 및 게시 준비 시 bass_cr HEAD=1d8e965547f363ab49fcdc82b9aaa7b172fce698, branch=research/r4q-gap-closure-20261001. 같은 branch의 새 문서만 추가한다. Receiver=76be0902679f1e8b6446edf4d50294a27a9cc3df, tree=888ff8ead50f4364c30f1031f31706fbbd8bdcbd, branch=forward/rust-reion-kernels-20260922. 이 ref는 이전8629a630 뒤의 첫 slab 결과다. 시작과 게시 경계의 live ref가 같았다. Receiver production source/runtime_returns/CODEX_SYNC는 변경하지 않았다.

## 입력과 provenance

Drive id1e7GptuaOcTjmbASmGRfdQSJg6qUOztNo의 REI_CHAT_FLRW08_SLAB_20261005.zip을 실제 회수했다. bytes93647, SHA2560930677e58a01488538bea048a98f872f19c0628875d3fe88ed7c85778b93f86, 48manifest payload의 size/SHA256와 CRC를 확인했다. 필요한 계약·입력·기존 증거와 interval_decimal.py/slab_model.py를 원 bytes로 계승했다. Donor의 전체 native/IVP/잔차/Jacobian/tube 계산은 재실행하지 않았다.

입력은 donor inputs/ACCEPTED_SLAB.json의 actual_records[0].audits[1] 의미론적 발췌다. 원 prefix blob=a9af816937792a8fdebcc637fc2fb512431835c6. 발췌를 whole raw journal restore로 부르지 않는다. 새 SOURCE_BINDING.json이 소비한 모든 파일의 identity를 고정한다. F04I ZIP SHAab1e422c49ce680f615a1dace64426d375ab01f2bf5a654bfd2c927906e114e5의 계약·인계만 계승했고 transport 진단은 반복하지 않았다. F04I와 donor active generator의 수학적 연결을 owner runtime import ACK로 표현하지 않는다.

## 연속 목표와 세 가열량

s=t/h, h=625000000s, z=(xHII,xHeII,xHeIII,w/w0,p16/P0,...,p24/P0), P0=.05/H이다. 동일 donor 모형의 H=1e-14/s, nH0=1e-4cm^-3, continuous source5e-15photons/H/s at13.7eV, 온도의존 RR/CI/두 DR와 gas work를 유지한다. FLRW 각도합 닫힘은 BI에 자동 이식하지 않는다.

c=29979245800cm/s, kB, eV-to-erg를 유지한다. Node와 coefficient literal은 같은 binary64 값을 정확한 실수로 해석하고 source의 exp/log/power는 실수 함수다. Native rounded sigma와 donor real-analytic Verner sigma를 같다고 놓지 않았다. 새 계산은 후자의 구간을 사용한다. Physical binding chiHI와 fit cutoff13.6eV를 구분한다. 가스에는 H와 He가 모두 존재한다.

원 native endpoint를 잇는 zhat(s)=(1-s)z0+s*z1에 대해

    q(s,z)=h*c*nH0*exp(-alpha*s)*(1-xHII)
           *sum_j (Ej-chiHI)*sigmaj*pj,
    alpha=3*H*h,
    Q=integral_0^1 q(s,z(s)) ds

로 정의한다. pj는 photons/H, Q는eV/H다. 추가dt/nH나 a^3/a^4를 곱하지 않는다.

- Q_BE: 저장된 첫 HALF1의 rounded PI event count를(E-chi)로 정확 projection한 값.
- Q_rec: 같은 native-endpoint affine reconstruction에 q를 넣은 연속 적분.
- Q: 선언된 continuous semidiscrete solution의 누적 가열량.

Raw native heat accumulator는 미기록이므로 Q_BE의 bit identity 대상으로 삼지 않는다. Q-Q_BE는 source 주입·transport·밀도 시간처리·반응 coupling 및 저장 산술을 포함한다. Pure chemical BE truncation 또는 실제 원자물리 오차로 단순화하지 않는다.

## 직접 유도: 재구성 적분과 goal-error 전파

재구성에서 x와p가선형이므로 q(s,zhat)=exp(-alpha*s)*(c0+c1*s+c2*s^2)다. Moment

    Im(alpha)=integral_0^1 s^m exp(-alpha*s)ds
             =sum_k (-alpha)^k/[k!*(m+k+1)]

의24/25차 짝수·홀수 부분합을 정확 Fraction으로 계산한다.0<=alpha<=1에서 항 크기가 감소하므로 두 부분합은 올바른 상·하계다. Signed coefficient의 interval 곱을 보존한다.

Donor 볼록 tube에서 r=zhat'-F(s,zhat), |r|<=R이고 M_ii>=sup DF_ii, M_ij>=sup|DF_ij|(i!=j)라 하자. Dini 비교로

    |z-zhat|<=b, b'=M*b+R, b(0)=b0

를 얻는다. 첫 slab만 b0=0이다. 후속 initial error를 받는 API를 구현해 자동reset을 막았다. ell_i>=sup|dq/dz_i|이면

    |Q-Q_rec|<=integral_0^1 ell^T*b(s)ds.

전체13변수M을 사용하므로 q가 직접 의존하지 않는 온도/He 변수의 효과도 상태오차 전파에 남는다. 기존 cube radius.02에서 nH<=nH0, |pj/P0|<=|zj0|+.02와1-xHII<=1-x0+.02로 ell을 구성했다.

    A_aug=[[M,0,R],[ell^T,0,0],[0,0,0]]

에 대해 exp(A_aug)*(b0,0,1)을 구하면 누적 goal bound가 나온다. 단순히 endpoint state error에 시간간격을 곱한 결과가 아니다.

omega=max(0,-min diag A_aug), B=A_aug+omegaI>=0, qB=||B||inf로 shift하고32차 양의 행렬급수와

    tail<=||v||inf*qB^(n+1)/(n+1)!/[1-qB/(n+2)]

를 사용했다. qB/(n+2)<1을 실제 검사한다. omega≈.435345<=1이므로 exp(-omega)는 정확 교대급수로 감쌌다. Power vector가 정확0이면 모든 후속항도0이므로 tail0을 사용한다. 부동소수점 threshold로 잘라내는 과정은 없다.

이 새 전파 계산은 donor의 M/R/tube가 유효하다는 전제에 의존한다. Native floating program 전체나 donor의 proof implementation을 독립 검증한 것은 아니다. Donor SIG 구간은 변경하지 않은 Decimal60자리 primitive의 exp/ln 계약에 의존하며 새 moment/matrix propagation은 exact rational이다.

## 실제 결과

소수는 표시값이고 정본 끝점은 results/final/GOAL_CERTIFICATE.json의 signed hexadecimal 분자·분모다.

|양[eV/H]|표시값|
|---|---:|
|Q_BE, stored event projection|5.905661585118707e-6|
|Q_rec|5.913262257494858e-6|
|Q_rec-Q_BE|7.600672376150740e-9|
|상계 |Q-Q_rec||6.386388608457494e-10|
|Q|[5.9126236186340125e-6,5.913900896355704e-6]|
|Q-Q_BE|[6.962033515304989e-9,8.239311236996488e-9]|

바깥쪽으로 느슨하게 쓰면

    5.9126236e-6<Q<5.9139010e-6 eV/H,
    6.9620e-9<Q-Q_BE<8.2394e-9 eV/H.

Q_BE 대비 상대차는[0.11788%,0.13952%]안이다. 따라서 같은 첫 half의 선택된 연속모형 가열량이 stored BE 사건 projection보다 크다는 부호가 전제하에서 분리된다. 이산 root/observable box가 매우 좁다는 사실과 continuous-time error를 구분한다. 시간정확도 기준을 새로 만들거나 전체history/physical admission을 승인하지 않았다.

## 검증과 실패

새 focused tests27 PASS, Python7파일 syntax PASS(빈 package marker2개 포함), 최종 출력의6개 exact 조건을 확인했다. 초기moment 기능1개와 nilpotent-tail 회귀수정1개에 assertion RED→GREEN을 기록했고 나머지25시험은tests-after다. 전체를 test-first 구현이라고 부르지 않는다.

독립 경로는 moment16건(4exact-zero+12quadrature), exp4건, analytic sigma9개, actual reconstruction quadrature1개, augmented matrix action14성분, gradient corner40값을 확인했다. mpmath300자리는 작업정밀도이지 물리적 정확성 자릿수가 아니다. 이 수치대조가 bound를 대신하지 않는다. 새 IVP truth를 만들거나 저장되지 않은 continuous heat를 소급 관측한 것은 아니다.

실패1: nilpotent 합성계의 generic norm tail 약7e-22가 폭시험1e-25를 초과했다. 기존 enclosure는 안전했으나 과대폭이었다. 정확 power-vector 소멸시 tail=0인 분기를 추가했고 허용오차는 유지했다. 실제 비nilpotent source 결과는 변하지 않았다.
실패2: 폭 약2.4e-152의 exact moment interval을100자리 quadrature와 비교해 약3.6e-102 차이로 실패했다. 독립 검사정밀도만300으로 높였으며 proof interval/과학 허용오차는 바꾸지 않았다. 수정 전 코드와 실패·원인 JSON을 보존했다.

최종 argv/exit는 logs/FINAL_COMMANDS.json, 코드 SHA는 VERIFICATION.json, 결과는 results/final이다. Development01을 정본으로 사용하지 않는다. 독립 human/agent reviewer 및 proof assistant는 수행하지 않았다.

새 native/IVP/root/owner checker·tube·Jacobian·residual 재실행/old suite/원자적분/receiver mutation은 모두0이다. 새 유리수 matrix propagation과 quadrature는 실제 수행했다. 첨부 Rust 환경 스크립트는 참고만 했고 toolchain을 실행하지 않았다.

## 정본과 실제 이중백업

파일=BASS_CR_CHAT_F04J_20261005_v1.zip
bytes=333748
SHA256=2fdb3e29ce7085e92302a1ee906c98c38d91564d85877a3537bdb74382337585
ZIP64members,63payload size/SHA256와CRC를local에서확인했다.

Google Drive: upload success 및metadata readback 확인. id1vaTEmuAuiTMPSDX2aI946nmjZ2jXDyPu, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ, 이름/size333748일치.
Dropbox: 첫 업로드는 source FETCH_FAILED. 같은 immutable ZIP으로 재시도한 업로드는 completed, id:BSpOijBcT10AAAAAADzHmg, size333748, modified2026-10-05T09:29:36Z.
Dropbox path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04J_20261005_v1.zip.

R1 UPLOAD_VERIFIED이며 remote checksum은 응답에 노출되지 않았다. 새ZIP의 full restore/독립 remote bytehash는 수행하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Incoming donor archive의 실제 회수·해시 검증과 outgoing R1을 구분한다. 실제 코드·시험·전체 보고·정확 결과는 immutable ZIP에 있으며 이 문서는 summary/provenance/backup pointer다. 포장후 실제 commit/tree/ACK는 별도 detached DELIVERY_RECEIPT에 기록한다.

## 다음 연결과 유지 상태

실제 owner half2의 새 tube/M/R/reconstruction이 오면 첫-half state-error와 누적 goal-error를 함께 초기조건으로 전달한다. 새 discrete root box로 continuous error를0으로reset하지 않는다. BI에는 실제 counterpart와 새 state/angle mapping이 필요하다. 동일first-half/projection/oldhistory를 반복하지 않는다. Owner import ACK와raw native heat accumulator는null이다.

CR_OFF_FASTEST,precision atomic PARKED,G02UNRESOLVED,physicalproductionHOLD,capture=false,all_boundOPEN,b_gridNO_GO,actualCRcounter=null을 유지한다. 기존 원자실행승인/fullK/318patch/CR-on을 재사용하지 않았다. 새 mandatory gate가 아니다.

산술 원전: Python 공식 fractions 및 decimal 문서. Exact float변환, Decimal exp/ln correctly-rounded HALF_EVEN의 계약을 확인했고 moment·comparison·tail 공식은 REPORT_KO.md에서 직접 유도했다.
