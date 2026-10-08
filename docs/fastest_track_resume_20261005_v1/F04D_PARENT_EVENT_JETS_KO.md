# F04D: 고정 original parent의 혼합 미분과 두 half-step 사건 미분

## 판정

SCOPED_MIXED_PARENT_AND_EVENT_JET_TRANSPORT_COMPLETE.

F04C의 4변수 온도의존 BE 잔차를 실제 owner의 7개 initial-state parent 좌표에 연결했다. R_p/R_zp/R_pp와 implicit 1·2차 미분, reconstructed 7state, PI9/CI3/RR3/DR2 사건 및 incremental escape의 same-parent two-half 합성을 구현하고 유한점에서 검산했다. 새 코드·시험·결과의 정본은 아래 immutable ZIP이다. 이 Git 문서는 요약·동기화·백업 영수증이다. Production Rust, receiver runtime_returns, CODEX_SYNC는 변경하지 않았다.

시작 및 게시 직전 bass_cr HEAD=3c7d7d4b811dd5f6eeafe60bafa1308a52dc1cf2, tree=fd1d83ccad021817bdede642f3427a00a630a55e. 동일 research/r4q-gap-closure-20261001 branch의 새 경로만 추가한다.

## 중요한 상태 갱신: owner 정적 F04 완료 수신

현재 수신한 rei_bianchi HEAD=b553698a114fbff05640ab6ecb95d260410de492, tree=8144ffac066134b5cde1c507336e241eb31eca44, branch=forward/rust-reion-kernels-20260922다. Owner는 실제 parent를 고정하고 제한된 정적 FT03 수학적 map 인증을 완료했다. 이번에는 그 결과·범위와 checker 소스를 읽었고 checker 또는 기존 campaign을 재실행하지 않았다.

주요 identity:
- runs/rei_fastest_v1/map_certificate/parent_manifest.json: blob ab4e317c09ebb0c22bfc605ae9b4bb5c9331ce22, certificate가 연결한 SHA256 f4112ac46d520d839fed2070388938c9b0db73a7e16c0d603d519463fca7f9a5.
- 같은 디렉터리 certificate.json: blob 70969be0f99756f85c3809ea86f9ddd6d4cab23e. 필요한 producer/연결 구간을 읽었으며 전체 파일 복원이나 proof 재계산은 하지 않았다.
- checker_receipt.json: blob 283efad33c92709410adcf35da18ef309f9def3c. 원문 bytes를 보관하고 blob을 확인했다.
- docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_map_constants.json: blob f53cd5ace49e713ef4ba7168ec90c377ccff5dbc. 원문 bytes·blob 확인.
- tools/check_map_certificate.py: blob 8fde751ea01e09e3fa8f82016e213a5026ea7a6f.
- runtime_returns/evidence/F04_certificate/checker.py: blob 9f169d8e13f9d7bb3e584d1db63693bd6c34f965. Independent MPFI source와 same-parent 조립 공식을 읽었고 실행은 하지 않았다.
- runtime_returns/EXECUTION_STATE.json: blob 73d628da81af290117c192984f951dce45a4bcb8.

수신한 checker receipt는 PASS, production_evaluator_called=false, precision_bits=200을 기록한다. 세 site q는 약(3.81208e-9,1.90667e-9,2.63960e-9), 네 full/two-half local bounds는(9.534453118819423e-9,4.601848744068603e-10,1.519527255699016e-11,8.185094581543662e-10), max public width=1.5867951486958153e-6이다. 이 수치는 owner 보고를 계승한 것이며 이번 새 검산 수치와 합치지 않는다.

따라서 ACTUAL_PARENT_DOMAIN_NOT_FROZEN과 정적 actual certificate NOT_RUN을 현재 blocker로 유지하지 않는다. Parent manifest/EXECUTION_STATE에 남은 옛 prerequisite 문자열은 최종 F04_actual_map_certificate 및 checker receipt보다 앞선 이력이다. 현재 owner 판정은 SCOPED_STATIC_NUMERICAL_DOMAIN_PASS__PHYSICAL_HOLD, 다음 canonical task는 REI-F05이며 다음 chat task는 REI-CHAT-FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION이다. 원 history·expanding S0·physical fit error까지 닫힌 것은 아니다.

## 실제 입력과 이번에 선택한 범위

q=(xHII,xHeII,xHeIII,w,p0,p1,p2), w=u/(nH*epsilon_eV), p_g=N_g/nH. epsilon_eV는 1eV의 erg 환산 에너지이며 counts는 per H, normalized energy는 1eV/H 단위다. 물리 상수 c,kB,epsilon_eV는 유지한다.

Owner의 정확 normalized center bits, sigma bits, model constants bits를 읽어 사용했다. 선택 필드를 저장한 inputs/OWNER_PARENT_EXTRACT.json은 원 manifest 전체 bytes가 아니다. 원 parent 반경은(1e-7,1e-7,1e-7,1e-5,1e-8,1e-8,1e-8)이고 h=1e9 s다. 이는 수학적 검증용 이웃이며 physical IC/source 불확실성 추정값이 아니다. nH/nHe, 고정 photon energies, coefficient family 및 모든 physical source parameter는 고정했다. 새 uncertainty나 interval box는 추가하지 않았다.

Compiled DR 상수는 owner의 dr_a_bits,b1_bits,b2_bits,b12_bits를 각각 독립적으로 읽었다. b12를 실수 b1+b2로 재생성하지 않았다. 실제 b12-(b1+b2)=4.3655745685100555419921875e-11 K를 보존했다. 이는 새로운 물리 오차 추정이 아니라 수학적 map identity에 필요한 상수 차이다. F04C rate reference 파일은 vendor에 원 bytes 그대로 넣고 별도 adapter에서 compiled DR 상수를 사용했다.

## 혼합 미분과 재구성

z=(xHII,xHeII,xHeIII,eta), eta=ln(T/1K), R(z,p)=0, A=R_z라고 하자. 이 루프의 energy residual scale Ustar=nH*epsilon_eV는 고정이며 old.u를 scale로 다시 미분하지 않는다.

    z_a = -A^(-1) R_a
    z_ab = -A^(-1) [R_ab + R_z,a z_b + R_z,b z_a + R_zz[z_a,z_b]].

Photons는 Nbar_g=N_g0/(1+h*kappa_g(x))로 복원한다. 따라서 reconstructed 7state의 parent 미분에는 z의 implicit 미분뿐 아니라 old photon과 h의 explicit 미분도 들어간다. EOS 온도와 ne는 full/half1/half2 각각의 endpoint 함수로 평가하며 서로 같게 고정하지 않는다.

부가적인 lambda=ln(h/h_ref) 방향은 형식적 점미분 API로만 구현했다. Owner의 7차원 인증 parent를 8차원으로 확장하지 않았다. 시간 미분 변환은 Y_h=Y_lambda/h, Y_hh=(Y_lambdalambda-Y_lambda)/h^2, Y_qh=Y_qlambda/h다. Source parameter uncertainty를 추가하거나 site별 독립 rate noise를 만들지 않았다.

## 두 half-step 합성과 사건 누적

수신한 owner checker에는 이미 정적 state의 J2*J1 및 H2[J1,J1]+J2*H1 합성이 있다. 이를 새 발견이나 재인증으로 주장하지 않는다. 이번 보조 결과는 4변수 reduced API를 그 parent 의미에 연결하고 17개 cumulative reaction events와 escape까지 2차 미분을 확장한 것이다.

    y1 = Phi_(h/2)(q)
    y2 = Phi_(h/2)(y1)
    J_total = J2 J1
    H_total,i = J1^T H2,i J1 + sum_j J2_ij H1,j
    E_accepted = (h/2)*e(y1) + (h/2)*e(y2).

사건 벡터 e는 PI9,CI3,RR3,DR2다. Escape는 같은 두 endpoint에서 평가한 에너지 유출률의 적분 increment다. 첫 half의 Hessian, 두 번째 half의 initial-state 의존성, h 자체의 미분을 빠뜨리지 않았다. 폐기된 full trial 사건은 accepted 누적량에 넣지 않는다. 마지막 endpoint의 사건률에 h를 곱해 두 half를 대신하지 않는다. Native controller의 tolerance 경계와 branch 선택 자체를 미분한 것은 아니다.

## 미분된 수·에너지 장부

fHe=nHe/nH이고 고정 모형에서

    I_N = xHII+fHe*(xHeII+2*xHeIII)+sum_g p_g
    L_N = Delta I_N - sum CI + sum RR + sum DR = 0
    I_E = w + chiH*xHII
          +fHe*[chiHeI*xHeII+(chiHeI+chiHeII)*xHeIII]
          +sum_g E_g*p_g
    L_E = Delta I_E + escaped_increment = 0.

에너지의 chi/E 수치는 동일 eV 단위다. Analytic map에서는 이 항등식과 original parent에 대한 1차·2차 미분도0이다. 구현은 각 half의 사건과 에너지를 같은 endpoint로 묶어 해당 장부의 값·gradient·Hessian을 함께 검사한다.

75자리 mpmath 점계산에서 two-half number residual의 최대 크기는 값1.1585e-77, gradient1.4787e-76, Hessian6.9548e-79였다. Energy는 값1.5747e-74, gradient5.1739e-75, Hessian9.0399e-76였다. 이는 임의정밀도 산술잔차이지 outward interval bound나 해당 자리수 정확성 보장이 아니다.

폐기된 full trial 사건·escape를 의도적으로 더한 부정 대조에서는 number defect=6.3560413180345947e-6 per H, energy defect=4.2212986080353811e-7 in 1eV/H units가 나타났고 미분 장부도 깨졌다. 이는 일부러 잘못 조립한 시험이며 production 버그를 발견했다는 뜻이 아니다.

고정 parent 중심의 새 점미분에서 dxHII/dw0는 full1.6966330157123319e-6, twohalf1.6969827608487721e-6이고 twohalf d2xHII/dw0^2=2.1799062350263168e-7이다. 온도결합으로 초기 열에너지에 대한 분율 응답이 실제로0이 아님을 나타내지만 전역 단조성이나 physical fit accuracy를 의미하지 않는다.

## 검증 증거와 한계

새 focused unittest24개 PASS, Python7파일 syntax PASS, JSON과 Markdown control-character 검사를 통과했다. 1개 시험에는 assertion RED→GREEN 로그가 있고 나머지23개는 tests-after다.

- R_zp/R_pp 관련272성분을 별도 고정밀 수치미분과 대조: max scaled error8.6361685551e-78, 사전 tolerance1e-45.
- 세 source site의 4변수 재구성과 7변수 original-coordinate implicit 미분1512성분 대조: max absolute discrepancy2.2993798778e-75. 서로 다른 좌표 미분 경로이며 독립 원자물리 소스 검증은 아니다.
- 25출력의 방향1·2차 미분50개를 centered/Richardson finite difference와 대조: max relative discrepancy1.2736034443e-26, 사전 tolerance1e-9. 네 perturbed parent는 기존7D box 안이고 h는 고정했다.
- Diagnostic driver의 새4D point refinements15회: central3과 finite-difference12, 최대 normalized residual1.6245527031e-74. 별도 smoke/unittest의 refinements도 있었으므로15를 세션 전체 실행 횟수로 쓰지 않는다.

새 실제 root 점계산은 있었지만 uniform root 인증을 다시 수행한 것은 아니다. Owner checker/interval campaign 재실행0, 새 native 실행0, 과거 science suite0, 원자 적분0, cosmological history0, owner box expansion0이다. 실행 argv/exit와 stdout은 logs 및 results에 보관했다. Direct raw GitHub 요청1회는 DNS 실패였고 connector 읽기는 성공했다. Independent human/agent review와 proof-assistant 검증은 없다.

이번의 새 cumulative event/escape jets에 대한 uniform Taylor remainder, actual native event/escape consumer binding, expanding source-stage weighting, physical rate error는 미완료다. 이미 수신한 owner의 정적 state/observable certificate와 이 추가 출력의 미완료를 섞지 않는다.

## 정본 ZIP과 실제 이중백업

파일=BASS_CR_CHAT_F04D_20261005_v1.zip
bytes=224864
SHA256=14a076a223ad62a445149521ae00683b8b88ac23e26227b3e5a19f827fd17879
ZIP41 members,40 payload의 SHA256/크기 및 CRC를 local에서 확인했다. Pycache와 이전 ZIP 전체를 넣지 않았다.

Drive upload success ACK 및 metadata readback:
id=1uZ-4xT8qIxX15FVkHu6WsQnD0hdlhsuL
parent=1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ
name=BASS_CR_CHAT_F04D_20261005_v1.zip
size=224864

Dropbox completed:
id=id:BSpOijBcT10AAAAAADyj1w
path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04D_20261005_v1.zip
size=224864
modified=2026-10-04T19:42:33Z

동일 immutable local archive를 두 provider에 create-only로 저장했다. R1 UPLOAD_VERIFIED(ID/name/size/path 또는 parent)다. Remote checksum은 응답에 노출되지 않았으며 full restore와 독립 remote byte-hash 검증은 하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. ZIP 안에 미래 업로드 성공을 미리 쓰지 않았다. 게시 commit/tree/readback은 별도 실제 DELIVERY_RECEIPT.json에 기록한다.

읽기: TASK_RETURN.json → INTAKE_ACK.json/SOURCE_BINDING.json → REPORT_KO.md → results/run01/SUMMARY.json. 필요할 때만 CENTRAL_PARENT_JETS/MIXED_RESIDUAL_BLOCKS를 읽는다. 새 코드는 src/chain.py,src/jet2.py,src/ft03_parent.py 및 research/run_f04d.py이며 standalone 패키지로 제공한다.

## 다음 연결과 유지한 claim gate

선택적 보조 노드=BASS-CR-CHAT-F04E_EVENT_JET_RECEIVER_BINDING. 실제 REI-F05 또는 이후 event-consuming call site의 state/time/units/accepted-step identity를 먼저 읽어 이번25-output 계약에 연결한다. 이미 있는 native record는 재사용하고, 부족한 필드만 정확하게 특정한다. 같은24/272/1512/50 검증과 old native probe를 새 목적 없이 반복하지 않는다. 정적 escape increment에 팽창 가중치를 붙일 때 실제 source-stage/time convention을 별도로 고정한다. 새로운 강제 선행 gate가 아니다.

CR_OFF_FASTEST, precision atomic PARKED, G02=UNRESOLVED, production physical admission=HOLD, capture=false, all_bound=OPEN,b_grid=NO_GO를 유지한다. 실제 CR-off dispatch는 이번에 검사하지 않았고 source/loader/callback 관측=null이다. 이를 전역 interface 부재나 실제0회 호출 증거로 바꾸지 않는다. S-only window 상계5.599633283869504e-17 및7.49726779045559e-17 ta^-1은 계승한다. CR-on/full-K/R4AQ/318patch/소비된 승인은 재사용하지 않았다.
