# R4 — 구체적 사건 구성과 작은 정확한 예

단위 CR_PHYS02_HE_EVENT_UNION_V1. 중앙 관찰22a99cb9b1691274e74c122d54521be4f2f51ba5의 **28/88**, 88 nodes/17 edges를 유지하며 집계 효과는 0이다. 아래는 유도된 정확한 수학적 fixture다. 실제 PHYS02 source의 새 계산이나 empirical joint kernel 측정이 아니다.

## 세 가지 직접 구성

유한 원자 marginal을 μ=Σₓmₓδₓ, mₓ≥0으로 쓴다. 모든 구성은 atomwise μ를 보존한다.

1. **All-single:** S=μ, D=0. C=0이며 parent 사건 수는 N=μ(U)다.
2. **Diagonal-double:** S=0, D=Σₓ(mₓ/2)δ_(x,x). 이때 2π₁D=μ, 전체 double 사건 수는 N/2이지만 C=0이다. C와 전체 double count가 다른 양임을 보여 준다.
3. **Half-shift:** N>0일 때 질량 원[0,N)을 partition별 연속 block으로 배치한다. 각 atom은 길이 mₓ인 interval을 차지하고 f가 그 label을 돌려준다. T(u)=u+N/2 mod N으로 두고 D=(1/2)(f,f∘T)_#du, S=0으로 정의한다. T가 measure-preserving involution이므로 D는 symmetric이고2π₁D=μ다. 각 partition의 within-double mass는 max(0,nᵢ−N/2)이므로 C=N/2−Σᵢmax(0,nᵢ−N/2)=min(N/2,N−maxᵢnᵢ)다. N=0이면 영측도가 유일한 구성이며 C=0이다.

Unordered pair(x,y,w)는 x≠y일 때 D(x,y)=D(y,x)=w/2를 뜻한다. Pair weight를 symmetric matrix의 두 entry에 각각w로 넣으면 marginal을 두 배로 만들어 거절해야 한다.

## n=(2,1,1)의 정확한 예

세 atoms a,b,c가 서로 다른 birth partitions에 있고 μ=2δ_a+δ_b+δ_c라 하자. N=4, M=2이므로 C_max=min(2,2)=2다. 이 예의 질량값은 수학적 fixture이며 실제 source에서 읽힌 nᵢ가 아니다. 네 번째 birth partition의 질량을 0으로 두면 실제 네 분할 형식에 그대로 포함된다.

| 구성 | Single records | Unordered double records | C | Union parent ν_U | Union double δ_U |
|---|---|---|---:|---:|---:|
| All-single | (a,2),(b,1),(c,1) | 없음 | 0 | 4 | 0 |
| Diagonal-double | 없음 | (a,a,1),(b,b,1/2),(c,c,1/2) | 0 | 2 | 2 |
| Half-shift maximum | 없음 | (a,b,1),(a,c,1) | 2 | 2 | 2 |

Half-shift는 a=[0,2), b=[2,3), c=[3,4)의 배치에서 길이 2의 shift다. 따라서 D_ab=D_ba=D_ac=D_ca=1/2이고 다른 entries는 0이다. Atomwise electron incidence는 a에 2, b에 1, c에 1로 원 μ와 정확히 같다.

## Partition별 반환과 union의 차이

Half-shift 최대 witness에서 각 partition은 자신과 만나는 double 사건을 반환한다.

| 집합 | s | p | d | ν=s+p+d | δ=p+d | (ΔHeI,ΔHeII,ΔHeIII) |
|---|---:|---:|---:|---:|---:|---|
| {a} | 0 | 2 | 0 | 2 | 2 | (−2,0,+2) |
| {b} | 0 | 1 | 0 | 1 | 1 | (−1,0,+1) |
| {c} | 0 | 1 | 0 | 1 | 1 | (−1,0,+1) |
| Partition 합 | 0 | 4 | 0 | 4 | 4 | (−4,0,+4) |
| U={a,b,c} | 0 | 0 | 2 | 2 | 2 | (−2,0,+2) |

보정은 union minus partition sum이므로(+2,0,−2)=(+C,0,−C)다. Ionic charge correction은−4=−2C이고, 이미 disjoint인 selected electron count 4의 correction은 0이다. 각 atom의 에너지 εₓ가 무엇이든 selected kinetic marginal Σₓεₓμₓ도 바뀌지 않는다. 이 예는 저장 kinetic 값을 새로 계산하지 않는다.

Fixture의 밀도 단위를 m⁻³로 선택하고 같은 조건부 n_b=8750/47m⁻³를 적용하면 native species correction은(47/4375,0,−47/4375)이다. Chemical bookkeeping correction은−(24.59+54.42)×2=−158.02eV m⁻³다. 이는 actual heating 또는 donor work가 아니다.

## 모든 중간값과 판별력

0≤λ≤1에서 all-single과 half-shift를 섞어 S_λ=(1−λ)μ, D_λ=λD_half로 두면 같은 μ를 보존하면서 C_λ=2λ를 얻는다. 이 예의 union parent는 4−2λ, single count는 4(1−λ), double count는 2λ다. 따라서 C의 전체 interval [0,2]가 달성된다.

반면 diagonal-double은 C=0이면서 double count 2다. 그래서 C를 전체 He double-ionization count로 대체하는 구현, selected electron correction에−2C를 적용하는 구현, 또는 partition 합에 source-ion 보정 없이 RR을 다시 더하는 구현은 이 예로 구별할 수 있다. 이러한 사례의 실제 실행 결과는 후속 bounded tests가 기록한다.
