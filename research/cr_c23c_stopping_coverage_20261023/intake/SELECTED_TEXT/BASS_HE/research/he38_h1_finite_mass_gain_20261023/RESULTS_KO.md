# HE38 결과 — H1 CI의 유한질량 반동과 종별 heat/STF

## 1. 이번 단원에서 닫은 범위

HE37의 heavy-target H1 gain을 **원전 Jacobi 좌표의 유한질량 모형**으로 확장했다. 전자·중성 수소·양성자의 생성/소멸, kinetic-energy source와3×2STF 응답을 연결했고, 사건별 momentum/energy 보존 및 Maxwell–Grad 선형화와 일치하는 코드를 저장했다. Workflow1.0.0 / approval0.2, 이론R1–R10→코딩C1–C10의20단계다. 각 단계의 실제 전달 상태·commit·archiveACK는 DAG.json과 delivery/*_ACK.json에 있다.

채택한 것은 **명시적인 물리 근사모형**이다. 원전의 정확한 운동학 위에 original Jacobi 방향의 독립 uniform density를 둔다. Common temperature/common bulk Maxwell 기준과 독립적인 무한소 electron/H0 STF를 사용한다. 실제 H1 angular distribution의 교정, 유한 비등방 분포, 서로 다른 온도/상대속도, totalgas stress closure는 이번 완료 범위 밖이다.

HE32의8핵종21상태 prescribedUV photo+caseA RR pilot,392nominal+2angular-guard IVP,그림6쌍은 완료 근거를 재사용했다. HE32 gasπ_b=0과 nonbaryonic matter stress의 구분을 유지한다. **기존 IVP/suite/diagnostic/provider-benchmark/render 재실행0, 이번 새IVP0**이다.

## 2. 최신 변경 자료와 원전 재사용

이전 cutoff2026-10-23T02:05:02.183087Z 이후를 조사했다.7repo의 advertised branch1285개를15페이지로 읽고, 추가4·tip변경2·삭제0을 확인했다. Updated PR metadata290행에서 cutoff이후9개를 선별했고, 선택comment collection9개와 새댓글7개를 읽었다. 고정source text15개/170926bytes는 모두 Git blob SHA1과 일치했다. Dropbox의 새ADD33개 중 선택ZIP5개의 metadata를 확인했다. 해당 기존ZIP전체를 다시 내려받았다고 주장하지 않는다.

새 PHYS82 Li CI, REC LINE01, REI ANGTHERM01, BASS background recovery, CR C23B 계약을 대조했다. 특히 조사 중 바뀐 C23B pin54477b285e0c712610453bca1408a076af43521d까지 반영했다. 이 자료들은 source/frame/energy ownership 또는 후속 열·광원·핵채널에 유용하지만 H1 correlated finite-mass CI의 직접 donor는 아니다. 원문권위와 제한은 evidence/intake/INTAKE_REPORT_KO.md에 있다.

Personal Context를 이번에 실제 조회했지만 unavailable 응답이었다. 따라서 과거 private 대화 전수조사를 했다고 기록하지 않는다. 기존 Le–Cambier PDF, HE36 incoming loss/REI event lift, HE37 radial source와129T저장행은 identity를 확인하고 재사용했다. 새 문헌 검색은 SciSpace/Exa primary qualification으로 기록했고 Wolfram은 새 유한질량 대수 항등식7개를 독립 확인했다.

기준 원전은 Le & Cambier2016, Physics of Plasmas23,063505, DOI[10.1063/1.4953050](https://doi.org/10.1063/1.4953050), [arXiv1605.06545](https://arxiv.org/pdf/1605.06545) Eq2–7,11–12,85 및 §III.E다. Mass는 공식 [NIST CODATA2022](https://physics.nist.gov/cuu/pdf/wallet_2022.pdf)를 사용했다. Threshold13.6eV는 source convention을 유지하며 정밀 분광값/CCC normalization으로 교체하지 않았다.

## 3. 유한질량 사건과 공유 적분의 축약

전자 질량m,양성자 질량M,중성종 운동학 질량h=M+m,사건 전체 질량L=M+2m를 둔다.

\[
\eta=m/L,\quad\zeta=h/L,\quad d=m/h,\quad f_p=M/h=1-d,\quad\mu=m\zeta,\quad\theta=k_BT.
\]

원전의 입력 상대에너지는E=μg0²/2이고, 최종 Jacobi 에너지는μg1²/2=E−Υ, μ_tg2²/2=Υ−I다. 출력 속도를

\[
v_1=V+\zeta g_1,\quad v_2=V-\eta g_1+f_p g_2,\quad v_p=V-\eta g_1-dg_2
\]

로 구성하면 momentum은 사건마다 보존되고 kinetic energy는 사건마다I만큼 감소한다. Ionization internal reservoir가+I를 한 번 받는다. 이는 Newtonian mass-additivity convention이며 binding mass defect를 relativistic restmass로 처리한 모형은 아니다. Lab electron energy와E를 혼동하지 않는다. Stationary H target에서는E=ζE_lab이다.

선정한 source law는

\[
\sigma(E)=4\pi a_0^2I(E-I)/E^2,\qquad
p(\Upsilon|E)=IE/[(E-I)\Upsilon^2],\quad I\le\Upsilon\le E.
\]

원래g1,g2방향에 uniformG=1/(16π²)를 명시적으로 적용한다. Final lab velocities는 momentum conservation 때문에 상관된다. 두 전자는한 사건의 두 출력으로 합하며 extra2나1/2 factor를 넣지 않는다.

K=gσ, α=〈K〉, β=〈EK〉, γ=〈E²K〉라 두면, conditional transfer mean은 IE log(E/I)/(E−I)다. Source-weighted Maxwell measure에 곱해 부분적분하면

\[
\boxed{\Lambda=\langle K\bar\Upsilon\rangle=\beta-\theta\alpha,\qquad U_1=\theta\alpha,\qquad U_2=\beta-(I+\theta)\alpha.}
\]

이 식은 채택한 σ와 transfer law를 함께 쓴 결과다. 일반 CI에 보편적으로 적용하는 식이 아니다. 원래2차원 공유 적분을 생산 코드에서 없애고 기존 α,β로 계산한다. 같은 source의 radial moments는 기존 HE37값에ζ^(-1/2)를 곱하면 된다. Near threshold에는log1p를 사용하고 작은U2 차감은 production heat에 필요하지 않도록 식을 정리했다. Positive H(x)=x∫₀∞t exp(−t)/(x+t)²dt가독립 oracle다.

## 4. 종별 에너지와 비등방응력

사건률r=n_e n_H α이다. 직접 구현한 종별 에너지는

\[
Q_e/(n_en_H)=(3\eta/2+2\eta d)\theta\alpha-\eta d\beta-f_pI\alpha,
\]
\[
Q_H/(n_en_H)=-3\zeta\theta\alpha/2-\eta\beta,
\]
\[
Q_p/(n_en_H)=[3(\zeta-\eta)/2-2\eta d]\theta\alpha+d\beta-dI\alpha.
\]

합은정확히Q_total=−Ir다. 작은heavy합은Q_H+Q_p를 큰 두 수의 차로 만들지 않고 별도 직접식으로 반환한다. 아래 값은사건당eV이며, 양의양성자항은생성입자의kinetic moment다. 기존양성자의열평형화율이라는해석은하지않는다.

| T(K) | Q_e/r(eV) | Q_H/r(eV) | Q_p/r(eV) | (Q_H+Q_p)/r(eV) |
|---:|---:|---:|---:|---:|
| 2,000 | -13.592460625 | -0.265963347 | +0.258423972 | -0.007539375 |
| 20,000 | -13.591194766 | -2.592903484 | +2.584098250 | -0.008805234 |
| 200,000 | -13.578534262 | -25.858786090 | +25.837320352 | -0.021465738 |

\(\kappa_1=2\beta/(3\theta)\),\(\kappa_2=4\gamma/(15\theta^2)\)와

\[
A=\eta^2\alpha+2\eta\zeta\kappa_1+\zeta^2\kappa_2,\quad
B=\zeta^2\alpha+2\eta\zeta\kappa_1+\eta^2\kappa_2,\quad
C=\eta\zeta(\alpha-2\kappa_1+\kappa_2)
\]

를사용하면전체종별STF사상은

\[
\begin{pmatrix}J_e\\J_H\\J_p\end{pmatrix}=
\begin{pmatrix}
n_H(2\eta^2\alpha-A)&n_e(2\eta\zeta\alpha-C)\\
-n_HC&-n_eB\\
n_H\eta(\zeta-\eta)\alpha&n_e\zeta(\zeta-\eta)\alpha
\end{pmatrix}
\begin{pmatrix}\pi_e\\\pi_H\end{pmatrix}.
\]

합은

\[
\boxed{J_{\rm total}=-\kappa_2(n_H\zeta\pi_e+n_e\eta\pi_H).}
\]

이식은일반적인−νπ_b closure가아니다. Electron,H0,proton stress의배분과다른충돌/수송을정해야전체gas stress를진화시킬수있다. 전자의입력만있을때,같은T의HE37에대한totalSTF계수비율은√ζ이고반응률비율은ζ^(-1/2)다.

| 변화 | 이번 값 |
|---|---:|
| η | 0.0005440244515373176 |
| ζ | 0.9994559755484628 |
| α_finite/α_HE37 | 1.000272123262085, +272.123262ppm |
| electron-only totalSTF coefficient ratio | 0.9997279507688392, −272.049231ppm |

수치원본은 components/diagnostic/outputs/METRICS.json 및 finite_mass_moments.csv/npz다. 전체129T에서 에너지합의 최대부동소수점잔차는5.3291×10⁻¹⁵eV였다. 이잔차는모형의물리오차를추정한값이아니다.

## 5. 물리에 기반한 비용 절감

동일한129개Λ출력에대해,기존모멘트로계산하는β−θα와양의relative-energy Laguerre128×transfer-CDF Legendre128적분을비교했다. Nodes와radial moments는두경로모두미리준비한상태다.

| 항목 | 관측값 |
|---|---:|
| 압축식 중앙값 | 1.368804μs /129outputs |
| 지정2D quadrature 중앙값 | 22.206737ms /129outputs |
| 지정참조대비비율 | 16223.4600 |
| 상대차최대 | 1.9984×10⁻¹⁴ |
| 고온128²→192²변화 | 2.8866×10⁻¹⁵ |

7 timing batches를사용했다. 비율은**이추가sharing contraction의지정수치참조대비국소비교**다. 전체provider,IVP 또는가능한모든적분법대비속도향상으로확장하지않는다. 성능효과의핵심은새적분차원자체를제거한것이다. 이작은O(N_T)경로에는현재native compiler나GPU설치가필요하지않다.

## 6. 실제 검증과 남긴 시도

| 검증 | 실제 범위 | 결과 |
|---|---|---|
| 독립 유도 exact/Wick | 3질량비,108사건,90종별STF tensors | Exact residual0 |
| Transfer-only65자리적분 | E/I3점,x3점 | 최대상대잔차1.90×10⁻⁶⁵ |
| Wolfram 대수 | 7 rational-polynomial identities | 모두0 |
| 새구현 affected controls | 107개,12float events 포함 | PASS |
| 별도 interface probe | tinySTF와fully-ionized boundary2개 | PASS |
| 독립 raw integral | 3T+hotrefinement,48tensorblocks | 전case최대상대1.3464×10⁻⁹;선택fine3T최대STF5.4812×10⁻¹² |
| 새로운finiteM진단 | 129T, APIbatch1회 | PASS |
| 실제그림 | 고유1쌍,render2회 | 원본제목교정1회뒤actualview PASS |

Raworacle는원래incoming Maxwell/Grad weights와7,838,208개의outgoing velocity triples에서생성한dyad를사용했다. 닫힌species응답식을복사하지않고raw결과를저장한뒤production을import해비교했다. Coarse→fine차이는관측된수렴이며rigorous bound가아니다.

구현control CPU0.918811s,별도probe CPU0.848680s,rawwhole-child CPU5.977551s다. Theory2.538973s는elapsed wall값이며CPU로바꿔표현하지않는다. 진단과두render의합계CPU17.277931s,최대RSS83392KiB로30s/512MiB예산안이다. Raw내부timer와childtimer를중복합산하지않는다.

F1은direct wrapper.J와nested donortraceprojection구별을문서화해닫았다. F2는실행원본15파일을보존한채명시경로/고유attempt/hardlimit을받는portableentry로닫았다. 새portableentry는정적검사만거친PREPARED_NOT_SCIENCE_EXECUTED다. F3는동일CSV/metrics에서제목위치만교정하여닫았다. Independentreview는open/blocker0으로끝났다. C1backup의FETCH_FAILED1회는동일sealedarchive재전달로해결했으며과학재실행을유발하지않았다.

## 7. 구현과 물리적 사용 경계

FiniteMassModel.evaluate는immutable α,β,γ,δ,공유모멘트,종별heat,3×2STF계수를반환한다. finite_mass_source는독립π_e,π_H에서종별/직접total을계산하고event_kinematics는원전속도변환으로사건을구성한다. h1_ci_source는pureH21의H0slot1/H+slot2와ne=nB Yp를유지한다. 원자료6파일은byte-preserved donor다.

Physical fixedT,nB abundanceJacobian은ne(Y)미분을포함하며frozen-ne donorJacobian과구별한다. 내부heat,sumQ,wrapperQ,dEth는하나의owner다. 모든입자retainedthermal scope를명시했을때만reaction dotT를반환하며이선언으로실제thermalization이증명되지는않는다. SignedSTF를fullpressure에서trace빼기로복구하지않고directJ를읽는다.

## 8. 전체 목표와 다음 DAG

완료된것은선정H1 source모형의finiteM instantaneous component다. 전체목표에는교정된원자/핵반응망,진화하는T/UV,바리온비등방응력과metric/source feedback이남아있다. 모든unstable isotope,음이온,분자또는fullyreactive19채널핵망을완료한것으로해석하지않는다.

NEXT_DAG.json은HE37 N0/N1/N1M 및선정H1 N2를조건부완료로갱신했다. 남은angular provider,종별elastic/thermalization coefficients,공통T/u와totalgasstress closure,T/UV/sourcecensus,추가atomic/nuclear source와newcoupledIVP를서로의의존성으로표시한다. 종과적용domain이아직고정되지않은전체목표에unit20/20을퍼센트로환산하지않는다.

다음연구는최신cutoff2026-10-23T03:46:44.729Z 이후변경분부터읽는다. 우선H1 angular calibration또는H1종간수송/열화계수중실제primarydata가admission되는한track을선택한다. Source가모형조건부이면그수준을유지하고,동일HE38계산을새성과로다시실행하지않는다. 미래수치HE번호는동시branch확인후부여한다.

## 9. 게시·백업·재개

Science manifest는현재과학payload를고정한다. DAG와각stage의payloadmanifest/ACK는그시점의snapshot을가리킨다. C10과최종archiveACK뒤의metadata게시에는모든20stageACK와두handoff를포함한다. Commit자체SHA를같은commit내용에넣을수없으므로sciencepin,finalarchive,publicationreadback을구별한다.

복원후verify_saved.py --require-delivery만으로저장파일·receipt를확인한다. 새stage tar들이로컬에있으면--archives로그payloadhash를확인할수있다. 이것은과학적재실행이아니다. Exactpins,archiveSHA/DropboxID와단계별진척은delivery/FINAL_ACK.json,DELIVERY_LEDGER.md 및외부최종readback을사용한다.
