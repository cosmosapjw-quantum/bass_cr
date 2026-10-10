# 실제 CR proton 주입·수송 구현 반환

문헌 원문 결속은 INJECTION_MODEL_KO.md와 INJECTION_SOURCES.json을 따른다. 구현은 src/injection.py, focused 검증은 tests/test_injection.py이며 실제 계산 반환은 evidence/INJECTION_TRANSPORT_CHECK.json에 있다. 저장소 commit은 만들지 않았다.

Leite2017 v1 Eq23의 momentum power-law를 kinetic-energy 변수로 옮긴 q(K)=C beta(K)^−1[p(K)/p(K0)]^−alpha를 그대로 구현했다. alpha=2.2, K0=1 GeV, source support=10 keV..1 PeV이다. C는 전체 source support의 적분 ∫Kq(K)dK가 주입 power와 같도록 정한다. 1..4 MeV collision domain으로 다시 정규화하지 않는다.

MD14 v3 Eq15의 comoving SFRD에 같은 Salpeter convention인 Eq16 k_CC=0.0068/Msun, E_SN=10^51 erg, CR efficiency=0.1, escape fraction=1 시나리오를 곱한다. proper power는 comoving power의 (1+z)^3배이며, 코드의 최종 단위는 J m^-3 s^-1이다. Leite의 다른 IMF에서 유래한 0.01을 MD14 normalization과 혼용하지 않았다. z=0..8만 현재 구현의 명시된 fit-use domain으로 받아들인다.

수송은 non-tilted axisymmetric Bianchi I의 일정한 H,s를 사용하는 정확한 무충돌 characteristic이다. H_perp=H−s, H_parallel=H+2s이며 pc_perp=pc0 sqrt(1−mu0²) exp(−H_perp age), pc_parallel=pc0 mu0 exp(−H_parallel age)이다. 최종 운동에너지는 pc²/[sqrt(pc²+m²c⁴)+mc²]로 계산하여 낮은 에너지에서의 상쇄를 피한다. s=0일 때 방향별로 정확히 p=p0 exp(−H age)를 복원한다.

입자수 가중치는 exp(−3H age) q(K0)dK0 dage dmu0/2이다. 이것은 birth 좌표에서의 적분이므로 별도 final-energy/angle Jacobian을 다시 곱하지 않는다. 각 age,mu0에서 final 1,4 MeV를 inverse characteristic으로 birth K0에 매핑하고, source energy 적분을 below/active/above의 세 매끄러운 구간으로 나눈다. top-hat window를 단순 quadrature 노드에서 잘라서 생기는 불연속 적분 오차를 피한다.

반환 노드는 kinetic_eV, birth_kinetic_eV, mu, birth_mu, age_s, birth_time_s, number_density_m3이다. 이는 **구간 끝 시각의 실제 source-weighted population**이다. 생성 중인 CR의 누적 충돌 수를 구하려면 시간에 대해 population을 추가 적분해야 한다. 최종 rate에 dt를 곱하는 방법은 짧은 turn-on에서 평균 population의 대략 두 배를 쓰는 endpoint 근사이므로 누적 상호작용의 정확한 값으로 표기하면 안 된다.

에너지 반환은 raw proper injected power×dt, 최종 부피 측도로 dilution한 birth energy, 최종 full CR kinetic storage, active kinetic storage, below/above tails와 signed adiabatic work를 구분한다. tail은 unresolved CR storage이며 gas heat로 넘기지 않는다. 한 방향이 수축하는 경우에도 bounded exponent domain에서는 characteristic을 계산할 수 있고 adiabatic work는 부호를 유지한다.

실제 z8, dt=10^10 s, H=10^-14 s^-1 파일럿에서 proper power는 5.315371751092545e−34 J m^-3 s^-1이었다. FLRW final full CR energy는 5.3142525001196285e−24 J m^-3이고 1..4 MeV active fraction은 약 0.00852819이다. s=2e−15 s^-1인 axisymmetric 파일럿도 같은 full source를 사용했다. active population의 가중 P2는 FLRW 약 2.49e−16, axisymmetric 약 −1.67987e−5였다. 이것은 CR 입자 분포의 방향 moment이며 CMB 관측량이 아니다.

14개 focused 검증은 모두 통과했다. 독립 adaptive log-energy quadrature와 source normalization 비교, comoving/proper 변환, exact relativistic round trip, FLRW characteristic, anisotropic component, source cutoff, active-window 변경 시 전체 power 불변, tail partition, number dilution, quadrature refinement, OFF/zero-efficiency의 spectrum no-call, 입력 정의역을 확인했다. 이 “독립 적분”은 다른 수치 적분법을 쓴 owner 검산이며 독립 decision reviewer 판정을 뜻하지 않는다.

현재 계산은 zero initial population에서 시작하는 frozen-z source의 국소 turn-on이다. CR stopping feedback, target evolution, 핵반응, 전 역사 또는 물리적 universe prediction은 수행하지 않았다. 얇은 표적 한계는 이 population을 실제 collision operator에 결합한 뒤 stopping fraction으로 별도 확인해야 한다. 전하·바리온 저장고와 injection-current 가정은 원문 source 보고서의 qualification을 그대로 유지한다.

