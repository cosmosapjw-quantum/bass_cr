# C23C N5 독립 C9 검토: 원자 population·에너지 소유권·동위원소 축약

**판정: `PASS_SCOPED_FINDINGS_CLOSED`.** 세 finding을 같은 C9 pass 안에서 최소 수정으로 닫았다. 최초 155개 검증은 이미 완료된 결과를 재사용했고, 수정된 조건에 직접 대응하는 6개 검사만 새 실행으로 확인했다. 이 판정은 정확한 inventory·보존·소유권·대수 축약 계약에 한정된다. 실제 원자 rate coverage, stopping/thermalization provider 및 전체 thermochemical/radiative RHS는 여전히 OPEN이다. `global_error_bound=null`을 유지한다.

## 검토 범위와 독립성

검토자 `/root/c23c_intake`는 N5 구현의 작성자가 아니다. 이 검토는 C23C의 한 번의 독립 C9 pass 가운데 N5 부분을 맡은 것으로, N4 검토와 상보적이다. 코드와 해석을 읽고 대수 조건을 독립적으로 검토했다. 실제 실행은 root가 자원 관측·lease·create-only 출력 계약 아래 수행했다. 검토자는 기존 과학 계산이나 155개 검사를 재실행하지 않았다. 적용 정책은 `physmath-research-loop` 1.3.0 및 `POLICY_INTEGRATION.md`다.

검토 대상은 `theory/atomic_coverage/implementation/atomic_contract.py`, 최초 verifier, 수정 후 targeted verifier 및 일치하도록 수정된 이론 문서다. 저장된 최초 실행 코드 2개와 현재 실행 코드 3개는 각 실행의 `SOURCE_IDENTITY.json`에 기록된 byte size 및 SHA256와 실제 파일을 비교해 일치함을 확인했다. 이 파일 동일성 확인은 새로운 물리 계산이 아니다.

## 수용한 정확한 계약

| 항목 | 검토 결론과 범위 |
|---|---|
| 21 populations | n, H1, D, T, He3, He4, Li6, Li7의 선언된 전하 상태 합계는 21개다. 자유전자 좌표를 더한 stoichiometry는 22차원이다. 누락 species를 0으로 채우지 않으며, 명시적으로 선언한 n/T 초기 0은 허용한다. |
| 전하 사다리 | 각 CI/PI/RR에 13개 rung이 있다. CI는 `lo+e -> hi+2e`, PI는 `lo -> hi+e`, RR은 `hi+e -> lo`의 원자·전자 반응을 사용하며 photon 소유권은 별도다. 각 반응의 개별 핵종 수, baryon 수 및 전하 잔차는 정확히 0이다. |
| 입자 수 | 이온화는 원자와 모든 자유전자를 합한 입자 수를 1 늘리고 RR은 1 줄인다. 이 수는 전자가 열평형 pool에 들어갔다는 가정이 없는 한 열적 입자 수와 동일시하지 않는다. |
| SourceSupport | 명시적으로 admitted된 threshold 아래의 물리적 0과 coverage 밖의 `null`을 구분한다. source 구간 안에서도 아직 평가하지 않은 rate는 `null`이다. threshold와 첫 source knot 사이의 간극을 임의의 0으로 채우지 않는다. |
| 에너지 장부 | 공급된 같은 frame의 incoming/outgoing 전자, photon, binding, recoil 에너지를 합산한다. 누락된 이차전자 에너지나 열화율을 추론하지 않는다. recoil은 명시적으로 입력해야 한다. |
| 유한 질량 recoil | 정지 표적·비상대론적 탄성 산란에서 올바른 운동량 전달 단면적 가중 계수를 사용한다. 계수만으로 실제 stopping rate가 공급되지는 않는다. |
| 상대 Maxwell 분포 | 독립·등방·평균 상대 drift 0인 비상대론적 두 Maxwell 분포에 대한 환산 질량 및 상대 온도 항등식에 한정된다. |
| 동위원소 quotient | 한 bath 상태에서 arbitrary isotope inventory에 대한 number closure와 chemical-energy source closure를 별도로 검사한다. 모든 bath 상태에서의 실제 rate 동등성을 주장하지 않는다. |

## 독립 대수 점검

동위원소별 population을 \(n_a\), 열벡터 방향의 생성자를 \(G_a\)라 두면
\[
\dot n_a=G_a n_a,\qquad N=\sum_a n_a.
\]
임의의 동위원소 조성에서 \(\dot N=G N\)으로 닫히려면 모든 \(G_a=G\)가 필요하고 충분하다. 각 동위원소에 population을 하나씩만 두는 선택으로 필요성을 확인할 수 있다. 총 chemical-energy source가 aggregate \(N\)에 대해 단일 row로 닫히려면 추가로 \(\epsilon_a^T G_a\)가 동위원소에 무관해야 한다. 구현은 이 두 조건을 정확한 유리수 row 비교로 구분한다.

공통 \(G\)의 rank가 \(n-1\)이면 열합 0에 의해 왼쪽 영공간이 \(\operatorname{span}\{\mathbf1^T\}\)이고, 따라서 energy-row equality는 binding-energy 차이가 상수 offset인 것과 동치다. Irreducibility는 이 rank 조건의 충분조건이다. 단순한 weak connectivity는 충분하지 않다.

유한 질량 계수도 직접 확인했다. projectile 질량 \(m\), 정지 표적 질량 \(M\), 입사 kinetic energy \(E\), CM 산란각 \(\theta\)에 대해
\[
\Delta E_M=\frac{2mM}{(m+M)^2}E(1-\cos\theta).
\]
따라서 \(\sigma_{\rm mt}=\int(1-\cos\theta)\,d\sigma\)를 쓸 때 energy-transfer cross section은 위 질량 계수에 \(E\sigma_{\rm mt}\)를 곱한 것이다. 실제 angular cross section과 표적 분포가 없는 상태를 complete provider로 승격하지 않는다. 독립·무 drift Maxwellian의 상대 속도 성분 분산을 합하면
\[
\mu=\frac{mM}{m+M},\qquad T_{\rm rel}=\mu\left(\frac{T_m}{m}+\frac{T_M}{M}\right)
\]
을 얻는다. 구현은 이 제한된 조건을 반영한다.

## 발견 사항과 같은 pass 안의 종결

### N5-C9-F1 — directed generator의 연결 조건

최초 문서의 “connected common G이면 constant offset과 동치”라는 조건은 너무 넓었다. 일반 energy-row 비교 구현 자체는 올바르다. 검토자가 제시한 인접 rung 반례는 다음과 같다.

\[
G=\begin{pmatrix}0&1&0\\0&-2&0\\0&1&0\end{pmatrix},\quad
\epsilon_a=(0,13,24),\quad \epsilon_b=(0,14,26).
\]

이 directed graph는 weakly connected이지만 두 absorbing state를 가지며 reducible이다. 두 binding vector 모두 neutral 기준 0이며 증가한다. 차이 \((0,1,2)\)는 상수가 아니지만 \((\epsilon_b-\epsilon_a)^T G=0\)이고 두 energy row는 모두 \((0,-2,0)\)이다. 문서를 `rank(G)=n-1` 조건과 그 충분조건인 irreducibility로 고쳤다. 일반 exact row 비교는 유지했다. 실제 targeted 실행에서 이 반례가 통과했다. **CLOSED.**

### N5-C9-F2 — 모든 자유전자 kinetic energy와 thermal heat 구분

최초 verifier는 입력 \(20\to3+10.5+6.5\)의 자유전자 kinetic change를 thermal loss라고 설명했다. 자유전자의 열화 또는 동일 thermal pool 귀속이 선언되지 않았으므로 이 해석은 성립하지 않는다. 숫자 장부는 올바르며, 설명을 “tracked free-electron kinetic change”로 고치고 반환값에 `electron_pool=all_free_kinetic`을 명시했다. 모듈은 같은 frame의 에너지 contraction이고, source·frame·reaction multiplicity를 binding하는 일은 caller의 의무임을 명시했다. 실제 targeted 검사에서 owner tag와 숫자 장부의 보존을 확인했다. **CLOSED.**

### N5-C9-F3 — 누락 recoil과 명시적 recoil 0 구분

기존 `recoil_eV="0"` 기본값은 누락 recoil과 명시적으로 선택한 0-recoil closure를 구별하지 못했다. 이제 `recoil_eV`는 필수 keyword이며, 생략과 `None`을 거부한다. 선언된 0은 그대로 허용하고 positive recoil도 명시적으로 합산한다. 실제 검사에서 생략·unknown 거부, 0-recoil의 기존 숫자 보존 및 \(20=3+10+6.5+0.5\)의 비영 recoil 장부를 확인했다. **CLOSED.**

## 실제 실행과 source identity

| 실행 | 상태 | 실제 검사 | 이번 검토의 처리 |
|---|---|---:|---|
| `c23c_atomic_contract_20261023_v1` | `PASS_SCOPED` | 155 | 저장된 완료 receipt와 실행 source를 재사용. 재실행 0. |
| `c23c_atomic_repair_20261023_v2` | `PASS_SCOPED` | 6 | 세 finding에 대응하는 targeted 검사만 root가 새 실행. |

최초 execution source identity:
`7c6c53c4fa0fc687e421f0f2afc8f4a7d53fbdf590e1890854c80cf766a4cc75`

수정 후 execution source identity:
`ebbeccb95b0e5f1d4b0defffa313779f73204568aa4b1f281d8f3ef58f88a117`

수정 후 실제 `SUMMARY.json`의 wall time은 0.015551989003142808 s, CPU time은 0.015546393999999998 s, max RSS는 13,440 KiB다. worker CPU 1, native thread 1이며 CPU55는 사용하지 않았다. 자원 admission 및 lease release receipt가 존재한다. 이 값은 작은 계약 검사의 실행 기록이며 물리 모델의 speedup 측정이 아니다. 신규 ODE 0, empirical rate evaluation 0, 기존 155개 replay 0이다.

현재 `atomic_contract.py` SHA256:
`6246cff6dcc1bac18dd6f8c47b9e9da11f4d14a8bd342c21d30eee19eee9ca69`

현재 `verify_atomic_contract.py` SHA256:
`4ad46350df554c4fac9a46c7c8f682176d926fad0e868386046f43a196eda9c0`

현재 `verify_atomic_repair.py` SHA256:
`a417fb7976139fea7eeb77afbc30ec47223bf7ca4ae242bd382f2897ea9e3e00`

최초 실제 실행 source 2개는 `implementation/history/v1/`에 byte-identical로 보존되어 있다. `REVISION_MAP.json`의 `PREPARED_ROOT_LEASE_PENDING`은 생성 시점의 사전기록이다. 그 뒤 생성된 `runs/c23c_atomic_repair_20261023_v2/`의 실제 완료 receipt가 runtime authority이며, 이전 기록을 소급해 덮어쓰지 않는다.

## 남은 연구 범위 및 네 축 상태

실제 source를 energy frame·reaction·동위원소·유효 에너지/온도 구간에 binding하고, 누락 process 예산과 thermalization 소유권을 닫는 작업은 다음 연구 범위다. 이는 이번 제한된 모듈에 추가 blocking finding을 무한히 붙이는 요청이 아니다. HH83의 132-rate/324-steady/732-transient campaign은 이 계약 검증으로 완료 처리하지 않는다.

| 축 | 상태 |
|---|---|
| EXECUTION | 최초 155개 결과 재사용; 수정 관련 6개 실제 PASS; 검토자 과학 실행 0. |
| PUBLICATION | 검토자는 외부 mutation을 수행하지 않았다. parent의 publication 묶음에 이 검토와 실행 receipt를 포함한다. |
| BACKUP | 검토자는 별도 외부 백업을 수행하지 않았다. parent가 배포본과 readback 증거를 관리한다. |
| DAG | N5 inventory·소유권·quotient 계약은 이 범위에서 수용. 실제 atomic-rate coverage와 full energy closure는 OPEN. |

증거 경로: `runs/c23c_atomic_contract_20261023_v1/`, `runs/c23c_atomic_repair_20261023_v2/`, `theory/atomic_coverage/implementation/history/v1/PRESERVED_SOURCE.json`, `theory/atomic_coverage/implementation/REVISION_MAP.json`. 기계 판독 가능한 source pin, finding 및 scope는 같은 디렉터리의 `n5_independent_review.json`에 있다.
