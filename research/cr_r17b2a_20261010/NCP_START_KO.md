# NCP local Codex: bass_cr R17B2B

담당은 cosmosapjw-quantum/bass_cr 하나다. 현재 research/cr-r17b2a-physical-response-20261010을 읽고 실제 HEAD를 확인한다. core science18948fcbdb51f8a26bb2f0aa6b4ffcff05e27be0, parent eb692c19c7cef3e3721f1e044ca3d41151d9309d. 다른 repo는 read-only donor이며 그들의 과학 작업/코드를 수정하지 않는다.

## 실제 입력

BASS_CR_R17B2A_20261010_v1.zip,143722bytes,SHA256 e46cb3d29c67abbe776324a19f22add884fd6bcedb0e58947cbf5b7d54d5cc89.
Drive id1LbC2uPEXzHLNZjwidCKC9IsOi9NyDgjj, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ.
Dropbox id:BSpOijBcT10AAAAAAD3uMw, /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_R17B2A_20261010_v1.zip.
두 provider R1 ACK/name/size 확인. ZIP은 Git에 포함됐다고 가정하지 말고 NCP의 기존 연결로 회수한다. 실제 bytes와 CRC/55payload MANIFEST를 검증한다. 접근이 없으면 BLOCKED_INPUT_AUTH이며 비밀을 채팅에 요구하지 않는다.

ZIP의 REPORT_KO.md,NCP_HANDOFF_KO.md,SOURCE_BINDING.json,CLAIM_GATE.json,VERIFICATION.json과 src4개를 전체 읽는다. python -B reproduce.py --verify-only를 우선 사용한다. 변경된 환경의 검사가 필요할 때만 새 빈디렉터리로 한 번 재현하고 기존 R16B/R17A/B1 donor suite를 반복하지 않는다.

## 새 연구의 목표

R17B2A가 완료한 것은 arbitrary-birth nominal eta=0 full-coupled response 및 물리수지와 조건부 birth C2 정리다. source interval,전체eta,K''''/J3 상계는 없다. R17B2B는 같은 FT03 firstmacro [0,1.25e9]proper s,H=1e-14,nH0=1e-4,fHe=.083,Eb13.7eV,초기gas(.9,.3,.6),초기photon.05/H,원6birth와 sourceweight family를 유지한다. Grackle 모델을 섞지 않는다.

mu_eta=(1-eta)mu_Q+eta mu_S,0<=eta<=1의 continuum photon population과 가스 common tube를 구성한다. 기존7cohort adjoint를 arbitrary-birth 보간하지 말고 이미 구현한 causal probe/old-photon memory tangent와 adjoint를 interval backend에 연결한다. nominalK만으로 int K d(muS-muQ)를 계산하면 finite-source remainder가 반드시 필요하며, 없으면 DIAGNOSTIC_ONLY다.

known same-energy additive birth에서 K,K',K'' jump=0의 조건부 정리를 활용하되 필요한 smooth energy trace/thermal regime/source homotopy 전제를 실제 닫는다. 다른 sourceenergy/cutoff/thermalbranch에는 자동0을 적용하지 않는다. actual J3와 regular fourth derivative 및 anchor를 검증하고 R17B1 source_peano.py에 LOCAL/GLOBAL derivative scale과 factorial을 맞춰 전달한다. 계수 예산99.7754%의 첫sourcecell을 우선하되 뒤두구간은 별도의 검증된 fallback으로 감싼다. 이것은 실제error분담률이 아니다.

검증: wrongclock/source/weight/unknownjump/nominal-only-homotopy 거절, old-photonmemory 누락시 수지 실패, sameenergy C2 cancellation과 differentenergy 반례, 전방/후방 독립계산, photon/heat-delay identities. 이 18개 기존시험은 변경되는 부분의 regression에만 사용하고 새기능의 실제 assertion RED→GREEN을 기록한다. Python NumPy complex-step point나 DOP853 dense interpolation은 interval 증거로 사용하지 않는다.

성공이면 기존 R17A보다 엄격한 source interval을 도출하고 불변 R16B 시간오차와 한 번만 결합한다. 좁아지지 않으면 NO_CERTIFIED_SOURCE_SHARPENING으로 종료하고 부모를 유지한다. signed physicalerror를 억지로 양수로 만들지 않는다.

새 bass_cr-only branch, create-only결과, 실제 cgroup/CPU/RAM/peakRSS,coordinator와16–24GiB예비,thread1,boundedpilot,no-fastmath를 유지한다. 새로운 물리실행·interval·실패수를 정확히 기록한다. Nonforcepush 및 기존 Drive/Dropbox create-only백업은 실제 ACK로만 R1이라 한다. CR_OFF_FASTEST,G02UNRESOLVED,b_gridNO_GO,precisionPARKED,physical/productionHOLD와 Grackle/G02의 별도blocker를 유지한다.

반환: BASS_CR_NCP_R17B2B_RETURN_KO.md,RETURN.json,SOURCE_BINDING.json,VERIFICATION.json,CLAIM_GATE.json,RECOVERY_INVENTORY.json,원코드·입력·로그·불변ZIP과 detached receipt. 계획만 쓰지 말고 실제 가능한 검증을 수행하되, 이미 완성된 nominal response를 다시 구현하는 작업으로 대체하지 않는다.
