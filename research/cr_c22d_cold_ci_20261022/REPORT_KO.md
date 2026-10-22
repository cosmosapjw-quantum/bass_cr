# C22D — 유한 H1 충돌 이온화, 보존적 열화학 연결과 sandbox 최적화

## 결과와 범위

**C22D의 네 가지 새 초기값 문제를 실제 실행하고, 유한 저장·accepted mesh와 엄격한 참조해 비교 범위에서 수용했다.** 새로운 물리는 H1 바닥상태의 전자 충돌 이온화(CI)다. 기존 C22A의 열에너지·유한 UV photon 장부, C22B의 외부 CMB bath, C22C의 H1 n=2 excitation source에 CI의 입자 수·전하·결합에너지 이동을 연결했다. 과거 C21O/A/B/C 계산의 복원 목적 재적분과 NCP dispatch는 모두 0이다.

이번 결과의 두 변화는 별도로 측정했다. 같은 새 energy registry에서 CI만 켜고 끈 비교가 CI의 coupled-model 차이다. 저장된 C22C와 새 registry의 CI OFF 비교는 문턱·에너지 규약 변경의 차이다. 서로 다른 원인과 source identity를 한 ensemble로 합치지 않았다. 수치 분석의 전체 표와 유도는 `analysis_v1/ANALYSIS_REPORT_KO_v2.md`, 독립 검토는 `evidence/review_final/FINAL_REVIEW_KO.md`에 있다.

| 축 | 이 문서를 고정할 때의 실제 상태 |
|---|---|
| EXECUTION | 새 ODE4 완료; saved804·accepted8047; 기존 ODE 재실행0; 과학 수용 COMPLETE_SCOPED |
| PUBLICATION | 로컬 source commit26068749, 원격 source closure commit9496f159 및 authority branch ACK·readback 확보; 최종 전체 로컬 commit/bundle와 결과 문서 게시 영수증은 외부 final authority에 결속 |
| BACKUP | 5,798,208-byte 실행 체크포인트는 두 저장처의 실제 byte/SHA/CRC 재다운로드 PASS; 최종 배송본은 별도 receipt로 판정; Drive OPEN |
| DAG | C22D 채택 범위 완료 → 저장 상태를 이용한 line-admission 최소 진단 → 실제 line/source coverage와 geometry 결속. 전체 열화학·복사 폐쇄 OPEN |

## 1. 물리식과 구현의 연결

시간 변수는 eta=ln(a/a_i), abundance와 누적 사건 수는 기준 수소핵 Href당 값이다. 채택한 single-T Maxwell 전자에서

\[
\mathrm{H1}(1s)+e\longrightarrow\mathrm{H1}^{+}+2e,
\qquad r=\frac{n_eX_{H1,0}q_{\rm core}(T)}{H}
\]

를 사용했다. 한 사건의 변화는 X0'=-r, X+'=r, Xe'=r이고,

\[
U'_{\rm CI}=-\chi r,\qquad B'_{\rm CI}=+\chi r,
\qquad L'_{\rm CI,escape}=0.
\]

따라서 핵종 수와 전하를 보존하고, 이 반응 안에서 열·결합에너지 이동이 상쇄된다. 입자 수 N=sum(Xatom)+Xe를 포함한 T=2U/(3k_B N)로부터

\[
T'_{\rm CI}=-\left(\frac{2\chi}{3k_B}+T\right)\frac{r}{N}
\]

가 나온다. 코드에서는 U와 abundance를 진화시키므로 이 입자 수 항을 별도의 온도 source로 한 번 더 넣지 않는다. 누적 CI counter를 추가한 전하 장부는

\[
X_e+C_{\rm RR}-C_{\rm PI}-C_{\rm CI}-X_e(0)=0
\]

이다. Wolfram의 실제 기호 검산, 독립 scalar SI Maxwell 적분, 변경 지점의 보존 검산과 독립 saved-array 합산을 연결했다. Wolfram 초기 도구 오류·첫 evaluator 재귀 오류와 교정 후 PASS는 원 기록에 함께 보존한다.

전체 상태78개 중 solver 상태75개다. 제거한 세 좌표는 상속한 n,T0,T1의 정확한 영 초기 inventory에 결속한다. 21 atomic populations는 모두 출력에 남는다. H1에만 CI를 추가하므로 이전 H1/D의 같은 ionized-fraction 축약 조건은 유지되지 않는다. 모든 isotope quotient가 불가능하다는 결론은 채택하지 않았다.

Non-tilted LRS, metric(-,+,+,+), full Frobenius convention을 유지한다. signed Pr=Pgamma+Pnu, Pi_r=abs(Pr), Pi_tot=abs(Pm+Pr)를 별도로 저장·검산한다. Atomic gas의 isotropic stress closure와 별도 nonbaryonic Vlasov matter stress를 유지하며, line radiation의 등방성을 이 가정으로 대신하지 않는다.

## 2. 실제 atomic-rate coverage와 energy registry

CCC 저자 표의 H1 총 이온화 단면적87행을 고정했다. 문턱은 표의 13.6058 eV, 첫 양의 표본은 13.64 eV, 상한은968.61 eV다. Piecewise-linear 단면적에 대해 양의 endpoint Maxwell moments를 계산한다.

\[
q_{\rm core}(T)=K\theta^{-3/2}
\int_{\chi}^{E_{\max}}\sigma_{\rm PL}(E)E e^{-E/\theta}\,dE,
\quad \theta=k_BT\ [\mathrm{eV}],
\quad K=10^6a_0^2\sqrt{\frac{8\,\mathrm{eV_J}}{\pi m_e}}.
\]

이 값은 표가 정의하는 유한 적분이다. 끝점 밖 physical tail, 표 보간의 물리 오차상한, 실제 모든 원자종의 CI coverage를 뜻하지 않는다. 작은 온도에서 float64 rate가 underflow하더라도 log10(q)를 유지하여 표현 가능한 수치0과 source 미제공을 구별한다. 11개 독립 scalar SI 검산의 최대 log10 차이는5.68434e-14였고, fail-closed 입력 검사10개를 통과했다. 실제 pilot domain은3<T≤20,000 K, nHref≤0.01 cm^-3다.

| T[K] | q_core[cm^3 s^-1] |
|---:|---:|
| 300 | 8.61856e-239 |
| 2,000 | 7.21075e-44 |
| 10,000 | 6.51063e-16 |
| 20,000 | 2.74414e-12 |

새 registry `Hfamily_CCC13.6058_PI_support_refined_V1`은 H1/D/T의 공통 electronic threshold를13.6058 eV로 명시하고 PI support, 결합에너지, PI heating, RR export, CI cooling의 에너지 문턱을 일치시킨다. PH2의 계수 모양과 에너지 축은 그대로 두며 새 문턱 아래 support를0으로 정한다. 기존 RR number/capture fit은 독립적으로 유지한다. 이 조합에 Milne 관계나 LTE 상세평형이 성립한다는 주장은 하지 않는다.

13.6058 eV는 CCC 표의 convention이다. NIST가 제시한 H1 이온화에너지13.598433 eV와 구별한다. [NIST H1 자료](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable1.htm), [CCC 저자 자료](https://atom.curtin.edu.au/CCC-WWW/index.html), [Bray 등 2018 원전](https://link.aps.org/doi/10.1103/PhysRevLett.121.203401)을 실제 확인한 범위와 source SHA에 결속했다. 13.6→13.6058 변경의 상대 문턱 차이가 작아도 [13.6,13.6058) 구간의 PI support 차이는100%다. 실제 crossing 위치와 그에 따른 coupled 경로 차이를 별도 대조군으로 계산했다.

첫0.0342 eV 구간의 p=1.127 대안은 threshold-law에 근거한 동일 경로 민감도 진단이다. LRS accepted mesh에서 PL 대비 누적 functional 변화는약-1.92467e-5다. 같은 PL 사다리꼴 적분과 ODE counter 차이+1.15346e-4가 더 크므로 이를 정확한 counter 변화나 feedback 해 오차로 해석하지 않는다. 조건부 ground inverse/RR의 최대2.07344e-21 역시 채택한 유한 ground model·실제 ne·선언한 통계중량 조건의 진단이며, all-level 3-body omission bound와는 구별한다.

## 3. sandbox에서 채택한 계산 단순화

물리 상태를 같은 eta,y에서 세 번 재평가하던 경로를 한 번으로 통합했다. 현재 상태에 필요한 q(T)는 매 호출의 실제 T에서 계산하며, 다른 상태 사이에 cache를 이월하지 않는다. Maxwell moment의 공통 Taylor term을 한 번 만들어 J0,J1,J2에 사용하고 기존 k=0..18의 per-entry 나눗셈·누적 순서를 유지했다. 빈 branch는 계산하지 않는다.

304개 moment 입력,197개 provider 온도,24개 저장 상태×77개 상속 RHS 성분에서 signed zero를 포함한 bytes 일치를 확인했다. 이 근거로 ordered 경로를 production에 채택했다. Horner 후보는 moment에서4.2324e-16 상대 차이가 생겨 production HOLD로 남겼다.

측정 시간은 반복 방식에 따라 달랐다. 첫 측정의 combined 중앙비2.204, paired 중앙비1.288, paired 총시간비1.375가 기록되어 있다. 같은 입력에서 연산 중복을 줄인 구현과 byte 동등성은 확보했지만, 일반적인2.2배·campaign 전체 speedup은 주장하지 않는다. 62→33 대수 축약이나 외부 REI prepared-RHS 성능을 이 코드의 측정 성능으로 대체하지 않았다.

실제 sandbox affinity0..8, CPU quota8, memory8GiB를 확인했다. coordinator0, ODE workers1·2, 분석CPU3, 독립 검토·후속 경량 진단CPU4를 분리하고 모든 native thread를1로 유지했다. CPU55는 이 sandbox에 없으며 보호 대상에서 제거하거나64-core host가 있다고 가정하지 않았다. 협력 lease 조사 결과와 메모리 여유를 실행 직전에 확인했고, 독점 lease를 획득했다는 주장은 하지 않는다.

## 4. 새 입력과 수치 결과

모든 새 case는 T_initial=300 K, z20→2, finite-photon scale1, Compton bath Tcmb0=2.7255 K, H1 n=2 excitation을 유지한다. LRS initial signed coordinates는 Sigma0=.3, Pm0=.0002, Pr0=.0008이다. FLRW control은 이 세 입력을0으로 둔다.

| 새 case | solver·rtol/atol | accepted점 | nfev | 실제 wall[s] |
|---|---|---:|---:|---:|
| 새 registry, CI OFF, LRS | BDF 3e-11/3e-13 | 1,618 | 3,614 | 56.749 |
| CI ON, LRS | BDF 3e-11/3e-13 | 1,618 | 3,614 | 67.219 |
| CI ON, FLRW | BDF 3e-11/3e-13 | 1,616 | 3,608 | 41.577 |
| CI ON, LRS 참조 | Radau 3e-12/3e-14 | 3,195 | 22,546 | 115.886 |

각 case는201개 saved times, 전체72 segments를 보존한다. BDF input identity는83b5730124730ffba28015af40aa3cde68727b6344cd27508f3287bee5638453, Radau는42a1cef0ac19adba207c5b613ffa7ad73ed2f143326a6ad05215d4a59da72af5다. 각각의 run·raw SHA는 `SCIENCE_ACCEPTANCE.json`과 원 receipt에 있다.

사전 기준은 energy1e-8, nuclei/charge/photon1e-10, scaled population≥-2e-9, UV·counter≥-2e-11, 선언한 exact-zero inventory와 domain이다. saved와 accepted 모두 통과했고, accepted energy 상대 잔차 최대는약1.446e-11이다. 약1e-14의 UV 음수 잔차는 원래 허용치 안에서 보존했으며 clipping하지 않았다. 이 검사는 유한 표본의 residual이며 연속 구간의 오차 certificate가 아니다.

엄격한 Radau와 비교한 T,ne,tau_T,Sigma_F,Pi_r_F,H1 ion fraction,bath energy,n2 escaped energy,CI counter의9개 normalized 차이가 모두2e-7을 통과했다. 최대는 CI counter6.35698e-8, 다음은 n2 escaped energy2.92182e-8이다. 단위·초기0의 정규화는 frozen contract 그대로 사용한다. 분석 단계에서 새 ODE0·RHS0이며, 완료된 이전 C22C summary도 재계산하지 않았다.

| LRS z=2 결과 | 새 registry CI OFF | 같은 registry CI ON | ON−OFF |
|---|---:|---:|---:|
| T[K] | 29.8985991406 | 29.8968531736 | -0.0017459670 |
| ne[cm^-3] | 1.44565813247e-7 | 1.44561288882e-7 | -4.52436502e-12 |
| tau_T | 0.0223412071329 | 0.0223412385540 | +3.14211435e-8 |
| H1 ionized fraction | 0.0278874599328 | 0.0278865921463 | -8.67786509e-7 |
| n2 escaped energy[eV/Href] | 0.0398252310876 | 0.0398069348889 | -1.82961987e-5 |

온도 차이의 저장 mesh 최대절댓값은0.480120 K다. CI ON의 누적 CI 사건은7.37974053e-6/Href이며, FLRW에서는7.38874015e-6/Href다. 전자 생성 반응을 추가했는데 최종 ne가 감소한 이유는 coupled 장부에서 드러난다. 두 경로의 ΔPI=1.9317881e-14, CI=7.37974053e-6, ΔRR=8.25804404e-6이므로 ΔXe=ΔPI+CI−ΔRR=-8.78303490052e-7/Href다. 원 ne/nHref의 차이와3.45e-18만 다르다. 이 장부 설명은 두 coupled 경로의 차이를 설명하며, 개별 rate의 독립 인과효과를 추정한 것은 아니다.

전단의 ON−OFF 최대 차이1.83126e-11은 ON의 BDF−Radau 차이1.65345e-10보다 작다. 전단의 CI 효과는 이번 자료에서 미분해로 기록한다. 반면 threshold registry 변경은 종료온도-0.01171996 K, tau_T-3.0612573e-6, n2 escaped energy-0.000375905 eV/Href의 별도 차이를 만들었다. 이 수치들을 CI 효과에 합쳐 보고하지 않는다.

## 5. 발견한 오류와 수정의 범위

초기 변경 검사의36개 중34개는 통과했고, warm CI increment의 두 비교는 실패했다. 원인은 큰 base RHS에 작은 CI increment를 더한 뒤 작은 increment 기준으로5e-12 상대정확도를 요구한 판정이었다. 독립 exact-Fraction 검산에서24개 덧셈은 모두 올바른 binary64 반올림과 일치했고, 이후 뺄셈24개도 exact였다. 원 FAIL을 보존한 채 잘못된 두 predicate를 명시적으로 폐기하고 ULP·stoichiometry·보존식 및 실제 strict reference 근거로 대체했다. ODE tolerance나 물리를 조정해 통과시킨 일이 아니다.

실제 runner의 후속 segment 준비 예외가 이전 accepted points를 잃을 수 있는 보존 결함도 발견했다. integration 실패 경계 안으로 준비 단계를 옮겼고, 가짜 solver를 쓴 fault test의 RED/GREEN으로 이전 두 점·한 segment가 보존됨을 확인한 뒤 source를 고정했다. fault test의 cosmological ODE는0이다.

수치 분석v1의 네 그림에는 symlog 자동 padding에 의한 음수 시간/eta tick과 label 겹침이 있었다. 원 그림을 보존하고 저장 CSV/NPZ/raw만 읽는 figure-only 경로로 figures_v2를 만들었다. root와 독립 reviewer가 PNG4개를 실제 판독했다. 원 analyzer SHA3391cfd378e76c31c4f3509c395f80ded2b8a6eef7b0487bb7591facffadde5e는 `analyzer_executed_v1.py`에 보존한다. 최종 analyze.py에 추가한 재렌더 기능은 완료 수치 실행 source와 구별한다. 보고서v2는 잘못 적은 source 파일명 ci.py를ci_finite.py로 교정했다.

원 SUMMARY의 `all_gate_failures_preserved=false`는 분석 gate 실패가 없다는 구현상의 표현이다. final completion과 독립 review에서 analysis gate failures=0, prior light-check FAIL preserved를 명확히 했다. 원 수치 bytes는 변경하지 않았다.

## 6. 외부 근거와 후속 연구

마지막 intake는7개 저장소1,271 advertised heads였으며 직전1,259 대비+12/3changed/0removed였다. 선택 text15개113,097 bytes를 Git blob SHA1과 endpoint bytes로 확인했다. 외부 raw 재실행·다운로드는 이번 intake에서0이다. 외부 HE85의 새394 identity는 owner의 recovery rerun 보고이며 원 NPZ bytes 복원으로 채택하지 않는다. REI219의 일부 가족 완료와 native coupled production HOLD를 구별한다. 원127 JSON 실패·재적분, VigilODE P02 C6FAIL 및 이전 HE85/REI219 미완료 이력은 유지한다. 접근 불가 대화는 UNAVAILABLE, 원 핵반응 PNG는 NOT_RECOVERED_NOT_READ다.

다음 최소 단위는 저장된 signed H,s에서

\[
H_\gamma(\mu)=H+s(3\mu^2-1),\qquad
\frac{d\ln\nu}{dt}=-H_\gamma,\qquad
\frac{d\mu}{dt}=-3s\mu(1-\mu^2)
\]

를 진단한다. line opacity에 필요한 column/geometry, A/f/profile, 2s two-photon differential spectrum, cascade branching, mixing/de-excitation, secondary energy-sharing source는 별도 계약에 따라 확보한다. 원자 방출, resonance에서의 이탈, 실제 공간 경계 탈출은 각각 다른 energy channel이다. 단순 escape factor를 gas cooling에 곱하기 전에 excited/resident-radiation reservoir와 반응별 상쇄를 유도한다. 누락 입력은0 대신 null과 REQUIRED_INPUT_UNAVAILABLE로 기록한다.

새 strong no-go는 채택하지 않았고 NG1–NG7은 새 배제 정리 채택에 대해 N/A다. 고온 핵반응 전체 및 tilted/triaxial/polarized CMB 확장은 HOLD다. 현재 Maxwell single-T·즉시 level return·완전 line escape와 선택된 원자 rate의 적용 범위를 유지하며 전체 열화학/복사 에너지 폐쇄는 OPEN이다. **global_error_bound=null.**

## 7. 후속 C22E 최소 단위의 실제 완료 결과

위 계약을 이어 `c22e_line_admission_20261022_v1`을 실제 실행했다. 기존 saved804점과 accepted8047점, 합계8,851개 표본의 저장된 H,s와 source/array identity를 재사용했다. mu²에 대한 Hgamma의 affine 구조로 각 시점의 angular extrema를 두 endpoint에서 정확히 계산했다. 별도 각도격자나 새 ODE·RHS·provider 평가를 추가하지 않았다.

LRS 전체 표본에서 min(Hgamma/H)=0.8775255128608411, max(Hgamma/H)=1.2449489742783177이고 모든 방향의 순간 적색편이율이 양수였다. max(3abs(s)/H)=0.3674234614174767이며 마지막에는약0.01914546이다. FLRW의 약1.42e-20 수준 signed-s 수치잔차를 그대로 유지했다. 이 결과는 각 시간 표본에서 모든 방향을 다루며, 시간 표본 사이의 전역 극값 판정과는 구분한다.

실제 CPU4·native thread1에서 wall4.775s/CPU4.625s로 완료했다. sign·missing·invalid-input fixture와 exact-rational endpoint 검산을 보존했고 기존 raw/accepted bytes는 변하지 않았다. geometry, A/f/profile, 2gamma spectrum, residence/destruction, cascade/mixing, secondary source의 누락은 null+REQUIRED_INPUT_UNAVAILABLE다. 따라서 빠른 준위 제거·즉시 boundary escape의 물리적 수용은 REGIME_NOT_ESTABLISHED로 유지한다. 결과와 식–코드의20단계 대응은 `evidence/line_admission/LINE_ADMISSION_REPORT_KO.md`에 있다.

## 재개 순서

최종 배송본과 외부 final authority의 해시·실제 provider 상태를 먼저 읽는다. 이미 완료된 raw·accepted 분석·원전 검산을 재실행하지 않는다. line-admission 진단 결과에서 실제 누락 source와 geometry를 채운 뒤, 검증된 level elimination 또는 resident-radiation adapter를 선택한다. 물리 계약 변경은 별도 source/input identity로 고정하고 가벼운 검증 후 새 run ID와 fresh resource/lease로 실행한다.
