# CR_FERRERS_PREFIX_EXACT_V1: 에너지 순서 기반 exact flow-network 압축

**Authority:** `cosmosapjw-quantum/bass_cr`, immutable parent Draft PR123 HEAD `9f520c5e4042cb15bbd55da14ef946d6d9960d97`. Original NPZ SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. 이 문서의 물리적 외삽은 금지된다. 실제 He exclusive event kernel, 에너지 cap의 물리 선택, clock, normalizer, donor/partner bookkeeping, stopping은 공급되지 않았다.

## Definition and units

서로 다른 원자군 H,L은 각각 `2E_h>K`, `2E_l<=K`로 구분한다. 각 원자의 양의 또는 영인 marginal `w_i`는 m^-3 s^-2, 에너지 `E_i,K`는 eV이다. 허용 HL 사건은 `E_h+E_l<=K`; 비용 `χ_hl=1_{b_h != b_l}`. Fractional event flow `x_hl>=0`은 양쪽 원자의 marginal 용량을 소모한다. 고정 총 HL 사건 질량 `m=Σx`의 최소 비용을 `C_min(m)=min Σχx`라 한다. `M(c)=max{m:C_min(m)<=c}`, `d_max(c)=(L_tot+M(c))/2`; 마지막 식에는 모든 미사용 low mass가 에너지 허용 low-low diagonal을 통해 double event로 채워질 수 있다는 원래 전제가 사용된다.

## Theorem A: exact Ferrers/prefix extended formulation (derived)

각 low birth bin `b`에 포함된 원자를 에너지 오름차순으로 정렬하자: `l_{b,1},...,l_{b,n_b}`. 임의 high `h`에 대하여 허용 low는 정확히 `j<=k_{hb}`, 여기서

`k_{hb} = max{j: E_{l_{b,j}} <= K-E_h}`이다. 따라서 에너지 허용 관계는 bin별 prefix들의 합이다. 각 bin의 low 열에 자식 방향 capacity `U > Σ_i w_i` 와 cost 0을 가진 정적 이진 segment-tree DAG를 만든다. 각 high `h`는 bin `b`의 prefix `[1,k_{hb}]`을 정확히 분할하는 O(log n_b)개 canonical segment nodes에 `U` 용량, cost `χ(h,b)`로만 연결한다. 원래 source->high와 low->sink 용량은 그대로 둔다. 원자 margin, 전체 HL flow 및 cross-bin 비용을 동일하게 유지한다.

**Proof (projection):** 원래 허용 edge `(h,l_{b,j})`마다 해당 prefix의 canonical partition에 j를 포함하는 segment는 정확히 하나이다. 따라서 원래 실현가능한 `x_hl`을 유일한 `h -> segment -> ... -> l`에 흘리면, 각 모든 source/high/low/sink 용량 및 비용이 보존된다. 역으로 압축 DAG에서 양의 유량은 유한 비순환 경로의 비음수 분해를 갖고, high에서 low leaf로 가는 모든 경로는 반드시 해당 high의 허용 prefix 내부에서 끝난다. 원래의 허용 HL edge로 경로 질량을 대응시키면 정확히 동일한 `m`, `C`, 원자별 `w_i` 부등식을 얻는다. `U`는 총 공급을 넘으므로 내부 경로가 원래 없던 제약을 부과하지 않는다. 두 방향의 사상이 있으므로 `(m,C)` 가능집합, `C_min`, `M(c)`, `d_max(c)`가 정확히 동일하다. 끝.

## Theorem B: original-graph witness and dual lift (derived)

원래 DAG의 고정 유량에 대해, 각 high->segment arc의 순유량에 high label을 부착한 다음, tree 내부의 순유량에 맞춰 label을 하위 자식에게 분배할 수 있다. 모든 구간 node의 유량 보존과 내림순서(부모 먼저) 구성으로 유한 단계 안에 low leaf별 labelled flow `x_hl`이 만들어진다. 초기 labelled 총량과 child arc 총량이 일치하므로 greedy label split은 언제나 가능하다. 모든 계산은 정확한 i128 정수, 예산 내 fractional endpoint에선 공통 분모 k를 이용한다.

residual의 0/±1 cost와 도달 가능한 잠재함수 `d(v)`에 대해, 임의 원래 허용 HL pair로 이어지는 압축 경로가 존재하므로 `d(l)-d(h)<=χ_hl`가 성립한다. source/sink 부분에서 구성된 `p_h=max(0,d(h)-d(s))`, `p_l=max(0,d(t)-d(l))`, `λ=1/k`(양의 slope k) 는

`p_h/k + p_l/k + χ_hl/k >= 1`

을 만족한다. 잔차 순환 potentials의 cost -k인 `t->s` arc와 complementary slackness를 통해 `Σ_i w_i p_i + c = k M(c)`가 성립한다. 입력에서 영용량 원자는 가격 1을 부여해 대응 행 비용 0으로 dual feasibility를 유지한다. 원래 이웃이 없는 양의 high 원자는 flow=0 및 가격0으로 제거 가능하다. 따라서 Python consumer가 **원래 3,201개 원자와 모든 102,831 admissible HL edge**에서 primal-dual gap=0을 직접 검증하도록 하였다. 이렇게 검증되지 않은 압축 graph 잠재함수만으로 과학 claim을 승인하지 않는다.

## Exact complexity and limits

Low tree node는 O(L), tree edge는 O(L), high-prefix attachment는 O(Σ_h Σ_b log(1+n_b))개다. 일반 dense HL edge의 수 O(HL)와 달리 압축의 topology는 O(L+H B log L) 크기다. 모든 원래 HL 사건 witness를 출력하거나 original dual constraint를 전수 검사하면 출력/검증 비용은 다시 O(number of output pairs + number of original admissible edges)일 수 있다. Potentials-Dijkstra SSP의 augmentation 횟수와 exact rational bit complexity에는 별도 상한이 필요하고, 이 압축만으로 계산시간 단조 향상을 보장하지 않는다.

원본 K=3eV fixture에서 high 2,748개 중 high 2,295개는 양의 low 지원으로 향하는 허용 edge가 없다. 나머지 453 high와 453 low, 논리적 102,831 HL edge에 대해 현재 구현은 4,307개의 forward arc 및 1,358개 network vertex로 정확히 축약한다. `102831/4307≈23.874`는 graph arc 수 압축비이며 메모리·walltime 속도비가 아니다.

이론은 **bin-specific constant cost**와 **energy-sum threshold / nested neighborhoods**를 전제로 한다. 각 원자쌍마다 개별 확률·시간·물리 kernel이 다른 경우 일괄적으로 동일한 비용을 부여할 수 없으므로 동일한 축약은 자동으로 성립하지 않는다. 또 fixed-C joint region의 전체 성질은 budget upper frontier와 별개의 역문제다.

## Literature boundary

Király & Kovács (2012), *Efficient implementations of minimum-cost flow algorithms*, https://arxiv.org/abs/1207.6381 : SSP, potentials, cost-scaling 및 network simplex에 관한 선행 이론·구현.

Ghiyasvand (2015), *Solving the parametric bipartite maximum flow problem in unbalanced and closure bipartite graphs*, https://doi.org/10.1007/s10479-015-1807-7 : 무한 용량 이분 그래프의 별도 parametric max flow 선행 결과. 이 문서의 하나의 cross-budget min-cost flow 알고리즘과 동일한 정리가 아니다.

Range-edge segment-tree gadget은 일반적인 알고리즘 아이디어로서 신규성 주장을 하지 않는다. 여기서 새로 구성·검산한 부분은 CR의 정확한 energy/bin 수학과 source-locked atom-level primal-dual certificate 보존이다.
