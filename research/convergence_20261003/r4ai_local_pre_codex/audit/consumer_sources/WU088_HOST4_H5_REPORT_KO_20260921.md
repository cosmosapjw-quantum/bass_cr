# HOST4-H5: 새 물리 모델 상태 specification과 co-binding gate

## 판정

`PARTIAL_CLOSE__MODEL_DEFINED_NEW_PHYSICAL_STATE_MATERIALIZED_AND_HASHED__STATE_FRAME_TIME_MEASURE_SOURCE_SUPPORT_COBINDING_PASS__WARM_TARGET_AND_STATE_WEIGHT_CONTRACTS_IMPORTED__REFERENCE_HOST_PROJECTION_PASS__R4_ACTUAL_RATE_PREFLIGHT_REMAINS_BLOCKED__PRODUCTION_HOST_PIN_OPEN__NO_PHYSICAL_RATE_RUN`

이번 루프는 H4의 `HOST4_H5_NEW_PHYSICAL_STATE_SPECIFICATION_AND_COBINDING_GATE`를 실행했다. H3/H4의 결론대로 잃어버린 actual snapshot을 복구했다고 부르지 않았다. 대신 하나의 새로 정의한 물리적 모델 초기조건을 실제 JSON bytes로 materialize하고, 그 state/target/source/frame/time identity를 함께 고정했다.

핵심 구분은 다음과 같다.

- `classification = NEW_PHYSICAL_STATE`
- `authority_class = MODEL_DEFINED_TRACE_CR_REIONIZATION_BENCHMARK_NOT_OBSERVATIONAL_RECOVERY`
- recovered actual snapshot: **NO**
- observational inference: **NO**
- physical rate evaluation: **0회**
- production `HOST_PIN`: **OPEN**

즉 H5가 닫은 것은 **상태 자체의 명시적 물리 단위, provenance, co-binding identity와 source-support gate**다. rate/source interpolation/quadrature/production-host 승인은 별개의 다음 gate로 남긴다.

## 1. Parent와 sibling 복구

### H4 parent

H4 최종 core를 새로 SHA-256/ZIP CRC 검사했다.

- name: `WU088_HOST4_H4_NEW_REFERENCE_HOST_AND_STATE_CONTRACT_20260921_v1.zip`
- bytes: 3,251,302
- SHA-256: `7fc98e6ea67763bd663529712e78fb52fc0186d6af5c21c0f3d8027656467df9`
- members: 248
- CRC: PASS

H4의 reference commit/tree는 그대로 유지한다.

- commit `0d10793fe1e7ca997552c1866577cda8e875164d`
- tree `d6cc91ebed28309556c0c552050a9339b85ea460`
- production host commit/tree/entrypoint: null

### 새로 회수한 state/target 계약

9월 20일 sibling에서 H5에 직접 필요한 두 정본을 추가 회수했다.

1. `WU088_STATE_WEIGHT_HOST_INTEGRATION_20260920_v1`
   - weight는 외부 고정 벡터가 아니라 state-dependent operator다.
   - finite-dimensional contract:
     \[
       \Phi_i=n_t\sum_j G_{ij}F_jv_jq_j.
     \]
   - consumer state hash, target state hash, source-native grid hash, state-evaluation operator hash, observable signature, quadrature rule hash를 각각 요구한다.
   - fresh replay: **8 PASS**.

2. `BASS_CR_SNAPSHOT_R2_STATE_SUM_AND_WARM_TARGET_AUDIT_20260920_v2`
   - zero-drift isotropic neutral Maxwellian이면 scalar count는 full angular distribution 대신 gas-frame radial spectrum으로 정확히 축약된다.
   - warm kernel:
     \[
     \overline K(v,T)=\int_0^\infty dg\,P(g|v,s)\,g\sigma(g),\quad s^2=k_BT/m_H.
     \]
   - fresh verifier: **6 assertion groups PASS**.

이 두 계약을 H5의 상태/target 의미론 SSOT로 import했다. synthetic state-weight witness나 finite-basis capture sum의 수치를 H5 CR normalization으로 재사용하지 않았다.

### 루프 중 최신 sibling refresh

봉인 직전 bounded refresh에서 다음 변경을 확인했다.

- H-H R3 final: `STOP_NUMERICAL_METHOD_PARTIAL`. Fresh family/strong-weak/chart checks는 개선됐지만 cross-batch replication 2항이 marginal FAIL이라 reference interval과 propagation은 없음.
- CR R3M10: independent TDL/AOCC local reproduction package. 6/6 unit tests와 smoke는 통과했지만 TDL spatial smoke가 미수렴이고 full b-grid는 `NO_GO`; production central과 physical rate 없음.
- P0 R18 FINAL: 봉인 직전 새 최종 정본을 다시 동기화했다. `N38=24/38`, physical P0=`OPEN`, J0 physical ingest=`NOT_RUN`; `local_cov`, source-authorized `mode_cov`, cross-energy joint dependence는 모두 absent다. 새 최대 observed discrete two-model span은 0.0055 eV에서 나타나지만 이것은 continuous bound/covariance가 아니다. R18 final package SHA-256은 `e4741b93e275b4f4e58282260f7f82f97801f0b08ddf606ec3e5de88cf7ccda5`다.

어느 것도 H5의 state identity나 source/rate admission을 자동으로 승격시키지 않는다. 특히 P0 R18의 discrete model span을 H5의 probabilistic UQ나 warm-target rate error로 import하지 않았다.

## 2. H5가 정의한 새 모델 상태

### 2.1 Background와 gas

[literature-supported benchmark + model-defined]

Planck 2018 base-LambdaCDM abstract central values를 투명한 benchmark로 사용했다:

\[
H_0=67.4\,\mathrm{km\,s^{-1}Mpc^{-1}},\quad
\Omega_m=0.315,\quad \Omega_bh^2=0.0224.
\]

`Y_p=0.245`는 H5가 명시적으로 고른 benchmark parameter다. 방사 성분을 생략한 local background 정의에서

\[
H(z)=H_0\sqrt{\Omega_m(1+z)^3+\Omega_\Lambda},
\]

\[
n_H(z)=\frac{(1-Y_p)\Omega_b\rho_{c0}}{m_p}(1+z)^3,
\qquad \rho_{c0}=\frac{3H_0^2}{8\pi G}.
\]

`z=8`에서:

- `H = 3.3149362225571165e-17 s^-1`
- `n_H = n_HI = 138.4520191201626 m^-3`
- `T_HI = 10^4 K`
- target bulk velocity = 0 in the gas tetrad
- neutral velocity law = isotropic Maxwellian

이 숫자는 관측된 특정 cell의 posterior가 아니라 H5의 model initial condition이다.

### 2.2 Bianchi-I anisotropy

[model-defined]

local event에서 `a_i=1`로 좌표 정규화하고

\[
H_i/H=(1.01,\,0.995,\,0.995)
\]

를 썼다. 따라서 `sum H_i = 3H`가 정확히 유지되고,

\[
\frac{\sigma}{\theta}=2.886751345948118\times10^{-3}
\]

이다. 이 1% directional stress는 observational anisotropy constraint가 아니라 characteristic/interface를 실제 Bianchi-I 방향성 아래 검사하기 위한 명시적 model knob다.

### 2.3 CR spectrum

[literature-supported form + model-defined normalization/support]

강한 비상대론 충격의 test-particle DSA에서 momentum-space `f(p) proportional p^-4`가 표준 benchmark라는 문헌 맥락을 사용했다. H5에서는 gas tetrad에서 isotropic하게

\[
G(p)=\int d\Omega\,p^2 f(p,\Omega)=C p^{-2},
\qquad p_{\min}\le p\le p_{\max},
\]

그 밖에서는 0으로 정의했다.

- support: 4-81 keV/u
- `n_pCR/n_H = 10^-6`
- `n_pCR = 1.3845201912016257e-4 m^-3`
- H0CR initial population = 0

정규화는

\[
C=\frac{n_{pCR}}{p_{\min}^{-1}-p_{\max}^{-1}}
\]

로 고정했다. 독립 audit에서 `integral G dp = n_pCR` residual은 binary64에서 0이었다. `10^-6` normalization과 support cutoff는 관측 추정치가 아니라 tracer-regime H5 benchmark choice다.

## 3. Warm-target 수학과 source-support gate

[derived + Wolfram checked + parent verifier replayed]

neutral Maxwellian의 relative-speed density를

\[
P(g|v,s)=\frac{g}{\sqrt{2\pi}sv}
\left[e^{-(g-v)^2/(2s^2)}-e^{-(g+v)^2/(2s^2)}\right]
\]

로 두면 Wolfram clean algebraic result는

\[
\int_0^\infty P\,dg=1,
\qquad \langle g^2\rangle=v^2+3s^2.
\]

또 `h(v)=v sigma(v)`에 대해 radial Gaussian averaging의 2차항은

\[
\overline K=h+\frac{s^2}{2}\left(h''+\frac{2h'}v\right)+O(s^4),
\]

\[
\frac{\overline K-h}{h}
=\frac{s^2}{2v^2}\left(2+3\alpha+\alpha^2+\beta\right)+O[(s/v)^4]
\]

이며 `alpha=d ln sigma/d ln v`, `beta=d alpha/d ln v`다. 따라서 cold-target 오차는 온도만으로 정할 수 없고 local slope/curvature authority가 필요하다는 R2 결론을 유지한다.

H5는 cold-target을 억지로 승인하지 않고 **warm-target model**을 유지한다.

`T=10^4 K`, `delta=10^-6`, source domain 1-100 keV/u에 대해 probability-support gate는

\[
E_{\rm admitted}=[1.2421066122,\,97.7231425169]\ \mathrm{keV/u}.
\]

H5 CR support `[4,81] keV/u`는 이 안에 완전히 들어가므로 `source_support_pass=true`다.

단, `P(|u|>U_delta)<=10^-6`는 **rate tail error bound가 아니다**. 또한 D102563은 native 10-node source이므로 node 사이의 continuous `sigma(g)`를 H5가 임의 spline하지 않는다. 따라서 strict warm convolution rate는 계속 OPEN이다.

## 4. Co-binding identity

[numerically checked]

새 state bytes:

- file: `contracts/NEW_PHYSICAL_STATE.json`
- raw SHA-256: `3f0e35418861984ec2671363ff0c9d7c6db4bdc88c75c7fb7e1bbb95907ca9f2`
- consumer-state hash: `b01bd400f1de2bba4b76c9fbb3763e67e53f79d89a33f2137e6a0acaec44789e`
- target-state hash: `2f90b020f8628edfb55064aa40ea8124440a4e8873ee348868880d6c32598435`
- source-native grid hash: `77ae8b339fd20eec4449fc15096cd4f6503c978a8d33218af9bb69aaafb2b8e5`
- analytic state-evaluation operator hash: `37fcb5dc7e3e6242f5d6c34f8d2546348830382e4d1cdb61236f464d4257354e`
- observable: `H0_CR_1s_FORMATION_COUNT__NOT_TOTAL_GAS_HII`

이 observable 선택은 중요하다. D102563 1s capture는 fast H0_CR(1s) formation에는 맞지만 **total gas-HII charge-exchange count에는 불충분**하다. 후자를 요청하면 R2의 bound-state-summed source lane을 다시 열어야 한다.

H5 state-dependent operator identity 중 state/target/grid/evaluation/observable은 닫혔다. 하지만 `quadrature_rule_hash=null`이고 physical quadrature error authority는 OPEN이다. 이것을 임의 값으로 채우지 않았다.

## 5. H4 characteristic projection witness

[numerically checked, verification-only]

H5 state에서 25 keV/u shell의 ±x, ±y, ±z 여섯 방향을 꺼내 H4 reference characteristic에 투영했다. 이는 전체 spectrum evolution이나 collision run이 아니라 co-binding된 geometry의 독립 witness다.

`Delta tau = 0.05/H = 1.5083246446723608e15 s` 동안 `E=B=0`으로 실행했다. analytic Bianchi-I law

\[
p_i(\tau)=p_i(0)e^{-H_i\tau},
\qquad a_i(\tau)=e^{H_i\tau},
\qquad n(\tau)=n(0)e^{-\theta\tau}
\]

과 비교하면:

- momentum directional max relative error: `9.6923e-15`
- scale-factor max relative error: `0`
- proper-density relative error: `1.1373e-16`

이다. 이 검사는 H4 reference characteristic가 H5의 model event convention과 수학적으로 일치함을 확인한다. production host admission이나 collision coupling은 아니다.

## 6. R4 physical preflight를 일부러 속이지 않은 결과

H5 state를 R4 schema 모양의 shadow packet으로 변환해 기존 physical preflight를 실행했다. 결과는 `pass=false`이며 blocker는 다음 8개다.

1. `cold_target_authority_missing`
2. `cold_target_error_not_accepted`
3. `invalid_quadrature_weights`
4. `quadrature_authority_missing`
5. `snapshot_not_actual_declared`
6. `synthetic_origin_not_actual`
7. `snapshot_hash_not_registered`
8. `physical_quadrature_bound_missing`

앞 네 항은 warm-target/physical quadrature를 아직 rate authority로 바꾸지 않았기 때문에 남은 과학적 blocker다. 뒤 네 항은 이 state가 caller-attested actual data product가 아니라 **새 model-defined state**라는 provenance firewall이 정상 작동한 결과다.

따라서 이 실패를 고치기 위해 status string을 `ACTUAL_DECLARED`로 바꾸거나 빈 registry에 가짜 attestation을 쓰지 않았다.

## 7. Gate 판정

### CLOSED / PASS

- [fresh verified] H4 parent SHA/CRC identity.
- [model-defined] one immutable physical model state with SI units and explicit provenance.
- [derived/numerically checked] Planck-benchmark gas density and weak Bianchi-I kinematics.
- [literature-supported + model-defined] isotropic test-particle DSA `p^-4` spectrum with explicit normalization/support.
- [imported + Wolfram/Python checked] zero-drift isotropic warm-target scalar reduction.
- [numerically checked] source support at `delta=1e-6` for state support 4-81 keV/u.
- [numerically checked] state/target/grid/evaluation/observable hashes.
- [numerically checked] H4 characteristic projection against analytic Bianchi-I solution.
- parent warm-target verifier 6 groups PASS; state-weight parent tests 8 PASS; H5 tests 5 PASS.

### OPEN / BLOCKED

- `CONTINUOUS_SOURCE_KERNEL_BETWEEN_NATIVE_NODES_OPEN`
- `PHYSICAL_QUADRATURE_ERROR_AUTHORITY_OPEN`
- `WARM_TARGET_STRICT_RATE_TAIL_BOUND_OPEN`
- `PRODUCTION_HOST_PIN_OPEN`
- total gas-HII CX source if that observable is requested: bound-state-summed/high-n authority OPEN
- P0 probabilistic/joint UQ remains independent and OPEN

No rate was evaluated, no tail was set to zero, no interpolation was smuggled into the source, and no model state was relabeled as recovered actual data.

## 7.1 최종 fresh replay와 runtime 분류

[implementation-verified]

R18 FINAL을 반영한 뒤 state builder, H5 tests, independent audit를 다시 실행했다. 첫 builder 호출을 `python src/build_h5_artifacts.py`로 직접 실행했을 때 import root가 `src/`로 잡혀 `ModuleNotFoundError: src.h5_state`가 발생했다. 이는 물리/수치 실패가 아니라 `RUNTIME_INVOCATION_FAILURE__DIRECT_SCRIPT_IMPORT_ROOT`로 보존했다. package root에서 `python -m src.build_h5_artifacts`로 같은 코드를 다시 실행하면 정상 종료했고, state SHA-256은 기존 `3f0e35418861984ec2671363ff0c9d7c6db4bdc88c75c7fb7e1bbb95907ca9f2`와 동일했다.

봉인 직전 fresh evidence:
- H5 tests: `5 passed`
- independent H4-state projection audit: PASS
- P0 R18 final manifest: `5/5 PASS`
- P0 R18 ZIP CRC: PASS

이 replay는 기존 physical blockers를 제거하지 않는다.

## 8. 다음 canonical node

`HOST4_H6_CONTINUOUS_CX_KERNEL_AND_PHYSICAL_QUADRATURE_AUTHORITY_GATE`

H6는 H5 state를 바꾸지 않는다. 먼저 1s observable에 대해 source-authorized continuous kernel 또는 명시적 interpolation-error authority를 확보하고, warm-target tail에 strict rate bound를 붙이며, analytic H5 spectrum에 대한 physical quadrature와 error certificate를 분리해서 닫아야 한다. production host pin은 그와 독립된 gate로 계속 유지한다.
