# BASS cosmic-ray charge exchange

출판된 H⁺ + H(1s) → H(bound) + H⁺ 문제의 독립적인 paper-based 구현과 결과 감사입니다. Nichols 비공개 코드 또는 raw data의 재현을 주장하지 않습니다.

현재 상태: **100-keV/u b-grid NO_GO**. 단일 b=2 a₀에서 TDL 6개와 one-electron AOCC 2개 실행을 완료했습니다. 전체 테스트는 20/20 PASS이며 TDL 공간 refinement 변화는 10.47%, AOCC basis refinement 변화는 9.07%입니다. 수치 안정성이 확보되지 않았으므로 단면적 적분과 50/225 keV/u 계산은 실행하지 않았습니다.

- [상세 결과 보고서](results/R3M10_LOCAL_RETURN_20260921/README_KO.md)
- [Gate 결정](results/R3M10_LOCAL_RETURN_20260921/report/DECISION.json)
- [TDL 수렴표](results/R3M10_LOCAL_RETURN_20260921/report/tdl_convergence.csv), [AOCC basis 수렴표](results/R3M10_LOCAL_RETURN_20260921/report/aocc_basis_convergence.csv)
- [실패 기록](results/R3M10_LOCAL_RETURN_20260921/report/FAILURE_LEDGER.json), [수정 patch](results/R3M10_LOCAL_RETURN_20260921/report/changes.patch)
- [전체 결과·체크포인트 archive](https://github.com/cosmosapjw-quantum/bass_cr/releases/tag/r3m11-single-b-20260921), [asset 해시 및 Git 제외 파일 목록](provenance/RELEASE_ASSETS.json)

현재 루트의 source/config/tests는 실제 실행 사본과 byte 단위로 일치합니다. 원본 R3M10은 최초 커밋과 결과 묶음의 `input_package.tar.gz`에 보존되어 있습니다. `R3M10_STATUS.json`과 `00_READ_FIRST_KO.md`는 당시의 역사적 상태이며 현재 결정은 위의 DECISION.json입니다.

Git에는 코드, 설정, 모든 result JSON, stdout/stderr, 환경·테스트 receipt, 수렴표, 실패 기록을 포함합니다. 큰 TDL `state.npy` 6개는 같은 저장소의 prerelease archive에 포함됩니다. 가상환경 자체는 제외하고 설치 목록과 환경 정보를 보존합니다. Prerelease는 자료 배포 표식이며 scientific admission이 아닙니다.

Git checkout 검증:

```bash
sha256sum -c MANIFEST.sha256
```

전체 archive를 내려받아 `.sha256`과 대조하고 압축을 푼 뒤, 그 폴더의 `MANIFEST.sha256`을 검증하면 체크포인트까지 확인할 수 있습니다. Git 안의 결과 하위 폴더에서는 `GIT_SUBSET.sha256`이 현재 포함 파일을 검증하며, 그 폴더의 원본 `MANIFEST.sha256`은 전체 archive용입니다.

다음 CR node: `R3M11_IMPORT_LOCAL_SINGLE_B_RESULTS_AND_DECIDE_BGRID_GATE`.
