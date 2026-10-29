# CR_PHYS03_RR_TEMPORAL_FIRST_ABSORPTION_V1

## 정의와 물리 범위

부모는 BASS-CR PR127 (`631130bb0210a2fd6ec385b17f32ac99c64950ed`); 방출 원본은 PR125의 바이트 고정 SOURCE ZIP이다. 사양은 original PR110 `PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED` prescribed gas-rest 상태이며 관측 시각은 proper seconds. 전자 온도 100 K, H I 수밀도 `138.6 m^-3`, He I 수밀도 `11.427127659574467 m^-3`, 시간 구간 `[0,2.5e9,5e9,7.5e9,1e10] s`를 원본에서 가져온다. 원본의 H 및 He ground-RR 발생광자 에너지는 각각 `E_e+13.60 eV` 및 `E_e+24.59 eV`; 원자 3,200개×채널 2×시간구간 4개의 비음수 적분 가중치 `w_cji`는 `m^-3`. 광자 방출 시각의 정확한 분포는 알 수 없고 각 원본 구간 `[l_j,r_j]` 안의 임의값만 허용한다.

Verner et al. (1996) ApJ 465, 487, DOI `10.1086/177435`의 H I/He I 원래 ground-state photoionization fits를 사용한다. 원본 Table 1 두 줄은 부모 PR127에 이미 바이트 고정돼 있다. 이 연구는 새 fitted cross-section을 추가하지 않는다. 각 target `a`의 흡수계수는 `alpha_a(E)=n_a sigma_a(E) [m^-1]`, `alpha(E)=sum_a alpha_a(E)>0`이고, 광자는 모델의 정지·균질 매질을 직선으로 `c=299792458 m s^-1` 속력으로 이동한다. 광자의 산란, redshift, 자발·유도 재방출, 광원/흡수체 자기피드백, 시간의존적 중성분율, secondary electron, thermalization은 **계산하지 않는다**.

## 정리: 누적 원자별 첫 흡수의 최적 interval

한 광자의 발생 시각 `s in [l_j,r_j]`, 관측 시각 `T>=0`, 파장 대신 광자 에너지 `E`, 흡수 target `a in {H I,He I}`에서,

`P_a(E;s,T) = (alpha_a/alpha) [1 - exp(-c alpha (T-s)_+)]`, `(x)_+=max(0,x)`.

이는 `s>T`이면 0이고, `s<=T`이면 경쟁하는 상수 hazard `c alpha_a`의 first-event probability다. `alpha_a>=0`, `alpha>0`로부터 `dP_a/ds = -c alpha_a exp[-c alpha(T-s)] <= 0` (`s<T`). 따라서 원본 측도 가중치를 바꾸지 않는 모든 허용 발생시각 배치에 대해 최적 누적 하한/상한은

`A_a^-(T) = sum_{c,j,i} w_cji P_a(E_ci; r_j,T)`;
`A_a^+(T) = sum_{c,j,i} w_cji P_a(E_ci; l_j,T)`.

서로 다른 원자/시간구간 발생시각에 대한 추가적인 결합 제약이 없을 때 하한은 모든 광자를 오른쪽 구간 끝에, 상한은 왼쪽 끝에 두어 동시에 달성할 수 있다. 이것은 현재 소스 계약에 대한 *sharp pointwise enclosure*이며 확률적 발생시각 분포를 추정하는 것이 아니다. `T`에 걸친 photoionization 상·하한은 각각 단조 비감소하고 음수가 될 수 없다.

## 광전자 에너지·threshold의 분리

광자 `E`가 species `a`를 photoionize하면 광자에 의해 새로 가능한 일차 광전자의 운동에너지는 `K_e=(E-I_a)`, `E>=I_a`로, 해당 channel/target/시간/에너지 bin의 누적 count는 `w P_a`. 응답 측도에 대한 세 비음수 적분은 다음이다.

`U_a(T)=int E dA_a(T)`;
`U_ion,a(T)=I_a A_a(T)`;
`U_e,excess,a(T)=int (E-I_a) dA_a(T)`.

각 허용 history에서 `U_a = U_ion,a + U_e,excess,a`가 성립하고, 적분 integrand가 모두 비음수이므로 단조 time endpoint를 사용한 상·하한에 같은 identity를 적용할 수 있다. 단위는 J m^-3이고, `1 eV = 1.602176634e-19 J` (정의상 정확). `U_e,excess`는 **일차 광전자에 공급되는 운동에너지 예산**이지 gas heat, deposition, ionization feedback 또는 EOS 변화가 아니다. 새 물리 데이터 산출물은 각 `T=0,1.25,...,10 Gs`에서 1 eV 단위의 `[k,k+1)` 광전자 운동에너지 bin별 source-parent/target count의 하·상한이며, bin 열의 물리 단위는 m^-3 (density per eV로 쓸 때는 bin 폭 1 eV로 나눈다).

## 생존 광자의 별도 envelope

`S(E;s,T)=1[s<=T] exp[-c alpha(E)(T-s)]`는 시각 `T`에 이미 방출되어 아직 첫 흡수를 겪지 않은 광자의 조건부 기대존재수다. 발생구간 `[l,r]`에 대해서 `(S_min,S_max)`는

* `T<l`: `(0,0)`;
* `l<=T<r`: `(0,1)`; 구간 내 미래에 방출할 수도, T에 바로 방출할 수도 있기 때문;
* `T>=r`: `(exp[-c alpha(T-l)], exp[-c alpha(T-r)])`.

이것들은 개별 `T`에 대한 sharp bounds다. 발생·흡수·생존의 각기 **독립적으로 극대/극소한** envelope를 동일한 emission-history의 실현값으로 동시에 더해서는 안 된다. 단, 최종 `T=r_4`에는 모든 원본 광자가 반드시 방출되므로 `S^-+A^+=N_source`, `S^++A^-=N_source`가 성립한다.

## 검증·유효범위

1. `T=1e10 s`의 first-absorption number/energy/target partition은 원래 PR127과 일치해야 한다. 따라서 기존 결과를 반복하지 않고 실제 시간별 출력으로 확장한다.
2. `H-RR -> He I` 광자는 모두 He I 24.59 eV 이하이므로 channel이 엄밀하게 0이다.
3. 모든 원본 에너지는 Verner Table 1 적용 범위 안; `E_gamma`의 redshift 및 time-varying threshold는 사용하지 않는다.
4. 원자별 1 eV kinetic histogram 합은 그 channel/target 누적 count에 반드시 일치한다.
5. source cross-section, prescribed densities 또는 bin support가 바뀌면 새 source identity와 다시 검증한 contract가 필요하다.

## 외부 원전

- Verner, Ferland, Korista & Yakovlev (1996), ApJ 465, 487, DOI 10.1086/177435, https://www.pa.uky.edu/~verner/photo.html
- Switzer & Hirata (2008), Phys. Rev. D 77, 083006, DOI 10.1103/PhysRevD.77.083006: 실제 우주론적 He I continuum opacity는 방출선 transfer와 HI photoabsorption을 결합해야 한다. 이 연구는 그 문제의 해답이 아니라 source-frozen 국소 control이다.

## 증거 상태

- 수학적 interval lemma: `derived`; Wolfram에서 범위 내 도함수·에너지 identity 검산.
- 원본 모델 source/Verner cross sections: `literature_supported/source_locked`.
- 시간·광전자 스펙트럼 산출: `numerically_checked/implementation_verified` within stated source.
- 실제 이온화 반응속도 이력·가스 가열·우주 광학깊이·exclusive He kernel: `unresolved/HOLD`.
