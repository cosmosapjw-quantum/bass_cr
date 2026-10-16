# C21B C6/C7/C8: 실제 샌드박스 이론·수치 검증 (2026-10-16)

## 실행 및 과학 범위

선행: parent bass_cr PR75 `6eda7834abb33750439e4316916b06cc2885b9fc`; 원본 native C20 PR74 `caf587b3edf4e27d038c6a918419be498d7d389c`; 사용자 제공 native C21 epoch RHS commit `807a46029cd2ebca16ab58cc3d92669277be3c00`는 본 샌드박스에서 실행하지 않았다. 비교 사용 자료: rei_bianchi PR160/162/163, BASS_HE HE23/PR70. 원본 Grackle RR/CI/DR/CMB, Case-A escape 및 NCP production은 변경하지 않았다.

연구 산출물: 양의 원본형 Verner H I/He I/He II 3종 반응, 별개의 MD14 birth-time GL2 패킷, 각 photon q=a_b E_b, FLRW gas adiabatic work, 기체/광자/결합 수지. 샌드박스 초기분율은 명시적으로 제조한 `[xHII,xHeII,xHeIII]=[0.2,0.2,0.01]`, `Tgas=8500 K`이며 owner C20 checkpoint의 동일 초기상태라고 주장하지 않는다. 입력 nH0는 HE23 verified native total-H density로부터 환산한 1.8981984507140266e-7 cm^-3이다.

## 실제 C6 수치검산 및 발견한 결함

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q tests` **27 passed in 0.49s**, exit 0 (sandbox Python 3.13.5, NumPy2.3.5, SciPy1.17.0, pytest9.0.2). 테스트는 안정적 exact-pair 및 independent Radau, q↔qref↔E map, native total-H density, 원본 Verner fit thresholds, positive source spectrum, MD14 GL2 vs QUAD, source-free 3종 동적 기체 연립 Radau, 실제 threshold crossing, source-on positivity/stoichiometric work, optical-stiff 상태, invalid input, transaction rollback, 독립 continuous-mono reference 및 실제 보존 잔차를 포함한다.

첫 source-on 5-case sweep에서 정확한 R5 source code는 caller 상태를 직접 변경했으나, API에 외부 트랜잭션 보장이 없었다. 물리 입력 실패 시 부분 적용될 위험이 있었으므로 `PhotonReactor.advance`가 내부 상태를 복제한 다음 전체 통과 시에만 반환하도록 교정했다. **첫 수정 후 호출자도 반환 객체를 대입해야 한다는** 실행 결함을 실제 저장된 무변화 사례에서 확인했다. 그 첫 실패 JSON은 `evidence/STUDY_POST_TRANSACTION_CALLER_FAILURE.json`로 보존했고, caller `state=model.advance(...)`로 정확히 고쳤다. 기존 실패 결과를 PASS로 재분류하지 않는다. 예외 시 입력 상태 및 birth counter 불변 회귀 테스트 추가 후 전체 27/27 PASS.

## C7 보존·물리 검증

`run_study.py` 원본 출처 형태 MD14/Verner source-on FLRW, 부드러운 opacity_scale=1e-4, 에너지 2 Gauss nodes/원본 3 threshold segments, x0=ln(1/12), Δx=8e-4, n=2/4/8/16/32: 최대 광자 수 잔차 2.88e-19/H, 총 photon+gas+binding+work 잔차 3.45e-13 eV/H. 이는 바이트 오차가 아닌 double-precision 계산상 수지 잔차. 기체/광자 양성 및 종별 사건 보존 통과. 광학적으로 강한 별도 native-원본형 Verner-단면적 스케일 factor=1 검산 Δx=1.5e-4, n=2/4/8/16: 최대 광자 1.006e-17/H, 에너지 2.757e-14 eV/H.

위 수치의 `native_opacity_stiff`란 **단면적 스케일이 원본형(1)**이라는 뜻이지, 실제 원본 C21 Rust/NCP native 실행을 뜻하지 않는다.

## C8 독립 연속 기준해와 수렴

실제 Verner는 photon E에 의존하므로 source-age cohorts 전체를 총 에너지 모멘트 하나의 ODE로 축약하지 않는다. 그 대신 검증 가능한 제조 기준에서만 주파수와 무관한 세 양의 단면적 `(1e-18,3e-18,5e-18)` cm²와 mono 80eV birth, 진짜 MD14 시간 방출을 사용했다. `independent_mono.py`는 단일 연속 원천 `j(t)`에 대한 coupled `N,Ugamma, H0,H+, He0,He+,He2+,w,work` ODE를 직접 SciPy Radau 적분하며 exact-pair 식·사건 합성 코드를 호출하지 않는다.

nsteps 2/4/8/16/32에서 독립 연속해에 대한 8개 주요 상태 변수 무한 노름 오차: `5.676566204426692e-6`, `1.3871761763706303e-6`, `3.4488341915661636e-7`, `8.611248869527799e-8`, `2.152273648192704e-8`. 각 2배 정제의 실제 관측 차수: `2.0328674702415306`, `2.0079703511465756`, `2.001814381868077`, `2.000360964276586`. 이는 **해당 smooth manufactured continuum problem에 한정한 2차 수렴**이다. 실제 C21 native solver 및 원래 Verner에 대한 일반론적 전역 수렴차수는 HOLD.

## Source-age 분해가 실제로 구별하는 기작

두 실제 GL2 source birth 시각 vs 모든 birth를 한 midpoint로 모은 경우를 비교한다. `j=3e-17 photons/(H s)` 일정, mono birth E=54.55eV, Δln(a)=.004, 원본 Verner cross sections, manufactured opacity_scale=.03. 두 실험은 **같은 양의 photon birth number 0.0023562226787267894/H와 같은 총 birth energy를 갖도록** 통제했다. 그럼에도 source-age GL2 vs midpoint-collapse에서 HeII photon absorption 차이 `(GL2 - midpoint)=-1.3733106363622024e-5/H`, endpoint gas temperature 차이 `-49.184766450685856 K`. GL2 첫 cohort의 HeII fit cutoff crossing 1개, 단일 midpoint cohort는 crossing 0개. 양쪽 모두 수지 잔차 ~1e-15eV/H. 과학적으로 이는 **조건부 birth-time 분포 민감도/비가환성 예제**이고 실제 MD14 native reionization의 예측차 또는 보편적 하한이 아니다.

## 실제 다음 계산 단위

- User-reported NCP C21 evolving-epoch Rust bridge `807a4602...`를 owner source+binary SHA로 실제 읽고 C19 checkpoint parity 3/3의 명령·원시 출력 확인.
- PR75/본 C21B의 photon q20→qref factor21, birth cohort source/Verner true shape, native total-H density, fixed gas initial state/clock를 정확히 일치시키는 native interface 구축.
- PR150 actual prepared photon BE closure와 본 positive exact-pair 합성의 차이를 같은 단계·source/IC에서 분리해 관측; PR162 old/newborn BE cancellation 및 PR163 midpoint RR 임계 오차와 비교.
- 원본 native Grackle Case-A RR/CI/DR/thermal/CMB와 통합하는 경우 동시 Newton residual+energy gate 및 transaction rollback; source-age/thermal/threshold independent refinement. 전체 history, signed Bianchi, anisotropy inference, full EoR은 HOLD.

## 증거 계층

`R5 DERIVED + Wolfram_5_ZERO`; `C5 IMPLEMENTATION_VERIFIED`; `C6/7 SANDBOX_PASS_27`; `C8 MANUFACTURED_SECOND_ORDER`, `C20/C21 full-native parity NOT_RUN`, `Case-A dynamic native/ Bianchi/full EoR HOLD`. Native subagent unavailable, serial fallback. GitHub and cloud delivery are 별도 영수증으로 보고하며 소스·검산 성공이 전송 성공을 대체하지 않는다.
