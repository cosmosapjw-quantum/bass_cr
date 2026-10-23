# 다음 대화용 BASS_CR / REI_BIANCHI C23C handoff

아래 내용을 다음 대화에 복사해 사용할 수 있다. 이 파일을 담은 문서 commit의 정확한 SHA와 후속 final-documents/terminal 백업 ID는 `FINAL_DOCUMENT_PUBLICATION_RECEIPT.json` 및 `C23C_TERMINAL_TRANSPORT_RECEIPT_20261024.json`에서 확인한다. 본문은 자기 commit SHA나 아직 일어나지 않은 업로드 ACK를 미리 포함하지 않는다.

```text
$physmath-research-loop 1.3.0으로 BASS_CR / REI_BIANCHI를 이어라.
이번 C23C의 제한된 연구 단원은 완료됐다. 다음 물리 leaf는 CR_N4_STOPPING_KERNEL이며,
병렬 의무는 CR_N5_ATOMIC_ISOTOPE_COVERAGE다. 완료 계산을 복원 목적으로 재실행하지 말라.

[현재 Git 권위]
Repo: https://github.com/cosmosapjw-quantum/bass_cr
새 branch: research/cr-c23c-cutoff-binding-20261023
새 Draft PR98: https://github.com/cosmosapjw-quantum/bass_cr/pull/98
C23C science: 54c2ff11e8308d45c545679301059bc1fcf268eb
Unit path: research/cr_c23c_stopping_coverage_20261023
실제 최신 document/terminal commit은 PR98 head와 terminal receipt로 확인하라.
기존 PR96 branch research/cr-c21o-hheli-z2-sandbox-20261021은
aa57be95b7459eb397d9881b686d9c7bc4444755로 보존됐고 merge하지 않았다.

[실제 C23C 완료]
N4: real saved C23B atoms 32,592개를 재사용한 새 synthetic bath fixture18개.
세 z(2.316/2.479/2.649) × 세 T0(100/10000/50000K) × chi(1.5/3).
각case13개 exact rational count/charge/nuclei/energy/EOS residual=0.
Independent C9: rawCSV Decimal80,18cases977scalar,maxrel1.2507493130458459e-78,
사전기준1e-40. 새source equality1, 새normalizationpair1, APIguard12.
Production originalguard16, 발견한 unknownfield guard의 targetedrepair5.
N5:21 populations+freeelectron ledger,13charge rungs × CI/PI/RR=39directions.
원155checks와 C9영향6targetedchecksPASS;155replay0.
Mainworkerwall8.84398767s, independentwall2.053914436s. 이것은 speedup 측정이 아니다.
새ODE0, freshsourcequadrature0, empiricalrateevaluation0, historicalscience rerun0.
Main execution source identity:
c6174a7a78247a1ee89dfeb152444ba49e2094004926bfe0597eb613e30b7faf
현재guardedbindingSHA:
acedb6e893f08dc1207c6fc40a63af0f4d21480cbf226e0266b6d8f81b883401
각실행SOURCE_IDENTITY와 history/v1 원본을 구별하라. 최신코드로 과거receipt를 재서명하지 말라.

[재사용]
C23B science54477b285e0c712610453bca1408a076af43521d.
KC sourcea5c29ad4070acb931d92d2bec42a927a57f479ca의 KC4finiteatomic/KC7reference 재사용.
inputs/photoelectron_atoms.csv 1,681,578bytes, SHA256:
f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3
q_ij는 perabsorbingtarget/propersecond, K는 이미 bathframe eV다. 재boost하지 말라.
count=N_target_i*delta_tau*q_ij. Density/abundance normalization은 하나만 선택한다.
Frozen targets/volume/properduration의 first-order source predictor이며 daughter를 같은step에서 재처리하지 않는다.
Thermal baseNB,UB에는 resolved 새primaryelectrons를 중복합산하지 않는다.
Kc=chi*kB*Tcal과 FS10eV loweredge는 별도 경계, equality는thermal 소유다.
Source가 바뀐 freshinventory에서forward branch를 구성하며 일반유일성/continuation을 주장하지 않는다.
Tcal 변화는 count까지 포함한 caloric diagnostic; physical_heating/stopping_time/global_error_bound=null.
Sub10eV전량을 즉시heat로 처리하지 말라. 실제 Coulomb/neutral/atomic exchange 공급자가 필요하다.
N5 totalfreeelectron과thermalbath electron을 구분하라.
Energyowner=all_free_kinetic; recoil은명시적0도필수, missing값은0으로채우지않는다.
Isotope number quotient는같은bath에서commonG,energyquotient는epsilon^T G row일치가추가로필요하다.
Constantbindingoffset 조건의동치에는 rank(G)=n-1이필요하며 irreducibility가충분하다.

[배송본]
BASS_CR_C23C_CUTOFF_COVERAGE_DELIVERY_20261024T001759KST.zip
4,773,760bytes,316payload+manifest
SHA256 b299ecfc0fe06b47fa76557e9faf5a9a15f6f8e4a375f4c2256114e8980abdc9
Library libfile_d11c8a9f3e388191b86314203743c09e
Dropbox id:BSpOijBcT10AAAAAAD_6iQ
둘다 실제bytes재다운로드 SHA/size/CRC/member316 R3PASS.
Drive는단일create-new시도의ACK부재 UNKNOWN_NO_ACK, R3NOT_RUN.
정확한파일명+기존폴더의읽기전용reconciliation1회는0건이었다.
원격실패라고단정하지말고, 같은업로드를무작정재제출하지말라.
이후ack또는실제metadata에서ID가확인되면그ID의readback부터진행하라.
MainZIP는providerreceipt생성전동결됐다. 후속finaldocuments/terminal자료도함께사용하라.
delivery/restore_c23c.py는SHA검증한메모리bytes를BytesIO로읽고CRC/memberSHA를검증한다.
실제새디렉터리복원316개와복원된diskbyteshash까지PASS,science실행0.

[그림/문서]
최종선택은analysis/FINAL_FIGURE_RECEIPT.json의PDF4/PNG4다.
v2의90mmPDF하나는생성후bytes불일치가발견되어rejected로보존됐다.
v3의saveddata PDF교정과v4actualPDFreadback으로마감;원래읽었던render와byte-identical.
미세above-FS energyfraction3.630236936141936e-9는선형그림에안보이지만0이아니다.
교정caption은후속document에있으며숫자/그림/과학코드는변경하지않았다.

[최신조사범위]
이번intake시점7repo RESTheads1294,복구baseline1285대비+9/7changed/0removed.
OpenPRmetadata831,draft772,11pages완료;최근35PR상세metadata.
선택text42개397,536bytes Gitblob+sizePASS;N5추가donor11파일별pin도있다.
모든branch본문/모든backup내용을읽은것이아니다.
다른대화전체UNAVAILABLE, 검색snippets는대화원문복원이아니다.
외부host현재process/lease는UNOBSERVED.
HH83 PR140 head65c6751d363363cfc15eba0c7debf50eb493c1c9는S0sourcecheckpoint:
132rates/324steady/732transient NOT_RUN이다. Completion제목만으로완료판정하지말라.
REI220/BASS180 compact33mirror,대표raw4 PASS_SCOPED,전체127재감사아님.
최초127 JSON실패/재적분이력,C21O와RRDR/UVT/tolerance차이를보존하라.
62->33 대수축약을측정speedup으로부르지말라.
VigilODE P02C6FAIL,HE85/REI219의과거미완료campaign을유지하라.
Exa이번검색은402creditlimit;SciSpace검색과primary확인은수행했고Wolfram새7항등식0을확인했다.

[과거보존상태]
C23Bmain Drive1wP4AQgvZB_4c8YBV_iFp2mGi0_Fk2QRi는이번실제R3PASS(453payload).
이상태를C21O/C23A/C23Bfinaldocs의Drive로확대하지말라.
C21O초기권위C6b6db06e8148e6826a2d5bf7dbc53d362126ca62,
Df7ca6905729f7d8d36ca0605f7b1dd7ad5595819,Ra5e12c5f3e6d323e211d65fefad34060ec07eff0.
C21O45stress+6controls,z20->2,201savedtimes완료를재실행하지말라.
C21OoriginalmainDriveUNKNOWN_NO_ACK,originaldocumentNOT_RUN,recoveryZIPNOT_ATTEMPTED를유지하라.
NCP기존51재실행불필요. 전체archive삼중백업완료라고쓰지말라.

[물리/DAG]
Non-tiltedLRS,fullFrobenius,Pi_r=abs(Pgamma+Pnu),Pi_tot=abs(Pm+Pr).
Signed amplitudes/scalar norms/cancellation구분,atomicgasisotropicstress와별도nonbaryonicVlasov구분.
21 populations는n,H1,D,T,He3,He4,Li6,Li7의명시된전하상태다.
n/Tinitial0은선언inventory;absent species/rates를0으로대신하지말라.
C21O는prescribedUV/Tphoto+CaseARR->ne->photonThomson모델이다.
fullthermal/UV/stars/nuclear완료를주장하지말라.
N4connectorCOMPLETE_SCOPED,N5bookkeeping/coveragecontractCOMPLETE_SCOPED.
다음:finite-temperaturestopping/thermalexchange계약+actualatomicratecoverage
->에너지/입자/전하/핵종보존및유효T/E/omittedprocess/isotopequotient조건
->새구현->가벼운검증->새input/source/runID->실제resourcelease확인->실행->분석->게시/백업.
CPU55/coordinator보호,worker당1nativethread,create-onlyoutput을지켜라.
Fullnuclearhigh-energy/generaltriaxial/tilted/polarizedCMB는HOLD.
원nuclearnetworkPNG는NOT_RECOVERED_NOT_READ.
매단계EXECUTION|PUBLICATION|BACKUP|DAG를기록하고전체completionpercent는null로유지하라.
```
