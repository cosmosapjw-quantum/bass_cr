# BASS_CR NCP 반환 (2026-10-08)

실제 R15 계산으로 첫 macro [0,1.25e9] proper s의 **fixed-six-birth FT03 shadow continuum − 실제 native gas-fraction 선형 재구성** Thomson 광학깊이를 조건부 인증했다. 아래 표시 구간은 보수적으로 바깥쪽 반올림했고 정본은 RESULTS.json 및 GOAL_LEDGER.json의 exact rational이다.

- tau_native ≈ 2.5541305163341501e-9 (무차원).
- signed delta_tau ∈ **[1.84951686695075e-17, 2.10105887626795e-17]**: 이번 고정 목표에서는 0을 제외한다.
- tau_cont ∈ [2.554130534829318e-9, 2.554130537344740e-9].
- 독립 DOP853 optical 진단 delta_tau=1.9731045074324378e-17, 전32 prefix 포함 확인.

첫 cell의 R14 rational 결과는 동결 계승하고 재실행하지 않았다. 나머지31 cell의 실제 전시간 interval 496개에서 새 광학 잔차 functional을 계산했다. 이전 signed state error 및 native interface 차를 보존하고 여섯 고정 photon birth만 추가했다. tau는 birth에서 계속 누적한다. forcing, incoming signed optical contribution, full nonlinear RHS feedback bound를 cell별로 나눠 저장했다. 이 remainder는 linear feedback까지 포함하며 Hessian-only bound가 아니다.

인증은 기존 donor Decimal60 directed arithmetic/outward exp-ln과 Picard/Jacobian 증명에 조건부다. Fraction의 exact Taylor5/6 커널로 광학 goal만 새로 계산했다. 독립 검산은80자리 exponential 구적 및 새 augmented optical IVP이며 proof premise가 아니다. 독립 interval backend/proof assistant/물리 원자율 인증은 하지 않았다. source quadrature, observer tail, Bianchi, 전체 이력, discrete-family tau는 여전히 미인증이다. FT03와 Grackle를 하나의 식으로 결합하지 않았다.

P0: GitHub handoff HEAD58295e59를 fetch하고 새 worktree /root/bass_cr_ncp_r15와 branch research/ncp-r15-20261008을 만들었다. 원 dirty checkout의 기존 두 결과 디렉터리는 보존했다. local rclone 실행파일/설정은 없었으나 기존 Dropbox connector로 네 ZIP을 회수했다. manifest size/SHA256/CRC 및394개 extracted member byte identity를 확인했다. 최초 BLOCKED_INPUT 기록도 보존했다. .codex/readback-policy.json은 해당 commit에 없고 docs/READBACK_POLICY.md를 적용했다.

자원: Xeon Gold5220, affinity CPU0–63, RAM125GiB, 시작 여유디스크 약60GiB, cgroup ancestor CPU/RAM finite cap 없음. coordinator1 CPU와 RAM24GiB reserve, 과학worker1/BLAS1로 제한했다. interval9.58s/peakRSS29696KiB; 독립 최종67.68s/88288KiB. MPI/NCP64 speedup은 실행·주장하지 않았다. GCC/GFortran13.3, OpenMPI4.1.6, Python3.12.3; Rust/Cargo/rclone은 미설치다. 새 native 코드가 없어 build는 해당없음이다.

검증: focused assertion RED3개(exit1)→GREEN3개(exit0); 추가 source/clock/birth/variant corruption 포함 최종8 tests PASS. R13선택payload52개와 R6library source31개 identity 확인. 독립 중첩구적의 캐시증가를 중단(exit130)했고, 다음 실행의 NumPy boolean JSON 실패(exit1)를 수정했다. 두 실패로그 모두 보존했고 최종검산 exit0이다. 독립 사람/별도agent 리뷰는 미수행이다.

P2: BLOCKED_OWNER_INPUT. R13전체point/R6native evidence만 있으며 새로운 동일 Grackle model·source·clock·owner accepted stage와 전시간 state/moment 자료는 없다. 기존96+48point와 R6시험을 반복하지 않았다. 필요한 자료는 GRACKLE_READINESS.json에 기록했다.

P3: BLOCKED_INPUT. authoritative BASIS.npz/JSON/SCIENCE_CONTEXT 및 별도 CANDIDATE, native manifests의 pinned 외부경로는 확인했으나 actual bytes는 없다. scientific PASS 및 새 operator call은0이다. 정확한 hash/path는 G02_READINESS.json에 있다. 기존 완료 central derivative 검증도 반복하지 않았다.

CR_OFF_FASTEST, G02=UNRESOLVED, all_bound=OPEN, b_grid=NO_GO, capture=false, physical/production=HOLD를 유지한다. owner ACK/global CR counter/observer tail=null. REI BRIDGE14 및 타repo science/수정/push는0회다.

재현은 reproduce.py --stage VERIFIED_STAGE --output NEW_OUTPUT --independent를 사용한다. 새 stage는 --source-dir ORIGINAL_ZIP_DIRECTORY를 추가한다. requirements.txt에 이번 검산 버전을 고정했다. ZIP은 source commit 이후 create-only로 만들며4개 원본 ZIP과 코드·결과·로그를 포함한다. 실제 commit/tree/remote ref, packageSHA256/size, Drive·Dropbox provider ACK/ID는 **봉인 후 별도 DELIVERY_RECEIPT.json**에만 기록한다. 이 문서의 science checkpoint 단계에서는 배포/백업 성공을 미리 주장하지 않는다.
