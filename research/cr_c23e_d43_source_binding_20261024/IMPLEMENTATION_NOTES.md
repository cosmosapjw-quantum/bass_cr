# C23E V2 구현·실행 반환 — 독립 Astra 검토 대기

## 실행 범위 및 실제 skill binding

Controller가 동결한 FROZEN_CONTRACT.md V2를 그대로 구현했다. intake/bass_AGENTS.md,rei_AGENTS.md,policy/PHYSMATH_MAIN.md,THEORY_LOOP.md,CODING_LOOP.md를 읽고 C5–C8 구현/검산/보존 범위로 수행했다. native delegated executor n5_metadata_intake이며 requested role은 lower-tier coder다. 실제 runtime model identity는 별도관측되지 않았으므로 추정하지 않는다. 물리판정·C9·게시권한은 root에 있다.

V1 hdx.py는 history/superseded_v1/hdx.py로 보존했다. V1 ODE12+4와 geometric-mean 모델 실행0. 기존 H source,ISO-COUPLE,PHYS79,atomic155+6 suite 재실행0.

## 코드와 입력 매핑

- implementation/d_binding.py: C23B narrow-band GL와 boundary transfer, conditional D43K CX 추출, C22A VF RR 재사용,21population 및thermal/fast pool instantaneous source.
- implementation/validate_d_binding.py: exact input identities,새D전구간quad3개,narrowband8/16/32각3개,18pointstate,integerconservation,guard와zero-defectcontrol,저장atomfilterdiagnostic,저장결과그림.
- implementation/dispatch_d_binding.py: 실제preflight,cooperativelease,단일worker/affinity/thread/caps,create-onlyrun.
- implementation/reuse/c23b/: exact spectral provider/CONTRACT/Verner 및3PW19table.
- implementation/reuse/c22a/rr_energy_moment.py, reuse/c21o/vendor/atomic/rr_table.dat: exact원문. WU79 d_cx_rates의detailed_balance분기를attributed소규모추출했다;다른He/Lipotential은가져오지않았다.
- inputs/C23B_CASES_EXACT.json: intake원문에서transportnewline1개를제거하여blob61bcbc0b44206f496534da6bdffcdfe1731ad063/25699bytes확인. intake원본은불변.
- savedatoms: 계약경로1681578bytes/SHAf5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3확인. 읽기/filter/sum만했다.

reuse/INTAKE_MANIFEST.json 및run/IMMUTABLE_READBACK.json에 exact source결속. 실행3source와계약SHA는EXECUTED_SOURCE_MANIFEST.json. Import-time과학/쓰기는없다.

## 실제 실행

명령: `python cr_n5_rate_domain_20261024/implementation/dispatch_d_binding.py`

한번primary: runs/C23E_D43_SOURCE_BINDING_20261024T021612Z_v1

- exit0;104checks모두통과.새pointsource18,newDtargetintegrations3,bandorders9(3z×8/16/32),ODE0,parentrerun0,benchmark0.
- workerCPU8,coordinator별도CPU;CPU55제외.OMP/OPENBLAS/MKL/BLIS/NUMEXPR/VECLIB1.로컬one-workerlease획득후동기실행/반환해제.
- capCPU60s/wall180s/addressspace1GiB;실측childCPU2.161932s/wall2.1714153429929866s,maxRSS122500KiB. RESULT내부CPU1.630962739s/wall1.638411324s와구분한다(수입/import포함여부).
- inheritedknownCPU13.331329114s+이번child2.161932s=15.493261114s,trackedlineagelowerbound.미측정CAS/과거전체/금전/잔여는null이며예산reset없음.

PREFLIGHT.json은actualaffinity,cgroupCPU/memory,meminfo,processworkload를보존한다.단일rawattempt만있고repair/rerun0.

## 관측 결과

- BandGL8/16/32최대상대차5.626252649309911e-16(기준2e-10).
- BoundaryD와독립Dquad최대상대차1.7485509595587793e-15(기준2e-11).
- Photoenergy최대상대잔차8.07907976464989e-17(기준5e-14).
- Floatingnuclideresidual0;pool정규잔차최대1.1401679038436815e-16;totalenergy6.824722606685112e-17;statepotential1.25791865881435e-16(모두기준2e-13).
- 각z의GammaD/GammaH−1은−0.00123905641117,−0.00124477617594,−0.00125167647917.
- 단순oldatomthresholdfilter의count상대오차는−0.00144346275977,−0.00145010031845,−0.00145810472575.이는새thresholdresolutiondiagnostic이며parent실패판정이아니다.kinetic상대오차약−2.01e-7…−2.06e-7.
- missing21key,mixedpotential,wrongpoolsum,Tdomain위반/NaN이명시거부되었다.3/200000Kdomainendpoints확인.동일potentialcycle은exactFraction대수0으로확인하고floatingstatecontraction은별도보존했다.

수치결과는모형범위에서의관측이다.conditionalPI/RR ledger이며microscopicMilne/LTE/물리오차개선/empiricalisotoperesolvedD/finite-mass정밀도에대한새판정은하지않았다.thermal/fastsource만구분하며stopping/secondaryheat0을가정하지않고미계산으로남긴다.다른species는stoichiometricspectator이며physicalrate0으로선언하지않았다.

## Raw 및 그림

run에 SOURCE_z.json(구간별quad값/error estimates포함),SOURCE_DIAGNOSTICS.json,POINT_INPUT.json,POINT_SOURCES.json/CSV,BAND.csv,RESULT.json,rawstdout/stderr,resource/identity/outputmanifest를보존했다. figures/D43_source_binding.png/.pdf는동일run그림의복사다. PNG를실제열어2panel,축/legend/conditionallabel,세z노드와추세를확인했다.종속오차·상속parent오차·quadreportederror는물리uncertainty/globalbound가아니다.

EXECUTION:primaryboundedcheckscomplete;PUBLICATION:NOT_RUN;BACKUP:newartifactlocal/root담당;DAG:C23Echildreviewpending/fullN5OPEN.global_error_bound/global_completion_fraction=null.원격쓰기0.

## 단일 승인 delivery-only repair

Fresh Astra finding에따라원실행3script를run/source_snapshot/에원bytes/hash로보존하고배포본만수정했다. validate는inputs/C23B_CASES_EXACT.json과inputs/photoelectron_atoms.csv의ROOT상대경로를읽고검증하며inputs에쓰지않는다. exactsavedatoms를inputs에포함했다. dispatcher의모든변경/실행은main와__name__guard뒤로옮겼다.수학/계수/허용오차변경0.

Targeted명령: `PYTHONDONTWRITEBYTECODE=1 python cr_n5_rate_domain_20261024/implementation/verify_delivery_repair.py`.

29개delivery-only확인PASS:3moduleimport무쓰기/무spawn,2exactinputblobidentity,create-onlycollision은spawn전에FileExistsError,기존raw및3source원bytes보존,원FROZEN_CONTRACTSHA불변. numericalmain/sourcequad/pointsource호출0;원104checks재실행0. 새배포hash는run/delivery_repair/DELIVERED_SOURCE_MANIFEST.json,원실행hash는EXECUTED_SOURCE_MANIFEST.json및source_snapshot/MANIFEST.json으로분리한다. Unifieddiff와TARGETED_REPAIR_RECEIPT.json도동일directory. verify_delivery_repair.py는이한번repair전용이며동일create-onlyreceipt가있으면반복하지않는다.
