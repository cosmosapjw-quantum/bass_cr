# BASS_CR: full-source thermal-prefix 사건과 유한 오차

연구 단위 `CR_FULL_SOURCE_EVENT_20261014`, 선택 노드 `NT_PREFIX_EVENT_FULL_SOURCE_BINDING`의 R5 구성적 유도 및 단계 내 검산이다. 실제 기준 PR54 head `e484feb7762f969dbe29b3116b886455baa14395`는 게시 직전에도 동일했다. 결과는 새 H_i=0 시나리오에 한정한다. 이전 moving no-event 또는 two-edge 사건의 수치 인증을 복사하지 않았다. 외부 독립 과학 심사는 미수행이다.

## 실제 원본·코드·근거

전체 한국어 증명은 archive의 `REPORT_KO.md`, 정확한 full-model 값은 `results/FULL_SOURCE_CERTIFICATE.json`, 사건상태는 `results/FULL_EVENT_STATE.json`, reference와 검산은 `REFERENCE.json`, `VALIDATION.json`에 있다. 재현 코드·원 입력·실패·DAG·CAS 입력과 실제 선택 출력이 모두 포함된다. Git의 본 문서는 실질 정리와 복원 진입점이며 전체 실행 payload는 불변 ZIP에 둔다.

- ZIP: `BASS_CR_FULL_SOURCE_EVENT_20261014_SOURCE.zip`.
- Bytes743391, members71, manifest-bound payloads70, font binaries0.
- SHA256:`a69fb10a699e5a1d86c356e48f5f5e1577a67b4e608e036cbba5db1719f8f1e4`.
- Manifest SHA256:`a002b923da69fb0c26e9d9c01663dc02d5964ced28dd03139ac04b64837ab1d3`.
- Report SHA256:`7b535c4ae1e417cab1410714e0747eee630952ed848398e55b46eb3a47ae9c61`.
- [전체 재현 원본](https://drive.google.com/file/d/1VALUlOfPf-seFf2OhqO1AO1QQAOoRsdu/view?usp=drivesdk). Drive parent:`1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`; 업로드 및 metadata가 이름·ID·parent·크기743391를 확인했다.
- Dropbox:`/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_FULL_SOURCE_EVENT_20261014_SOURCE.zip`, ID:`id:BSpOijBcT10AAAAAAD5GYQ`; completed와 크기743391 확인.
- Local CRC와70payload SHA256를 확인했다. Remote 검증은 R1 ACK/ID/name/size/parent이며 원격 full restore가 아니다. 이전 원본·권한·production source는 변경하지 않았다.

## 1. Full-source 정의와 새 시나리오

H_i=0, 상수V, proper horizon100000s, signature(-,+,+,+), eV/cell·count·SI density를 사용한다. 원 핵13, HI7/HeI3/HII3, thermal electron1과 실제 원 volume/cv를 유지한다. 새 active stock은 P1, S0.999, node23 A0.001로 총 자유전자3이다. 초기 T는 node23 cutoff 온도보다0.002K 낮게 선택하고 U0=14cvT0다. 이 변경된 IC와 H=0는 CASE.json에 exact fractions로 기록했다.

Full comparison에는 모든 active donor의 HI/HeI 이온화와 downward Coulomb stopping을 남긴다. 실제 primary HI15600/HeI6812 paired full-sharing과 고정 positive projection을 사용한다. 다른 donor는 원4739-coordinate total rates와 양의 count2/kinetic+thermal+binding-energy 보존 daughter kernel class로 다룬다. 상계는 이 class 전체에 균일하여 원 BED positive-projection 구성을 포함한다. 후속 differential generator를 모두 새로 만들거나 full cascade를 적분하지 않았다. Cold-target/nonrelativistic source와 monatomic EOS, 원 정확한 count/energy completion을 유지한다. 원자모형·측정상수·관측 불확실성은 방법 간 인증과 구분한다.

Reference는 P2/S3의7상태, A23, 두 primary extent와 J의11변수다. Passive primary daughters는 실제 저장된 mass*magnitude로 들어간다. Bath density와 neutral depletion을 매 상태에서 갱신한다. 초기율을 고정한 CTMC가 아니다.

    beta_a^(p)=2-sum_(j>=p)m_ja,
    q_a^(p)=Ep-Ba-sum_(j>=p)Ej*m_ja,
    Nth=1+A0-A+sum beta_a^(p)*x_a,
    U=U0+E23(A0-A)+sum q_a^(p)*x_a
      +sum_P(Ep-Er)Pr+sum_S(Es-Er)Sr,
    x_a'=kappa_Pa*(Xa0-x_a)*P0/V,
    J'=x_H+x_He.

Stopping lambda_j=alpha_j*n/(Ej-Etarget)*(L0j-0.5log(n/nref)), n=Nth/V,nref=1m^-3. Reference에서 생략한 born 전체 충돌, P1/P2 이온화 및 P/S 말단 stopping은 full model에 남기고 다음 잔차에 포함한다.

## 2. 전체 donor residual과 보존 affine guard

Z=(K_j,U,C_H,C_He), K_j=EjNj,Ca=Ba*x_a^full이다. 기체를 고정한 collision generator는 Metzler/zero-column-sum이므로 선형 비자율 전파자 norm은1이다. 매 이온화·stopping 사건의 비용은2Eparent이며, 철회된2DeltaE를 사용하지 않는다.

Birth count<=t sum_a rho_a m_ja와 각 retained lineage sum<=root count에서

    Gamma_j=2Ej[sum_a kappa_ja/(V Ba)+lambda'_j(nmin)/(V E23)],
    L=max_P Gamma+S0 max_S Gamma+A0 Gamma23
      +h sum_j Gamma_j sum_a rho_a m_ja,
    ||r(t)||1 <=sum_r C_r*t^r/r!,
    B(t)=sum_r C_r*t^(r+1)*phi_(r+1)(Lt),
    phi_m(z)=sum_(k>=0)z^k/(k+m)!.

원 raw paired projection과 저장 mass의 미세한 차이만 source-specific IR evidence에서 재사용한다. 이전 B,L,T,current bounds는 새 시나리오에서 재사용하지 않았다. 전체 rate/density bound와 새 C_r를 directed Decimal65로 계산했다.

정확한 total free count는3+CH/BH+CHe/BHe이다. 분모가 양수인 cutoff guard를

    G23=E23[16+CH/BH+CHe/BHe-sum_j Kj/Ej]-eta U,
    eta=40/3

로 쓰면 상태에 affine이다. 두 경로의 total energy가 같으므로1^T e=0이며, guard gradient에 constant vector를 빼서

    |delta G23| <= C_G ||e||1,
    C_G=(eta+E23/BH)/2

를 얻는다. 최신 HE zero-sum quotient를 guard에 구체적으로 적용한 결과다. 일반 oscillation-duality의 최초성을 주장하지 않는다.

원 S의 무반응 생존분과 첫 stopping 가열을 남기고, 전체 이온화의 positive guard contribution을2E23*Imax로 제한했다. Imax=13 max_j sum_a kappa_ja Xa0/V다. 그 결과 전체100000s에서

    -G23' >=nu_full>7.084920753290937e-10 eV/s,
    -Gref' >=nu_ref>2.715735193096114e-9 eV/s.

10000/15000s에서 reference guard에 +/-CG B를 적용해도 부호가 반대이므로 full 첫 사건이 그 사이에 유일하게 있다. Mean-value theorem으로 |tf-tr|<=CG B(15000)/nu_ref<0.065629131723s다.

## 3. Source-commuting reset과 실제 full 사건

편입할 count는 원 A survivor만이 아니라 a=A+sum_a m23,a*x_a다. U+=E23a,Nth+=a를 적용하고, 미래 primary source에도

    beta_a^24=beta_a^23+m23,a,
    q_a^24=q_a^23+E23*m23,a

를 적용한다. 따라서 fixed reset R과 primary column은 R*bI23=bI24로 정확히 commute한다. Future-born node23도 bath로 간다.

일반 finite batch는 정렬된 node를 현재 Ej<=eta U/B인 동안 반복 편입한다. 평균 변화 Nj(Ej-U/B)/(B+Nj)>=0와 first-crossing mean ordering이 유지되므로 finite grid에서 최대 node 수만큼 검사하면 최소 reachable consistent prefix에 도달한다. Cooling reinsertion 또는 전역 대수적 branch 유일성을 주장하지 않는다. 단일-if 후보는 두-bin witness에서 실제 assertion 실패했고 동일 테스트가 while-closure에서 통과했다.

새 full-source 구간(표시는 outward):

    first tf in[11965.79994109,11965.93119936]s,
    reference tr in[11965.86557022328634,11965.86557022330411]s,
    full Tpre=101.10436413400510398165...K,
    full Tpost in[101.19325491331,101.19325494250]K,
    transferred count in[0.00099808010274830,0.00099808043035314],
    HI extent in[1.42944569146e-9,1.43338754772e-9],
    HeI extent in[7.96104939521e-11,8.17839944188e-11].

두 이온화 extent가 모두 strictly positive다. 저장된10000s endpoint에서 full event window로 추가 국소 Taylor extension1개를 평가하고 B(15000)로 full event state를 감쌌다. 이번은 실제 하나의 node를 편입하며 batch helper는 더 많은 node를 지원한다.

## 4. 유한 사건시각과 최종 온도

Reference를 임의의 시각s에서 reset한 뒤 공통시각t까지 보낸 H_t(s)=Phi+(t,s,R Phi-(s,0,Z0))를 미분·적분한다. 미분은 D Phi+[Rt+DR f- -f+ oR]다. Primary source는 commute하고 A→thermal도 R후 소거되므로, static reference의 timing mismatch는 bath 증가에 따른 P/S stopping-rate 변화만 남는다.

    M_R <=a_trans,max/V
          [max_P 2Ej lambda'_j(nmin)+S0 max_S2Ej lambda'_j(nmin)]
        <3.064654104418e-9 eV/s,
    E(t) <=B(t)+exp(Lt)M_R delta_t

는 두 경로가 모두 reset을 지난 공통시각에 성립한다. Full과 full 사건시각에 reset한 reference 사이에는 B를, 서로 다른 시각의 reference 사이에는 두 번째 항을 적용한다. 이전 two-edge saltation norm 또는 first-order remainder를 유한 상계로 대신 사용하지 않았다.

현재 new L=1.75880001616594e-5/s. 100000s에서 B<8.605245542644e-9eV, timing<1.167656939814e-9eV, total<9.772902482457e-9eV다. 같은 post-prefix에서 thermal count sensitivity1/E23와 Nthermal+nuclei>=14, actual reference tube T<102K를 사용하여

    R_T<5.809090907827e-6K,
    Tref=101.2067234829248068259...K,
    Tfull in[101.20671767383,101.20672929202]K.

기존0.001K budget을 바꾸지 않았다. 한쪽만 reset한 asynchronous window에는 이 작은 state-error bound를 적용하지 않는다. 별도 full heat-power 상계로 그 window의 T<101.226284255K를 얻었다. 두 reset 뒤에는 전체 reference tube+오차가 next threshold 약102.899438K 아래다. Lower guard의 단조성과 first-exit 논증을 결합하여100000s까지 두 번째 prefix event가 없음을 닫았다.

## 5. 실제 사건을 포함하는 matched Thomson observable

Reset은 total-free current에 impulse를 만들지 않는다. 이번에는 ionization이 살아 있어 total-free count 자체는 시간에 따라 증가한다. 같은 reference에서 직접 계산한 J로

    tau_ref=c sigmaT/V*(3h+J(h))

를 얻었다. 같은 total energy에서는 |delta Nfree|<=E/(2BH)다. 비동기 window는 별도 current bound를 사용한다: w=2delta_t+width(tr), 시작 count차이<=B(15000)/(2BH), 두 source-rate 차이<=2Imax이므로 그 적분은 w B(15000)/(2BH)+Imax w^2 이하이다.

    R_tau <=c sigmaT/V *{[Bint+M_R delta_t h phi1(Lh)]/(2BH)
                         +w B(15000)/(2BH)+Imax w^2},
    tau_ref=5.9472799085193020784367...e-15,
    R_tau<1.725098317728e-25,
    tau_full in[5.94727990834679,5.94727990869182]e-15.

초기3-electron baseline을 뺀 full lower bound도 양수다. Constants c=299792458m/s,sigmaT=6.6524587051e-29m²를 사용한다. 측정오차와 KN closure는 별도다.

최신 HE43의 material-age A=q.k와 Doppler D=-u.k, all-sky |b|<1 및 D/A weight를 읽었다. 현재 normal static source에는 A=D=1이다. 일반 batch stress-work는 xAct로 유지했고 H=0에서만0을 적용했다. 다른 clock/geometry에는 current center와 equal-energy bound를 복사하지 않는다.

## 6. 실제 검산과 범위

Directed Decimal65 Taylor6, strict Picard whole-step tube, order7 remainder로21개 fresh history step을 계산했고 모든 trace가 남는다. 추가 full event-state 국소 extension은1개다. 별도 RHS 구현의 mpmath60 Gauss4를2500/1250s로 처음부터 적분한 root·pre/post T·11final states가 모두 interval에 들어왔다. 최종 T 차이8.17e-33K는 numerical check이며 interval proof를 대체하지 않는다.

Actual Wolfram15.0.1:15named groups/34scalar literal zeros. Actual xTensor1.3.0:7tensor literal zeros. 원 input scripts와 selected normalized observed outputs를 보존했다. 새 read-only checks108개, 별도 batch unittest4개 통과. 같은 작성자의 별도 CAS/산술 경로이며 external independent scientific review/native subagent는 NOT_RUN이다.

첫 Picard 동시전체-inflation failure는 실패 성분만 inflate해 strict inclusion을 만족하도록 수정했다. Single-bin assertion RED와 GREEN, exact-equality checker 점연산 failure/Fraction repair, tuple-return checker repair를 보존한다. Bare Decimal root-width subtraction을 directed interval subtraction으로 고치고 해당 bound/check만 재계산했다. 과학식·acceptance를 느슨하게 바꾸지 않았다.

SciSpace/Exa primary-discovery 및 실제 arXiv metadata로 Le-Cambier2017, Kong et al2024, Michel-Siegle2024와 비교했다. CME/FSP의 probability sink를 nonlinear energy certificate로 그대로 옮기지 않았고 학술적 최초성을 주장하지 않는다.

Latest cross-repo snapshots: HE43 efacaa1c7a17416debac18101cc6558e44e825cf의 full R8 result를 guard/current에 사용했다. HH60 c56cae5662a4c44b4f387699b5602355e63cb7dc 및 REI115 4716c469535422ba6c293a26e3478cedd3923e6b의 실제 최신 PR 결과를 읽었으나 수치계수/observer covariance를 이 모형에 넣지 않았다. CR/RCT/HH OFF와 기존 owners를 유지한다.

## 다음

`NT_MOVING_FULL_SOURCE_EVENT_CLUSTER`: H_i!=0, birth-time/angular full-sharing source, moving nodes의 방향별 guard/cluster, finite batch와 geometry-work까지 포함하는 새 event tube. 이 static completion과 이전 PE/IR 수치를 새 기하/IC/시간에 재사용하지 않는다. 원 DAG의 선택하지 않은 nodes와 F/G/atomic/b-grid/globalREI 상태를 보존했다. Full generator, full cascade, native receiver, HPC, main merge 또는 permission change는0이다.
