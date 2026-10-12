## 연구 문제

이전 feedback step에는 실제 HI/HeI collision kernel을 공통 사건 열에 연결하는 구성과, 온도에 따라 움직이는 cutoff의 유한 EOS closure가 남아 있었다. 이 PR은 저장된 9600-node source를 직접 사용하여 그 두 이론 노드를 완결한다.

## 변경과 결과

- 실제 PHYS02C full-BED HI/HeI와 PHYS02B projector·선택 CCC·stopping을 양의 count/energy 사건에 결속했다. 실제 격자 간격 조건으로 같은 parent–target family의 sharing 확률이 capacity 적용 뒤에도 유지됨을 보였다.
- 고정 common inventory에서 signed count·energy 분할, 연속 cutoff의 유효 열용량·유일근·잔차 certificate, retained atoms의 전체 branch 열거 및 유한 가열·냉각 continuation을 구성했다.
- 공변 경계 current와 rest-mass subtraction을 연결하고, 고정 선형 reconstruction 또는 고정 atomic branch에서 event-to-temperature/density/composition gain과 inner/outer residual bound를 도출했다.
- KC1–KC7은 독립 심사 PROMOTE_SCOPED / PASS다. 9개 보완사항을 닫았고 72개 근거 파일을 동결했다. Metadata 사후 결속에서 72/72 identity와 scientific-body hash가 유지됐다.
- 36쪽 한국어 LaTeX/PDF, 두 reference 구현, 원 실행 결과, source identity와 다음 DAG를 제공한다.

## 실제 검증

- 실제 사건 열 17개 × 선형 invariant 4개: exact residual 68개 모두 0.
- 같은 ionization family의 실제 sharing 3 samples에서 donor·capacity denominator·extent/probability 비율 동일.
- 두 thermal reference 그룹 PASS: exact heating/cooling roots, equality, 복수 atomic branches, inherited zero-step identity.
- Wolfram scalar 17 zero groups / 21 scalar zeros와 inequality 5개 True; Wolfram 안의 xAct 6개 tensor residual 0. 합계 28 groups.
- 최종 PDF 두 번 컴파일 및 전체 36쪽 시각 검수 PASS, overflow·missing glyph 0.

## 적용 범위와 다음 구성

CONTRACT.json과 CLAIMS.json의 source/rate domain, positive base inventory, root bracket, effective-capacity bound, fixed reconstruction/branch 가정을 사용한다. 큰-step capacity 사례의 EOS 값은 구성한 inventory의 보존·양성 witness다. 실제 source/history와 관측량 오차 예산은 기존 응용 node에서 결속한다.

기존 DAG의 33 nodes / 60 edges를 보존하며 선택된 두 노드를 완료하고, coupled branch solver 및 geometry 후 kernel 재결속 두 노드를 추가했다. 현재 35 nodes / 65 edges다. 이전 과학 suite의 재실행이나 NCP job은 0이다.

## 재현과 배포

[시작 문서](research/cr_kernel_cutoff_20261013/README_KO.md), [PDF](research/cr_kernel_cutoff_20261013/latex/report.pdf), [독립 판정](research/cr_kernel_cutoff_20261013/review/DECISION.json), [DAG](research/cr_kernel_cutoff_20261013/NEXT_DAG.json), [HANDOFF](research/cr_kernel_cutoff_20261013/HANDOFF.json).

외부 논문 원문 cache 11개는 URL/query/digest index로 제공한다. Source ZIP에는 검토된 자체 근거 61개와 폰트·license를 포함한다. 실제 Dropbox/Drive acknowledgement는 후속 metadata commit의 DELIVERY/HANDOFF에 기록한다. 루트 AGENTS.md에는 이번 결과의 navigation을 추가했으며 기존 정책 원문을 보존했다.

