# HeIII ground RR의 native 25좌표 사상 — R5 독립 구성 지원

## 0. 범위와 읽은 근거

작성일 2026-10-27 KST. 본 작업은 부모가 선택한 He4III + tagged fast electron → He4II(ground) + photon 사건의 **정확한 입자수/에너지 사상**이다. R5 구성 지원이며 최종 R6 독립 심사나 새 coupled IVP를 수행하지 않았다. 원 source 코드와 통계 결과를 수정하거나 재실행하지 않았다.

실제 읽은 근거:

- bass_cr local HEAD `b11b2e9255f2b10fb5582376412e045bd1e9151c`, branch `research/cr-heiii-ground-rr-20261027`, 현재 AGENTS SHA256 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`. 새 작업 전 read-only status에서 복원된 input/NPZ/dense CSV의 untracked 상태를 확인했으며 손대지 않았다.
- `research/cr_external_interfaces_20261025/contracts.py`: `Species`, `Event.validate`, `EventBook.append/energy_rates`, `CaloricDerivative.temperature_rate`, `require_physical_provider`.
- 동일 단위 `consume_saved.py`: 기존 HeII label `He4:1`→`He4:2`, `e:fast` 및 `photon`, eV→J와 proper volume/rate convention.
- 회수한 REI source ZIP SHA256 `1b80efed0892f3368dc307e3cd6757b93dc444a4d7d2d186b352b926e230648a`의 `coupled_source_20261027/theory/CONTRACT.md`와 `implementation/coupled_photo_source.py`: native basis 및 \(\zeta,w_{nt},w_{ext},\ell\)의 의미.
- 같은 ZIP의 REC119 `atomic_network.py` 및 `pw19_rec_callback.py`: native index, charge, baryon weights, cumulative ionization energy.

이 네임스페이스는 제공자의 identity와 isotope policy를 그대로 사용한다. PR236의 z=2.479 donor \(n_b,T\)와 CR의 별도 prescribed bath \(n_b,T\)는 서로 다른 물리 입력이다. 아래 사상은 변수·보존법칙의 재사용이며 두 상태를 동일 scenario로 묶는 연산이 아니다.

## 1. native 상태와 정확한 단위

native zero-based 상태 순서는
\[
(n,H1I,H1II,DI,DII,TI,TII,He3I,He3II,He3III,
He4I,He4II,He4III,Li6I,Li6II,Li6III,Li6IV,Li7I,Li7II,Li7III,Li7IV)
\]
이다. 따라서 He4II=index11, He4III=index12, \(q_{11}=1,q_{12}=2\), \(A_{11}=A_{12}=4\)다.

\[
Z=(Y[21],\zeta,w_{nt},w_{ext},\ell),\qquad \ell=\log(T/1\,{\rm K}).
\]

| index | 변수 | 의미/단위 |
|---:|---|---|
| 0…20 | \(Y_i=n_i/n_b\) | ion/heavy-particle count per baryon |
| 21 | \(\zeta=n_{e,nt}/n_b\) | selected nonthermal electron count per baryon |
| 22 | \(w_{nt}=u_{nt}/n_b\) | **J/baryon**; \(u_{nt}\)는 J m⁻³ |
| 23 | \(w_{ext}\) | **J/baryon의 signed external photon-transfer ledger** |
| 24 | \(\ell\) | 무차원 log temperature; proper-time RHS 단위 s⁻¹ |

따라서 \(\dot w_{nt}\)는 J baryon⁻¹ s⁻¹, \(n_b\dot w_{nt}\)는 J m⁻³ s⁻¹이다. 에너지 eV를 쓸 때 \(\epsilon_J=(1.602176634\times10^{-19}\,J/eV)E\)로 한 번 변환한다.

native total free-electron count는 \(x_{e,tot}=q^TY\), thermal electron count는 \(x_{e,th}=q^TY-\zeta\), thermal particle count는
\[
\chi_{th}=(\boldsymbol1+q)^TY-\zeta
\]
다. \(\zeta\)는 총 자유전자의 subset이며 charge neutrality에 다시 더하지 않는다.

## 2. 하나의 RR 사건과 finite extent

이 단위의 미시 사건을
\[
{}^4He^{2+}+e_{nt}(E)\longrightarrow{}^4He^+(1s)+\gamma(E+I),
\qquad I=54.42\,eV
\]
로 둔다. 이 에너지식은 선택된 stationary heavy target/zero recoil, scalar spontaneous ground channel에 해당한다. source-qualified RR 공급자의 cross section, ground assignment, isotope validity는 부모의 source 계약에서 별도로 보유한다.

고정 \(n_b\)에서 \(a\ge0\)를 **사건수/baryon의 유한 extent**로 두고 \(\nu=e_{11}-e_{12}\)라 하면
\[
\Delta Y=a\nu,\quad \Delta\zeta=-a,
\quad \Delta w_{nt}=-a\epsilon_J.
\]
다른 abundance는 그대로다. explicit full event stoichiometry는 He4:2 −1, He4:1 +1, e:fast −1, photon +1이며 e:thermal은 0이다.

핵종과 baryon:
\[
\boldsymbol1^T\nu=0,\quad A^T\nu=4-4=0,
\quad N_{He4}^T\nu=1-1=0.
\]
ionic charge:
\[
q^T\nu=1-2=-1.
\]
따라서
\[
\Delta(q^TY)=-a,\quad
\Delta x_{e,th}=q^T\Delta Y-\Delta\zeta=-a+a=0,
\]
\[
\boxed{\Delta\chi_{th}=(\boldsymbol1+q)^T\Delta Y-\Delta\zeta
=(2-3)a+a=0.}
\]

free electron가 하나 소멸하면서 ionic positive charge가 하나 줄므로 full electric charge는 보존된다. bound electron 수는 하나 늘어난다. free total number의 감소와 nuclei/charge 보존은 서로 다른 진술이다.

finite-update의 coarse necessary domain은 \(a\le Y_{12}\), \(a\le\zeta\), \(a\epsilon_J\le w_{nt}\)다. 실제 energy-resolved update에는 해당 에너지에서 제거 가능한 양의 electron measure가 있어야 한다. 이 세 moment 조건만으로 spectrum support나 finite-step positivity를 인증하지 않는다. 공급자 hazard와 fast measure가 이 조건을 보유한다.

## 3. 에너지와 photon 소유권

native \(I_i^J\)는 cumulative ionization energy per ion이다. He4II→He4III threshold 때문에
\[
I_{12}^J-I_{11}^J=I_J,\qquad I_J=54.42\,eV\times (J/eV).
\]
그러므로 RR의 내부 에너지 변화는
\[
\Delta w_{ion}=I^{J,T}\Delta Y=-aI_J.
\]

선택된 **retained photon** 계정은
\[
\Delta w_{\gamma,ret}=a(\epsilon_J+I_J).
\]
thermal, recoil, escape, external 계정의 이 선택 사건 기여는 모두 0이다. 따라서
\[
\boxed{\Delta w_{ion}+\Delta w_{nt}+\Delta w_{\gamma,ret}
=-aI_J-a\epsilon_J+a(\epsilon_J+I_J)=0.}
\]
binding은 native \(I^{J,T}Y\)가 소유한다. 여기에 별도 evolving binding state를 중복 추가하지 않는다.

### 25좌표에 필요한 하나의 명시적 output port

기존 REI의 index23 \(w_{ext}\)는 열린 photon bath와의 **external transfer ledger**다. retained emitted photon density와 의미가 다르다. 기존 25좌표 semantic identity를 보존하는 최소 사상은
\[
\boxed{\Delta Z=(a\nu,-a,-a\epsilon_J,0,0)}
\]
와 별도 반환값
\[
\boxed{\Delta N_{\gamma,ret}/N_b=a,\quad
\Delta w_{\gamma,ret}=a(\epsilon_J+I_J)}
\]
를 함께 내는 것이다. photon carrier를 실제 진화시키는 후속 소비자는 이 port를 받아야 한다.

단순히 기존 photo source의 모든 부호를 바꾸어 \(\Delta w_{ext}>0\)를 넣으면 emitted energy를 prescribed external reservoir로 보내는 **다른 경계 계약**이 된다. 이는 algebraic inverse ledger로는 정의할 수 있지만 현재 closed-box retained-photon RR의 동일 계약이 아니다. 닫힌 광자 모델에서 기존 \(w_{ext}\)를 재명명하거나 에너지를 누락해서는 안 된다.

광자 port가 붙은 합성 에너지 balance는 닫히지만, 이것이 photon transport/occupation/feedback/history의 구현 완료는 아니다. 방향별 photon emission law나 recoil도 이 scalar map으로 얻지 않는다.

## 4. 열적 입자수와 온도

이 선택 사건에서
\[
\Delta x_{e,th}=\Delta\chi_{th}=0,\qquad Q_{th}=0.
\]
common monatomic thermal bath의
\[
u_{th}=\frac32 n_b k_BT\chi_{th}
\]
를 쓸 때, 고정 \(n_b\) source 기여는
\[
\dot\ell=
\frac{2Q_{th}/(3n_b k_BT)-\dot\chi_{th}}{\chi_{th}}=0.
\]
이는 fast electron가 thermal pool에 들어가는 과정이 아니라 **포획되어 제거되는 선택 RR 사건**의 결과다. \(Q_{th}=0\)을 전체 stopping/heating의 물리적 영으로 확대하지 않는다. 기존 caloric partition의 heating null/assimilation false 상태를 바꾸지 않는다.

native all-electrons-thermal RR/DR의 \(n_e=n_bq^TY\)를 이 tagged-fast RR에 중복 붙여서는 안 된다. fast capture source와 thermal recombination source는 서로 다른 electron subpopulation과 독립 공급자·owner 계약을 갖는다.

## 5. source rate와 tangent — finite extent와 구별

외부 `Event.extent_m3_s`는 \(R\ge0\) **proper m⁻³ proper s⁻¹의 rate**다. 위 finite extent \(a\)와 동일한 숫자/차원이 아니다. \(r=R/n_b\), \(a=\int r\,dt\)로 연결한다.

고정 E,I,n_b에 대해
\[
F_Z=(r\nu,-r,-r\epsilon_J,0,0),\quad
S_{\gamma,ret}^{count}=r,\quad
S_{\gamma,ret}^{energy}=r(\epsilon_J+I_J).
\]
rate direction \(\delta r\)의 JVP는 같은 column에 \(r\to\delta r\)를 대입한 것이다. E를 움직이는 별도 mapping을 택하면 \(\delta\dot w_{nt}=-\epsilon_J\delta r-r\delta\epsilon_J\)와 photon의 \(+r\delta\epsilon_J\)를 쌍으로 더한다. 본 fixed-grid 사상에는 E/I derivative가 없다.

physical count/power의 product rule은 \(\delta(n_bF)=\delta n_bF+n_b\delta F\), eta clock은
\[
F_\eta=F/H,\qquad
\delta F_\eta=\delta F/H-F\delta H/H^2
\]
다. logT는 intensive rate이므로 일반적으로 density 변환을 곱하지 않는다. 이번 zero row에서는 값이 0으로 일치한다. 반응/입자수/energy rows의 per-reference map은 \(f_{ref}=\beta F\), \(\delta f_{ref}=\delta\beta F+\beta\delta F\)다.

RR chain이 주는 per-injected-electron first-passage probability 또는 accumulated photon moment를 물리 source rate로 쓰려면 initial/injection measure와 exposure/history가 별도로 있어야 한다. probability를 그대로 `extent_m3_s`에 넣지 않는다. 기존 source atoms의 count 및 energy moments를 same extent로 소비하는 경우에도 이를 monoenergetic spectrum으로 해석하지 않는다.

## 6. 기존 external engine를 재사용하는 정확한 코드 경로

다음 schema는 실제 기존 `contracts.py`의 구조에 맞는다.

| field | HeIII RR event |
|---|---|
| `event_id` | source/case/grid-energy/route가 구분되는 canonical ID |
| `source_contract` | 새 source-qualified HeIII ground contract의 고정 identity |
| `microscopic_owner` | 해당 RR supplier의 단일 owner |
| `transport_owner` | CR consumer의 단일 owner |
| `extent_m3_s` | 공통 R (proper rate) |
| `number_per_event` | He4:2 −1, He4:1 +1, e:fast −1, photon +1 |
| `binding` | −I_J |
| `thermal_kinetic` | 0 |
| `fast_kinetic` | −epsilon_J |
| `radiation` | epsilon_J+I_J |
| `recoil`, `escaped`, `external` | 각각 0 |
| `process` | `radiative_recombination` |
| `momentum_status` | `SCALAR_ENSEMBLE_ONLY` |
| `frame` | parent RR와 external consumer가 명시적으로 일치시킨 동일 bath frame |

정확한 소비 순서는 source/domain/isotope/review pins 확인 → 명시적 native21↔external species mapping → `Event(...)` → `EventBook.append` → `energy_rates` → 새 25좌표+photon-port projection이다.

- `Event.validate`는 7개 energy reservoir가 각각 한 번만 등장하도록 하고, energy closure와 nuclear/charge closure를 확인한다. RR에서는 binding/fast/thermal nonpositive, radiation/escape/recoil nonnegative, external=0을 요구한다. ENERGY_RTOL은 기존 **2e-13**이다.
- `EventBook.append`는 같은 book에서 event ID 중복과 frame 혼합을 거부한다.
- `EventBook.energy_rates`는 하나의 R를 모든 energy term에 곱한다.
- `CaloricDerivative.temperature_rate`에 \(Q_{th}=0,\dot n_{th}=0\)을 주면 positive \(C_V\)에서 0을 반환하는 구조다. 기존 EOS source identity가 필요하다.
- `require_physical_provider`는 immutable source/review pins와 process/species/frame/mass/domain을 확인한다. 문자열 또는 bytes hash 자체가 미시 공급자의 과학적 타당성을 증명하지는 않는다.
- `consume_saved.py`의 HeII label map은 `He4:1`→`He4:2`이며 이를 역으로 쓰는 RR event에서 isotope key `He4`를 그대로 보존한다.

기존 engine에는 25좌표 변환이나 \(\zeta\) state-domain validation이 없다. 또한 conservation만 통과하는 event 중에는 다른 stoichiometry도 있으므로, HeIII→HeII ground/fast-electron sink/photon+1/thermal0라는 특정 column은 새 thin adapter의 명시적 계약과 표적 검사 대상이다. source identity와 event invariants가 모두 통과해야 이 구체 사건으로 채택할 수 있다.

부모의 구현 단계에 필요한 최소 표적 확인은 (1) exact index/species column, (2) \(\Delta(qY)-\Delta\zeta=0\) 및 \(\Delta\chi=0\), (3) internal+fast+retained-photon energy, (4) finite extent/rate normalization의 분리, (5) duplicate/frame/domain rejection과 retained/external owner 구분이다. 이것은 실행 계획이며 본 R5 작업에서 검사를 실행했다고 주장하지 않는다.

## 7. 결론과 유지 의무

단일 HeIII ground fast-capture event는 native 25-state의 abundance/fast-count/fast-energy rows로 정확히 사상되며 thermal number와 source temperature row를 바꾸지 않는다. retained photon count/energy를 별도 output port로 반환하면 기존 signed external ledger의 의미를 보존하면서 전체 선택 사건의 에너지 balance가 닫힌다.

이 구성은 source-only linear event projection이다. 원 부모의 rate/domain/isotope policy, 단일 owner, 고정 bath와 feedback 부재, N6/N7 predecessor gates, 미확정 물리 uncertainty, 과거 UNKNOWN 및 프로젝트별 budgets는 그대로다. 이번 child에서 과학 CPU debit은 새 실행이 없으며 mechanical reading/hashing 비용은 미계측이다. 기존 REC 또는 CR 예산을 자동으로 가져오거나 남은 예산을 0/새 cap으로 초기화하지 않았다.

새 strong no-go를 제시하지 않았으므로 NG1–NG7 채택 판정은 해당하지 않는다. 본 문서의 독립성은 별도 agent의 source-grounded construction이며 root의 최종식에 대한 R6 fresh review와 구별한다.

