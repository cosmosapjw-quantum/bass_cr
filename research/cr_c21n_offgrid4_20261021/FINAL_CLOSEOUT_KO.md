# C21N offgrid4 최종 연구 마감

**초기 matter/radiation 응력을 상쇄한 네 입력의 실제 궤적·성분별 그림·검산을 완료했고,
별도로 도착한 NCP 실행도 원 source와 raw에 결속해 수용했다.** 새 샌드박스 실행은4회,
외부 NCP 실행은 동일 입력의4회이며, 외부 반환 수용에는 새 ODE를 사용하지 않았다.
고유 초기조건은 기존125+새4=129개다. 기존81/125를 이 대화에서 재적분하지 않았다.

최신 상태의 권위는 이 문서, `RESEARCH_DAG.json`,
`external_ncp4/NCP_RETURN_ACCEPTANCE.json`, 게시 후 작성하는
`C21N_OFFGRID4_FINAL_AUTHORITY_RECEIPT_*.json`이다.
초기 content의 NCP `NOT_RUN`은 그때 관측한 역사적 상태이며 아래 실제 반환으로 갱신한다.

## 1. 게시와 실행 provenance

| 구분 | 실제 identity |
|---|---|
| Repository / draft PR | cosmosapjw-quantum/bass_cr / https://github.com/cosmosapjw-quantum/bass_cr/pull/95 |
| 게시 branch | research/cr-c21n-offgrid4-sandbox-20261021 |
| 새 샌드박스 raw·분석·guard content | e7729092abc6edbe74f31d0ed82aa84d5506b8d5 |
| NCP 반환 수용 content addendum | 038aa0c8e5790f5c94e596035ea816fbca588a15 |
| 원 실행 code content | 5ecb8a6c4961302b7066b06278e72ecd2d77f8c9 |
| 원 REI 물리 source | 3b85dedce84d37b3e165da00685a8a984950aafe |
| 원 기준 document HEAD | 0f45d0a422d79ccead565a8abaab860fcc230687 |
| 외부 NCP 원 게시 | PR94 / 92b1b3f5575375580cf8de8039252ac492353b7e |
| 이 문서 commit | 자기 hash를 만들지 않으며 실제 게시 후 외부 final authority receipt에 결속 |

첫 content는93개 새 파일, NCP addendum은52개 새 파일이다. C21L/M/N의 기존 파일은
변경하지 않았다. 이번 문서 단계에서만 새 unit의 DAG·단계표를 갱신한다. 해당 두
상태 파일은 content 시점 manifest와 document 시점 파일이 다르므로, 복원 명령은
content Git blob 검증과 document 검증을 구분한다.

## 2. 최신 외부 결과 수용

13:06:07 UTC의 범위 조사에서7개 관련 repo의1,240 advertised heads를 확인했다.
이전 기준 대비 새7개·변경3개를 분류했으며 source·fixture·grid·구간이 다른 결과는
별도 lineage로 보존했다. ACCEL02의 C++ reflection-pair/Neumaier reduction은 원 FP
연산 순서가 다르므로 같은 연산 재사용 최적화에 자동 편입하지 않았다. HH·HE·REC·Vigil
결과의 확인 범위는 `intake/github/RESUME_INTAKE.json`에 있다.

다른 대화 검색 서비스는13:46:43 UTC 실제 보완 조회에서도 `UNAVAILABLE`였다.
접근 불가 범위를 전역적 결과 부재로 해석하지 않는다. PR95 생성 후 새 번호라는
단서를 따라 PR94만 추가 조사했다. PR94는13:14:54 UTC에 생성됐으므로 앞선 조사
이후의 실제 반환이다.

| 실행 | 시작 UTC | host | Python | run identity |
|---|---|---|---|---|
| 이 대화 sandbox | 13:10:16 | af4832b34a81 | 3.12.14 | f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023 |
| 외부 NCP | 13:10:24 | s1a0e5abed09 | 3.12.3 | a07a95f85042f9db7df2e3e465288524b458bcb6f190e9d4f01db1869c139360 |

두 manifest의 차이는 site와 Python patch version이다. NumPy2.3.5/SciPy1.17.0,
source17, grid, tolerance 및 물리 입력은 같다. 실제 NCP 원43개 파일을 Git blob에
결속해 회수했고, 네 COMPLETE seal·NPZ 전체 bytes 및 **236개 FP64 배열/52,520개
값이 모두 byte-identical**, 최대 절대차0임을 확인했다. 이 결과는 지정된 네 경우의
전체 저장 출력에 관한 교차 호스트 재현 근거다. 원 uncached solver의 독립 전체
trajectory replay와는 구분한다.

NCP 원 metadata의 두 CSV는 Git의 LF와 원 checksum의 CRLF가 달랐다. 각5개 줄바꿈을
메모리에서만 변환하면 원 광고 SHA와 정확히 맞는다. 원 bytes·checksum·첫 비교
중단 근거를 보존했다. `content_tree`가 run identity를 담은 필드명 오류도 별도
설명했다. 기존125를 중복 저장하는 combined NPZ 하나는 회수하지 않았고, 원 manifest
전체 PASS나 해당125 prefix의 재검증을 주장하지 않는다. 물리 raw의 P0 충돌은0이다.

## 3. 이론과 코드의 실제 기여

원 분포는 massive sector에서 $f_{\rm FD}(q)[1+A P_2(\mu)]$이며, $A$마다 distribution
weight·packet population·reference energy normalization을 다시 생성한다. Radiation은
기존 source의 공통 quadrupole $k$를 photon과 massless neutrino에 적용하고 두 species를
별도 보존한다. C21M의 독립 초기축 builder와 C21N의 immutable geometry 준비 계층을
그대로 사용했다. 이번 실행에 scalar $A$만 바꾸는 shortcut은 없다.

Signed source amplitude는 $p_X=(p_{\parallel,X}-p_{\perp,X})/3$이다.

\[
S=\frac{\sqrt6s}{H_t},\qquad
P_X=\frac{\sqrt6(8\pi G/c^2)p_X}{H_t^2},\qquad
\Sigma=|S|,\quad\Pi_X=|P_X|.
\]

$H_{\rm geom}=H_t/c$이면 $\kappa_E=8\pi G/c^4$와 같은 무차원 정의다. Full Frobenius는
원 half-contraction의 $\sqrt2$배다. $P_r=P_\gamma+P_\nu$, $P_{\rm tot}=P_m+P_r$를
먼저 만든 뒤 norm을 취한다. Dust는 실제 isotropic species이고 UV의 absent와 baryon
anisotropic stress의 unmodeled 표지는0으로 대체하지 않는다.

SciSpace·Exa 원전 확인과 Wolfram 성공2건으로 뒷받침한 기존 mass-shell 유도를 재사용했다.
새 문헌검색·CAS campaign은 하지 않았다. Conserved packet 합의 직접 미분을 통해
초기 $S_0=P_{{\rm tot},0}=0$에서

\[
p'_{m,0}=(-5+\beta_m)p_{m,0},\quad p'_{r,0}=-4p_{r,0},\qquad
S''_0=-(1-\beta_m)P_{m,0}
\]

를 얻는다. 따라서 $S(\eta)=-\tfrac12(1-\beta_m)P_{m,0}\eta^2+O(\eta^3)$이다.
이번 네 입력의 packet 값은 $\beta_m\simeq0.031700764390593$이다. 실제 구현은
tiny stress로 나누지 않는 직접 mass-release 합과 원 RHS를 사용하며, 초기 FP offset을
보존한 $S_0+S'_0\eta+\tfrac12S''_0\eta^2$를 저장 궤적과 비교했다.

새 분석기 `analyze_offgrid.py`는 source/manifest/input 경로를 검증하고 외부 output
경로의 create-only 저장을 지원한다. 기존 성분 분해·물리 검사·미분 모듈을 재사용해
tensor·signed amplitude·norm·보존량·국소 jet을 함께 저장한다. 새129 registry와
`completed_input_guard.py`는 이름을 바꾼 완료 입력도 축별2e-13 이내에서 거부한다.
역사적 runner를 바꾸지 않았으므로 다음 새 grid는 guard를 명시적으로 먼저 통과해야 한다.

## 4. 실제 결과와 그림

초기 signed 좌표는 $S_0=0$, $P_{m,0}=\pm7.5\times10^{-5},\pm1.75\times10^{-4}$,
$P_{r,0}=-P_{m,0}$이다. z20→4,40상태×101저장점, 원FP64 DOP853,
rtol3e-11/atol3e-13을 유지했다.

| $P_{m,0}$ | $S_f$ | $P_{m,f}$ | $P_{r,f}$ | $P_{{\rm tot},f}$ |
|---:|---:|---:|---:|---:|
| −1.75e-4 | +2.14722623e-5 | −9.96100539e-6 | +4.11389388e-5 | +3.11779335e-5 |
| −7.5e-5 | +9.20242234e-6 | −4.26904013e-6 | +1.76310855e-5 | +1.33620453e-5 |
| +7.5e-5 | −9.20245870e-6 | +4.26909686e-6 | −1.76312530e-5 | −1.33621561e-5 |
| +1.75e-4 | −2.14724603e-5 | +9.96131424e-6 | −4.11398509e-5 | −3.11785366e-5 |

초기에 거의1이던 cancellation $C=1-|P_m+P_r|/(|P_m|+|P_r|)$는 끝점에서
약0.38986이다. Massive stress가 더 빠르게 감소하면서 초기 상쇄가 해제되고 shear가
발생한다. 반대 부호 입력의 norm은 가깝지만 exact antisymmetry로 강제하지 않았다.

새4의 z4 최대 norm은 $\Sigma=2.1472460270\times10^{-5}$,
$\Pi_m=9.9613142422\times10^{-6}$, $\Pi_r=4.1139850874\times10^{-5}$,
$\Pi_{\rm tot}=3.1178536631\times10^{-5}$다. 기존125의 endpoint 최대값은 바뀌지 않는다.
이 수치는 해당 ensemble의 표본 결과다. 129개는125 Cartesian 격자에4개를 더한
불규칙 ensemble이다.

국소2차 jet의 최대 상대 잔차는 첫 양의 저장점 $\eta=.0143508453$에서2.12234%,
$\eta=.1004559168$에서15.83743%다. 3차 계수·유한구간 remainder·전역 오차 상계는
이번 단위의 산출물이 아니며 `global_error_bound=null`이다.

![Signed stress and shear](analysis/signed_components_offgrid4.png)

![Full norms and cancellation](analysis/norms_cancellation_offgrid4.png)

![Local quadratic jet residuals](analysis/local_jet_new_existing.png)

## 5. 검산과 독립 검토 범위

| 확인 | 실제 범위 |
|---|---|
| 초기조건 | 원 parameter·prepared builder·raw40상태 bytes 일치 |
| Cached/uncached fields |404개 저장상태,23,836 FP64값 byte equality |
| Cached/uncached RHS |404개 저장상태,16,160 FP64값 byte equality |
| Hamiltonian / massive number |최대 상대잔차2.2204460493e-16 /4.4408920985e-16 |
| Radiation number |최대 절대잔차0 |
| L8 angular positivity |64노드×404상태×4배열=103,424값의 최소.941509322965 |
| 독립 검토 |source17/raw28, input53/output15 bindings, 저장 수치 대조, PNG3 직접 확인 |
| 신규 NCP 수용 |source17/grid4/seals4, 전체NPZ4 및236배열 byte equality |

이산 각도 양성을 연속 각도 정리로 확대하지 않는다. 모든 adaptive 내부 stage의
동등성, 원 uncached 전체ODE 재실행, 시간·격자 수렴 campaign, PDF 별도 raster 검토,
성능 benchmark는 수행하지 않았다. 원 wall/RSS는 실행 provenance로만 보존한다.
최종 DAG의 FP64 count 필드명은 값의 개수와 byte 수를 구분하도록 문서상 교정했다.

## 6. 백업·DAG·NCP 인계

고정 sandbox-content ZIP은1,395개 Git 파일을 담고, 내부 CRC·payload bytes·Git blob을
검증했다. 별도 NCP addendum content와 최종 문서는 후속 작은 closeout ZIP으로 보존한다.

```text
BASS_CR_C21N_OFFGRID4_RESEARCH_DELIVERY_20261021T134804Z.zip
bytes  = 38502346
SHA256 = c5ae168f04b0fde9232237e9337e224d5d1380723cead1cda529ba6f3c4a2df9
Library = libfile_9c24298a7a6c8191a193dda15106ae81  ACK_COMPLETED
Dropbox = id:BSpOijBcT10AAAAAAD_hjA              ACK_COMPLETED
Drive   = UNKNOWN_NO_ACK; object ID 미확인
```

Drive에는 새 이름으로1회 요청했다.45.004초 응답 관측 후 ACK가 없어 미확정으로
기록했고, 알려진 폴더72개 목록의 정확한 이름 대조에서도0개였다. 이 범위의 관측을
업로드 실패·전역 부재로 바꾸지 않는다. 재요청·원격 취소는0이다. 위 SHA는 로컬 ZIP의
값이며 제공처의 SHA 반환과 실제 다운로드 재검증은 별개다. 세 저장처 모두 이번 ZIP의
download byte 재검증은 NOT_RUN이다. 실제 최종 document SHA·closeout ZIP·그 후
provider 응답은 final authority receipt에 저장한다.

| EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|
| Sandbox4 완료, 외부NCP4 수용, 수용ODE0 | PR95 content2개 게시, 별도 문서 마감 | 첫ZIP Library/Dropbox ACK, Drive 미확정; 후속ZIP 별도 결속 | 고유129, 실행·분석·검토 완료; Drive reconciliation OPEN |

NCP 원 실행 당시 affinity64개, available RAM85,958,209,536bytes, storage72,625,807,360bytes와
5,970,296inodes를 관측했다. WorkerCPU1–4, coordinatorCPU0, CPU55보호를 유지했다.
실행 당시 가용량을 현재 예약으로 해석하지 않는다. 새 입력에는 live affinity/quota/
RAM/load/lease/disk/inode를 다시 관측하고 case 수보다 worker를 많이 만들지 않는다.
Worker512MiB·coordinator256MiB·reserve는 보수적 운영 예산이며 실측 memory bound가 아니다.

Numeric library thread1과 process의 관리 thread는 구분하며 양쪽 실행에서 worker의
2threads가 반환 시 관측됐다. 다른 owner의 process·lease·파일을 변경하지 않는다.
현재 네 case는 두 site에서 완료되어 NCP 재실행할 작업이 없다. 재사용 가능한 원
launcher와 source/자원/guard 명령은 `CODEX_HANDOFF_KO.md`에 있다.

## 7. 연구 루프와 다음 의무

| 단계 | 이론 R | 코딩 C |
|---|---|---|
|1|고정 LRS 초기 상쇄 문제와 재개점 확인|원source·FP64·tolerance 유지|
|2|외부 refs/반환/문헌 근거 재사용|기존 source/분포/manifest 경로 대응|
|3|full norm·signed·SI 정의 유지|원 quadrature·reduction·적분 설계 유지|
|4|준비된4개 off-grid 판별 입력 채택|현재 자원 관측,worker4/coordinator1|
|5|기존 mass-shell 유도를 새입력에 적용|새 분석기·129 guard·외부 반환 비교기|
|6|기존 대수/물리 심사 재사용|guard focused검사와 오류 경로 확인|
|7|4실행·404상태·jet 관측잔차|Hamiltonian/number/energy/shear/positivity|
|8|상쇄 해제와 국소 근사 범위 판정|FP64 byte 검사 및 외부 교차 호스트 출력 비교|
|9|수식–CSV/NPZ/그림 연결|별도 독립 검토, 신규 반환만 추가 수용|
|10|실제 게시·백업·DAG·인계|content/doc 분리 및 create-only 배송|

새 strong no-go 정리는 제출하지 않았다. 열린 연구 문제는 예를 들어 초기 jet의
3차 항 또는 유한구간 remainder를 원 RHS에서 구하고 기존 저장자료로 판별하는 것이다.
이 질문의 입력·기여·검증 범위를 먼저 정하면 기존 사용자 승인 범위에서 이어갈 수 있다.
완료 계산의 반복이나 새 승인 절차를 기본값으로 추가하지 않는다. 사용자 고정 물리
가정·정확도를 바꿔야 하는 선택만 그 변경의 근거와 함께 확인한다.

현재 unit의 science·구현·그림은 완료다. 남은 storage 의무는 Drive 미확정 객체의
증거 기반 reconciliation이며 독립적인 후속 연구를 막는 전역 gate가 아니다.
General triaxial, full H/He/UV/stars reionization, 완성 CMB 예측은 HOLD다.
기존 C21F–K의 원 source·실패·raw·HOLD·역사적 NOT_PUBLISHED는 보존했다.
