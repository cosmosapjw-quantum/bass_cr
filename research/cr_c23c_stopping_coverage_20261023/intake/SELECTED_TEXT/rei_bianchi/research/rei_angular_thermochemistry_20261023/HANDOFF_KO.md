# 다음 대화 스레드 복사용 handoff

아래 내용을 다음 대화에 복사한다. 최종 정확한 commit과 압축파일 identity는 같은 단위의 FINAL_DELIVERY.json을 함께 전달한다. 파일 자체가 포함된 commit의 자기 해시를 본문에 미리 넣지 않는다.

---

physmath-research-loop intrinsic 1.0.0 / approved v0.2로 rei_bianchi 연구를 이어가줘. SciSpace·Exa·Wolfram을 필요한 원전 탐색·독립 검산에 사용하고, sandbox에서 실행 가능한 물리적 축약과 실제 코딩을 계속해줘. 매 과학 단계의 결과·DAG·완료 상태와 실제 게시/백업 receipt를 남겨줘.

현재 완료 단위는 research/rei_angular_thermochemistry_20261023, ANGTHERM01이다. 저장소 cosmosapjw-quantum/rei_bianchi, PR221, branch research/rei-coupled-isotope-contract-20261022. 이전 기반은 73c5e00cac26b4efc782446975bd6b6762555997, 준비 게시 commit은 00303ab27c33a7afa0cec61679af78ef72e3f4aa다. 최종 과학 commit·archive SHA·백업 ID는 FINAL_DELIVERY.json을 실제로 읽고 최신 branch head를 확인해라. PR222의 b4b5d289aaad9ef167f683f19418b0ff87ed8425는 다른 유효한 분기다. 둘을 덮어쓰거나 무조건 merge하지 말아라.

먼저 REPORT_KO.md, SCIENTIFIC_DECISION.md, INDEPENDENT_REVIEW.md, DAG.json, REPRODUCE.md를 읽고 변경된 의존성만 확인해라. 이미 끝난 전체 조사·donor IVP·10개 계산을 새 작업으로 반복하지 말아라. 이전 로컬 경로가 없어도 exact commit/archive로 해당 단위를 복구하면 된다. Git은 reviewable text, 완전한 동반 ZIP은 원본 NPZ/PNG를 포함한 모든 실행 입력과 결과를 보존한다. Git 텍스트만으로 34-file prepare를 실행하지 말고 archive의 입력도 복구해라. Git 저장소에 연결된 프로젝트이므로 별도 Library 복제는 필요 없다.

이번 조사에서는 REI 263 branches/260 unique heads/207 open PRs/14 closed PRs를 목록 끝까지 확인했다. 인접 13 repos의 1,374 heads, 최근 PR 236건, text85+binary2 sources를 확인했다. 알려진 Drive176/Dropbox93 목록, 관련 대화·최근 보관 자료를 조사했다. 비공개 대화 전체나 모든 backup archive 내용까지 읽었다는 주장은 하지 않는다. 전체 원본 조사 metadata는 준비 checkpoint archive에 있다.

과학 결과는 PASS_SCOPED_ANGULAR_THERMOCHEMISTRY_ON_PRESCRIBED_BACKGROUNDS다. C13/C15/C16의 exact directional photon map와 signed shear work를 C22A의 21-state photoionization/Case-A RR/common-temperature closure에 결합했다. C21O의 실제 저장 grid044/grid022 배경에서 z20→2를 계산했다. 동일 electronic rates+initial fractions와 reflection/azimuth symmetry 아래 isotope21→fraction9, photon192→group24, 전체221→41의 exact finite quotient다. logG=logG0−tau와 directly scaled photo coefficients를 RHS/J 양쪽에 사용하며 floor/clipping/renormalization은 없다.

주요 donor pins:
- C13 d7d0e3ad2d6d7cccdfd70df3a0f310df93ec553d
- C15 435c94308c0cd7b1ba8ff6518246da061f2fc2fa
- C16 af67c5314669492b07cb574170c09f70994974e4
- BASS_CR C22/C21O recovery 15fd250ab91574bd4f3348e91d739a15a6ed6005; selected source ba39fc75521aa18705ec832d789e50dd5c6565bc
- grid044 SHA256 ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b
- grid022 SHA256 5d0ef6ee7adadf3a3acf148a930136cf406fab2b3eb484682e2a93de7119b7c0

10개 궤적이 완료됐다. 기본/221-state oracle population max8.1673e−11, T relative1.8696e−9; 최대 정규화 energy residual2.5395e−11. 온도6.12246..13803.0397K. HeI source row는 HeI b로 확인돼 이전 도메인 의문은 닫혔다. Frozen source hashes34개가 일치한다. 원래 중단 실패·partial states를 보존했고 persisted interval replay0; 미저장 node2개만 재계산했다. Oracle는 단 한 번 적분하고 summary만 고쳤다. 초기n/T의 structuralzero와 directoracle의tinyroundoff를 구분한다. 서로 다른rtol/nativeatolnorm 때문에 관측 CPU비를 equal-error speedup으로 쓰지 말아라.

가장 중요한 새 결과: 같은 grid044 H/n와 tight tolerances에서 b=b'=0인 mean-drift counterfactual과 directional run을 비교했다. M4 LiI/LiII fraction maxdifference0.04899986856, M16vsmean0.049121828. 10eV photon의 LiI5.392eV threshold crossing이 M4eta0.488914..0.726724, M16eta0.456828..0.727992에 퍼지며 meaneta0.617668719와 다르다. T/electron bulk difference는 매우 작다. YLi=5.0001e−10이므로 Li fraction0.049의 electron scale은2.45e−11/Href다. M4/M8 Li difference9.97743e−5, M8/M16 4.64160e−5가 남아 있으므로 Li angular-continuum tolerance2e−7를 달성했다고 말하지 말아라.

다음 최소 연구 목표는 이 문턱에 민감한 Li 각도 오차다. 출발식 mu_c²=[(chi/E0)² exp(2eta)−exp(2b)]/[exp(−4b)−exp(2b)], b=0은 별도 공통 문턱으로 처리한다. 기존 M4/8/16와 mean 결과를 재사용하고 문턱을 반영한 각도 적분·오차 설계를 먼저 유도해라. 새 quadrature/remap을 쓰면 fixed-q photon measure, positivity와 count/energy/work 보존을 어떻게 유지하는지 계약에 명시한다. 근거 없이 수렴 차수를 선언하거나 큰 sweep을 시작하지 말고 유한 후속 계산으로 후보를 판별한다. 이번 300CPU/420wall 예산은 완료된 단위의 기록이며 새 연구 단위의 무한 추가 실행 예산이 아니다.

전체 목표의 열린 의존성도 유지해라: 이 긴 구간 trace의 새 UV/gas/escape source에 대한 Einstein feedback은 아직 없고, Case-A escape는 bolometric ledger다. 실제 emissivity와 spectrum, Compton/secondary/line 등 선택한 thermal processes, isotope-specific rates, nonzero n/T beta energy partition·stopping·daughter branching, 일반 Bianchi 및 관측 예측은 별도 입력과 검증이 필요하다. 기존 C15의 짧은 구간 feedback과 C22B/REC125 Compton 후보는 재사용 가능하므로 처음부터 재구현하지 말아라. 방향 수송 자체가 새 발명이라는 주장도 금지한다.

역할은 Astra의 이론·계약·과학 판정, lower-tier의 구현·bounded 실행·패키징, 구현을 쓰지 않은 Astra의 독립 검토로 유지해라. 현재 checkout을 기본 사용하고 승인 없이 새 clone/worktree를 만들지 말아라. 이미 승인된 안전한 계산·추가형 PR 게시·기존 Drive/Dropbox backup은 불필요하게 재승인받지 말고 실행하되, 파괴적 변경·merge·force push는 하지 말아라. 과학적 미해결과 저장 metadata를 구분하고 닫힌 검토를 새 절차로 무한 반복하지 말아라.

---
