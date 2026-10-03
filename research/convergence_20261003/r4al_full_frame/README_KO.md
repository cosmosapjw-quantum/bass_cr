# R4AL: 전체 18채널의 H1 Gram / weak norm tube

현재의같은유한s+p candidate, b=2a0,v=2.00798106651023a0/ta, z=-32a0의두기존window에한정한다. 새cross/radial/M9/oldR8평가0, 완료과학suite반복0.

- H=a0/64: lambda_min(S18)>=0.944949461133, cond2<=1.116515308239.
- H=a0/128: lambda_min(S18)>=0.971145650753, cond2<=1.059423319715.
- 전체weakK의zero-reference상계는60.426980672353Eh 및59.980131124719Eh. 유효하지만작은bridge오차가아니다.
- physical_bridge_upper=null; full_stencil_total_upper=[null,null]; G02UNRESOLVED/productionHOLD/capturefalse/all_boundOPEN/b_gridNO_GO.

순서:기존R4ABexactG/T+R4AF중심C구간을hash로묶고,1DHardy와full-multipletH1translation으로uniformGram하한을얻었다. originalnorm/offdiagonal/ETF/epoch를보존한다. exactfinitecandidate와physicalbasisaccuracy를구분한다.

새시험43건,독립산술검토211조건이통과했다. 독립검토의첫고유값표시인덱스오류는수정·이력보존했으며생산certificate는바뀌지않았다. 고유값floating진단이uniform상계의근거가아니다.

Git게시에는실제full_frame.py/run_r4al.py와새시험을포함한다. completeinputs/results/DB/실행계약은양쪽cloud의재현package에있다. Gitcodecoverage와완전한archive를구분한다. 실행은이미완료했으므로다시run하지않는다.

다음로컬: R4AM_WEAK_K_CONTACT_CELL_PROVIDER_AND_REMAINDER.
다음외부: R4AH_m64,기존코드를실제NCP환경에서1점만승인/실행/반환.
rei_bianchi의배경·재이온화동역학은이곳에서추가하지않는다.
