# R6 독립 검토: exact atomwise energy-sum support

## 판정과 범위

**PASS_SCOPED_ENERGY_SUM_THEOREM.** 유한하고 분할 가능한 비음수 질량, 비음수 에너지, 명시적인 조건부 cap \(K\ge0\), 항상 허용되는 singles, \(E_a+E_b\le K\)인 doubles라는 계약 아래
\[
\delta=\max\{0,\max_h[H(E\ge h)-L(E\le K-h)]\},\qquad
d_{\max}=\frac{N-\delta}{2}
\]
는 정확한 최댓값이다. 독립적으로 유도한 상계, 구성적 greedy, dual certificate가 같은 목적값을 준다. 모든 \(d\in[0,d_{\max}]\)에 대해 exact marginal witness가 존재하며 남은 수학적 증명 의무는 없다.

이 검토자는 부모의 후보 명제와 frozen 계약에서 직접 증명을 구성했다. 검토 시점에는 실제 R5 문서가 아직 없었으므로 부모가 R5 문구와 본 검토의 가정·공식을 대조하여 R6로 채택한다. source identity 확인과 기존 consumer의 정적 읽기만 수행했다. 과학 프로그램, NPZ 배열 로드, 수치 시험, CAS, 외부 게시·백업은 실행하지 않았다. 구현 검증은 not_run이다.

대수적 attainable interval과 native consumer의 수용 interval은 구별한다. 보존된 중성 He 재고 조건에 의해 특정 proper window의 수용 interval이 줄어드는 식을 §8에서 유도한다.

## 1. 원문과 identity

기준 repo staging root: /workspace/scratch/db96a47a0549/bass_cr_work.

| 원문 | 확인한 identity | 이번 사용 |
|---|---|---|
| research/cr_he_energy_sum_20261028/CONTRACT.json | SHA256 d0d4e5db908bc990d12136cde1b299609f4032d5141e2c380a45a55811e68cd2 | frozen theorem·state·acceptance |
| research/cr_he_energy_sum_20261028/inputs/INPUT_MANIFEST.json | SHA256 f5317d1b19f721ba1d85ebfd90dbe89338e18da6dfa30134f96deee4881fb6b3 | 기존 input identity의 재사용 |
| research/cr_he_event_union_20261028/implementation/event_union.py | 18,732 bytes; SHA256 6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d | exact scalar, marginal, proper factor, native inventory, species·chemical mapping |
| research/cr_parent_event_native25_20261028/runs/prepare_v1/ATTRIBUTION_ARRAYS.npz | manifest상 233,050 bytes; SHA256 1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47 | pinned evidence 참조; 배열 미로드 |
| research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json | manifest상 4,394,309 bytes; SHA256 8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf | source provenance; 재적분·refit 없음 |

계약·manifest·event_union의 현재 SHA는 이번 정적 검토에서 직접 확인했다. NPZ·actual-source의 identity는 읽은 manifest의 재사용 근거이며 이번 리뷰에서 새 byte scan이나 계산을 주장하지 않는다.

사용자 physmath-research-loop 1.0.0의 RESEARCH_POLICY.md, THEORY_LOOP.md(R5/R6 포함), EVIDENCE_AND_HANDOFF.md를 읽고 적용했다. resource root는 skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop/references/ 이다. PR113의 구현·결과·예산을 사용하지 않았다.

## 2. 독립 primal 정의

각 atom의 질량 \(w_i\ge0\), 에너지 \(E_i\ge0\), 총질량 \(N=\sum_iw_i\)를 둔다. 질량은 분할 가능한 exact 값이며 정수 입자 수가 아니다. 허용 unordered pair에는 \(x_{ij}\ge0\), 각 atom에는 single \(s_i\ge0\)를 둔다.
\[
s_i+\sum_{j\ne i}x_{\min(i,j),\max(i,j)}+2x_{ii}=w_i,\qquad
d=\sum_{i\le j}x_{ij}.
\]
허용되지 않은 pair 변수는 0이다. diagonal은 두 marginal legs를 소비한다. singles가 항상 허용되므로 double legs의 packing inequality를 먼저 풀고 잔여 질량을 singles로 채우는 것은 이 등식 문제와 동등하다.

\[
\mathcal L=\{i:E_i\le K/2\},\qquad
\mathcal H=\{i:E_i>K/2\}.
\]
모든 low-low pair와 low diagonal이 허용되고 high-high pair와 high diagonal은 허용되지 않는다. high \(i\)의 low 이웃 집합은 \(\{\ell:E_\ell\le K-E_i\}\)이다. high를 에너지 내림차순으로 처리하면 이 집합은 포함관계로 커진다.

## 3. Tail deficit 상계

서로 다른 high energy \(h\)마다
\[
B(h)=\sum_{i\in\mathcal H:E_i\ge h}w_i,\qquad
A(h)=\sum_{\ell\in\mathcal L:E_\ell\le K-h}w_\ell
\]
로 둔다. \(E_i\ge h\)인 high가 double에 들어가면 상대 low는 반드시 \(E_\ell\le K-E_i\le K-h\)이다. 따라서 이 high tail에서 double로 흡수할 수 있는 질량은 \(A(h)\) 이하이며, single로 남는 high 질량은 적어도 \(B(h)-A(h)\)이다. 비음수 조건을 함께 사용하면 전체 single 질량은 적어도
\[
\delta=\max\left(0,\max_{h\in E(\mathcal H)}[B(h)-A(h)]\right)
\]
이다. high가 비면 \(\delta=0\)으로 정의한다. 각 double은 두 legs를 소비하므로 모든 feasible measure에 대해
\[
2d=N-\sum_i s_i\le N-\delta.
\]

## 4. Greedy가 상계에 정확히 도달함

서로 다른 high energy를 \(h_1>\cdots>h_r\), 그 level 질량을 \(b_j\), 누적 high 질량을 \(B_j=\sum_{k\le j}b_k\), 이웃 low 질량을 \(A_j=A(h_j)\)로 둔다. \(A_j\)는 비감소한다.

Greedy는 가장 높은 high부터, 남은 적격 low 중 가장 낮은 energy부터 가능한 만큼 매칭한다. level \(j-1\)까지 매칭한 총질량을 \(Q_{j-1}\)라 하자. 이전에 사용한 low는 전부 현재의 이웃 집합에 포함되므로 현재 사용 가능한 low 질량은 정확히 \(A_j-Q_{j-1}\)이다.
\[
Q_j=Q_{j-1}+\min(b_j,A_j-Q_{j-1})
=\min(Q_{j-1}+b_j,A_j).
\]
\(\Delta_j=B_j-Q_j\)라 쓰면
\[
\Delta_j=\max(\Delta_{j-1},B_j-A_j),\qquad\Delta_0=0.
\]
따라서 귀납적으로
\[
\Delta_j=\max(0,\max_{k\le j}(B_k-A_k)).
\]
마지막에는 \(\Delta_r=\delta\), \(m_{LH}=Q_r=H-\delta\)이다. 마지막 high threshold를 대입하면 \(\delta\ge H-A_r\ge H-L\), 또한 \(\delta\le H\)이므로 \(0\le m_{LH}\le\min(H,L)\)이다.

남은 low 질량 \(L-m_{LH}\)는 atom별 diagonal의 계수에 절반씩 넣고, 남은 high 질량 \(\delta\)는 singles에 넣는다. 이 구성은 모든 marginal과 pair cap을 만족하며
\[
d=m_{LH}+\frac{L-m_{LH}}2
=\frac{L+H-\delta}{2}=\frac{N-\delta}{2}
\]
에 도달한다. general matching theorem이나 numerical LP solve는 이 증명의 전제가 아니다.

## 5. 독립 dual certificate

double-leg packing의 dual은
\[
\min_{y_i\ge0}\sum_iw_i y_i,\qquad
y_i+y_j\ge1\ \ (i<j\text{ 허용}),\qquad
2y_i\ge1\ \ (i=i\text{ 허용})
\]
이다. feasible primal과 dual에는 pair별 제약을 더하여 \(d\le\sum_iw_i y_i\)가 직접 성립한다.

\(\delta=0\)이면 모든 \(y_i=1/2\)가 feasible이고 목적값 \(N/2=d_{\max}\)를 준다.

\(\delta>0\)이면 maximum deficit의 threshold \(h_*\)를 고른다. high tail \(B_*=\{i\in\mathcal H:E_i\ge h_*\}\)에 \(y=0\), low 집합 \(A_*=\{\ell\in\mathcal L:E_\ell\le K-h_*\}\)에 \(y=1\), 나머지에 \(y=1/2\)를 둔다.

- 모든 low-low pair와 low diagonal은 각 low의 \(y\ge1/2\) 때문에 feasible하다.
- \(B_*\)의 high에 연결되는 허용 low는 반드시 \(A_*\)에 있어 합이 \(0+1=1\)이다.
- 나머지 high와 low의 합은 적어도 \(1/2+1/2=1\)이다.
- high-high 및 high diagonal은 허용되지 않는다.

목적값은
\[
A(h_*)+\frac{L-A(h_*)}{2}+\frac{H-B(h_*)}{2}
=\frac{N-\delta}{2}.
\]
따라서 exact primal-dual equality를 얻는다. threshold가 같은 high atoms는 전부 포함해야 하며 동일 energy level의 임의 atom prefix로 대체하지 않는다.

## 6. 모든 target d, 희소성, K 의존성

최적 witness의 doubles가 atom \(i\)에서 쓰는 leg 질량을 \(r_i\le w_i\)라 하자. \(d_{\max}>0\), \(0\le d\le d_{\max}\)일 때 \(\lambda=d/d_{\max}\)를 두고 모든 optimal double coefficient를 \(\lambda\)배 하고 single을 \(w_i-\lambda r_i\)로 둔다. 이는 비음수이고 marginal을 보존하며 total double coefficient는 \(d\)이다. \(d_{\max}=0\)이면 target은 0만 가능하므로 singles를 직접 구성하고 division을 하지 않는다.

양의 질량 atom 수를 \(n_+\)라 하자. 매 positive greedy match가 최소 한 atom residual을 0으로 만든다. 최종 residual low는 atom별 diagonal 하나, residual high는 atom별 single 하나만 필요하다. 따라서 maximum witness는 \(n_+\)개 이하 events이다. 임의 target에서는 그 doubles를 축소한 뒤 atom별 singles를 넣어 \(2n_+\)개 이하 events를 얻는다. sorting은 \(O(n\log n)\), sorted sweep은 \(O(n)\) 산술·비교 단계이며 exact rational bit complexity는 별도이다.

K가 증가하면 허용 edge 집합이 커져 \(d_{\max}(K)\)는 비감소한다. 유한 source에서는 pair sums \(E_i+E_j\)와 diagonal \(2E_i\)를 포함한 유한 threshold 사이에서 일정하고, equality를 포함하므로 우연속이다. plot은 유한 cap 표본의 saved result라는 범위를 보존해야 한다.

## 7. 경계와 exact scalar

| 경우 | 결과·처리 |
|---|---|
| high 없음 | \(\delta=0,d_{\max}=N/2\); low diagonals |
| low 없음 | \(\delta=H=N,d_{\max}=0\); singles |
| 모든 질량 0 | \(N=\delta=d_{\max}=0\); positive event 없음; scaling division 없음 |
| \(K=0\) | \(E=0\) atoms만 low로 diagonal 가능; \(E>0\) atoms는 singles |
| \(E_i=K/2\) | low 분류; diagonal equality 허용 |
| 같은 energy | complete level의 질량으로 deficit 계산; atom-key tie-break는 witness만 정함 |
| 0 질량 atom | objective 불변; positive-event constructor에는 0 계수를 넘기지 않음 |
| \(E_i>K\) high | eligible low가 없어 singles |
| 유리수·분수 질량 | 정수 parity 제약 없음; \(w_i/2\) diagonal 허용 |
| malformed scalar·bool·float·NaN/Inf | 선언한 exact-input 정책으로 거부 |

기존 cutoff는 \(E_0=\operatorname{Fraction.from\_float}(0.1)\)이다. binary64의 정확한 값으로 쓰면
\[
E_0=\frac{3602879701896397}{2^{55}},\qquad
2E_0-\frac15=\frac1{5\cdot2^{54}}>0.
\]
따라서 \(K=1/5\)에서는 ghost diagonal이 제외되고 \(K=2E_0\)에서는 포함된다. float rounding으로 두 cap을 같게 만들면 exact acceptance를 위반한다. ghost 하나의 질량이 2인 fixture에서 두 경우의 optimum은 각각 0과 1이다. 이는 직접 유도한 예이며 실행된 test가 아니다.

일반 정리는 \(E\ge0\) 전체에서 성립하지만 이전 event_union.validate_atoms는 원 source domain \([E_0,10]\) 및 고정 4-partition을 강제한다. 새 core의 general atom API와 native adapter의 제한을 명시해야 한다. 일반 \(E=0\) fixture가 이전 native loader에 들어간다고 가정하지 않는다.

## 8. Proper history, species, inventory, normalization

원 source에서 \(w_i,N,d,\delta\)는 \({\rm m^{-3}s^{-2}}\) 단위 coefficient이다. \(q_i(t)=tw_i\)는 proper \([0,10^{10}]\)초에 주어졌고, 기존 consumer는
\[
W[a,b]=\frac{b^2-a^2}{2},\qquad0\le a<b\le10^{10}
\]
를 한 번 적용한다. \(W>0\)이며 density는 coefficient의 W배이다. source fit·normalization·quadrature는 재적용하지 않는다.

full selected-support witness는 모든 double 양쪽을 선택하므로 \(p=0\)이다.
\[
s=N-2d,\quad\nu=N-d,\quad
(\Delta n_{\rm HeI},\Delta n_{\rm HeII},\Delta n_{\rm HeIII})
=W(-N+d,N-2d,d).
\]
species 합과 He4 baryon 변화는 0이며 ionic charge 변화는 \(WN\), 즉 selected electron density이다.
\[
\Delta u_{\rm chem}
=W[I_1(N-2d)+(I_1+I_2)d]
=W[I_1N+(I_2-I_1)d],
\]
\(I_1=24.59\), \(I_2=54.42\) eV이다. selected kinetic energy는 \(W\sum_iE_iw_i\)로 pairing에 무관하다.

일부 birth partition만 선택하여 한 double의 상대가 선택 집합 밖에 남으면 기존 consumer의 p가 발생한다. coefficient 표기에서
\[
s=N-p-2d,\quad\nu=N-d,\quad
(-\nu,s,p+d),\quad
u_{\rm chem}=I_1N+I_2p+(I_2-I_1)d.
\]
따라서 p=0 식의 scope는 full selected support이다.

기존 consumer는
\[
W(N-d)\le H_0,\qquad
H_0=\frac{1085}{94}\frac{99}{100}\ {\rm m^{-3}}
\]
를 검사한다. 대수적 구간과 특정 window의 recipient 구간은
\[
\mathcal D_{\rm algebraic}=[0,d_{\max}],\qquad
\mathcal D_{\rm recipient}
=\left[\max\!\left(0,N-\frac{H_0}{W}\right),d_{\max}\right]
\]
이다. 두 번째의 왼쪽 끝이 오른쪽 끝보다 크면 수용 witness가 없다. raw finite-measure theorem은 유지되며 해당 conditional inventory/window return이 거부된다. 기존 gate를 제거하거나 inventory를 바꾸지 않는다. 이는 한 source return의 same-state 조건이며 실제 시간 진화된 EOS/transport 상태를 산출하지 않는다.

명시적 \(n_b=8750/47\,{\rm m^{-3}}\)가 주어진 경우에만 기존 consumer가 species density를 한 번 나누어 native source species21로 바꾼다. absolute volume은 null이다. 3200 active atoms, 별도 cutoff ghost, proper history 밖 unknown, retained photon·RR once-only port를 유지한다.

## 9. Cross duplicate C와 total d

d는 선택 집합 안 모든 double coefficient이다. C는 partition별 반환의 합에서 같은 parent가 두 번 세어지는 cross-partition double coefficient이다. 같은 partition double과 diagonal은 d에 들어가지만 C에 들어가지 않는다.

native support 안의 예로 \(E_1=1\)(partition 1), \(E_2=2\)(partition 2)에 질량 1씩, \(K=4\)를 둔다. 두 diagonal을 각각 coefficient \(1/2\)로 사용하면 \(d=1,C=0\)이다. cross pair를 coefficient 1로 사용해도 \(d=1\)이지만 \(C=1\)이다. 따라서 max d만으로 C는 정해지지 않는다. 기존 consumer가 실제 witness에서 계산한 C는 보고 가능하나, 이를 energy-sum support의 sharp max-C로 채택하려면 별도 목적함수 문제가 필요하다.

## 10. Finding → 근거 → 영향 → 최소 교정

| ID·대상 | 근거 | 영향 | 최소 교정·상태 |
|---|---|---|---|
| F01 algebraic interval / inventory | consume_event_union의 neutral inventory gate | 일부 d·window의 native return 거부 | §8 recipient intersection을 R5/R9·return contract에 반영; theorem proof 완결 |
| F02 p=0 mapping | evaluate_event_set이 partial selection의 p를 셈 | partial selection에서 species·chemical 오계산 가능 | full support로 scope 고정; partial은 §8 일반식 |
| F03 cutoff equality | CUTOFF=Fraction.from_float(.1) | decimal cap과 ghost diagonal equality 차이 | exact 비교, 두 fixture 분리; frozen acceptance가 포함 |
| F04 C와 d | §9의 두 exact witness | witness C를 max-C로 오표기할 위험 | C는 witness-specific, 최적 목적은 dmax |
| F05 theorem/API domain | validate_atoms의 [CUTOFF,10]·partition 조건 | 일반 E=0 예와 native 수용 범위 혼동 | general core 또는 native subset API를 명시 |
| F06 dmax=0·zero events | scaling과 positive Event 조건 | 0/0·zero-event 거부 | zero optimum 직접 singles 분기, zero events 생략 |

각 finding은 정확한 식·범위·분기로 본 검토에서 해결했다. 부모 R5/R9 및 C단계 반영은 후속 integration 의무이다. 새로운 global no-go나 novelty 주장은 하지 않는다.

## 11. C단계에서 실제 실행할 판별 의무

1. 작은 general allowed-pair graphs에서 별도로 쓴 exact dual enumeration과 비교한다. loop 제약은 \(2y_i\ge1\)이다.
2. production 함수에 의존하지 않는 evaluator가 witness의 모든 atom marginal, pair support, total d, dual feasibility와 목적값을 검사한다.
3. cutoff 두 cap, ties, empty low/high, zero masses, d=0/dmax/중간 target, malformed scalars를 실행한다.
4. wrong pair, 삭제 event, forged dual, wrong source/state/window/nb, 겹치는 replay의 거부를 검사한다.
5. pinned source를 재사용하고 original proper W, inventory, explicit nb, actual physical nulls를 보존한 return을 확인한다.

독립 oracle이 \(\{0,1/2,1\}\)만 열거하는 근거도 해석적으로 확인했다. 비음수 목적계수 아래 dual 좌표를 1로 잘라도 feasibility가 유지되고 objective가 증가하지 않는다. bounded polytope vertex의 tight edge는 \(y_i+y_j=1\), loop는 \(y_i=1/2\)이다. 연결 성분이 0/1 경계에 닿으면 값이 정수로 전파되고, odd cycle이나 loop가 있으면 모두 \(1/2\)로 정해진다. 둘 다 없는 bipartite 성분에는 두 색에 반대 부호의 작은 perturbation이 가능하여 vertex가 아니다. 따라서 half-integral optimum이 존재한다. 이 증명은 아직 실행하지 않은 oracle의 결과를 대신하지 않는다.

## 실제 실행·채택 상태

- 독립 수학 유도: completed / derived.
- 정적 contract·consumer 검토: completed / pass_scoped.
- 과학 계산·NPZ 배열 로드·source replay·CAS·production 검증: not_run.
- scientific CPU와 metadata/provider CPU: unmeasured / null.
- 외부 게시·백업·PR113 변경: 수행 없음.
- 최종 R6 채택: 부모가 실제 R5와 대조 후 기록.
- 문서 첫 저장 시 apply_patch hunk 문법 오류가 1회 있었고 파일 생성 없이 실패했다. 본 저장은 line-prefix를 프로그램적으로 구성하여 교정했다. 이는 artifact-edit 오류이며 과학 실패나 실행으로 분류하지 않는다.

