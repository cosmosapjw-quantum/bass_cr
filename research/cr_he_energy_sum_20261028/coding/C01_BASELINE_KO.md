# C1 구현 baseline과 재사용

기준은 실제 immutable PR112 D와 manifest에 묶인14개 입력 파일이다. SOURCE/CLOSEOUT 원본을 검증해 얻은 파일 projection을 사용하며, 현재 GitCLI 네트워크 실패 때문에 local GitHEAD를 주장하지 않는다. 각 실제 게시의 commit/tree/expected-parent/ref readback은 GitHub API로 따로 증명한다.

재사용하는 과학 입력은 PHYS02 source JSON identity, saved attribution NPZ와 byte-pinned event_union consumer다. Canonical source를 다시 fit/적분/투영하거나 transport/RR를 재실행하지 않는다. Source JSON 대신 attribution을 새로운 authority로 승격하지 않는다. C1은 identity와 호출 경계를 확인하는 단계이고 새 source 계산이 아니다.

구현 파일은 exact core/adapter, bounded runner, primary/controls, 독립 reference/worker, saved-result plot으로 분리한다. Reference author는 reference와 worker의 SHA를 동결한 뒤에만 production을 읽었다. C4 이전 과학 import, NPZ array load, compiled execution, test 또는 plot 실행은 하지 않는다. Python runtime의 실제 일반 probe는 이번 세션에서 성공했고, 새 단위의 자원부담 probe는 C4에서 별도로 남긴다.

새 scope는 PR114 하나이며 current central28/88·count effect0이다. 과거 실행 실패와 provider 실패는 해당 identity와 함께 남긴다. R05 Dropbox 전송 실패2건은 metadata 실패이며 source/과학 실패나 science 재실행으로 합산하지 않는다.
