# 결과: H1/He4 neutral elastic energy exchange

## 확보한 결론
선택한 C23D impulsive source와 기존 EE+EI+H(1S→2S/2P) finite chain에 **H1/He4 중성 탄성 에너지 교환의 선도 질량비 Fokker–Planck 항**을 결속했다. 실제 CCC/LXCat MTCS 두 표를 사용하고, 기존 PR103의 grid·source·EE/EI generator·CE hazards 및 baseline 결과는 저장본 그대로 재사용했다.

현재 gate는 **NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_NEUTRAL_FP_FINITE_CHAIN**이다. 독립 R6 및 C9를 통과했다. C9의 reviewer 진단 정의 정정과 원 FAIL은 모두 보존한다. 전체 CR_N5_ATOMIC_ISOTOPE_COVERAGE와 CR_N4_STOPPING_KERNEL은 PARTIAL/OPEN이고 N6/N7을 열지 않는다.

## 조건과 수학
T_e=T_i=T_n=10000 K, theta=0.8617333262145178 eV, thermal n_e=0.14 cm^-3, prescribed lnLambda=20. HI/HII/HeI/HeII/HeIII=(0.9,0.1,0.07,0.02,0.01)cm^-3. Elemental neutral populations를 H1(1S), He4(ground singlet)로 조건부 배정한다. M/me=(1837.152673426,7296.29954171); binding mass defect는 생략했다. Closed box/no escape, stationary isotropic prescribed Maxwell baths다.

원 source exposure10000 proper s는 초기 pulse population을 정의한다. 초기0<W<10eV 선택을 경로의 상단으로 쓰지 않는다. Active first-entry boundary q=chi theta, chi=1.5 또는3; reflecting upper boundary U=Rtheta, R=40 또는80; nominal N=1024/2048을 쓴다. Finest grid는 각 경우2480nodes(2479active)다.

채택한 표준 탄성 operator의 source binding은 다음 식이다.

```text
nu_m(E) = n_N sqrt(2 E e_J / m_e) sigma_mt(E)
D_N(E)  = 2 theta E nu_m(E) / r
mu_N(E) = D_N'(E) + D_N(E) [1/(2E) - 1/theta]
        = 2 nu_m(E)/r [theta(2 + E sigma_mt'/sigma_mt) - E].
Var(dE) = 2 D_N dt.
```

p(E)∝sqrt(E)exp(-E/theta)는 이 flux를 정확히0으로 만든다. 새 conductance c_N=c_EE D_N/D_EE로 두 중성종 generator만 생성했다. 각 bath gain은 같은 Q_species의 -Q_species^T E로 정의한다. Signed gain, 그 norm, absolute-component 합을 구별한다.

전체 stopped-history energy ledger는 초기 선택 kinetic energy = 6bath gains + q first-entry energy + initially inactive own energy + CE outgoing kinetic energy + CE internal gap이다. CE internal gap10.20435eV는 bath heat와 별도다. Elastic channel은 electron·target 수, 전하, 핵종과 ground internal state를 보존한다.

## Finest-grid 결과
아래 delta는 동일 저장 baseline에 두 중성종만 더한 짝지은 비교다. tau_noCE는 CE killing을 끈 active first-entry 평균이며, P_CE는 CE killing을 포함한 별도 resolvent의 선택 source 적분 확률이다. 서로 다른 문제의 평균을 혼합하지 않는다. Neutral heat는 H1+He4 bath 합, **선택 전자 한 개당 micro-eV**이다.

| chi | source z | 새 tau_noCE (proper s) | delta tau (s) | delta P_CE/P_CE_old (%) | neutral heat (micro-eV/selected e) |
|---:|---:|---:|---:|---:|---:|
| 1.5 | 2.316 | 281892.945 | -14.617 | -0.01093100 | 84.2237 |
| 1.5 | 2.479 | 281531.620 | -14.575 | -0.01092663 | 84.0619 |
| 1.5 | 2.649 | 281332.771 | -14.542 | -0.01092073 | 83.9800 |
| 3 | 2.316 | 271366.202 | -18.375 | -0.01096875 | 67.4328 |
| 3 | 2.479 | 270472.156 | -18.292 | -0.01096475 | 67.2522 |
| 3 | 2.649 | 269633.110 | -18.210 | -0.01095926 | 67.1408 |

CE 확률의 상대 감소는 약0.01092–0.01097%, no-CE first-entry 평균의 상대 감소는 약0.00517–0.00677%다. 선택 전자 한 개당 neutral bath gain은6.7141e-5–8.4224e-5eV다. 비교한 stopped-history에서 neutral heat/ion heat는 chi1.5에서 약9.56–9.59%, chi3에서 약14.00–14.04%다. EE gain은 약1.035–1.709eV/selected electron으로 더 크다. 이 비교는 정해진 source·density·boundary·operator에서의 적분 결과이며, 누락된 모든 원자 과정의 전역 우선순위를 주지 않는다.

각 pulse에서 적분한6bath gain은 양수다. 이는 개별 저에너지 전자의 drift가 항상 cooling이라는 뜻이 아니다. 첫 진입은 재진입을 지운 진단이며 irreversible assimilation 또는 Maxwellization이라는 물리적 주장으로 바꾸지 않는다.

## 실제 실행과 검증
- Controls:39checks PASS.
- Primary:8combined matrices,16새 neutral generators,14physical RHS×8=112,24source-integrated rows,18finite comparisons PASS.
- 독립 C9: finest2matrices를 별도 Decimal70 Thomas법으로 해석,14RHS×2=28. 여기에는 t,v_s,v_p가 실제 포함된다. Production science module import0, old baseline solve0.
- 저장된3×384=1152source atoms를8cases에서 평가했다. Private per-atom rows9216은 새로운9216입자 또는 source quadrature가 아니다.
- 새 ODE0, source quadrature0, finite-Maxwell thermal quadrature0, old generator evaluation0, source reprojection0, old primary replay0.

최대 scaled linear residual8.543996e-13(기준2e-12), partition defect5.468693e-11(2e-8), energy ledger defect2.626804e-11(2e-8), no-CE MFPT backward residual1.987883e-16(2e-12)다. 독립28해의 최대 norm-relative 차이는3.061615e-11(5e-10), reference backward residual<8.773e-70이다.

Finite no-CE comparison은 delta=max(c_H+c_He)/c_old=2.1520413e-4에서 Told/(1+delta)<=Tnew<=Told를 만족했다. Grid principal-observable 최대 상대 변화1.143894e-4, upper-boundary 변화5.379659e-11이다. **개별 P_CE의 grid 변화와 중성종 효과 크기가 비슷한 차수**지만, 짝지은 delta(P_CE)/P_CE_old의 grid 차이는 최대1.3821e-9(효과의 약1.3e-5)였다. 후자는 유한 격자 비교에서 신호가 안정적임을 보여 주며 continuum absolute-error certificate를 만들지 않는다.

## 독립 검토에서의 정정
v1은 mpmath 미설치로 실제 child가 초기 실패했다. 기존 PR103의 정확한 pinned wheel만 회수했으며 옛 oracle은 실행하지 않았다. v2에서28RHS·물리 검산은 완료했지만, cancelling signed bath reward의 net norm에 generator2e-13 기준을 적용한4진단이 FAIL이었다.

v4는 그4reward series만 Decimal70으로 다시 구성했다. 기존 고정 independent 기준5e-10에 대한 최대 net-norm 상대차4.440587e-13, 기존 generator 기준2e-13에 대한 최대 absolute-component-scaled 차이1.425949e-19로 모두 통과했다. Production code·입력·허용오차 수치·물리식을 바꾸지 않았다. 원 v2 FAIL과 v3 own-stale-lease refusal도 남겨 두었다. 상세 disposition은 review/ROOT_C9_DISPOSITION_V2.json이다.

## 물리 근사의 남은 범위
Active q에서 theta/(rE)는 H1 최대3.628804e-4, He4 최대9.137052e-5(chi1.5)이고 chi3에서는 절반이다. 그러나 생략한 cold-recoil diffusion의 별도 진단2E/(rtheta)는 R80 상단에서 H1약0.0870913, He4약0.0219289까지 간다. 이 수치는 sigma_2<=2sigma_mt에서 얻은 선도항 비율의 상계 진단이다. 전체 operator·source observable의 엄밀한 오차한계가 아니다.

정확한 finite-M Boltzmann variance, angular second moment, 원 데이터 불확도, 비공통 bath T, bath feedback, missing isotope abundances와 CI/RR/DR/CX coverage가 남는다. MTCS에서 total elastic event rate 또는 event count를 추정하지 않는다. global_error_bound=null, global_completion_percent=null이다.

## 출처와 재사용
원전·데이터 IDs/해시·범위는 SOURCES_AND_COVERAGE_KO.md, 유도는 THEORY_KO.md, 고정 계약은 FROZEN_CONTRACT.md에 있다. PR103 Science d3d9b0de8796de6e988c0d95540b1dbbe1d1cff3, Documents bdcb576f4202be81b7436726eca6b588029de840을 재사용했다. 표준 충돌식 자체를 새 정리로 주장하지 않는다. 이번 기여는 실제 두 MTCS의 source/finite-chain 결속, 새6bath 보존 ledger, 독립 검산과 조건부 경쟁효과 수치다.
