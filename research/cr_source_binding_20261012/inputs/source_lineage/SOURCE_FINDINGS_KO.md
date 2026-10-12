# PHYS01 → PHYS02 전자 소스 계보 확인

대상 commit: `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`.
역할은 후보의 **source 분석자**다. 최종 채택 판정은 하지 않았다. Git 원문, 저장 JSON, 기존 NPZ의 scalar·배열 해시만 읽었다. source 재계산, 배열 합산 정규화 검산, G 구성, 시간전파, 과거 suite 실행은 없다.

## 1. 결론과 범위

**PHYS01과 실제 paired9600 실행은 같은 기본 양성자 주입 모형과 Rudd 원문을 사용한다. 실제9600 fullBED/legacy는 같은 전자 birth 배열과 같은 물리적 진폭을 공유한다.** 이 일치는 단순한 함수 이름 추정이 아니라, 실제 실행 영수증 → 실행 당시 launcher/API 해시 → 해시 확인된 부모 모듈 → 기본 constructor로 연결된다.

다만 PHYS01은 정확 collisionless Bianchi 수송으로 얻은 최종 양성자 개체군에 FS10 terminal 전자 응답을 합성한다. PHYS02는 그 소스의 **초기 국소 근사** `Qe(W,t)=t A(W)`와 별도의 고정 bath causal cascade를 사용한다. 따라서 PHYS01 terminal 가열률과 M0 응답의 직접 동일성은 성립하지 않는다. M0까지의 D/E/F pulse/cache 경로는 부모 분석자가 별도로 담당한다.

## 2. 정확한 소스 정의와 단위

[ADER]의 식 (2), [A] `DirectElectronSource` lines175–225:

\[
A(W)=\sum_{s=\mathrm H,\mathrm{He}}n_{s,0}
\int_{1\,\mathrm{MeV}}^{4\,\mathrm{MeV}}
q_p(K)v_p(K)\frac{d\sigma_{p,s}}{dW}\,dK,
\qquad Q_e(W,t)=tA(W).
\]

| 양 | 정의/단위 | 직접 근거 |
|---|---|---|
| `qp(K)` | 각도 적분된 양성자 `dN/(proper m³ s dK)`, 즉 m⁻³ s⁻¹ eV⁻¹ | [INJ] lines173–190 |
| `dσ/dW` | m² eV⁻¹, 중성 원자 H·He의 proton-impact ionization | [RUDD] lines1–17,37–48 |
| `A(W)` | m⁻³ s⁻² eV⁻¹ | [A] lines188–206와 위 식 |
| `Qe(W,t)` | m⁻³ s⁻¹ eV⁻¹ | [A] lines11–12,175–180 |
| `selected_A_energy` | `∫[0.1,900] W A(W)dW`, eV m⁻³ s⁻² | [A] lines219–225; [B] lines77–88 |
| `energy_scale_eV_m3` | `T_END² × selected_A_energy` | [B] line88 |

양성자 spectrum은 `leite_shape = beta⁻¹ (p/p0)^(-alpha)`이고 `K0=1 GeV`다. `qp`의 정규화는 **10 keV–1 PeV 전체 주입 에너지**에 대해 정해진다. 1–4 MeV 충돌 창을 다시 전체 source power로 정규화하지 않는다. `proper` 변환 `(1+z)³`는 `InjectionModel.power_proper_J_m3_s`에서 이미 적용된다. 추가 `4π`, `(1+z)³`, 또는 충돌 창 재정규화를 붙이면 다른 source가 된다. [INJ] lines8–13,29–32,85–97,121–129,156–190,207–209.

## 3. 실제 기본값과 고정 bath

| 항목 | 사용 값 | 확인 수준 |
|---|---:|---|
| `z_snapshot` | 8.0 | PHYS01 저장 audit +9600 실행에 묶인 constructor |
| `alpha` | 2.2 | 동일 |
| `supernova_energy_J` | 1e44 J | 동일 |
| `cr_efficiency` | 0.1 | 동일 |
| `escape_fraction` | 1.0 | 동일 |
| `k_cc_per_solar_mass` | 0.0068 | 동일; MD14 Salpeter convention |
| `enabled` | True | 실제9600의 인수 없는 `ElectronSource()` → 기본 `DirectElectronSource()` |
| source 정규화 Gauss order | 128 | [INJ] line141 |
| A의 proton log-K Gauss order | 64 | [B] line78 → [A] lines182–195 |
| `nH`, `YHe` | 140 m⁻³, 0.248 | [A] lines192–194, [CCON] fixed_physics |
| 이온화 조성 | xHII=xHeII=0.01, xHeIII=0 | [CCON] line51, [B] lines29–32 |
| 전자 bath 온도 | 100 K, prescribed, feedback 없음 | [CCON] line51 |
| source local horizon | `T_END=1e10 s`, 초기 비열적 population 0 | [A] lines11–12,34,239–242; [CCON] line40 |
| cascade closure | `quantum_constant=0`, sharing order4, source order8 | [CRUN] lines88–89; [CCON] lines52,110–111 |

PHYS01 [P01AUD]에 저장된 값은 `power_comoving_J_m3_s=7.2913192744753696e-37`, `power_proper_J_m3_s=5.315371751092545e-34`, proper 변환 인자729다. 이는 저장값 전사다. 9600 영수증은 모든 constructor 인수를 별도 JSON으로 출력하지 않으므로, 9600 기본값의 근거는 **실제 실행 코드 해시와 transitive constructor 호출 연결**이라고 정확히 표시한다.

이 bath는 native receiver의 별도 xi=0.1 knot와 다르다. 같은 양성자 모형이 있다는 이유로 그 knot에 고정9600 kernel을 적용할 수 없다.

## 4. 실제9600의 원문 호출 연결

1. [C9600RESULT] `provenance.code_config_identities`가 실제 adapter와 `tests/run_targeted.py`, `src/coherent_bed.py` 해시를 보존한다. 저장 상태는 `PASS_SCOPED`, actual_exit0, transport calls2다. [C9600EXIT]는 child/coordinator exit0, timeout false를 기록한다.
2. [C9600LAUNCH] `worker` line51은 `source=api.cc.ElectronSource()`를 호출한다. lines53,56에서 같은 객체를 fullBED와 legacy에 전달한다.
3. [CRUN] line15는 `cc=bed.parent`; `run_grid` lines88–89는 같은 부모 Cascade와 source quadrature를 사용하며 line110이 `physical_energy_scale_eV_m3`와 birth tags를 NPZ에 보존한다.
4. [C] lines12–18은 frozen contract와 parent manifest를 해시 확인하고 B를 import한다. lines65–66은 `Cascade` 및 `ElectronSource`를 B에 연결한다. fullBED의 변경은 전자충돌 ionization atomic representation이다.
5. [B] `ElectronSource` lines77–88 → [A] `DirectElectronSource` lines182–195 → [INJ] `InjectionModel` lines132–141. [CMAN], [BMAN], [AMAN]이 이 경로의 정확 바이트를 확인한다.

| 실제 source/receipt | SHA256 |
|---|---|
| 실행 adapter launcher | `6ede08c6398bd3556b0168832b18dc59d4cbe938e3c4172109be49188613426b` |
| 실행 `run_targeted.py` | `8b86749819172a7174815a10368909f0d6ab988fafc1c5294ecef7ec07f87024` |
| 실행 `coherent_bed.py` | `30e6e043859c3b2014429c5860314e5e6a833381141469eac24cd6293c43acca` |
| actual9600 numerical receipt | `0b33ad9af1be50297e54fa8b38570471c35b5e342ce771d834bb576458a91500` |

## 5. 저장된 W 격자와 amplitude

[B] lines215–220의 grid는 cutoff0.1와 split10, upper900을 사용한다. 실제9600은 low3200/high6400이다. low active nodes는 `linspace(0.1,10,3201)[1:]`, high는 `geomspace(10,900,6401)[1:]`다. 0.1 eV는 active grid의 첫점이 아니라 cutoff/ghost 경계다. [B] lines237–270은 cutoff kinetic energy를 별도 보존한다.

두 actual9600 NPZ에서 읽은 다음 메타데이터와 해시는 같다.

| 저장 항목 | 직접 읽은 값 |
|---|---|
| physical scale | `1.1242596728743301e-13 eV m^-3` |
| time | `[0.0, 1e10] s` |
| birth tags | `direct_0p1_10`, `direct_10_900` |
| energy shape/dtype | `(9600,)`, float64 |
| 저장된 energy index0 /3199 /3200 /9599 | `0.10309375000000001`, `10.0`, `10.007033424904009`, `900.0` eV |
| energy raw C SHA256 | `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292` |
| source_vectors shape/dtype | `(9611,2)`, float64 |
| source_vectors raw C SHA256 | `07dd0fa81154f5aecaf262b00c2adfada21ebc9b2a2dba59703e03e3f5dab609` |

원 NPZ의 whole-file SHA256은 fullBED `7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc`, legacy `a3f81dbbd86c1d0521f962db8a2ee2ed158f613f3f7a069caccbda9c964acda6`이며 actual receipt의 값과 일치한다.

[B] `source_vectors` lines358–369에서 integrand는 `A(W)/selected_A_energy`다. 이는 source 좌표의 에너지 정규화이며 원 양성자 주입 에너지를 재배정하는 물리적 renormalization이 아니다. 두 birth 열은 같은 selected 분모를 사용한다. `η_j=eᵀb_j` 자체의 저장 scalar는 읽은 JSON에서 찾지 못했다. 새 배열 합산은 하지 않았다.

[C9600RESULT]에는 두 모델에 공통으로 다음 입력량이 저장돼 있다.

| tag | injected energy at T [J m⁻³] | injected number at T [m⁻³] |
|---|---:|---:|
| direct_0p1_10 | 5.47033142884169e-34 | 8.583703187582436e-16 |
| direct_10_900 | 8.459279749254517e-33 | 8.304211765519884e-16 |
| selected_total | 9.006312892138684e-33 | 1.6887914953102317e-15 |

기존2400/4800 [CR001] `coverage`의 source 값도 직접 전사한다: all-direct `A_energy=1.5285042578786697e-33 eV m^-3 s^-2`, low `6.828624650684662e-35`, high `1.0559734263674833e-33`, selected fraction `0.7355293039449105`, 최소 표본 endpoint `2154.927725029828 eV`. 이것을 새9600 coverage 계산이라고 표시하지 않는다. `selected_A_energy` 별도 수치 필드는 이 JSON에 없고 정의 및 저장 physical scale이 있다.

### 기존 coverage를 같은9600 source에 연결하는 근거

[CR001]의 `/identities`는 scientific contract, parent manifest, coherent_bed 및 run_targeted의 같은 해시를 보존한다. [CRUN] main line145는 `source=cc.ElectronSource(); result['coverage']=source.coverage()`를 **electron grid loop line146 전에** 수행한다. [B] `ElectronSource`는 electron mesh를 입력받지 않으며, [A] lines219–225의 적분은 proton nodes/weights와 Rudd moment만 사용한다. 실제9600도 같은 constructor를 사용한다. 그러므로 이 coverage는 같은 frozen source의 기존 기록으로 재사용할 수 있다. 새로운9600 source 적분이라고 부르지는 않는다.

[CR001]의 정확 JSON 경로는 `/coverage/band_A_energy_eV_m3_s2`다.

| key | 저장 A-energy [eV m⁻³ s⁻²] |
|---|---:|
| below_cutoff | 1.674709854087335e-38 |
| direct_low | 6.828624650684662e-35 |
| direct_high_selected | 1.0559734263674833e-33 |
| unselected_900_1000 | 3.0326802746639703e-35 |
| unselected_above_1000 | 3.7390103515915917e-34 |

전체 분모는 `/coverage/all_direct_A_energy_eV_m3_s2`, 선택 비율은 `/coverage/selected_fraction_of_all_direct`에 있다. **분모는1–4 MeV proton impact에서 직접 태어난 모든 전자의 kinetic energy**다. 전체10 keV–1 PeV CR injection power 또는 primary target binding을 포함한 에너지와 같지 않다.

## 6. 시간 근사와 과정 구분

[INJ] `transport_population` lines263–274의 정확 최종 population measure는 `exp(-3H age) qp(K_birth) dK_birth dage dmu_birth/2`이며 redshift된 최종 K를 사용한다. [P01] lines74–85가 이 population으로 terminal packet을 만든다.

반면 [ADER] lines58–98은 `Np=t qp+O(H t² qp)`의 leading term을 사용한다. [A] `bianchi_coefficients` lines232–236은 exact transported coefficient를 **비교용**으로 제공하며 source를 교체하지 않는다. [ARES]에는 세 시각 `2.5e9, 5e9, 1e10 s`에서 coefficient 상대차가 저장돼 있고, T에서 약 `6.93e-7`다. 저장된 문구는 명시적으로 “Finite samples, not an interval certificate”다. 이 표본 차이를 연속 이력의 오차 상계로 사용하지 않는다.

| 사건/범위 | 현재 원문에서의 처리 |
|---|---|
| p + neutral H/He primary ionization | Rudd의 primary target-ionization rate와 binding 비용; [P01] lines81–92 |
| 그 사건에서 직접 태어난 전자 | PHYS02 외부 source `Qe`; direct 두 birth tag |
| 전자의 후속 ionization | B/C cascade가 두 전자 daughter와 추가 ionization/binding을 추적; 별도의 외부 birth source로 중복 주입하지 않음 |
| low-energy crossing | high-born 전자의 descendant 경로; low-born 외부 source와 구분 |
| neutron / nuclear channel | 이 경로에 없음. `neutral H/He`는 중성 원자 target이며 중성자라는 뜻이 아님; [RUDD] lines12–17은 nuclear/isotope reaction 미제공을 명시 |
| source 밖의 전자·양성자 / cutoff residue | 생략·미완결 energy로 남기며 heat로 재배정하지 않음 |
| 실제 coupled history와 오차 예산 | 이 source tracing의 완료 범위 밖; 새 소비자 요청의 binding 필요 |

`SOURCE_INVENTORY.json`은 각 식별자의 정확 Git 경로, blob SHA1, raw SHA256, 읽은 범위와 고정 commit 링크를 제공한다. 이 기록은 원문·실행 계보의 근거이며 물리적 정확도 인증을 추가하지 않는다.
