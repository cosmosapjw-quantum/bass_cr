# C21I native exact-cache admission·runner 연결 검토

`native_cache_contract.py`와 `tests/test_native_cache_contract.py`를 새로 구현했다. 현재 Python3.12.14에서 **14개 focused 계약 PASS**다. 검사는 원본 Python provider class와 미리 넣은 protocol 응답·가짜 process/stream을 사용했다. 실제 NativeMicro 생성자, Popen, native/Rust 프로그램, ODE 적분기와 기존 C21H/C21F/C21G suite를 실행하지 않았다.

## API와 runner 연결

```python
contract, guard = admit_native_cache(
    provider,
    native_provenance,  # 실제 C21G verify_native_binary의 반환값
    {"fixture_sha256": f.digest, "fixture": asdict(f)},
    source_identity,    # 실제 H+I runtime closure와 입력 context를 확인한 JSON mapping
)

result = run_optimized_reference(
    f, provider, source_dir, bridge, out, scales,
    optimization="vectorized_exact",
    cache_contract=contract,
    cache_guard=guard,
    # 원 runner의 같은 rtol/atol/FD/method/남은 job budget를 전달
)
guard(full_hash=True, current_provider=provider)
# 이후 원 runner의 postchecks·receipt·provider.close 경로를 유지
```

이 호출은 `vectorized_exact`의 native 경로에만 필요하다. 기본 `vectorized`는 successful-value cache를 사용하지 않으므로 purity admission을 요구하지 않는다. Caller가 반환 contract를 받은 뒤에도 동일한 provider 객체를 adapter에 전달해야 한다. `current_provider` 인자는 상위 binding을 명시적으로 재확인할 때 사용한다.

helper의 import는 표준 라이브러리만 사용한다. **Fresh process에서 source가 확인된 private H runner를 먼저 load**하여 `NUMPY_ALREADY_IMPORTED`와 thread=1 설정을 실행하고, 그 뒤 optimized adapter를 import한다. H flag를 False로 덮어써서 우회하지 않는다. 이 순서는 새 focused 검사에서 실제 확인했다.

상위 runner의 immutable source identity에는 I runner·optimized adapter·이 helper·실행 설정 및 원 H 실행 closure가 들어가야 한다. helper는 이 mapping을 소유 JSON으로 contract에 넣고 원 mapping의 깊은 변경을 guard에서 거절한다. 실제 전체 H+I source 파일의 전후 검증, 고정 fixture의 validation/digest, cell-owned key와 full-state validation은 기존 runner/optimized adapter의 책임으로 계속 남는다.

## 구체적으로 admission한 경로

원본 C21F `NativeMicro` 또는 그것을 직접 감싼 원본 private C21H `BudgetedNativeMicro`만 admission한다. 타입 이름이나 `kind` 문자열만으로 허용하지 않는다. 실제 class가 정의된 module namespace·파일 SHA, 모든 원 method의 code field·nested constant·default·property, class namespace를 source와 비교한다. 그 후 실제 class/function/instance/inner binding을 고정한다. Subclass, 기존 method 교체, 추가 `__getattribute__`, instance method override와 이후 교체는 거절한다.

Native provider source SHA256은 `ce27acea344604c08159e08d6e703f66a85d51f0729b4e30aa2248a3337ecc27`, budget wrapper source는 `6f344f60d26a0ddb7bb205255cb767fdc230062bf60c56aae1ce58f5ef258f6c`다. Native point wrapper SHA256 `3812cf4fec625fdec32e47d737bec8e0306cc538372c5a2cf801d2b0cf590e2d`와 C21G authority SHA256 `fb450ad1d00c35e73e99d52c868f2c1a70d1ef71ab1ae83a08ed0e6c0dc00451`도 확인한다.

Native provenance는 입력 문자열을 신뢰해서 넘기지 않고, source가 고정된 C21G `verify_native_binary`를 별도 namespace에 load하여 다시 계산한다. 따라서 원 PR82 binary hash 재사용 또는 같은 owner에 대한 기록된 build 입력·binary·archive identity가 일치해야 한다. 원 command는 절대 경로의 native binary 한 개여야 하며 `--export-source` 같은 다른 동작을 같은 cache 계약에 합치지 않는다. NativeMicro의 constructor가 남긴 `native_process.json`의 owner·command·binary SHA·initial timeout·max_calls도 대조한다.

실제 owner는 `6ea2b1b4b3875c9163cafc45efe720afded43fc4`다. 기존 독립 검토는 `native_point::evaluate`의 EVAL이 요청마다 새 상태를 만들고 `igm_point_rhs`를 호출하는 경로와 owner5파일의 Git blob을 확인했다. `c21i_theory/REVIEW_PLAN_KO.md` 및 `raw/owner_purity/BYTE_IDENTITY.json`의 기존 검토를 재사용했고 새 owner/native 과학 실행으로 표시하지 않았다. 확인된 owner5개 Git blob은 helper의 `OWNER_PROOF`에 기록한다.

이 admission은 source/build provenance와 intended fresh runner context에 대한 계약이다. 기존 namespace의 모든 가능한 Python library monkeypatch나 OS 프로세스의 실행 내용을 일반적으로 증명하는 attestation은 아니다. Fresh verified namespace와 source/runtime 전후 검증을 계속 요구한다.

## 매 callback의 guard와 성공값만 저장하는 경계

guard는 actual-call counter를 늘리거나 provider를 호출하지 않는다. 다음 운용 경계를 검사한다.

| 항목 | 동작 |
|---|---|
| Provider binding | exact class/method/global binding, 같은 native inner instance 유지 |
| Native 설정 | 원 command·고정 max_calls·원 instance field 집합 유지 |
| Process | 같은 process 객체·class·PID·args·poll binding; poll 결과가 아직 None |
| IO | 같은 stdin/stdout/log/stderr와 열린 stream; 같은 selector/interface |
| Counter | 정수 actual calls가 감소하지 않고 0≤calls≤max_calls |
| Timeout | 원 wrapper가 바꾸는 finite `0 < timeout <= 15s` 허용 |
| Deadline | budget wrapper의 원 monotonic deadline bit identity와 만료 여부 확인 |
| Fixture/source/provenance | 전달 mapping과 반환 contract의 깊은 변경 거절 |
| Files | admission 당시 확인한 source/binary/build/process receipt의 immutable-file lease 확인 |

`calls == max_calls`일 때 N번째 실제 호출의 성공과 이미 성공한 exact hit는 허용한다. 새로운 native 호출을 쓰지 않는 hit는 call cap을 소비하지 않는다. N+1번째 **miss**는 원 NativeMicro의 `NATIVE_CALL_BUDGET`로 거절된다. 이 경계는 원 Python `__call__`를 실제 실행하되 IO만 stub으로 둔 검사에서 확인했다. 허위 native log나 call count를 만들어 hit를 실제 실행으로 표시하지 않는다.

deadline이 지난 hit, closed/dead process의 hit, 교체되거나 변조된 context의 hit는 실패한다. 원 BudgetedNativeMicro의 `timeout=min(15초, 남은 job budget)` 및 실제 native call 전후 deadline 검사도 그대로 실행된다. Timeout 값은 call 시작 시 설정되므로 call 끝의 더 짧아진 remaining 값과 같아야 한다고 잘못 요구하지 않는다.

Bare NativeMicro에는 원래 one-job deadline 필드가 없다. 이 경우 helper가 새 deadline을 만들어 예산을 연장하지 않고, `run_optimized_reference`의 공통 job deadline guard를 사용한다. H native runner의 정상 경로는 BudgetedNativeMicro이므로 원 deadline을 추가로 바인딩한다.

helper 자체에는 value cache가 없다. `optimized_adapter`가 원 RHS의 성공·finite·shape validation과 post-call guard를 지난 값만 소유 copy로 삽입한다. 실패·NaN 결과가 삽입되지 않는 것을 새 focused 검사로 확인했다. 기존 물리 state·ledger15개·accepted trace·WRMS·수지 검사는 생략하지 않는다.

## File SHA와 경량 guard의 구별

admission에서는 실제 바이트 SHA256을 검증한다. 매 callback에서는 canonical path와 `(device, inode, size, mtime_ns, ctime_ns, mode)`가 그대로인지를 검사한다. Metadata 또는 경로가 바뀌면, 같은 내용으로 보이더라도 그 lease를 거절한다. 같은 길이로 파일을 바꾸고 mtime을 되돌린 경우도 ctime 변화로 실패하는 것을 검사했다. 이 경로를 매 callback마다 binary 전체를 SHA 재계산했다고 표시하지 않는다.

`guard(full_hash=True)`는 실제 terminal SHA를 다시 계산한다. **provider.close 전에 호출**해야 하며, 원 H runner의 `verify_native_binary` 및 전체 source postcheck를 대체하지 않는다. 검증된 파일이 정상 filesystem metadata 의미 아래 변경되지 않는다는 lease를 이용한 범위다. 이 helper의 비용에는 JSON context 비교와 여러 stat이 포함되므로, 가벼운 제조 provider guard를 사용한 benchmark의 속도 향상을 그대로 native-cache 속도 향상으로 옮기지 않는다.

## 실제 검사와 실패 원본

`evidence/native_cache_contract_03/RECEIPT.json`은 현재 source의 14개 focused 계약 PASS를 기록한다. 기존 H/I source와 새 helper/test8개 파일의 전후 SHA가 일치했다. 세부 raw는 동일 디렉터리에 있다.

앞선 실패를 보존했다.

1. `native_cache_contract_01`: `marshal.dumps(code)`가 동일한 code field에도 intern/reference serialization 상태에 따라 달라져 정상 class를 거절했다. 실제 비교 진단은 모든 code field가 같음을 보였다. Source code field·nested constants·float bits를 직접 비교하도록 helper를 교정했다.
2. `native_cache_contract_02`: helper13계약이 통과했고 replacement test는 다른 거절 경로를 관측했다. Test의 `copy.copy(NativeMicro)`가 Python copy protocol을 통해 class에 `__slotnames__`를 지연 생성했기 때문이다. Replacement fixture는 원 class의 `__new__`와 field 사본으로 바꾸었고, admission 전 추가 class namespace도 거절하도록 강화했다.
3. `native_cache_contract_03`: 변경된 class admission에 의존하는 새14계약을 모두 재확인했다. Native/Rust/ODE 실행0, source 전후 identity 일치다. 이를 기존 과학 suite의 red-first 또는 native PASS로 합산하지 않는다.

## NCP compile·작은 호환 수정의 범위

원 H handoff의 실제 build 명령은 다음 형식이다. 변수 값은 현재 NCP inventory와 실제 published execution content commit의 격리 worktree에서 정한다.

```bash
taskset -c "$C21H_CPU" bash "$C21H_UNIT/rust_bridge/build_bridge.sh" \
  --cargo "$C21H_CARGO" --rustc "$C21H_RUSTC" \
  --target-dir "$C21H_BRIDGE_TARGET"
```

build helper는 고정 Cargo.lock과 `--locked --release --jobs1`을 사용하고 create-only absolute target을 요구한다. Registry/git dependency가 실제로 준비됐을 때만 `--offline`을 추가한다. 세 build source는 H의 `rust_bridge/Cargo.toml`, `Cargo.lock`, `src/main.rs`다. 독립 block_solver의 compile receipt를 H bridge source receipt로 사용하지 않는다.

현재 ChatGPT runtime에서 실행했던 작은 환경 수정은 bundled rust-lld의 executable mode 문제를 피하는 `RUSTFLAGS='-C linker-features=-lld'`였다. Source·Cargo/lock·VigilODE pin을 바꾸지 않았고 system linker로 actual locked compile PASS를 얻었다. 이 호스트의 실패·수정·binary identity는 `intake_current/runtime/`에 보존했다. 현재 NCP에서도 같은 문제가 있다고 가정해 이 flag를 기본 적용하지 않는다. 실제 Rust/Cargo/linker와 Python 버전을 먼저 확인하고, 관측된 호환 문제만 작게 수정한다. Helper의 class/code 검사는 현재 Python3.12.14에서 확인한 범위이며 새 NCP interpreter의 class metadata/code-field 차이는 그 실제 버전에서 확인할 항목이다.

H handoff의 `status=PUBLISHED` guard와 실제 content commit을 읽는 절차는 유지한다. 이 helper 구현은 현재 NCP live 자원 확인·CPU 할당·새 locked compile·actual native 실행을 수행한 근거가 아니다.

| 실행 | 게시 | 백업 | DAG |
|---|---|---|---|
| helper 구현·현재14 focused stub 계약 PASS; native/Rust/ODE0 | 이 subtask GitHub write0 | 상위 create-only 백업 영수증의 실제 ACK 확인 필요 | source purity→admission/guard 구현→stub 검사 완료; runner 통합·NCP/native는 상위 노드에서 별도 평가 |

`native_chemistry=NOT_RUN`, `native_performance=NOT_EVALUATED`, `global_error_bound=null`.
