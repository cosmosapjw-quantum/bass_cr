# 다음 CR 유한 사건 consumer — 구현 intake

## 결론과 현재 상태

실제 이름과 revision이 고정된 consumer 코드를 읽은 결과, 가장 작은 유용한 후속 작업은 **선택된 low-birth source의 H/He 기원 전자 수를 새로 분리하고, 저장된 유한 RR·cutoff 응답을 새로운 100 K 조건부 native25 유한 사건 adapter에 연결하는 것**이다. theory/source 대조에서 Rudd helium SDCS가 inclusive electron yield이며 low selection이 electron-marginal임이 확인됐다. 이중 이온화 한 사건의 두 전자 중 하나만 low selection에 속할 수 있다. 식별된 H 부모와 **unresolved partner를 갖는 affine He coefficient ledger**를 반환하고, 실제 He branch/partner point와 전체 부모 native25는 null로 둔다. 기존 RR 전파, source spectrum, 원래 full source 해를 재실행할 필요는 없다. 새 adapter의 계산과 독립 검증은 별도 R1/C4 계약이 동결된 뒤 수행해야 한다.

이 문서는 read-only source/계약 조사와 prospective 설계다. 새 과학 실행, import, compile, source 재계산, 테스트 실행, Git 변경, 원격 게시와 backup GET은 수행하지 않았다. R/C 단계를 완료로 표시하지 않는다. 작성 파일은 next_intake_20261028/consumer 아래에만 있다. metadata 파일 읽기·해시·정확한 원문 저장은 과학 실행과 구분한다.

정책과 인계의 실제 pin은 다음과 같다.

- bass_cr local HEAD: 616b166fa0108ca35defece3f8c9d99fc79895cb.
- AGENTS SHA256: bf1b921550473363df97f75bbbfc2e839120990f89a330b35da66867695f17b5.
- 최종 PR110 handoff SHA256: 4b1d3c0276e62a839cd4143976b02ee038677b578f34e008e371dcbc5c16e13c.
- NEXT_UNIT_CONTRACT SHA256: 0c1cc839b832e83351b5a984642d905f67af0a5581b7457ac94bc21a117abe42.
- PR110 S=2eed7ef835c55ee17e4ce96e0eda7fe8d82dc47c, D=616b166fa0108ca35defece3f8c9d99fc79895cb, M=42cc3a909688d670200ba09c500e2ca83a94fa10.
- physmath 1.0 SKILL.md와 THEORY_LOOP, CODING_LOOP, RESEARCH_POLICY, EVIDENCE_AND_HANDOFF, RUNTIME_AND_LEGACY를 읽었다. 현행 루프의 identity/scope 재사용, 변경 의존성만 계산, 실패 종류 보존을 따른다.

## 실제 consumer 세 종류의 차이

| 실제 코드 | 읽은 identity | 실제로 제공하는 계약 | 이번 source에 대한 한계 |
|---|---|---|---|
| axisym_cr_deposition.rs::cr_deposition_derivative | rei_bianchi@17f8d0daa72e0f76a49cde01b110f650a6688c42; blob64613c6d0cb58406fb8d4d2b1bbfe56c8aad0a05 | 특정 t=1e10 s의 source-pinned FS10 instantaneous terminal packet. H/He ionization, 열, 내부에너지, escape, 외부입력 power. | q=tA finite history API가 아니다. 모든 전자가 thermal이라는 13종 proper-density 상태를 사용한다. |
| cr_integrated_return_20261027/implementation/integrated_return.py | rei_bianchi@d91de6299e614520949c5873a9378000ceb1f85c; blobde5626b0499320cd85e9f24c1d81216fe145285d | 명시적 양의 b가 있으면 integrated event를 native25와 별도 retained-photon port로 사상. event에 1/H를 곱하지 않음. state_update=false. | 기존 HeIII, 10000 K source 범위. 일반적인 같은 상태 검증이나 이번 100 K 부모 source를 제공하지 않는다. |
| thermal_assimilation_20261027/implementation/thermal_join.py | 같은 d91 revision; blobac40275661bfb46fa2b38c2c491c2104d87f4296 | Y[21], ζ, w_nt, signed w_ext, logT. g=q·Y−ζ, χ=(1+q)·Y−ζ. | 저장된 PW19 node, 별도 photo/Planck/Mao RR·DR/constant-nu 완화 모형. 이번 source에 이를 실행하면 다른 물리를 가져온다. |
| bass_atomic_storage_consumer_20261027/implementation/atomic_storage.py | rei_bianchi@835707bb00ef8f778f24f667f102a412ae8ce0ca; blobee8afb928445e5c32abb2e1477fcfa1cd618f417 | 원문 decimal을 Fraction으로 보존한 유한 BASS 원자 재고·에너지 표현. target ion binding와 hidden atomic storage를 분리. | 실제 recipient nb와 native25는 null. 이 BASS continuum transaction의 fast ζ=0을 CR fast cohort에 가져올 수 없다. |

첫 consumer branch research/accel02-native-broad-20261011은 root의 2026-10-27 public ref 조사에서도 17f8d0…로 유지돼 있다. 네 번째 consumer가 새로 관찰된 후속 코드다. 이 범위의 조사는 모든 공개·비공개 consumer의 부재를 입증하지 않는다.

### 100 K의 동일성은 온도 숫자만으로 정하지 않는다

old Rust validate_state는 nH를 **전체 H 핵 밀도**로 해석한다. nHI=nH(1−xi), nHII=nH xi이며 He도 같다. nH=140 m^-3, nHe=11.542553191489361 m^-3, xi=.01, T=100 K는 PR110에서 새로 선언한 conditional total-nuclei inventory와 이 의미에서 대응한다.

그러나 Rust state에는 fast electron 수가 없다. thermal_particle_density_all_thermal_m3는 모든 ion charge에서 나온 자유전자를 thermal로 센다. PR110의 살아 있는 비열적 전자나 arbitrary cutoff를 이 API에 바로 넣는 것은 같은 상태 연결이 아니다. t=1e10 s도 source exposure가 아니라 정확한 packet snapshot clock이다.

PR110 nb=8750/47 m^-3는 explicit conditional H1/He4 inventory에서 정의된 값이다. 이전 PR109의 nb=null을 소급해서 채우지 않는다. Rudd source의 nH 인자가 실제 중성 target 수인지 전체 핵 밀도인지도 부모 source 계수에서 별도로 대조해야 한다. consumer와 숫자가 같은 것만으로 source target normalization을 같다고 하지 않는다.

## native25 코드에서 확인한 에너지와 재고 의미

native_identity/atomic_model.json의 species_order는 n,H1I,H1II,DI,DII,TI,TII,He3I,He3II,He3III,He4I,He4II,He4III,Li6I,Li6II,Li6III,Li6IV,Li7I,Li7II,Li7III,Li7IV다. native atomic_network.py가 이 순서에 A와 q를 선언한다. 이 모델의 자체 pilot abundance, isotope electronic-equality policy, UV field는 이번 새 inventory로 수입하지 않는다.

| 좌표 | 새 adapter가 연결할 의미 |
|---|---|
| 1,2 | H1I,H1II per-baryon number |
| 10,11 | He4I,He4II per-baryon number |
| 21 | fast electron 수 ζ |
| 22 | 비열적 전자 운동에너지 w_nt, J per baryon |
| 23 | signed external reservoir w_ext; native rate 코드에서 absorbed input은 음수, escape는 양수 |
| 24 | log(T/K); integrated event에 clock factor를 추가하지 않음 |

native binding 기준은 atomic_coefficients.json의 threshold에서 조립된다. H는 13.6 eV, HeI는24.59 eV다. 원 source Rudd H의13.605693122994 eV와 PR110 RR H의13.60 eV 차이는 식이나 scalar 변환 중 지우면 안 된다. 새 BASS storage consumer는 target ion-storage에 들어가지 않는 atomic difference를 별도 hidden-energy port로 보존하는 실제 선례다. 이 sidecar는 heat도 w_ext도 아니다.

## 최소 새 구현 계약 제안

가칭 consume_selected_low_birth_window는 production 모듈을 재실행하지 않고 다음 입력을 읽는다.

1. 실제 PR110 RESULT/ARRAYS와 source input의 byte/SHA, source family와 native birth partition, inventory, frozen-history pin.
2. 새로 확보할 **선택 low source의 target-resolved J_H/N_eHe**와 source-energy convention, 원 coefficient·projection identity. total spectral tag에서 H/He 비율을 발명하지 않는다. N_eHe는 helium에서 나온 전자 수이며 HeI→HeII 사건 수와 자동 동일시하지 않는다.
3. 정확한 same-state donor/recipient inventory, proper frame, fixed proper-volume density convention, [0,T] history, disjoint observation-bin 소유권.
4. root가 명시적으로 채택한 cutoff closure. 기존 결과 자체는 physical thermal closure가 없으므로 기본값을 자동 thermalization으로 두지 않는다.

출력은 baseline_native25와 delta_native25를 분리한 두 부분 표현으로 둔다. source δY는 baseline보다 매우 작아 보통 float 덧셈에서 사라질 수 있으므로 baseline+delta를 단일 authoritative endpoint로 저장하지 않는다. 필요하면 rounded endpoint는 별도 진단으로만 기록한다.

J_H는 해당 관측 구간의 식별된 H 부모 ionization 수, N_eHe는 He 기원 선택 전자 수, C_H/C_He는 저장된 같은 구간의 RR 수라고 하자. s는 선택 전자를 하나 내는 single event, p는 두 전자 중 하나만 선택된 double event, d는 둘 다 선택된 double event로 둔다. 비음수 s,p,d는 s+p+2d=N_eHe를 만족한다. H1II 변화는 J_H−C_H, He4I는 −s−p−d+C_He, He4II는 s−C_He, He4III는 p+d다. 따라서 He charge 변화는 N_eHe+p−C_He이며 추가 partner count p를 포함한다.

native ζ에 선택 전자만 넣고 ion charge를 전부 넣으면 q·Y−ζ가 unresolved partner p를 자동 thermal electron으로 잘못 센다. p의 energy/support/history/pool은 독립 sidecar와 미결 gate로 보존해야 한다. He+ residual excitation도 atomic hidden-storage port가 필요하다. p,d 또는 residual ground-state branch를 실제 데이터 없이0으로 정하지 않는다. p=0의 닫힌 family와 ground residual은 명시적으로 라벨을 붙인 conditional fixture에서만 사용한다. 선택된 충돌에서 projectile proton은 양쪽에 남으므로 이 사건의 Δnb=0이다. 이것은 전체 외부 proton injection 계약을 닫는 주장이 아니다. 새 부모 생성이 기존 frozen RR bath/target hazards를 역으로 바꾸는 feedback도 계산하지 않는다.

cutoff의 기본값은 retained unresolved reservoir다. direct cutoff는 원래 low-source의 E=.1 ghost로의 projection이며, 이를 실제 W<.1 birth로 재해석하지 않는다. cutoff를 새 conditional instant-assimilation closure로 명시적으로 채택하면 **선택 전자 component의** Δn_thermal=N_cut이며 선택 fast increment는 J_H+N_eHe−C_H−C_He−N_cut이다. 이 값을 saved active count change와 비교하되 기존 count residual을 repair하지 않는다. unresolved He partner까지 포함한 전체 thermal/native state activation은 별도 partner/branch closure가 없으면 거절한다. cutoff closure를 채택하지 않으면 해당 caloric endpoint는 null이어야 한다.

새 finite caloric 진단을 채택할 경우 Q_th=Q_C+U_cut, Np0는 명시한 baseline thermal particle 수, c_v=3kB/2로 두고 안정적인 식은

    δT/T0 = [Q_th/(c_v T0) − N_cut] / [Np0 + N_cut]
    δlogT = log1p(δT/T0)

이다. 이는 새 cutoff/EOS 가정 아래의 **선택 component caloric 표현**이다. unresolved partner가 baseline 또는 thermal count에 미치는 영향이 닫히지 않았으면 이것을 전체 실제 endpoint로 활성화하지 않는다. coefficient는 여전히 저장된 frozen100K 응답이며, 변경된 T의 feedback이나 coupled history를 새로 푼 결과가 아니다. theory reviewer는 Q=(3/2)kB[(Np0+Ncut)T1−Np0T0]에서 이 식을 독립적으로 확인했다. 수치 oracle 검증은 아직 실행하지 않았다.

energy ownership은 source kinetic, 부모 atomic cost, capture kinetic, retained photon, Coulomb transfer, cutoff transfer, atomic convention sidecar를 각각 한 번만 가진다. 단일 채널에 shared I_star를 선택하면 후보 sidecar는 (I_source−I_star)J +(I_star−I_RR)C다. helium family의 atomic cost는 s,p,d와 He+ residual excitation으로 따로 구성하며 N_eHe마다 단일 이온화 비용을 곱해 닫지 않는다. partner energy가 없으면 required work도 그 미결 변수를 포함한 coefficient ledger다. Rudd inclusive electron source만으로 실제 projectile loss를 식별했다고 하지 않는다. 기존 native ThermalJoin의 w_ext는 이름은 signed external aggregate지만 구현된 legs는 photo, Compton, RR/DR escape뿐이며 CR donor 계약은 없다. 따라서 새 actual w_ext는0인 scoped projection으로 두고 required_donor_work(s,p,d,partner_energy,hidden_atomic)를 별도 sidecar로 보존하며, actual proton loss/work는 null로 둔다. 제공되지 않은 stopping·recoil·전체 proton source work를 추정하지 않는다.

기존 full_source_native25(global/full9600 의미), 외부 consumer physical activation, 전체 transport/thermal-history completion, worldtube totals, physical global error/completion/budget/currency는 이번 선택 사건 출력과 별개로 null을 유지한다. retained photon은 기존 explicit atoms를 재사용하고 heating·w_ext로 이동하지 않는다.

## 독립 검사 제안 — 현재 미실행

- actual low-birth H+He source split가 retained total source를 원래 허용치 안에서 재구성하는지 검사. 다른 target density·4π·clock·volume factor를 재적용하면 거절한다.
- 순수 H와 He s,p,d family의 baryon/charge/선택 전자/partner 수 및 required energy를 독립 rational oracle로 검사한다. p=0의0/mid/max double 분기와 p>0 사례는 synthetic conditional fixture이며 actual branch/partner-null을 유지한다.
- p>0인데 partner를 누락하면 native thermal count가 p만큼 오염된다는 adversarial control을 둔다. partner energy/history/pool 없이 full state activation을 거절한다.
- zero source, zero RR, cutoff 없음, 완전 cutoff, RR만 존재하는 구간을 별도로 확인한다. 없는 실제 상태를 물리 결과로 부르지 않는다.
- source가 끝난 구간이라고 임의로 zero를 붙이지 않고 known history 밖 query를 거절한다.
- 겹치는 prefix/bin, 같은 physical family의 producer revision alias, 총 source와 low subset의 이중 claim을 거절한다. cumulative prefix는 additive 사건으로 접수하지 않는다.
- 같은100K라도 total-nuclei/neutral-target 정의·nb·frame·isotope·threshold convention 중 하나가 다르면 거절한다.
- tiny δY/δlogT가 ordinary endpoint 합에서 소실되더라도 two-part delta가 보존되는지 검사한다. stable log1p 식은 독립 Fraction 또는 고정밀 one-step oracle와 비교한다.
- atomic convention difference를 heat 또는 외부 work에 잘못 더한 입력을 거절하며, original residual을 clipping/zero repair하지 않는다.
- conditional cutoff closure를 명시하지 않은 입력의 caloric endpoint는 null, physical heating completed는 false다.
- 실제 scoped output에 대해 별도 저자가 source split·species mapping·caloric algebra를 확인한다. 기존 3200-state RR 전파/46개 기존 control/517개 reference의 무변경 부분을 다시 실행하지 않는다.

새 허용치와 exact test 수는 여기서 동결하지 않는다. root R1/C4와 독립 검토가 구체적인 source split 알고리즘을 확인한 뒤 결정한다.

## 실행 wrapper와 새 예산 제안

PR110의 실제 closeout은 charged24.692011/40 CPU s, 순수 측정14.616973, 보수적 tails10.075038000000001이다. 남은15.307989는 이월하지 않는다. C4 자원 거절, controls_v1 oracle 실패, plot_v1 실패와 각 debit은 그대로 남는다.

기존 wrapper가 제공하는 create-only receipt, same-unit preparation manifest, maximum-cumulative debit reconciliation, unknown reservation gate, manifest-before-execution, named allocation, process group/affinity/RLIMIT는 새 unit identity로 옮겨 쓸 수 있다. 다음 두 수정은 과학 코드와 분리해 검토할 가치가 있다.

- 이전 실제 receipt는 descendant monitor가 worker를 관찰했다고 증명하지 못했다. 현재 queue가 /proc/.../children에서만 시작하므로 새 wrapper는 known Popen PID와 start identity를 명시적으로 추적해야 한다. 살아 있는 worker의 proc identity를 읽지 못하면 CPU를0으로 가정하지 않고 owned process만 중단·실패로 기록한다. 이 변경은 아직 실행 검증되지 않았다.
- legacy ledger measured_worker_plus_coordinator_cpu_s는 charged preparation baseline을 포함해 순수 측정값이 아니었다. 새 ledger는 measured preparation, worker, coordinator, reserved tail, conservative charge를 처음부터 별도 필드로 둔다.

prospective 새 envelope는40 CPU s이며 이전40과 독립이다. root는 이 별도 envelope를 R1용으로 잠정 수용했으나 active C4 budget은 아직 없다. 예시 named worker 할당은 preparation3, controls3, primary4, independent6, saved-output plot6으로22다. coordinator 각2와 각 tail.05를 합친 reservation은2.05씩10.25, C4·실패 포함 준비 reserve4를 더하면36.25가 예약되고3.75가 미할당 contingency로 남는다. target-split 실제 비용·worker 구조가 확인되면 root가 동결한다. BUDGET_MANIFEST_TEMPLATE.json은 실행에 사용할 수 없는 초안이다.

one native thread, selected256MiB worker limit, upper512MiB, host reserve1GiB를 prospective 기준으로 제안한다. 새 C4는 당시의 실제 host/cgroup counters를 다시 읽어야 한다. PR110 file-LRU50% credit은 unit-specific non-atomic admission estimate였으며 새 단위에서 자동 보증으로 재사용하지 않는다. RLIMIT와 환경 가시성의 한계도 숨기지 않는다. plot이 필요하면 새 결과에 대한 가벼운 그림만 한 번 만들고, 이전 plot을 다시 계산하지 않는다.

## 남은 입력과 인계

당장 필요한 새 과학 입력은 selected low J_H/N_eHe 및 그 original coefficient projection pin이다. native state order·threshold와 실제 legacy consumer 의미는 이제 원문으로 확인했다. source-parent isotope/state, electron-marginal helium s,p,d family와 actual branch/partner-null, residual excitation, required-work와 actual donor loss의 구분, direct-cutoff projection 의미와 새 conditional thermal-assimilation 선택은 R1에서 명시해야 한다.

Intake 수정 이력: 최초의 HeI→HeII 단일 사건 후보는 inclusive SDCS 원문 대조로 폐기했다. 이어 V1+2V2=N_eHe인 닫힌 selected-family 후보도 한 double event의 partner가 선택 밖에 있을 수 있다는 반례로 실제 해석에서 폐기했다. p=0은 conditional fixture로만 남긴다. 이 수정들은 실행 전이며 기존 PR110 과학 결과·검토·비용을 변경하지 않았다.

새로운 same100K adapter는 실제 이름과 입력 identity를 갖춘 코드로 작성할 수 있으나, foreign REI consumer의 물리 활성화·history 완료를 뜻하지 않는다. central 현재28/88, 이번 CR count effect0과 N4/N5 partial,N6/N7 predecessor gates를 유지한다. 개인 대화 전수 검색 unavailable과 Drive partial inventory는 root의 전체 survey 범위와 함께 보존한다.

각 원문과 로컬 해시는 SOURCE_MANIFEST.json에 기록한다. 다음 행동은 root가 이 최소 범위 및 별도 예산을 동결하고, 새 source split과 finite-event adapter만 구현하는 것이다.

