# CR_PHYS09 | 중성 H/He 밀도 변동에 대한 첫 광이온화의 인과 응답핵

## 원본과 해석 범위

원본 `BASS-CR PR133` HEAD `7386c9e707405438f1b2f69ad13c5900a575f99e`, complete SOURCE ZIP SHA256 `16d0b7c9e2540777ea0e360511e502303e6ea887ae0ecd658282d14d79923ae4`. 내부에는 PR132 전체 SOURCE ZIP이 **바이트 그대로** 포함되어 있다. 원본 100 K 균질 H I/He I, 3200 H-origin + 3200 He-origin energy atoms, 4 birth-time bins, Verner et al. (1996) 단면적만 사용한다. 현재 밀도는 `n_HI=138.6 m^-3`, `n_HeI=11.427127659574467 m^-3`. Proper time은 초, 광자 에너지는 eV, 광자 수 가중치는 `m^-3`이다.

새 물리 문제: 위 가정으로 계산한 **첫 광이온화량**이, 시간에 따라 달라지는 중성 H/He 밀도에 **선형 차수에서** 어떻게 응답하는지를 source-owner 입력만으로 계산한다. 실제 밀도 이력을 임의 도입하거나 REI/BASS21의 광자원·시계를 결합하지 않는다. 이전 He 이중전자 사건 source kernel 또는 collision energy cap `K`를 추정하지 않는다.

## 정리 1: 인과 Fréchet 응답

광자 기원 p의 고정 에너지 `E`, 출생시간 `s`, 관측 `T`를 고정한다. 고정 배경에서 `k_a=c*n_a*sigma_a(E)>=0` [s^-1], `k=sum_a k_a`, 첫 target `a`의 확률은

`P_a(s,T)=int_s^T k_a(t)*exp[-int_s^t k(v)dv]dt`.

밀도를 시간 의존적으로 변동시키되 원본 단면적·광자 에너지는 유지한다. 임의의 작은 `delta ln n_b(t)`에 대한 첫 차수 변동은

`delta P_a = int_s^T K_ab(t;s,T)*delta ln n_b(t) dt` (b 합),

`K_ab(t;s,T)=k_b*exp[-k(t-s)]*{delta_ab-(k_a/k)[1-exp[-k(T-t)]]}` for `s<=t<=T`.

이는 `delta P_a=direct gain - survival competition`을 Duhamel/Volterra 전개에서 도출한 것으로, 원래 이동 중의 선형 응답이지 실제 화학계 전진 적분이 아니다. `K_ab`의 단위는 `s^-1`, 원본 `w`를 곱해 합치면 `m^-3 s^-1`이 된다.

시간구간 `[u,v]`에 `delta ln n_b=epsilon`이 **상수**인 경우 `L=max(s,u)`, `U=min(T,v)`, `d=max(U-L,0)`,

`A=(exp[-k(L-s)]-exp[-k(U-s)])/k` (L<U, k>0),

`G_ab^[u,v](s,T) = delta_ab*k_b*A - (k_a*k_b/k)*(A-d*exp[-k(T-s)])`.

구간이 광자 출생 전이나 관측 이후면 `G=0`. `k=0`의 결과도 `G=0`. 원래 사건 원자들에 출생 bin 가중치를 곱한 뒤 합산하여 실제 숫자 `dN_abs,a(T)/d ln n_b^[u,v]` [m^-3]를 얻는다.

## 정리 2: 부호·인과성·합 규칙

비음수 두 경쟁위험의 일반 성질에 의해 `G_aa>=0`, `G_ab<=0 (a!=b)`이며 교차 성분은 `G_HI,HeI=G_HeI,HI`(로그밀도 미분 기준)이다. 두 target 합은 명시적으로

`sum_a G_ab^[u,v] = k_b*d*exp[-k(T-s)] >=0`.

즉 중성종 `b`의 밀도 증가가 그 target에 대한 흡수를 늘리고, 다른 target과의 경쟁에서는 흡수를 줄이지만, 총 첫 흡수확률은 증가시킨다. 인접한 8개 perturbation proper-time window의 `G`를 합하면 전체 기간 균일 `delta ln n_b`의 직접 미분과 정확히 같다.

`k_a=0`인 H-origin→He I 성분과 그 흡수종에 대한 어떤 응답도 0이다. 인과 응답은 발광 방향·공간경로가 없더라도 **시간 순서와 원자적 첫 사건**에 대한 기여를 표현한다. 별도의 실제 방출각·수송 거리 또는 열침적을 추정하지 않는다.

## 결과의 물리적 해석과 단계

출생시각을 모르는 기존 4개 bin에 `earliest`, `midpoint`, `latest` 세 개의 **전역적으로 일관된 witness**를 적용한다. 각각의 `G`는 그 witness 하의 실제 source-conditional 수치이며, 모든 가능한 출생시각 분포에 대한 extrema를 자동으로 주장하지 않는다. `formal_delta_n`은 같은 고정-가스 source 단위에서의 일차 계산이 제공하는 순중성종 증분을 **전체기간 균일 로그밀도 섭동**으로 가정해 `G*delta ln n`을 평가한 진단이다. 이는 실제 시간분포의 photo-chemistry feedback 해가 아니다.

최종 시각 `T=1e10 s`, earliest witness에서 `dN_HI/d ln n_HI = 1.622081870638181e-26 m^-3`, `dN_HI/d ln n_HeI = -1.9049811921263098e-30 m^-3`, `dN_HeI/d ln n_HeI=1.9588001379369733e-28 m^-3`. 단일 균일 섭동 진단으로 계산한 전체 첫 흡수 1차 보정 `2.760147434251847e-53 m^-3`, latest witness는 `1.1058536357663236e-53 m^-3`. 매우 작은 값이지만 장부상 formal 결과로만 남긴다.

## 비포함 범위

이 정리는 중성종 density-response operator의 source-conditional 1차 구성이다. 실제 시간 의존 `n_a(t)`, 방향 종속 광자수송, 산란, 에너지 적색편이, 다른 원자상태·재결합 cascade, `K`와 He의 exclusive (e,3e) double-event kernel, 외부전자·partner energy ownership, plasma heating, native25/L4/production은 **입력 부재로 HOLD**한다. 인자 `k`는 광자 hazard이며, 옛 CR budget energy cap `K`와 단위부터 다르다.

원전: Verner et al. (1996), DOI 10.1086/177435; Switzer & Hirata (2008), DOI 10.1103/PhysRevD.77.083006; Chluba et al. (2016), DOI 10.1093/mnras/stv2691. He (e,3e) double-event 소스 후보는 Shah et al. (1988), DOI 10.1088/0953-4075/21/15/019 및 Dorn et al. (2001), DOI 10.1103/PhysRevLett.86.3755이나, **현재 PHYS09 원본에 이들 숫자를 투입하지 않았다**.
