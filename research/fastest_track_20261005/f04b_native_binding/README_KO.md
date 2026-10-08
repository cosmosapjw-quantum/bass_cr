# F04B: 실제 native 저장 비트와 제한된 root certificate 연결

F04A의 준비된 exact-real 코드를 그대로 사용하여, 실제 F03 기본 모형·초기 상태·full BE endpoint의 binary64 비트를 연결했다. 기존 로그가 보존하지 않은 좌표만 새 관측 wrapper로 확보했다. 원본 `hhe_events.rs`, `microstep.rs`, `thermal.rs` 및 기본 `StepControl`(80 iterations, residual tolerance 1e-14)은 변경하지 않았다. 관측 대상은 dt=1e8 s의 full/discarded 후보 하나다. adaptive 호출, accepted two-half 갱신, history 실행은 없다.

새 관측 1회, 재시도 0회. endpoint는 F04A의 기존 반경 1e-8 cube 안에 있다. 상속한 exact-rational preconditioner·contraction bound와 실제 잔차를 사용한 root 거리 상계는 1.4758856593968439e-18이다. 성분별 상계는 (1.4758856593968439e-18, 2.866750739234034e-19, 1.0659650356755103e-19)다. 소수는 표시값이며 `evidence/BINDING_RESULT.json`의 분자·분모가 정본이다.

실제 초기 u와 F04A의 exact-real 초기화 공식 사이에는 -5.467016701323603e-33 erg cm^-3 차이가 있다. 이를 0으로 처리하지 않았다. fraction residual/Jacobian은 old.u에 의존하지 않으므로 기존 root proof를 상속하고, thermal 상자는 실제 old.u로 다시 평가했다. B 하한은 2.2673539065737397e-16 erg cm^-3로 양수다. 실제 7좌표의 exact-real scaled residual 최대는 1.1705073952391452e-16이고 native reported norm은 1.1705736578619066e-16이다. 실제 photons와 algebraically eliminated photons의 차이 및 RHS 산술 차이를 구분한다. 작은 잔차를 정확 0으로 반올림하지 않는다.

증명 사용: T=x-A G(x)의 기존 cube contraction q<1에서, cube 안 native endpoint y에 대해 ||y-root||inf <= ||A G(y)||inf/(1-q). E_ij=sup|(I-A DG)_ij|를 사용하면 성분 i의 오차는 |A G(y)|i + sum_j E_ij * 위 inf bound 이하이다. 단일 dt·고정 합성 모형의 exact-real root에 관한 결론이다. 기존 certificate 상자의 외부 root, parameter correlation, floating 실행 전체의 rounding enclosure, continuous ODE error, full/half controller, canonical REI-F04 전체 인증은 포함하지 않는다.

신규 binding 방어 시험 10개 PASS. model/dt/control/old-fraction identity 변경, cube 이탈, NaN/Inf, 중복 좌표 및 decimal/bit 불일치를 거절한다. 기존 27시험·F00–F03 suite·FLRW02 E2/E3·m64/9점은 반복하지 않았다. compiler와 모든 자식 프로세스를 포함한 peak RSS는 138240 KiB, 관측 driver wall은 0.593175895 s이며 endpoint 단독 RSS나 HPC scaling으로 해석하지 않는다.

다음은 owner가 지정한 joint-parent box가 있을 때만 확장한다. accepted half1→half2 initial-box 전달과 endpoint/event binding은 별도이며 이번 full 후보로 대신하지 않는다. 새 consumer callsite·edge closure가 없는 FLRW03 production integration도 시작하지 않는다. 새 FLRW02 모듈과 최종 review를 수신했으며 종료된 검증은 상속한다.

CR-F0=WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING, 실제 source/loader/callback 관측은 null. 원자 lane PARKED, G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO를 유지한다. 직접 ChatGPT 스레드 ACK는 확인되지 않았으며, 지정된 스레드 https://chatgpt.com/c/6abfa205-dbe8-83ee-969b-0e00111c9404 의 동기화 자료는 이 Git 반환 및 클라우드 ZIP이다.

실행기는 새 output 경로만 허용한다. `run_binding.py --source ORIGINAL_THREE_SOURCES --reference VERIFIED_F04A_PACKAGE --rustc PINNED_RUSTC --output NEW_DIRECTORY`는 새 관측용이며 이번 완료 결과를 재현하기 위해 다시 실행할 필요가 없다. 읽기 전용 검토에는 보존된 `endpoint_bits.stdout`, 결과 JSON 및 입력·library hashes를 사용한다.
