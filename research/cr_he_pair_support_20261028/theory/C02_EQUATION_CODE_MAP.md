# C2 equation-data-code mapping

| Mathematical/physical obligation | Data/implementation path | Observable check |
|---|---|---|
| fixed electron-leg coefficients | byte-pinned NPZ -> unchanged eu.load_pinned_source -> AtomBundle | NPZ SHA, shape3201, binary64 exact lift, content ID |
| x>=0,Bx<=a | solve_envelope, four-bin symmetric network | independent returned primal degree inequalities |
| y>=0,y_i+y_j>=1 | residual cut dual; verify_certificate | exact cover inequalities |
| rho=1·x=a·y=F/2 | certificate rational fields | zero exact primal/dual gap; independent enumerated dual optimum |
| C∈[0,rho],C<=d<=A_tot/2 | construct_witness -> requested totals | domain-specific ValueError controls |
| full-rectangle sparse realization | atom queues, allowed edge pairs, residual diagonal/singles | every original atom marginal; forbidden edge rejection |
| diagonal consumes2legs | eu.Event(a,a,weight) | marginal counts a twice; exact d and residual legs |
| source/state/frame/history | graph_binding includes complete unchanged eu.binding and content ID | source/state/window/provenance mutation rejection |
| density W=(v²-u²)/2 | events retain coefficient; unchanged consumer integrates once | returnedC=W*Ccoeff,d=W*dcoeff and homogeneity |
| same-state neutral inventory | unchanged eu.consume_event_union Eq.(8) gate | explicit fixture refusal plus actual-source admission |
| once-only union/native | claims_by_partition then consume_event_union once | ion/charge/chemical/native correction, replay and nb guards |
| independent optimum | reference.py enumeration of doubled cover coordinates |64×81integer cases and64 raw-source cases |

원래 event_union.py와 RR/source science는 수정하지 않는다. 새 Python은 file SHA를 확인한 바로 그 predecessor bytes를 import하며 source fit이나 quadrature module을 import하지 않는다. Full witness sidecars는 정확한 Event fields로 직렬화하고 source/graph/certificate와 묶는다. 큰 sidecar는 archive-only로 분류하며 Git에는 code·compact result·actual file hashes를 게시한다.

오류 분류는 graph/model 가정, exact numerical/data representation, implementation, current host transport, provider metadata, missing physical input을 구별한다. 현재 확인된 R6-F1은 consumer 적용 가정의 명시 교정이고, R01의 shell argument size 문제는 metadata transport 문제였다. 둘을 source physics 실패나 예산0으로 바꾸지 않는다.
