# bass_cr 인수인계

중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.

첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.

현재 소스 핀·예약·자원 정책(원본 계약 기준):

```json
{
  "atomic/LONGTERM_CONTRACTS.json": {
    "schema": "ATOMIC_LONGTERM_CONTRACT_V1",
    "as_of": "2026-10-23",
    "scope": "survey and planning; no science executed",
    "pins": {
      "WU088_HH": "09289300ec2e500806aa2cb82365f00329e41c8c",
      "bass_cr": "aa57be95b7459eb397d9881b686d9c7bc4444755"
    },
    "selected_current_loop": "Root chose HE38 angular moment-cone; cutoff is future only",
    "coverage": {
      "WU_branches": 148,
      "CR_branches": 175,
      "pages_each": 3,
      "terminal_cursors": null,
      "PR_search": "updated>=2026-10-22 top100 returned6WU/2CR; connector exposes no total or cursor",
      "actual_file_reads": "selected latest contracts/reports/handoffs, root AGENTS; full branch contents not exhaustively read",
      "private_conversations": "UNAVAILABLE",
      "external_runtime": "UNOBSERVED",
      "backups": "C23B authority+terminal full text read; producer R3 reused, no archive redownload"
    }
  }
}
```


## CR_N4_C23B_CUTOFF_BINDING

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/0`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "CR_N4_C23B_CUTOFF_BINDING",
  "depends_on": [],
  "equations": [
    "Qe=sum_i n_target_i*sum_j w_ij*delta(K-Kij)",
    "Nth=Nnuc+Ne,all-int_Kc^inf F(K)dK",
    "Uth=Uall-int_Kc^inf K*F(K)dK",
    "dT=2*dUth/(3*kB*Nth)-T*dNth/Nth"
  ],
  "domain": "C23B bath-frame rest target atoms, three z only; finite count/energy, positive T; cutoff Kc=chi*kBT, chi>=3/2 for inherited atomic branch existence",
  "input": [
    "photoelectron_atoms.csv SHA256 f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3",
    "Oct13 KC1-KC7 source a5c29ad4070acb931d92d2bec42a927a57f479ca",
    "declared target density or abundance, never both"
  ],
  "output": [
    "new supplier-to-existing-cutoff compatibility adapter, missing bath fields explicit"
  ],
  "admission_gate": "old theorem assumptions mapped; no physical heat from partition alone; cutoff is not FS10eV boundary; atom energy/count exact; unresolved He/H and stopping retained",
  "pr_boundary": "Small new connector PR; no fresh theorem novelty and no duplicate old cutoff checks"
}
```


## CR_N4_STOPPING_KERNEL

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/1`. 내부 선행: CR_N4_C23B_CUTOFF_BINDING. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "CR_N4_STOPPING_KERNEL",
  "depends_on": [
    "CR_N4_C23B_CUTOFF_BINDING"
  ],
  "equations": [
    "partial_t F+partial_K(dotK*F)=S+gain-loss",
    "Jcut=(dKc/dt-dotK(Kc))*F(Kc)",
    "Qbath=int b_coll(K)*F(K)dK + cutoff_energy_transfer"
  ],
  "domain": "K<10eV plus above-cutoff source; finite-T Coulomb/elastic/inelastic channels, density and ionization explicit",
  "input": [
    "primary low-energy stopping rates with validity",
    "bath composition and thermal distribution",
    "C23B low-energy source atoms"
  ],
  "output": [
    "positive conservative stopping/exchange operator and timescale ratios"
  ],
  "admission_gate": "finite-time t_stop/t_evolution and escape assumptions established; no cold drag extrapolation through thermal bath; count/energy same boundary flux",
  "pr_boundary": "Physical kernel PR separate from algebraic cutoff connector and integrated ODE"
}
```


## CR_N5_ATOMIC_ISOTOPE_COVERAGE

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/2`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "CR_N5_ATOMIC_ISOTOPE_COVERAGE",
  "depends_on": [],
  "equations": [
    "r_a=n_i*n_j*k_a(T) or n_i*Gamma_a",
    "S_charge*r defines Ne,all source",
    "DeltaUbind=sum_i I_i*DeltaN_i"
  ],
  "domain": "n,H1,D,T,He3,He4,Li6,Li7 explicit charges; isotope source equivalence separately proved",
  "input": [
    "C23B HI/HeI/HeII fits with13.6/24.59/54.42eV thresholds",
    "WU PHYS81/82/83 completion",
    "CI/RR/DR/CX data"
  ],
  "output": [
    "source-by-species/rate/energy-domain matrix and unique energy owners"
  ],
  "admission_gate": "missing rate=null; source isotope quotient qualified at target accuracy; own source thresholds never silently replaced",
  "pr_boundary": "Supplier coverage PR; no coupled-science claims"
}
```


## CR_N6_CONSERVATIVE_COUPLING

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/3`. 내부 선행: CR_N4_STOPPING_KERNEL, CR_N5_ATOMIC_ISOTOPE_COVERAGE. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "CR_N6_CONSERVATIVE_COUPLING",
  "depends_on": [
    "CR_N4_STOPPING_KERNEL",
    "CR_N5_ATOMIC_ISOTOPE_COVERAGE"
  ],
  "equations": [
    "d(Uth+Unt+Ubind+Urad+Uescape)/dt=external_supply-expansion_work-shear_work",
    "dNe,all/dt=charge_incidence",
    "pi_total=sum signed frame-aligned pi"
  ],
  "domain": "non-tilted LRS; original isotropic gas; source3z no unqualified z interpolation",
  "input": [
    "admitted source kernels and bath",
    "radiative escape/reabsorption and normal-frame mappings"
  ],
  "output": [
    "closed conservative thermochemical RHS, block Jacobian and audit"
  ],
  "admission_gate": "single owner for photoheat/fast kinetic/binding; no simultaneous direct heat and full nonthermal source; FS physical composition gate independently closed",
  "pr_boundary": "Conservative component PR followed by consumer integration PR"
}
```


## CR_N7_NEW_PARCEL

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/4`. 내부 선행: CR_N6_CONSERVATIVE_COUPLING. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "CR_N7_NEW_PARCEL",
  "depends_on": [
    "CR_N6_CONSERVATIVE_COUPLING"
  ],
  "equations": [
    "dy/dtau=f(y;input)",
    "error comparison uses same input/model/tolerance registry"
  ],
  "domain": "new closed-parcel input first, then separately admitted cosmological pilot",
  "input": [
    "frozen source/code/IC/solver/closure identity",
    "known cumulative budget and resource lease"
  ],
  "output": [
    "create-only outputs, invariant and refinement comparisons, performance only if paired"
  ],
  "admission_gate": "analytic limit, charge/nuclei/energy and valid domain gates before one new unit; retain global_error_bound=null until justified",
  "pr_boundary": "New-input science PR distinct from code and main; completed C21O-C23B/NCP51 reused"
}
```


## CR_BETA_FULL_OWNER

원본: `atomic/LONGTERM_CONTRACTS.json/nodes/bass_cr/5`. 내부 선행: 내부 없음. 외부 선행: `[]`. 조건부 선행: `[]`.

원 저자 계약(변경 없음):

```json
{
  "status": "OPEN",
  "execution": "NOT_RUN",
  "budget": {
    "inherited_spend": null,
    "remaining": null,
    "currency": null,
    "policy": "unknown is not zero; retain existing campaign receipt; no new heavy launch"
  },
  "publication": {
    "kind": "separate additive draft",
    "merge": false
  },
  "gate_transition": "OPEN -> DERIVED_SCOPED -> IMPLEMENTATION_VERIFIED -> NUMERICALLY_CHECKED_SCOPED -> CONSUMER_ADMITTED only with named consumer and valid source/domain/owner",
  "no_replay": "completed identities reused, changes verify only affected obligations",
  "id": "CR_BETA_FULL_OWNER",
  "depends_on": [],
  "equations": [
    "E=gamma*(Eprime+beta*c*pprime*mu)",
    "decay rate transforms with declared proper clock",
    "Eparent=Edaughter+Ee+Enu+Erecoil"
  ],
  "domain": "evaluated beta spectrum plus parent direction/charge/recoil; full high-energy campaign HOLD",
  "input": [
    "C23B isotropic boost kernel complete",
    "evaluated beta spectra and daughter/recoil/neutrino owners"
  ],
  "output": [
    "physical spectrum supplier and full event ledger"
  ],
  "admission_gate": "synthetic mean-line witnesses replaced by evaluated spectrum before admission; source clock/volume/reference all fixed",
  "pr_boundary": "Theory/source PR only; no full nuclear launch"
}
```


## 저장소 간 조건부 연결

채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.


- `CR_N4_STOPPING_KERNEL` → `REI-L1`: claiming thermalization of supplied fast photoelectrons. Without provider, energy remains explicitly nonthermal; no instant heat


- `CR_N6_CONSERVATIVE_COUPLING` → `REI-L4`: selecting CR coupled radiation/deposition pathway. Source and gas use same event measure and valid domain


- `CR_BETA_FULL_OWNER` → `REI-L2`: activating source-qualified beta partition and stopping. One beta owner; total Q not all heat
