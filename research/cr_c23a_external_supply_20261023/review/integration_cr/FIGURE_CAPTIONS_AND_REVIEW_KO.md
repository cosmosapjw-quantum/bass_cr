# C23A 최종 그림 검토 및 caption

`07-Figure-Residual-Error-Pass.txt`와 `08-Figure-Hostile-Audit.txt`를 읽고 적용했다. analysis_v2 PNG 세 장을 실제 `view_image`로 열었고, 수정 후 analysis_v3의 exposure PNG를 다시 열었다. 다른 두 그림의 v3 PNG/PDF는 v2와 byte-identical임을 확인하여 그 시각 검토를 재사용했다. 검토 identity와 계산한 출판 크기는 `FIGURE_REVIEW.json`에 있다.

**최종 판정: analysis_v3 세 장은 180 mm 컬러 배치에서 PASS.** 90 mm로 직접 축소하는 배치는 변경이 필요하다. 남은 source-model 의무는 그림 caption에 명시한 범위를 따라 유지한다.

## 의미와 패널 구조

| 그림 | 보여주는 내용 | 처음 읽는 독자의 오해를 막는 caption 요소 |
|---|---|---|
| `p19_source_moments` | 59개 P19 source node의 이온화율과 heating/ionization ratio | imposed moment table이며 incident spectrum 재구성이 아님. 선은 source node를 연결 |
| `p19_frozen_exposures` | 각 redshift에서 독립적으로 고정한 공급을 처음 중성인 H/He에 적용한 온도·전자 생성 | redshift는 각각의 고정 배경 label. θ=1,10,100은 독립 exposure이며 IGM history가 아님 |
| `deposition_moments_and_cost` | 동일 count/energy 입력의 서로 다른 침적 채널과 실제 사전 적분 비용 | raw reported 채널, 재정규화 없음. 시간비는 construction+64 query 및 9 pairs 전부 포함 |

두 세로 패널은 같은 x축과 color 의미를 공유한다. deposition 두 패널은 물리 판별과 계산 비용이라는 다른 양을 보여주며 각 y축이 명확하게 다르다. 레이아웃을 재설계할 필요는 없다.

## Ranked residual ledger

| 우선순위 | 관측 | 처리 |
|---|---|---|
| P0 | 범위 caption을 적용하면 원 데이터·모델과 어긋나는 의미 없음 | CLOSED |
| P1 | v2 exposure의 upper-right legend가 green θ100 하강부 z≈7.5–8.0, T≈27.5–28.5 kK를 덮음 | 부모가 v3에서 lower-right로 이동. 실제 재열람으로 선·peak·shoulder 모두 가리지 않음을 확인, CLOSED |
| P1, 90 mm 조건 | 직접 절반 폭 축소하면 legend text가 약 4.91 pt, 마지막 그림은 약 3.50 pt | 180 mm 배치로 확정. 90 mm가 필요할 때만 패널 분리/폰트 재설정 |
| P2, 흑백 조건 | exposure의 orange/green 곡선은 실제로 가까워 일부 겹침. 컬러는 구별되나 흑백에서는 구별이 약해질 수 있음 | 현재 컬러 배치 PASS. 흑백 투고가 정해지면 dash style 추가 |
| P3 | 마지막 그림의 legend는 180 mm에서 약 7.0 pt로 세 그림 중 가장 작음 | 180 mm에서 판독 가능. 이 폭보다 작게 배치하지 않음 |

v1의 peak 가림, v2의 shoulder 가림, v3의 수정은 각각 보존한다. 그림 수정은 저장된 결과의 postprocess였으며 source subflow·ODE를 다시 실행하지 않았다.

## 출판 크기 검토

실제 PDF MediaBox와 plotting font 설정으로 계산했다. 종이에 출력한 검사는 수행하지 않았다.

| 그림 | PDF 원 폭 | 180 mm legend | 90 mm legend | 판정 |
|---|---:|---:|---:|---|
| source moments | 183.303 mm | 9.82 pt | 4.91 pt | 180 mm PASS |
| frozen exposures | 183.303 mm | 9.82 pt | 4.91 pt | 180 mm PASS |
| deposition/cost | 231.563 mm | 7.00 pt | 3.50 pt | 180 mm PASS, 추가 축소 비권장 |

실제 PNG에서 label·tick·제목·수식의 잘림은 보이지 않았다. v3 exposure legend는 오른쪽의 모든 데이터보다 낮은 빈 영역에 있다. 마지막 bar legend는 100 eV 부근 bar 상단보다 위에 있고, timing legend는 측정점 아래에 있어 데이터에 겹치지 않는다.

## 사용할 수 있는 caption 초안

### Figure 1 — P19 source moments

**Prescribed P19 fiducial UVB rate moments.** (a) Photoionization rates for H I, He I and He II at the 59 nodes of the pinned arXiv:1801.04931v1 fiducial table. (b) The ratio of the tabulated heating rate to the corresponding ionization rate, in eV per ionization event. Lines join the supplied nodes. Redshift labels the imposed background; these moment ratios do not reconstruct an incident UV/X-ray spectrum. The separate caller binding-energy registry does not establish the source's numerical threshold convention.

### Figure 2 — Frozen-source exposures

**Independent H/He exposures to fixed external photoionization and heating moments.** Every redshift label starts a separate fixed-proper-volume calculation with HI=1, HeI=0.083 per initial H nucleus, the other three H/He populations explicitly zero, and T₀=100 K. The dimensionless duration is θ=maxᵢΓᵢΔt=1,10,100. Panels show (a) final gas temperature using the evolving particle number and (b) electrons produced per initial H nucleus. These are source-only exposure diagnostics; recombination, cooling and expansion are excluded. The prescribed durations need not fit within the cosmic age and the connected curves are not an IGM thermal history.

### Figure 3 — Spectral response and measured cost

**Channel-sensitive electron deposition and bounded precontraction timings.** (a) The downloaded finite FS2010 response at ξ=0.1 gives different ionization, heating and excitation energies for one 100 eV electron and for equal weights at 10 and 190 eV, although both inputs have electron count 1 and total kinetic energy 100 eV. Raw reported channels are stacked without renormalization; their small tabulation closure defects are retained. (b) Nine paired single-CPU measurements compare direct evaluation of 64 queries with fresh precontraction plus the same 64 queries, covering three declared PL spectra and three repetitions. The dashed line marks the median ratio 4.91 and the dotted line equal elapsed time. These measurements concern the finite Python source operator; wall-time stability and cosmological-ODE speedup were not measured.

## 제한된 독립 질문 확인

1. **z축이 한 기체의 진화 시간인가?** 그림 2 label과 caption은 independent fixed background라고 명시한다.
2. **H/Γ가 incident spectrum을 결정하는가?** supplied rate ratio만 보여주며 spectrum 재구성을 주장하지 않는다.
3. **bar 총합을 정확히 100 eV로 강제했는가?** 저장 raw channel을 그대로 읽어 stack했다. `analyze_saved.py`에서 정규화 연산이 없다.
4. **시간비의 준비 비용이나 불리한 pair가 빠졌는가?** `direct_over_build_plus_queries`의 9개 값 전부를 표시했다.
5. **green curve의 최대 및 하강부가 가려지는가?** v3 실제 이미지에서는 가림이 없다.
6. **현재 구조와 축소 레이아웃 중 무엇을 택하는가?** 현재 세 그림을 180 mm 컬러로 유지한다. 90 mm가 요구될 때만 해당 폭에 맞춘 별도 레이아웃을 만든다.

그림 안에 추가 annotation을 넣을 필요는 없다. source 범위·데이터 버전·timing의 해석은 위 caption으로 전달하는 편이 현재의 명료한 축과 panel을 유지한다.

## 상태

| EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|
| PNG 실제 보기·PDF geometry·source/caption 읽기, science 재실행0 | analysis_v3 180 mm 컬러 후보 승인 | review는 로컬; durable ACK는 부모 기록으로 연결 | v2 잔여 finding CLOSED → C9 그림 검토 PASS → C10 게시·백업 |
