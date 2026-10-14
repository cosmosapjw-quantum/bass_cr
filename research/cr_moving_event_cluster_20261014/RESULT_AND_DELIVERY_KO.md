# BASS_CR: moving full-source의 전방향 thermal-shell cluster

2026-10-14, Asia/Seoul. 실제 PR55 head `4abd195f1a3124e59b0fa498b446b590ef0116e5`의 successor `NT_MOVING_FULL_SOURCE_EVENT_CLUSTER`를 R5 구성적 유도와 단계 내 검산으로 수행했다. 이전 static certificate의 수치 반경을 옮기지 않고, 움직이는 source/rate/heat/reset/work의 잔차를 새로 계산했다. 원래 AGENTS와 현재 per-unit handoff를 읽었으며 scientific/production gate는 구분한다.

## 전체 재현 자료와 보존

- `BASS_CR_MOVING_EVENT_CLUSTER_20261014_SOURCE.zip`: 801634 bytes,41members/40manifest payloads.
- SHA256: `cf083027c8ac8491c00210c047678a0f8ac8df1050f6346acef82f524dc7648f`.
- Manifest SHA256: `8f0097101732ef63ff0f88368936b7589c9bf0cb0f3d1420403f557b162a82d5`.
- [전체 한국어 증명·실행 코드·원 입력·결과·실패·DAG](https://drive.google.com/file/d/1YcSvXaOZVZOl0h2w5tAhHiuL6jCzvHSn/view?usp=drivesdk).
- Drive ID `1YcSvXaOZVZOl0h2w5tAhHiuL6jCzvHSn`, parent `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`. 실제 업로드와 metadata에서 이름·ID·parent·801634bytes 확인.
- Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_MOVING_EVENT_CLUSTER_20261014_SOURCE.zip`, ID `id:BSpOijBcT10AAAAAAD5GdA`. Completed와801634bytes 확인.
- R1 ACK/ID/name/size/parent 검증이며 remote full restore는 미수행이다. Local payload hashes와 nested ZIP CRC, font absence를 확인했다. 원본·권한을 변경하지 않았다.

전체 증명은 ZIP의 `REPORT_KO.md`, 정확한 긴 끝점은 `results/MOVING_CERTIFICATE.json`, 사건 상태는 `results/MOVING_EVENT_STATE.json`에 있다. Git의 이 문서는 실질 유도와 restore entrypoint이며 모든 실행 payload를 Git에 중복 확장한 것은 아니다.

## 1. 새 physical scope와 계산하는 reference

Signature(-,+,+,+), x0=ct, proper normal seconds, eV/cell,count,V in m3, cv=3kB/(2epsilon_eV), eta=40/3. 원 scalar IC P1,S0.999,A23=0.001,thermal1,nuclei13,HI7/HeI3/HII3와 T0=E23/(eta cv)-0.002K를 유지한다. 기하는 H=(2,4,6)e-15/s, V=V0 exp(theta t), h100000s다. P는 ±x pair, S와 유한 A23 seed는 ±z pair다. 실제 birth daughter는 생성시각의 물리 frame에서 isotropic marginal이며 full kernel class는 inversion symmetry를 유지한다.

원 primary HI15600/HeI6812 paired full-sharing samples와4739 total-rate coordinates를 사용한다. Full comparison은 모든 donor의 HI/HeI ionization/downward stopping을 포함한다. 비일차 differential kernel은 gas-independent positive count2/energy conserving class이며 source-specific residual은 이 class에 균일하다. 원 cold-target/nonrelativistic collision law와 massive geometry, monatomic thermal EOS를 구분한다. 원자모형/calibration/측정상수 불확실성은 numerical certificate와 별도다.

M=me c2일 때 생성시각 s의 energy w, 물리 방향 n에 대한 energy는 W=z/(sqrt(M2+z)+M), z=w(w+2M)sum n_i2 exp[-2Hi(t-s)]이다. 초기 angular label에는 J_s=detA_s/|A_s n0|3가 들어간다. 원 quadrature xi_k를 유지해 w_k(E)=xi_k(E-Ba), p_k(E)=normalize[p_k0 fBED(E,w_k(E))/fBED(EP0,w_k0)]로 재가중하고, 현재 same-direction grid에 positive count/first-moment projection한다. Subgrid daughters는 thermal에 직접 배정한다. 매 에너지의 adaptive generator 재실행과 같은 모형이라고 선언하지 않는다.

새 reference는 저장된11-variable static nonlinear reference에 L_t=diag(Wj/Ej0,exp(-ag t),1,1), ag=2theta/3를 적용한 것이다. ||L_t||1<=1이며 counts는 원 reference를 사용한다. 이 계산 가능한 reference와 실제 moving birth-time source 사이의 차이를 모두 새 defect로 계산한다. 새로운 full moving history ODE를 실행했다는 주장은 하지 않는다.

## 2. 새 residual과 nonzero-work guard

Full fixed-gas collision matrix는 Metzler/column-sum0이고 moving-coordinate dot(R)R^-1 및 bath work diagonal은 비양수다. 선형 전파자는 norm<=1이다. Gas feedback은 새 moving bounds에서

    Gamma_j=2Ej0[sum kappaBar_ja/(V0 Ba)+dLambdaBar_j/(V0 Emin)],
    L=max_P Gamma+S0 max_S Gamma+A0 Gamma23+h sum_j Gamma_j sum_a rho_a0 m_ja0

로 제한했다. L은 약1.75880002147704e-5/s다. 모든 stopping event 비용은2Eparent다.

Omitted newborn reactions, retained P1/P2 ionization, terminals, anchor mismatch, moving source reweight/projection/angular Jacobian, energy/density/volume rate shifts, adiabatic heat mismatch를 포함하여

    ||r(t)||1<=sum C_r t^r/r!,
    B(t)=sum C_r t^(r+1) phi_(r+1)(L t),
    phi_m(x)=sum_(k>=0) x^k/(k+m)!.

Positive series/tail을 directed Decimal65로 계산했다. Heat mismatch sum만 C_U t로 남고 다른 collision/source columns는 energy conservative다. D*=2Hmax에서 DeltaPre<=D* integral B+C_U t2/2다.

각도별 최소 energy는 z축 W23,z다. Affine guard

    Gz=W23,z[16+CH/BH+CHe/BHe-sum integral Kj/Wj]-eta U

의 gradient oscillation을 사용하면 |deltaGz|<=CG B+(eta/2)|Delta|, CG=(eta+E23/BH)/2다. Static guard와 reference lift의 차이에는 [exp(ag t)W23,z-E23]Bcap가 남으며, rz>ag에서 절댓값<=(D*-ag)E23 t Bcap다. 이 항을 버리지 않았다.

새 signed barriers10000/15000s와 full transversality>7.08492071709157e-10eV/s를 확인했다. Finite first-event radius는0.150123807678s 미만이며 full first contact는[11965.71544641560,11966.01569403099]s다.

## 3. Continuum angular shell을 하나의 cluster로 닫는 조건

첫 minimum-energy seed의 count a, pre-capacity Bcap, shell range[wmin,wmax]에 대해 seed reset이 cutoff를 올리는 양은

    Jseed=(eta-1)wmin a/(Bcap+a).

Jseed>wmax-wmin이면 남은 전방향 shell이 즉시 eligible하다. Seed reset 후에도 평균energy<=wmin이므로 더 높은 shell 부분을 합산할 때 평균/cutoff가 감소하지 않는다. 연속 angular measure의 count와 energy를 적분해 하나의 aggregate reset으로 끝낸다.

이번 whole-domain 값은 a_seed>0.000969170514346291, angular width<3.136500000000001e-11eV, seed jump>8.01087768909538e-5eV다. Bcap+a<=26을 사용한 충분 seed threshold는3.794594595195e-10count 미만이다. 따라서 유한 ray sample에 기대지 않고 전각도 편입을 닫았다. 다음 shell24는 reset 후에도 active로 남는다. Seedless/grazing에서는 이 충분조건을 사용하지 않는다.

저장된10000s pre endpoint에서 새 event interval로 Taylor6/Picard/order7 extension을 한 번 수행했다. Full event state:

- Tpre in[101.10436411948730,101.10436411948768]K.
- Tpost in[101.19325489121,101.19325494273]K.
- HI extent in[1.42852051934,1.43431271984]e-9.
- HeI extent in[7.91035549185,8.22909334525]e-11.

두 이온화 하한이 양수다. Low/next-shell margins도 엄격히 양수다. 온도 jump는 finite-bin instantaneous thermal closure의 결과다.

## 4. Reset timing과 current의 유한오차

Physical reset은 current energy W23를, reference lifted reset은 exp(-ag s)E23를 bath로 옮긴다. 이 차이는 epsilonR<5.227500043230e-14eV로 따로 제한했다. Physical reset norm1을 적용하고 이 defect만 더한다.

Reference 두 reset시각 사이의 common-final flow를 미분해 적분하면, 새 Mstatic과 delta_t로

    epsilon*=epsilonR+Mstatic delta_t,
    E(t)<=B(t)+exp(Lt)epsilon*

가 두 path가 모두 reset한 시각에 성립한다. 원 witness의 infinitesimal saltation norm2.0209를 복사하지 않았다. h에서 B<9.601502104062e-9eV, total state radius<1.227277047794e-8eV이며

    T_radius<7.295032313199e-6K,
    Tfull(h) in[101.20671610692,101.20673069700]K.

기존0.001K 예산을 충족한다. 한 path만 reset한 window는 작은 state bound 대신 explicit jump norm과 full heat-power로 처리하여 T<101.26857976314K를 얻었다. 그 뒤에는 whole reference tubes와 E(t)를 사용한다. 모두 W24,min cutoff 아래여서100000s까지 두 번째 shell 사건이 없다.

Nonzero work와 비동기 window를 포함하면 Delta(h)<8.104747075835e-14eV, integralDelta<6.186633311839e-9eV*s다. Latest HE44의 계약에 맞춰 먼저 cross-section-free column을 계산한다. Normal clock에서

    Cref=c/V0[3(1-exp(-theta h))/theta+integral exp(-theta t)(xH+xHe)dt].

Saved positive static J에 exp(-theta h)J<=weighted J<=J를 적용한 새 enclosure이며 static center를 복사하지 않았다. Full column in[89399726752864.50828,89399726760211.73435]m^-2. SigmaT=6.6524587051e-29m2를 한 번 곱하면

    tauFull in[5.94727990470654,5.94727990519532]e-15,
    tauRadius<2.443855825416e-25.

Initial-census excess는 양수다. Conditional probability1-exp(-tau)도 평가했지만 foreground는 null이다. 일반 clock에는 D/A와 spatial current term을 유지한다.

최신 REI115 R6의 observable-projected event/slope-jump 구조를 적용했다. 현재 subthreshold shell23는 ionization rate0이고 reset은 other donor/neutral stocks를 바꾸지 않으므로 total Nfree뿐 아니라 Nfree'도 연속이다. Smooth V를 포함한 optical rate ell과 ell'가 연속이어서 direct optical saltation row와 첫 slope-jump interpolation term은0이다. 이후 stopping/work/chemistry response까지0이라고 결론내리지 않는다.

## 5. Evidence, source reuse, next

실제 Wolfram15.0.1:22 scalar literal-zero residuals, fast-axis conditionTrue. 공식 hash를 대조해 load한 실제 xTensor1.3.0:8 tensor literal-zero residuals. 별도 Fraction/mpmath85/NumPy checks185passed. Parent/static/full history ODE는0runs, 새 local extension1step. Point full-sharing arithmetic은 float와longdouble이 혼합되며 separate sanity allowance를 interval proof에 넣지 않았다.

새 checker의 subgrid projection-domain 오류와 longdouble serialization failure를 보존했다. Thermal boundary ownership 및 diagnostic serialization만 수정했고 certificate/source/허용차는 유지했다. Scalar pre-analysis L warning, web cache misses, host TERM diagnostic도 남겼다. Tests-after이며 전체 TDD campaign이라고 주장하지 않는다. Same-author separate CAS/arithmetic이고 external independent review/native subagents는 NOT_RUN이다.

실제로 읽은 HE44 db92d431453a93913ba63e47d7ea92934ad11e20의 full R9, HH61 f4e7d717dc9d358026d86bab3836bdcf5f476323의 detailed PR, REI115 7782c0fd819400ae9e06a97e283d72779ddfc40c의 full new R6 diff를 기록했다. HH numerical rate/observer fixture는 수입하지 않았다. SciSpace와 Exa primary passages는 Le-Cambier2017/Taitano2019/Kong2024의 일반 conservation/moving-coordinate/saltation 맥락으로 사용했으며 이 source-specific certificate나 최초성의 근거로 오인용하지 않는다.

재현: `python src/moving_certificate.py`, `python src/event_state.py`, `python checks/validate.py`, `python checks/verify_bundle.py`. 실제 source code, all new results, immutable parent archive and selected kernel sources are in the linked ZIP. Forty new manifest payloads and nested CRC verified;162read-only packaging/source checks are not162scientific claims.

다음 READY는 `NT_CONTINUOUS_ANGULAR_PREFIX_FRONT`: 유한 angular delta seed를 없앤 smooth shell에서 angular threshold front/onset/feedback와 finite error를 구성한다. 원 all-angle seeded result와 seedless model을 구분한다. Unselected DAG와 원 F/G/atomic/b-grid/globalREI 및 CR/RCT/HH OFF는 유지한다. No old-suite replay, full generator, HPC, native receiver, main merge, force push or permission change.
