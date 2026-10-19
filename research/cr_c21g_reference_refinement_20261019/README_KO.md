# C21G: reference 민감도와 상쇄 이후 시간 정련

C21G는 C21F의 고정 fixture와 native nonphoto kernel을 유지하면서, reference의 수치 민감도를 관측하고 hybrid–FULLMID 차이의 leading coefficient를 분리하는 작업이다. 필요한 이론·실행기·분석기를 구현하고 새 소프트웨어 검사 35개, 제조 analytic 9 cases, 제조 wiring smoke 3 jobs를 검증했다. **새 C21G native reference 8개와 조건부 정련 4개는 아직 `NOT_RUN`**이다. 현재 원격 실행 도구의 가용 호출량이 0이라 NCP의 실제 자원·campaign를 확인하지 못했다.

문서 작성 시점의 게시·백업 상태는 `NOT_YET_PUBLISHED` / `NOT_YET_BACKED_UP`이다. 최종 전달은 `PUBLICATION_RECEIPT.json`, `BACKUP_RECEIPT.json`, [DAG_C21G.json](DAG_C21G.json)의 실제 응답으로 갱신한다. 새 실행 결과의 완료와 코드 전달 완료는 별개다.

## 1. 재개 기준과 새 결과 확인

부모는 [PR83](https://github.com/cosmosapjw-quantum/bass_cr/pull/83)의 `d780c2c53f869c914add1d5492312d0bc507f976`이다. C21F의 실행 기준 `f8359232df8d0dd4fe91fcdabeb6701eb06089ba`, PR82 native 원자료, PR83의 signed-error 분석을 재사용한다. Native owner는 `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`다.

연구에 앞서 Drive의 bass_cr 폴더 45개와 root 최근 목록 100개, Dropbox의 `/bass_cr/C21` 6개 파일 및 C21F 검색 결과를 실제 확인했다. 관측 범위의 최신 C21F 산출물은 기존 `BASS_CR_C21F_NATIVE_ASSESSMENT_20261019T0530Z.zip`이었으며 새 native 실행 archive/receipt는 발견하지 못했다. Drive legacy 검색의 archive 누락과 Dropbox 시간 필터의 불일치는 직접 목록·metadata로 보완했다. 기존 archive 전체를 다시 받거나 과거 56개 검사와 native 행렬을 반복하지 않았다. 자세한 범위와 한계는 [새 백업 intake](evidence/intake/BACKUP_DELTA_INTAKE_20261019T0800Z.json)에 있다.

이 단위의 기존 경로 수정은 `research/cr_c21e_event_native_20261018/src/reference_tau.py`의 control·solver 진단이다. Native kernel, photon coupling 식, source fixture, binding energy는 유지한다. 새 실행은 C21F 실행 commit으로 표기하지 않고 **C21G 실제 실행 commit과 실행 manifest**로 기록한다. 검증한 `EXECUTION_MANIFEST.json`의 SHA256은 `7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed`다.

## 2. 새 이론 결과

### Photon과 온도의 비교

같은 양의 cohort amplitude (A)에서 (N=Ae^{-\tau})이면

\[
\Delta\log N=-\Delta\tau,\qquad
\widetilde N-N=N\operatorname{expm1}(-\Delta\tau).
\]

두 reconstruction이 IEEE zero가 되어도 유한 log-survivor 차는 남는다. `diagnostics.py`는 공통 (\log A)를 먼저 소거한 tau 차와 stable count 차를 기록한다. 구조적 (A=0), 유한 log를 갖는 underflow, log를 알 수 없는 positive-weight zero를 구별하며 stock floor를 넣지 않는다.

Gas (g=(x,y,z,w)), (Y=n_{\rm He}/n_{\rm H})와 (D=1+Y+x+Y(y+2z))에서

\[
T=\frac{w}{(3/2)k_BD},\qquad
T_L-T_R=\frac{\Delta w-w_R\Delta D/D_R}{(3/2)k_BD_L}.
\]

따라서 thermal 오차와 temperature 오차는 구별해야 한다. 분석기는 직접 EOS 온도차와 위 항등식의 stable 평가를 함께 보존한다. H/He number·binding·energy ledger도 solver의 `totals()`를 import하지 않고 독립 재계산한다.

### Reference 변화량의 해석

Radau의 local tolerance는 endpoint global error의 상계가 아니다. 실제로 검증된 reference 오차 상계가 (\rho)라면 stored component error (E_n=u_n-R)에 대해

\[
\max(0,|E_n|-\rho)\le|u_n-u_*|\le|E_n|+\rho
\]

이며 양의 lower bound가 있을 때 조건부 차수 interval을 얻는다. 이번 ladder의 마지막 차와 mesh 차는 **empirical sensitivity radius**로만 기록한다. `global_error_bound=null`을 유지한다. 공통 kernel·event 정책의 편향은 여러 reference의 차에서 소거될 수 있다. 엄밀한 인증으로 이어지는 residual·stability·event-error 분해와 남은 의무는 [이론 유도](theory/THEORY_REFERENCE_ERROR_KO.md)에 적었다.

### Reference를 소거한 두 scale 계수

\[
d_n=u_{\rm HYB}(n)-u_{\rm FULLMID}(n)
=A/n+B/n^2+O(n^{-3})
\]

라는 점근 전개가 성립하는 구간을 가정하면

\[
\widehat A_n=n(4d_{2n}-d_n),\qquad
\widehat B_n=2n^2(d_n-2d_{2n}).
\]

(C/n^3) 항까지 있을 때는 정확히 (\widehat A_n-A=-C/(2n^2)), (\widehat B_n-B=3C/(2n))다. 이 식을 실제 구현하고 대수 제조 검사로 확인했다.

기존 endpoint에 새 진단을 적용한 thermal 값은 다음과 같다. 새 native 실행은 아니다.

| 시작 (n) | native_source (\widehat A_n) | native_source (\widehat B_n) | common_ic (\widehat B_n) |
|---:|---:|---:|---:|
| 8 | −7.654158066117134e−5 | −1.4562402725459833e−5 | −1.8175683180743363e−10 |
| 16 | −7.654582731220216e−5 | −1.4494456308966619e−5 | −2.53749021794647e−10 |
| 32 | −7.654775441068296e−5 | −1.4432789157581283e−5 | −6.293703336268663e−10 |

Native (\widehat A_n)는 세 쌍에서 음수이고 변화가 작다. 그러나 인접 drift의 비는 약 2.20으로, (n^{-2}) 잔여항의 4배 축소를 확인한 자료는 아니다. Common (\widehat B_n)는 안정하지 않다. 이 값으로 zero crossing을 예측하거나 계수의 정확도 상계를 만들지 않는다. 전체 성분은 `evidence/baseline_coefficient/BASELINE_COEFFICIENT_DIAGNOSTIC.json`에 보존한다.

## 3. 여기서 구현한 실행 계약

기존 두 fixture는 common_ic 9 cohorts, native_source 27 cohorts이며 birth·spectrum·opacity를 그대로 고정한다. 기존 L0 reference는 재사용한다.

| 새 tier | rtol | vector atol multiplier | cell max-step divisor |
|---|---:|---:|---:|
| L1 | 2e−11 | 2e−14 | 8 |
| L2 | 2e−12 | 2e−15 | 8 |
| L3 | 2e−13 | 2e−16 | 8 |
| L3M | 2e−13 | 2e−16 | 16 |

Vector atol은 고정 scale에 multiplier를 곱한다. Tau와 fraction은 1, number ledger는 1/H, thermal은 (w_0), energy ledger는 초기 thermal·binding과 모든 고정 birth photon energy의 합을 사용한다. 실제 state를 floor로 바꾸는 처리가 아니다. (Y=0)에서는 두 He fraction과 대응 atol 성분을 축소하여 같은 reduced solve에 전달한다.

Reference의 RHS 호출·nfev/njev/nlu, actual accepted grid hash, effective tolerance, dynamic dimension, underflow와 one-sided endpoint 정책을 기록한다. `L3`와 `L3M`의 실제 grid가 같으면 `MESH_CAP_INACTIVE`로 보고한다.

사전 pilot resolution 목표는 다음과 같다. 물리 수용 기준이나 오차 인증 기준과 구별한다.

| Pairwise endpoint diagnostic | common_ic | native_source |
|---|---:|---:|
| max(fraction 차, abs(Δw)/w0) | 1e−14 | 1e−10 |
| max cohort abs(ΔN) /H | 1e−14 | 1e−12 |
| max positive cohort abs(Δlog N) | 1e−10 | 1e−8 |

**8개 reference job이 모두 실행 완료이고 native_source의 L1–L2·L2–L3·L3–L3M 차가 목표 안에 있을 때**, native_source의 FULLMID와 MIDPHOTO_ENDMICRO에 (n=128,256)을 추가한다. Common_ic의 budget 초과는 독립 판정이므로 이 조건의 native 정련을 막지 않는다. Common_ic의 실행 실패·누락은 전체 reference 단계 미완료다.

`run_campaign.py`는 한 worker씩 실행하고 job별 wall 300초, native/RHS 200,000 호출, native call 15초의 사전 예산을 기록한다. 현재 campaign를 확인해 할당한 CPU 하나만 사용하며 보호 CPU 55는 제외한다. Timeout 시 이 실행기가 생성한 process group만 종료한다. 기존 watcher·dirty files·checkpoint·다른 job은 보존한다. 출력은 create-only이며 `--reuse`는 signature와 payload 검증을 통과한 **완료 C21G job**만 읽는다.

## 4. 실제 경량 검증과 남은 실행

| 검증 | 작성 시점 상태 | 근거 |
|---|---|---|
| 기존 reference의 control·진단 수정 | 새 집중검사 9/9 PASS | `evidence/tests/reference_patch/` |
| 독립 endpoint/ledger/order 진단 | 새 집중검사 9/9 PASS | `evidence/tests/diagnostics/` |
| 제조 analytic IVP | 새 9 cases PASS, 1.9097576초 | [ANALYTIC_REFERENCE_CHECK.json](evidence/analytic_reference/ANALYTIC_REFERENCE_CHECK.json) |
| 실행기·복원 provenance 검사 | 새 집중검사 14/14 PASS | `evidence/tests/campaign/` |
| Standalone 분석 입력 binding 검사 | 새 집중검사 3/3 PASS, unittest 0.022초 | `tests/test_analysis_binding.py`, `evidence/tests/` |
| 제조 wiring smoke | 3 jobs COMPLETE/PASS, 4.4942750초 | `evidence/tests/wiring_smoke/` |
| 새 C21G native 8+4 jobs | NOT_RUN | 원격 자원 확인·실행 receipt 필요 |

Analytic IVP는 무차원 시간에서 (\tau'=\kappa), (N=Ae^{-\tau}), (P'=\kappa N), (w'=Q\kappa N-\mu w), (L'=\mu w)다. (\kappa=80,800)의 네 tier와 (\kappa=\mu)의 resonant case를 계산했다. κ=800에서 finite log를 보존하는 survivor underflow를 실제 확인했다. 해석식을 binary64로 평가한 값과의 차이며, machine precision 부근의 차를 실수 산술의 정확도 인증으로 표현하지 않는다. L3/L3M의 actual grid는 두 stiff case 모두 같아서 `MESH_CAP_INACTIVE`였다.

소프트웨어 검사 35개는 reference patch 9 + diagnostics 9 + runner 14 + analysis binding 3개다. Analytic 9 cases와 smoke 3 jobs는 별도로 센다. Analysis binding의 process wall은 0.1276117초이며 unittest 내부 보고 0.022초와 구별한다. Smoke는 작은 Y=0 제조 fixture에서 reference L1·FULLMID 4·hybrid 4의 실제 배선 경로를 확인했다.

모든 검사를 red-first라 하지 않는다. Control patch와 orchestration 교정의 최초 실패 증거, diagnostics·analysis binding의 새 대수·경계 검사, 과거에서 재사용한 검증을 구별한다. 독립 검토의 S1 실행 gate, S2 log completeness, S3 binary64 비교 명칭, S4 provenance 연결은 최종 교정과 해당 검사로 닫혔다. 근거는 `evidence/review/SCIENCE_REVIEW_KO.md`에 있다.

현재 단계 지도는 선택된 PhysMath Research Loop 1.3.0을 따른다. C5 구현·C6 소프트웨어 검증·C9 범위 내 독립 검토를 완료했고, C7/C8은 제조 문제의 검증과 새 native 검증을 분리한다. 새 native C7 물리 검증과 C8 정확도·수렴 검증은 `NOT_RUN`이다.

**Full48, source-age, spectral, angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity는 HOLD**다. 다음 native 결과는 source/fixture/raw identity, 실행 상태, 수지, reference 민감도, component별 signed 차수와 active component 교체를 분리 평가한다.

## 5. 시작 파일

- [REPRODUCE.md](REPRODUCE.md): 읽기·가벼운 검증·새 native 실행 명령.
- [RESEARCH_LOOP.md](RESEARCH_LOOP.md): R1–R10, C1–C10과 근거 연결.
- [DAG_C21G.json](DAG_C21G.json): 상태·의존성·게시·백업.
- [CODEX_HANDOFF_KO.md](handoff/CODEX_HANDOFF_KO.md): 실제 자원 발견부터 시작하는 실행 인계.
- `EXECUTION_MANIFEST.json`: 실행 코드와 재사용 fixture/baseline의 정확한 SHA.
