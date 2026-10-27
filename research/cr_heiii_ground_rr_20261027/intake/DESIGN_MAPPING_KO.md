# HeIII → HeII ground RR: 입력–식–코드 대응 초안

## 범위와 현재 상태

부모가 선택한 consumer A의 R9/C2 설계 지원이다. 새 unit의 implementation 편집이나 과학 실행 권한은 받지 않았다. 실제로 읽은 정책은 current `bass_cr/AGENTS.md`, PhysMath 1.3.0의 THEORY R9와 CODING C2/C5 정의 및 POLICY_INTEGRATION이다. `research/cr-heiii-ground-rr-20261027`의 관찰 local HEAD는 `b11b2e9255f2b10fb5582376412e045bd1e9151c`였다. 저장 배열의 ZIP/NPY header만 읽었고 coefficient table point, solver, 예전 controls를 실행하지 않았다. 원자료 row는 텍스트로 읽었다. 모든 새 R/C 완료·admission은 root 기록을 따른다.

## 실제 재사용 입력

기존 unit `research/cr_he4_ground_rr_20261025/` 아래:

- `inputs/reused/pr104/{case}.npz`: E grid, offdiagonals, first6/bath6 RHS, 각 z의 source projection 및 active mask.
- `inputs/reused/pr105/{case}.npz`: 원 H1 hazard/column 및 계보 identity. 새 consumer에 필요한 H1 hazard와 column은 아래 HeI 결과에도 저장되어 있으므로 반복 solve는 불필요하다.
- `runs/cr_he4_rr_primary_20261025_v1/{case}.npz`: exact stored HeI baseline `K_diag`, `K_lower`, `K_upper`, `lambda_H1`, `lambda_He`, `rhs_physical16`, `p_H1`, `p_He`, `u_s`, `u_p`, `t`.
- `inputs/reused/c23d/ATOMS_{2.316,2.479,2.649}.csv`: 각 384개 원 pulse atoms. 재투영하지 않는다.
- `inputs/reused/c23b/spectral_photo_source.py`: SHA256 `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`.
- `inputs/reused/c23b/data/verner_photo.dat`: SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`.

현재 public code는 `Verner96.from_table('HeII', data_dir)`를 지원한다. HeII row는 Z=2,N=1 및 `(I,Emax,E0,sigma0,ya,P,yw,y0,y1)=(54.42,50000,1.720,13690,32.88,2.963,0,0,0)`이다. `from_table`는 표 전체 hash와 row tuple을 검증한다. `sigma_cm2(Egamma)` point 호출만 사용하면 PW19 spectrum, 원자 source quadrature 및 thermal quadrature 경로는 호출되지 않는다.

nominal N은 배열 길이가 아니다. 예를 들어 `chi1.5_R80_N2048`의 E grid 길이는 2480이고 active operator 길이는 2479다. 실제 24개 입력 NPZ의 모든 array name/shape/dtype는 `INPUT_ARRAY_HEADERS.json`에 있다. 구현은 `len(K_diag)`를 사용한다.

## 연산자와 28 RHS 대응

`K0 = stored HeI K_diag/K_lower/K_upper`가 exact numerical baseline이다. 새 intended operator는 `K1 = K0 + diag(lambda_new)`이며, H1·HeI killed generator를 다시 만들지 않는다. 새 capture target은 He4III이고 density는 0.01 cm^-3다. bound HeII ground electronic g=2, bare ion electronic g=1이므로 d=2g_ion/g_bound=1이다. `lambda_new=n_HeIII v sigma_RR`이며 electron bath density 0.14 cm^-3를 대입하지 않는다.

| Physical18 column | RHS | 의미 |
|---|---|---|
| 0,1 | 기존 first6의 첫 두 열 | CE_s, CE_p probability |
| 2 | 기존 first6 column 2 | cutoff first entry |
| 3 | 기존 first6 column 3 | mean first stop time |
| 4,5 | 기존 first6 column 4,5 | CE incident kinetic moments |
| 6,7 | HeI baseline의 rhs_physical16[:,6:8] | H1 count/kinetic reward |
| 8,9 | HeI baseline의 rhs_physical16[:,8:10] | HeI capture count/kinetic reward |
| 10,11 | lambda_new, lambda_new*E | 새 HeII bound-state capture count/kinetic reward |
| 12:18 | 기존 rhs_bath6 또는 HeI rhs_physical16[:,10:16] | six signed bath rewards |

권장 구성은 `first10 = oldHeI['rhs_physical16'][:,:10]`, `bath6 = oldHeI['rhs_physical16'][:,10:16]`를 그대로 복사하고 새 두 열을 끼우는 것이다. PR104 first6/bath6와 동일하다는 read-only identity 비교를 새 소비자에 포함한다. 새 source를 만들거나 옛 rate를 다시 계산할 필요가 없다.

- conditional5: 새 physical solution의 columns `[0,1,6,8,10]`를 RHS로 `K1`에 다시 적용한다. `v_j/p_j`가 각 event의 conditional first-stop time이다.
- stable response4: `-lambda_new * [oldHeI.u_s+oldHeI.u_p, oldHeI.t, oldHeI.p_H1, oldHeI.p_He]`에 `K1^-1`를 적용한다. 모든 old vector는 PR105가 아니라 바로 이전 HeI baseline의 것이다.
- w1: `K0^-1 lambda_new`. 옛 operator를 사용하는 새 RHS이므로 old science replay가 아니다.

따라서 각 case 18+5+4+1=28 RHS, 8 cases 224 RHS다. physical/conditional 184, response/diagnostic 40으로 보고할 수 있다. 두 finest case 독립 검산은 56 RHS다. 새로 추가되는 hazard는 하나이므로 `w/(1+max(w)) <= p_new <= w`라는 single-added-channel bound가 적용된다. 세 개 RR 채널을 각각 독립 문제로 풀어 합치면 동일 trajectory competition이 깨진다.

## 업데이트된 보존식

각 active node의 probability partition은

`p_entry+p_CE_s+p_CE_p+p_H1+p_HeI+p_HeII = 1`.

새 HeIII capture 1회의 number column은 `He4III:-1, He4II:+1, e:fast:-1, photon:+1`다. native REC21 indices는 12→11이다. ion nuclear count와 charge는 보존된다. thermal electron count는 이 사건에서 변하지 않는다. 총 charge-derived free electron 감소와 nonthermal subset 감소가 각각 1이므로 최신 REI의 `xe_th=q.Y-zeta` 및 `chi_th=(1+q).Y-zeta`와 정합한다.

새 event의 signed energy는 `fast=-E`, `binding=-54.42`, `retained_photon=E+54.42` eV이고 thermal/recoil/escaped/external은 선택한 모델에서 0이다. source-averaged count p와 kinetic reward r에 대해 `photon=r+54.42p`, `internal=-54.42p`를 사용한다. 이 두 항의 합 r을 final energy account에 넣으면 electron removal −r을 또 final reservoir로 합산하지 않는다.

final total account에는 기존 bath6, entry, CE outgoing/internal, H1 photon/internal, HeI photon/internal, **새 HeII photon/internal**, 그리고 처음부터 inactive였던 atom energy가 포함된다. 기존 sum16용 bath slice10:16은 새 sum18에서12:18로 이동한다. 이것을 그대로 두는 것이 가장 직접적인 indexing 위험이다. old baseline RR photon/internal rewards를 그대로 붙이지 말고 새 shared solution에서 recompute해야 한다.

## 중요한 인터페이스 단위 경계

기존 `cr_external_interfaces_20261025/contracts.py`의 `Event.extent_m3_s`와 `EventBook.energy_rates()`는 사건율을 뜻한다. 이번 source-average의 `expected_*_events_cm3`는 한 pulse가 종료될 때까지의 **적분 사건수**다. 이것을 event rate 필드에 넣거나 1초 exposure를 암묵적으로 지정하면 단위가 바뀐다.

새 export는 (a) source-qualified per-event template과 (b) integrated count m^-3 및 integrated signed energy J m^-3로 구성하는 것이 맞다. 선택한 노출시간이나 실제 clock history가 없으므로 rate와 exposure는 null/NOT_SUPPLIED로 둔다. per-event stoichiometry, isotope mapping, energy ownership, native row12→11 및 중복 event ID 검증은 그 자체로 수행할 수 있다. integrated return을 현재 rate-only Event API에 강제로 넣을 필요가 없다. source moment만으로 emission spectrum이나 instantaneous source rate를 복원하지 않는다.

## 독립 Decimal70 설계

독립 reference는 `Decimal.from_float(stored_HeI_K_diag)+Decimal.from_float(lambda_new)`를 사용한다. `Decimal.from_float(rounded_new_K_diag)`를 기준으로 삼으면 diagonal-addition loss 검사가 사라진다. old HeI의 과거 intended-vs-rounded 차이는 이미 끝난 근거로 유지하며 이번 baseline을 원래 PR104+H1+HeI의 실수 합으로 몰래 재정의하지 않는다.

18 physical RHS 중 immutable old RHS는 저장된 binary64 값 그대로 reference operand로 사용한다. 새 `lambda_new*E` 및 stable response 곱은 exact decimal products로 독립 검산할 수 있다. conditional RHS는 독립으로 푼 reference probabilities에서 구성한다. H1/HeI 계수 자체의 근거는 재사용하고, 새 HeII 계수만 독립 native row 계산으로 확인한다. 모든 28 solution column을 자기 infinity norm으로 정규화하여 작은 capture 효과가 큰 time/bath 열의 scale에 묻히지 않게 한다.

물리/수치 acceptance는 root의 frozen contract가 정한다. 기존 참고 기준은 linear2e-12, partition/total-energy2e-8, event-energy5e-13, own-column5e-10, ordinarygrid.005/upper-domain1e-5, pairedgrid.01이다. 변경을 요구하는 새 관찰은 현재 없다. grid/domain comparison은 아직 실행하지 않았다.

## C5 최소 구현 표면 제안

새 unit에 engine/primary/changed-controls, config/input manifest, independent reference, saved-only report/plot을 두되 기존 unit 파일은 수정하지 않는다. engine은 새HeII coefficient, exact stored baseline consume, three-channel source average, integrated event export를 담당한다. dispatcher는 새 unit 예산과 command/source identity를 받아 실행하며 old budget을 이전하지 않는다. 실행 실패나 diagonal addition loss를 숨기지 않는다.

변경된 위험을 직접 구별하는 controls는 HeII row/d1/nHeIII.01/지원범위, electron density 오사용, 3RR shared competition analytic control, 네 stable-response sign, first18/conditional5 indexing, photon/binding sign, native12→11와fastpool, integrated-count/rate 구별, source/zero-target domain이다. 기존 HeI31 controls 전체를 복제 실행할 이유는 없다. node·source·run ID·scope가 다른 새 unit으로 기록하고 원 H1/HeI solver 및 source projection·quadrature 재실행 횟수는0으로 유지한다.

이 문서는 계산 결과나 C6/C9 PASS가 아니다. root가 입력·예산·오차 기준을 동결한 뒤에만 point coefficients, 새 solver 및 실제 검증을 실행한다.
