# C21N 최종 마감: 기존125 결과 재사용, 초기 상쇄 응답, 준비 계층 게시

## 1. 판정

독립 matter/radiation 초기응력을 갖는 non-tilted collisionless LRS Bianchi I의
첫 pilot/preliminary plot은 이미 **125개 완료 결과**로 확보됐다. 최신 NCP98
반환을 실제 source·input·raw·seal과 연결해 수용했고 기존26개와 원 중심1개에
합쳐진 ensemble을 재사용했다. 이번 C21N에서는 **새 과학 ODE0회**로 이론 유도,
샌드박스 focused 검산, 코드 구현, 기존 결과의 성분별 그림과 국소 응답 분석을
마쳤다. 자세한 근거는 [REPORT_KO.md](REPORT_KO.md)에 있다.

| 구분 | 마감 상태 |
|---|---|
| EXECUTION | 기존125 후처리·scoped 코드/물리 검산 완료; 새 offgrid4 ODE는 NOT_RUN |
| PUBLICATION | content `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`, Draft PR93; 이 문서는 별도 document commit |
| BACKUP | 아래 실제 provider 영수증에 한정; ACK와 다운로드 byte 재검증을 분리 |
| DAG | 이번 이론/구현/분석 COMPLETE_SCOPED; offgrid4 PREPARED/NOT_RUN; 확장물리 HOLD |

## 2. 게시 권위와 문서 경계

- Repository: https://github.com/cosmosapjw-quantum/bass_cr
- Draft PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/93
- Branch: `research/cr-c21n-mass-shell-cache-20261021`
- Content: `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`
- Content tree: `a88047102008e51ac8061f0ac18773ff09f0ff10`
- Parent/PR92 head: `645a7f1a960be10e10574a819d7fb35a4511d9fa`
- 고정 물리 source: REI `3b85dedce84d37b3e165da00685a8a984950aafe`

Content의130개 새 파일에 대한 blob ACK와 실제 원격 branch SHA를 확인했다.
기존 C21L/M 파일 변경은0개다. 이 마감 문서는 content의 과학 source나 결과를
바꾸지 않는 후속 document commit이다. Document 자신의 SHA는 자기 내부에
기록하지 않으며, 별도 document 배송본의 authority receipt와 최종 응답에
실제 SHA를 기록한다. 실행은 위 content SHA로 고정한다.

`CONTENT_MANIFEST.json`은 **고정 content snapshot**의129개 payload를 검증한다.
후속 document commit에서 갱신한 DAG/ledger 파일을 그 옛 hash로 검증하지 않는다.
원 content와 모든 기존 과학 검증 receipt는 그대로 보존한다. 검증 당시의
`PUBLICATION=PENDING`은 당시 관측값이며, 현재 게시/백업 상태는 이 문서와
`PUBLICATION_RECEIPT.json`/`BACKUP_RECEIPT.json`이 연결한다.

## 3. 이론과 물리 결과

Full Frobenius 규약에서 signed 좌표는
`S=sqrt(6)*s/H_t`, `P_X=sqrt(6)*(8*pi*G/c^2)*p_X/H_t^2`이고
`Sigma=abs(S)`, `Pi_X=abs(P_X)`다. `p_X=Delta p_X/3`이다.
`kappa=8*pi*G/c^4`는 `H_geom=H_t/c`와 함께 쓰면 동일하다. Matter,
photon, 존재하는 massless neutrino를 분리해 보존하고 tensor 합 뒤 norm을 취한다.
Half-contraction이나 `Pi_tot=Pi_m+Pi_r`로 바꾸지 않았다.

Conserved momentum packet을 직접 미분해 massive energy identity와 응력
도함수를 구현했다. 초기 `S0=Ptot0=0`의 이상적 상쇄에서

\[
S''_0=-(1-\beta_m)P_{m,0},\qquad
S(\eta)=-\tfrac12(1-\beta_m)P_{m,0}\eta^2+O(\eta^3),\quad
\eta=\ln(a/a_0)
\]

를 얻었다. 현재 비영 상쇄4case의 `beta_m≈0.031700764391`이며 실제 초기
offset과 FP grouping 잔차도 따로 보존했다. 원 mass-shell 항등식은 Exa로
원전, SciSpace로 서지를 확인했고 Wolfram의 성공2건으로 대수를 검산했다.
이는 질량이 다른 성분의 국소 적색이동 응답에 대한 유도이며 다른 source
family의 전역 isotropization 정리를 이 문제에 이식한 결과가 아니다.

국소 이차식과 기존 저장 trajectory의 상대차는 첫 양의 저장점에서 최대
2.1223%, 표시한 마지막 `eta=0.1004559168`에서15.8374%다. 국소 부호와
계수 해석에 유효하지만 전체구간 대체·1% 근사·전역 오차보증은 성립했다고
판정하지 않는다. 연속 remainder bound와3차 계수는 미확립이다.

| z4 norm | 기존125 ensemble 최대값 |
|---|---:|
| Sigma | 1.4449836382490454e-3 |
| Pi_m | 1.2574783729509532e-5 |
| Pi_r | 6.344480064794384e-5 |
| Pi_tot | 7.577499571350794e-5 |

이 값은 특정125개 ensemble의 종단값이며 보편 상계가 아니다. 초기81개의
다른 ensemble 결과를 대체하지 않는다. 성분별25cell 그림과 상쇄4trajectory
그림의 PNG를 직접 확인했고 PDF도 내보냈다. 별도 PDF raster/print 검토는
NOT_RUN이다. 중심의 미세한 raw stresses는 보존하되 그 FP 잔차의 cancellation
비율을 그림에서 물리적으로 해석하지 않도록 표시했다.

## 4. 구현과 정확한 검증 범위

새 `PreparedMomentumFactory`는 A와 무관한 radial/angular geometry만
worker당 준비한다. A마다 distribution weight, packets, cell populations,
energy normalization, number/minimum을 원 연산 순서로 재생성한다. 원
moment/RHS/DOP853,FP64,허용오차는 보존했다. 외부 ACCEL01에서는 immutable
backing과 metadata guard 원칙만 채택했다. 다른 C15 solver의 cache는 이식하지 않았다.

| 검증 | 실제 수행한 범위 |
|---|---|
| 원 constructor/moments |15구성/45상태 FP64 bytes 동일 |
| 기존125 초기조건 |mapping receipt dictionary equality, initial state bytes 동일 |
| 원 full source 정적 비교 |375저장상태,22,125field 값+15,000RHS 값 bytes 동일 |
| 준비 작업 재사용 |추가 quadrature를 금지한5개 A trial 통과 |
| 독립 source 심사 |vendor9파일, AST/FP order/alias/guard/source binding |
| 도함수 |12packet states; complex-step 최대4.44e-16;3초기 full-source 방향미분 최대8.74e-14 |
| 보존 항등식 |massive12,625상태 residual 최대1.025e-15; radiation375상태1.7005e-14 |
| shared runner |3focused groups의 fake science3case; 이후 바뀐 대기 중 storage guard만 별도 검사 |

Mapping receipt 전체를 byte-identical이라고 확대하지 않는다. Cached source로
125개 trajectory를 다시 적분하지 않았다. 후처리의 signed field2,250값은
numeric 차이0이며 해당 검사까지 byte-equality라고 바꾸지 않는다. 첫 테스트의
manifest nesting 오류와 첫 plot의 mathtext 오류는 당시 source/실패 영수증을
보존했고 수정 범위도 기록했다. 이 검산은 discretization의 전역 오차상계가 아니다.

Storage admission은 available blocks/inodes를 run/lease 생성 전·자원 대기 중·
dispatch 전에 확인한다. 완료125개 물리좌표를 이름 변경만으로 다시 실행하는
것도 막는다. 공유 CPU55/coordinator/threads1/lease·가용자원 제한은 유지한다.
구체적인 운영 검증의 source hash 경계는 `checks/ops_final_scope.json`을 따른다.

**Speedup·RSS 절감·64-core scaling은 UNMEASURED**다. 새 성능 캠페인을 하지
않았으며 NCP98의 단일 elapsed를 이번 최적화의 성능 자료로 사용하지 않는다.

## 5. 외부 intake 범위와 원본 정정

7repo의 광고된 refs 1,232개와 기존1,224개를 비교했다. 새8·변경5·삭제0이다.
이는 모든 branch의 모든 파일을 읽었다는 뜻이 아니다. 관련 변경을 source와
연결해 선별 수용했고 접근 불가능한 대화/다른 scratch는 UNAVAILABLE다.
Drive는 검색 누락을 관측해 known-ID metadata와 folder listing을 사용했다.

NCP98의 canonical identity는
`7f89b12adbeee64a70832e633ae563584bc2a68f6ac433dc56f759a1946eb718`이다.
원4문서의 suffix 오기, CSV LF/CRLF의 원 manifest byte 일치6/7,
archive actual509files를 추가 정정으로 남겼다. 원 raw와 문서를 덮어쓰지 않았다.
새 외부 tar.gz는 Dropbox에서 실제 다운로드해17,911,591bytes,
SHA256 `e9baa6bab57790d29a0dfb06747a3304f0449a48e7dfc2d14c6630849f9c1d0a`,
508/508 payload hashes와98 seals를 검증했다. 이번 Drive intake는 metadata다.

## 6. 남은 실행과 인계

`CODEX_HANDOFF_KO.md`는 정확한 content pin·새 격리 checkout·requirements·
grid SHA·plan/run/resume 명령을 제공한다. `NEXT_THREAD_HANDOFF_KO.md`에는
새 대화가 최신 외부 반환부터 수용하도록 복사 가능한 연구 prompt를 담았다.

남은 새 입력은 `c21n_offgrid4_opposing_z20_z4_20261021`의4개다.
초기 `S0=0`, `Pm0=±7.5e-5,±1.75e-4`, `Pr0=-Pm0`이며 grid SHA256은
`2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5`다.
기존125와 겹치지 않는다. 새 외부 결과가 있는지 먼저 확인한 뒤 실제 실행한다.
현재 NCP 접근/새 실행은 NOT_RUN이다. 기존 NCP98 완료 상태와 혼동하지 않는다.

명목64logicalCPU/128GB는 실행 시 관측할 자원이다. 현재4case에서는 최대4worker,
각1thread와 coordinator1개를 사용한다. 실제 quota·RAM·idle CPU·lease가
허용하는 범위에 맞춘다. 메모리 worker512MiB/coordinator256MiB 및 reserve는
분석적 계획값이다. 기존61worker NCP98 기록은 보존하되64-core scaling으로
해석하지 않는다. 다른 owner의 작업은 건드리지 않는다.

## 7. DAG

| 노드 | 상태 |
|---|---|
| C21K 및 C21L81/component publication | COMPLETE_SCOPED, 기존 권위 보존 |
| C21M 독립 builder/26+center | COMPLETE_SCOPED |
| 외부 NCP98/combined125 | COMPLETE_SCOPED_ACCEPTED |
| C21N mass-shell 유도/후처리/그림 | COMPLETE_SCOPED |
| C21N prepared constructor/shared runner | IMPLEMENTED_PASS_SCOPED |
| offgrid4 초기조건/plan | PREPARED_VALIDATED |
| offgrid4 과학 실행 | NOT_RUN |
| 성능 캠페인/64-core scaling | NOT_RUN/UNMEASURED |
| 연속 remainder/global error bound | NOT_ESTABLISHED, null |
| General triaxial/full reionization/CMB | HOLD |

기존 C21F–K source·실패/raw·HOLD·역사적 NOT_PUBLISHED는 바꾸지 않았다.
다음 단위는 새4case 반환의 수용과 국소 응답의 판별 검증이다. 완료한 과학 계산과
코드 검증 전체를 새로 반복하는 단계로 돌아가지 않는다.

## 8. 실제 백업 영수증

아래 표는 `BACKUP_RECEIPT.json`의 실제 성공 응답에서 생성한다. Main ZIP은
content 시점 C21L/M/N의1,296 tracked files와 배송 metadata를 포함하며,
payload1,299개와 ZIP1,301개 regular files를 로컬에서 재읽어 검증했다.
Document 마감은 별도 ZIP으로 배송하며 main ZIP을 덮어쓰지 않는다.

**Main ZIP:** `BASS_CR_C21N_RESEARCH_DELIVERY_20261021T122801Z.zip`  
크기: **36,735,301 bytes**  
SHA256: `df874b53da8eb3e434500a3e7196626755304850556939d0e93e5f41cd96c524`

| 저장처 | 실제 관측 상태 | Object ID | 크기 확인 | 이번 다운로드 byte 재검증 |
|---|---|---|---:|---|
| Library | ACK_COMPLETED | `libfile_991cd4c187dc81918078fd3e761cac90` | 36735301 | NOT_PERFORMED |
| Dropbox | ACK_COMPLETED | `id:BSpOijBcT10AAAAAAD_gTA` | 36735301 | NOT_PERFORMED |
| Google Drive | REQUEST_PENDING_NO_ACK | 미확보 | 미확보 | NOT_PERFORMED |

Drive에는 새 main ZIP을1회 요청했다. 2026-10-21 12:42:11 UTC의 known-parent 조회에서는71개 항목 중 exact-name match가0이었다. 요청의 완료 응답이 없으므로 실패나 전역 부재를 단정하지 않는다. 이 문서 시점에는 삼중 백업 완료가 아니다. 기존 미확정 배송본을 재업로드하지 않았다. 뒤늦은 응답은 별도 최종 authority receipt로 연결한다.

이 snapshot의 로컬 SHA256과 provider ACK는 서로 다른 증거다. 새 archive의 provider download byte 재검증은 수행하지 않았다. 앞서 외부 NCP98 tar.gz를 실제 다운로드해 검증한 사실을 새 ZIP의 다운로드 검증으로 옮겨 쓰지 않는다.
