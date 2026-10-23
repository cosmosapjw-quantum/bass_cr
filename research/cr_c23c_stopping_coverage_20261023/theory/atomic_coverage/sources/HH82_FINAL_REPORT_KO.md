# PHYS82 최종 과학 보고: Li7 문턱 source-gap의 조건부 Maxwell closure

## 1. 완료한 연구와 판정

PHYS81 실제 최종 HEAD `b3ec271a96cb67e583bffa9b61533802838236f9`에서 이어, Li7 chemical threshold–6 eV 구간의 source 근거를 보강하고 다섯 조건부 단면적의 Maxwell rate·반응 가중 에너지·온도 도함수·고정 노출 민감도를 유도하고 구현했다. 기존 CCC 6–15 eV의 13개 knot는 변경하지 않았다. 문헌의 finite-resolution 선형 기울기를 별도 비교 모델로 보존했다.

**새 과학 실행 1시도=1완료+0실패.** 72개 온도에서 새 gap 평가360, 기존 finite operator의 새 온도 평가63, 저장 baseline 재사용9, 총 rate 조합360, 고정 노출 결과1080을 보존했다. 동일 scientific identity 재개1회는 `SKIPPED_IDENTICAL_COMPLETE`, scientific callback0이다. 새 ODE0, benchmark0, 과거 완료 identity 재실행0, 다른 process 종료0이다. 독립 검증1924assertions는 미해결 실패0이며 source 정확도와 수치 구현의 판정을 분리했다.

이번 단원의 지위는 **COMPLETE_SCOPED / conditional source sensitivity**다. 실제 isotope-resolved unsmeared 단면적의 uncertainty enclosure 및15eV 위 tail은 OPEN이다. 완성된 연구 루프를 전체 collisional atomic/thermal model의 완성으로 바꾸어 부르지 않는다.

## 2. 최신 identity와 외부 결과 재사용

현재 조사 범위는 2026-10-23 11:22–11:25 KST의 관련6repo 최신 갱신PR 각5개, 별도 actual branch ref와 changed commit 비교, PHYS81 두 provider 전달 metadata다. Connector read39회와 고정 원격 텍스트16개를 보존했다. 기존51repo/2175branch inventory는 재사용하고 현재 bounded delta를 대조했다. 접근 불가능한 private conversation 또는 live external host 전수 확인을 주장하지 않는다.

| 대상 | 관측 identity | 실제 재사용 판정 |
|---|---|---|
| WU088_HH PR137 | b3ec271a96cb67e583bffa9b61533802838236f9 | 실제 부모와 AGENTS byte identity 일치 |
| BASS_HE PR90 / HE37 | d618344413193950ec3e4e499be526d1ed636d98 | H1 differential gain/net source의129T 및7bridge producer evidence; electron infinitesimal Grad STF이며 gas STF 아님 |
| bass_cr PR96 / C23A | 215defe6f631050255b73baec83e9418a8a2b66f | science7643af28의 P19H/He, FS2010finite, beta조건부 coverage; 전달 metadata descendant |
| REI PR221 / ANGTHERM01 | 00303ab27c33a7afa0cec61679af78ef72e3f4aa | PREPARED_INPUTS_ONLY; 새IVP0 |
| REC126 | 12068893fab749ae1efb513563d0a86cc1cf649f | 저장512상태C2; C3handoff만, 새 post-PHYS81 과학으로 중복 집계하지 않음 |

이 결과들은 Li7의 실제 threshold gap을 대신 채우지 않는다. HE37의 무한히 무거운 표적/등방 outgoing, C23A P19의 z0–15.1 및H/He 범위, FS2010의 finite energy/source coordinate를 유지한다. 자세한 비교는 inventory/CURRENT_INTAKE_KO.md 및 CURRENT_REFS.json이다.

## 3. 원문 사실과 채택한 다섯 모델

Zapesochnyi–Aleksakhin1969 원문 printed p44의 Li 항목은 threshold5.39eV, resolved linear interval3.4eV, slope mantissa0.9 및 peak4.2e-16cm²를 준다. p42의 final monochromator spread는 전자의90%를 포함하는0.1eV이며, p43의 energy-axis uncertainty0.1–0.2eV와 다른 양이다. 헤더의 cm^-2/V 인쇄는 literal로 보존하고 cross-section 정의에 따라 cm²/eV로 해석했음을 기록했다. 정오표를 발견했다고 주장하지 않는다. [S1]

원문의 absolute±15%, threshold relative≤3%는 pointwise slope covariance 또는 isotope별 confidence interval이 아니다. Energy-response 함수, deconvolution, isotope assay와 정량적 excited-state purity가 없으므로 실제 Li7 무한분해능 곡선으로 승격하지 않았다.

Wannier의 원논문은 neutral atom의 약1.127 exponent와 비엄밀 ergodicity 가정을 명시한다. 정확 radical은 Friedrich–Ihra–Meerwald1999 Eq2의 residual chargeZ=1을 사용했다. Peterkop–Tsukerman1970은 alkali 비선형 threshold 영역이 당시 분해능보다 좁을 가능성을 논한다. 실험의 resolved linear interval과 엄밀한 threshold 극한은 서로 다른 명제다. [S2–S4]

고정값은 $I=5.39172060034581\,\mathrm{eV}$, $E_0=6\,\mathrm{eV}$, $\Delta=E_0-I=0.6082793996541902\,\mathrm{eV}$, $\sigma_0=5.18148\times10^{-17}\,\mathrm{cm^2}$다. I는 PHYS81이 확인한 Li7 chemical defect를 재사용한다. Stationary-target/electron-mass Maxwell convention에서 incident threshold로 쓰며 finite-mass recoil threshold correction을 새로 인정하지 않는다.

$$\sigma_{p,q}(E)=\sigma_0\left(\frac{E-I}{\Delta}\right)^p\left(\frac{E_0}{E}\right)^q,\qquad I\le E\le E_0,$$
$$p_W=\frac{\sqrt{91/3}-1}{4}=1.1268926368215255\ldots.$$

| 모델 | p | q | amplitude 계약 |
|---|---:|---:|---|
| L0 |1|0| CCC endpoint 고정; 정확한 한 PL cell |
| L1 |1|1| 같은 endpoint, smooth1/E factor |
| W0 |pW|0| Wannier 형태를 gap 전체까지 연장한 가설 |
| W1 |pW|1| 같은 asymptotic 가설과 smooth factor |
| ZA1969 |1|0| 원문 slope9e-17cm²/eV를 부모 I로 재중심화; CCC로 재정규화하지 않음 |

ZA1969의 6eV amplitude는 5.474514596888e-17cm², CCC 대비 1.056554227149배(+5.6554%)다. 이 mismatch는 원자료 간 진단으로 남겼다. 동일 shape이므로 ZA/L0 gap-rate ratio는 모든T에서 이 amplitude ratio다. 네 matched-model envelope에 ZA를 포함시키지 않는다.

IAEA D107424는 Wutte/Lennon 계열 rounded Bell-like fit이며 새 pointwise gap 측정이 아니다. ADAS type1의 좌표는 E/I이고 nominal-threshold 다음 sample1.15가6eV 위다. Type3 scaled rate는 local cross section으로 역변환하지 않았다. Younger의 distorted-wave 저에너지 불일치와 Schweinzer 원문 fulltext 미확보도 source contract에 남겼다.

## 4. 물리 구조를 이용한 계산 단순화

$\theta=k_BT$와 $z=\Delta/\theta$에서 양의 moment를 정의한다.
$$F_j(p,z)=\int_0^1 t^{p+j}e^{-zt}dt=\frac{\gamma(p+j+1,z)}{z^{p+j+1}}.$$

$C=100\sqrt{8\,\mathrm{eV_J}/(\pi m_e)}$를 쓰면 q=0의 rate와 반응 가중 평균은
$$K_g=C\sigma_0\Delta\theta^{-3/2}e^{-I/\theta}(I F_0+\Delta F_1),$$
$$\mu_g-I=\Delta\frac{I F_1+\Delta F_2}{I F_0+\Delta F_1}.$$

q=1에서는 Maxwell flux의 E와 단면적의1/E가 상쇄되어
$$K_g=C\sigma_0E_0\Delta\theta^{-3/2}e^{-I/\theta}F_0,\qquad\mu_g-I=\Delta F_1/F_0.$$

온도와 무관한 cross section 및 고정된 energy 경계에서는 $d\log K/dT=(\mu/\theta-3/2)/T$가 정확하다. Gap과 table은 logaddexp와 양의 rate weights로 합친다. Small-z에서는 양의 급수, 그 외에는 regularized incomplete gamma를 쓰며 log-domain에서 exponential reference를 보존한다. 수치 quadrature는 독립 검증에서만 사용했고 과학 profile의 각 rate에는 호출하지 않는다. 이 구조적 절감에 실제 wall-time speedup 주장을 붙이지 않는다.

공통 thermal pool로 outgoing kinetic energy가 돌아오는 사건 회계는 $-\mu+(\mu-I)=-I$다. 반응 가중 입사 에너지를 별도 cooling으로 빼지 않는다. 이온화로 증가한 particle count의 EOS 효과는 별도 의무다. Parent geometry나 reacting-gas anisotropic stress를 갱신하지 않았다.

조건부 rectangle $p\in[1,p_W],q\in[0,1]$에서 양의 kernel에 의해 $K_{\rm tab}+K_{W0}\le K_{\rm tot}\le K_{\rm tab}+K_{L1}$이다. 이 수학적 envelope는 물리적 신뢰구간이 아니다. 같은p에서 $1<K_{p,1}/K_{p,0}<E_0/I$도 성립한다. 자세한 차원·경계·저온/고온 극한 및 mean-order 증명은 theory/THRESHOLD_CONSTRUCTION_KO.md에 있다.

## 5. 새 과학 결과

아래 범위는 네 matched 모델의 W0–L1 envelope다. Rate는 gap+기존6–15eV table을 합한 finite operator의 값이다. 그 밖 실제 단면적이0이라는 의미가 아니다.

| T [K] | Ktotal 범위 [cm³/s] | Ktotal / Ktab | 전체 finite rate의 gap 비중 |
|---:|---:|---:|---:|
| 255 | 8.7856759e-116 – 1.3930203e-115 | 2.3374326e+10 – 3.7061361e+10 | 100% – 100% |
| 1000 | 5.1797681e-36 – 6.7388498e-36 | 115.01141 – 149.62921 | 99.1305% – 99.3317% |
| 3000 | 1.3489454e-17 – 1.4918922e-17 | 2.967197 – 3.2816285 | 66.2982% – 69.5273% |
| 10000 | 5.9316511e-11 – 6.0307315e-11 | 1.1700056 – 1.189549 | 14.5303% – 15.9345% |
| 25370.663 | 4.2031561e-09 – 4.2163133e-09 | 1.0307055 – 1.0339319 | 2.97907% – 3.28183% |
| 50000 | 1.4078383e-08 – 1.4095459e-08 | 1.0120247 – 1.0132522 | 1.18819% – 1.30789% |

**부모의 실제 Tmax=25370.66308424773K에서** matched 모델의 gap 추가는 기존 finite rate 대비3.07055–3.39319%다. ZA1969는3.45822%를 준다. 반면255K에서는 enhancement가2.3374e10–3.7061e10배지만 절대K가8.7857e-116–1.3930e-115cm³/s다. 따라서 큰 상대비율 하나로 실제 이온화 영향이 크다고 판단하지 않는다.

네 matched 모델 간 최대 비율은 현재 격자에서255K의1.58555847배다. Tmax에서 upper/lower 비율은 약1.00313배다. 이는 선택한 amplitude/shape family의 민감도이며 실제 source 오차의 상한이 아니다. ZA가 일부 온도에서 matched upper rate보다 큰 것도 그 경계의 조건부 성격과 일치한다.

## 6. 고정 노출량의 절대 효과

외부에서 T와 전자 노출량 $\Lambda=n_e\tau$를 지정하면 $P=1-e^{-\Lambda K}$다.
$$\Delta P=e^{-\Lambda K_{\rm tab}}[1-e^{-\Lambda K_g}]\le e^{-\Lambda K_{\rm tab}}\min(1,\Lambda K_g).$$

낮은T에서는 gap/table 비가 지수적으로 커져도 둘의 절대rate가0으로 가므로 유한Lambda의DeltaP도0으로 간다. 같은 prescribed history에 대한hazard적분으로 확장할 수 있으나 coupled T/xe의 다른 history에 이 경계를 옮기지 않는다. 아래는 각 모델의 **저장72점 격자 최대값**이며 연속T의 최적화 결과가 아니다.

| Lambda [cm⁻³ s] | W0 최대 DeltaP (T K) | L1 최대 DeltaP (T K) | ZA1969 최대 DeltaP (T K) |
|---:|---:|---:|---:|
| 1e+09 | 0.0243428229 (15758) | 0.0269199885 (15758) | 0.027393622 (15758) |
| 1e+11 | 0.0819264043 (8146.05) | 0.0910216806 (7501.15) | 0.0922741114 (7501.15) |
| 1e+13 | 0.159532746 (4966.29) | 0.177641319 (4966.29) | 0.179409756 (4966.29) |

Lambda1e13에서 약0.178의 L1 최대 increment는18%의 rate error라는 뜻이 아니라 이 prescribed-exposure 모델의 이온화 확률 차이(약17.8 percentage points)다. Lambda는 관측된 우주론 전자 노출에서 추정하지 않았으며, 선택한 진단 변수다.

## 7. 검증, 실행 identity 및 실패 기록

| 검증 | 최대 관측 오차 | gate |
|---|---:|---:|
| Gamma-free QAWS gap K |1.4142509577352486e-14 상대|1e-10|
| 새14-knot PL 대응 K |5.697880933875216e-14 상대|1e-10|
| logK finite-difference |6.615020692129179e-10 scaled|1e-7|
| K finite-difference |4.2895300314704e-9 scaled|1e-7|
| Fixed-exposure DeltaP |7.93867395428653e-13 상대|1e-10|

독립 reference는 production gamma 함수를 호출하지 않는 QAWS endpoint-weight 적분108개다. 새gap평가150, total합150, 새검증온도baseline27, 한PLcell6, joinedPL6을 구별한다. 본 과학 grid의360/63과 중복 집계하지 않는다. 80개 malformed-input guard,17개 immutability assertion,2개 synthetic skip 및5개 rejection에서 science callback0을 확인했다.

첫 검증 실행은 모든 수치 matrix를 통과한 다음 verifier label의repr(b) NameError로 중단됐다. 이 예외와 그로 인한 callback-accounting mismatch 두 기록을 보존했다. 원코드·diff·전후SHA를 남기고 미완료 guard/control만 실행했으며 completed numerical assertion 재실행0이다. 합성판정은1924assertionsPASS_SCOPED다. Wolfram의 네 symbolic residual0과 binary64 수치 검증을 별도로 기록했다.

Science identity: `caae042b139373a10c516d759854ad117d807e9f7ace8c365529a1621419b73f`. source·input·runtime이 identity에 결속된다. 실제 완료 파일 및 create-only sidecars는 results/THRESHOLD_STUDY.json*과 results/IDENTITY_CLAIMS에 있다. 실제 resume는 저장 결과를 검사하고 scientific callback0으로 skip했다. 같은filename뿐 아니라 다른filename도 완료identity를 재실행하지 못하도록 구현했다.

각 실행은 부모와 동일한 byte-pinned cooperative lease,0.5GiB와1thread를 사용했다. Matplotlib은 기본 cache 경로가 읽기 전용이라 임시/tmp cache를 자동 사용했고 render는 exit0으로 완료됐다. 그림을 재실행하거나 이 경고를 과학 실패로 세지 않았다. 셋의PNG를 직접 육안 점검했으며 대응PDF도 생성했다.

## 8. 그림과 재사용 진입점

- figures/01_rates_and_enhancement.png 및.pdf: 절대 rate와 상대 enhancement.
- figures/02_gap_fraction_and_energy.png 및.pdf: gap비중과 reaction-selected excess energy.
- figures/03_prescribed_exposure.png 및.pdf: 고정노출 probability와 conditional sensitivity.
- source/threshold_gap.py: `named_models`, `evaluate`, `combine_rates`, `fixed_exposure`.
- source/run_study.py: pinned saved9baseline 재사용과 create-only science identity.
- source/plot_study.py: 저장배열만 읽는3종 후처리.

기존 결과가 있는 checkout에서 runner는 skip해야 한다. 새 물리질문이나 input 변경이 없는 같은identity를 지우고 재실행하지 않는다. 실제 신규실행 전 currentrefs·source계약·sharedlease를 먼저 확인한다.

## 9. 전체 목표와 다음 선택 DAG

이 단원은 Li threshold source 사실/조건부 positive Maxwell reduction/독립 구현 검증/새 민감도 grid를 닫았다. LOW_T_CI_SOURCE_COVERAGE와COLLISIONAL_ATOMIC_AND_THERMAL_CLOSURE는PARTIAL이다. 전체목표의 분모가 고정되지 않아 임의완성도%를 주지 않는다.

다음 원자 단원은 BOUND_BOUND_CE_AND_RADIATIVE_COOLING의 primary strength/state/branching 및 radiation-energy 계약이다. He/LiCX source/product/photon-energy는 병렬 열린 가지로 유지한다. Li의 instrument response와 isotope/target-state uncertainty는 실제자료 또는 명시한forward-convolution 연구로 이어가되, 이번곡선을 다시 계산하는 작업으로 대체하지 않는다. 핵쪽은 부모의 radiative-capture recoil 사건회계를 thermal/fast particle-number ownership 및 finite-T event averaging과 먼저 연결한다. 새 nuclear rates/stopping은 활성화하지 않았다.

RECOMBINATION_TO_Z20_INITIAL_CHARGE_CONTRACT, D_PI_RR_MATCHED_SOURCE_MOMENTS, LI_HARD_UV_INNER_SHELL_SPECTRAL_CONTRACT, FULL_GEOMETRY_SPECTRAL_BACKREACTION은OPEN이다. Non-tiltedLRSBianchiI, signed same-normal-frame tensor합 후norm, Frobenius=sqrt2×half-contraction, reactinggaspi0/collisionlessDMpi_m 분리는 유지했다. 동일trajectory의 species 성분분석을 causal species-off 실험으로 부르지 않는다.

**HH_R10=OFF. Production admission NOT_ISSUED.** 이번 단원 뒤 다음 단원을 자동 시작하지 않는다.

## 10. 게시·백업과 최종 전달 권위

Draft PR138은 실제PHYS81 부모의 additive descendant다. S0 intake와S1 verified-code checkpoint를 게시하고 양쪽 provider 업로드ACK를 보존했다. S2 science와최종meta는 delivery/PUBLICATION_HISTORY.json에 분리한다. ACK와fullrawrestore는 별개의 상태다. 최종HEAD·ZIP SHA256·두providerIDs·CRC/payload/Gitblob 검증과 finalJSONreadback의 확정권위는 외부 PHYS82_FINAL_DELIVERY_20261023.json 및PR138 최종본문이다. 이 파일은 자기 commit hash나 archive hash를 자기 안에 넣는 순환구조를 만들지 않는다.


## 최종 Git byte 복구

최종 원격 blob 대조에서 PHYS81_LITERAL.csv 하나의 CRLF가 초기 text export에서 LF로 바뀐 사실을 확인했다. 로컬 과학 입력과 S0/S1/S2 백업 payload는 원본 bytes를 유지했으므로 저장 과학 결과와 scientific identity는 변하지 않았다. 원격 source pin은 변환된 CSV의 실행을 거부한다. 원본 bytes를 base64 Git blob으로 복구하는 추가 descendant를 만들고 최종 원격 전체 파일을 대조했다. delivery/TRANSPORT_BYTE_REPAIR.json이 관측된 이전 blob과 정확한 원본 identity를 기록한다. 과학 결과 commit6a5c5a48만 checkout하지 말고 외부 final-delivery JSON이 가리키는 최종 HEAD를 사용한다. 새 과학 실행0이며 final archive가 이 복구를 포함한다.

## Primary sources

- [S1] Zapesochnyi & Aleksakhin, Sov.Phys.JETP28,41–45(1969): https://jetp.ras.ru/cgi-bin/dn/e_028_01_0041.pdf (원본bytes SHA와 pixel provenance는source contract).
- [S2] Wannier, Phys.Rev.90,817(1953), original public abstract: https://doi.org/10.1103/PhysRev.90.817 (fulltext는 접근벽을 존중).
- [S3] Friedrich,Ihra,P.Meerwald, Aust.J.Phys.52,323–339(1999), Eq2: https://doi.org/10.1071/PH98091 (primary web-extracted equation 보존, originalPDF bytes 미확보).
- [S4] Peterkop & Tsukerman, Sov.Phys.JETP31,374–376(1970): https://jetp.ras.ru/cgi-bin/dn/e_031_02_0374.pdf .
- [S5] Bell etal1983, Eq1/Table5: https://doi.org/10.1063/1.555700 ; 실제계수와온도profile은PHYS81재사용.
- Curtin CCC author database: https://atom.curtin.edu.au/ccc-db/index.html ; Li13rows와원sourcehash는PHYS81 literal에결속.
