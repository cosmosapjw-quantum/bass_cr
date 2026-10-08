# R4AL 이후 atomic-only Codex 시작 지시

최신 R4AL 전체 패키지와 DELIVERY_RECEIPT를 회수해 archive SHA256를 대조하고 새 디렉터리에 푼다. Dropbox/Drive의 실제 ID와 SHA는 detached receipt에 있다. 이전R4AK patch 대신 이번publication/PENDING.patch와PENDING_MANIFEST.json만 사용한다.

1. verify_package.py로 바이트를 확인하고 CODEX_HANDOFF_KO.md, FINAL_STATE, REPORT, DERIVATION, NEXT_DAG를 읽는다. 완료 계산/시험을 반복하지 않는다.
2. 현재 repo/branch/HEAD를 읽는다. 기대부모는 ce1a050b581791462e9b2f0954a88ea49278c3f0. 같고 clean이며 모든새path가없을때만 tools/apply_pending.py --manifest publication/PENDING_MANIFEST.json --repository <repo>로check한다. --apply후실제diff/hash검토및samebranchnon-forcepush를수행한다. 부모가다르면정지하고새diff계약을작성한다.
3. runtime/R4AH_M64_RUNTIME.zip의원본launcher를사용해NCP환경prepare/build/pin을수행한다. 기존코드를다시구현하거나guard를낮추지않는다. exactBATCH/native/output과m64범위를검토·승인한뒤m64한점만실행한다. 나머지9자동실행/기존중심/M9/oldR8반복금지.
4. 성공또는실패의전체evidence를bundle하고읽기전용검토뒤반환한다. m64성공은전체stencil/bridge/단면적승인이아니다.
5. cosmology/transport/재이온화진화는rei_bianchi가담당하며여기는원자데이터producer만이다. G02UNRESOLVED,productionHOLD,capturefalse,all_boundOPEN,b_gridNO_GO를유지한다.

R4AL의새결과는두기존window의full18Gram하한과거친weaknorm이다. K약60Eh상계를정밀오차또는작은bridge상계로사용하지않는다. 여기서계속할로컬과제R4AM은실제weakK검증적분기/나머지와원자export규약이며NCP의m64와병렬이다.
