# R4AL 전체 18채널 Gram·weak 연산자 상계

2026-10-03. **FULL18_LOCAL_GRAM_AND_COARSE_WEAK_TUBES_CERTIFIED**.
R4AL의 이번 bounded substep은 완료했지만 정밀 K/Sdot enclosure와 실제 bridge는 미완료다. 원자물리 데이터 전용이며 rei_bianchi 코드는 수정하지 않았다.

## 실제 진전

R4AK에서는 pair의 Gram만 인증했고 full18은null이었다. 이번에는 R4AB exactG/T와R4AF의인증된중심S를재사용하고H1/Hardy/완전m multiplet의회전대칭으로새적분없이full18하한을얻었다.

|기존halfwidth|uniform lambda_min lower|uniform lambda_max upper|cond2 upper|
|---|---:|---:|---:|
|a0/64|0.944949461133|1.055050538867|1.116515308239|
|a0/128|0.971145650753|1.028854349247|1.059423319715|

바깥쪽으로반올림한표시이며정본은evidence/run_v1/CERTIFICATE.json의유리수다. 두window는원래z=-32부근이며전궤도/다른에너지/b/basis인증이아니다.

L_C<=3.353112271358/a0, ||Sdot||<=6.732985954769/ta. 상계에는p원점의실제비영slope,radial도함수jump,전체m,ETF의위상항이포함된다. H1 병진상계는C9와달리contact회피가필요없지만M9domain을확대하지않았다.

0차Sreference오차는H=1/64에서0.052392379239961 이하, 1/128에서0.026196189619981이하다. 이는연속variation상계지새point오차가아니다. K의zero-reference상계는각각60.426980672353Eh,59.980131124719Eh다. 유효한크기상계이지만작은bridge오차인증에충분히날카롭지않다. 기존H/D의오차가60이라는뜻도아니다.

## 검증·실행

정확유리수scalar단계는한번완료했다. wall약0.012s, maxRSS93,604KiB이며NPZ검사만numpy를썼다. 전체조사/구현/시험시간과다르다. 새cross/radial/M9/oldR8/D/V평가0, m64resourceprepare0, historicalsuite0이다.
새변경영역시험43건통과. 첫Gram행동은실제RED→GREEN이며나머지는추가시험이다. 독립검토211조건은생산코드를import하지않고입력원소·제곱부등식·Hardy상계·epoch·norm을별도Fraction구성으로확인했다. 70자리anchor고유값진단은min0.9978700387829397797,max1.0021299612170420241이며uniformbound의증명은이floating진단이아니다.
독립검토첫버전에서mpmath columnmatrix의e[-1]를마지막고유값으로잘못읽어max0을출력했다. ordering assertion으로실패를재현하고명시적len(e)-1로수정했다. invalid report/source/log를보존했다. 이오류는생산certificate값에영향없었고certificateSHA를그대로확인했다.

## 상태

physical_bridge_upper=null, precise_K_cubature_error=null, full_stencil_total_upper=[null,null].
G02=UNRESOLVED;production=HOLD;capture=false;all_bound=OPEN;b_grid=NO_GO.
NCP의실제m64는여전히필요하다. 그러나여기서수행할원자이론이전부끝나지는않았다. 다음로컬은weakK의contact-cell검증적분/나머지이며atomicexportschema도남아있다. 반복메모리준비나문헌DB재구축은다음작업이아니다.

## 전달

DBv25에새scopedclaims와실행근거를append하고기존15view·과학gap13행은보존한다. 신규코드게시coverage와양쪽backup은최종detachedDELIVERY_RECEIPT의실제ACK를읽는다. 원격restore또는모든역사적pendingmapping의완료를자동선언하지않는다.
