# CR-XTHREAD-R10: source/cutoff 경계와 optical quadrature의 jump 보정

2026-10-08 KST. EXACT_EVENT_KERNEL_AND_SOURCE_ATLAS_COMPLETE__CONTINUOUS_TAU_OPEN.

R9의 실제 네 노드 cubic readout은 변경하지 않았다. 이번에는 그 정칙성 전제에 필요한 source/cutoff event 위치와 derivative-jump의 적분 기여를 유도·구현했다. 과거 tau 이력을 다시 적분하거나 더 높은 다항식으로 바꾸지 않았다. 실제 jump 진폭·node error·regular fourth-derivative bound가 미제공이므로 실제 연속 tau enclosure는 null이다.

## 최신 intake와 scope

bass_cr intake=96d3f163d5fa176a696711a52d7131e35fdb4157, branch=research/r4q-gap-closure-20261001.
HE=20cc88382b2280ec0f42fd2539acfd163dd0f1b1. E3는 CR R8/R9 원 코어의 실제 사용을 보고한다. 실제 rate9개 목표는 Gauss2/4축에서 FAIL이고 시간축은 기준 이내다. 다음 HE E4의 same-state cutoff-aware rate 연구를 대신 실행하지 않았다.
REI=d78f52bc194ed03fcc0c02fdec750b6398938e8c. BRIDGE08은 첫 macro의 carried-energy/count family를7cohort까지 연결했으며 다음은 BRIDGE09 parameter-aware acceptance다. 새 root 결과는 수신만 했다.
HH Git=649ecb06321d3f7956fc13902666f062dfcde50c. HE가 Library ON06G(total256,t3.2e11s)를 수신했다고 보고하지만 이곳에서 직접 읽지 않았다. Git 무변화를 HH 전체의 무진전으로 해석하지 않는다.

과학 입력은 historical HE E2 c8820730aa8b1249be07abe55fe8117ea57d212557e18f8a58436956ff2f353f와 R9 7d45de8687487431edba6664fe51243e30bf50ea7658b16eb844eaa6df975207이다. 정확9개 선택 payload와 source identity를 SOURCE_BINDING.json에 보존했다. HE E3의535payload 사용자첨부 E2와 여기의 remote E2(5개 완료) archive를 혼합하지 않았다. 다른 owner source/default/CURRENT/production mutation은0이다.

## 직접 유도한 정칙성 구조

ell=ln(a), proper density[cm^-3], D=1, C_T=c_SI*sigmaT_SI*1e6로 둔다.

    Xe=h+fHe*(y+2z), A=C_T*nH/H, q=A*Xe, tau=integral q d ell.
    E_i/eV=exp(eta_i-ell)
    Gamma_a=c_cgs*nH*sum_i omega_i F_i sigma_a(E_i).

q/tau/ell은 무차원이고 Gamma는 absorber당s^-1이다. 원 fit support cutoffs13.60/24.59/54.42eV를 binding chi와 동일시하지 않는다.

명시적으로 고정-node continuous target을 정의하고, 고립된 cutoff에서 gas/photon/background가 연속이라고 가정하면, stock와 absorber가 양수일 때

    [Gamma_a]=-c_cgs*nH*omega_i*F_i*sigma_a(Ecut+)
    [q_ell]=(A/H)*sum_a nu_a*[Gamma_a]
    nu=(1-h,fHe*(1-y-z),fHe*y).

대괄호는 오른쪽-왼쪽 jump다. Sourcefront에서 F_i'=j_i-(kappa_i/H)F_i와 매끄러운 sigma를 가정하면 [F_i']=[j_i], [Gamma_a,ell]=c_cgs*nH*omega_i*sigma_a*[j_i], [q_ellell]=(A/H)*sum nu_a*[Gamma_a,ell]이다. 더 높은 미분jump도 일반적으로 남는다.

이는 모든 실제 event의 비영 jump를 관측한 결과가 아니다. 최종 snapshot density를 과거 event density로 쓰지 않았다. Native floating program의 미분이나 연속 에너지 적분을 먼저 취한 물리모형에 같은 jump를 자동 적용하지 않는다.

## 정확 event-aware 적분 계약

한 panel의 실제 네 노드와 R9 weights에서 L(f)=integral f-sum w_i*f(x_i)를 정의한다. H_r=(x-xi)_+^r/r!, r=0..3의 정확 kernel은

    K_r(xi)=(b-xi)^(r+1)/(r+1)!-sum_(x_i>xi) w_i*(x_i-xi)^r/r!.

r=0이 sampling node에 놓이면 left/right trace가 필요하다. Piecewise C4 target의 모든 jump J_(j,r)=[f^(r)]를 H_r로 빼면 0..3미분이 연속인 W4infty 함수가 남는다. 따라서

    L(f)=sum J_(j,r)*K_r(xi_j)+integral K_3(t)*f_regular^(4)(t)dt.

R9의 안전한 Lagrange 상수 B4=integral|product(x-x_i)|/24를 그대로 사용해, 실제 node error e_i와 M4를 공급받았을 때

    integral f in Qhat+sum[J]*[K_r(Xi)]
                  +/- (sum|w_i|e_i+B4*M4)

를 계산한다. Uncertain event 위치는 actual node에서 분할한 polynomial Bernstein 범위로 감싼다. Event box가 panel을 가로지르면 단일panel API는 거절한다. Event 진폭/완전한 목록/node error/regular bound 중 빠진 전제를0으로 만들지 않는다. 외부 전제의 과학적 정당성 자체를 자동 인증하는 함수는 아니다.

정확 반례: nodes(0,1,2,3), f=(x-1/2)_+의 cubic quadrature는51/16, 실제 적분25/8, jump correction은-1/16이다. 양쪽 regular fourth derivative가0이라는 이유로 전역 C4처럼 취급하면 틀린다. R9의 원 전제가 참인 경우를 반박한 것은 아니다.

Unit panel nodes(0,1/3,2/3,1)에서는 K1(1/6)=-1/144, K1(1/3)=1/72, K1(1/2)=0이다. Event가 sampling node인 것만으로 충분하지 않다. 연속함수의 derivative jump는 panel boundary에서 분할하거나 kernel로 보정해야 한다. 모든 jump가 비영 적분오차를 만드는 것도 아니다.

## 실제 source grid 결과

Canonical E2 OFF_N384_P512_O4 final spectrum의 immutable eta2440개와 양의 weight만 사용했다. 실제 N384 clock385개는 R9의128개 cubic panel을 정한다. log는90항 atanh급수와 명시적 tail, 뒤이어192fractional-bit outward dyadic rounding으로 감쌌다.

|잠재 경계|event수|영향 panel수|
|---|---:|---:|
|HI fit cutoff13.60eV|0|0|
|HeI fit cutoff24.59eV|96|96|
|HeII fit cutoff54.42eV|96|96|
|source start100eV|96|96|
|source stop13.7eV|96|96|

총384개가 서로 다른96개 panel 내부에 있다. 모든 위치구간은 하나의 actual time cell 안에 엄격히 포함되며 node/window ambiguity는0이다. N24의23개 내부anchor 중16개는 optical panel 경계가 아니다. 이 inventory는 세 fitted cutoff와 두 sourcefront에 완전하며, 모든 thermal branch의 정칙분할까지 완전하다는 뜻은 아니다.

최대 event interval width=1.5930919111324523e-58, native-like eta-f64log(E)와 exact-real 위치의 최대 차이=4.341512446764499e-16이다. 둘을 같은 비트로 치환하지 않는다.

HeI/HeII의 sum|K1| 상계는 표시값1.188375350164104e-12/1.188375350755381e-12다. 각각 kernel 부호48양/48음이다. Source start/stop의 sum|K2|는2.052353935254430e-19/2.052353935224853e-19다. 이는 단위 derivative jump에 대한 geometry 감도이며 실제 tau 오차나 다른차수 사이의 정확도 비율이 아니다. 전체 interval은 results/final/EVENTS.json에 있다.

## 실제 실행 및 검증

새23unit PASS(1assertion RED→GREEN,22tests-after),19artifact조건 PASS,8새Python파일 syntax PASS. 별도 exact moment선형계128사례/512kernel항등식/2560uncertain-location검사/512piecewisequartic적분 enclosure가 통과했다. mpmath120자리 독립경로의 actual 위치384개와 kernel1536개가 interval 안에 있다. 작업자릿수는 물리정확성이 아니다. 독립human/agent심사와 proofassistant는 미수행이다.

첫 atlas는20초tooltimeout, output0개였다. 잔존process없음을 확인하고 원 code/log를 보존했다. 이미 증명한 로그구간을192bit dyadic으로 바깥쪽 확장해 산술크기를 줄여 새 directory에서 완료했다. 입력·물리식·과학허용오차는 불변이다. 동일 결과를 final로 옮겼고 old science나 R9readout을 반복하지 않았다.

Native/IVP/root/atomicprovider/oldscience/BASSreceiver/otherrepo mutation은 모두0이다. 새 exact log/event/kernel/합성대조는 실행했다. Rust환경은 사용하지 않았다.

## 실제 게시와 정본 백업

Core event_readout.py commit0e6ded5fdc136c2b49782b90247827957c010e84, blobd0a336b0afb0a691460f8ea99278b8f7da05b2ed,size6637.
exact_log.py의 최초 게시 dcfa5566ab88d2bd32fc4c6747eb7c38f5d28b6e는 불완전한 payload 전송이었다. d861742b1d54c167c5cc270250370611714a3b8d에서 봉인된 시험 원문으로 교정했다. 최종 blobca73e3f4bbb46ad0f407281652bc9b1a3c5dad32,size1517은 local tested source와 같다. 계산코드/결과/ZIP을 바꾼 것이 아니며 publication failure와 correction commit을 보존한다. 두 core의 remote directory metadata가 시험 blob/size와 일치한다.

Archive=BASS_CR_XTHREAD_R10_20261008_v1.zip
bytes=587365
SHA256=f042fd73f7cb24f60c5029fff90d1e227d5ba715046d16c2d2dea7505363e7ed
50entries/49payload localCRC/SHA/size검사 및 verify-only exit0.

Drive: success 및metadata name/size/parent 일치, id18srkWeiM-z5lfW1BW03yZOBLUrq3fyra, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ.
Dropbox: completed,id:BSpOijBcT10AAAAAAD3Sgw,size587365,modified2026-10-08T01:35:27Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_XTHREAD_R10_20261008_v1.zip.

동일 ZIP을 create-only 저장한 R1 UPLOAD_VERIFIED다. Remote checksum은 노출되지 않았고 새ZIP 원격전체복원/독립bytehash는 미수행이다. 실제 최종commit/tree/provider ACK는 ZIP밖 DELIVERY_RECEIPT에 남긴다. Git은 core+summary+return, 전체실행자료는ZIP이다.

다음 최소입력은 같은 continuous target의 event 양측 상태/rate jets 또는 상계와 node error, thermal까지 포함한 정칙분할이다. 이 입력 전에는 actual jump/tau certificate/ownerR10ACK는null이다. 기존 R8/R9의 HE scoped reuse와 새R10 adoption을 구분한다. CR_OFF_FASTEST,precisionatomicPARKED,HH ACTIVE,canonicalS0OFF,physicalHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capturefalse를 유지한다.
