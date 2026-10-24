# 유한 온도 ee 계수와 cutoff 원장의 독립 재사용 검토

검토 단위: `CR_N4_STOPPING_KERNEL`의 선행식 재사용 판정.  
검토자: `/root/stopping_physics_review`. 이 검토자는 구현을 작성하지 않았다.  
적용 규약: `physmath-research-loop` 내장 1.0.0의 R2/R5/R6 및 공통 연구 정책. 별도 재귀 검토를 만들지 않는다.

## 판정

표준 Maxwell 배경의 시간당 에너지 drift/diffusion 식, 같은 cutoff를 쓰는 수·에너지 원장, 고정 bath first-passage 공식은 **PR59의 완료 근거에 이미 존재한다**. 아래 독립 유도와 원전 대응은 그 식들과 일치한다. 상태는 `REUSED_MATCHED`; 새 ee 이론 또는 새 solver의 성과로 세지 않는다. 현재 과제의 유용한 다음 변경은 C23B 공급자를 기존 연산자에 연결하는 입력·단위·bath 소유권의 결속이다. PR60–64의 finite-bath/nonlinear 연산자와 현재 공급 입력 사이의 대응은 root의 별도 선택·검토 대상이다.

실제로 읽은 기존 파일:

| 파일 | bytes | SHA256 |
|---|---:|---|
| `research/cr_coulomb_partition_20261014/coulomb_partition.py` | 3984 | `0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86` |
| 같은 디렉터리 `RESULT_AND_DELIVERY_KO.md` | 11636 | `899a0c79e190e07944e0eba49cad13b316a59f8bd2ca6fbcce89d97b77e627d0` |

현재 intake의 PR59 head는 `029b2122db4f76f5a639e8ae4d58cf552e71b91d`; 보고서는 테스트된 코드의 원 게시 commit `7900d17dcf4f13c07cdd144b1abc85e53811e3e4`를 보존한다. 이번 검토는 이 두 role을 합치지 않는다. 파일 취득의 Git blob 확인은 intake 소유 기록을 사용한다.

## 1. 물리적 정의와 원전 대응

가정은 비상대론적·비축퇴·약결합 plasma, 등방 dilute test electron, 정지 Maxwell 전자 bath, 일정한 leading Coulomb logarithm이다. `n_e,th`는 **열 bath 전자의 proper density**다. 자유전자 총밀도에서 자동으로 대입하지 않는다. 이 소단위의 fixed thermostat는 finite-bath 온도 진화와 구별한다.

SI에서 \(E=mv^2/2\), \(\theta=k_BT>0\), \(v_T=\sqrt{2\theta/m}\), \(x=v/v_T\)로 두고

\[
\Gamma=\frac{4\pi n_{e,\mathrm{th}}e^4\ln\Lambda}{(4\pi\epsilon_0)^2m^2},\qquad
G(x)=\frac{\operatorname{erf}x-x\operatorname{erf}'x}{2x^2}.
\]

Jeffrey et al. (2014)의 Appendix 식 (1)–(4)를 직접 읽어, \(D_{vv}=\Gamma G/v\), velocity flux의 friction \(F_v=-2\Gamma x^2G/v^2\) 및 원전의 \(\Gamma\) 정규화를 확인했다. 원전의 \(v_{\rm th}\)는 \(\sqrt{k_BT/m}\)이므로 이 문서의 \(v_T=\sqrt2v_{\rm th}\)와 대응한다. 원전은 cgs이며 위 식에 SI Coulomb 상수를 명시했다. [P1]

**이후 식은 직접 변수 변환한 결과다.** 등방 위상공간 밀도 \(f(v,t)\)의 radial 식은

\[
\partial_tf=v^{-2}\partial_v\{v^2D_{vv}[\partial_vf+(mv/\theta)f]\}.
\]

수/에너지 밀도 \(F(E)=4\pi vf(v)/m\)를 사용하면

\[
\partial_tF=-\partial_E(AF)+\partial_E^2(DF)=-\partial_Ej,
\quad j=AF-\partial_E(DF),
\]
\[
D=m^2\Gamma vG(x),\qquad
A=m\Gamma v^{-1}[2x\operatorname{erf}'x-\operatorname{erf}x].
\]

여기서 \(\mathrm{Var}(dE)=2Ddt\), \([A]=\mathrm{J/s}\), \([D]=\mathrm{J^2/s}\)다. velocity-density에서의 미분과 radial Jacobian을 포함하면
\(A=m(3D_{vv}+vD_{vv}'-mv^2D_{vv}/\theta)\)가 된다. \(2G+xG'=x\operatorname{erf}'x\)를 넣어 위 \(A\)를 얻는다.

원전 본문의 path-length SDE는 \(ds=vdt\)로 generator를 시간 변환해야 한다. drift에는 \(v\), noise amplitude에는 \(\sqrt v\)가 곱해져 같은 \(A,D\)가 나온다. 원전의 electron **flux** spectrum과 여기의 electron **count** spectrum을 동일시하지 않는다.

공식 PlasmaPy `SingleParticleCollisionFrequencies` 소스의 독립 표현은 \(y=x^2\), \(\psi(y)=\operatorname{erf}x-x\operatorname{erf}'x\), \(\nu_\epsilon=2[\psi-\psi']\Gamma/v^3\)이다. 따라서 \(A=-E\nu_\epsilon\)가 같은 결과를 준다. 해당 구현은 실제로 읽었으며 설치하거나 실행하지 않았다. [P2]

## 2. 평형과 극한: 현재 구현의 대응

\[
\pi(E)=\frac{2\sqrt E}{\sqrt\pi\theta^{3/2}}e^{-E/\theta},\qquad
A=D'+D\left(\frac1{2E}-\frac1\theta\right),
\]
\[
j=-D\pi\,\partial_E(F/\pi).
\]

따라서 \(F\propto\pi\)이면 \(j=0\). 수렴하는 경계 조건 아래 수 보존과 배경에 대한 signed kinetic-energy exchange는 \(\dot U_{\rm test}=\int AF\,dE\), \(\dot U_{\rm bath}=-\dot U_{\rm test}\)다. 실제 finite-bath closure에는 bath shape와 reciprocal terms의 계약이 더 필요하다.

\[
E\downarrow0:\quad
A\to\frac{2m\Gamma}{\sqrt\pi v_T}>0,\quad
D=\frac{4m\Gamma}{3\sqrt\pi v_T}E+O(E^2).
\]
\[
E/\theta\to\infty:\quad A\sim-m\Gamma/v,\quad D\sim\theta m\Gamma/v.
\]

PR59 코드는 \(W=E/\epsilon_{\rm eV}\), \(\theta_W=\theta/\epsilon_{\rm eV}\), \(b_0(W)=b_*\sqrt{W_*/W}\)를 쓴다. 물리적 밀도와의 대응은

\[
b_*=\frac{m\Gamma}{\epsilon_{\rm eV}v(W_*)},\quad
D_W=D/\epsilon_{\rm eV}^2,\quad a_W=A/\epsilon_{\rm eV}.
\]

코드의 `gammainc(1.5,W/theta_W)`는 위 \(\psi\)와 같고 `drift=b*(dAdx-A)`가 위 signed drift다. `energy_flux`, `reversible_generator`, `bath_energy_rate` 및 `moving_interface`는 각각 divergence flux, finite-band detailed balance, opposite kinetic moment, 공통 cutoff 원장을 구현한다. running-log 옵션은 기존 문서가 명시한 별도 평형보존 확장이며 일정 로그의 원전 계수와 합치지 않는다.

## 3. moving-cutoff diffusion 원장: 기존 식 재사용

\(c(t)=K_c(t)>0\), active 영역 \((c,\infty)\), \(j\)는 큰 에너지 방향으로 양수다. source/work를 일단 분리하고, 필요한 경계 항이 무한대에서 사라지는 경우

\[
J_{\rm in}=\dot cF(c)-j(c),\quad
\dot N_{\rm active}=-J_{\rm in},\quad
\dot U_{\rm active}=-cJ_{\rm in}+\int_c^\infty j\,dE.
\]

\[
\int_c^\infty j\,dE=\int_c^\infty AF\,dE+D(c)F(c).
\]

즉 같은 분할의 core/bath energy 원장은

\[
\dot U_{\rm core}=cJ_{\rm in}-\int_c^\infty j\,dE
=cJ_{\rm in}-\int_c^\infty AF\,dE-D(c)F(c).
\]

**재사용 결론:** PR59의 `Jrel=-Jin`, `IC=int_tail j_C`와 `moving_interface`가 바로 이 식이다. 새 구현 변경 요구가 아니다. `b_coll=-A`만 적분하고 diffusion boundary 항을 생략하는 새 adapter는 이 원장을 깨뜨린다. absorbing \(F(c)=0\)를 선택한 별도 문제에서는 해당 항이 0이다. 기존 \(\partial_K(\dot KF)\)의 drift-only 약식은 FP 도입 시 전체 current \(j\)로 대응해야 한다.

Maxwell 평형에서 \(\int_c^\infty AF=-D(c)F(c)\)이므로 bulk current와 분할 energy change가 모두 0이다. 이 관계는 새 인터페이스가 잘못된 추가 가열을 만들지 않는 판별 기준으로 사용할 수 있다.

## 4. 시간 척도의 의미

\(E/|A(E)|\)는 국소 mean-drift 척도이며 \(A=0\)인 곳에서 발산한다. cutoff 도달시간과 동일하지 않다. 고정 \(c>0\) absorbing, \(E_R>c\) reflecting 문제의 첫 도달시간은

\[
A\tau'+D\tau''=-1,\quad\tau(c)=0,\quad\tau'(E_R)=0,
\]
\[
\tau(E)=\int_c^E\frac{dz}{D(z)\pi(z)}\int_z^{E_R}\pi(u)\,du.
\]

이는 \((D\pi\tau')'=-\pi\)를 적분해 직접 얻는다. **동일한 공식과 이미 실행한 source-anchor 예제가 PR59에 있다.** 그 과거 숫자를 새 C23B 입력의 결과로 옮기지 않는다. 새로운 입력의 시간 척도가 필요하면 bath, source, cutoff, upper boundary, escape/evolution time을 새로 결속해야 한다. 이 첫 진입 문제는 재진입을 허용하는 전체 Maxwell화 문제와 서로 다른 관측량이다.

## 근거와 실제 상태

- [P1] Jeffrey, Kontar, Bian, Emslie (2014), arXiv:1404.1962, DOI `10.1088/0004-637X/787/1/86`: https://arxiv.org/pdf/1404.1962 . 실제 읽기: 본문 식 (8)–(13), low-energy 설명, Appendix 식 (1)–(15)의 추출 text. PDF 시각 판독은 수행하지 않았다.
- [P2] PlasmaPy 2026.2.0 공식 문서의 실제 source: https://docs.plasmapy.org/en/stable/_modules/plasmapy/formulary/collisions/frequencies.html . `SingleParticleCollisionFrequencies`의 식·`energy_loss`·`parallel_diffusion`·`Lorentz_collision_frequency`·`phi` 구현을 읽었다. 실행/벤치마크는 `NOT_RUN`.
- 기존 코드/보고서: https://github.com/cosmosapjw-quantum/bass_cr/tree/029b2122db4f76f5a639e8ae4d58cf552e71b91d/research/cr_coulomb_partition_20261014 . 실제 로컬 선택 원문 두 개를 읽었다.

**EXECUTION:** 원전 읽기·독립 대수 유도·기존 코드 대응 완료. 새 수치 실행 0, 이전 과학 replay 0.  
**PUBLICATION:** 이 검토는 로컬 원문이며 root의 게시 결정 대기.  
**BACKUP:** 이 검토 자체의 신규 전송 `NOT_RUN`; 과거 backup 상태를 승격하지 않음.  
**DAG:** 표준 ee 계수·moving-interface·MFPT 공식은 `REUSED_MATCHED`. 현재 C23B-to-stopping 공급 계약과 실제 적용성 검증은 별도 진행. Full stopping/neutral/inelastic/isotope 및 integrated thermochemistry completion은 이 검토의 판정 대상 밖이다.

새 strong no-go를 채택하지 않으므로 NG1–NG7 새 성과 admission은 `NOT_APPLICABLE`. 출처 미확보를 물리적 불가능성으로 해석한 항목은 없다. 본 검토 뒤 남는 의무는 실제 선택한 adapter 및 새 입력의 검토이며, 동일 계수의 과거 검산을 다시 실행할 이유는 없다.
