# C23A IGM 외부 공급: rate-moment 계약과 복사·입자 장부

## 범위와 판정

본 packet은 Puchwein 등의 실제 공개 fiducial UVB rate 표를 회수하고, 외부에서 지정된 광이온화·가열 모멘트를 gas evolution에 연결하는 연산자를 구현한다. 근거 버전은 **arXiv:1801.04931v1 (2018-01-15)**이며, 관련 최종 논문은 Puchwein et al., MNRAS 485, 47 (2019), DOI 10.1093/mnras/stz222이다. arXiv v1 표와 journal version의 byte identity는 주장하지 않는다.

현재 packet의 출력은 `P19Fiducial.evaluate(z)`와 명시적 binding registry에 대한 `source_budget`이다. 스펙트럼, radiation reservoir, stellar population synthesis, CR acceleration 또는 nuclear reaction network를 복원하는 연산자가 아니다. R/C 루프의 원자료·유도·구현·제한된 검증은 완료했고, 상위 작업의 독립 검토·실제 모델 통합·게시·백업을 기다린다. 신규/복원 ODE 실행은 0이다.

## R1–R3: 원자료와 채택 결정

직접 회수한 파일은 `sources/P19V1_rates_fiducial.txt`이다. URL은 https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt 이고 크기는 4,381 bytes, SHA-256은 `5b4cca58fcc46e821970c0a5a8cbb188cf2b5e6c00f56d6942588c86806662fe`이다. 59개 redshift node가 0 ≤ z ≤ 15.1을 덮는다. 열 순서는 z, Γ_HI, H_HI, Γ_HeI, H_HeI, Γ_HeII, H_HeII, Compton이다. Γ 단위는 s⁻¹, H 단위는 흡수 target 하나당 eV s⁻¹이다. 앞의 여섯 process-rate 열은 실제 모든 행에서 양수다.

원 저자의 readme(https://arxiv.org/src/1801.04931v1/anc/readme.txt)와 논문 Appendix D1/Table 3(https://arxiv.org/html/1801.04931v1)은 이 표를 비평형 이온화·가열 적분용으로 지정한다. 별도 D2와 TREECOOL은 equilibrium solver가 특정 평균 IGM history를 모방하도록 만든 equivalent-equilibrium 모델이다. 본 packet은 D1만 채택한다. 논문 HTML Table 3과 ancillary 표의 59×7=413개 수를 실제 비교하여 모두 같음을 확인했다. 이는 같은 저자의 두 표현을 확인한 것이며 독립적인 물리 calibration은 아니다.

원 readme와 현재 읽은 논문에는 숫자로 된 원자별 threshold convention과 Compton 열의 충분한 계약이 없다. 따라서 threshold 값은 caller가 명시하고, source의 숫자 threshold와 정확히 같다는 의무는 OPEN으로 유지한다. Compton 열은 보존하되 계산에 사용하지 않는다. 기존 CMB Compton 항과 이 열을 중복해 더하지 않는다. 원 자료의 license는 arXiv non-exclusive distribution license이며, 별도의 permissive source-code license가 있다고 주장하지 않는다. 원 rate 숫자는 출처를 명시한 사실 자료이고 adapter 구현은 이번 작업에서 작성했다.

FG20 저자 페이지 https://galaxies.northwestern.edu/uvb-fg20/ 는 웹 fetch 및 실제 HTTP에서 502였다. 이를 FG20 데이터가 존재하지 않는다는 판정으로 확대하지 않는다. Grackle 공식 문서는 비교 대상으로 읽었다. Grackle의 HM12/FG11 UVB 최대 z와 Cloudy cooling density/T 범위는 서로 다른 계약이고, 이를 본 P19 표의 계약에 이식하지 않는다. Grackle 전체 chemistry를 설치하거나 실행하지 않았다.

## R4–R5: proper intensity, emissivity, 광자 수

metric signature는 (−,+,+,+), h=2πℏ를 유지한다. 등방적인 proper specific intensity J_ν의 cgs 단위는 erg s⁻¹ cm⁻² Hz⁻¹ sr⁻¹이고, proper volume emissivity ε_ν의 단위는 erg s⁻¹ cm⁻³ Hz⁻¹이다. 두 양은 같지 않다. P19의 방정식은

\[
(\partial_t-H\nu\partial_\nu)J_\nu+3HJ_\nu
=-c\kappa_\nu J_\nu+\frac{c}{4\pi}\epsilon_\nu.
\]

comoving emissivity ε_ν,c를 proper frequency에 대해 정의했다면 ε_ν=a⁻³ ε_ν,c이다. Mpc⁻³ 표를 cm⁻³로 바꿀 때에는 길이 단위의 세제곱 변환도 별도로 필요하다.

proper photon number density per proper frequency를 n_ν=4πJ_ν/(c hν)로 정의하면

\[
\partial_t n_\nu+3H n_\nu+\partial_\nu(-H\nu n_\nu)
=\frac{\epsilon_\nu}{h\nu}-c\kappa_\nu n_\nu.
\]

따라서 N_ν=a³ n_ν는 spatial dilution만 없애며 redshift flux는 남는다. 로그 frequency x=lnν에서 P_x=a³νn_ν로 바꾸면 FLRW collisionless transport는 ∂tP_x−H∂xP_x=0이다. 이 식은 finite-volume energy-bin 경계 flux를 직접 준다. 유한 에너지 구간을 사용하면 경계로 나가는 photon number와 energy를 별도 장부에 기록해야 한다.

LRS 방향 flow는 C22E의 convention H_γ=H+s(3μ²−1), v_μ=−3sμ(1−μ²)를 사용한다. proper density per dν dΩ에 대해 conservative form은

\[
\partial_t n_{\nu,\mu}+3Hn_{\nu,\mu}
+\partial_\nu(-H_\gamma\nu n_{\nu,\mu})
+\partial_\mu(v_\mu n_{\nu,\mu})=S_{\nu,\mu}-c\kappa n_{\nu,\mu}.
\]

방정식의 비미분 계수는 3H−H_γ+∂μv_μ=2H_γ이며, I_ν/ν³의 geodesic invariance와 일치한다. 이 항등식은 Wolfram에서 정확히 0으로 검산했다. 따라서 a³ scaling 후에도 LRS의 주파수 및 각도 flux가 남는다. 외부에서 등방 UVB를 매 시점 강제하는 모델은 외부 regulator가 있는 모형이다. 그 table을 자가 일관적인 LRS finite photon reservoir와 동일시할 수 없다.

## R5: 흡수와 에너지 모멘트의 정확한 연결

흡수 target i, threshold χ_i=hν_i에 대해

\[
\Gamma_i=4\pi\int_{\nu_i}^{\infty}\frac{J_\nu\sigma_i(\nu)}{h\nu}\,d\nu,
\qquad
\mathcal H_i=4\pi\int_{\nu_i}^{\infty}\frac{J_\nu\sigma_i(\nu)}{h\nu}(h\nu-\chi_i)\,d\nu.
\]

Γ_i는 target당 event rate이고 H_i는 초과 전자 에너지 모멘트다. 이를 전부 gas heat로 사용하는 것은 즉시 thermalization closure이다. 에너지분해 secondary 처리에서는 같은 초과 에너지를 thermal, secondary-ionization binding, excitation/radiation, unresolved 또는 escape에 나누어야 한다.

고정된 comoving reference의 proper 밀도 n_*∝a⁻³와 X_i=n_i/n_*를 사용하면 외부 moment source는

\[
\dot C_i=X_i\Gamma_i,\quad
\dot U_{\rm ext}=\sum_iX_i\mathcal H_i,\quad
\dot B_{\rm ext}=\sum_i\chi_iX_i\Gamma_i,
\quad
\dot E_{\rm import}=\sum_iX_i(\chi_i\Gamma_i+\mathcal H_i).
\]

η=ln a 적분에서는 우변을 H로 나눈다. 동일 absorption event를 internal photon reservoir에서도 차감하면서 위 E_import를 외부에서 다시 넣으면 중복이다. `mode=prescribed_moments`는 외부 import를, `mode=transported_photons`는 internal photon 감소와 실제 boundary/emissivity 공급을 사용해야 한다.

현재 source_budget의 χ_i는 **caller model registry**이다. 원 표의 수치 threshold가 확인되지 않았으므로 E_import는 이 모델의 모멘트 기반 정의이다. 실제 원 스펙트럼의 흡수 에너지 적분과 정확히 같다는 주장은 OPEN이다. 이것이 새로운 코드 단위를 가동할 수 없는 일반적 no-go는 아니다. 제한된 rate-moment 모형의 계산식과 그 스펙트럼 등가성 의무를 구분한다.

단일 Maxwell gas의 U=(3/2)k_BNT에서 N은 동일 reference당 총 gas particle 수다. 이온화 source로 \dot N=Σ_i X_iΓ_i라면

\[
\dot T_{\rm ext}=\frac{2\dot U_{\rm ext}}{3k_BN}
-\frac{T}{N}\sum_iX_i\Gamma_i.
\]

둘째 항은 입자 수 증가에 따른 변화이므로 별도로 다시 넣지 않는다. 이 식과 source energy cancellation은 Wolfram 및 제한된 Decimal 수치 검산으로 확인했다.

## R6: 두 모멘트의 정보 범위와 secondary 처리

Γ_i와 H_i/Γ_i는 흡수된 전자의 총 event rate와 평균 excess energy만 준다. 일반 에너지의존적인 secondary function의 평균은 결정되지 않는다. 구체적으로 단위 event rate에서 excess energy distribution δ(E−20 eV)와 [δ(E−10 eV)+δ(E−30 eV)]/2는 같은 zeroth/first moments를 갖지만, 진단 함수 g(E)=E²/(E+20 eV)의 평균은 각각 10 eV와 32/3 eV다. 이는 Wolfram의 유리수 계산으로 확인했다.

이 반례의 범위는 정확히 두 모멘트에서 일반 nonlinear observable을 복원하는 문제다. 실제 secondary provider의 보편적 불가능성이나 모든 closure의 실패를 주장하지 않는다. 따라서 P19의 mean excess energy에 FS10 등 secondary fraction을 한 번 평가한 것을 원 spectrum에 대한 적분으로 부르면 안 된다. 실제 spectrum 또는 명시적으로 선택한 spectral family가 있으면 그 추가 계약으로 별도 연구를 진행할 수 있다.

## Cosmic ray·원자·핵종 공급의 연결 계약

등방 CR intensity j_a(E)는 number intensity이며 j_a=v_a n_a(E)/(4π)다. 직접 impact event rate는 R_i=4π n_i Σ_a∫j_a(E)σ_ai(E)dE다. b_a(E)=−dE/dt를 사용한 연속 감속 energy transfer는 ∫n_a(E)b_a(E)dE다. 둘을 동시에 사용하면 각 b 및 σ에 어떤 채널이 포함되었는지 명시하여 중복을 제거해야 한다. secondary yield가 이미 포함된 effective ζ를 쓰면서 동일 yield를 다시 더하지 않는다.

외부 baryon 공급 S_i를 허용할 때도 n_*는 기존 fixed reference로 유지할 수 있다. 이때 \dot X_i=(R_i+S_i)/n_*이고, 각 isotope inventory는 injection/outflow를 포함하는 장부로 바뀐다. CR proton이 gas에 정지해 편입되는 과정은 energy deposition만의 문제가 아니다. proton의 핵종·rest energy·전하와 neutralizing current/동반 electron 계약이 필요하다. 아직 nonthermal reservoir에 있는 projectile을 atomic H⁺ population에 즉시 더하면 안 된다.

21 population(H1/D/T/He3/He4/Li6/Li7의 지정 charge states와 n)을 사용하는 상위 solver는 채널 mapping을 별도로 확인해야 한다. 이 provider가 아는 것은 HI/HeI/HeII 세 absorber channel이다. D/T/He3 등의 isotope 재사용, Li 외부 ionization, charge exchange, 분자 형성은 자동으로 대체되지 않는다. 미지원 채널의 값은 missing이며 0이 아니다. 별도 H/He 연구 입력을 선언하는 것은 가능하나 기존 21-population campaign과 같은 모델로 합치지 않는다.

열핵 reaction library의 Maxwellian ⟨σv⟩를 비열적 CR spectrum에 그대로 적용할 수 없다. CR spallation/fragmentation에는 projectile/target별 σ(E), fragment yield, Q-value와 fragment charge/energy가 필요하다. nuclear reaction은 baryon number와 charge를 보존하는 stoichiometry 및 질량차 c²를 포함해야 한다. beta decay에는 electron·neutrino energy와 escape를 추가한다. stellar ejecta에는 시간별 IMF·stellar lifetime·yield 및 주입 조성·에너지 정보가 필요하다. 현재 packet은 이 입력들을 확보했다고 주장하지 않는다.

중력까지 닫으려면 ∇_aT_m^{ab}=Q^b, ∇_aT_source^{ab}=−Q^b를 함께 다루거나 source를 test-fluid 외부 조건으로 명시해야 한다. u_a u^a=−c²이고 Q가 proper volume·proper time당 에너지 공급률일 때, 순수 등방 가열의 four-force density는 Q^a=(Q/c²)u^a이다. 그러면 −u_aQ^a=Q이고 spatial projection은 0이다. 비tilted gas의 energy density ε에 대해서는 \dot ε+3H(ε+p)+σ_abπ^{ab}=Q가 된다. 이번 코드에는 four-force 또는 Einstein source closure가 구현되어 있지 않다. 등방 source의 직접 momentum·tracefree stress는 0이라는 모형 조건만 사용하며, 별도 Vlasov anisotropic stress와 합치지 않는다.

## C1–C8: 구현과 실제 검사

`p19_uvb.py`는 Python 표준 라이브러리만 사용한다. Source bytes의 SHA-256, 59×8 shape, finite 값, z의 단조성, 여섯 process rate의 양수성을 검사한다. node에서는 원 float 값을 그대로 반환하고, node 사이에서는 log(1+z)에 대해 log(rate)를 선형 보간한다. 같은 endpoint rate가 있는 plateau는 원 값을 그대로 반환한다. Source 범위 밖, NaN/Inf, 누락·추가 channel, 음의 population, invalid binding registry는 명시적으로 거부한다. Z=20 입력도 거부한다.

초기 검증에서는 plateau에 exp(log(rate))를 적용해 두 상수 구간이 몇 ULP 변하는 구현 문제가 발견되었다. `p19_uvb_attempt1.py`, `validate_p19_attempt1.py`, `P19_VALIDATION.json`의 FAIL을 보존하고 constant branch를 추가했다. Physical rate와 수용 tolerance는 바꾸지 않았다. 수정 뒤 `P19_VALIDATION_v2.json`은 18개 검사 PASS_SCOPED이며, 348 midpoint rate의 60-digit Decimal 기준 대비 최대 상대차는 9.26521480112809e−15였다. 모든 354 node rate는 binary64 identity가 같았다. CPU4, native thread1, wall 0.21665 s, ODE0이다.

환경 실패로 BeautifulSoup import가 없었던 기록을 보존하며, stdlib HTMLParser로 같은 원문 Table3를 읽어 해결했다. WolframContext의 INTERNAL ERROR도 보존했고, 직접 evaluator의 실제 성공 결과를 별도로 기록했다. 추가 검증은 상위 독립 검토의 구체적 finding을 처리할 때만 수행한다.

## R8–R10 / C9–C10: 인계와 다음 진입점

채택 가능한 다음 단위는 (a) source-supported 0≤z≤15.1에서의 actual moment-array operator 검증, (b) 명시적 H/He inventory 및 외부 regulator를 둔 새 gas pilot이다. 전체21 species·self-consistent radiation·secondary spectrum coupling은 각각 입력 의무를 충족한 뒤 확장한다. 온도 독립적인 외부 rate table이라고 해서 gas cooling/CI/RR provider의 T 유효범위가 사라지지 않는다. 기존 C22D의 온도 계약은 실제 선택한 gas module에 따라 별도로 확인한다.

`EXECUTION`: 원자료 회수·기호 계산·18개 제한 검증 완료; ODE0.
`PUBLICATION`: parent integration pending; 외부 write0.
`BACKUP`: 이 packet은 현재 로컬 파일이며 parent delivery에서 실제 ACK/ID와 연결해야 함.
`DAG`: source/provider 계약 READY; 독립 검토 및 새 가스 입력 승인→실행→분석→게시/보존. Spectrum/threshold/isotope mapping과 nuclear/stellar 공급 의무 OPEN. global_error_bound=null.
