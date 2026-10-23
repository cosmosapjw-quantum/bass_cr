# C22E 최소 계약: 선복사 에너지의 적용 조건부터 판별

2026-10-22 UTC · physmath-research-loop 1.0.0 / approval 0.2의 다음 단위 제안. **이 addendum의 ODE 실행0, 완료 계산 재실행0**. C22D의 실행·물리 결과는 아직 이 문서의 근거로 채택하지 않는다. 기존 public manifest와 모든 동결 파일은 변경하지 않는다.

## 1. 다음 산출물은 admission 진단기다

최소 coding unit을 **`diagnose_line_admission.py`**로 정의한다. 완료 후 실제 authority가 확인된 C22D saved/accepted 상태와 명시적인 geometry/source 계약을 읽어, 현재 H1 n=2의 즉시 귀환·완전 탈출 가정이 어느 조건에서 가능한지 판별한다. 새 ODE를 시작하지 않고, 확보된 항목은 계산하며 빠진 항목은 `REQUIRED_INPUT_UNAVAILABLE`과 null로 출력한다. 이 상태를 0 rate 또는 실패한 물리 법칙으로 바꾸지 않는다.

입력은 source/run SHA, signed H·s, a, T, ne, H1 ground abundance, nHref, H1 2s/2p 사건률, 기존 UV photon6개·각 energy다. signed s가 없으면 norm에서 부호를 추정하지 않는다. 기존 H1 n=2 source는 collisional excitation의 부분집합이며, Case-A RR에서 발생하는 Lyα·2γ cascade yield는 아직 이 입력에 포함되지 않는다.

처음 실행 가능한 범위는 **명시적 finite cell, isotropic atomic gas, single-T Maxwell, source 범위3–20,000 K, 작은 excited fraction**을 조건으로 삼는 thin-cell diagnostic이다. 실제 cell size·column·geometry가 없으면 이 범위의 적용 여부도 미정이다. cosmological mean density에 임의로 Hubble length를 곱해 실제 column을 만들지 않는다. 외부 자료가 없어도 H·s에서 directional expansion과 source coverage 상태는 출력할 수 있다.

## 2. ‘탈출’의 뜻과 에너지 ledger를 먼저 고정한다

세 가지를 구분한다. (i) 지정한 공간 경계를 통과한 photon은 cumulative boundary export다. (ii) 적색편이로 Lyα resonance를 벗어난 photon은 여전히 계산 영역의 continuum radiation일 수 있다. (iii) 원자의 2p→1s 방출은 원자 준위에서의 방출이며 공간 경계 탈출과 같지 않다. 따라서 resonance 이탈을 곧바로 외부 energy sink로 기록하지 않는다.

2p의 resonant absorption과 radiative re-emission은 한 번의 scattering cycle이다. 광자 수1을 보존하는 이상화에서는 그 전체 photon energy를 gas heat로 적립하지 않는다. recoil·Doppler redistribution이 있으면 실제 photon energy 변화의 반대값만 gas에 주고, atomic excitation 중간 에너지도 포함한다. **true absorption/destruction**은 collisional de-excitation, continuum photoionization 등 photon이 다른 energy channel로 전환되는 경우로 분리한다.

현재 ΔE=10.20435 eV의 H1 excitation source에 단순 escape factor β를 곱하여 gas cooling을 줄이는 방법은 별도 유도가 필요하다. gas에서 빠진 에너지가 excited levels·resident radiation·true absorption 중 어디에 있는지 정해야 한다. 동적으로 확장하는 경우 필요한 회계는

\[
\frac{d}{dt}(U+B+E_{exc}+R_{line}+R_{2\gamma}+V_{UV}
+W_{exp}+L_{boundary}+L_{RR}+L_{bath})=0
\]

의 해당 반응별 상쇄다. bath는 기존 signed external ledger다. CI에 escaping-energy reservoir를 새로 붙이지 않는다. excited population을 추가한다면 H1 ground에서 그만큼 빼고 (X_{1s}+X_{2s}+X_{2p}+X_{H^+})를 보존한다. 기존21-state neutral abundance에 excited atom을 다시 더해 이중 계수하지 않는다.

## 3. 2p, 2s와 다른 반응의 연결

**2p Lyα:** 실제 A coefficient·oscillator strength·line profile과 redistribution source가 필요하다. τscat와 τtrue를 분리하고, optically thick scattering을 true heat deposition으로 취급하지 않는다. β=(1−e^(−τ))/τ 같은 식은 geometry·velocity-gradient·redistribution 조건을 먼저 갖춘 뒤 채택한다. τ가 크더라도 짧은 residence time과 작은 destruction probability가 입증되면 빠른 탈출 근사가 가능할 수 있으므로, 모든 thick regime을 배제하는 결론을 내리지 않는다.

**2s two-photon:** number spectrum φ(ν)를 emission event당 정의하고

\[
\int_0^{\nu_0}\phi(\nu)d\nu=2,
\qquad \int_0^{\nu_0}h\nu\phi(\nu)d\nu=\Delta E,
\qquad h\nu_0=\Delta E
\]

를 확인한다. 개별 photon은 continuum에 배분하며, 임의로 두 photon을 각각 ΔE로 두지 않는다. 현재6개 UV cohort에 2γ spectrum을 투영하려면 photon수·energy를 동시에 보존하는 새 quadrature/bin 계약이 필요하다. 그 계약 전에는 별도 reservoir 또는 spectrum으로 둔다. Lyα와 2γ photon은 H1 ground PI 문턱13.6058 eV 아래지만, LiI ground 문턱5.392 eV보다 높은 photon은 해당 흡수에 참여할 수 있다. ‘H ground를 이온화하지 않음’을 ‘흡수가 전혀 없음’으로 바꾸지 않는다.

**mixing·de-excitation:** 기존 intake의 `CCC_1S_2P.txt`, `CCC_1S_2S.txt`는 실제 downward 후보 bytes다. 이번에는 header·SHA만 확인했으며, thermal integral·통계중량·detailed balance·저에너지 끝점 처리를 검증한 provider는 아직 없다. CCC README는 LS-degenerate same-n 2s↔2p 전이의 형식적 발산을 경고한다. 이를 유한 mixing coefficient로 복사하지 않는다. physical splitting과 perturber(e/p/기타)의 실제 rate source가 필요하다.

**secondary/thermal coupling:** finite excited population이 있으면 excited-state PI·CI 문턱과 source가 별도로 필요하다. 기존 ground PI를 그대로 대입하지 않는다. 원자료의 총 CI 단면적만으로 primary/secondary energy-sharing을 정할 수 없다. 현재 초기 UV 최대150 eV에 대한 H1 primary excess의 상한136.3942 eV, LiI까지 포함한 기존 ground PI의 상한144.608 eV는 **입력 에너지 범위에서 유도한 source 요구 범위**다. 실제 C22D secondary 결과가 아니다. Coulomb 이완 진단만으로 이 에너지대의 중성원자 inelastic 경쟁이나 gas의 single-T 조건을 확정하지 않는다.

## 4. LRS에서는 directional redshift를 확인한다

상속 metric의 (H_\perp=H-s,\ H_\parallel=H+2s), 광자 방향 μ=cosθ에 대해 자유 비행은

\[
\frac{d\ln\nu}{dt}=-H_\gamma(\mu),\quad
H_\gamma=H+s(3\mu^2-1),\qquad
\frac{d\mu}{dt}=-3s\mu(1-\mu^2).
\]

이는 상속 LRS geometry의 직접 유도이며 새 transport 원자료를 확보했다는 주장이 아니다. 진단기는 min/max(H−s,H+2s), 방향별 Hγ의 부호, (3|s|/H)를 출력한다. 어떤 방향에서 Hγ≤0이면 모든 방향이 단조롭게 redshift한다는 가정의 Sobolev 처리에 바로 넣지 않는다. peculiar velocity가 있으면 실제 line-of-sight gradient도 필요하다.

atomic gas가 isotropic이라는 가정만으로 line radiation도 isotropic이 되지는 않는다. isotropic resident radiation을 별도로 가정할 때만 per-Href (R'=-R+(Q_{emit}-Q_{abs}-Q_{esc})/H,\ W_R'=R)를 사용할 수 있다. angular radiation이면 stress-work σ:π 항과 주파수·각도 수송을 함께 유도한다. 새 line stress를 기존 CMB/neutrino signed amplitude에 근거 없이 넣지 않는다. non-tilted LRS와 기존 full Frobenius/cancellation convention은 유지한다.

## 5. 진단 출력과 필요한 source

| 진단 | 필요한 자료 | 현재 실제 상태와 판별 |
|---|---|---|
| directional expansion | signed H,s | 저장 상태 authority 확인 뒤 직접 계산 가능; 새 D 결과는 이 문서에서 미채택 |
| excited-level elimination | A2p,A2s, excitation·absorption injection 및 mixing/de-excitation rates | A·완전한 level source 미공급; (t_{level}/t_{macro}), 추정 excited fraction은 null |
| line opacity | column/geometry, f 또는 σν, profile, level populations | 미공급; τscat와 τtrue를 별도 요구 |
| immediate boundary escape | L/c 또는 검증된 residence kernel, destruction probability | 실제 geometry 미공급; 탈출시간을 임의 생성하지 않음 |
| 2γ normalization/absorption | dA2γ/dν 원전, A2s, 종별 σPI(ν) | spectrum·A 미공급; 기존 selected ground PI는 재사용 후보 |
| collisional return/mixing | downward CCC endpoints 및 detailed balance; splitting-resolved mixing | downward bytes 확보, provider 검증 미완료; same-n LS는 그대로 사용 불가 |
| RR cascade line injection | channel별 capture state·cascade branching·energy | inherited Case-A 총 energy만으로 photon branch는 미정 |
| Maxwell/secondary admission | energy-sharing/secondary yield, e-neutral transfer, actual Coulomb log | 현재 단일-T closure는 부과한 조건; 필요한 source OPEN |

새로 확보할 primary source의 구체 항목은 다음이다: (a) fine-structure convention까지 명시한 H1 Lyα A/f/wavelength와 2s lifetime, (b) normalized differential 2s→1s two-photon spectrum, (c) 실제 scattering redistribution/recoil kernel과 채택 geometry의 escape/residence 규칙, (d) splitting-resolved electron/proton mixing 및 de-excitation coefficients와 3–20,000 K 유효성, (e) RR cascade branching, excited-state PI/CI와 UV-generated secondary yields. NIST ASD/원자 전이 원전, 저자 two-photon 표 및 해당 scattering·atomic-collision 논문을 확보할 대상이며 **현재 읽었다고 표시하지 않는다**.

진단기의 출력에는 numerical ratio·단위·source SHA·validity interval·판정 이유를 함께 둔다. 판정은 `COMPUTED_SCOPED`, `CONDITIONAL_INPUT_DIAGNOSTIC`, `REQUIRED_INPUT_UNAVAILABLE`, `REGIME_NOT_ESTABLISHED`로 구분한다. 즉시 level elimination/escape의 충분조건을 검토할 때는 사용자 또는 preregistration이 정한 ε에 대해 (t_{level}/t_{macro}\ll1), (t_{escape}/t_{macro}\ll1), excited fraction≪1, destruction probability≪1을 각각 확인한다. finite optically thin cell은 그중 단순한 후보이며, 이 sample ratios를 연속시간 오차상한으로 승격하지 않는다.

## 6. 다음 실제 순서와 4축

첫 구현은 위 read-only 진단기와 create-only `LINE_SOURCE_COVERAGE.json`, `LINE_ADMISSION.csv/json`이다. 입력 누락과 실패 경로, 2γ 적분정규화 및 반응별 energy 상쇄를 가볍게 검증한다. **실제 source·geometry·admission이 고정된 뒤** 최소 excited/resident-radiation adapter 또는 유도된 빠른 준위 제거를 선택하고, 새 input/run ID를 등록한다. 그때 fresh resource/lease와 CPU55·coordinator 보호, worker1thread를 확인한다. 기존 ODE를 복원용으로 반복하지 않는다.

| 축 | 이 addendum의 상태 |
|---|---|
| EXECUTION | 새 ODE0·완료 ODE 재실행0; 기존 downward 후보 header/SHA와 알려진 근거 재사용 |
| PUBLICATION | 별도 새 계약·addendum manifest; 기존 manifest immutable |
| BACKUP | 부모의 실제 운송·readback 영수증으로 확정; 이 문서가 완료를 주장하지 않음 |
| DAG | 다음은 line admission/source coverage 진단. full thermochemical/radiative closure OPEN; full nuclear high-energy/general tilted·triaxial·polarized CMB HOLD |

새 strong no-go 없음, NG1–NG7는 새 배제 정리 채택이 없어 N/A다. 모든 isotope quotient를 불가능하다고 결론내리지 않는다. 원 핵반응 PNG는 회수·판독되지 않았고 접근 못한 대화는 UNAVAILABLE다. **global_error_bound=null.**

근거는 보존된 `CI_THEORY_AND_ADMISSION_KO.md`, C22C의 `THEORY_SCOPE_AND_NEXT_CONTRACT_KO.md`·선택 source metadata, [CCC 저자 자료](https://atom.curtin.edu.au/CCC-WWW/index.html)와 실제 README, 기존 SW91 p303–304 및 [NIST H1 원전 페이지](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable1.htm)로 한정한다. 이번 addendum에서는 새 문헌 검색·새 rate provider 채택을 하지 않았다.
