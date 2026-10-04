# CR-off fastest 재개: F03 source 수신 및 사건-잔차 투영

사용자의 fastest-track 재개 요청을 적용한다. 기본 경로는 CR_OFF_FASTEST다. Peebles/FLRW의 완료 유도는 비교 기준으로 보존하고 canonical baseline을 대체하거나 필수 재시험으로 만들지 않는다. 정밀 CR 원자 lane은 PARKED다.

## 현재 source와 실제 작업

bass_cr 시작/게시 전 HEAD=3e52c30943c50fa111d319dac2499eac13ec5e48.
rei_bianchi source 기준=c1d7f89c8abc90a6adf971390f2bce7ae7530a23, branch=forward/rust-reion-kernels-20260922.

F03 반환과 실제 hhe_events.rs, microstep.rs, lib.rs, Cargo.toml, hhe_solver_binding.json, CODEX_SYNC_KO.md를 읽었다. actual hhe_rhs, implicit_hhe_step, BE endpoint residual이 존재한다. 과거 'consumer 자체 부재'를 현재 blocker로 재사용하지 않는다. F03의63 crate tests/8 frozen/7 boundary assertions 및 refinement 기록은 계승했고 재실행하지 않았다.

현재 F03는 static/proper HHe, 고정 합성 계수, 3group photons, Case-A energy escape 모형이다. actual CR switch/provider-loader/callback interface는 읽은 F03 entrypoint에 없다. 소스가 CR 항을 포함하지 않는다는 해석을 실제 off-switch 호출 검증으로 바꾸지 않는다. CR-F0는 WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING이며 source/load/callback 관측값은 null, CR_OFF_ACCEPTANCE.json 미생성이다. owner의 다음 canonical 구현은 REI-F04다.

## 직접 유도한 source-bound 보존 및 잔차식

y=(xHII,xHeII,xHeIII,u,N0,N1,N2), n_e=nH*xHII+nHe*(xHeII+2*xHeIII), wN=(nH,nHe,2*nHe,0,1,1,1).
P_ag는 동일 endpoint의 primary photo events, C_a/R_a는 collision/recombination event density rates다. hhe_rhs를 정확 산술로 해석하면

    wN*f = sum_a(C_a-R_a)
    d(n_e+sum_g N_g)/dt = sum_a(C_a-R_a).

각 광흡수 사건은 photon 한 개 감소와 electron 한 개 증가를 만든다. 현재 tracked photons에는 escaping recombination photons가 재주입되지 않는다. 이 관계를 CaseB/명시적 diffuse photon 모형으로 자동 옮기지 않는다.

energy row wE는 u+binding+sum(Eg*Ng)의 계수이며, 반환 escaped energy까지 포함하면

    wE*f+f_escape=0.

이는 source의 synthetic 3kBT/2 recombination thermal closure에 결합된 장부 항등식이다. 물리적으로 정확한 냉각계수라는 증명은 아니다.

저장 endpoint y0,y1와 RHS fhat, 반환 사건 Cevent/Revent를 같은 IEEE754 bit의 유리수로 읽는다.

    r=y1-y0-dt*fhat
    eps_source=wN*fhat-(sum Chat-sum Rhat)
    eps_event=(sum Cevent-sum Revent)-dt*(sum Chat-sum Rhat)
    DN=wN*(y1-y0)-(sum Cevent-sum Revent)
      =wN*r+dt*eps_source-eps_event.

energy에 대해서는

    r_escape=escape1-escape0-dt*fescapehat
    eps_E=wE*fhat+fescapehat
    DE=wE*(y1-y0)+escape1-escape0
      =wE*r+r_escape+dt*eps_E.

따라서 solver residual, source 산술/같은-site 비일치, 반환 event assembly를 분리할 수 있다. scalar defect만으로 그 원인을 반올림이라고 확정하지 않는다. 각 항 절댓값합의 조건부 상계도 구현했다. exact diagnostic normalization과 원 Rust의 floating residual_norm은 별도로 기록한다.

Accepted two-half의 중간 상태는 telescoping되지만 discarded full trial의 events를 섞지 않는다. 실제 two-half runtime exporter는 이번 v1에 없으며 단일 BE endpoint exporter만 제공한다. 정적 고정 nH/nHe의 식을 expansion/history로 확대하지 않는다.

dx/dtau=-x^2,x0=1,dtau=1의 반례에서는 BE endpoint=(sqrt5-1)/2, BE residual=0이지만 exact ODE endpoint=1/2다. 작은 algebraic residual/장부 보존만으로 연속해 오차나 F04 interval/root certificate를 닫을 수 없다. 이 반례는 해석식만 확인했으며 ODE 실행은0이다.

## 실제 검증 및 명시적 미완료

새 Python exact analyzer16 tests PASS; 별도 SymPy6 conditions True. 첫 기능은 assertion RED->GREEN, 나머지는 구현 후 focused tests다. 최초 fixture expected-value 오기는 구현 전에 정확 산술로 교정했고 초기/수정 RED 로그를 모두 보존했다. 별도 인간/agent/proof-assistant review는 없다.

이 환경의 Python/container는 작동했다. rustc/cargo는 PATH 및 제한된 알려진 경로에서 찾지 못했다. 직접 raw GitHub 네트워크는 DNS 실패다. 실제 receiver Rust build/run=0, atomic integrations=0, old suite replay=0, cosmological histories=0.

source/event_projection.py와 tests/test_projection.py는 실행 검증했다. runtime/export_endpoint.rs는 실제 공개 F03 함수를 호출하는 신규 단일-step probe 소스지만 DRAFT_NOT_COMPILED다. runtime/run_probe.py는 Python syntax만 검증했으며 end-to-end 실행은 NOT_VERIFIED다. 이를 production 완료로 부르지 않는다. 한-step 선택은 원자/HPC 실행 승인과 무관하고, 기존 F04 작업에서 필요할 때만 source 검토 후 제한적으로 사용한다. 이 보조 도구가 F04의 새로운 선행 gate는 아니다.

## 종료 전 동기화

rei_bianchi가9455c2a3cbf2ce5ebaba28e9bfb1dfe79aed0efa로 전진했다. compare 결과2개 commit/10개 REC-PB02 docs-only 경로이며 F03 crate는 바뀌지 않았다. REC owner의 Peebles Rust reference 게시 인계는 읽었지만 REC archive/native 검증을 재실행하지 않았다. 그 게시도 실제 REI adapter binding 완료가 아니며 현재 F03 Case-A를 치환하지 않는다.

## 정본 코드·보고서·증거 패키지

파일=BASS_CR_FASTEST_F03_LEDGER_20261004_v1.zip
bytes=24566
SHA256=810c0eb30092878443d7c74f4d0c5d7f9309d265bee910332a0a1e530c81261b
ZIP22 members/21 payload SHA 확인.
Dropbox ID=id:BSpOijBcT10AAAAAADyJqw
Drive ID=18WpSFeRiSgAp30OxF6gbX-Kk2TjViTyu

같은 bytes의 패키지를 두 provider에 create-only 저장했고 ACK/ID/name/size를 확인했다. R1 UPLOAD_VERIFIED이며 remote full restore는 하지 않았다. 이 Git 문서는 요약/동기화이며 코드·시험·실행로그의 정본은 immutable package다. 한 인증된 mirror만 직접 회수하며 사용자 재업로드를 요구하지 않는다.

## 다음 작업

Canonical owner는 REI-F04를 계속한다. 실제 off-dispatch hook이 생기면 이 스레드는 그 entrypoint에서 source/loader/callback0을 focused 검증한다. 다른 source 변화 없이 동일 blocker가 유지되면 재시험/새 ZIP/원자 재시도를 반복하지 않는다. 별도 Peebles/FLRW 검증은 유지된 자료를 실제 adapter가 필요할 때 적용하며 원 모형을 소급 바꾸지 않는다.

G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO 유지. 기존 S-only 두 window 상계5.599633283869504e-17 및7.49726779045559e-17 ta^-1을 그대로 상속한다. 새 physical provider·CR-on·full-K·R4AQ·과거318patch 및 소비된 승인 확장은 없다.
