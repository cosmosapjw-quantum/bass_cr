# A2 / R4AC: same-center V_other 표본별 오차 통제

2026-10-02. `R4AC_SAMPLE_VOTHER_CERTIFIED_AND_H_ONLY_REASSEMBLY_PASS`.

유한 s+p candidate와 z=-32a0 근방의 저장된 11개 geometry에서 V_other의 수치 오차를 직접 감쌌다. A2 전체나 연속 궤도·물리 source 정확도의 인증은 아니다. R4AB intrinsic cache와 S/D/여섯 cross block은 그대로 보존했다. 새 cross 호출과 완료된 R4Z/R4AA/R4AB 계산·시험 재실행은 모두 0회다.

## 결과

- 새 GL32/GL48/interval radial 배치: 각 11개, 두 중심 certificate 22개.
- 저장 자료 H-only 재조립: 34/34 통과.
- 새 V 성분 절대오차 상한: 7.243285943310776e-18 Eh.
- 새 V Frobenius 오차 상한: 1.7027341263765435e-17 Eh.
- 저장 order-20 V 성분 절대오차 상한: 4.901947050845828e-17 Eh.
- 저장 order-20 V Frobenius 오차 상한: 7.038301725162392e-17 Eh.
- GL32/48 최대 성분차: 6.938893903907228e-18 Eh. 이것은 진단이지 certificate의 근거가 아니다.
- full H relative Hermiticity 최대: 5.94195544493205e-20.
- 새 과학 모듈 시험 15건, 전달 verifier 시험 3건 통과.
- 독립 산술 검토 3854조건 통과: 120자리 local-s recurrence의 radial225개 및 direct spherical projection의 potential486개가 모두 interval에 포함됐다.

기존 order-20 V도 이 표본들에서는 이미 매우 정확했다. 따라서 같은 위치의 quadrature order를 계속 높이는 대신 연속 정칙성과 미분 나머지 통제로 이동한다.

## 방법과 범위

Legendre 생성함수·구면조화함수 가법정리·Gaunt triangle/parity에 따라 s+p의 Coulomb 각도 투영은 L<=2에서 정확히 끝난다. 원전은 DLMF18.12.E11,14.30.E9,34.3.E22다. 선택된 span의 이 항등식은 기저의 물리적 완전성을 뜻하지 않는다.

P_ab(r)=U_a(r)U_b(r)에 대해 K_L(R)=R^(-L-1) integral_0^R(P_ab r^L dr)+R^L integral_R^rmax(P_ab r^(-L-1)dr)다. 저장 degree4 함수의 곱을 정확한 유리수 degree8 다항식으로 만들고 패널별 power/log로 적분한다. 정확 stored FP64 좌표의 sqrt 및 log까지 Python 정수 기반 320fractional-bit outward interval로 감싼다. log는 atanh120항과 직접 증명한 나머지 상한을 사용한다. 고정밀 차이를 엄밀한 상계라고 부르지 않는다.

실행용은 local-s endpoint/bubble 직접 평가의 strict FP64 Fortran GL32, 비교는 GL48이다. 원소별 결정론적 보상 합과 no-fast-math/no-FMA-contraction을 유지한다. 실제 G/H0/A 비직교성과 S/D/cross bytes를 보존하고 V만 새로 넣어 H의 boost 항을 일관되게 조립한다. adapter는 real radial/x-z plane/s+p/등록된11geometry에 한정한다.

정수 interval 코드의 구현 검증과 형식 검증된 일반 라이브러리는 다르다. certificate는 finite stored candidate의 표본별 오차이며 H0/A/cross 전체 H 오차나 physical model discrepancy를 포함하지 않는다. 고정밀 독립 검산은 같은 runtime의 다른 알고리즘이지 별도 인간·에이전트 검토가 아니다.

관측 stage는 1회 완료, 실패0, 자동재시도0. 4CPU quota/4GiB cgroup, worker/native1thread, wall1.212109209s, peakRSS97580KiB다. 전체 연구·코딩·시험 시간이나 NCP64 성능은 아니다.

## 다음 한 단계

`A2/R4AD_CONTACT_CELL_REGULARITY_AND_S_ONLY_REMAINDER_CONTRACT`.

현재 z=-32 contact cell에서 cross S의 실제 정칙성, moving-domain/ETF의 경계항, 필요한 차분 나머지를 유도한다. 정당한 R8 상계 또는 구체적 obstruction과 근거 있는 대안을 반환한다. S 입력 적분/roundoff와 truncation은 별도다. 새 cross0, V0, 완료된 시험·계산 재실행0이며 다른7점/capture/basis/b/energy 확대는 자동 승인하지 않는다.

same-center radial의 경우 P가 C0이면 K_L은 R>0에서 C2이나, 패널 경계에 P'의 점프가 있으면 [K_L third derivative]=-(2L+1)[P']/R^2가 일반적으로 남는다. 이를 cross S의 C9 증명으로 전용하지 않는다. A2는 `PARTIAL_CONTINUOUS_OPERATOR_AND_DERIVATIVE_REMAINDER_OPEN`이며 C0 actual receiver binding도 pending이다.

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO.

## 완전한 재현 자료와 실제 백업

`BASS_CR_R4AC_VOTHER_PACKAGE_20261002_v1.zip`

- bytes: 46346100
- SHA256: eb6df89601419292a6c71ef389bc8b9600e605598e92bcdd9ab5f4c0a4995a8c
- Drive ID: 1Waz2AfAWRQb0i6sSE9F0N1Dhbudjg_3_
- Drive parent: 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
- Dropbox ID: id:BSpOijBcT10AAAAAADxmMA
- Dropbox path: /bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/BASS_CR_R4AC_VOTHER_PACKAGE_20261002_v1.zip

두 provider가 실제 업로드 완료와 46346100bytes를 확인했다. R1 UPLOAD_VERIFIED이며 remote checksum은 반환되지 않았고 RESTORE_VERIFIED=false다. 로컬 ZIP은263members CRC와262payload SHA를 확인했다.

이 Git 경로에는 실제 실행한 source8개와 test5개, 설명·상태·결과·DAG pointer4개를 게시한다. source/test13개는 로컬에서 계산한 Git tree e9be2d3255b2caa09c1ca4f8d5f74fd837bd733d와 provider tree ACK가 일치한다. 전체 유도, 계약, input76개, native, raw/result, DBv15, 부모 R4AB ZIP, 실행·반환 지침은 양쪽 cloud의 완전한 패키지에 있다. 두 전달 표면의 coverage를 혼동하지 않는다.

R4AA의 이전379개 원 파일 전체 작업트리 동기화는 별도 미완료다. 이번 새 node 게시로 소급 완료하지 않는다. 이후 새 환경 재현이 꼭 필요하면 패키지 RUNNER_API.md에 따라 새 native/resource/context를 고정하고 기존 결과를 덮어쓰지 않는다.
