# F04F2: 기존 F05 root box 위의 사건·escape observable enclosure

## 판정과 계승

SCOPED_UNIFORM_EVENT_ENCLOSURE__INHERITED_ROOT_MEMBERSHIP.

F05 level0 첫 accepted transaction의 기존 7차원 initial-state parent와 세 root box를 전제로, PI9/CI3/RR3/DR2 및 incremental escape의 18출력 범위·중심 affine 계수·Hessian 곡률 remainder를 새로 계산했다. F04E의 초기값 정규화 차이도 같은 실수 BE map에서 remainder와 함께 감쌌다. Root 존재·유일성·box membership은 owner의 기존 인증을 계승한다. 이번에 root certificate를 독립 재발급한 것은 아니다.

시작 및 게시 직전 bass_cr HEAD=4ccc46333f2d06591392fc051dbf9f7cd9887b0e, tree=86a4a6e1142ca8064d91cb8d603446fb0406ba5b. 동일 research/r4q-gap-closure-20261001 branch의 새 경로다. Concurrent f04f_record_coverage의 7000개 기록 연결은 이미 완료되어 REPORT와 OWNER_SOURCE_LOCK만 수신했다. 이를 재실행하거나 이번 성과에 합산하지 않았다. 이름과 성과 중복을 피하기 위해 이번 단위는 F04F2다. F04/F05 완료 및 F04E native 관측은 그대로 계승한다.

Receiver live snapshot=8e8ea0c664e2ba2f2f8560e0c64266d206fbd50f, tree=fc37657ffcc71111385a4b56d3fc3e287becf367, branch=forward/rust-reion-kernels-20260922. coupled_primary.rs의 public state/stage/events와 F08_stage qualification을 읽었다. 해당 receipt는 조건부 stage PASS와 paired history NOT_EXECUTED를 구분한다. F08/receiver 소스·runtime_returns/CODEX_SYNC를 변경하지 않았다. 정적 결과에 임의 a^3/a^4 가중치를 붙이지 않았다.

## 정확 입력과 소스

검증된 F04E ZIP(bytes404871, SHA256 b88932c7a2337972df19231755491725b7090bab347d203fa514fce2717b7cdd)의 payload SHA/size/CRC를 확인하고 필요한 파일만 상속했다. 새 ZIP의 inputs/IMPORT.json에 원 entry와 SHA가 있다. 자동 mount된 첨부를 불필요하게 다시 materialize하거나 전체 원격 백업을 복원하지 않았다.

좌표 q=(xHII,xHeII,xHeIII,w,p0,p1,p2), w=u/(nH*epsilon_eV), p=N/nH. epsilon_eV는 1eV의 erg 환산 에너지다. 시간은 초, density는 proper cm^-3, 반응 사건은 per H, escape increment는 eV/H다. c,kB,epsilon_eV를 유지한다. h=1e9s, 각 half=5e8s이며 source physical parameters와 compiled realization은 모두 고정했다.

실제 영역은 첫 F05 record의 저장된 outward-rounded parent_box다. 명목 반경(1e-7,1e-7,1e-7,1e-5,1e-8,1e-8,1e-8)을 새로 구성하지 않았다. 실제 양 끝점과 parent_center, full/half1/half2 center·box·preconditioner를 사용했다. 이는 수학적 검증 영역이며 물리 불확실성 분포가 아니다.

원 source bytes와 live metadata의 일치:
- ft03_controlled.rs: Git blob370fd2fa60521f2dc121ee81c7d24013a3b0d1e5, SHA25661e11471482bb49d99e5d0eb79504d3f67538fbe6361653a0462d1abb0b672db.
- ft03_rates.rs: Git blobb8a85ff37de160ecc576a168e4259ed23920a499, SHA2561a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f.

Compiled DR의 dr_a,b1,b2,b12를 각각 저장 비트로 읽었고 b12를 b1+b2로 대체하지 않았다. 기본 EOS/rate kB identity를 확인했다. Native 중간 반올림과 이 고정 실수 map의 parameter identity는 구분한다.

## 산술과 수학적 구성

src/interval.py는 70자리 Decimal의 방향반올림을 사용한다. 사칙연산은 FLOOR/CEILING, exp/ln은 공식 correctly-rounded nearest-even 계약 뒤 한 representable 값씩 outward 확장한다. Power는 exp(p*ln(x))로 구현하고 일반 Decimal.power를 사용하지 않는다. float는 Decimal.from_float로 정확히 읽는다. Nonfinite, denominator crossing0, 비양수 log/power, overflow/underflow/subnormal은 실패로 반환한다. JSON proof endpoints는 Decimal 문자열이며 float serialization으로 줄이지 않는다. 표준 산술 구현 계약을 전제로 하는 interval 계산이며 작업 정밀도가 물리적 정확성 자릿수는 아니다.

고정 tau에 대해 R(y,q)=y-q-tau*f(y)=0, A=I-tau*f_y이면

    J=A^(-1)
    H_phi,i=tau*sum_k J_ik * J^T*H_f,k*J.

원 root membership을 전제로 저장 C에서 B=I-C*A, qN=||B||inf<1을 확인하고

    A^(-1)=sum_(k=0)^8 B^k*C + tail
    ||tail||inf <= qN^9/(1-qN)*||C||inf

로 inverse/J/H를 감쌌다. 이번 qN은 owner의 weighted Krawczyk q와 같은 수치가 아니다. 중심 affine 계수를 실제 중심 root에서 평가하기 위해 근사 endpoint의 잔차와 inverse bound로 central posterior distance를 계산하고 기존 box 포함을 확인했다. Half2 중심에는 half1의 posterior 오차도 전달했다. 새 root 탐색이나 Krawczyk campaign은 없다.

한 stage의 출력 B_tau(q)=tau*e(Phi_tau(q))에 대해

    G_event=tau*e_y*J
    H_event=tau*[J^T*H_e*J +sum_i e_y,i*H_phi,i].

Accepted E(q)=B_tau(q)+B_tau(Phi_tau(q))의 Hessian에는

    H_E=H_event1+J1^T*H_event2*J1+sum_i G_event2,i*H_phi1,i

가 들어간다. 첫 half의 Hessian을 버리지 않는다. PI9/CI3/RR3/DR2와 escape를 같은 endpoint에서 계산하고 full discarded 사건은 accepted 누적량에 넣지 않는다. RR kinetic의 g'' 항은 직접 구성한 rate 표현의 interval AD로 유지한다.

실제 중심값과 gradient를 포함하는 interval a,b 및 원 영역의 M_ij>=|E_ij|에서

    E(q) in a+sum_i b_i*(q_i-q0_i)+[-rho,rho]
    rho=(1/2)*sum_ij M_ij*r_i*r_j.

이는 Hessian으로 제어한 affine Taylor의 곡률 remainder다. 2차 Taylor polynomial의 3차 나머지를 구했다고 표현하지 않는다. 원 parent가 볼록이므로 적분형 Taylor remainder를 적용한다. 최종 값 범위는 직접 stage interval과 Taylor 범위의 교집합이다. 같은 parent의 full/twohalf 차이는 affine 계수를 먼저 빼고 독립 remainder는 더한다. 새로운 event acceptance tolerance는 지정하지 않았다.

## 실제 출력 결과

18출력 모두 구성됐다. 아래 값은 반올림 표시이며 정본의 모든 directed endpoints·J/H·remainder는 results/enclosure02/ENCLOSURE.json에 있다.

|출력|accepted enclosure 표시값|곡률 remainder 표시값|full/twohalf 절대차 상계 표시값|
|---|---|---:|---:|
|PI_HI_group0|[3.31171173489428,3.31171968029472]e-5|6.64378e-18|8.80084e-9|
|CI_HI|[6.35714144003977,6.35718927888890]e-6|2.91552e-17|6.23477e-10|
|RR_HII|[1.16705062290328,1.16705267221725]e-8|6.59930e-21|2.66061e-13|
|RR_HeIII|[3.73575319915348,3.73575965193869]e-9|1.97911e-21|4.39004e-14|
|DR_0|[3.63653615657691,3.63658294363378]e-11|5.68271e-22|6.95029e-17|
|escape[eV/H]|[4.22122528284389,4.22123162343850]e-7|2.31968e-19|7.01550e-12|

사건 행은 per H다. RR_HII/RR_HeIII/escape 범위의 폭은 직접 interval 평가보다 약2.25/2.43/2.96배 좁다. 이는 같은 수학적 family의 enclosure 폭 개선이며 물리 예측 정확도의 개선 배수가 아니다. 비활성 PI3채널의 값·gradient·Hessian·remainder는 정확0이다. 저장 native aggregate18값과 retained MP18값 모두 범위에 포함되었으나 이는 finite inclusion diagnostic이며 native floating program의 uniform rounding이나 derivative 인증이 아니다.

## 새 입력 이동 remainder

F04E에서 q_native=actual physical old_state를 exact scales로 정규화한 값과 q0의 최대차1.4574269354471891e-15를 보존했다. 그때 없던 uniform curvature term을 이번 동일 parent 영역의 Hessian으로 계산했다.

    DeltaE in sum_i b_i*delta_i+[-rho_delta,rho_delta]
    rho_delta=(1/2)*sum_ij M_ij*|delta_i|sup*|delta_j|sup.

q_native가 원 parent_box 안에 있음을 확인했다. Escape 이동의 absolute bound 표시값은2.74816590368e-23 eV/H, curvature remainder는3.32970009266e-39 eV/H다. CI_HI absolute bound는2.47287207800e-21 per H다. 이제 동일 exact-real BE map의 입력 정규화 이동 항이 나머지와 함께 감싸졌다. 이 수치로 native endpoint residual·floating assembly·physical fit error를 대신하지 않는다.

## 검증과 실패 보존

최종 focused tests33 PASS, first-party science/test Python9파일 syntax 및 result input/software hashes PASS. 사칙연산240개는 Fraction 포함을 검사했다. Source 유한점2개에서 interval observable jets2052성분을 retained mpmath analytic-rate 경로와 대조했다. 별도로 full/accepted의 저장 출력 value/gradient/Hessian2052성분을 새 interval 결과와 대조했다. 과거 reference campaign을 다시 실행한 것은 아니며 두2052검사를 한 독립 과학인증으로 합산하지 않는다.

1개 시험은 assertion RED→GREEN,32개는 tests-after다. 새 비교 시험에서 donor Jet.H를 .h로 읽은 오류, column-gradient를 flat으로 읽은 오류가 각각 발생했다. 실제 donor schema를 확인하여 테스트 adapter만 수정했고 오류와 수정 전 시험을 logs에 보존했다. Mathematical failure나 native runtime failure로 분류하지 않는다. 최종 계산 알고리즘·허용오차는 그 수정으로 바꾸지 않았다.

Final evidence는 logs/07_FINAL_ENCLOSURE.txt,10_FINAL_TESTS.txt,11_SYNTAX_AND_IDENTITY.txt 및 각 exit 파일이다. 최종 runner의 wall은 약2.578s이며 전체 세션 시간이나 HPC scaling 수치가 아니다. 독립 human/agent review와 proof-assistant 검증은 없다.

이번 root solve/native call/owner checker replay/history replay/old suite replay/원자 적분/owner box expansion/receiver mutation은 모두0이다. Standard-library main runner와 mpmath를 사용하는 새 시험만 실행했다. 이번 event extension은 첫 record의 범위이고 나머지6999개의 uniform event enclosure를 완료하지 않았다. Inherited root premise와 새 observable 미분·remainder의 검증은 구분한다.

## 정본 패키지와 실제 이중백업

파일=BASS_CR_CHAT_F04F2_20261005_v1.zip
bytes=428005
SHA256=39d1632bd00e55b22deeb72d31541371a5129b6536ed2a41c74749bc1d162093
ZIP64members,63payload의 size/SHA256 및 CRC local검증.

Drive success ACK와 metadata readback: id1isqsxcNggNoTxZjq5aq_VtwN5vWRmNkv, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ, name/size428005 확인.
Dropbox completed: id:BSpOijBcT10AAAAAADzBeQ, size428005, modified2026-10-05T00:13:42Z, path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04F2_20261005_v1.zip.

동일 immutable local archive를 두 provider에 create-only로 저장했다. R1 UPLOAD_VERIFIED(ID/name/size/path 또는 parent). Remote checksum은 응답에 노출되지 않았고 새 ZIP의 full restore/독립 remote bytehash는 하지 않았다. Concurrent owner F04F의 R3를 이번 F04F2에 상속하지 않는다. UPLOAD_VERIFIED!=RESTORE_VERIFIED.

이 Git 문서는 summary/sync이며 코드·시험·정확 결과·전체 유도·실패 로그의 정본은 위 ZIP이다. ZIP에 미래 provider 성공을 쓰지 않았고 실제 commit/tree/ACK는 별도 DELIVERY_RECEIPT에 기록한다. 읽기 순서 TASK_RETURN.json→SOURCE_BINDING.json→REPORT_KO.md→results/enclosure02/SUMMARY.json, 정확 끝점은 ENCLOSURE.json. enclosure01은 입력 이동 항 추가 전 개발 snapshot이다.

## 종료와 다음 연결

첫 record의18출력 범위와 입력 이동 항은 위 범위에서 닫았다. 동일 결과의 추가 반복 감사보다 실제 consumer가 요청한 stage/time/units/packet ID/energy/work 계약이 다음 대상이다. 새 실제 계약이 없으면 동일 first-record 계산을 더 돌리지 않는다. F08 또는 후속 receiver가 같은 source/parent/tau/root membership을 사용하는지 읽기 전 정적 envelope를 이식하지 않는다. 해당 source 수정은 owner 영역이며 새 mandatory gate를 만들지 않는다.

CR_OFF_FASTEST, precision atomic PARKED, G02=UNRESOLVED, physical production=HOLD, capture=false, all_bound=OPEN,b_grid=NO_GO 및 actual CR source/loader/callback 관측=null을 유지한다. 기존 원자 실행 권한·full-K·318patch·CR-on을 재사용하지 않았다.

방법론 산술 근거: Python 공식 decimal 문서의 exp/ln correctly-rounded HALF_EVEN, next_minus/next_plus, FLOOR/CEILING 계약. URL은 https://docs.python.org/3/library/decimal.html . 적용 Taylor/implicit derivative/Neumann tail 식은 정본 REPORT_KO.md에 직접 유도했다.
