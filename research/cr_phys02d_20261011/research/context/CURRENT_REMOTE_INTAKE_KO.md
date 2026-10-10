# bass_cr 원격 상태 intake — 2026-10-11 KST

## 판정

**실제 새 paired 9600 결과를 확인하고 복원했다.** 이전 PHYS02C의 `PREPARED_NOT_EXECUTED`는 역사적 상태다. 후속 PR30이 실행과 독립 `PASS_SCOPED`를 추가했고, PR31은 CCC 원천 정체성을 `SOURCE_IDENTITY_UNRESOLVED`로 유지하는 세 파일을 더했다. 이번 intake에서는 원격 쓰기·과학 계산·새 후보 설계·독립 재심사를 하지 않았다.

| 기준 | 정확한 정체성 |
| --- | --- |
| 다음 additive 연구의 권장 base | `research/ccc-source-identity-hold-20261011` / PR31 |
| 최신 commit / tree | `f98ed974c3f3158dabd16cd854ecc5e04b9f5b31` / `ae9c5ea98edd724423bfa8cb79db976908d1c123` |
| paired 9600 commit / tree | `55a97935c5f589e1857e0de595263c94dc52ce53` / `77e7e4a64bb19415a401df2bec147d8653ea58dc` |
| paired commit의 실제 parent | science `f34a0cc1484247caf252afde3d5fbe834640e9e4` |
| 원래 PR28 receipt head | `eecb9bdceb40ff8dbb84feba969d1eec6555970f` — 그대로 유지 |
| main | `77237751bdd2aed5934bf7fc3bc626d631a09058` |

PR30의 PR base branch는 PR28이지만 실제 commit parent는 science f34a0cc1이다. 후기 receipt eecb9bd는 PR30/31의 조상에 포함되지 않는다. 원래 전달 영수증을 별도 provenance로 보존해야 한다. PR30·31은 모두 open draft다.

## 읽은 실행 근거

원시 NUMERICAL_RESULT·ACTUAL_EXIT·두 NPZ·로그를 exact Git blob으로 확보했다. 2026-10-10 18:14:45–18:36:47 UTC 실행이며 child/coordinator exit0, timeout false, wall1321.697224491초다. 두 순차 call은 fullBED671.934927초와 legacy646.572190초이며 각각9600노드다. 실제15개 check가 PASS_SCOPED다.

`INDEPENDENT_DECISION.json`은 controller가 공급한 fresh Astra 검토를 mechanical worker가 직렬화했다고 명시하며 publication worker의 runtime model 독립 관측은 없었다고 기록한다. 이번 intake는 published scoped 판정을 재사용한다. ACTUAL_EXIT의 `AWAITING_INDEPENDENT_ASTRA_REVIEW`는 후속 decision 이전 시점의 상태로 보존한다.

새 fullBED의 T=1e10s에서 H I ionization은6.181443264058178e−18m⁻³, He I는2.318707345589628e−19m⁻³, heat power는3.4427310257273574e−44Jm⁻³s⁻¹, finite/terminal ratio는0.03418586005219275다. 95개 행의 raw분류66/22/7을 유지하며, 7개 low-tag 미해결 행의 roundoff 차이에 물리적 유의성을 부여하지 않는다.

새 실행은 Python3.12.3 / NumPy2.4.2 / SciPy1.17.0 /1thread다. 기존4800 결과는 Python3.12.14 / NumPy2.3.5였다. 4800→9600을 동일 환경에서 격자만 바뀐 완전히 분리된 실험이라고 표현하지 않는다. 실제32GiB급·24개 affinity CPU 관측은 NCP64 실행·scaling 증거가 아니다.

## 운영 수정과 실패

기존 plan은 true cgroup2 root의 max/current 파일 부재를 HOLD로 처리했다. additive adapter는 true root의 ENOENT와 cpuset controller 비활성 자손의 inherited effective set만 허용한다. 비root 결손·권한·읽기 실패는 계속 HOLD다. 실제 ops SHA256은 `8360e9f123bfc5814507728d6f946acd5109daaff2b475048d7c6ff586a4f2e7`, launcher는 `6ede08c6398bd3556b0168832b18dc59d4cbe938e3c4172109be49188613426b`다. launcher 변경은 import/provenance 기록이다.

첫 adapter execute는 기존 run-dir guard에서 exit1이었다. 이 zero-transport 실패와 이전 preflight를 보존했고 새 디렉터리에서만 두 수송을 완료했다. 다음 launcher가 필요하면 원 science를 덮어쓰지 말고 adapter source와 receipt를 명시적으로 사용한다.

## CCC 및 다음 상태

PR31은 raw marker10.2043500/21.1156000을 보존하고 state-energy substitution·axis shift를 금지한다. exact2026ZIP에 결속된 (1)state/eigenenergy·단위, (2)Hamiltonian/basis/질량/shift, (3)first-zero exporter/rounding/axis 관계, (4)생성 provenance 네 종류의 upstream 입력이 필요하다. 이번 intake는 새 CCC 원문을 읽지 않았다.

paired9600은 DONE_SCOPED다. 다음은 저장 결과를 재사용하여 독립 READY 연구를 진행하는 것이며 네 번째 격자는 NOT_AUTHORIZED다. PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, global physical admission HOLD를 유지한다.

root AGENTS/readback 정책 blob은 baseline과 같고 Astra tier-routing은 기존 context copy로 보존돼 있다. 두 PR은 root 정책을 바꾸지 않았다. AGENTS가 참조한 machine readback JSON은 exact tree에 없지만 docs/READBACK_POLICY.md를 실제 읽었다.

## 복원 및 백업 범위

33개 원격 파일1237488bytes를 sources/에 복원하고 Git blob·size·SHA256을 확인했다. 성공 returnZIP514527bytes의 SHA256은 `66c63211a45fd28285b8ea56c6d9b5c82613c9300b0e98589896bb8e68cc9644`이며 내부28payload와 exact entry set도 검증했다. ZIP 단독은 불완전하다. 8파일 first-failure sidecar와7파일 operational-adapter sidecar도 함께 확보했고 published hashes와 일치한다.

가장 작은 관측 complete recovery는 Dropbox `CR_PHYS02C_PAIRED_9600_REVIEWED_20261011.tar.gz`,5383056bytes, ID `id:BSpOijBcT10AAAAAAD33DQ`다. 위치는 `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS03_20261010_RECOVERY/`이며 extracted receipt SHA256은 `5d977891e4b2e8187c3e9f66c630986ed0d237c063cb255227767808fa0e8267`다. 이 archive 자체는 다운로드하지 않았다. 기존 부모 자료와 더 작은 exact Git payload 복원으로 필요한 근거를 확보했다.

Drive의 특정9600 검색 및100 direct-child 조회에서는 새9600 백업을 확인하지 못했다. Dropbox에는 대응3객체가 있다. 이는 bounded 조회 결과이며 exhaustive absence가 아니다. 새 반환의 이중백업 완료를 확정하지 않는다.

Dropbox fetch는1480bytes 영수증을1481bytes extracted text로 반환했다. 최초 size assertion 실패를 기록하고 EXTRACTED.txt로 보존했다. 이 텍스트의 해시를 원격 원시 byte hash라고 주장하지 않는다. Git 원시 source의 exact 검증과 구분한다. 관련 메타데이터는 REMOTE_READ_RECEIPTS_SANITIZED.json, 전체 파일 정체성은 SOURCE_BYTES_VERIFICATION.json, 반환 검증은 RETURN_ARCHIVE_IDENTITY_CHECK.json 및 RETURN_MANIFEST_VERIFICATION.json에 있다.

