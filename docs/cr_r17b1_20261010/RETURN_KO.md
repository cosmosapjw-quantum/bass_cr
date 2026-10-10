# R17 백업·게시 복구 및 R17B1 연구 반환

2026-10-10 KST. 담당 bass_cr만. R16B parent=997281e566a60c71554192a6d653aa82c29cd2f7. 새 branch=research/cr-r17-recovery-r17b1-20261010. 다른 repository 및 기존 branch의 rewrite/main merge는 없다.

## 1. 실제 복구

서로 다른 R17 두 원본을 SHA-256/CRC와 각 내부 manifest38·41파일로 확인하고 변경 없이 Drive·Dropbox에 create-only 저장했다. 둘은 같은 수식/파일의 두 직렬화가 아니므로 하나로 덮어쓰지 않는다.

- BASS_CR_R17_20261010_v1.zip:169120bytes,SHA256 f7ea6083d0e4b9e06bf59bbf8cd3f0fa449f7c5fea110672a883b455f1be3755. Volterra/direct-electron source bound≈1.7007493451e-18. Drive1Fs4RXZW_b2gLIgPAWM9oPyirI23fFh-1;Dropbox id:BSpOijBcT10AAAAAAD3tGg.
- BASS_CR_R17_CAUSAL_SOURCE_20261010_v1.zip:134977bytes,SHA256 b6b6f623f22f7fd2917f32c87d1f2bc92b3b3d6264599cd68a7414823c0c1dca. Prefix contraction/dynamic-density source bound≈2.1250340658e-18. Drive1g2wQ1oew9zfM297UsP710R3GuYf-0sqL;Dropbox id:BSpOijBcT10AAAAAAD3tGQ.

이번에는 최신 chronological causal-source handoff를 기준으로 후속 계약을 구성했다. 더 이른 작은 상계는 별도 유도로 보존하며 무효화나 독립 재증명을 하지 않았다. 네 provider 응답에서 ACK/name/size/path를 확인한 R1_DUAL_UPLOAD_VERIFIED다. 원격 checksum·full restore는 미수행이다. 원본 안의 WRITE_TOOL_NOT_EXPOSED/PENDING은 과거 seal 당시 상태로 남긴다.

RECOVERED_ARCHIVES.json commit0ea2fe590f824e838a1aa5b1cb765aa49bd7caef, 원 causal_source.py 게시commit3002786c23a29002e09e03d75bca4da7b59cce12. Core blob ac89ef8b184c29add44867a330ed7a466721e48a가 실제 시험 원문과 같다.

## 2. 새 R17B1: 전체 signed kernel에 필요한 수학적 전달

진행한 것은 실제6birth의 모멘트 결함·경계항·Peano norm 계산이다. 새 FT03 IVP/kernel/homotopy 계산이나 새 source tau upper를 보고하지 않는다.

원 source 구간 [a,b], h=b-a, x=(birth-a)/h, M=S*h로 정규화한다. L(f)=M int_0^1 f(x)dx-sum wi*f(xi)이며 부호는 continuous-minus-discrete다. f는 source homotopy mu_eta=(1-eta)mu_Q+eta*mu_S의 전체 coupled optical response K_eta를 eta에 대해 평균한 local kernel이어야 한다. eta=0 nominal 또는 frozen-gas kernel로 대체할 수 없다. 이 정당화는 아직 외부 전제다.

실제 binary64 source clock/weight box를 정확 Fraction으로 읽어

    d_k=M/(k+1)!-sum wi*xi^k/k!, k=0..3
    C_r(xi)=L((x-xi)_+^r/r!), r=0..3
    P4(t)=M*(1-t)^4/24-sum_(xi>t) wi*(xi-t)^3/6

를 계산했다. 이상적인 Gauss 노드로 교체하지 않으므로 d_k를0으로 강제하지 않는다. 완전한 piecewise-C4 partition과 내부 jump J_r가 주어지면 정확히

    L(f)=sum d_k*f^(k)(0+)+sum J_r*C_r+int P4*f_reg''''.

값 jump가 source atom과 만나면 left/right trace를 지정한다. 출력 노드 위의 derivative jump도 일반적으로 사라지지 않는다. 제조 rule M=1,nodes=(1/4,3/4),weights=(1/2,1/2),f=(x-1/3)+는 regular fourth derivative0이지만 L(f)=1/72다. 이는 FT03 결과가 아닌 실제 코드 반례시험이다.

## 3. 실제 계산 수치

3개의 원 source cell,6개 원 birth,144개 full subinterval에서 Bernstein convexity와 Fraction 다항식 적분으로 모든 weight choice의 Peano L1을 감쌌다. 표본점 extrema는 사용하지 않았다.

전체 u=birth/T 좌표의 동일 fourth derivative upper M4를 곱할 계수:

    C4_total <=2.5799877760925946815392074954550e-10 photons/H.

세 cell의 coefficient share=99.7753872361%,0.2223761682%,0.00223659572%. 이것은 true source error의 분담이 아니다.

같은 global-u 미분 convention의 anchor 계수 절댓값 합:

    d0:1.0106224076840892e-21
    d1:3.0632778689500903e-22
    d2:7.2197565033039291e-23
    d3:1.2363251688060138e-23 [photons/H].

실제6birth 위치에서의 potential jump coefficient 합:

    J0:3.1250000000000003e-6
    J1:1.5401702535614055e-7
    J2:7.1686462226547551e-9
    J3:2.6305685172750210e-10 [photons/H].

실제 jump가 비영이라고 관측한 것이 아니다. 정칙구간 전체 목록, 실제 anchor/jump 및 regular derivative upper가 없으므로 new_FT03_source_error_interval=null이다. API는 missing premise를 거절하며 boolean flag 자체는 수학적 전제를 증명하지 않는다.

설계상 최신 safe fallback2.125035e-18의90%를 smooth remainder에 배정하면 M4<7.412947912864e-9가 필요하고 다른 모든 항에10% budget이 따로 필요하다. 이것은 인증된 도함수가 아니라 앞으로 검증할 목표다. Local/global derivative는 (h/T)^r를 적용하고 factorial을 중복으로 나누지 않는다.

## 4. 새 검증 및 실제 실패

새 고유 Python tests19 PASS:1 assertion RED→GREEN,18tests-after. 독립80자리 direct-hinge 계산으로 실제 low moments48개·Peano L1 corner integrals12개 확인. Piecewise cubic+내부jump의 exact rational 사례64개 일치. Python6파일 syntax검사. 독립 full RHS backend/human/agent/proof-assistant는 미실행이다.

첫 fresh reproduce에서 INDEPENDENT.json이라는 로그가 같은 이름의 result를 덮어써 바이트 검사가 실패했다. child과학실행은exit0이고 stdout이 정본과 같았다. 로그를 *_RUN.json으로 분리한 뒤 새 빈 디렉터리에서19시험·실제계산·독립검사 전부 통과, 두 결과 JSON 바이트 일치. 원 입력과 수학 코드는 변경하지 않았다. 실패원문 보존.

부모 R16/R17/donor suite, 새 FT03 native/IVP/root/AD/원자provider는0이다. 새 계산은 모멘트 및 Peano/JUMP 계수와 조건부 변환이다. 실제 FT03 coupled-kernel 인증은 R17B2 OPEN이며 기존 source/time bound는 불변이다.

## 5. 실제 게시·재현 ZIP

새 core path research/cr_r17b1_20261010/source_peano.py, code commit22b317c2c1d63c62bdcb0bc468bb1edd16be1b11, blob af96a5b6d935c592dfb394379e603f24fbba54d7.

Full code/tests/selected source/result/report/failure logs:
BASS_CR_R17B1_20261010_v1.zip,40194bytes,27entries/26manifestpayloads,
SHA25695b2cba70b84c3cb53df6f5747504d48a82105389acc464e0421f4711ee11374.
Drive id1kuHg5j5AISsfWaM7yGVQwnSqFGL3kccS,parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ.
Dropbox id:BSpOijBcT10AAAAAAD3tPA,path /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_R17B1_20261010_v1.zip.
Both ACK/name/size verified; R1_DUAL_UPLOAD_VERIFIED. Remote checksum unavailable, full restore not performed. Git carries core/summary/return/handoff; full standalone artifacts are in this ZIP. It needs no donor network access for reproduction once fetched. Run python -B reproduce.py --verify-only, or --output NEW_EMPTY_DIRECTORY. No old science suites.

Next: R17B2 arbitrary-birth coupled optical kernel, full source homotopy and derivative jumps, first source cell prioritized. Same CDF/old tau computations should not be repeated. CR_OFF_FASTEST,precision_atomicPARKED,HH_ACTIVE,G02UNRESOLVED,all_boundOPEN,b_gridNO_GO,physical/productionHOLD and ownerACK/observer_tail=null retained. Other repos read-only.

Primary mathematical background: NIST DLMF sections3.3 and3.5. Actual coefficients and generalized finite-moment+jump identity here are directly calculated/derived, not a claim that DLMF certifies FT03.
