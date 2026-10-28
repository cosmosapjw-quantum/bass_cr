# R2 문헌 검토: incidence·weighted Hall·joint 범위

**범위:** 2026-10-28, 지정한 1차 문헌의 실제 본문과 이 단위 CONTRACT.json 대조. 문헌 단계만 수행했다. 새 polygon 증명·과학 계산·코드 실행·원격 변경은 수행하지 않았다.

## 실제 읽은 1차 자료

1. Roger E. Behrend, *Fractional Perfect b-Matching Polytopes I: General Theory*, arXiv:1301.7356v1 (2013). 실제 읽은 URL: https://ar5iv.labs.arxiv.org/html/1301.7356v1 . §1.2, §2 식(2)/(4), §3 Theorems3/6, Theorem22 진술을 확인했다. Exa 추출은100,000자 cap이므로 논문 전체 독서로 기록하지 않는다.
2. Twan Koperberg, *Couplings and Matchings: Combinatorial notes on Strassen’s theorem*, arXiv:2202.02092v1 (2022). 실제 읽은 URL: https://ar5iv.labs.arxiv.org/html/2202.02092 . Theorems1/2, Proposition4, §3의 equivalence와 Proposition6을 확인했다. arXiv 서지·v1도 https://arxiv.org/abs/1301.7356 및 https://arxiv.org/abs/2202.02092 에서 확인했다. ar5iv 일반 web open은 실패했으나 Exa actual-text fetch는 성공했다.

## 1. Behrend의 loop와 우리 사건 변수

**문헌 사실:** Behrend는 loop를 해당 정점의 incident-edge 집합에 한 번 넣으며 incidence entry도1이다. 따라서 \(\mathcal P(G,b)=\{x\ge0:I_Gx=b\}\)의 loop weight를 우리 double-event mass와 그대로 동일시하면 안 된다. 비음수 실수 가중치, loops·multiple edges를 허용하는 일반 polytope와 그 비공집합·vertex 이론은 이미 prior art다.

**계약에 대한 해석:** 우리 unordered 사건 질량을 \(p_{ij}\), singles를 \(s_i\)라 쓰면
\[
m_i=s_i+2p_{ii}+\sum_{j\ne i}p_{ij}.
\]
Behrend 좌표로 옮길 때 physical loop는 \(x_{ii}=2p_{ii}\), off-diagonal은 \(x_{ij}=p_{ij}\)다. Singles는 별도 slack 변수로 구분한다(그래프로 구현하면 별도 loop). 그러면
\[
d=\sum_{i<j}x_{ij}+\tfrac12\sum_i x_{ii}^{\rm physical},
\qquad C=\sum_{\substack{i<j\\b_i\ne b_j}}x_{ij}.
\]
Physical loop의 허용조건 \(2E_i\le K\)와 항상 허용되는 single slack을 합쳐서는 안 된다. 이는 **incidence 변환**이며 joint polygon의 증명이 아니다.

## 2. Weighted Hall/finite Strassen의 정확한 사용 범위

**문헌 사실:** Koperberg Proposition4는 finite bipartite \(A,B\), \(w\ge0\), **\(w(A)=w(B)\)**에서 모든 \(U\subseteq A\)의
\[
w(U)\le w(N(U))
\]
가 지정된 각 정점 marginal을 갖는 비음수 edge weighting의 존재와 동치임을 명시한다. Theorem1은 확률 coupling 버전이고 Proposition6은 allowed relation 밖 질량을 \(\varepsilon\) 이하로 허용하는 deficiency 버전이다. Hall/Strassen equivalence와 flow를 통한 coupling 구성은 기존 결과다. 읽은 HTML의 Lemma3에는 \(w(B)=w(B)\) 표기가 있으므로 균형 전제는 명시적인 Proposition4를 기준으로 삼는다.

**적용 한계:** Low/high의 총 capacity가 서로 다르면 각각을 따로 정규화한 probability coupling은 원래 capacity 문제와 같지 않다. 필요한 selected marginals·잔여 singles 또는 slack의 대응을 먼저 명시해야 한다. 이 bipartite 정리를 loop와 low–low 사건까지 포함한 전체 사건계에 곧바로 적용하지 않는다.

## 3. 이번 주장의 prior-art 경계

일반 fractional matching, weighted Hall, finite coupling, deficiency 정리 자체의 novelty를 주장하지 않는다. 이번 후보는 CONTRACT의 **모든 허용 positive-mass low–high pair가 cross-bin**이라는 추가 전제 아래, 에너지 support를 보존하는 \((d,C)\)의 정확한 투영과 원래 atom marginals를 갖는 공동 증인을 제시하는 특수화다. 두 개의 개별 optimum이나 각각의 coupling 존재만으로 공동 달성은 따라오지 않는다. 그 전제의 실제-source 확인, 공동 달성·퇴화 경우·전체 영역 증명은 이후 R3+의 독립 의무이며 **R2에서 승인하지 않았다**. 두 문헌 조사만으로 전 세계 신규성을 확정하지 않는다. Actual exclusive kernel·physical \(K\)와 chemistry activation도 공급하지 않는다.
