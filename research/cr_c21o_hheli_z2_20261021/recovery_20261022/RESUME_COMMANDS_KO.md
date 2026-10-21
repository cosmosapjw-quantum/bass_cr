# 복구·후처리 실행 및 후속 handoff

## 배송 묶음만으로 복원

새 recovery ZIP을 빈 폴더에 풀면 `archives/`, `recovery/`가 있다. 그 최상위에서:

```bash
python recovery/restore_c21o.py \
  --content archives/BASS_CR_C21O_HHELI_Z2_RESEARCH_DELIVERY_20261021T154615Z.zip \
  --document archives/BASS_CR_C21O_DOCUMENT_CLOSEOUT_20261021T155819Z.zip \
  --authority archives/C21O_FINAL_AUTHORITY_20261021T1603Z.json \
  --output ./restored
```

목적지 `./restored`는 존재하지 않아야 한다. 정확한 archive pins와 manifest/CRC/Git blob을 확인하고
327개 연구 파일을 복원한다. 과학적 적분은 실행하지 않는다. Python dependency는 복원된
`research/cr_c21o_hheli_z2_20261021/requirements.txt`에 고정되어 있다.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
C21O=./restored/research/cr_c21o_hheli_z2_20261021
python "$C21O/analyze.py" \
  --grid-run "$C21O/runs/c21o_grid45_v1" \
  --control-run "$C21O/runs/c21o_controls6_v1" \
  --output ./analysis_new
```

`./analysis_new`도 새 경로다. 저장된51개 결과를 읽어15개 출력을 생성한다. 이번 재개 환경에서는
15개가 모두 원 `analysis_v2`와 byte-identical이었다. 환경이 달라지면 그림 bytes까지 같다고 미리 보증하지 않는다.
현재 이 repo의 HEAD를 직접 받은 경우 C21O 경로에서 동일 명령을 실행하면 되고, archive 복원은 생략할 수 있다.

## Codex handoff — 복사 가능

```text
cosmosapjw-quantum/bass_cr, branch research/cr-c21o-hheli-z2-sandbox-20261021, draft PR96을 사용하라.
원 과학 content6b6db06e8148e6826a2d5bf7dbc53d362126ca62,
기존 documentf7ca6905729f7d8d36ca0605f7b1dd7ad5595819를 보존하라.
recovery_20261022의 기록과 external final authority로 최신 recovery/document head를 대조하라.
51개(45grid+6controls) z20->2 계산은 완료됐다. 새 ODE를 복원 확인 목적으로 재실행하지 말라.
원본ZIP을 restore_c21o.py로 새경로에 복원하고 필요시 analyze.py만 실행하라.
새 복구 영수증은 327researchfiles와 15analysisoutputs의 byte identity를 확인했다.
C21O는 prescribedUV/T photo+CaseA_RR -> ne -> photonThomson LRS 조건부 모델이다.
Matter는 nonbaryonicVlasov, atomicgas는 isotropicclosure; photon/neutrino stress를 별도로 보존한다.
Full Frobenius와 signed amplitude를 구분하고 Pi_tot는 tensor합 뒤 norm을 취하라.
global_error_bound=null. 완전한 thermalUVstars/nuclear network 완료를 주장하지 말라.
외부 REI220/BASS180 compact127+full62oracle2는 별도UV/T/RRDR/tolerance 모델이다.
두 paired raw의 재비교를 수용하되 C21O ensemble에 합치지 말라. 최초외부127의 serializer실패/재실행도 보존하라.
새 물리 입력을 받았을 때만 새source/input/run으로 실행하라.
NCP에서는 affinity,cgroupquota,memory,CPUusage,lease,disk,inode를 새로 확인하고 CPU55+coordinator를 보호하라.
Worker1thread,유휴CPU와RAM이 허용하는만큼만 dispatch,다른owner의 process/file/lease를 변경하지 말라.
Drive 원main 요청은 역사적·현재 두 시도 모두 UNKNOWN_NO_ACK; exact-name 확인없이 재업로드하지 말라.
```

## 다음 대화 handoff — 복사 가능

```text
$physmath-research-loop로 BASS_CR C21O 이후 작업을 이어가라.
먼저 현재ref와새 실행반환을 대조하라. 완료된 C21L81,C21M/N125+offgrid4,C21O45+6 및 채택외부pilot을 재실행하지 말라.
repo cosmosapjw-quantum/bass_cr,branch research/cr-c21o-hheli-z2-sandbox-20261021,PR96.
과학content6b6db06e8148e6826a2d5bf7dbc53d362126ca62,
원documentf7ca6905729f7d8d36ca0605f7b1dd7ad5595819,
sourceidentityc60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f.
2026-10-22 KST 재개에서 Library3파일 다운로드SHA검증,327연구파일복원,
후처리15출력 전부 byte-identical,신규ODE0을 달성했다.
recovery_20261022/RECOVERY_REPORT_KO.md,EXTERNAL_INTAKE.json,REANALYSIS_BYTE_COMPARISON.json,
DRIVE_REPAIR_RECEIPT.json과 최신 external FINAL_AUTHORITY를 읽어라.
새REI220/BASS18062->33compact127+oracle2를source/receipt와대표raw4개로 수용했다.
이 모델의5–200eVUV,100–12000KT,RR/DR,tolerance는C21O와다르며 전체127raw 재감사는NOT_RUN이다.
다른새REI218,REC119,HH133,HE85는 intake의정확한수용범위를 유지하라.
다음 과학 단계는 full thermochemical/radiative closure·rate coverage 계약과 누락반응의지배성평가다.
이 단계가 명시적으로 선택되면 Exa/SciSpace 원전과 Wolfram 검산을 사용해 진행하라.
새case는 새contract/source/run에만 쓰며 isotope-specific/nuclear변경시 compact불변부분공간을 재판정하라.
H1/D/T/He3/He4/Li6/Li7+n21populations가 모든가능핵종/반응 완료를 뜻하지 않는다.
원네트워크PNG는 이번20개첨부에 없었다. 접근불가대화는UNAVAILABLE이다.
mainZIP SHA5741bcac7943e91cdacd8ca15cd8c34ff8a83b7b08b6d8a6bfad31cdb5b2c781,
docZIP SHAa8cf3cd2431332becd39465010e121ebc4ff172feab81a81c9da948883e79b1c.
원Library mainlibfile_c44d3555829481919287affc7c541856/doclibfile_41f901d7b87c819199787964c4e6bcf4,
Dropboxmainid:BSpOijBcT10AAAAAAD_hoQ/docid:BSpOijBcT10AAAAAAD_how.
Drivefolder1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy,mainUNKNOWN_NO_ACK;재시도 전 정확한 이름과 직접 폴더 목록을 확인하라.
매 단계 EXECUTION|PUBLICATION|BACKUP|DAG와 다음작업을 구분하고 global_error_bound=null을 유지하라.
```
