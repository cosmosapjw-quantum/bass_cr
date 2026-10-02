# R4AG shifted S 실행계약과 정확 구간 stencil

2026-10-03 KST. R4AG=CLOSED_PORTABLE_IMPLEMENTATION_AND_EXECUTION_RETURN_CONTRACT. 실제 shifted 원자적분은 0회이며 numerical certificate는 NOT_RUN이다. 두 window의 total_upper는 null이다. 이 게시물을 실제 10점 실행 성공으로 읽지 않는다.

## 실제 산출

원래 R4AD의 immutable GEOMETRY/S에서 z0=-32에 +/-1/64,+/-1/128,+/-1/256,+/-1/512,+/-1/1024를 더한 10개 입력을 회수했다. 두 R8 window는 각각 8개 표본이며 6개를 공유한다. 실제 FP64 geometry/time hex, 원 raw/full/task/S와 source identity를 보존했다. 중심점은 shifted registry에 없다.

source/common.py, runtime_contract.py, point_engine.py, batch.py, collect.py, stencil.py, independent_review.py의 7개 모듈과 시험 2개를 작성했다. Gaussian numerical vendor 6개는 parent R4AF와 byte-identical이다. 새 point_engine은 shifted source/input/native/resource/output 계약을 사용한다. 소비된 R4AF runner/계약은 수정하지 않았다.

새 시험49건, 읽기 전용 검토133조건을 통과했다. 다른 Lagrange 다항식으로 가중치와 polynomial response를 확인했고 source/epoch/누락/중복/단위/실행계약을 검사했다. 독립 인간/에이전트 검토나 10점 numerical validation은 아니다. 기존 R4Z-R4AF 과학/시험, center/M9/oldR8/D/Vother 실행은0이다.

최초 자원 admission은 실제 available RAM 1982025728bytes가 worker1+reserve 2415919104bytes보다 작아 build/원자적분 전에 차단됐다. production 조건은 완화하지 않았다. 계약 시험은 자원 관측 경계만 명시적인 test-only8GiB fixture로 바꾸고 실제 compiler/filesystem을 사용했다. point_engine은 이 test-only context의 실행을 거절한다. NCP build/native end-to-end는 아직 NOT_RUN이다.

## 정확한 epoch 및 stencil 합성

원자 저장 단위 a0, ta=ħ/Eh에서 delta=(v*z-v^2*t_FP)/2, C_ideal=exp(-i*delta)C_actual이다. 실제 구간 midpoint M, full-cross 반경 eps, inverse-phase rational midpoint q와 modulus 오차 eta이면 ideal sample 반경은 eps+eta*||X(M)||F 이하이다. phase의 정확한 유리수 Taylor와 실제 나머지를 포함한다.

고정 가중치 w로 midpoint=sum w*X(q*M), 반경=sum |w|eps + sum |w|eta*||X(M)||F + inherited Peano. 유리수 multiply/add는 정확하므로 별도 accumulation rounding항0이다. 입력/phase/norm/truncation의 오차가0인 것은 아니다. 기존fsum 결과를 이 새 certificate로 소급 인증하지 않는다. 모든8표본이 없는 window는 midpoint/total/within_target을 null로 반환한다. 기존 H, weights, 1e-12 ta^-1 기준은 유지한다.

## 완전한 실행 패키지

BASS_CR_R4AG_SHIFTED_STENCIL_PACKAGE_20261003_v1.zip
bytes=2322003
SHA256=05160e18660bf0866320d3e128e79b0efdd39b0db79904b3f333e9f27dd48ff8
Drive ID=1v-NiC71TbpzgDFLcjEJkKeGeYzZe5pHg
Dropbox ID=id:BSpOijBcT10AAAAAADxoGA
Drive parent=1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
Dropbox directory=/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/

두 provider가 업로드 완료와 정확한 이름/크기를 확인했다. R1 UPLOAD_VERIFIED, remote checksum not returned, RESTORE_VERIFIED=false. ZIP은91members CRC/90payloadSHA와49source-input pins를 확인했다. package에는 전체소스/vendor/필수입력/Peano근거/실행반환계약/시험/DBv19/보고서가 있다. 부모의 큰 archive를 다시 중첩하지 않았다.

source lock SHA256=9795d7c0bf930978d4383a7e35113f0b1b8da1d5b05ff43be96b9fa9a748530c
result SHA256=16674a147347db2541da01bb08e87c75543e3290553b3031802c96a166a99ae7
DBv19 SHA256=90062e044a857855bdf8dc08b475acf50ad5690da0ac23d88f3d0b86274aca14
DBv19 integrity=ok, current13rows, other12/v18view unchanged.

## 다음 한 단계

R4AH_SHIFTED_S_RUNTIME_PILOT. 패키지 NCP_START_HANDOFF_KO.md와 START_RUNTIME.md에 따라 실제 NCP 환경에서 prepare로 새 native/환경/output을 pin한다. exact BATCH SHA와 범위 승인 후 m64(z=-2049/64a0) 한 점만 실행해 반환한다. 첫 pilot의 source/geometry/epoch/cover/pole/1e-16 point-target이 수락되기 전에 다른9점을 자동실행하지 않는다. 중심점과M9는 재실행하지 않는다. 구현을 처음부터 다시 쓰지 않는다.

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. A1 previous scope CLOSED, A2 PARTIAL, C0 actual receiver binding PENDING. 포획count와 자유전자/열원을 구분한다.

## 게시 coverage

이 Git commit은 결과 index, state pointer, runtime 시작 지침만 추가한다. package에 있는27개 source/test/contract/doc create-only mapping의 전체작업트리 적용은 NOT_PERFORMED다. 로컬 isolated patch 적용 및27파일 byte일치는 검증했다. 전체코드는두cloud에보존된다. oldR4AA379/R4AD/R4AE/R4AF mapping을 소급완료하거나 과거 safety-block된 mutation을 우회하지 않는다. 향후 전체mapping 적용전 실제ref/diff와 대상부재를 확인해 새 expectedparent 계약으로 non-force 게시한다.
