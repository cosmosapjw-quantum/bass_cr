# PHYS02G 시작 시점의 bass_cr 소스 확인

2026-10-11 UTC의 읽기 전용 확인이다. 현재 GitHub 최신 PR은 draft PR36이며 head `b21009893b93ed9b7e4af22ac4f480fe4b8e5c4b`, tree `63cd76b80393f3d9c506dec7c80eda8925df39e3`다. 이 커밋은 과학 소스 `39e272815ef13069d7c54fa8c50eab4103f14a79`의 publication-only 후속 커밋이다.

최신 PR 10개, 전체 branch 101개, PR36의 전체 변경 파일 103개와 잘리지 않은 tree 6,346개 항목을 읽었다. 이 범위에서는 PHYS02F 실제 NCP 반환의 새 PR/branch/파일을 찾지 못했다. 판정은 `NOT_OBSERVED_IN_GITHUB`이며, 다른 호스트에서 실행하지 않았다는 증명으로 사용하면 안 된다. 게시된 준비 자료의 `consumed=false`와 `READY`는 당시 기록이다. 현재 미게시 실행의 소모 상태는 알 수 없다.

PR36 전체 파일 103개와 root 정책 4개의 surviving local bytes는 현재 authoritative tree의 size/Git blob SHA와 모두 일치했다. 새 복구가 필요한 파일은 0개였고, 기존 파일 수정은 0개다. SHA256도 영수증에 기록했다. 이 결과는 source byte binding이며 과학 의미의 신규 검증이 아니다.

기존 F 독립 판정은 유도·저장된 9600점 scalar 분석·준비된 adjoint residence 코드 범위의 PASS_SCOPED다. 실제 NCP residence 결과는 이 소스에서 제공되지 않는다. 준비 실행 계약은 fullBED→legacy, G 2회, resolvent block 2개, 삼각 풀이 호출 10회, pulse/expm 0회, wall 900초다. runtime은 Python 3.12.3 / NumPy 2.4.2 / SciPy 1.17.0 및 thread pool 1이다.

상세 `FACTUAL_STATUS.json`에는 기존 Drive/Dropbox ZIP·START ID, 크기, 해시와 판정·DAG·TO04 기록을 보존했다. 이 agent는 provider를 새로 조회하거나 원격 ZIP을 복구하지 않았다. 실제 scientific call, 테스트, candidate/acceptance 설계는 모두 수행하지 않았다.
