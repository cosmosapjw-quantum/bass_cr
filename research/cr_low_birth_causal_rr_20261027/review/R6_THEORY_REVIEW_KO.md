# R6 독립 물리·수학 검토

## 판정과 정확한 검토 대상

**PASS_SCOPED_THEORY — 미해결 blocking finding 0, 미해결 nonblocking finding 0.** 이 판정은 고정된 유한 상태·frozen bath 모형의 이론과 source-to-return 해석에 한정된다. Production 코드, 실제 floating-point 결과, 실행 예산 준수, release 및 물리적 활성화에 대한 판정이 아니다.

- Unit: `CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1`.
- `CONTRACT.md`: SHA256 `0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210`.
- `THEORY_KO.md`: 40,012 bytes, SHA256 `d42d88d8adefa0a08f847f7a38440b038b5383ee68f3bfadb9cc5d5ddb18d026`.
- `THEORY_TO_CODE_KO.md`: SHA256 `7d3f696cb9b183220a32694b73936a5a0ffabc9f45650eb99c6bf56a8f679133`.
- 실제 PR109 `ACTUAL_SOURCE_RECORDS.json`: 4,394,309 bytes, SHA256 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`.

완전한 읽기 대상·현재 해시는 동반 `R6_THEORY_REVIEW.json`에 기록했다. 파일이 바뀌면 변경된 가정·식에 대해서만 다시 검토해야 한다.

## 검토자의 역할과 방법

검토자 `/root/source_qualification`은 이번 및 이전 source qualification, 공급자 관측, 알고리즘 primary-literature 대조를 맡았다. 이번 주 유도와 production 구현의 작성자는 아니다. 주 유도·독립 sparse reference의 작성자는 `/root/theory_review`다. 이 검토자는 초안을 읽고 아래 세 가지 정의역·표기 clarification을 요청했으므로 blind review라고 주장하지 않는다.

이번 검토는 문서·원 코드의 정적 판독, 식의 해석적 대조, JSON metadata 및 byte hash 확인이다. 과학 모듈 import, source quadrature, coefficient evaluation, ODE/propagator 실행, CAS, old-science replay는 모두 0이다. 원 source/RR 검증은 identity와 범위가 일치하는 부분을 재사용했다. 취득·문서화·hash 비용은 별도로 계측하지 않았고 0으로 쓰지 않는다.

Root의 R01 preflight와 실제 prior source/closeout의 양쪽 R3 receipt를 읽었다. 이 보고서는 단계 게시 전에 준비한 독립 검토 산출물이며 R06의 실제 최신 owner/HEAD/receipt preflight나 게시·백업 자체를 인증하지 않는다. 해당 live stage 작업은 root가 담당한다.

## 핵심 확인

### Source, 동일 상태와 정규화

Actual `direct_0p1_10` record를 직접 읽었다. 3,200 active atoms와 direct-cutoff atom 하나, proper [0,10^10] s, history 밖 unknown, 100 K, fixed proper volume의 크기 null이 명시되어 있다. Total source의 E≤10 절단은 high-born E=10 성분을 포함할 수 있으므로 이 선택을 대신하지 않는다.

새 H1/He4-only inventory에서 nb=nH+4nHe=8750/47 m^-3는 명시적 model normalization이다. 이는 원 source의 nb 제공이나 다른 실제 baryon의 부재를 입증하는 것이 아니며, PR109 nb/native25 null을 바꾸지 않는다. Source의 neutral-target·angle·729/proper conversion은 재적용하지 않고 새 RR의 ionic target factor를 lambda에 한 번 넣는 구분이 맞다. Absolute volume 없이 extensive worldtube 총량은 만들지 않는다.

실제 source 문서의 4ca5 snapshot, retained D 및 PR109 record는 서로의 역할을 유지한다. 원 generation revision 또는 잃어버린 full9600 G가 새로 회수됐다고 주장하지 않는다. Coulomb law와 RR fit을 읽어 현재 source bindings와 대조했으며, 새 constants recipe를 쓰는 coefficient 평가가 새 의존성임을 확인했다.

### 유한 proper-time 응답

Variation-of-constants와 Metzler positivity의 가정이 맞다. Ramp의 t²phi2, 실제 occupancy의 t³phi3, 창 시작 a에 비례하는 a*d*phi1 항은 절대 source clock을 보존한다. Bin occupancy는 기존 n(a)를 유지하는 항과 a*h²phi2, h³phi3 forcing 항을 모두 갖는다. Midpoint에서 빈 상태로 재시작하거나 창마다 source clock을 0으로 되돌리는 해가 아니다.

Count와 energy identity는 각각 drift 항의 telescoping 및 d_j(E_j−E_(j−1))=b_j에서 나온다. Direct cutoff와 drift cutoff를 구분하고, captured kinetic과 photon energy를 같은 event의 독립 이중 sink로 합하지 않는다. Actual occupancy와 endpoint lambda·n은 mean lifetime 또는 cumulative count/elapsed-time 평균과 구별된다. T의 rate는 known-history left limit이며 post-T source를 만들어내지 않는다.

### Uniformization과 작은 RR 채널

Count 확장에 대한 P의 stochasticity와 active block의 substochasticity를 구분했다. 양의 ramp 가중치의 finite-n 절단 합은 0.5 Pr(Pois(x)≤M−2)이고, 누락 count tail은 Pr(Pois(x)≥M−1)이다. Occupancy 가중치의 합은 (1/6) Pr(Pois(x)≤M−3)이며 finite triangular sum은 같은 M에서 truncated capture와 lambda·O의 일치를 준다.

작은 채널의 추가 bound는 k-step capture probability≤k*lambda_max/nu와 Poisson third factorial moment로 확인된다. 누락 n≥M+1의 세 칸 이동이 **Pr(Pois(x)≥M−2)**를 주므로 count tail과 한 칸 다른 지수가 맞다. 여기의 S_A는 active-source coefficient 합이며 direct-cutoff birth를 포함하지 않는다. Capture kinetic/photon reward의 Emax 및 Emax+I 상한은 이 irreversible downward 모형에 결속된다.

누적 prefix 두 개의 차가 자동 lower bound는 아니다. 식17의 비대칭 endpoint bound와 실제 bin의 별도 positivity·오차 확인이 필요하다. Absolute Poisson mass와 재정규화된 Fox–Glynn weights를 구별했고, analytic truncation과 binary64 roundoff/outward certification도 분리했다. 관련 원전과 실제 취득 기록은 `../literature/PRIMARY_READMAP.json`, `PRIMARY_ACQUISITION.json`에 있다.

### Native25, 전하와 retained photon

기존 authoritative native21 순서의 H1I/II indices1/2 및 He4I/II10/11과 새 RR map이 맞는다. RR에서 ionic charge와 zeta가 같은 양만큼 줄므로 q·DeltaY−Delta zeta=0이며 thermal-electron count는 변하지 않는다. w_nt는 captured kinetic만 제거하고 w_ext는0, logT는 frozen diagnostic0이다. Photon atoms는 actual per-energy capture measure에서 만들 때만 정당하며 retained port를 heating으로 바꾸지 않는다.

Primary source의 parent-ion chemistry가 없어 full-source native25 closure는 null이다. Nactive/nb와 Uactive/nb는 닫힌 charge-neutral source state가 아닌 diagnostics다. 일반 baryon-changing quotient는 positive denominators와 physical final densities를 요구하고 density-derived 좌표에만 적용한다. Cutoff join의 조건부 Cv 식에는 추가 thermal particle 수의 heat-capacity 항이 들어가며 physical temperature history의 완료를 주장하지 않는다.

## 검토 중 제기하여 해결한 사항

| ID | 원 finding | 최종 해결 |
|---|---|---|
| R6-N01 | 일반 quotient의 양의 분모·최종 density domain 및 intensive logT 적용 제외를 명시할 필요 | 식12 뒤에 모두 명시 |
| R6-N02 | Active 생성자와 conservative count extension의 dimension/표기 구분 필요 | L_act/A_act, L_count/A_count, P_act와 active projection을 명시 |
| R6-N03 | A_act가 vector와 scalar sum에 중복 사용됨 | scalar를 S_A로 분리하여 식16c 및 occupancy tail에 일관 적용 |

세 사항 모두 현재 검토 hash에서 직접 확인했다. 주 유도의 다른 해석적 오류나 fixed contract와의 충돌은 발견하지 않았다.

## 별도로 남는 실제 검증과 claim ceiling

16개 analytic review 항목의 상세 근거를 JSON에 기록했다. 이 숫자는 실행한 numeric test 수가 아니다. 다음은 이론 결함이 아니라 이후 code/run 단계의 고정 의무다.

- C4 actual host/code/input/budget admission, 새로운40 CPU-s cap과 실패·coordinator 포함 계측.
- 실제 positive coefficients/P, finite output, source identity 및 ownership/state/support 거절.
- 각 positive RR N/K/photon quantity 자체의 scale에서 독립 reference≤1e−9; count/energy와 stoichiometry≤1e−11.
- Input N/E 및 tiny channel의 분리된 truncation allocation, endpoint-to-bin tail 전파, floating-point 오차 확인. Ordinary floating-point tail 평가를 outward interval로 부르지 않는다.
- Scalar/zero-rate/zero-source 한계와 전체 source closure null의 유지.

이 리뷰로 중앙27/88가 증가하지 않는다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4false와 global physical completion/error/budget remaining/currency null을 보존한다. HE photon05는 새 로컬 미게시 source/delivery 및 기존 dual ACK/metadata와 이번 Dropbox-only GET을 구별한다. WU7168의 scoped 수학 채택도 physical density/consumer/destruction을 제공하지 않는다. 이 공급자 자료나 타 owner 예산을 CR bath 또는 새 allowance로 옮기지 않는다.
