# Codex/NCP handoff v2: C21F는 게시·원격 백업 완료

$physmath-research-loop를 사용해 bass_cr C21F의 이미 구현된 코드를 native 환경에서 컴파일·실행해줘. 사용자에게 파일 다운로드, 첨부 또는 내장 패치 적용을 요구하지 마. 아래 GitHub commit을 직접 확보해.

## 권위 기준

- Repo: cosmosapjw-quantum/bass_cr
- Draft PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/81
- Branch: research/cr-c21f-recovered-release-20261018
- 실행 commit: f8359232df8d0dd4fe91fcdabeb6701eb06089ba
- 작업 경로: research/cr_c21e_event_native_20261018/
- Parent PR80: 82c71000fccf0e353534080efbbf4eff7f31ac4c
- Native owner: cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4

먼저 PR81의 실제 최신 상태, C21F_RELEASE.md, C21F_PUBLICATION_RECEIPT.json, DAG_C21F.json과 백업 경로에서 더 새로운 native 결과를 확인해. 이후 doc-only commit과 위 실행 commit을 구별해. 이미 native 결과가 있으면 source/fixture/raw SHA를 확인하고 재실행하지 마.

이전 research/cr-c21f-optical-depth-reference-20261018@7905762c63dcdd40f107ff33e3d19ca26c33bca1은 중간 게시본이다. 보존하되 자동 merge하지 마. 최종 복구본은 PR81이다. C21E의 기존 CODEX/RELEASE_NOTE/manifest와 ZIP 안의 미게시 상태 문구는 역사 기록이며, 현재 C21F_RELEASE와 이 v2 프롬프트가 게시 상태를 대체한다.

## 수정·검증 범위

공개 PreparedAbsorption.evaluate 호출 교정, 동일 연속방정식의 optical-depth Radau, Y=0 고정 He unknown 제거, 명시적인 population 대조 경로가 모두 반영되어 있다. 광자 clipping, epsilon floor, silent fallback은 없다. Underflow는 log-survivor와 함께 기록한다. 네 핵심 변경 파일과 study runner는 최종 복구 ZIP과 Git blob이 일치한다.

원본 ZIP/패치 복원 검산에 이어 게시 재시도에서 56/56 Python tests를 다시 통과했다. Native Rust와 Grackle 실행은 아직 NOT_RUN이며, 제조 nonphoto rates/3-energy fixed-GL2 결과를 native 정확도로 바꾸지 마. 과거 APPLY_C21F_FULL.py나 내장 패치를 이미 수정된 PR81 위에 다시 적용하지 마.

## 실행

기존 작업·watcher·dirty files·checkpoint를 보존하고, 새 isolated worktree를 사용해. 현재 NCP CPU/RAM/affinity/process를 직접 읽고 한 개 CPU를 할당해. 과거 CPU55 campaign 소유권 확인 전 해당 CPU를 사용하지 않는다.

기존 repo가 있으면 git fetch 후 위 commit으로 새 worktree를 만들고, 없으면 사용자 권한으로 GitHub를 clone해. 정확한 실행 commit을 checkout한 뒤 작업 경로에서 다음 기존 실행기를 사용해.

```bash
export PATH="$HOME/.cargo/bin:$PATH"
# CPU와 OUT은 실제 확인한 할당 CPU 및 아직 존재하지 않는 새 출력 경로다.
# 필요한 numpy/scipy/pytest는 기존 환경 또는 isolated venv/requirements.txt를 사용한다.
bash run_ncp.sh "$OUT" "$CPU" "$EXISTING_OWNER_REPO"
```

마지막 owner repo 인자는 선택이다. 생략하면 실행기가 정확한 owner를 별도로 fetch한다. 실행기는 git archive의 고정 소스를 빌드하며 기존 owner working files를 수정하지 않는다. 핵심 알고리즘은 이미 구현돼 있으므로 새 기능 개발을 시작하지 마. 실제 compiler/API 오류에 필요한 최소 수정은 최초 오류·diff·새 commit과 표적 테스트로 보존한다. 물리 변경은 작은 호환성 수정으로 숨기지 않는다.

원본 Rust tests, PreparedAbsorption delta-point 대조, 공통 explicit-IC native/Radau 행렬 및 native MD14 cell-source 행렬을 실행해. 오류가 나면 FAILURE.json과 부분 accepted_steps/native_points를 보존한다. 기존 run_ncp.sh는 오류에서 중단할 수 있으므로 새 출력 경로 없이 전체를 덮어써 재실행하지 마. 독립 사례가 남아 있으면 조건을 바꾸지 않고 별도 새 경로에서 실행할 수 있다.

Native photo=0,h=0 소유권, integrated events, Newton+energy 동시 gate, rollback, fit threshold/binding 구분, q=aE와 qref=21q를 유지해. 광학깊이와 population 변수의 같은 rtol/atol은 같은 물리 오차가 아니므로 observables와 보존수지를 따로 검사해. Explicit fixture는 checkpoint 시각 재해석이 아니다.

## 완료된 백업과 새 결과 반환

과학 아카이브 BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip: 394429 bytes, 102 payloads.
SHA256: 4bd711063c1d8d4e7724da693f8e021fd6742f5a1edfda3cbecd12f0956ed768
Drive: https://drive.google.com/file/d/1jeaxLIO24gJDyhLvTUvAMTBcX0HogL3O/view
Dropbox: /bass_cr/C21/BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip
Dropbox ID: id:BSpOijBcT10AAAAAAD_Mug
Library: /BASS_DERIVATION_DOSSIERS_20260912/bass_cr/BASS_CR_C21F_NATIVE_PREFLIGHT_TAU_20261018.zip
세 사본의 raw SHA/ZIP CRC/102개 payload 해시는 실제 재다운로드로 확인됐다. 이 기존 파일은 덮어쓰거나 중복 백업하지 마.

새 native 산출물만 별도 Draft PR/evidence commit 및 Dropbox·Drive create-only 백업으로 보존하고 원격 재다운로드 SHA/manifest를 검사해. 반환에는 source/binary/toolchain SHA, tests, CPU/RSS/time, SUMMARY/ANALYSIS/Radau, fixture/source export, accepted_steps/native_points, FAILURE와 RETURN_TO_CHATGPT를 포함해.

Full48, source-age/spectral/angular convergence, Case B, signed Bianchi와 full EoR는 해당 실제 검증 전까지 HOLD다. 준비·게시·백업 완료와 native 과학 검증을 구별해.
