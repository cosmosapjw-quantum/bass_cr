# FLRW-PRQ01: local rate / photon number / filling factor 복원

2026-10-04 사용자 요청의 이론 검증 결과. Peebles effective-three-level benchmark와 별개이며 기존 CR-off fastest 모형, F00 Case-A lock, receiver production 코드를 변경하지 않는다. Bianchi/consumer 구현 소유자는 rei_bianchi다.

## 상태

- 국소 photoionization–recombination rate equation 및 photon-number equation: 선언한 변수/closure에서 직접 유도하고 Wolfram 기호 검산.
- filling-factor 고전식: 단순 등방 극한이 아닌 two-phase/averaging/photon-budget closure 아래 조건부 복원.
- 현재 지정 Rust 함수: exact source를 읽어 방정식 대응 확인. Rust를 실행한 regression이나 전체 history 수락이 아니다.
- 실제 원자/native/과거 suite/history 호출 0. Python과 container 도구는 각각 ClientError로 시작 실패했으며 메모리/권한 문제로 추정하지 않았다.

## 읽은 identity

bass input HEAD=936f78d535416281276102ba825b747c9355c0fc.
receiver input HEAD=67957715cf3336b89c27c1e59c33ca23098f8934, branch forward/rust-reion-kernels-20260922. 시작 및 중간 조회에서 동일했다. 이후 원격이 전진하면 아래 경로의 bounded diff만 추가 확인한다.

| receiver path | Git blob |
|---|---|
| rust/rei_microphysics/src/homogeneous_rates.rs | d5aedfd37485b33c82a4cf0ee1d854099a517842 |
| rust/rei_microphysics/src/group_rates.rs | 17984eb686719e4b7213095202d96ff56fd86038 |
| rust/rei_microphysics/src/lib.rs | b36af83364747cb4b93aee2b295033ed3647cd92 |
| docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/closure_process_decision.json | 456bf4fd1a6f1005b69cdbb0c246a8ec50a5d60e |

## 1. 국소 H 분율

signature=(-,+,+,+), t=gas proper time, n_s=proper density, N_s=a^3 n_s. h=2pi hbar, c와 kB 유지. pure H primary model부터 검증하고 helium/secondary/다른 흡수자는 별도 event owner로 확장한다.

nH의 dilution continuity와 HII의 source continuity를 나누면

    dot x=(1-x)(Gamma_HI+k_ci*n_e)-alpha_X*n_e*x
    Gamma_s=4pi integral J_nu sigma_s/(h nu) dnu
           =c integral n_nu sigma_s dnu
    n_nu=4pi J_nu/(c h nu)

이다. fraction에 -3Hx를 더하지 않는다. pure H에서 n_e=nH*x이면 recombination은 x^2이며, 고정 n_e의 scalar constant-rate oracle은 다른 문제다. Helium이 있으면 n_e=nH*xHII+nHe*(xHeII+2*xHeIII). 이미 bin/angle 적분된 photon count에 4pi나 bin width를 중복 곱하지 않는다. dt/dz=-1/[(1+z)H].

Case A/B는 geometry에서 결정되지 않는다. Explicit ground recombination continuum은 alpha_A sink와 같이 계상한다. OTS로 같은 ground photons의 local reionization을 제거하면 alpha_B=alpha_A-alpha_1. alpha_B와 동일 ground diffuse photon source를 동시에 적용하면 중복이다. 고온 excited free-bound ionizing yield, helium cascades, secondary electrons는 별도 정의가 필요하다.

## 2. Spectral / integrated photon number

평균 energy intensity에 대해

    (partial_t-H nu partial_nu)J_nu+3H J_nu
       =-c kappa_nu J_nu+c epsilon_nu/(4pi)

를 사용한다. epsilon은 proper energy emissivity. s_nu=epsilon_nu/(h nu)로 바꾸면

    partial_t n_nu-H nu partial_nu n_nu+2H n_nu=s_nu-c kappa_nu n_nu
    partial_t n_nu+3H n_nu+partial_nu(-H nu n_nu)=s_nu-c kappa_nu n_nu
    partial_t N_nu+partial_nu(-H nu N_nu)=a^3 s_nu-c kappa_nu N_nu.

Spectral number의 2H와 integrated proper number의 3H, integrated energy의 4H를 구별한다. 순 공간 경계flux가 0인 비교영역을 사용한다.

고정 물리 문턱 nuH 위에서 적분하면

    dot N_gamma^>=E_gamma^c-A_gamma^c-Z_H^c
    Z_H^c=H nuH N_nu(nuH)

이다. H>0, high-frequency boundary flux=0 가정. Collisionless라도 ionizing-band comoving number는 일반적으로 감소한다. 전체 frequency의 comoving number만 conserved다. q=a nu 좌표로 바꿔도 원자 문턱 qH=a nuH의 이동에서 같은 손실이 나온다.

고정 물리 frequency bin에서는

    dot N_g=E_g-A_g+F_(g+1)-F_g, F_g=H nu_g N_nu(nu_g).

공유 edge flux를 사용하면 내부항이 telescoping한다. 실제 spectral inflow가 있는 최상위 edge를 0으로 놓지 않는다. F_g=r_g N_g는 within-bin spectrum closure를 필요로 하므로 r_g=H 또는 임의 redshift_coeff만으로 continuum 복원을 선언하지 않는다.

## 3. Joint photon/atom budget와 filling-factor defect

주기적 또는 순경계 flux가 0인 같은 comoving domain의 NH=a^3 mean(nH)를 사용한다. XM=mean(nH*x)/mean(nH). E_ext와 E_rec은 추적한 band의 comoving number emissivity, RA는 total recombination event, Icoll은 collisional ionization, Lother는 추적 H와 중복되지 않은 photon owner다.

    NH dot XM=A_H-RA+Icoll
    dot N_gamma=E_ext+E_rec-A_H-Lother-ZH
    NH dot XM+dot N_gamma=E_ext+E_rec-RA+Icoll-Lother-ZH.

E_rec=R1이고 RA=RB+R1인 declared one-photon ground-recombination closure에서는 RHS가 E_ext-RB+Icoll-Lother-ZH가 된다. General hot/cascade model의 photon yield를 R1로 가정하지 않는다. 같은 recombination/absorber를 RA와 Lother에 중복 넣지 않는다.

QV=mean(I_HII), Delta_i=mean(nH|ionized)/mean(nH),

    XM=QV*Delta_i+deltaX,
    deltaX=mean[(nH/mean(nH))*(x-I_HII)]

이므로

    dot QV=[E_ext+E_rec-RA+Icoll-Lother-ZH-dot N_gamma]/(NH*Delta_i)
           -QV dot Delta_i/Delta_i-dot deltaX/Delta_i.

이것이 고정 비교영역의 일반 회계식이다. s=E_ext/NH, F_std=s-QV/t_rec에 대한 정확한 defect는

    dot QV-F_std=s*(1/Delta_i-1)
      -[dot N_gamma+ZH+Lother-Icoll]/(NH*Delta_i)
      -(RA-E_rec)/(NH*Delta_i)+QV/t_rec
      -QV dot Delta_i/Delta_i-dot deltaX/Delta_i.

따라서 고전 dot Q=E_ion,IGM^c/NH-Q/t_rec은 sharp two-phase, Delta_i=1 constant, deltaX=0, photon storage/threshold loss/other owners의 제어, 일관된 recombination closure를 추가해야 나온다. 작은 omitted terms를 가정하지 않고 위 defect의 항별 상계 또는 측정을 요구한다.

상수 alpha_B, ionized phase의 chi_e=n_e/nH와 conditional clumping C_i일 때

    R_B^proper=alpha_B*chi_e*QV*C_i*(Delta_i*mean(nH))^2
    1/t_rec=alpha_B*chi_e*C_i*Delta_i*mean(nH).

Global mean에 포함된 Q를 conditional C_i와 중복하지 않는다. 온도/전자밀도 상관은 별도다. Q=0에서 conditional ratio를 직접 계산하지 않는다. Photon-counted source에 (1-Q)를 다시 붙이거나 Q=1에서 남는 photon budget을 버리고 clipping을 conservation으로 부르지 않는다.

## 4. 정확한 반례와 실제 검산

Wolfram stateless evaluator의 대수 항등식18개 및 general filling defect/partial-ionization identity2개, 총20개 모두 True. Full executable Wolfram blocks와 observed outputs는 아래 완전 보고서 section12에 있다. 수치 solver 테스트20개라는 뜻은 아니다.

- Uniform density, mean x=1/2: everywhere partial x=1/2이면 rec moment=1/4, half fully ionized/half neutral이면1/2. 같은 평균분율에 sink가2배 다름.
- Equal volumes, n=(3/2,1/2), x=(1,0): mean n=1, QV=1/2, XM=3/4, Delta_i=3/2, recombination moment=9/8.
- 같은 photon count, nu/nuH=2와4, diagnostic sigma~nu^-3: Gamma ratio8. 원자 fit 채택 아님.
- Initial photon reservoir=0 with positive emission: initial photoionization=0, photon storage derivative>0. Instantaneous absorption closure는 initial layer에서 exact하지 않음.
- Rational four-bin transport example sum=-1/7을 별도 확인.

Free-streaming n_nu=a^-2 exp(-a nu)에서 exact N_gamma^>=exp(-a nu0) 및 threshold flux를 기호 확인했다. 최초 infinite-domain NIntegrate12개는 underflow/stop warning을 냈다. 출력된 작은 오차를 clean pass 또는 rigorous enclosure로 채택하지 않고 경고를 기록했다. 이후 별도의 u in [0,100] diagnostic과 exact exp(-100) tail은 메시지 없이 완료; tail<10^-43을 확인했다. WorkingPrecision60에서 closed form과 차이는 numerical zero였지만 rounding enclosure나60자리 정확도 보증이 아니다. 기존 계산을 repeat/replay하거나 source tolerance를 바꾸지 않았다.

## 5. 실제 source 대응의 한계

homogeneous_photo_rates는 proper V=(a*MPC_CM)^3으로 한 번 변환하고 동일 sigma로 photon loss와 species event를 계산한다. 식 수준에서 loss/V=sum events가 성립한다. 이 함수는 primary absorption ledger이지 전체 recombination/history solver가 아니다. 이번 Rust 실행은0.

legacy photon_rates의 group sum은 source sum-absorption sum-r0*N0이다. Internal flux conservation은 대수적으로 대응하지만 redshift_coeff의 physical edge-spectrum binding은 별도다. Legacy effective-MFP lowgroups와 homogeneous local Gamma를 무조건 섞으면 same-owner photon accounting이 보장되지 않는다. 의도된 compatibility API를 이번 이론으로 덮어쓰지 않는다.

현재 읽은 State의 x_hii는 QV 또는 phase population이 아니다. Q 구현의 부재 판정은 지정 crate/읽은 경로에 한정한다. 실제 Q interface를 발명해 실행하거나 상태를 재명명하지 않는다.

## 6. 실제 전달

전체 보고서: 유도·가정·정확 반례·20개 기호검사 코드/출력·경고·source map·machine-readable 판정·다음 실행 계약을 한 문서에 보존.
Native Google Doc ID=10Nw044PzWc_UdtUcGn2SGEAVfqOEGdJ9pcfueYlPV34
https://docs.google.com/document/d/10Nw044PzWc_UdtUcGn2SGEAVfqOEGdJ9pcfueYlPV34/edit

동일 export file reference의 plain-text mirror:
name=FLRW_PRQ_THEORY_AND_VERIFICATION_20261004_v1.txt
bytes=26402
Google Drive ID=1JCgHCwu9T-01wyuMGLTc_BFf9tjjdItv
Dropbox ID=id:BSpOijBcT10AAAAAADyH0A
Dropbox path=/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/FLRW_PRQ_THEORY_AND_VERIFICATION_20261004_v1.txt

두 provider 완료 ACK/ID/name/size를 확인했다. R1 UPLOAD_VERIFIED이며 remote byte readback/SHA-256 independently verified는 false다. Container/Python runtime 불가로 SHA를 계산하지 않았으며 metadata adapter도 checksum을 반환하지 않았다. ZIP/CRC/새 binary manifest를 만들었다고 주장하지 않는다. Export text와 Git 요약은 다른 artifact이며 byte identity를 주장하지 않는다. Codex는 한 인증된 mirror를 직접 회수하고 사용자가 재업로드하지 않도록 한다. 추후 runtime에서 local SHA를 계산할 수 있으나 이번 R1을 소급 R3로 바꾸지 않는다.

## 7. 다음 bounded 연구 및 실행 계약

FLRW-PRQ02_SOURCE_BOUND_EVENT_AND_REDSHIFT_REGRESSION.

L lane: actual hydrogen RHS에서 동일 alpha/case/ne/units를 고정. Expansion dilution cancellation, pure-recombination exact reference, source-off 한정 회귀를 검증한다. F02 constant-ne oracle로 nonlinear ne를 대체하지 않는다.
P lane: 실제 F01 absorption 함수의 photon loss/V=sum species events를 targeted 실행한다. Legacy group flux는 edge-spectrum profile을 잠근 뒤에만 continuum recovery를 주장한다. Internal cancellation/lower threshold loss/upper inflow/empty-photon initial layer를 검사한다.
Q lane: 실제 phase/averaging API가 있을 때 XM,QV,Delta_i,deltaX와 defect를 연결한다. 없으면 NOT_APPLICABLE_TO_HOMOGENEOUS_STATE 및 receiver binding 미실행으로 남긴다.
Source-bound 검증 이후에만 짧은 같은-model coupled regression을 판단한다. 이 문서 자체는 history 실행 승인이나 production 물리 변경이 아니다. 이미 완료된 PB01, F01 및 기존 suite를 전수 반복하지 않는다.

원전: Madau/Haardt/Rees1999 DOI10.1086/306975(arXiv:astro-ph/9809058v1) Eq2/Eq20; Haardt/Madau2012 DOI10.1088/0004-637X/746/2/125(arXiv:1105.2039v3) Eq1/Eq18; Madau2017 DOI10.3847/1538-4357/aa9715(arXiv:1710.07636v1) Eqs2-4 및 pre/post-overlap 논의. HM2012 PDFp2와 M2017 PDFp5는 시각 확인했다. MHR PDFp14 및 HM PDFp7 screenshot 실패를 보존했고 parsed text와 구분했다. 실제 source-fit accuracy/observational cosmology를 새로 채택하지 않는다.

```json
{"task_id":"FLRW-PRQ01-20261004","state":"THEORY_REDUCTION_CHECKED_SOURCE_READ_RUNTIME_REGRESSION_NOT_RUN","symbolic_checks":20,"symbolic_all_true":true,"actual_rust_regression_run":false,"atomic_integrations":0,"cosmological_histories":0,"production_mutation":false,"case_B_universal_requirement":false,"X_M_equals_Q_V_without_assumptions":false,"infinite_quadrature_diagnostic":"WARNINGS_RETAINED_NOT_ACCEPTANCE","finite_quadrature_diagnostic":"COMPLETED_NO_MESSAGES_NOT_INTERVAL_CERTIFICATE","next_task":"FLRW-PRQ02_SOURCE_BOUND_EVENT_AND_REDSHIFT_REGRESSION","dual_backup":"R1_ID_NAME_SIZE_ACK_VERIFIED","archive_sha256":null,"sha256_reason":"No local runtime; provider metadata did not expose checksum","preserved_gates":{"G02":"UNRESOLVED","production":"HOLD","capture":false,"all_bound":"OPEN","b_grid":"NO_GO"}}
```

새 NCP 원자 batch, full-K, R4AH10점/M9/중심점, legacy precision lane, consumed approvals, 318파일 patch를 열지 않는다.
