# C21F native 평가 후속 인계

평가 디렉터리: research/cr_c21f_native_assessment_20261019/. 아래 파일 경로는 이 평가 디렉터리를 기준으로 읽는다.

## 먼저 읽을 현재 authority

1. PUBLICATION_RECEIPT.json, BACKUP_RECEIPT.json과 DAG_C21F_ASSESSMENT.json.
2. README_KO.md, EVIDENCE_INTAKE_RECEIPT.json, INDEPENDENT_REVIEW_KO.md.
3. results/ASSESSMENT.json과 native_point_audit/POINT_AUDIT.json.
4. 원시 실행이 추가된 PR82의 최신 실제 head. 이 평가 시점 head는 c4a502e0c931a201edfa3c7046f7a91230c2278f였다.

실행 소스는 f8359232df8d0dd4fe91fcdabeb6701eb06089ba, native owner는 rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4다. 평가 시점의 PR81 문서 head 249d9b29b0adc5a8cf615a9999065aff26ff6900은 실행 소스 이후 문서만 변경한 1개 commit이며, 17개 executable files의 바이트는 같다.

PR82는 실행 commit에서 분기했으며 PR81 문서 head와의 merge base도 실행 commit이다. GitHub three-dot 비교에서 확인한 169개 추가 파일은 merge base→PR82 차이다. PR81 후속 문서 commit이 PR82에 포함되었다는 뜻으로 해석하지 않는다.

## 이미 완료된 작업

- C21F 최종 구현·복구·PR81 게시. 이전 3개 저장처의 6개 사본 재검증 근거를 재사용했다.
- PR82의 실제 native Rust compilation, Rust 검사 3개, Python 검사 56개, 두 native 행렬. 2 fixtures × 3 modes × 4 levels = 24 histories와 Radau reference 2개다.
- 이번 GitHub raw text 167개 취득 및 identity 확인. Manifest의 168개 payload 중 text payload 166개를 검증했고, binary 2개의 바이트는 이번에 취득하지 않았다.
- 소스 17개 byte identity, native JSONL 26개에 저장된 호출 27,140개의 내부 물리 수지, accepted steps 2,160개와 terminal ledger를 검토했다.
- 새 local defect 유도, signed cancellation과 reference-free 분석, 새 analyzer 검사 5개 PASS, v3 분석 exit 0, 독립 cross-review를 완료했다.

과학 ZIP의 NOT_PUBLISHED나 과거 PR81의 native NOT_RUN으로 상태를 되돌리지 말 것. 기존 패치·APPLY_C21F_FULL.py를 재적용하지 말 것. 역사적 중간 branch와 최종 복구본을 자동 merge하지 말 것.

## 과학 결론

FULLMID의 fixed-fixture 시간 2차 경향을 채택한다. Native-source hybrid의 높은 finite-grid p는 thermal 부호 상쇄와 active norm component 전환을 포함한다. d_n = w_HYB − w_FULL에는 약 1차 성분이 직접 보이며, n*d_n은 이번 n=8→64 정련에서 −7.8362e-5→−7.6773e-5 eV/H로 변했다. 명시한 smoothness·stability 전제 아래 local gas defect h²/2 DgM(Pg+M)+O(h³)가 이 기작을 설명한다. Hybrid는 comparator로 유지한다.

Native reference의 rtol 2e-10, atol 2e-13은 global state error 상한이 아니다. Common-IC FULLMID의 정규화 상태 차이 약 1e-12에서는 reference·roundoff·nonlinear error를 아직 분리하지 못했다. 부적합한 all-four hybrid fit의 crossing과 미실행 level 외삽을 실제 관측이나 예측으로 쓰지 않는다.

## 다음 bounded READY 작업

현재 GitHub·백업에 이후 결과가 있는지 먼저 확인한다. 새 결과가 없을 때:

1. 현재 NCP 자원, 다른 campaign, dirty files, watcher, checkpoints를 read-only로 확인한다. 이번 device-control은 월 quota 오류라 현재 inventory를 얻지 못했다. 역사적 자원 로그를 현재 값으로 쓰지 않는다.
2. 같은 source·fixture를 보존하여 더 엄격한 optical-depth Radau reference ladder를 실행한다. 기존 baseline reference는 재사용한다. physical gas/photon/log-survivor와 ledger 차이를 기록한다.
3. cancellation 이후 정련이 필요할 때 native_source FULLMID·MIDPHOTO_ENDMICRO의 새 n=128, 256만 추가한다. 기존 n=8/16/32/64 행렬과 56개 검사는 반복하지 않는다.
4. 소스·fixture·binary·raw SHA, solver status, 물리 수지, reference 민감도·관측 차수를 별도로 판정하고 새 데이터만 create-only로 게시·백업한다.

큰 기능 구현을 Codex/NCP에 새로 위임할 필요는 없다. 게시된 build_native.sh/run_ncp.sh와 frozen source를 사용하며 필요한 추가 resolution/reference invocation만 구체화한다. 전체 standalone Grackle driver parity, Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR는 독립 검증 전 HOLD다.

## 백업 기록의 층위

새 native archive C21F_NATIVE_NCP_20261018T1358Z_evidence.tar.gz의 Drive ID 1sQiP-1RHuCUaQnNkolLGSsmNfVA-0rjo와 Dropbox ID id:BSpOijBcT10AAAAAAD_NlA를 이번 metadata로 확인했다. Archive SHA256 05bd41fc998c2bda46e7606c07653cd5ab7ea36fa35556c1c480c5ca06384a90은 기존 PR82 readback 영수증의 기록이다. 이번에 archive 전체를 새로 받아 계산한 값과 구별한다.

이번 새 평가 artifact의 실제 이름·SHA·provider acknowledgement·readback 범위는 BACKUP_RECEIPT.json을 따른다. ZIP 생성 이후 확보한 업로드 확인과 readback 영수증은 같은 평가 branch의 canonical GitHub 문서에 추가한다. 실제 Files에서 확인한 ID와 경로만 사용하고, 사용자에게 원코드 다운로드를 요구하지 않는다.
