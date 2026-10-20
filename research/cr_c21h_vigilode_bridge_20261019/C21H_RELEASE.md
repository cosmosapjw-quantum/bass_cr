# C21H release: 원본 RHS를 재사용하는 두 Rust stiff 적분 경로

> 현재 게시 중단: 새 명시적 push 지시 후의 create_tree594개 재시도도 user rejected MCP tool call을 반환했고 tree SHA가 없었다. commit·branch·PR 생성은 실행하지 않았다. 최신 상태는 `PUBLICATION_RECEIPT.json`을 따른다. 원래 8개 runtime source는 변경하지 않았다. 현재 환경의 locked 실제 재컴파일과 복원 근거는 새 영수증에 보존하며 native chemistry/NCP는 NOT_RUN이다.

> 역사 기록 — 재지시 이전의 2026-10-20 게시 요청: 새 create_tree도 `user rejected MCP tool call`을 반환했다. 원격 tree SHA·commit·branch·PR은 확인되지 않았고 현재 게시 상태는 `PUBLICATION_RECEIPT.json`을 따른다. 원 과학 source·검증은 유지되며 최신 실행/복구 증거는 별도 create-only 백업에 보존한다.
## 현재 판정

> 역사 기록 — 2026-10-20 이전 이관: 다른 대화로 이관하기 위해 C21H 게시 요청이 중단됐다. 마지막 create_tree 응답은 aborted by user였고 SHA가 없으며, 실제 branch/commit/PR 생성은 확인되지 않았다. 프로그램과 검증 raw는 세 저장처에 보존된 원 과학 ZIP에서 바이트 동일하게 복원했다. 현재 영수증을 읽고 게시를 재개한다. Native chemistry/NCP는 NOT_RUN이다.

**C21H 구현·지역 컴파일·제조 검증은 완료했다. 실제 native chemistry/NCP 실행은 NOT_RUN이다.** 게시 상태는 `PUBLICATION_RECEIPT.json`, 새 백업 상태는 `BACKUP_RECEIPT.json`, 단계별 연구·실행 의무는 `DAG_C21H.json`이 담당한다. 이 문서의 최초 content snapshot 이후 영수증만 추가될 수 있으며 실행 내용은 `EXECUTION_MANIFEST.json`으로 구별한다.

실행 manifest SHA256:

```text
7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb
```

Parent는 bass_cr PR84의 `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5`다. C21G 실행 내용 `e742d44f605c51c06615451774ba90af8f41f622`와 원본 `reference_tau.py`의 SHA256 `714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0`를 재사용한다. C21F 복구·게시·기존 native matrix를 다시 수행하지 않았다.

## 새로 구현한 것

`optical_adapter.py`는 원본 `reference_tau.py`를 private module로 읽고 그 module의 `solve_ivp` binding만 교체한다. 같은 광학깊이 RHS, birth·event 구간, exact Y=0 축소와 15개 누적 장부를 유지한다. 고정 양의 대각 scaling은 좌표별 절대 tolerance를 Rust의 scalar tolerance로 옮긴다. Tau 열의 Jacobian은 해석식, passive 열은 정확히 0, gas 열과 시간 편미분은 원본 RHS의 물리적으로 허용되는 표현 가능 노드를 사용한다.

`rust_bridge/`는 VigilODE `8a8bd409b1d96c7b7421f496d229e119fd3d284e`의 Rodas5P fast와 Diffsol `0.17.1` BDF/Faer를 연결한다. 실제 원시 JSONL 요청·응답, accepted state 전체, step·Jacobian·선형 작업 counter와 오류를 보존한다. Counter의 backend별 의미도 구별한다.

실제 검증에서 Diffsol의 convenience 초기 step 추정이 좁은 cell 밖을 조회하는 문제와, 음수 epoch의 마지막 1 ULP를 남기는 stop 처리 문제를 발견했다. 공개 초기 상태 API와 typed stop-time 처리로 수정했다. 마지막 ULP에서는 남은 길이의 실제 BDF step을 수행하고 공개 API의 1차 history restart를 기록한다. 실패 원시 자료와 수정 전 source identity는 유지했다.

`run_pilot.py`는 입력·source·binary·build 영수증을 전후 확인하며 새 output 디렉터리만 허용한다. 1 CPU, 300초 계산 deadline, 원 RHS 최대 200000회, 원래 native provider의 실제 호출 timeout을 사용한다. Base와 followup의 입력·method·fixture·binary 및 raw identity를 연결한다. 새 기능의 대규모 구현을 NCP로 넘기지 않는다.

## 실제 수행한 검증

| 계층 | 결과 | 증거 범위 |
|---|---|---|
| Python 광학 callback | 13개 고유 계약의 scoped PASS | 기존 12개와 영향받은 재검사, 새 짧은 cell 회귀 1개; 한 번의 전수 13개 실행으로 표시하지 않음 |
| Python pilot | 13개 고유 계약의 scoped PASS | provenance·create-only·예산·입력 실패; solver/native process 미실행 |
| Rust unit | 최종 source에서 10/10 PASS | 실제 Rust 1.94.1 컴파일 |
| 실제 Rust binary | 최종 16/16 PASS | 두 backend × 8개 제조 IVP·오류 계약 |
| Build receipt | 3/3 PASS | 명시적인 tool stub; 실제 컴파일과 별도 |
| 원본 RHS 연결 | 최종 4/4 실행 PASS | 두 방법의 base + 각각의 fd_half, 총 12 event segment |
| 최종 identity | runtime 8개·새 raw 122개 PASS | 실행 manifest, build source 3개, 4개 job receipt와 대조 |
| C21H native chemistry/NCP | NOT_RUN | NCP live 자원·실제 chemistry 미확인; 과거 remote quota를 현재 가용성으로 대체하지 않음 |

최종 로컬 binary SHA256은 `a11d3ab01474f9d1a88df51c9cd6d7910ca59b3443814fd39699ed959cb64048`이다. 배포 Cargo.toml/lock은 Git pin을 유지한다. 실제 제한된 로컬 빌드에는 Git blob·SHA가 검증된 같은 source의 path override를 사용했다. 두 lock의 차이는 3개 VigilODE package의 source 위치 필드뿐이며 registry version/checksum은 일치한다. 이 구분과 build mode를 영수증에 기록했다.

## 이번 제조 fixture에서 관측한 값

미시물리는 `MANUFACTURED_CONSERVATIVE_MICRO_NOT_GRACKLE`다. Y=0, cohort 9개, 전체 상태 28개 중 실제 적분 상태 26개, 구간 폭 `1e-7`을 사용했다.

| Base 방법 | accepted steps | 실제 원 RHS 호출 | 독립 photon number 수지 / H | 독립 energy 수지 / eV H⁻¹ |
|---|---:|---:|---:|---:|
| VigilODE Rodas5P | 27 | 423 | −2.244605877360619e−18 | +1.2417294486923328e−15 |
| Diffsol BDF | 53 | 74 | +3.682639635754642e−15 | −5.4296612942657086e−14 |

Gas와 time probe를 절반으로 한 후속 실행에서 양쪽 방법의 gas·온도 endpoint는 표시된 binary64 값이 같았다. VigilODE의 안정적인 photon 차이 평가는 최대 `6.166244974933198e-22`/H, log-survivor 차이는 `4.404571325722362e-20`이었다. Diffsol에서는 이 비교량도 0이었다. 이는 이 짧은 제조 fixture에서 관측한 차분 민감도다. Native reference의 수렴, 전역 오차 상계, 두 solver의 속도 순위로 사용하지 않는다.

## 다음 실행

C21H는 기존 `common_ic`와 `native_source` fixture에 각각 두 방법을 적용하는 base 4개, 그리고 각 base의 실제 완료를 요구하는 fd_half 최대 4개를 준비했다. 요청 tolerance는 `rtol=2e-11`, scalar `alpha=2e-14`, cell step divisor 8이다. C21G의 reference ladder 8개와 조건부 refinement 4개는 기존 PR84 계약을 유지한다.

NCP에서는 새 결과 확인, 현재 CPU/RAM·다른 campaign·dirty files·watcher·checkpoint 확인, 독립된 새 worktree, locked build 및 순차 실행을 수행한다. 보호 CPU55를 할당하지 않는다. 완료된 동일 source/fixture/job은 재실행하지 않는다. 실제 명령과 영수증 판독은 `handoff/CODEX_HANDOFF_KO.md`에 있다.

Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity는 해당 독립 검증까지 HOLD다. `global_error_bound=null`을 유지한다.
