# bass_cr NCP R17B2 반환

결과는 **NO_CERTIFIED_SOURCE_SHARPENING**이다. R17B2 full-coupled source RHS/adjoint와 고차 birth 연산 backend를 구현했고 공통 값 tube 및 coarse K0를 감쌌다. 고차 kernel 인증은 아직 완료되지 않았다.

R16B parent=997281e566a60c71554192a6d653aa82c29cd2f7, 복구 HEAD=eb692c19c7cef3e3721f1e044ca3d41151d9309d. 새 worktree /root/bass_cr_ncp_r17b2, branch research/cr-r17b2-source-kernel-20261010. 기존 main/복구 branch rewrite와 다른 repository mutation은 없다.

최신 causal ZIP(134977 bytes,b6b6f623…c0c1dca) 및 R17B1 ZIP(40194 bytes,95b2cba7…ee11374)을 Dropbox 원본에서 실제 복구했다. SHA256/CRC 및 manifest41/26payload 일치: 이번 두 input의 restore는 R3다. 더 이른 Volterra(169120 bytes,f7ea6083…be3755)는 별도 유도·기존 receipt로 보존했고 내려받거나 같은 이름 patch와 합치지 않았다. 기존 dual-provider R1 receipt의 의미를 R3로 바꾸지 않았다. 모든 전체 SHA는 SOURCE_BINDING/RECOVERY_INVENTORY에 있다.

실제 companion 분포 μη=(1−η)μQ+ημS와 continuous-minus-discrete 부호를 유지한다. 초기 gas/photon/energy, 동적 밀도·redshift, CaseA CI/RR/twoDR, 여섯 birth와 weight box를 고정했다. Source mass mismatch를 삭제하거나 source 질량을 정규화하지 않았다. 임의 b의 probe survival, E(t,b), 비광전 gas Jacobian, 현재 photon response 및 모든 이전 출생의 survival-memory feedback이 연산자에 들어간다. 기존 7-cohort adjoint 보간은 사용하지 않았다. Source/companion backward adjoint 및 0–4차 birth Jet RHS도 구현했다.

전 η∈[0,1]/원 weight family의 gas self-map·contraction이 새 directed Decimal80 및 독립 MPFR256 계산에서 확인되었다. contraction upper≈0.0013409569883603781043916500218235152238766554058234756067114210591721662330939803, coarse K0 radius≈7.9979003218239623819407999100535742283097431834742794867923507708725517508768690E-12. 이것은 실제 source error나 K4 인증값이 아니다. 임의 b kernel의 값에 대한 매우 보수적인 외측 enclosure다. 수식과 whole-domain 부등식은 THEORY.md, 정확 결과는 results/BOUNDS_CANONICAL.json에 있다.

**정확한 blocker:** 움직이는 birth 하한 u=b/T에서 평가한 resolvent의 혼합 time/birth derivative flow와 companion adjoint 분포의 derivative tube가 없다. 그러므로 anchor K1..3, 각 regular piece K4, 실제 모든 one-sided jump0..3을 감싸지 못했다. PARTITION_INVENTORY는 source atom/원 output·proof/source 경계 후보만 열거하며 완전성 증명이 아니다. 빠진 jump를0으로 채우지 않았고 boolean/nominal η=0/frozen gas로 승인하지 않는다. require_proof는 실제 proof producer가 생기기 전 모든 인증 요청을 fail-closed 거절한다.

첫 source interval[0,885031998.4547119]에 우선순위를 두었다.99.7754%는 정칙4차미분 계수의 비중이다. C4≈2.579987776092595e-10는 global-u K4 bound를 곱하는 계수이며 illustrative7.4129479e-9는 아직 얻지 못한 목표다. local 미분은(h/T)^r 변환하고 moment/hinge factorial을 다시 나누지 않는다. 나머지 두 source interval은 기존 causal whole-macro budget에 그대로 남긴다.

새 검증24tests PASS, 잘못된 source bytes/clock·mass erasure·local/global·누락 kink·nominal-only·frozen gas·lost memory/companion의9mutants 모두 해당 assertion으로 거절. 독립 RHS4값/Jacobian16항, nonphoto jets20개, probe jets5개 및 MPFR interval primitive400개 확인. Whole tube MPFR 대조25개. 독립 전방DOP853/후방RK45 대조30cases의 최대 상대차=1.352981e-10. Gauss8/16 companion 근사의 최대 kernel 상대차=7.799427e-11. **유한 η/출생/companion quadrature 진단이며 전체 구간이나 η 적분의 증명으로 쓰지 않는다.** 물리 source-error sign을 주장하지 않는다.

새 빈 디렉터리 재현은 총7commands 모두 exit0, bounded/independent JSON 바이트 동일. 실제 cgroup ancestor quota는 CPU/RAM max, affinity64CPU. Coordinator CPU0, worker CPU1, memoryreserve20GiB, worker RLIMIT_AS=111268560896bytes; 최대 RSS=77720KiB. BLAS/OpenMP1thread, fast-math/native flags 없음, 병렬 floating reduction 없음. 기존 R16B/R17/B1 계수·CDF/donor suite 재실행0. 최초 python 별칭/기본 scipy 부재, import RED, literal/family-sign 시험 오류와 모두 실패한 mutant 로그를 보존했다.

새 source interval/null, 새 combined interval/null. 기존 최신 causal exact rational radius 및 R16B time/기존 combined interval을 RETURN.json과 원 inputs/CAUSAL_RESULT.json에 변경 없이 보존했다. 이번 새 source/time 조합은0회다. 작은 새 구간을 인증하지 못했으므로 기존 경계를 재계산하거나 바꾸지 않았다. 더 이른 Volterra source proof도 별도로 유지한다.

Physical/production HOLD, CR_OFF_FASTEST, G02 UNRESOLVED, b_grid NO_GO, precision_atomic PARKED, Grackle owner-input blocker와 ownerACK/observer_tail=null 유지. REI/BASS_HE/WU088_HH suite는 시작하지 않았다.

실행: 별도 venv에 requirements.txt를 설치한 뒤 python3 -B reproduce.py --verify-only 또는 --output NEW_EMPTY_DIRECTORY. 실패 후 같은 output을 덮어쓰지 않는다. ZIP 봉인·Git non-force push·Drive/Dropbox create-only upload의 실제 결과는 봉인 뒤 DELIVERY_RECEIPT.json에 남긴다. ACK/name/size의 R1 backup은 remote full restore가 아니다.
