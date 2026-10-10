# R17B1: 실제 finite-birth 모멘트 결함과 jump-aware 광학 source 오차 전달

연구일: 2026-10-10 KST. 담당: bass_cr만. 상태: `EXACT_SOURCE_COEFFICIENTS_AND_CONDITIONAL_KERNEL_TRANSFER`; 새 FT03 source 오차 인증구간은 아직 없다.

## 1. 먼저 완료한 백업·게시 복구

서로 다른 두 R17 원본을 보존했다. `BASS_CR_R17_20261010_v1.zip`은 Volterra 및 직접 전자투영 경로로 source upper 약 1.7007493451e-18을 보고한다. `BASS_CR_R17_CAUSAL_SOURCE_20261010_v1.zip`은 prefix contraction과 동적 밀도 경로로 약 2.1250340658e-18을 보고한다. 이름의 R17A가 같다는 이유로 두 유도나 파일을 동일시하지 않았다. 원본 SHA/CRC와 manifest 38개·41개를 각각 확인하고 변경 없이 Drive와 Dropbox에 create-only 백업했다. 완료 ACK·ID·name·size를 모두 확인했다. 새로운 원격 checksum과 전체 restore는 하지 않았다.

최신 chronological handoff인 causal-source 패키지를 이번 인터페이스 기준으로 택했다. 더 이른 작은 상계는 역사적 별도 유도로 보존했으며, 이번에 무효화하거나 새로운 독립 재증명을 하지 않았다. 종전 원본 안의 WRITE_TOOL_NOT_EXPOSED/PENDING 기록은 당시 상태이므로 바꾸지 않았다. 실제 복구 상태는 새 detached receipt와 Git RECOVERED_ARCHIVES.json이 정본이다.

Git branch `research/cr-r17-recovery-r17b1-20261010`은 R16B HEAD `997281e566a60c71554192a6d653aa82c29cd2f7`에서 만들었다. 복구 manifest와 원본 causal_source.py를 먼저 게시했으며 core Git blob ac89ef8b184c29add44867a330ed7a466721e48a가 봉인 bytes와 일치했다. 다른 저장소나 기존 branch를 수정하지 않았다.

## 2. 다음 연구에서 계산한 것

새 연구는 기존 상계를 또 적분하는 대신, 임의 birth 시각의 coupled optical response K에 원 Gauss2 source를 적용할 때 필요한 오차 전달식을 구성한다. 이상적인 대수적 Gauss 노드로 저장 시각을 교체하거나 저차 모멘트가 정확히 소거된다고 가정하지 않는다. 실제 6개 birth, 3개 source 구간, 원 weight box를 유지한 정규화 모멘트 결함·Peano kernel·내부 jump 계수를 계산했다.

모형 기준은 그대로 FT03 첫 macro t∈[0,1.25e9] proper s, prescribed FLRW, HH/RCT/CR OFF다. 하지만 이번에는 FT03 RHS/IVP/AD나 source homotopy를 실행하지 않았다. 선택 입력은 BRIDGE14 내부의 실제 BRIDGE10_EVENTWISE_CONTRACT.json이며 BIRTH_PLAN.json으로 bytes 그대로 복사했다. 파일 SHA는 SOURCE_BINDING.json에 고정했다. 기존 R16B 시간구간도 변경하지 않았다.

## 3. 유한 source 차이를 다루는 정확한 목표

두 source measure를 μS(db)=S db와 μQ(db)=Σwj δbj(db), ν=μS−μQ로 둔다. S는 원 binary64(5e-15), weight와 시각도 원 정확 binary64 realification이다. 매개변수 η∈[0,1]에 대해 μη=(1−η)μQ+ημS를 사용한다.

모든 η에 대한 양의 공통 해 영역과 source 방향 미분의 존재, 미분과 목표적분 교환이 별도로 정당화되면

    τ(μS)−τ(μQ) = ∫0^1 dη ∫ Kη(b) ν(db).

Kη는 gas feedback, 기존 photons의 변분, probe photon의 survival 및 E(t,b)=Eb exp[−H(t−b)]를 포함하는 완전한 response다. R16B의 7-cohort adjoint를 arbitrary birth b에 보간한 값이나 frozen-opacity kernel로 바꿀 수 없다. 이번 계산은 이 조건을 증명하지 않으며 명시적 외부 전제로 남긴다.

각 원 source 구간 [aj,bj]에서 h=bj−aj, x=(b−aj)/h를 사용한다. 이 구간의 연속 source mass M=Sh이고 실제 노드는 xi=(birth_i−aj)/h다. homotopy 평균을 포함한 커널을 f(x)=∫0^1 Kη(aj+hx)dη로 정의한다. source 오차 functional은

    ℒ(f)=M∫0^1 f(x)dx − Σ wi f(xi).

질량을 정규화하지 않는다. f의 단위는 τ/(photons/H), ℒ(f)는 무차원이다. x 및 전체 u=b/T는 무차원이며, local r차 미분은 (h/T)^r 배의 global-u 미분이다.

## 4. 실제 모멘트 결함과 경계항

저차 모멘트 결함을

    d_k = M/(k+1)! − Σ wi xi^k/k!,  k=0,1,2,3

로 둔다. 이상적인 2점 Gaussian rule이면 모두 0이지만 현재 저장된 시각과 weight box에서는 이 값을 실제로 평가해야 한다. 특히 mass mismatch d0도 삭제하지 않는다.

구간 내부 ξ에서 f의 r차 도함수 jump를 Jr=f^(r)(ξ+)−f^(r)(ξ−), r=0..3으로 두고 Hr(x;ξ)=(x−ξ)_+^r/r!를 사용한다. jump의 구적 계수는

    C_r(ξ)=M(1−ξ)^(r+1)/(r+1)! − Σ_(xi>ξ) wi(xi−ξ)^r/r!.

r=0이고 ξ가 원자 노드와 같으면 f(ξ)의 왼쪽/오른쪽 trace 선택이 추가로 필요하다. API는 이를 명시적으로 받는다. r≥1의 hinge 값은 ξ에서 0이다. 단지 ξ가 quadrature node에 있다는 이유로 jump 계수가 사라지지 않는다.

완전한 정칙구간 목록과 piecewise C4 전제가 주어지면, Taylor 적분나머지와 각 jump를 분리하여

    ℒ(f)=Σ_(k=0)^3 d_k f^(k)(0+)
          + Σ_(ξ,r) Jr C_r(ξ)
          + ∫0^1 P4(t) f_reg''''(t)dt,
    P4(t)=M(1−t)^4/24 − Σ_(xi>t) wi(xi−t)^3/6

를 얻는다. 첫 두 항은 부호 있는 anchor·jump 전달이고 마지막 항만 smooth remainder다. 모든 kernel derivative가 homotopy 전체에 공통으로 감싸지거나 homotopy 평균 자체에 정당화돼야 한다. nominal η=0 kernel 하나의 높은 정밀도는 이 조건을 대신하지 않는다.

## 5. 전 구간 Peano norm을 실제로 계산했다

원 weight box의 각 값을 공유하는 경우의 오차를 반드시 포함하도록 interval polynomial을 사용했다. 원 두 노드에서 P4의 식을 나눈 다음, 각 구간을 16개로 나누었다. 3개 source 구간 전체에서 144개 subinterval이다. 각 다항식을 Bernstein 계수로 변환한다.

계수가 전부 비음수/비양수이면 부호가 고정되어 다항식을 정확히 적분한다. 부호가 섞이면 positive Bernstein basis와 triangle inequality로

    ∫a^b |P4| <= (b−a)/(n+1) Σk maxabs([B_k])

를 사용한다. 표본점 최댓값은 사용하지 않았다. interval coefficient에서 weight 상관을 잃는 것은 외측 완화이며 잘못된 축소가 아니다.

실제 global-u 4차 미분 bound M4가 모든 세 구간에 공통일 경우의 계수 합은

    C4_total = Σj (hj/T)^4 ∫0^1 |P4,j(t)|dt
             <= 2.5799877760925946815392074954550e-10 photons/H.

이 값은 source 오차 자체가 아니라 M4를 곱할 계수다. 각 구간의 coefficient budget 분담은 99.7753872361%, 0.2223761682%, 0.00223659572%이다. 실제 source 오차의 인과적 분담률이라고 해석하지 않는다.

같은 global-u derivative convention에서 anchor 계수들의 절댓값 합은

    k=0: 1.0106224076840892e-21
    k=1: 3.0632778689500903e-22
    k=2: 7.2197565033039291e-23
    k=3: 1.2363251688060138e-23     [photons/H].

작지만 정확한 0은 아니다. 이 계수에는 이미 k!가 들어 있다. 보고서의 수치를 사용하면서 factorial을 다시 나누면 안 된다.

알려진 여섯 birth가 실제 kernel의 정칙성 경계라면 그 위치에서의 global-u jump 계수 절댓값 합은

    r=0: 3.1250000000000003e-6
    r=1: 1.5401702535614055e-7
    r=2: 7.1686462226547551e-9
    r=3: 2.6305685172750210e-10     [photons/H].

이는 potential-event coefficient이며 실제 Jr가 비영이라고 관측한 것이 아니다. 실제 derivative jump, 필요하면 다른 내부 경계까지 supplier가 제공해야 한다. smooth M4만 줄이고 이 항들을 빼면 인증이 되지 않는다.

설계용으로 최신 causal fallback safe upper 2.125035e-18의 90%를 regular 4차항에 배정하면

    M4 < 7.41294791286391e-9 [τ/(photons/H), global-u derivatives]

가 그 항의 budget 조건이다. 나머지 anchor와 모든 jump에 10% 이하가 따로 필요하다. 이 수치는 실제 M4의 측정/인증이 아닌, NCP가 검증해야 할 목표값이다. 더 이른 Volterra 경로의 작은 상계와 비교할 경우 해당 목표 예산도 별도로 더 엄격하게 다시 계산해야 한다.

## 6. 반례와 검증

정규화 source M=1, 노드 1/4,3/4, weight1/2,1/2인 제조 rule에서 f=(x−1/3)+이면 모든 regular 4차미분이 0이지만 ℒ(f)=1/72다. source kernel의 내부 kink를 무시하면 잘못된 0 오차를 얻게 된다. ξ=1/4처럼 kink가 quadrature node에 있어도 coefficient는 1/32로 비영이다. 이 제조 rule은 실제 Gauss source를 대신하지 않고 구현의 경계항 검증에만 썼다.

새 고유 Python 시험19개 PASS, 그중 mass mismatch를 0으로 지우는 구현에 대한 1 assertion RED→GREEN을 보존했다. 다른18개는 tests-after다. 실제 규칙 weight corners의 모멘트48개 및 Peano L1 적분12개를 별도 80자리 direct-hinge quadrature와 대조했다. piecewise cubic+내부 jump의 정확 rational 사례64개에서도 완전한 항등식을 확인했다. 현재 source coefficient 생성 자체는 Fraction 정확 산술과 Bernstein 외측 상계에 의존하며 scalar quadrature는 독립 유한 검산이다.

새 FT03 IVP/native/원자provider/interval AD 및 이전 donor science suite 실행은0이다. 실제 full coupled kernel, derivative, jump, homotopy는 미실행이다. MissingPremise 인터페이스는 이 입력이 없거나 partition/homotopy 조건이 없으면 거절한다. boolean 조건만 true로 보내는 행위가 그 전제의 수학적 정당성을 증명하지는 않는다. proof assistant/독립 인간·에이전트 심사는 없다.

## 7. 종료와 다음 NCP 작업

이번에 닫은 것은 실제 source plan의 증명용 계수와 경계항 전달 코드다. 새 FT03 source/time 구간은 null이며 기존 R17A를 재명명하거나 축소하지 않는다. 후속 R17B2는 첫 source 구간의 arbitrary birth coupled homotopy-response를 실제로 구성하여 전 구간 regular derivative와 jump를 제공해야 한다. 기존 source·time 상계는 검증된 개선이 나올 때까지 유지한다. 같은 CDF 면적과 기존 donor 시험은 반복하지 않는다.

CR_OFF_FASTEST, precision atomic PARKED, G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, HH ACTIVE, physical/production HOLD를 유지한다. Grackle와 G02 blocker는 이 연구로 해소하지 않는다. 다른 repository mutation은 없다.

## 문헌과 근거 상태

NIST DLMF §3.5 (https://dlmf.nist.gov/3.5), §3.3 (https://dlmf.nist.gov/3.3)는 Gaussian quadrature 및 보간/나머지의 표준 배경이다. 본 문서의 finite-moment+내부-jump 식은 Taylor 적분나머지에 직접 ℒ를 적용해 유도했다. R17B1의 실제 수치와 가정은 본 패키지 입력·Fraction 계산에서 나온 것이며 DLMF가 이 FT03 계산을 인증하는 것은 아니다.

## 실행 복구 기록

새 재현기의 INDEPENDENT.json 로그가 같은 이름의 과학 결과를 덮어쓴 경로 충돌로 첫 fresh 검사가 실패했다. 자식 계산은 exit0이었고 로그 안 stdout이 정본 결과와 같음을 확인했다. *_RUN.json으로 로그만 분리하고 새 빈 디렉터리에서 19개 시험·계수 계산·독립 검산을 포함한 재현을 완료했다. 두 결과 JSON은 정본과 바이트 동일하다. 수정 전 실행기와 실패 출력은 failures에 보존했다. 이 수정은 수학 코드나 원 입력을 바꾸지 않았다.
