# 다음 대화용 C21N 연구 인계

아래 본문을 새 대화에 붙여 넣는다. 실제 document head와 main/closeout backup
object ID는 이 문서와 함께 배송되는 최종 authority receipt 또는 마지막 응답의
값을 덧붙인다. Document commit은 자신의 SHA를 내부에 저장할 수 없으므로,
실행 source는 아래 고정 content SHA로 별도 식별한다.

```text
$physmath-research-loop, SciSpace, Exa, Wolfram을 사용해
cosmosapjw-quantum/bass_cr와 rei_bianchi의 C21N 다음 연구를 이어서 해줘.
우선 다른 최신 branch/repo/접근 가능한 대화/Drive/Dropbox/Library에서
새 실행 결과가 왔는지 조사하고 source/input/build/solver/raw/receipt를
대조해 DAG에 수용해. 접근 불가능한 범위는 UNAVAILABLE로 명시해.

권위:
- Repository https://github.com/cosmosapjw-quantum/bass_cr
- C21N Draft PR93 https://github.com/cosmosapjw-quantum/bass_cr/pull/93
- Branch research/cr-c21n-mass-shell-cache-20261021
- 고정 content 5ecb8a6c4961302b7066b06278e72ecd2d77f8c9
- 부모 PR92 head 645a7f1a960be10e10574a819d7fb35a4511d9fa
- 물리 REI source 3b85dedce84d37b3e165da00685a8a984950aafe
- 연구경로 research/cr_c21n_mass_shell_cache_20261021/
- FINAL_CLOSEOUT_KO.md, BACKUP_RECEIPT.json, PUBLICATION_RECEIPT.json,
  REPORT_KO.md, RESEARCH_DAG.json, CODEX_HANDOFF_KO.md를 먼저 읽어.

완료 상태:
1. 원 C21L81 및 matter/radiation 성분 분리 게시 완료(PR90).
   component content17244259d25f793a25e0874443a28806e7c31d17,
   doc e954467132eef864a0fb86ba5de44f90f76b08e0.
2. 독립응력 초기조건 builder,26개 신규+원중심1 완료(PR91),
   content659c94312eb9c12ebb987de934459c12a63d67b0,
   doc b78a943e5d7ae341bbfe84f742a06a4ac36d0e43.
3. PR92 NCP98 반환을 실제 수용했고, 기존26+NCP98+원중심1=125개 완료.
   NCP98 canonical identity는
   7f89b12adbeee64a70832e633ae563584bc2a68f6ac433dc56f759a1946eb718.
   원4문서의 다른 suffix는 오기다. 원문을 바꾸지 않고 C21N intake 정정으로
   보존했다. 원 output manifest byte 확인은6/7; CSV LF↔CRLF 차이로
   field값은125행39열 모두 같다. 원 archive actual509regularfiles다.
4. C21N에서는 신규 과학 ODE0회. 기존125 raw를 후처리해 mass-shell
   도함수·초기 상쇄해제 shear계수를 유도하고 CSV/NPZ/PNG/PDF를 게시했다.
5. A-independent immutable 준비 계층을 구현했다. 매 A마다 distribution
   weights/packets/cell populations/energy normalization은 반드시 다시 만든다.
   원 DOP853/RHS/FP64/tolerance를 바꾸지 않았다.
6. 원 constructor15구성/moments45상태 bytes 동일,125 initialstate bytes 동일,
   mapping receipt dictionary equality,375저장상태의22,125field+15,000RHS
   FP64값 bytes 동일. Full new trajectory replay 검증은 NOT_RUN이다.
7. Shared runner는 CPU55/coordinator/thread1/lease 보호에 더해 disk/inode
   preflight와 완료125좌표 중복실행 차단을 구현했다. Fake worker3case와
   뒤에 바뀐 resource-wait guard 분기만 별도로 검사했다. 실제NCP 검증과
   구분하고 상세 성능benchmark는 수행하지 않았다.

정의:
sigma=diag(-s,-s,2s),pi_X=diag(-p_X,-p_X,2p_X),p_X=Delta_p_X/3.
signed S=sqrt(6)*s/H_t, P_X=sqrt(6)*(8*pi*G/c^2)*p_X/H_t^2.
Sigma=abs(S),Pi_X=abs(P_X): full Frobenius이며 half-contraction과sqrt2차이.
kappa=8*pi*G/c^4와는 H_geom=H_t/c로 대응한다. Photon+존재하는masslessnu
tensor를 radiation으로 합친 뒤 matter와 total을 만들고 norm을 취해.
Pi_tot를Pi_m+Pi_r로 놓지 마. Absent/unmodeled species를0으로 대체하지 마.

새 이론결과:
eta=ln(a/a0),zero-shear initial slice에서 직접 packet합 R_m을 계산하면
Ptot'_0=R_m-(4+2h0)*epsilon,
S''_0=R_m-(7+3h0)*epsilon,epsilon=Ptot0,h=H'/H이다.
이상적 S0=Ptot0=0에서는 R_m=-(1-beta_m)*Pm0이고
S(eta)=-0.5*(1-beta_m)*Pm0*eta^2+O(eta^3).
현재4비영 상쇄case의beta_m≈0.031700764391이다. 실제epsilon과FP grouping
잔차를 보존했다. 국소quadratic 대비 기존trajectory 상대차는 첫 양의
저장점eta0.0143508453에서최대2.1223%,eta0.1004559168에서15.8374%다.
국소계수 해석에만 사용하고1%모델/전체구간대체/오차상계로 승격하지 마.

기존125의 z4 endpoint norm 최대값(ensemble전용):
Sigma1.4449836382490454e-3,Pi_m1.2574783729509532e-5,
Pi_r6.344480064794384e-5,Pi_tot7.577499571350794e-5.
원81의다른ensemble최대값과혼동하지마.

아직 미실행:
- offgrid4 run_id c21n_offgrid4_opposing_z20_z4_20261021
- 입력 prepared_offgrid4/grid_offgrid4.json
- SHA256 2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5
- S0=0,Pm0=±7.5e-5,±1.75e-4,Pr0=-Pm0
- 초기조건 certificates와 sandbox plan은 완료, 과학ODE/NCP실행은NOT_RUN.
새 결과가 없다면 CODEX_HANDOFF_KO.md 명령으로 이4개만 실행해.
NCP명목64logicalCPU/128GB를 새로 관측하고 CPU55와 다른owner 작업을
보호해. Coordinator포함,workerthread1,가용affinity/quota/RAM/load/lease,
disk/inode에맞춰 dispatch해. 이4개는worker최대4개이므로 불필요한worker나
benchmark case를 늘리지마. 기존81/26/98/125의ODE를 재실행하지마.

Backup:
Main ZIP BASS_CR_C21N_RESEARCH_DELIVERY_20261021T122801Z.zip
36,735,301bytes
SHA256 df874b53da8eb3e434500a3e7196626755304850556939d0e93e5f41cd96c524
게시content의 C21L/M/N source/raw/analysis 1,296gitfiles를 포함한다.
문서 snapshot의 실제 main ACK는 Library libfile_991cd4c187dc81918078fd3e761cac90,
Dropbox id:BSpOijBcT10AAAAAAD_gTA 이다. Drive는1회요청후완료ACK가
없어 REQUEST_PENDING_NO_ACK이다. 늦은응답과실제객체를먼저확인하고
미확정요청을무작정중복업로드하지마.
Provider별 ACK/objectID와 다운로드재검증수준은 BACKUP_RECEIPT.json 및
최종authorityreceipt를 읽어. Main ZIP은 덮어쓰지마. 문서 마감ZIP은 별도다.

매 단계 EXECUTION | PUBLICATION | BACKUP | DAG를 따로 보고해.
완료 계산/새 구현/미실행을 구분하고 여기서 가능한 코드수정·focused 검산·push를
마쳐 NCP에는 실제 새 실행과 환경별 작은 수정만 남겨.
global_error_bound=null; 속도향상/RSS절감/64-core scaling UNMEASURED.
General triaxial/full coupled reionization/CMB는 HOLD.
기존C21F–K의source,HOLD,실패raw,역사적NOT_PUBLISHED는 보존해.
마지막에 한국어결과·실제commit/PR·SHA/ACK·DAG·다음handoff를 제공해.
```
