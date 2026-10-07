# CR-F0-R3: FLRW 시계·방출·redshift와 기존 IGM source-step 연결

2026-10-07. Status: SCOPED_LOCAL_CURRENT_SOURCE_FLRW_DRIVER_NATIVE_VERIFIED__SOURCE_TIME_ERROR_OPEN.

기존 CR-off point bridge와 source-fed BE를 다시 구현하지 않고, 현재 FlatFlrwBackground::at_ln_a에 연결한 cosmological driver를 구현·실행했다. nH/nHe/H/Tcmb를 같은 stage 시각에서 공급하고, cohort birth와 photon redshift 및 accepted-only 사건/에너지 장부를 연결했다. 새 native FLRW 진단 5개, 고유 Rust 시험 26개, 독립 C 원자율 기반 source-stage 검사를 수행했다. 원격 rei_bianchi의 production code와 기존 F08/S0는 변경하지 않았다. 로컬 current-source library의 실행 성공과 원격 owner adoption ACK는 별개다.

## Identity와 SYNC03 역할

bass_cr intake/prepublication HEAD=6429f8df1356de2aa4f0a39c3545d0712594878b, branch=research/r4q-gap-closure-20261001. 해당 SYNC03가 수신한 이전 R2 완료를 유지했다. Central34765f5cc35169b5e8718571f3c01777cd28aec7의 DAG에서 CR_COSMOLOGICAL_DRIVER는 CR owner에게 예약돼 있으며 이 스레드가 그 작업을 이어갔다. REI IGM long/SPEC/BASS observer 작업을 복제하거나 중앙 CURRENT/DAG를 덮어쓰지 않는다.

Receiver intake=89929b7ad34e6a667a8725580cc4210026587e1c, branch=forward/rust-reion-kernels-20260922. Parent84afbe7660ec79e5e43822e7aea49a0a9ee8daea 이후 변경은 문서뿐이었다. 원 library src tree=cb69b4736dd046e4675557577eb8e0ead037d1f3의 27개 원 파일과 이전 R2 bridge/source-step bytes를 유지했다. igm_background.rs blob=cdce6a9f0a9e9df930f33c8521ee720fd463a780. 원 lib.rs에는 새 driver export만 추가했다. 전체 원 repository checkout/과거 tests/examples를 복원한 것과 구분한다.

Input archive BASS_CR_FASTEST_STEP_20261007_v1.zip:196491bytes,SHA256=f3156ba8e07d4cfe263cb793c424a66958fa9730cbe9c1779c96007e10a11434. 실제 archive SHA/CRC 및 선택 payload identity를 확인했다. 원자식은 Grackle-based IGM이며 FT03의 Q2/C3/finite-shear certificate를 이 모형에 이전하지 않았다.

게시 직전 receiver=4dae4a26a5e15b2289b46668f546f0acd2a23417로 전진했다. Intake 이후 두 commit의 변경은 SYNC03 영수증 및 별도 FT-SPEC-BRIDGE03-FRONTIER 문서/연구 helper 추가이며 원 library source 변경은 없다. 해당 README blob7556e685f26a19ee13fca8755c9db3cf8a5b9409를 읽어 별도 FT03 frontier 결과를 수신했지만 이미 봉인한 IGM 입력이나 수치 reference로 가져오지 않았다. Late ACK는 detached receipt와 이 문서에 기록한다.

새 실행 source:
- crate/src/igm_cosmological_driver.rs SHA256=3e2c7a36fba001c62198d4b3cd2a1f4c934e29e86589bfaa41a8bd0f66a7deb7
- crate/tests/igm_cosmological_driver.rs SHA256=68fa02f6f86fe63aa081f4eb4136cc3164736b9b93c381ad26348c4199645eb5
- crate/examples/cr_flrw_history.rs SHA256=789b307d508ffb84c758b32162d57d6925acf8ad362416155506325b8b4aa628

## 시계와 source measure

ell=ln(a)는 a=1 today인 절대 scale-factor 좌표다. 원 background는 proper-time inverse를 제공하지 않으므로 ell을 초로 넘기지 않고

    dt = integral_[ell0,ell1] d ell / H(ell)

를 GL8로 계산한다. GL4와의 차이는 진단이며 엄밀한 quadrature 상계가 아니다. 같은 midpoint ell에서 proper nH/nHe/H/Tcmb를 평가하고 기존 source-step에 proper dt를 한 번만 전달한다.

Cohort(id,birth_ell,E_birth,p)의 energy는 E(ell)=E_birth*exp(birth_ell-ell), p는 photons/H다. 기하 이동은 p를 희석하지 않는다. Passive below-fit photons도 그대로 보존하며 reprojection/압축은 없다. Source는 명시적인 유한 birth 목록이고 경계에서 한 번만 추가한다. 이번 driver에서는 각 reaction leg의 기존 source-rate 배열을0으로 주어 중복 주입을 피한다. R2의 source-fed API를 삭제하거나 변경한 것은 아니다.

예제의4 birth는 ell bins의 중점이고 각 광자수는 S*해당 bin의 proper duration으로 정했다. 동일 목록을 모든 시간세분화에서 유지한다. 이는 연속 방출률의 유한 quadrature이고 exact continuous source가 아니다. Duplicate ID, 잘못된 순서/에너지/수와 유한 실행예산 초과는 거절한다. Birth list를 조용히 정렬하거나 missing input을0으로 채우지 않는다.

## Stage와 conservation

각 leg는 G-half / 기존 BE / G-half다. Source에는 중간 에너지·밀도·H·Tcmb가 들어간다. Gas expansion work2H*w는 원 BE에서만 계산하고 geometry가 w를 다시 스케일하지 않는다. Reaction이 BE이므로 배치가 대칭이라는 이유로2차라고 부르지 않는다.

    Wrad = eV_erg*sum[(E0-Emid)*p0+(Emid-E1)*p1].

뒤 기하 단계에는 흡수 후 살아남은 p1을 사용한다. Counts/events는 perH, ledger energy는erg/H다. Frame은 gas rest, density는proper이며 c/kB/eV 및 원 background의 G/mp 상수는 보존한다. 전체 장부는

    Delta(w+binding_perH+photon_energy_perH)
      +escape+gas_work+rad_work-CMB_to_gas-birth_energy=0
    Delta(electrons_perH+photons_perH)-birth_count-CI+RR+DR=0.

Escape는 방출시점의 누적 에너지이지 observer까지 redshift된 외부 radiation reservoir가 아니다. CMB는 gas 유입을 양으로 한 signed 항이다. 장부 clipping/사후보정은 없다.

Full과two-half는 같은 외부끝점과 birth 목록을 사용하지만 각 half의 background를 따로 평가한다. 수락된 두 half만 state/ledger에 넣고 discarded full을 제외한다. 일부 Newton/domain failure와 accuracy rejection은 유한예산 안에서 step을 줄이고, invalid source/clock/CR-on은 거절한다. 입력은 immutable이다. 원 canonical interval gate를 이 state-difference estimator로 대체하지 않는다.

Fit cutoff13.60/24.59/54.42의 crossing clock을 추가 경계로 사용하며 physical binding과 구별한다. Crossing 시각과 energy는 f64 구현이며 interval event-time certificate는 없다. Checkpoint/restart와 장시간 source convergence도 이번 범위 밖이다.

## 실제 실패와 repair

첫 native 호출은 방출 경계 직전1ulp=4.440892098500626e-16 ln(a) 구간이 남아 full/two-half의 기하 중점을 표현하지 못해 IGM_COSMO_CLOCK_RESOLUTION으로 중단됐다. 동일 입력을 assertion RED로 재현했고 원 코드와 두 실패 출력은 보존했다.

새 partition은 hard boundary를 먼저 정하고, 뒤에 두 번 이등분할 수 없는 꼬리를 남길 경우 직전 trial 끝을 바로 그 boundary로 잡는다. 늘어난 전체 duration을 실제로 적분하므로 시간을 건너뛰거나 gas/photon을 project한 것이 아니다. Nominal max step와 작은 rounding 차이는 명시한다. 직접 지정한 unsplittable 전체 구간은 여전히 거절한다. 수정에 원자율/허용오차 변경은 없다.

## 새 native FLRW 결과

Manufactured mixed background: H0=2.2e-18/s,Omega_r=9e-5,Omega_m=.3,Omega_b=.049,Omega_Lambda=1-.3-9e-5,YHe=.24,Tcmb0=2.7255K. 원 background의 핵질량 근사를 유지한다. 관측 best fit이 아니다. 초기ell=-ln11(z=10), 끝ell=초기+2e-5, proper duration≈4.53805465254713e11s, 끝z≈9.999780002199985.

Gas initial fractions(.9,.3,.05),T1e4K,.05photons/H at13.7eV, S=5e-15/H/s의 finite4birth를 사용한다. 총 emitted count=.00226902732627356444/H, emitted energy=4.98047411276630877e-14erg/H. Threshold 진단만 초기 photon을13.6001eV로 바꾼다.

|profile|accepted macro|rejected trial|끝xHII|끝T[K]|
|---|---:|---:|---:|---:|
|FLRW8|13|1|.9402067999750664|9817.895360399549|
|FLRW16|16|0|.9403413004054514|9817.302881635187|
|FLRW32|32|0|.9405617073246039|9816.332348848591|
|FLRW64|64|0|.9406731030627734|9815.841911998188|
|THRESHOLD16|17|0|.9255434431268840|9873.673562925065|

16/32/64의 연속 온도차 비=1.9789148914855237. 같은 finite source measure의1차 수렴과 일관된 제한 진단이며 실제 continuous-source/global error 상계는 아니다. FLRW8은 실제13macro로 adaptive 실행돼 8/16/32 고정격자 비에 넣지 않는다.

Final5 profiles=142accepted macros+1rejected trial,284accepted halves,429complete BE solves다. Max global number residual=1.5459300086316396e-15/H, absolute energy residual=3.6741985521573846e-26erg/H, normalized energy residual=3.688603202191193e-13이다. 장부가 작다는 사실과 시간정확도는 별개다.

Example INPUT.json의 nominal_refinements 필드는 개발 초기[8,16,32]를 기록하며 추가 FLRW64는 실행 loop와 profile/attempt/stage CSV에 있다. 원 INPUT을 뒤늦게 덮어쓰지 않고 INPUT_SCOPE_NOTE.json에 이 metadata-list omission과 실제5profile identity를 명시했다. 이는 수치시험 실패가 아니다. 최종 정본은 results/native_final이다.

## CR 및 관측량 반환

5profile 모두 이 driver 경계의 deferred CR load/callback=0이다. 실제 photo AtomicProvider와 IGM rate는 호출했다. Witness는 실제 CR 원자 provider가 아니며, 외부 eager loading/기존 history/global production counters와 owner remote adoption ACK는null이다. CR-on은 MissingAuthority이며 zero-fill physics가 아니다.

results/native_final/ne_endpoints.csv는289행(초기5+accepted-half끝점284)이다. Properne를 같은 background density/분율로 재구성했고 elapsed clock은 최초ell 이후 normal seconds다. Absolute age inverse가 아니며 observer tail은null이다. Optical depth/visibility를 이 스레드에서 새로 계산하지 않았다. OBSERVABLE_EXPORT_CONTRACT.json이 hash/clock/unit/finite-source범위를 고정해 SYNC03 독립 consumer에 넘긴다. 기존 BASS build나112000cell 관측량 실행을 반복하지 않았다.

## 실제 검증과 실행 횟수

새 distinct Rust26tests PASS:2assertion RED→GREEN(시계 초변환,1ulp partition),24tests-after. 이전 bridge/source-step23+23,old166suite,FT03/S0/BASS campaign은 재실행하지 않았다.

원 Grackle14개 C함수/headers/license를 그대로 사용한 독립 wrapper와 Python으로 모든284accepted stage를 대조했다. 선택9BE roots는 old state 초기추정에서 SciPy hybr로 풀었다. Native endpoint를 initial guess 또는 정답으로 주입하지 않았다.

- clock quadrature42 checks,maxrelative5.379884786968268e-16
- background1136 checks,maxrelative6.340283467604604e-16
- energy mapping2526 checks,maxrelative1.3061612538821864e-16
- independent C scalar checks4534, native BE residual max7.424616477180734e-16,event relative max5.921451861728117e-16
- independent9root max normalized state difference6.661338147750939e-16
- same birth lists 및289개 ne row 확인.

이 검사는 같은 이산 source map과 새 clock/geometry 구현에 대한 대조이며 interval-IVP/물리율 정확성 증명이 아니다. Mpmath65자리는 검산 정밀도다. 실제 scipy1.17.0,numpy2.3.5,mpmath1.3.0을 사용했다.

첨부 prefix에서 rustc1.94.1(e408947bf),cargo1.94.1(29ea6fb6a)을 복구해 실행했다. 배포서명 authenticity는 새로 검증하지 않았다. 최종 test/fmt/Python syntax3명령 exit0. Clippy exit0이나 새 GL literal excessive_precision2개 및 기존경고가 남아 warning-free는 아니다. Blanket suppression이나 숫자변경은 없다. VERIFICATION.json에 tested hashes/명령/exit를 보존했다.

개발4완료profiles+추가64profile과 최종5profiles로 이 turn의 정상완료 profile실행은10개, complete BE858개다. 최종5개와 개발 출력의 과학적CSV행이 모두 같음을 확인해 독립9root를 재실행하지 않았다. Unit의 추가 호출은별도다. 두 실패한 native example의 내부완료BE수는 계측하지 않아null이다. 10개를 독립 물리시나리오10개라고 부르지 않는다.

새 continuous IVP/global certificate/precision atomic/receiver remote mutation은0이다. 실제 새 cosmological native history5개와 독립BE9root는 실행했다. 독립human/agent review나proof assistant는 없다.

## 재현·패치·백업

receiver_cosmological_delta.patch는 원 source identity를 확인하고 같은 기존 R2를 보존하면서 driver/test/example/export만 추가한다. 별도 localcopy에 dry-run/apply하고3파일 bytes가 시험코드와 같은지 확인했다. 원격 rei_bianchi에는 적용하지 않았다.

Git launcher: research/fastest_rejoin_20261007/cosmological_driver/RUN_FROM_ARCHIVE.py. SHA256=74f271f37f003d8bc60e7c4f843c37720af490ed69f7ac24c7cc5e6c8266e3cc. Launcher syntax,실제archive verify-only, 같은크기 damaged archive 거절을 확인했다. 내부 reproduce.py verify-only도 실행했다. 전체wrapper의 dispatch를 별도새폴더에서 또실행하지 않았으며 실제구성 test/native/checker 명령의 실행과 구별한다.

Sealed archive: BASS_CR_FASTEST_COSMO_20261007_v1.zip
bytes=777922,211entries/210payload.
SHA256=2624ce1d5a441eda411b819708c39cb67d1280775ee4a590924520bac00e5002.
Local CRC/payload size/SHA와 tested source hashes 일치. 실제Rust source전체·test·patch·input·CSV·독립검사·실패로그·REPORT는ZIP에 있고Git에는launcher/summary/별도SYNC03 return을 게시한다.

Drive upload success 및metadata readback: id1pNjab2YNvbqQlS-yRCAcGWmYv1Z4XPDe,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ,name/size777922일치.
Dropbox completed: id:BSpOijBcT10AAAAAADzuZg,size777922,modified2026-10-07T12:14:55Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_FASTEST_COSMO_20261007_v1.zip.

동일immutableZIP의create-only이중백업이다. R1 UPLOAD_VERIFIED이며remotechecksum미노출,새ZIPfullrestore/independentremotebytehash미수행이다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 실제Git commit/tree와late delta ACK는 봉인ZIP밖 detached DELIVERY_RECEIPT에 기록한다. Provider sharing 권한은 바꾸지 않았다.

## 다음 최소 작업

이번 local cosmological driver 실행단위는 종료한다. 다음은 실제owner pipeline의opt-in 채택/반환 또는 같은source를유지한 시간오차와 같은time을유지한 source오차의 분리다. 새 generic stepper/old theory를 또작성하지 않는다. Observer consumer는export계약에맞는유한ne자료를독립적으로읽고physicalcold-Thomson validity와tail을따로정의한다. Globalcontinuousaccuracy,sourcequadrature,checkpoint/restart,BIangles 및physicalfit은이번완료범위가아니다.

CR_OFF_FASTEST,precisionatomicPARKED,physicalproductionHOLD,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,capture=false 유지. Source ON/FullK/318patch/소비된정밀원자승인을재사용하지않는다. FT03theory성공을IGM물리승격에사용하지않으며원격productionglobalcounter/ownerimportACK는null이다.
