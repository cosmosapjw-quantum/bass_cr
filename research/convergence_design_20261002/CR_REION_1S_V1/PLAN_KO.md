# BASS_CR → Bianchi 재이온화 수렴 설계

2026-10-02. 목적은 범용 원자충돌 프로그램이 아니라 Bianchi 재이온화 소비자가 실제 수락하는 H+ + H(1s) source와 portable 참조 구현이다. 설계/이론/구현/물리승인 상태는 서로 구별한다. 현재 G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO. 이번 전달·설계 단계의 신규 scattering query와 완료된 R4Z/R4AA 시험 재실행은 모두0이다.

## 1. 전달 결과와 상세 산출물

R4AA ZIP과 validation JSON은 Google Drive와 Dropbox에 create-only 저장됐다. 각각 ACK/원격ID/크기를 확인한 R1 UPLOAD_VERIFIED다. 원격 checksum은 반환되지 않았고 byte restore를 하지 않아 RESTORE_VERIFIED=false다. 이전 NOT_PERFORMED receipt는 immutable 역사로 보존했다.

원본 package: BASS_CR_R4AA_OFFCENTRAL_MINUS32_PACKAGE_20261002_v1.zip, 40892194 bytes, SHA256 7642eeadde16aa83fd5bc2e0c1951cc617d94603d0a79100b6f8d9ed6f7047e6. Drive ID 1wU90Nos02vCrvGR_dKiZJxIXsuM1hyou, Dropbox ID id:BSpOijBcT10AAAAAADxkbA.

상세 설계 package: BASS_CR_BIANCHI_REIONIZATION_CONVERGENCE_20261002_v1.zip, 72197 bytes, SHA256 25e25ee1363baa020429fe41f034c76782a4474fd1675fc74af059b6d79da1be. Drive ID 13qma46uo9wdCQEKQ0eNLtPMgQVxdWp8H, Dropbox ID id:BSpOijBcT10AAAAAADxknw. 실제 두 provider가 완료와72197 bytes를 확인했다.

설계 ZIP에는 상세 DESIGN_KO.md, DAG.json, provider/R4AB 계약, external queue, claim matrix, source ledger, 실제 consumer 원문2개, DBv13 상태 snapshot, exact algebra check, 다음 handoff가 있다. 20members의 CRC와19payload SHA, 설계/source-pin 일관성40checks를 확인했다. 이 검사들은 atomic solver 시험이 아니다.

현재 Git 게시 범위는 R4AA 전달 인덱스와 이 수렴 설계다. 원래379파일/10174852bytes의 source mapping 전체는 아직 적용하지 않았다. 전체 코드/raw/native/DB는 양쪽 cloud의 원본 ZIP에 있다. 직접 git 연결은 DNS 오류였고 connector에 mounted-file binary bulk upload가 없었다. Git의 UTF8/tree 쓰기 성공을 전체 source-tree 동기화라고 보고하지 않는다.

## 2. 과학적 출력 계약

회수한 HOST4 H16의 목적은 H0_CR_1s_FORMATION_COUNT__NOT_TOTAL_GAS_HII다. 이2026-09-22 목적 문서를 최신 actual host 상태로 간주하지 않는다. 최신 receiver commit/state/measure 및 fast outgoing acceptance는 물리 연결 전에 따로 pin한다.

반응 p_CR + H_g(1s) -> H_CR(1s) + p_g의 species순서(p_CR,H_g,H_CR,p_g,e_free)에 대한 변화는(-1,-1,+1,+1,0)이다. 전체 nuclei/charge/HII/HI/free-electron 변화는0, gas proton변화는+1, CR proton변화는-1이다. 이 정수대수는 이번 Wolfram 계산으로 확인했다. 이는 열화/운동량전달의 계산은 아니다.

포획 생성률을 자유전자 source 또는 photoionization에 그대로 더하지 않는다. CX의 간접 재이온화 효과가0이라는 뜻도 아니다. reservoir/neutral transport/heating을 계산하려면 그 목적에 맞는 differential kernel 또는 정당화된 transport moments/closure가 필요하다. formation_count_1s, reservoir_transfer, momentum_or_heat capability를 분리하고 미지원 출력은 UNSUPPORTED로 거절한다. 빠른 중성자 생성수를 R*E로 가열률에 대입하지 않는다.

## 3. 채택한 구조

원자 source 경로: A1 R4AB intrinsic Gram → A2 scoped operator → A3 authentic state/window/selected observable → A4 selected1s coupling-basis+b+energy source.

소비자 경로: C0 purpose/provider binding → B1 typed count/error adapter → B2 Bianchi gas-frame/reservoir interface.

합류: A4+B1 → M1 physical source admission; M1+B2 → M2 actual host replay/parent acceptance → F scoped closeout.

C0와 A1은 병렬이다. B경로는 labelled synthetic/model/evaluated source로 먼저 구현할 수 있으나 그 시험이 물리승인은 아니다. 다른 source를 실제 대체하려면 별도 amendment/intake가 필요하며 A경로 기존gate를 소급 닫지 않는다. '모든 원자반응 완료 후 소비자 구현'과 '문헌표를 써서 solver 결함을 숨기기' 두 구조는 채택하지 않는다.

## 4. 다음 한 원자 작업: R4AB

회수한 same_center_blocks는 외부핵 거리R로 분할한 radial quadrature를 intrinsic overlap에도 공유한다. R4AA의 same-center1ulp 변화가 window차이 제곱합의96.3–97.5%를 차지한다. 따라서 움직이는 V_other partition과 intrinsic S/H0/A의 적분을 분리한다. 코드 구조와 저장 결과에 근거한 다음 검증 설계이며 수정 성공을 미리 선언하지 않는다.

저장 candidate는 s=(r-r_e)/Delta r_e에서 u(s)=(1-s)L+sR+s(1-s)(q0+q1*s+q2*s^2)이며 c=(L,R-L+q0,q1-q0,q2-q1,-q2)다. normalized spherical harmonics와 phi=u(r)Y_lm/r에서
G_ab=delta_ll' delta_mm' sum_e Delta r_e sum_ij conj(c_ai)c_bj/(i+j+1).
이는 저장 candidate polynomial 자체의 정확한 적분식이다. 원래 잃어버린 nodal eigensolve 복원이나 physical basis certificate가 아니다. 공통 unitary translation/ETF는 Gram에서 소거된다. 실제 비직교 offdiagonal을 유지하며 G를I로 바꾸지 않는다.

새 r4ab_intrinsic_gram 경로에서 gram_exact.py, gram_fixed.f90, intrinsic_blocks.py, reassemble_saved.py, test_gram.py, test_reassembly.py를 구현한다. 제안 path이며 이번 설계에서 구현한 것은 아니다. exact oracle과 deterministic FP64값을 분리하고 H0/A 원점정칙성과 fixed-panel 오차를 검사한다. H/D의 v^2 S항까지 새 G와 일관되게 재조립한다. 옛 full H/D를 둔채 S만 바꾸거나 A를 강제 반에르미트화하지 않는다.

최초 raw cross cap=0. qualified raw34는 source/candidate/geometry pins로 재사용하며 새 context에서 intrinsic 변경범위만 검증한다. 원R4AA 실패/허용오차/D-firewall을 보존한다. 자원·wall·메모리·새native identity는 실제 다음 실행 전에 관측하여 고정한다. 나머지7점/capture/기저확대로 자동 진행하지 않는다.

## 5. 목적함수 오차와 에너지 범위

NR gas rest frame, normalized nonnegative velocity distributions에서 K=integral f_p(v)f_H(w)g sigma_1s(E_CM)d3v d3w, R=n_CR n_HI K. g=|v-w|, E_CM=mu*g^2/2. K[m3/s], R[m^-3/s]. 원G(p)의 measure/Jacobian과 E_lab/E_CM/keV/u의 질량규약을 확인해 변환한다. proper time/tetrad는 source signature의 일부다.

양의 weight에서 R=integral W_s(E)sigma(E)dE. 같은 채널/영역의 source envelope가 있으면 |deltaR|<=integral W_s epsilon_sigma + low/high tail + quadrature bound다. state/kinematics 오차는 별도다. empirical refinement difference는 hard bound가 아니며 여러 오차성격을RSS로 섞어CI를 만들지 않는다. 상대오차에는 인증된 양의 core 하한이 필요하다.

H16 모델 projectile은4–81keV/u, target은10^4K Maxwellian이다. 현재100keV/u,b=2a0 검증은 source continuum도 적분sigma도 아니다. b적분 및 relative-energy support/warm tails를 고려해 소비자 가중 기여가 큰 영역만 후속 계산한다. 50/100/225 등 임의 energy scan을 열지 않는다. H16의1e-8 rate numerical target과1e-12 tail/core는 engineering 목표이지 source의 물리정확도가 아니다. downstream x_e/열 오차배분은 receiver sensitivity 없이는 발명하지 않는다.

## 6. 기존 G01–G13을 어떻게 닫는가

G01 조건부 정리와 G07/G08 conditioning/covariance는 적용조건을 확인해 재사용한다. G02 국소성공과 전역operator domain은 별도다. G03의 경험적R^-2를 연속tail theorem으로 올리지 않는다. G04/G05의 bridge/authentic state transfer, G06/G11의 공동observable error, G12의 실제window는 여전히 필요하다. +/-12 state를 +/-32 state로 옮겨 읽지 않는다.

G09/G10/G13에서1s출력과coupling-basis 수렴은 다르다. 출력이1s라도 누락채널 효과를 bound/수렴검사해야 한다. all-bound총합은 별도 목표로 기존OPEN을 보존한다. 더 약한 목적함수 충분조건은 새CR_REION_1S_V1 계약에 증명하고 과거G 의미를 변경하지 않는다.

## 7. 여기와 NCP의 분업

여기서 필요한 이론·weak residual·error composition·typed source/state/capability 계약, Gram/operator/observable/rate 참조코드, 단위변환, 오류처리, cache/restart/provenance, 변경영역 시험, 실행/반환 계약까지 최대한 구현한다. 제안 파일군은 r4ab_intrinsic_gram/, operator_contract/, selected_source/, provider/{schema,rate,error_budget}.py, adapters/bass_gas_frame.py, ledger/reservoir.py, runtime/contract.py다.

NCP/local Codex는 전달코드의 compiler/ABI/NUMA/affinity/OpenMPI/OpenMP/SIMD 최적화, large b/E/basis/window runs, 실제host replay를 맡는다. 처음부터 재구현하지 않는다. strictFP64/no-fast-math/결정론적 reduction/oversubscription 방지 및 source-input-native identity를 유지한다. 환경변경에 영향받는 범위만 새로 검사하고 old completed suites를 반복하지 않는다. 실제측정 없이64CPU speedup을 주장하지 않는다.

Bianchi 배경은 기존 parent transport가 담당한다. local gas-tetrad source에 임의shear multiplier를 넣지 않는다. Bianchi-I p_i proportional a_i^-1, n proportional1/(a1a2a3), FLRW limit, frame/rotation, first-step/restart, 전체charge/nuclei/electron bookkeeping을 좁게 검사한다. source numerical accuracy와 host splitting error를 구별한다.

## 8. 범위와 종료

범용atomic engine, 전체recombination/HyRec/Ly-alpha, 모든원소/He/분자 확장, H-H/H2+ sibling재개발, 전체background/Einstein 재구현, CMB likelihood, 목적없는energy scan은 새 필수과제에서 제외한다. 다만 재이온화에 필요한 CR momentum/heat/neutral transport를 근거없이0으로 놓지는 않는다. actual receiver sensitivity 또는 relevance bound가 요구하면 그 최소moment/closure만 conditional branch로 연다.

SCOPED_THEORY_CLOSED, PORTABLE_IMPLEMENTATION_READY, SCOPED_PHYSICS_ADMITTED는 독립이다. 필수source/가정이 미확립이면 theory CLOSED가 아니고 실제host수락 없이는 physics completion이 아니다. model/evaluated/strict profile과 기존strict gate를 보존한다. 각단계는 실제 유도/코드/좁은검증/결정을 산출하고 메타감사를 반복하지 않는다.

근거: R4AA report/DBv13/current source; Library WU088_HOST4_H16_RESEARCH_PLAN_20260922_v1.md; H_ATOMIC_REVISED_RESEARCH_PLAN_20260929.md의 role firewall. 외부 primary abstract arXiv:1907.08234v2, DOI10.1103/PhysRevA.58.2872는 state-resolved observable 구분만 뒷받침하며 이candidate의 certificate가 아니다. 상세 출처/hash/검산/제한은 양쪽 cloud의 설계ZIP에 있다.
