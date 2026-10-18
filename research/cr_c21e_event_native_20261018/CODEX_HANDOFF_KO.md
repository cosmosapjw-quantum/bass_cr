# Codex/NCP: 기존 C21E 컴파일·제한 실행

`$physmath-research-loop`를 사용한다. 사용자에게 다운로드·업로드를 요구하지 않고 GitHub를 직접 읽는다.

고정 구현: cosmosapjw-quantum/bass_cr@**1ee8cb5a3377381de35b6b9a0e3b8dc1cfb12f41**. Branch research/cr-c21e-event-native-20261018, PR80. 경로 research/cr_c21e_event_native_20261018. 최신 RELEASE_NOTE.md, DAG.json, DELIVERY_RECEIPT.json을 읽되 소스는 위 고정 commit의 isolated worktree를 사용한다. 이전22623f99 대신 native 입력범위 교정이 포함된1ee8cb5a를 사용한다.

Native owner: cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4. 기존 dirty 작업·C21 epoch bridge·PR78 캠페인·watcher·checkpoint를 훼손하지 않는다. 완료한 C21C/C21D 연구를 중복 수행하지 않는다.

## 이미 구현된 것과 남은 일

Integrated-event nonlinear gas solver, persistent Rust nonphoto point bridge, native MD14 density/source exporter, PreparedAbsorption delta-point comparator, chronological source-age transport, continuous Radau, analysis, build_native.sh와 run_ncp.sh가 모두 작성됐다. Python44/44 및 제조 source-on12case가 검증됐으며 최종 Drive/Dropbox 복원도44/44다. Rust는 샌드박스에 컴파일러가 없어 미컴파일 상태다. NCP에서 알고리즘을 새로 구현하지 말고 컴파일·필요한 최소 API/문법 수정·실제 실행을 진행한다. 최초 실패와 수정SHA·표적 검산을 보존하고 과학적 허용오차는 완화하지 않는다.

## 직접 실행

현재 NCP process/CPU affinity/load/RAM을 확인해 한CPU를 할당한다. CPU55는 별도 연구에 사용됐으므로 현재 소유권 확인 전 사용하지 않는다. /root/.cargo/bin을 PATH에 추가한다. 기존 Python 모듈이 없으면 worktree 전용 venv에서 requirements.txt를 설치한다.

작업 경로에서 다음 명령을 직접 실행한다. NEW_OUTPUT은 실제 새 타임스탬프로 생성하고 CPU는 조사 후 정한다.

```bash
bash run_ncp.sh NEW_OUTPUT "$CPU" /existing/rei_bianchi/git/repository
```

마지막 인자는 선택이며 생략하면 원본SHA를 자동fetch한다. 실행기는 dirty 파일이 아닌 git archive의 원본commit을 내보내고 rlib/bridge를 빌드한다. 이어서3Rust tests,44portable tests,7native delta-point controls,세 clock의 공통IC native/Radau 행렬,실제MD14 native12cell-source 행렬,오차 분석을 수행한다. build/native-call/matrix 시간·호출 상한을 지킨다. 기존 출력경로는 사용하지 않는다.

## 유지할 물리 계약

원본 igm_point_rhs는 photo=0,h=0. 광자 손실·광전리·photoheat는 integrated event solver, CI/RR/DR/cooling/escape/CMB는 원본native RHS 소유다. 적분된 사건수로 잔차를 구성하며 Gamma=L/(dt*Aend) 또는 exposureGamma의 무수정 대입을 사용하지 않는다. Newton+energy 동시 gate, rollback, structural-zero helium, fit/binding 문턱의 차이, q=aE/qref=21q, 단한번의 geometry work를 유지한다.

첫 행렬은 explicit gas/제조3energy/opacity.001, 둘째는 explicit gas/원본MD14 cell source/opacity1이다. checkpoint를 다른 시각으로 재해석하지 않는다. 두 행렬을 동일 production 캠페인으로 합치지 않는다. GL2 source birth grid가 고정되어 있어 시간 정제를 age 수렴으로 표시하지 않는다. PreparedAbsorption delta parity는 전체 driver 동등성이 아니다.

## 실패와 반환

Native compiler/API failure는 원시 로그를 보존하고 최소 수정 후 해당검사를 재실행한다. midpoint 큰step의 positivity 실패, 원본RHS domain, strict Radau 내부 음수, timeout은 clip/tolerance완화로 숨기지 않는다. fixed-grid lane을 HOLD로 남기고 나머지 독립 완료 결과를 반환한다.

RETURN_TO_CHATGPT.json, FAILURE.json, SUMMARY/ANALYSIS/Radau, fixture/source export, native point와 accepted-step raw, source/binary/toolchain SHA를 저장한다. 새 실제native 결과만 additive Draft PR/evidence commit 및 기존 bass_cr Dropbox·Google Drive에 create-only 백업하고 full-byte readback+manifest를 검증한다. 사용자에게 추가 구현 프롬프트나 수동파일 준비를 요청하지 않는다.

Native science는 실제 통과한 범위만 PASS. full48, source-age/spectral/angular 수렴, CaseB, signed Bianchi, fullEoR는 이번 실행으로 자동 승격하지 않는다.
