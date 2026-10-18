# Codex/NCP: 기존 C21E를 컴파일·실행한다. 새 알고리즘 구현을 위탁하지 않는다.

`$physmath-research-loop`를 사용한다. 사용자에게 파일 다운로드나 재업로드를 요구하지 말고 아래 저장소를 직접 읽는다.

- Repo cosmosapjw-quantum/bass_cr
- Branch research/cr-c21e-event-native-20261018
- 고정 구현 commit 22623f990f781668dd30dc1a5ea4ac59214cfd0a
- 작업 경로 research/cr_c21e_event_native_20261018
- Native owner cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4

원격 branch 최신 README/DAG/영수증을 읽되 구현 소스는 위 commit에서 isolated worktree로 가져온다. dirty 원본, C21 epoch bridge, PR78 기존 캠페인, watcher를 건드리지 않는다. C21C/C21D 완료 계산을 중복 실행하지 않는다.

## 실제로 남은 작업

Python integrated-event solver, persistent Rust zero-photo/h=0 bridge, 실제 MD14 source exporter, PreparedAbsorption delta-point 비교기, Radau reference, build_native.sh/run_ncp.sh까지 모두 작성됐다. 43/43 Python PASS와 제조 microphysics 12-case 결과는 샌드박스 증거다. Rust는 이 환경에 컴파일러가 없어 AUTHORED_UNCOMPILED. NCP에서 새 알고리즘을 작성하지 말고 컴파일, 발견된 최소 API/문법 수정, 기존 실행기의 실제 실행을 진행한다. 최초 오류·수정 SHA·표적 재검증을 보존한다.

## 실행 순서

현재 CPU affinity/load/RAM/기존 process를 실제 조사하고 한 개 CPU를 할당한다. CPU55는 별도 캠페인 자리였으므로 현재 소유권 확인 전 사용하지 않는다. PATH에 /root/.cargo/bin을 추가한다. 기존 Python에 numpy/scipy/pytest가 없으면 isolated worktree의 venv에 requirements.txt를 설치한다.

작업 경로에서 실행:

```bash
bash run_ncp.sh /root/C21E_NATIVE_<새시각> "$CPU" /기존/rei_bianchi/git/경로
```

마지막 경로는 선택이다. 생략하면 실행기가 정확한 owner SHA를 별도 bare 저장소로 fetch한다. 기존 working files가 아니라 `git archive`의 고정 source를 사용한다. 실행기는 native compile+3Rust tests,43portable tests,7PreparedAbsorption delta points,세 결합 clock의 공통IC native/Radau 행렬,실제 native MD14 cell source 행렬,결과 분석을 실행한다. source48이나 GL8로 확대하기 전에 기본 bounded 비교부터 완료한다.

각 native call/time budget과 외부300초 실행 제한은 자원 한도다. timeout, 원본 RHS domain error, 음의 Radau 내부단계, 큰 timestep midpoint positivity 실패를 clip하거나 허용오차를 완화해 PASS로 만들지 않는다. 실패 시 해당 lane의 FAILURE.json/부분 accepted_steps/native_points를 보존하고 끝낸다. 다른 독립 완료 항목은 결과로 반환한다.

## 물리 계약

원본 nonphoto RHS는 photo=0,h=0. 광자 소멸과 photoheat는 외부 event solver, CI/RR/DR/cooling/Case-A escape/CMB는 원본 RHS 소유다. 적분된 사건수로 잔차를 구성하므로 Gamma=L/(dt*Aend)를 만들지 않는다. Newton+energy 동시 gate, rollback, structural-zero helium, fit cutoff와 binding 구분, q=aE/qref=21q를 유지한다. geometry work는 한 번만 적용한다.

첫 행렬은 explicit gas/제조3energy/opacity.001이고, 둘째는 explicit gas/실제MD14 native12cell/opacity1이다. 이 둘을 동일 production 캠페인으로 합치지 않는다. explicit point IC는 checkpoint 재해석이 아니다. GL2 birth times가 고정되어 있으므로 time refinement를 age convergence로 보고하지 않는다. delta PreparedAbsorption parity는 full driver equivalence가 아니다.

## 반환/보존

RETURN_TO_CHATGPT.json, FAILURE.json(있을 경우), SUMMARY/ANALYSIS/Radau, fixture/source export, native point 및 accepted step raw, source/binary/toolchain SHA를 보존한다. 결과는 별도 Draft PR 또는 additive evidence commit으로 게시한다. 기존 bass_cr Google Drive/Dropbox 연구 경로에 create-only 저장 후 원격 재다운로드 SHA와 manifest를 검사한다. 사용자에게 추가 구현 지시나 파일 전달을 요청하지 않는다.

Native science는 실제 실행된 범위만 PASS. full48, source-age/spectral/angular convergence, Case-B photon 재수송, signed Bianchi, full EoR는 이번 단위로 승격하지 않는다.
