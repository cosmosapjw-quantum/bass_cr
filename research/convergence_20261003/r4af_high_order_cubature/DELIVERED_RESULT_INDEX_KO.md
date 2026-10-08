# A2 / R4AF: 한 geometry의 고차 검증 cross-S cubature

2026-10-03 KST. `HIGH_ORDER_POINT_ENCLOSURE_TARGET_MET`.

동일 finite s+p candidate17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef, b=2a0,100keV/u,z=-32a0의 실제 저장 epoch에서 cross overlap을 새 tensor Gauss-Legendre/complex ellipse remainder 및256-bit outward GMP integer arithmetic으로 감쌌다. 새 방법으로 기존 한 geometry를 평가했으며 완료된 R4AE range method나 M9 jet을 재실행한 것이 아니다.

## 실제 결과

- 정확 dyadic midpoint의 full-cross Frobenius 반경 <=2.158e-20.
- 별도 저장 FP64 midpoint의 자체 오차 반경 <=2.129e-19.
- 사전 point 목표1e-16 통과. native/node/누적 반경 <=5.290e-38.
- analytic component의 보수적 full-cross L1 상계 <=9.169e-20.
- 기존 저장S의 TP/PT cross 절대차는 [2.3283808711e-16,2.3285104616e-16]에 포함된다. 이는 같은 actual epoch의 finite-candidate math quantity이며 fullS의 intrinsic Gram 오차를 포함하지 않는다.
- 모든1229개삼각형을 버리지 않고 추가 subdivision 없이 적분했다. 차수32:22,40:728,48:453,56:26. Tensor evaluation nodes2312576.
- 실제 geometry1개, 새 M9/window jet0,D0,V_other0,old six-block solver0,old R8matrix0,historical suite0.
- 성공1회와 실패preflight1회. 최초I+C adapter오류는Gauss평가전 발생했고 oldsource/contract/FAILURE를 보존했다. 같은 수학식의 operand order만 수정한 새 v2 context에서 완료했다. tolerance 변경/자동retry0.
- 새 변경영역38tests 통과. 읽기전용 독립산술108077조건 중99549개는cell별81성분 Gaussian부등식이다.176rootbrackets, native exact endpoint합, Frobenius제곱부등식, seal/pins/TP/PT거리도 확인했다. 별도인간/에이전트검토나 proof-assistant검증은 아니다.
- wall523.105253577s; coordinator maxRSS304044KiB; reported child maxRSS204164KiB. child ru_maxrss를 순수kernel memory나workers합으로 해석하지 않는다.4CPUquota/4GiB,3single-coreworkers. NCP64 scaling 증거가 아니다.

## 방법과 의미

공식 FLINT acb_calc 문서의 Gaussian ellipse bound 64M/[15(rho-1)rho^(2n-1)]를 tensor functional 항등식으로 합성했다. 각 variable의 복소타원/다른variable의실수구간에서 magnitude와pole회피를확인했다. target conjugation은상수계수에만적용한다. 원점u/r정확소거,entire-Q Phi,affineR vertex와signedJacobian을보존한다. SciPy/mpmath roots는제안만하며 exactrational Legendre부호변화와disjointbracket으로근을인증했다. quadrature-order차이를harderror로쓰지않는다. FLINT는설치/실행되지않았고GMP자체구간코드가실제runtime이다.

정확한 수치상계는 패키지 results/run_v2/S_ENCLOSURE.json 및 RESULT.json, FP64반경은 results/INDEPENDENT_REVIEW.json이 정본이다. 현재 한 중심점은 R8 shifted sample이 아니다. 이번 반경을 다른10개 shifted geometry로 복사하지 않는다. 전체stencil total_upper=null이며후속C0/physicalsource gate를승격하지않는다.

R4AE의M9와Peano상계는 원본 WINDOW_JET SHA256 95df9f4ba47056e7d79a72dd95fb4ad09996cac7f8338122981e45bb80c01daf로 보존했다. 새 DBv18 SHA256 2b857a1558c166b9bff0847850efc320d4423ccc2409fec0caa3e51501594ed9,8339456bytes. v17view 전체와 다른12gap행은동일하다.

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. A2는 PARTIAL_SHIFTED_STENCIL_AND_CONTINUOUS_OPERATOR_OPEN다. Bianchi재이온화목적의scoped 원자source 연구이며포획count를자유전자/heat로대입하지않는다.

## 실제 완료한 이중백업

BASS_CR_R4AF_HIGH_ORDER_CUBATURE_PACKAGE_20261003_v1.zip
bytes16541908
SHA256 dde12ae9bd21a7f9129eb59829238fa72d5d8a32e0a290d1cb500e4ceb3c22a7
Drive ID 1MSBW4NUaPE71OFjFtAH60Q_TUsRsOEIA
Drive parent 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
Dropbox ID id:BSpOijBcT10AAAAAADxoFA
Dropbox directory /bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/

두provider의완료ACK/ID/name/size를확인한R1_UPLOAD_VERIFIED다. 원격checksum은반환되지않았고R4AF RESTORE_VERIFIED=false다. LocalZIP108members CRC와107payloadSHA를확인했다. source/test/input/native/완료결과/계약/DB/derivation/실행반환지침을모두포함한다. 약99MB의역사archive는중첩하지않고정확한parentref로참조한다.

## 게시 coverage와 다음 단계

이번 Git commit은 결과/상태index와작은byte-verifier만게시한다. publication/CREATE_ONLY.patch의28개source/test/계약/doc를개별Git작업트리에적용하는작업은아직미완료다.그patch는격리디렉터리에서28파일의바이트일치까지확인됐으며양쪽cloud의완전한ZIP에있다.전달인덱스게시를fullsource-treesync라고부르지않는다. oldR4AA379/R4AD/R4AE mapping도별도다. 새index파일은그28mapping과겹치지않는다.

다음한node는 R4AG_SHIFTED_S_CERTIFIED_STENCIL_ASSEMBLY_CONTRACT다. 두고정R8window의unique10shifted입력을회수하고새batchadapter,epoch사상,정수구간stencil합산과실행계약부터닫는다. 초기새crosscap0. 큰10point평가는완성코드와실행계약을NCP/localCodex로넘길수있다. M9/현재point/oldR8를다시돌리지않으며새source/domain/pole를검사한다. 상세지시는ZIP의NEXT_HANDOFF_KO.md와contracts/NEXT_R4AG.json에있다.
