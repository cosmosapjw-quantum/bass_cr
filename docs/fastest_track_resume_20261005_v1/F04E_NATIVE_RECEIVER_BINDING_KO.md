# F04E: 기존 F05 accepted 기록과 native 사건·escape 계약 연결

## 판정

SCOPED_VALUE_AND_STAGE_BINDING_COMPLETE__REFERENCE_JETS_ONLY.

F04D의25출력 계약을 실제 REI-F05 첫 accepted transaction에 연결했다. 기존 이력은 재적분하지 않고 저장 기록을 소비했다. 원 record에 없던 두 half의 사건률·사건 수·온도·escape를 실제 원본 FT03의 두 BE 호출로 추가 관측했다. 최종7state+17events+escape increment1이 기존 accepted 기록과25/25 binary64 bit로 일치했다. Reference gradient/Hessian은 기존 값을 단위변환했을 뿐 native FP 프로그램의 미분이나 uniform event remainder를 인증한 것은 아니다.

시작/게시 직전 bass_cr HEAD=565df6d2c2c3dc1f97abbc1ee0dac70521256861, tree=f5442c03a2e673151502d14c9271be02376ec1d9. 기존 research/r4q-gap-closure-20261001 branch에 새 문서만 추가한다. F04D 뒤의 SYNC02 HANDOFF(blob68a23662331bff07e76de576d307a1e3f75feb93)를 읽어 F05 완료와 F04E의 optional read-only 범위를 계승했다. F08 owner source, receiver runtime_returns 및 CODEX_SYNC는 수정하지 않았다.

## 실제 source/data 복원

Receiver snapshot=cosmosapjw-quantum/rei_bianchi@7c5469101f8d6ef027c8c3119cc5c053e15ba1d9, tree=8033256c40ab1bcd46f1d895dfd314ac41b4d65c, branch=forward/rust-reion-kernels-20260922.

Owner의 정적 F04 인증과 F05 0..1e12s/7000accepted-step whole-interval 성공을 수신했고 재실행하지 않았다. 다음 세 원 파일을 Dropbox mirror에서 회수해 authoritative Git blob과 로컬 bytes를 일치시켰다.

- source_identity.dat:182814bytes, blob4fa48a5a05faeeeb83170697ce38a1569101c0ce, SHA2561feb6dfe00415fa02d8bab9478f9bc9129a1cff63239688d4999a954ee297821.
- level_0_transactions.jsonl.gz:2514942bytes, blob19163079b3b651b141e410c1744d853a213f97fd, SHA256b267c0e94e6ec08686977d12be3da27debe462d141e91a2d4e6ad3ff5bb6d7a2.
- checker_receipt.json:1476bytes, blob4bdd2f72d62c89ca587c818f19248e69460dda67, SHA256dd79747f4202fb3b4957da6c1e63a32e0ccd3ce0bffea1be26464ce139c61738.

source_identity는 first_interval의 compile-time 원문 container다. 파일명·byte length로22개 소스를 복원했고 source hash 목록을 보존했다. 그중 hhe_events.rs, microstep.rs, thermal.rs, atomic_provider.rs, ft03_rates.rs, ft03_controlled.rs의 원 bytes6개를 새 minimal crate에서 그대로 사용했다. 물리 함수 본문 변경은 없다. F05 당시에 기록된 소스를 사용한 것이며 최신 F08 source를 섞지 않았다.

기존 gzip의 첫 두 행 원 bytes를 저장했다. 첫 accepted 행만 새 물리 관측에 썼고 두 번째 행은 nonzero cumulative escape에서 increment를 계산하는 read-only 시험에만 사용했다. 최종 ZIP에는 원 gzip 전체 대신 두 행·원 gzip hash·source container와 복원 source를 담았다. 특정 source/data의 실제 readback 검증과 새 ZIP의 cloud upload 검증을 구분한다.

## 첨부 Rust 환경

첨부 Rust1.94.1 archive192287020bytes의 SHA256은294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40이다. 로컬 /mnt/data/rust-1.94.1-prefix에 필요한 rustc/std/cargo를 복원했다. install.sh는 읽었지만 실행하지 않았고 global 설치나 package download는 없다. 첨부 RUSTCORE는 별도 bianchi_rustcore crate로 확인했으며 F05 source 대용으로 쓰거나 build하지 않았다.

실제 rustc1.94.1(e408947bf2026-03-25), compiler commit e408947bfd200af42db322daf0fadfe7e26d3bd1, LLVM21.1.8의 version 출력·toolchain smoke·이번 physics probe build/run을 확인했다. 이전 local rustc 부재 blocker는 해소됐다.

Detached signature는 public key 부재로 No public key, official checksum/key 회수는 직접 네트워크 실패였다. 사용자 제공 bytes의 local hash와 실행은 확인했지만 공식 GPG authenticity는 NOT_VERIFIED다. Bad signature 또는 native 실행 실패로 분류하지 않는다. Toolchain와 executable bytes는 ZIP에 넣지 않고 실제 compiler/source/binary hashes와 stdout/argv/exit를 남겼다.

## 관측과 accepted 연결

Actual consumer는 first_interval.rs::record와 adaptive_history.rs::certified_ft03_trial이다. 기록은 accepted flag, old/state8좌표, parent/next boxes, full/half1/half2 normalized center, 합산17events와 ledgers를 포함한다. 개별 half events·원 physical state·온도는 모두 따로 저장되어 있지 않다.

첫 행 t0=0,dt=1e9s와 실제 StepControl(max_iterations200,residual_tolerance1e-15)를 고정했다. 옛80/1e-14를 쓰지 않았다. Original physical old_state를 저장 비트로 받아 두 actual ft03_implicit_step(h/2=5e8s)을 실행했다. 새 full trial/history/certifier 호출은0이다. 원 Ft03Events::plus로 accepted events를 합산했다.

- 최종7state+17events+escape increment:25/25 bit identity.
- half1/half2 normalized centers:14/14 bit identity.
- 모형 constants11+sigma9:20/20 bit identity.
- half1/half2 iterations:3/3.
- T[K]:49999.78787800223 /49999.575801042796.
- Native reported residual norms:9.860056429103134e-17 /1.5215560008779607e-16.

새 probe는 자체 acceptance를 발급하지 않는다. Acceptance는 기존 F05 transaction/checker에서 상속하며 source·input·step identity와25개 native 값 재현으로 연결한다. 새 ft03_rhs 두 번은 각 endpoint에서 필요한 rate를 다시 평가한 것이다. Solver 내부 rate 버퍼를 intercept했다고 표현하지 않는다. 물리 native program1회,BE2호출,추가RHS2회이며 별도 compiler smoke1회가 있다.

## 단위와 reference derivative 경계

q=(xHII,xHeII,xHeIII,w,p0,p1,p2),w=u/(nH*epsilon_eV),p=N/nH. Physical output의 에너지·escape scale은nH*epsilon_eV,photon·reaction count scale은nH다. Escape는 new-old increment이며 누적 escaped state 자체가 아니다.

고정 model에서 q=S*P,V=D*O(q)이면 Jphysical=D*Jq*S, Hphysical_i=D_i*S^T*Hq_i*S. 이전에 저장한25-output gradient/Hessian approximation에 이 exact linear 변환을 적용했다. 변환 산술이 exact라는 것과 입력 derivative가 rigorous라는 것은 다르다. 8번째 log-step 방향도 기존 formal point direction이며 새 uncertainty가 아니다. Native derivatives/interval event remainder는 미검증이다.

Native old.u를 exact physical scales로 정규화한 값과 F04D rounded normalized center는 같지 않다. 최대 parent 차이1.4574269354471891e-15를 보존했다. 이 차이를 포함한 단순 finite parity에서 normalized state7 최대절대차7.246594223321078e-16, nonzero events/escape 최대상대차1.8606620581117634e-15다. 사전 tolerance1e-12/5e-12를 통과했고 disabled PI3채널은 정확0이다. 저장J/H의 입력이동 Taylor 진단에는 새 remainder가 없으므로 증명 bound로 쓰지 않는다. 같은 observed state의80자리 source 재평가에서 event rate 최대상대차는2.1875690796504245e-15이며 finite diagnostic이다.

## 동일 stage의 잔차·사건 assembly

저장값을 exact rational로 읽고 r=Delta y-h_j*fhat, r_escape=Delta escape-h_j*fescapehat로 둔다. wN=(nH,nHe,2nHe,0,1,1,1), E=CI-RR-DR integrated net events, e=동일 endpoint 관측net rate이면

    DN=wN*Delta y-E
      =wN*r+h_j*(wN*fhat-ehat)-(E-h_j*ehat).

Energy weight wE에 대해서는

    DE=wE*Delta y+Delta escape
      =wE*r+r_escape+h_j*(wE*fhat+fescapehat).

두 half에서 이 분해를 정확 유리수로 확인했다. Event multiplication과 accepted floating addition의 실제 작은 차이를 별도 항으로 남겼다. Same-site source arithmetic, solver residual, 반환 assembly를 섞지 않았다. Total number defect=-3.7214657111635744e-17 perH, energy defect=-7.234257889366825e-16 eV/H다. Uniform bound나 physical-error 추정으로 해석하지 않는다.

## 새 정보경계: aggregate만으로 stage 가중합은 결정되지 않는다

E=E1+E2만 보존했을 때 w1!=w2이면 W=w1*E1+w2*E2를E만으로 복원할 수 없다. E1→E1-delta,E2→E2+delta는 같은 합을 유지하지만W를(w2-w1)*delta만큼 바꾼다. 최종 stage weight만 전체에 곱한 오차는

    W-w2*(E1+E2)=(w1-w2)*E1.

이번 실제 PI_0_0 stage counts에 인위적 weights(1,2)를 사용하는 부정 대조의 오차는-1.6562983444554425e-9cm^-3였다. 이 weights는 실제 FLRW a^3/a^4가 아니며 팽창 history나 work를 계산한 것이 아니다. 동일 weights이면 aggregate가 충분하다는 양성 대조도 통과했다. 실제 expanding consumer에는 stage times/weights·energy measure의 별도 owner 계약이 필요하다. Static jet·aggregate만으로 그 승인을 대신하지 않는다.

## 검증과 유지 상태

새 focused tests28 PASS, Python5파일 syntax PASS. 1시험은 실제 assertion RED→GREEN이고27시험은 tests-after다. 원 F04D24시험/272·1512·50 대조, F05 history/checker, FLRW06, 기타 원자 campaign은 반복하지 않았다. 새 reference root solve0, numerical differentiation0, owner box expansion0, receiver mutation0이다. 독립 human/agent review나 proof-assistant 검증은 없다.

CR_OFF_FASTEST,precision atomic PARKED,G02=UNRESOLVED,physical production HOLD,capture=false,all_bound OPEN,b_grid NO_GO와 CR-dispatch 관측null을 유지한다. 실제0회 callback의 증거로 바꾸지 않는다. CR-on/full-K/318patch/소비된 원자 승인은 사용하지 않았다.

## 정본 패키지와 실제 이중백업

파일 BASS_CR_CHAT_F04E_20261005_v1.zip
bytes404871
SHA256 b88932c7a2337972df19231755491725b7090bab347d203fa514fce2717b7cdd
ZIP101members/100payload SHA256·size·CRC local검증.

Drive success ACK 및 metadata readback: id1ratNamadO6AH1Idrc079nE74m1CEGinP, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ, name/size404871일치.
Dropbox completed: id:BSpOijBcT10AAAAAADyuAQ,size404871,modified2026-10-04T20:49:36Z,path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04E_20261005_v1.zip.

동일 immutable local archive를 create-only로 저장했다. R1 UPLOAD_VERIFIED(ID/name/size/path또는parent)이며 remote checksum은 응답에 노출되지 않았다. 새 ZIP의 remote full restore/독립 remote bytehash는 실행하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. Source/data3파일의 실제 회수·Git blob 일치와 이 upload 의미를 구분한다. 코드·전체 보고·28시험·실행로그·정확JSON은 immutable ZIP의 정본이고 이 문서는 summary/sync다.

읽기 순서는 TASK_RETURN.json, SOURCE_BINDING.json/INTAKE_ACK.json, REPORT_KO.md, results/binding01/SUMMARY.json이다. logs/ENVIRONMENT.json은 설치 전 snapshot이며 최종toolchain상태는inputs/FINAL_TOOLCHAIN_STATE.json이다. 이미 완료한 native 관측은 반복할 필요가 없다.

다음 optional F04F_EVENT_OBSERVABLE_ENCLOSURE_OR_STAGE_OWNER_BINDING은 live F08 요구를 먼저 읽고 기존 source/root boxes에 event+escape observable enclosure만 추가하거나 actual stage 소비 계약을 read-only 연결한다. 새로운 원 parent나 uniform certificate를 발명하지 않으며 F08 source owner를 침범하지 않는다. 이번25bit검사와28시험을 단순 동기화를 위해 반복하지 않는다. 새 mandatory gate가 아니다.
