# 새 ChatGPT 스레드 handoff v2: bass_cr C21F 게시 완료

$physmath-research-loop를 사용해 bass_cr 연구를 이어서 진행해줘. 연구 전에 실제 GitHub와 아래 백업에서 새로운 NCP native 결과부터 확인해. 이미 완료된 C21F 연구·복구·게시를 반복하지 마.

## 최신 권위 기준

Repo: cosmosapjw-quantum/bass_cr
Draft PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/81
Branch: research/cr-c21f-recovered-release-20261018
실행 commit: f8359232df8d0dd4fe91fcdabeb6701eb06089ba
경로: research/cr_c21e_event_native_20261018/
Native owner: cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4

현재 PR head는 연결 도구로 새로 읽어. 이후 metadata commit과 위 execution commit을 구별한다. C21F_RELEASE.md, C21F_PUBLICATION_RECEIPT.json, DAG_C21F.json, CODEX_HANDOFF_KO.md와 evidence/C21F/RESULTS_SUMMARY.json을 먼저 읽어.

## 게시 상태 정정

이전 세션의 'C21F 게시/백업이 전혀 없다'는 설명은 너무 넓었다. 실제 중간 branch research/cr-c21f-optical-depth-reference-20261018@7905762c63dcdd40f107ff33e3d19ca26c33bca1 및 R5/C5-C6 백업이 존재했다. 재시도에서 이를 확인·보존하고, 최종 56-test 복구본을 별도 PR81로 게시했다. 과거 중간본과 최종본을 자동 병합하지 마.

최종 과학 ZIP의 기존 publication=NOT_RUN 문구는 제작 당시 역사 기록이다. 이를 현 상태로 다시 인용하지 마. 새 publication receipt와 v2 handoff가 게시 상태를 대체하며 원본 science/실패 기록은 불변이다.

## 완료된 백업

파일: BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip
394429 bytes, 102 payloads
SHA256: 4bd711063c1d8d4e7724da693f8e021fd6742f5a1edfda3cbecd12f0956ed768
Google Drive: https://drive.google.com/file/d/1jeaxLIO24gJDyhLvTUvAMTBcX0HogL3O/view
Dropbox: /bass_cr/C21/BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip
Dropbox ID: id:BSpOijBcT10AAAAAAD_Mug
ChatGPT Library: /BASS_DERIVATION_DOSSIERS_20260912/bass_cr/BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip

세 저장본 모두 실제 재다운로드해서 전체 SHA, ZIP CRC, 102/102 파일 해시와 크기를 확인했다. 사용자에게 ZIP 다운로드나 첨부를 요구하지 말고 코드가 필요하면 GitHub를 직접 읽어. 프로그램 복원이 필요할 때만 현재 보이는 파일 id로 materialize해. file id·sandbox path를 만들어내지 않는다.

## 과학·구현 상태

C21E native bridge는 외부에서 pub(crate) 메서드를 호출하던 문제를 public PreparedAbsorption.evaluate로 바꿨다. 광자 population Radau가 강한 흡수에서 내부 음수로 중단되던 문제에는 동일 연속방정식의 tau'=lambda/H, N=N_birth exp(-tau) 기준해를 구현했다. Y=0의 고정 He 분율 두 개는 numerical unknown에서 제거했다.

기존 population 경로는 명시적 선택으로 남아 있다. Photon clipping/epsilon floor/silent fallback은 없고 log-survivor/underflow를 기록한다. Gas 내부단계의 strict domain은 유지한다. 동일 숫자 rtol/atol의 두 좌표계가 동일 physical error norm인 것은 아니다.

복구 소스 및 깨끗한 C21E에 guarded patch 적용 후 각각 56/56 tests 통과. 게시 재시도에서도 56/56 PASS, exit0,11.85s. 44 inherited +12 new이며 두 최초 행동검사만 실제 red→green 증거가 있다. 3개 좌표 비교와 제조 nonphoto/3-energy source end-to-end 두 실행은 이전 원시 증거를 그대로 보존했다.

Native Rust compiler, 실제 Grackle, NCP 실행은 아직 NOT_RUN. 기존 제조 결과를 native 정확도 또는 full EoR PASS로 승격하지 마. 네 핵심 변경 파일과 study runner의 Git blob은 최종 복구본과 일치한다.

## 다음 READY 단위와 운영

C21F 알고리즘은 이미 구현·게시됐다. 다음은 현재 NCP 상태를 확인하고 기존 build_native.sh/run_ncp.sh를 컴파일·실행하는 단계다. 이전 내장 APPLY_C21F 패치를 PR81 위에 다시 적용하지 마. 큰 기능 개발을 NCP/Codex에 다시 떠넘기지 않는다.

NCP를 사용할 때 CPU/RAM/affinity와 이전 CPU55의 별도 campaign 소유권을 실제로 확인하고 다른 연구·watcher·dirty files·checkpoint를 보존한다. 새 실행 결과가 오면 정확한 source/fixture/raw SHA와 물리·수치 gate를 판정한다.

새 연구 또는 재개 범위가 명시되면 그 범위만 수행하고, 각 완료 단계의 실제 산출물/검증/게시/백업/DAG를 표시해. 수학 오류, 수치 오류, 구현 오류, 환경·권한 blocker를 구분한다. 기존 과학 ZIP은 불변으로 두고 새 결과만 create-only 백업한다. Source48, source-age/spectral/angular, Case B, Bianchi 및 full EoR는 독립 검증 전까지 HOLD다.
