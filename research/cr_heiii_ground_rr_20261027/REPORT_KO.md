# HeIII ground-state RR 소비자와 보존적 적분 반환: 연구 결과 및 C10 인계

작성일: 2026-10-27 KST. 원 실행·게시 로그의 UTC 표기는 보존했다. 연구 단위: `CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1`. 저장소: `cosmosapjw-quantum/bass_cr`, branch `research/cr-heiii-ground-rr-20261027`.

## 1. 판정과 현재 완료 범위

**He4III + fast electron → He4II(1s) + retained photon의 source-qualified ground RR 소비자와 보존적 적분 반환을 PASS_SCOPED로 채택했다.** 정확히 저장된 이전 HeI 사슬에 새 HeII hazard 하나를 더하고 H1·HeI·HeII의 경쟁을 같은 operator에서 계산했다. 실제 결과는 8 case, 224 RHS, 24 source 행과 24 integrated exports다. 변경 control 36/36, grid/domain 비교 252/252, 두 finest case의 독립 Decimal70 56/56 own-column 비교 및 전체 독립 검사 754/754가 통과했다. 기존 허용치를 완화하지 않았다. [과학 채택 기록](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/ADMISSION.json)

이번 scoped child는 **1/1**이다. 원래 중앙 DAG는 **27/88**이며 원래 node 수에 대한 증가 효과는0이다. N4/N5는 PARTIAL_OPEN, N6/N7은 PREDECESSOR_GATED, L4는 false를 유지한다. 미병합 PR236의 별도 작업 DAG **32/88**는 중앙 승인 수와 구분한다. 전체 물리 완료율·전체 물리 오차 bound·전역 잔여 예산은 null이다.

R1–R10 및 C1–C9의 실제19개 commit/이중 backup receipt에 이어 이 문서는 C10의 최종 산출물이다. Source ZIP의 실제 local·Git·Dropbox·Drive R3 검증은 완료했다. **단계 산출물20/20**, 중앙 **27/88**, scoped child **1/1**을 구분한다. 이 문서를 담는 D의 자기 SHA, 뒤이어 생성할 중앙 M과 마지막 backup ACK는 자기 preimage 밖의 최종 closeout authority와 [PR107](https://github.com/cosmosapjw-quantum/bass_cr/pull/107)에 실제 발생 후 기록한다. 이 문서의 생성 시점에는 중앙 M과 마지막 closeout 전송이 아직 진행 전이다.

## 2. 조사 범위와 복구한 기존 근거

최초 고정 인계서 commit `8d0a5c375589fbddadc2bb90c8117311c80bad09`, 직전 science S `4caf4273eefd51f2c605a8667c3533d8489dd0f5`, document D `b11b2e9255f2b10fb5582376412e045bd1e9151c`를 출발점으로 삼았다. 이전 source ZIP의 SHA256 `7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa`를 실제 복원하여 198 payload의 hash와 CRC를 검사했다. H1 RR, HeI RR, C23E, 저장 source projection 및 bath generator의 성공한 계산을 재사용했으며 이 연구의 old-science replay는0이다. [복원 기록](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/intake/RECOVERY_R3.json)

초기 inventory는 접근 가능한 owner 저장소51개를 pagination 끝까지 확인하고 관련9개 저장소를 상세 대상으로 선정했다. 해당9개에서 **branch 1,378개, open PR903개, closed PR109개**를 목록화했다. 이는 관찰 시점의 목록 완결성과 관련 원문 조사 범위다. 모든 파일과 모든 개인 대화의 전수 독해를 뜻하지 않는다.

| 관련 저장소 | Branch | Open PR | Closed PR |
|---|---:|---:|---:|
| bass_cr | 184 | 105 | 1 |
| rei_bianchi | 278 | 221 | 14 |
| WU088_HH | 159 | 150 | 0 |
| rec_bianchi | 156 | 104 | 34 |
| BASS_HE | 107 | 102 | 0 |
| bass | 277 | 162 | 30 |
| vigilode | 215 | 59 | 30 |
| bianchi_phase_r | 1 | 0 | 0 |
| MOSAIC-ODE | 1 | 0 | 0 |

백업 조사에서는 2026-10-25 이후 최근 문서 목록314개를 두 페이지로 확인했고, 지정 Dropbox 경로의 bass_cr99개 및 rei_bianchi181개 항목은 recursive listing의 끝을 확인했다. Drive의 bass_cr81개와 C22C15개는 반환된 지정 폴더 범위이며, 일반 BASS 폴더100개는 continuation token을 얻을 수 없어 partial inventory로 남겼다. 검색 도구가 알려진 ZIP을 누락하거나 날짜 필터와 다른 결과를 반환한 사례는 부재의 근거로 사용하지 않았다. Personal Context는 실제 호출에서 unavailable였고 완전한 개인 대화 transcript 검색 API가 없었다. 이 접근 한계를 보존한 상태로 필요한 고정 입력과 직접 관련 계약을 복원했다. [조사·한계 기록](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/intake/BACKUP_SURVEY_KO.md)

## 3. 이번 단위에서 구성한 이론

### 3.1 Source와 isotope의 정확한 결속

Verner96 native HeII row `(Z,N)=(2,1)`의 문턱54.42 eV 및 photon 지원범위54.42–50000 eV를 유지했다. 전자 ground-state weight는 bound2, bare ion1이므로 `d=2g_ion/g_bound=1`이다. 표와 point provider는 기존 bytes 그대로 사용했다. SciSpace·Exa의 discovery를 primary 논문·표·식·NIST 상태 자료와 대조하여 ground channel, 통계 weight, 단위를 정리했다. 이 coefficient는 elemental-He 전자 단면적을 He4에 조건부 귀속한 모형이며 isotope-specific 실험 fit을 뜻하지 않는다. [R2 source qualification](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/intake/R2_SOURCE_QUALIFICATION_KO.md)

전자 kinetic energy E>0에서

\[
\sigma_{\rm RR}(E)=\sigma_{\rm PI}(E+I)\frac{(E+I)^2}{d m_ec^2E},\qquad
\lambda(E)=n_{\rm HeIII}v(E)\sigma_{\rm RR}(E).
\]

고정 capturing-ion density는 `n_HeIII=.01 cm^-3`이며 electron bath density `.14 cm^-3`와 구분한다. Fixed bath T=10000 K, stationary heavy target, zero recoil, nonrelativistic scalar, spontaneous ground only, closed box, proper seconds가 채택 범위다. Stimulated/excited/all-level RR, finite-mass/각분포, cascade 및 thermal assimilation은 이 단위의 완료 범위에 포함되지 않는다.

### 3.2 저장 operator와 안정적인 작은 효과

K0는 이전 PR106 HeI 결과에 저장된 binary64 tridiagonal operator 자체를 정확한 수치 피연산자로 정의한다. 새 intended operator는 K1=K0+D, D=diag(λ)이다. Non-singular M-matrix 전제에서 G0=K0⁻¹, G1=K1⁻¹는 양의 resolvent이고

\[
G_0-G_1=G_0DG_1\ge0.
\]

기존 비음성 terminal reward와 mean time은 감소한다. 새 capture probability p=G1λ, w=G0λ, η=max(w)에 대해

\[
\frac{w}{1+\eta}\le p\le w
\]

라는 단일 추가 hazard의 양쪽 bound를 사용한다. 세 RR을 별도 사슬에서 계산한 뒤 합산하지 않고 같은 K1에서 경쟁시킨다.

저장 이전 열을 ĥ0라 할 때 작은 변화는 큰 두 값의 차 대신 `δĥ=−G1D ĥ0`로 계산한다. 이 값은 **stored-column response**다. 이전 residual r0=b−K0ĥ0가 있으면 `h1−ĥ0=G1r0+δĥ`이므로 직접 subtraction과 이상적 이전 해에 대한 차이를 구별한다. 이번 stable4는 CE probability, mean time, H1 capture probability, HeI capture probability다. Conditional energy/time은 비율이어서 이 부등식만으로 비율의 단조성을 주장하지 않는다.

이 연구 단위의 새 구성은 위 관계를 source-qualified HeIII 입력, 실제 저장 행렬·reward 열, 보존적 적분 반환까지 연결하여 실행 가능한 계약으로 만든 점이다. R6 독립 이론 검토의 실제 두 finding인 SI 변환과 physical18 열 매핑을 같은 repair episode에서 수정했다. R7 Wolfram의 유리수·보존식 검산은19/19 PASS다. [최종 THEORY](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/THEORY_KO.md)

### 3.3 적분 사건과 native25 반환

새 사건의 species 변화는 `He4III[12]−1, He4II[11]+1, e:fast−1, photon+1`이다. 에너지 변화는 fast `−E`, binding `−54.42`, retained photon `E+54.42` eV다. Final stopped-energy sum에는 photon+binding의 순변화를 넣고 fast removal을 다시 더하지 않는다. He4 nuclei와 전하가 보존되며 이 사건의 thermal electron/particle count 변화는0이다.

Source 평균은 pulse가 종료될 때까지의 적분 사건수 N[cm⁻³]와 kinetic moment U[eV cm⁻³]를 준다. SI 변환은 각각10⁶ 및10⁶eV_J를 한 번 적용한다. 실제 exports에는 `event_rate_m3_s`, `exposure_s`, `instantaneous_rhs`, `native25`가 null이다. Conditional capture mean time을 exposure로 대입하지 않는다.

동일한 물리 상태의 nb[m⁻³]가 명시적으로 주어질 때만 a=N_SI/nb로 정규화하여 `ΔY11=a, ΔY12=−a, Δζ=−a, Δw_nt=−U_SI/nb, Δw_ext=0, ΔlogT=0`을 반환한다. Retained photon의 count와 energy는 별도 port가 소유한다. 실제24행에 외부 donor nb를 주입하지 않았고, 양의 nb를 명시한 control 한 건에서만 이 사상을 검증했다. 이 결과는 finite coupled abundance update나 physical heating 완료를 의미하지 않는다. [고정 contract](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/FROZEN_CONTRACT.md)

## 4. 실제 수치 결과와 정확도의 범위

χ={1.5,3}, R={40,80}, nominal N={1024,2048}의8 case를 계산했다. 각 case의 physical18+conditional5+stable4+w1이28 RHS이며 총224 RHS다. 저장된 z={2.316,2.479,2.649} source를 재투영하지 않고 각 case에 적용하여24행을 얻었다. 실제 배열 길이는 nominal N과 다르며 독립 검산한 두 finest case는 각각 active node2479개다.

| 검증량 | 실제 최대값/결과 | 고정 기준 |
|---|---:|---:|
| per-RHS scaled backward residual | 1.1263434346961322e−12 | 2e−12 |
| probability partition 잔차 | 8.498068915230306e−11 | 2e−8 |
| total scaled energy 잔차 | 3.7807871838044604e−11 | 2e−8 |
| RR event energy 잔차 | 6.764253985925056e−17 | 5e−13 |
| rare-bound 상대 위반 | 0 | 5e−10 |
| ordinary grid 120개 | 모두 PASS; 1.143893625718921e−4 | .005 |
| stable paired grid 48개 | 모두 PASS; 3.6363433333349046e−5 | .01 |
| upper-domain 84개 | 모두 PASS; 3.806794429081296e−11 | 1e−5 |
| independent own-column 56개 | 모두 PASS; 2.5830073808660873e−11 | 5e−10 |
| independent coefficient 10 points/40 scalar comparisons | 최대2.0021283548882072e−15 | 5e−13 |
| independent 전체 검사 | 754/754 PASS | frozen 개별 기준 |

[C7 요약](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/evidence/C07_SAVED_RESULT_SUMMARY.json), [C8 비교](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/evidence/C08_SAVED_COMPARISONS.json), [C9 독립 수치 요약](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/evidence/C09_SAVED_NUMERIC_SUMMARY.json).

R80/N2048의 대표6행은 다음과 같다. Δt는 stored-column mean-time 변화다.

| χ | z | 새 capture probability/active electron | 조건부 photon energy eV | Δt ms |
|---:|---:|---:|---:|---:|
| 1.5 | 2.316 | 7.3331666831e−10 | 58.56486539 | −0.2189426903 |
| 1.5 | 2.479 | 7.3277474445e−10 | 58.56056627 | −0.2184083500 |
| 1.5 | 2.649 | 7.3263203605e−10 | 58.55645498 | −0.2180042159 |
| 3 | 2.316 | 6.0357558048e−10 | 59.79763216 | −0.1843609694 |
| 3 | 2.479 | 6.0190501479e−10 | 59.79250590 | −0.1834709926 |
| 3 | 2.649 | 6.0037600701e−10 | 59.78701272 | −0.1825960044 |

이 표의 낮은 capture 확률과 매우 작은 기존 채널 변화는 stable response를 별도 RHS로 계산한 이유다. H1 probability 변화는 대략10⁻¹⁸, HeI 변화는10⁻¹⁹ 수준이다. 소스 평균·예상 사건수·signed reservoir는 [전체 source 결과](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/runs/cr_heiii_rr_primary_20261027_v1/SOURCE_WEIGHTED_RESULTS.json)에 보존했다.

새 diagonal addition loss의 최대 λ 대비 비율은1.0이었다. 일부 grid cell에서는 새 작은 diagonal 증분 전체가 binary64 덧셈에서 표현되지 않을 수 있다는 실측이다. 이를 지우거나 허용치를 넓히지 않았다. 독립 검산은 rounded K1을 그대로 정답으로 삼지 않고 `Decimal.from_float(stored K0)+Decimal.from_float(λ)`를 구성했으며,56개 열을 각각 자신의 infinity norm으로 검사했다. 위 오차와 finite grid/domain 결과는 해당 저장 문제의 수용 근거이며 전역 연속계/물리 오차의 interval certificate는 아니다.

## 5. 코딩 루프와 독립 검토

| 단계 | 실제 수행과 근거 |
|---|---|
| C1 | exact stored PR106 baseline, 물리 단위, 허용치·새30 CPU ceiling 동결 |
| C2 |21개 exact input, first18/conditional5/stable4/w, 적분↔rate·native25 단위 사상 |
| C3 |solver residual·새 addition loss·inherited rounding·grid/domain 차이 분리 |
| C4 |실제 CPU affinity, cache를 구분한 RAM 추정,1GiB reserve, 한 worker, threads1, AS512MiB, wall60 설계 |
| C5 |입력부터 source outputs/adapter/controls/dispatcher/plot까지7개 runnable source와 frozen templates |
| C6 |36/36 변경 controls; worker 내부 affinity/RLIMIT/threadpool 실제 readback 포함 |
| C7 |8-case224 RHS·24 source rows·24 exports 실행, 세 RR shared K1 보존 검사 |
| C8 |252개 저장 비교, finest6행 plot, 실제 PNG 시각 확인; 새 solver/provider0 |
| C9 |독립 Decimal70 56 RHS·754checks 및 현재/실행 source bytes·반환 결과를 별도 검토자가 결속 |
| C10 |source ZIP263 members와 Git209 blobs, Dropbox·Drive 실제 R3 완료; 최종 보고·인계·후속 DAG 및 중앙 owner-return 준비. D/M/최종 closeout identity는 실제 게시 후 외부 receipt에 기록 |

최종 C9는 **PASS_SCOPED, material finding0**이다. Producer와 Decimal checker 작성자가 아닌 검토자가 실제 C6–C9 결과와 실행 snapshot을 결속했다. 검토자가 R5 native25 구성과 C4 환경 조사에 참여한 사실도 명시하여 그 부분을 완전히 새로운 독립 유도로 가장하지 않았다. R6 독립 이론 검토와 실제 Decimal 검산을 함께 사용했다. [최종 독립 검토](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/review/C9_FINAL_REVIEW_KO.md)

## 6. 실제 비용과 보존한 실패

Preparation과 coordinator, 실패한 사전 실행을 포함한 실측 비용은 **6.988054525 / 30 CPU-s**다. 이 ledger의 범위는 새 scientific workers와 coordinator 및 exact-input preparation이다. 문서 읽기·모델 추론·게시·포장의 비용을 과학 CPU0으로 간주한 총비용 주장이 아니다.

| 실행 | Worker CPU s | Coordinator CPU s |
|---|---:|---:|
| C6 controls v1 | .427652 | .052623798 |
| C7 primary v1 | 1.431108 | .123628466 |
| C8 saved plot v1 | 3.055059 | .067896131 |
| C9 v1, worker 시작 전 차단 | 0 | .081043861 |
| C9 v2 | 1.470165 | .057253882 |
| exact input preparation | — | 별도 preparation CPU .221624387 |

C9 v1은 terminal plot의 owned stale lease 때문에 worker 시작 전에 차단되었다. `child_started=false`와 worker CPU0은 실제 receipt의 결과이며, coordinator .081043861 s는 비용에 남겼다. Plot PASS/exit0, 보존한 lease hash, 해당 PID의 부재를 확인하여 정확한 owned lease만 가역적으로 보존 경로로 옮겼다. 발생 원인 자체는 확정하지 않았고 unique v2로 진행했다. Failed attempt·옛 lease·recovery·authorization을 보존했으며 과학 worker가 시작된 뒤 실패한 경우는0이다. [실제 resource ledger](https://github.com/cosmosapjw-quantum/bass_cr/blob/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027/evidence/ACTUAL_RESOURCE_LEDGER.json)

H1 known lineage39.097868524, C23E15.493261114, 이전 HeI4.207939602, 외부 interface .147428830 CPU-s는 서로의 중복 관계를 임의로 해소하거나 합산하지 않았다. REI의595.225063/600 및 NO_MORE_IVPs, WU/HE의 기존 remaining0도 그대로다. Wolfram은 별도20초 time-constrained call1회, 관찰 elapsed8.138초이며 provider CPU는 null이다. 이번30 CPU의 산술적 잔여를 다음 unit에 자동 이월하지 않는다.

## 7. 종료 직전 공급자 재확인

선택된 WU/REC/HE branch를 실제 HEAD에서 다시 읽었다. WU는 두 commit 전진했고 REC·HE는 이전 선택 commit과 정확히 같다. 이번 atomic RR의 frozen 입력을 바꾸는 material change는 발견하지 않았다.

| 공급자 | 최종 관찰 HEAD | 채택할 실제 범위 |
|---|---|---|
| WU | `bfdeed676617c8b75ed81ac5e79e800fa69f83db` | He4(γ,d)D target6의 EXFOR 공급자4개·native36행, SIG24/DA12 및 별도 E2 보조7행;19 targets/28 directions의 primary-source reference28/28 |
| REC | `4a8e541030ee2cbd02e26ba671083b705d309d49` | 기존 HD35Hz gate:1행 PASS/7행 FAIL; H5 physical bounds0/313, physical epsilon null; 해당 AGENTS404 유지 |
| HE | `ac6042a6b0610b09d0576538767ee0299389a5eb` | conditional Tstar50–50000K, physical provider 미채택, HE101 PARTIAL_EXPORT/remaining0 유지 |

WU의 source-reference27/28→28/28는 자료 접근성의 진전이다. Empirical rate, nuclear Q, state/branch/domain, deposition, consumer 및 activation은 계속 false다. 새 MeV nuclear photon 자료의 beam·angle·identical-D normalization 의무를 보존하며, 이를 Verner atomic photon≤50keV RR 공급자로 사용하지 않는다. [WU 실제 admission](https://github.com/cosmosapjw-quantum/WU088_HH/blob/bfdeed676617c8b75ed81ac5e79e800fa69f83db/research/provider_registry_exfor_target6_20261027/SCIENTIFIC_ADMISSION.json)

HE의 AGENTS Git blob은 같고 과거 로컬 snapshot의 trailing newline 표현만 달랐다. 이를 새 provider 변경으로 해석하지 않았다. REC의 AGENTS404를 다른 branch의 지시로 대신 채우지 않았다. PR236의 donor T/nb 및 미병합32/88를 이 CR의 frozen bath나 중앙27/88로 옮기지 않았다. 최종 공급자 read-only 조사 기록의 결속 위치는 `intake/C10_FINAL_SUPPLIER_REFRESH.json (SHA256 a7dd44f11f52831a59dc98b2ef166374eb421d37a509ace798b6e58b8c1f9e87) 및 intake/C10_FINAL_SUPPLIER_NOTE_KO.md`다.

## 8. Source·문서·중앙 반영과 backup의 별도 identity

Science **S=`4e72c89b714431eb4c6ae07def777bbf72a5ae4c`**다. Git의 S commit/tree에서 실제 public blob209개를 raw readback하여 전부 SHA256 일치를 확인했다. Source ZIP은 다음과 같다.

| 항목 | 실제 값 |
|---|---|
| 파일 | `BASS_CR_HEIII_SOURCE_20261027_4e72c89b7144.zip` |
| Bytes | 33,586,109 |
| SHA256 | `deffe19ce3e2bd96c3af2bd1151fa635c4685a2b9d1f487969421d72236f94ac` |
| Local members 검증 |263개 actual raw SHA256/length/CRC PASS |
| 문서/closeout commit D | `이 문서를 최초 게시한 C10 commit D; 정확한 SHA는 PR107의 최종 S/D/M 표와 closeout authority에 결속` |
| 중앙 owner-return commit M | `D 이후 생성하는 중앙 owner-return commit M; 실제 SHA와 R3는 PR107의 최종 S/D/M 표와 closeout authority에 결속` |
| 최종 중앙 완료 수/원래 분모 | `27/88 (원래88 nodes·17 edges; 이번 child의 집계 효과0)` |
| Source Dropbox object/ACK/R3 | `id:BSpOijBcT10AAAAAAEC4Tg; ACK=true; 실제 full GET/R3,33586109 bytes,263 members hash/CRC PASS` |
| Source Drive object/ACK/R3 | `1yEQf3v5a-uqQj5ud1HFDKBftdJsb9ff_; ACK=true; 실제 full GET/R3,33586109 bytes,263 members hash/CRC PASS` |
| Source 문서 보존 ID/ACK | `libfile_9f14474283048191a064c902e5a5d780; ACK/xattrs 완료,R1; 별도 raw readback은 수행하지 않음` |
| Closeout backup objects/readbacks | `D/M 이후 생성하는 최종 closeout의 실제 IDs/해시/R3는 PR107 최종 보존 표에서 확인; 이 D preimage에서 미래 ACK를 주장하지 않음` |

Local archive 검증, Git raw readback, provider ACK, 원격 객체 복원 검증은 서로 다른 증거다. R1–C9의19개 checkpoint receipt는 실제 expected-SHA non-force commit과 해당 stage의 이중 backup R2 결속을 갖는다. Source 원격 ACK/R3는 publication/SOURCE_RELEASE_RECEIPT.json 및 SOURCE_REMOTE_R3.json에 결속했다. D의 C10 receipt와 이후 M/최종 closeout identity는 실제 발생 후 [PR107](https://github.com/cosmosapjw-quantum/bass_cr/pull/107) 및 최종 closeout ZIP에서 확인한다. 기존 `UNKNOWN_NO_ACK`는 과거 기록으로 유지하며 10/26 이후의 backfill 발견은 별도의 새 저장 증거로 덧붙인다. Final source manifest와 transport supplement는 S 본문을 소급해서 바꾸지 않는다.

## 9. 다음의 bounded 연구 단위

다음 목표는 **외부 photon/electron/baryon의 actual proper-time injection과 보존적 return contract**다. 이번24행은 종료까지 적분한 pulse 응답이므로, 다음 단계에서 실제 rate/exposure/time history와 원천의 clock·proper volume·energy coordinate·isotope/source support를 먼저 결속한다. 실제 nb는 같은 donor/state의 density여야 하며 PR236의 T/nb를 묵시적으로 빌리지 않는다.

선택할 최소 작업은 하나의 실제 공급자와 명시된 유한 time history를 고정하고, native source→proper source→적분 N/E→RR/native25 및 retained photon port의 단위와 소유권을 증명·구현·검증하는 것이다. Time/volume Jacobian은 한 번만 적용한다. Same-event ID 중복, frame 혼합, support 밖 확장, density의 이중 곱, conditional mean time의 exposure 대체를 거절한다. Photon transport·cascade·stopping·thermalization에 실제 공급자가 없는 부분은 미제공으로 남긴다. 입력이 없는 rate나 spectrum을 이번 moment에서 복원하지 않는다.

각 node 전에 최신 AGENTS, local/remote HEAD, 병렬 owner 작업, backup receipt를 확인한다. 기존 C6–C9 성공 근거는 identity와 scope가 맞는 부분을 재사용하며 old controls/solves를 재실행하지 않는다. 새 unit의 비용·범위·허용치를 별도로 고정하고, 독립 검토·expected-SHA non-force publication·source ZIP·이중 backup·실제 R3·DAG owner return까지 수행한다. N6/N7·L4·global physical error/heating의 승격은 해당 실제 predecessor와 물리 공급자 계약이 충족될 때 별도로 판단한다.

## 부록. 단계별 commit/receipt와 C10의 외부 결속

각 stage의 central scoped 표기는27/88을 유지했다. R1–C9는 아래의 실제19개 commit이며, C10은 이 문서를 최초 게시한 D다. C10 자신의 SHA·receipt는 게시 후 생성하여 최종 closeout에 담는다.

| 단계 | 실행 루프 위치 | 실제 commit | Receipt |
|---|---:|---|---|
| R01 | 1/20 | [5023b665ae0a](https://github.com/cosmosapjw-quantum/bass_cr/commit/5023b665ae0a247d6ec16a239f204d3e2669abb8) | `publication/R01_RECEIPT.json` |
| R02 | 2/20 | [1d82d5843ec0](https://github.com/cosmosapjw-quantum/bass_cr/commit/1d82d5843ec0fdf695d47067e8573758bad0eca7) | `publication/R02_RECEIPT.json` |
| R03 | 3/20 | [d69b6775ca9a](https://github.com/cosmosapjw-quantum/bass_cr/commit/d69b6775ca9a4cde60c8eb5503f095094bad9189) | `publication/R03_RECEIPT.json` |
| R04 | 4/20 | [79ee44590f5f](https://github.com/cosmosapjw-quantum/bass_cr/commit/79ee44590f5f59f874d10e85cec411c17655dec4) | `publication/R04_RECEIPT.json` |
| R05 | 5/20 | [030c53293628](https://github.com/cosmosapjw-quantum/bass_cr/commit/030c532936281f4112d3b8aad1406837bc1cb60f) | `publication/R05_RECEIPT.json` |
| R06 | 6/20 | [23a85cc51fe6](https://github.com/cosmosapjw-quantum/bass_cr/commit/23a85cc51fe603d3bb9c3d738f5ecd26d0baa2fa) | `publication/R06_RECEIPT.json` |
| R07 | 7/20 | [46d64307e9fb](https://github.com/cosmosapjw-quantum/bass_cr/commit/46d64307e9fb92c3e0518dee9d53c98fe9ebd7ce) | `publication/R07_RECEIPT.json` |
| R08 | 8/20 | [6d6e872a430d](https://github.com/cosmosapjw-quantum/bass_cr/commit/6d6e872a430d0a9dcbdb578312007be55676b6e1) | `publication/R08_RECEIPT.json` |
| R09 | 9/20 | [e7075044550d](https://github.com/cosmosapjw-quantum/bass_cr/commit/e7075044550dc04fd09f8ea633076d85d4ae7a99) | `publication/R09_RECEIPT.json` |
| R10 | 10/20 | [72b6f1252bd7](https://github.com/cosmosapjw-quantum/bass_cr/commit/72b6f1252bd76269c3f6e77d7c3b26e9ea13031a) | `publication/R10_RECEIPT.json` |
| C01 | 11/20 | [ed19249f7e06](https://github.com/cosmosapjw-quantum/bass_cr/commit/ed19249f7e0618e4f1dac6bcf88371faf691e4f7) | `publication/C01_RECEIPT.json` |
| C02 | 12/20 | [2e77af143110](https://github.com/cosmosapjw-quantum/bass_cr/commit/2e77af143110783a34f64c33df2a17c9bbad6bb9) | `publication/C02_RECEIPT.json` |
| C03 | 13/20 | [4ee4d2b41122](https://github.com/cosmosapjw-quantum/bass_cr/commit/4ee4d2b41122c48e9177feed76f72d82909cc5ea) | `publication/C03_RECEIPT.json` |
| C04 | 14/20 | [9c62481594eb](https://github.com/cosmosapjw-quantum/bass_cr/commit/9c62481594eb6f7727f17287b70d10c40e2270b4) | `publication/C04_RECEIPT.json` |
| C05 | 15/20 | [2fb37a395cbc](https://github.com/cosmosapjw-quantum/bass_cr/commit/2fb37a395cbc3ece11c0066fe631520a50540a7e) | `publication/C05_RECEIPT.json` |
| C06 | 16/20 | [1c88ba4b0f25](https://github.com/cosmosapjw-quantum/bass_cr/commit/1c88ba4b0f258c6ce83bcb197e4e2c3446915bbb) | `publication/C06_RECEIPT.json` |
| C07 | 17/20 | [02588ce7a5b1](https://github.com/cosmosapjw-quantum/bass_cr/commit/02588ce7a5b175ff8c0e8d9329da6273ebc94514) | `publication/C07_RECEIPT.json` |
| C08 | 18/20 | [e2be841b0cb0](https://github.com/cosmosapjw-quantum/bass_cr/commit/e2be841b0cb0d0346f424f7325c357ec904a720c) | `publication/C08_RECEIPT.json` |
| C09 | 19/20 | [4e72c89b7144](https://github.com/cosmosapjw-quantum/bass_cr/commit/4e72c89b714431eb4c6ae07def777bbf72a5ae4c) | `publication/C09_RECEIPT.json` |
| C10 |20/20|이 문서의 최초 C10 commit D; PR107 최종 표|게시 후 생성하여 최종 closeout에 담는 C10_RECEIPT.json|

## 최종 전송 상태의 읽기 순서

이 D 문서는 검증한 source와 과학 결과를 고정한다. 실제 중앙 반영과 마지막 전송의 종결은 [PR107](https://github.com/cosmosapjw-quantum/bass_cr/pull/107)의 S/D/M·closeout 표, 최종 closeout ZIP의 DELIVERY_AUTHORITY.json 및 REMOTE_R3 증거에서 확인한다. 원격 객체 ACK와 실제 byte readback을 구분하며 S 자체를 소급 수정하지 않는다.
