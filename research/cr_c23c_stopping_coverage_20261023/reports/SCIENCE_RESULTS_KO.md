# C23C: 저장된 광이온화 전자 공급과 온도 의존 cutoff의 결속

## 1. 이번에 확보한 결과

C23C는 C23B에서 이미 계산하고 저장한 광이온화 전자 분포를, 명시적인 기체 inventory와 온도 의존 cutoff에 연결했다. 실제 공개 UV spectrum에서 유래한 전자 공급량을 proper volume·target 수·proper duration으로 변환하고, 그 전자를 thermal 또는 active inventory에 배정하는 동안 입자수·전하·핵종수·운동에너지를 보존하는 구현을 완성했다. 기존 KC4의 finite atomic branch 구성을 재사용했으며, source를 다시 적분하거나 과거 campaign을 복원 목적으로 재실행하지 않았다.

새 실행은 세 redshift, 세 초기 온도, 두 cutoff parameter의 곱인 **18 cases**다. 각 case에서 13개의 유리수 보존·EOS residual이 모두 정확히 0이었다. 별도 구현 경로를 사용한 독립 Decimal80 검토는 977개의 scalar 값을 비교했고, 최대 상대차 \(1.2507493130458459\times10^{-78}\)를 얻었다. 사전에 정한 비교 기준은 \(10^{-40}\)이다. 새로 생성한 threshold equality witness, density/abundance normalization pair, 명시적인 입력 거부 조건도 확인했다. [실제 생산 결과](../runs/c23c_source_cutoff_binding_20261023_v1/SUMMARY.json), [독립 검토 결과](../runs/c23c_independent_c9_20261023_v1/RESULT.json)

이번 결과의 물리적 역할은 **전자 공급에서 보존적 cutoff 분할로 이어지는 연결부**를 닫는 데 있다. 여기서 산출하는 온도는 선택한 inventory 분할과 이상기체 EOS가 정의하는 caloric diagnostic이다. 실제 전자가 Coulomb 충돌, 중성 원자와의 탄성 충돌, 여기·이온화 등을 거쳐 열화되는 시간은 다음 공급자 계약에서 결정해야 한다. 따라서 physical heating, stopping time, global error bound는 계속 null로 유지한다.

**EXECUTION:** C23C 새 18 cases와 독립 검토 완료, 새 ODE0, 과거 완료 계산 재실행0.  
**PUBLICATION:** 이 문서는 root의 C10 게시 패키지에 합류하는 확정 과학 결과다. 실제 commit은 최종 authority에서 확인한다.  
**BACKUP:** provider ACK 및 다운로드 검증 상태는 최종 배송 영수증이 담당한다.  
**DAG:** CR_N4_C23B_CUTOFF_BINDING 완료 범위 → 실제 stopping·thermal exchange 공급자 결속.

## 2. 실제 source와 계산용 bath를 구분한다

원 source는 Taira, Kopenhafer, O’Shea가 공개한 2025년 UV background data release에 포함된 PW19 spectrum이다. C23B는 원 Cloudy 형식과 CSV가 함께 확인되는 \(z=2.316,2.479,2.649\)에서 HI, HeI, HeII의 ground-state photoionization source를 계산했다. 이 세 epoch 사이를 보간하거나, 서로 다른 epoch의 atoms를 하나의 gas state로 합치지 않는다. 공개 자료의 DOI는 [10.5281/zenodo.15367103](https://doi.org/10.5281/zenodo.15367103), 설명 논문의 DOI는 [10.3847/2515-5172/adddae](https://doi.org/10.3847/2515-5172/adddae)다. [원 논문](https://arxiv.org/html/2505.23544v1), [고정된 공개 코드·자료](https://github.com/tairaeli/Metagalactic_Ultraviolet_Background_Data_Tables/tree/863c3b7fa73a8510fbf57ee7b75ad1e8c34086de)

Atomic photoionization cross-section은 Verner 원자료에 결속되어 있다. 이번 source의 threshold convention은 HI13.60eV, HeI24.59eV, HeII54.42eV이고, 채택한 photon energy upper limit은 50keV다. 이 수치는 해당 fit의 convention이며, 모든 isotope에 대한 정확한 binding energy를 의미하지 않는다. 공식 자료와 원 논문은 [Verner photoionization data](https://www.pa.uky.edu/~verner/photo.html), [Verner et al.1996](https://arxiv.org/abs/astro-ph/9601009)에 있다.

C23C가 소비한 CSV에는 32,592개의 양의 quadrature atoms가 있으며 epoch당 10,864개다. 그 파일의 크기는 1,681,578 bytes이고 SHA256은 f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3이다. 원 spectrum의 positivity와 finite-domain source 계산 근거는 C23B에서 확보했고, 이번에는 그 저장 바이트를 직접 사용했다. 여기서 “atom”은 유한 측도의 수치 원소를 뜻한다. 개별 원자 또는 실제 전자선이 delta function으로 측정되었다는 표현은 아니다.

반면 이번 bath는 구현을 판별하기 위해 명시한 **synthetic five-fit-label inventory**다. proper volume은 \(1\,{\rm cm^3}\), 초기 proper densities는 HI0.9, HII0.1, HeI0.07, HeII0.02, HeIII0.01 \({\rm cm^{-3}}\)다. 이 수치를 경험적 IGM 조성이나 특정 cosmic-ray 환경의 관측값으로 제시하지 않는다. 모든 free electron은 처음에 charge-neutral thermal reservoir에 들어 있고, 초기 resolved nonthermal inventory는 없다고 선언했다. 초기 온도는 100, 10,000, 50,000K, source proper duration은 \(10^{10}\)s, \(\chi\)는 \(3/2\) 또는 3이다. [실행 계약](../CONTRACT.json)

이렇게 source와 bath를 분리하면 무엇을 재사용했고 무엇을 새 입력으로 정했는지가 명확해진다. 공개 UV·원자 fit에서 얻은 에너지 분포와, 그 분포를 특정 cell inventory에 적용하는 계산상의 선택은 서로 다른 근거를 갖는다. isotope-resolved 21 populations에 대한 반응 공급은 아직 이 five-label adapter에 자동으로 연결되지 않는다. 누락된 isotope나 반응을 0으로 채워서 범위를 확장하지 않았다.

## 3. per-target rate를 실제 cell count로 옮기는 식

C23B의 source를 channel \(i\)별로

\[
dQ_i(K)=\sum_jq_{ij}\delta_{K_{ij}}(dK),
\qquad q_{ij}>0,\quad K_{ij}\ge0
\tag{1}
\]

로 쓴다. \(q_{ij}\)의 단위는 흡수 target 하나당 proper second의 역수이고, \(K_{ij}\)는 bath frame에서 정지한 target이 방출하는 primary electron의 kinetic energy다. 해당 source가 이미 bath frame에 있으므로 새 boost나 parent decay lifetime factor를 덧붙이지 않는다.

proper volume \(V\), proper target density \(n_i\), proper duration \(\Delta\tau\)가 주어지면 각 packet의 count는

\[
N_i=Vn_i,\qquad
n_{ij}=N_i\Delta\tau q_{ij}
\tag{2}
\]

다. abundance 입력을 쓰는 경우에는 reference density를 추가로 명시해 같은 \(N_i\)로 변환한다. volume과 reference density를 모두 필요한 위치에서 한 번만 곱한다. 좌표 시간이나 conformal time을 사용할 다음 단계에서는 적절한 proper-time 변환을 별도로 넣어야 한다. 이번 입력의 시간 단위는 처음부터 proper second로 고정했다.

각 채널의 사건수, 전체 새 electron count, primary kinetic supply는

\[
S_i=\sum_jn_{ij},\qquad
S=\sum_iS_i,\qquad
E_s=\sum_{ij}K_{ij}n_{ij}
\tag{3}
\]

다. source를 frozen-target predictor로 사용하는 동안 targets, volume, UV spectrum은 고정하고, 그 단계에서 새로 만들어진 daughter를 다시 target으로 사용하지 않는다. 따라서 HeI에서 생성된 HeII를 동일 source stage에서 다시 이온화하는 연속 반응은 이 finite predictor에 포함되지 않는다.

이 조건에서는 기존 target 수보다 더 많은 사건을 요구하지 않도록 \(\Delta\tau\Gamma_i\le1\), \(\Gamma_i=\sum_jq_{ij}\)를 검사한다. 이 검사와 명시적인 positive inventory가 predictor의 positivity를 지킨다. 실제 시간 적분의 truncation error 또는 넓은 exposure 구간의 accuracy는 별도 문제이며, 그 error bound를 이번 exact arithmetic 결과에 덧붙이지 않았다. 코드의 source_time_discretization_error_bound가 null인 이유가 여기에 있다.

## 4. 같은 사건수를 전하·핵종·에너지 장부에 사용한다

Source 사건수는 population update와 electron measure에서 공통으로 사용된다.

\[
\begin{aligned}
\Delta N_{\rm HI}&=-S_{\rm HI},
&\Delta N_{\rm HII}&=S_{\rm HI},\\
\Delta N_{\rm HeI}&=-S_{\rm HeI},
&\Delta N_{\rm HeII}&=S_{\rm HeI}-S_{\rm HeII},\\
\Delta N_{\rm HeIII}&=S_{\rm HeII}.
\end{aligned}
\tag{4}
\]

이 식에서 H nuclei와 He nuclei 각각의 총수는 유지된다. ion charge의 증가는 \(S_{\rm HI}+S_{\rm HeI}+S_{\rm HeII}=S\)이며, source measure에 추가한 전체 free electron count와 같다. 이 charge bookkeeping은 thermal과 active electron을 모두 포함한다. thermal population만 charge-neutrality에 넣고 active electron을 빠뜨리면 다른 장부가 된다.

채널별 threshold를 \(I_i\)라 하면 binding supply와 photon absorption은

\[
\Delta E_{\rm bind}=\sum_iI_iS_i,\qquad
E_{\gamma,\rm abs}
=\sum_{ij}(I_i+K_{ij})n_{ij}
=\Delta E_{\rm bind}+E_s.
\tag{5}
\]

원 C23B의 zero-recoil, stationary-target convention을 그대로 유지했다. Binding energy와 primary kinetic energy를 별도 owner로 두면, 향후 secondary cascade나 radiative transfer를 추가할 때 동일 photon energy를 두 번 계상하는 일을 피할 수 있다. 외부 prescribed radiation에서는 흡수 에너지를 imported energy로 기록하고, 내부 photon reservoir를 실제 수송할 때에는 그 reservoir에서 같은 양을 차감하도록 소유권을 바꿔야 한다.

Cutoff 단계는 식(4)의 원자 population과 식(5)의 binding·radiation 장부를 변경하지 않는다. 이미 존재하는 free electron의 kinetic inventory를 두 표현으로 나누는 단계다. 이러한 순서 때문에 이후에 reaction operator가 확장되더라도, source event의 보존과 cutoff partition의 보존을 각각 추적할 수 있다. [구체적인 식–코드 결속](../theory/lowenergy/C23B_KC_BINDING_DERIVATION_KO.md)

## 5. source electron을 base에 중복으로 넣지 않는 것이 핵심이다

현재 fixture의 nucleus count는 \(N_{\rm nuc}=1.1\), 초기 free electron count는 \(N_{e,0}=0.14\)다. 따라서 unresolved thermal base의 count는

\[
N_B=N_{\rm nuc}+N_{e,0}=1.24,\qquad
U_B=\frac32k_BT_0N_B
\tag{6}
\]

이다. EOS의 thermal count에는 nuclei와 thermal free electrons가 모두 들어간다. source electron을 넣기 전의 base를 정의한 뒤, 새 전자는 전부 resolved measure에 추가한다.

기존 common count와 kinetic energy를 \(\mathcal C^0,\mathcal E^0\), 기존 resolved measure를 \(\mu^0\)라고 쓰면 source 후에는

\[
\mu^+=\mu^0+\sum_{ij}n_{ij}\delta_{K_{ij}},\qquad
\mathcal C^+=\mathcal C^0+S,\qquad
\mathcal E^+=\mathcal E^0+E_s.
\tag{7}
\]

따라서 \(\mathcal C^+-\int d\mu^+=N_B\)와
\(\mathcal E^+-\int K\,d\mu^+=U_B\)는 그대로다. 새 electron이 resolved measure와 base에 동시에 들어가거나, primary kinetic energy가 source atoms와 base energy에 동시에 더해지면 보존 row가 깨진다. 이번 구현은 이 두 항을 각각 독립 residual로 검사했다.

이 구조는 “모든 free electrons가 곧 thermal electrons”라는 묵시적인 동일시도 피한다. cutoff를 적용한 뒤 thermal electron 수는 \(N_{e,0}+L_N\), active electron 수는 \(S-L_N\)이며 둘의 합이 \(N_{e,0}+S\)로 돌아간다. nuclei는 thermal heavy-particle count에 남는다. 초기 nonthermal population이 존재하는 다음 모델에서는 그것을 명시적으로 전달하고 base에서 제외해야 한다. 현재 adapter는 그런 추가 state를 조용히 무시하지 않도록 입력 필드를 제한한다.

## 6. 유한 atomic prefix로 cutoff를 구성한다

에너지가 같은 packets를 합치고 \(K_1<\cdots<K_M\)으로 정렬한다. 처음 \(k\)개 energy group이 thermal인 candidate의 count·energy·온도는

\[
N_k=N_B+\sum_{j\le k}n_j,\qquad
U_k=U_B+\sum_{j\le k}K_jn_j,\qquad
T_k=\frac{2U_k}{3k_BN_k}
\tag{8}
\]

다. cutoff를 \(K_c=\chi k_BT_k\)로 정하고,

\[
K_k\le K_c<K_{k+1}
\tag{9}
\]

를 만족하는 prefix를 찾는다. 앞쪽 또는 뒤쪽에 atoms가 없는 경우 해당 부등식은 생략한다. equality는 thermal의 소유이므로 active 조건은 엄격한 \(K>K_c\)다.

이번에는 KC4의 \(\chi\ge3/2\) finite forward construction을 그대로 사용했다. 양의 base inventory에서 시작하여 다음 atom이 현재 cutoff 이하면 포함하는 과정을 유한하게 진행한다. 원 증명은 포함 후 온도가 반드시 단조 증가해야 한다는 조건을 요구하지 않는다. packet을 포함할 때 온도는 두 양의 평균에 의해 정해지고, 선택한 \(\chi\) 조건이 이미 포함한 atoms의 thermal ownership을 유지한다.

모든 candidate에서 thermal과 active의 수·에너지 합은 동일한 common inventory다. 유한 cutoff 이동의 energy transfer는 실제 포함·제외된 atoms의 \(K_jn_j\) 합을 사용한다. 최종 cutoff energy에 옮긴 입자수를 곱하는 방식으로 바꾸지 않는다. 또한 향후 cooling에 의해 cutoff가 내려갈 때 역분할하려면 thermal로 분류된 lower atoms도 보존해야 한다.

KC 원본은 [commit a5c29ad4070acb931d92d2bec42a927a57f479ca](https://github.com/cosmosapjw-quantum/bass_cr/tree/a5c29ad4070acb931d92d2bec42a927a57f479ca/research/cr_kernel_cutoff_20261013)에 있다. 이번 구현의 직접 재사용 대상은 KC4와 KC7의 atomic reference다. Continuous spectrum에 대한 KC3의 effective-capacity certificate나, coupled source-temperature map에 대한 KC6 contraction theorem은 이번 discrete source에서 자동으로 성립한다고 주장하지 않는다. 독립 검토는 실제 18개 입력의 모든 prefix candidates를 열거했고 각 입력에서 consistent root 하나를 관찰했다. 이 관찰의 범위는 그 18개 입력이다.

## 7. \(z=2.479\)에서 얻은 여섯 가지 분할

아래 표는 저장된 CUTS.csv에서 해당 redshift의 여섯 행을 옮긴 것이다. 같은 epoch·target inventory·duration을 사용하므로 여섯 case의 source count와 primary kinetic supply는 같다.

\[
S=0.011099621671440229,\qquad
E_s=0.04288487203201777\ {\rm eV}
\tag{10}
\]

이는 \(1\,{\rm cm^3}\) fixture cell의 연속 분포 count와 energy다. 초기 온도와 cutoff parameter가 바꾸는 것은 이 source를 어떻게 분할하고 어떤 caloric EOS state로 표현하는가이다. [원 수치 표](../runs/c23c_source_cutoff_binding_20261023_v1/CUTS.csv)

| 초기 \(T_0\)/K | \(\chi\) | \(T_{\rm cal}\)/K | \(K_c\)/eV | \(T_{\rm cal}-T_0\)/K |
|---:|---:|---:|---:|---:|
| 100 | 1.5 | 99.9982091644 | 0.0129257684098 | −0.00179083561309 |
| 100 | 3 | 99.9996642013 | 0.0258519129758 | −0.000335798705319 |
| 10,000 | 1.5 | 9,984.07085525 | 1.29054098809 | −15.9291447507 |
| 10,000 | 3 | 9,992.26402582 | 2.58320007462 | −7.73597418000 |
| 50,000 | 1.5 | 49,756.9985252 | 6.43158957623 | −243.001474819 |
| 50,000 | 3 | 49,778.4450307 | 12.8687235030 | −221.554969281 |

다음 표의 비율은 모두 **새 source 전체**를 분모로 사용한다. \(L_N/S\)는 cutoff 아래에 배정된 source count fraction, \(L_E/E_s\)는 그 source kinetic-energy fraction이다. 마지막 열은 active로 남으면서 동시에 FS table의 10eV 하한보다 낮은 source energy의 비율이다.

| \(T_0\)/K | \(\chi\) | \(L_N/S\) | \(L_E/E_s\) | Active \(K<10\)eV energy/\(E_s\) |
|---:|---:|---:|---:|---:|
| 100 | 1.5 | 0.00264182031002 | 0.00000214494149756 | 0.650861193764 |
| 100 | 3 | 0.00866980833543 | 0.0000277501762020 | 0.650835588529 |
| 10,000 | 1.5 | 0.328066487327 | 0.0500463742005 | 0.600816964505 |
| 10,000 | 3 | 0.530196732931 | 0.148329787478 | 0.502533551228 |
| 50,000 | 1.5 | 0.820882703570 | 0.458261561395 | 0.192601777310 |
| 50,000 | 3 | 0.949892131871 | 0.753854793158 | 0 |

저온 fixture에서는 source count 중 cutoff 아래에 들어가는 비율이 작고, active 상태이면서 10eV보다 낮은 전자가 많은 에너지를 가진다. 예를 들어 \(T_0=10^4\)K, \(\chi=3\)에서는 새 source count의 약 0.5302가 cutoff 아래에 분류되지만, 그 kinetic-energy fraction은 약 0.1483이다. 동시에 source energy의 약 0.5025는 active이면서 FS 지원 하한 아래에 남는다. 이 수치는 바로 다음 low-energy stopping 공급자가 다뤄야 할 inventory를 보여준다.

\(T_0=50,000\)K, \(\chi=3\)에서는 cutoff가 약12.8687eV여서 \(K<10\)eV인 source atoms가 모두 thermal 쪽에 분류된다. 마지막 열의 0은 두 수학적 구간의 교집합이 비어 있기 때문에 생긴다. 물리적인 energy loss rate가 0이거나 그 에너지가 이미 충돌을 통해 열화되었다는 관측으로 사용하지 않는다.

## 8. Caloric 온도 변화가 physical heating rate와 다른 이유

새로 thermal에 배정한 source의 count·energy를 \(L_N,L_E\)라 하면 식(6)과 식(8)에서

\[
T_{\rm cal}-T_0
=
\frac{L_E-\frac32k_BT_0L_N}
     {\frac32k_B(N_B+L_N)}
\tag{11}
\]

를 얻는다. 이 식은 source energy뿐 아니라 새로 추가되는 electron count도 함께 고려한다. \(L_E>0\)이어도 평균 추가 energy \(L_E/L_N\)가 기존 thermal particle당 energy \(\frac32k_BT_0\)보다 작으면 caloric temperature는 내려간다. 위 여섯 case의 음의 온도 차이는 이 분자에서 직접 설명된다.

전체18 cases의 caloric temperature change는 −246.26443132221186K에서 −0.0003292725246442509K 범위였다. 이 숫자는 선택한 bath·exposure·cutoff 아래의 endpoint 표현을 설명한다. \(\Delta T/\Delta\tau\)를 기체의 물리적 냉각률로 제시하지 않는다. 실제 시간 진화에서는 electron distribution과 thermal reservoir의 충돌 exchange, atomic inelastic losses, photon production·escape, 기하학적 work가 함께 정해져야 한다.

FS2010 deposition table의 lower support인10eV는 자료의 적용 에너지 경계다. \(\chi k_BT\)는 이번 caloric partition의 정의다. 두 경계를 분리하여 6개 cross-cells를 저장했기 때문에, source가 어느 구간에 있고 어떤 공급자가 아직 없는지 손실 없이 추적할 수 있다. FS 결과의 물리 범위와 조성 가정은 원문 [Furlanetto & Stoever2010, arXiv0910.4410](https://arxiv.org/abs/0910.4410) 및 기존 C23B source contract에 연결한다. 이번 cutoff 결과로 FS의 미확인 조성 또는 지원 범위를 확장하지 않았다.

이 구분은 thermal closure를 미루기 위한 표현상의 제한이 아니라, 다음 방정식에 들어갈 서로 다른 항을 분리하는 계산 계약이다. source 공급은 전자를 만들고 에너지를 수입한다. stopping operator는 그 분포를 이동시키고 bath와 에너지를 교환한다. cutoff는 그 결과의 일부를 thermal 표현에 배정한다. 이 세 역할을 각기 다른 장부에 두면 미래 구현에서 double heating을 검출할 수 있다.

## 9. 검증이 확보한 정확도의 의미

생산 구현은 저장된 CSV decimal values를 Fraction으로 읽었다. 따라서 finite count·energy·EOS 관계의 0 residual은 **그 저장된 유리수 측도와 정해진 predictor**에 대한 정확한 항등식이다. 원 UV spectrum의 관측·모델 불확실성, atomic fit error, 누락 반응 또는 시간 적분 error가 0이라는 뜻은 아니다. 정확한 유리수 ledger와 물리 모델의 오차 예산은 별도로 관리한다.

독립 검토자는 production numerical engine을 호출해서 같은18개 답을 다시 얻는 방식 대신, 원 CSV에서 Decimal80 직접 합산과 모든 prefix candidate의 EOS를 계산했다. source→target normalization, photoionization charge, base ownership, common inventory, thermal/active 분할, FS cross-cells를 비교했다. source fit과 branch 선택의 scientific acceptance는 바꾸지 않았고, 사전 기준 \(10^{-40}\)보다 작은 차이를 확인했다. Binary64 CSV 표시값은 별도의 표현 관계로 검증했다. [독립 검토 보고서](../review/C9_REVIEW_KO.md)

입력 계약에서는 top-level unknown field를 무시하는 API 문제가 하나 발견되었다. 실제 18 inputs는 허용된8개 필드만 포함하여 science output은 영향받지 않았다. 원 실행 source를 history에 보존하고, unknown fields와 non-object request를 명시적으로 거부하도록 교정했다. 필요한 field가 빠졌을 때는 어떤 값을 추정하거나0으로 대체하는 대신 BLOCKED 상태와 누락 항목을 반환한다. Root targeted guard5개와 독립 guard12개가 이 교정을 확인했다.

별도 equality witness는 실제 저장 source의 최저 \(K\)를 사용하여 \(T_0=K/[(3/2)k_B]\), \(\chi=3/2\)를 정했다. 양의 exposure를 주었을 때 경계에 정확히 놓인 atom이 thermal 쪽으로 배정되고 온도가 유지되는 것을 확인했다. 새로운 normalization pair에서는 volume7/3과 reference density5/2를 사용했다. 이러한 경계 검증은 이번 adapter의 구체적인 위험을 다룬 것이며, 과거 KC 또는 C23B campaign을 반복하지 않았다.

생산 worker의 실제 wall time은8.84399s, CPU time8.83968s였고, 독립 C9 worker는 wall2.05391s, CPU2.05259s였다. 각 실행은 실제 자원 관찰과 cooperative lease 아래에서 한 native thread를 사용했으며 CPU55를 사용하지 않았다. 이 시간은 해당 실행의 비용 기록이다. 동일한 정확도·입력·환경의 비교 benchmark를 수행하지 않았으므로 speedup 수치로 제시하지 않는다.

## 10. 현재 N4의 완료 범위와 다음 stopping 의무

현재 완료된 것은 **N4의 C23B source–cutoff binding 단위**다. 입력 source와 finite bath inventory를 실제 코드로 연결했고, 원자 population과 free electron count를 보존하며, caloric branch와 FS support 교차분할까지 산출했다. 실제 재사용된 KC theorem의 가정과 새 코드의 입력이 일치하는지 확인했고, independent implementation audit의 finding도 닫혔다.

다음 물리 노드는 저에너지 stopping과 thermal/nonthermal electron exchange다. 여기에는 bath electron temperature·density, Coulomb logarithm의 적용 조건, neutral fractions, elastic recoil, excitation·ionization·secondary production, escape 또는 trapping 조건을 실제 공급자와 연결해야 한다. 단순한 cold-target energy-loss coefficient를 thermal energy 부근까지 연장하는 대신, 필요한 경우 energy diffusion과 detailed balance를 포함하는 finite-temperature operator를 선택해야 한다. 어떤 항을 채택할지는 원문 계수와 코드의 정의역을 읽어 결정한다.

후보 문헌으로는 Allred, Alaoui, Kowalski, Kerr의 FP transport 연구가 있다. 원 abstract는 momentum 및 pitch-angle diffusion을 포함하는 kinetic transport model을 설명하며, 저자 code는 solarFP/FP에서 공개되어 있다. DOI는 [10.3847/1538-4357/abb239](https://doi.org/10.3847/1538-4357/abb239), 원문은 [arXiv2008.10671](https://arxiv.org/abs/2008.10671), 코드 주소는 [solarFP/FP](https://github.com/solarFP/FP)다. 현재 확인한 abstract·README·Apache-2.0 metadata는 다음 재사용 후보의 근거다. 이번 C23C에 그 코드 또는 stopping rate를 도입한 실적은 없다.

N5의 actual atomic-rate와 isotope coverage 계약은 이 연결부와 병렬로 필요한 의무다. 각 반응은 대상 charge state, threshold, 유효 energy·temperature 범위, daughter spectrum·angular assumptions, 전하·핵종·에너지 보존 row를 가져야 한다. 누락 과정은 실제 적용 환경에서 dominant할 수 있는지 평가하고, isotope quotient가 성립하는 조건을 확인한 뒤에만 묶는다. Five-fit-label source의 성공을 그 coverage의 완료로 옮기지 않는다.

이 두 공급자 계약이 준비된 뒤에는 gas kinetic energy, binding·excitation, resolved nonthermal distribution, radiation·escape, expansion 및 shear work를 합친 conservative energy closure를 구성한다. 그 다음 새 입력과 run ID로 가벼운 closed-parcel 검증을 수행하고, 승인된 자원 안에서 coupling 실행으로 나아간다. Full high-energy nuclear network와 general triaxial/tilted/polarized CMB 범위는 HOLD로 유지한다. 원 핵반응 네트워크 PNG는 이번 작업에서 회수하거나 읽지 않았다.

## 11. 현재 결과를 재사용하는 방법

재개자는 C23C 최종 authority와 실제 Git commit을 확인하고 저장된18 results와 independent audit를 재사용한다. 새로운 stopping provider가 바꾸는 식과 output을 새 run identity에 결속한다.

재개 시 사용할 핵심 파일은 CONTRACT.json, implementation/source_cutoff_binding.py, implementation/vendor/thermal_cutoff_solver.py, runs/c23c_source_cutoff_binding_20261023_v1/CASES.json, 그리고 runs/c23c_independent_c9_20261023_v1/RESULT.json이다. 입력·유효범위, source-to-cutoff 경로와 독립 수치 검토가 이 파일들에 결속되어 있다.

이 보고서는 결과 작성 단계에서 기존 파일만 읽어 작성했다. 새 과학 계산, 새 reviewer, 새 test campaign은 시작하지 않았다. 남은 C10 조치는 root의 게시·보존·복사 가능한 handoff이며, 다음 연구의 첫 질문은 “현재 low-energy inventory에 어떤 물리적으로 유효한 stopping/thermal-exchange operator를 결속할 것인가”다.

