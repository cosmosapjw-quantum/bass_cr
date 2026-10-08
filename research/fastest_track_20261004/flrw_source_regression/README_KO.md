# FLRW02의 실제 함수에 연결한 유한 회귀

`probe.rs`는 rei_bianchi의 실제 `hhe_rhs`, `homogeneous_photo_rates`,
`photon_rates`, `gamma_species`를 호출한다. 수신측 구현은 수정하지 않는다.
`verify.py`는 주어진 f64 입력의 정확유리수 사건 장부와 별도 선언한
spectral profile을 기준으로 출력값을 비교한다. 새 solver나 history를
구현하지 않는다.

입력 receiver commit은 `c1d7f89c8abc90a6adf971390f2bce7ae7530a23`이다.
게시 전 추가된 `9455c2a`까지의 변경은 REC-PB02 수령 문서뿐이며 관련 Rust
source는 동일했다. 같은 shared FLRW02 작업의 L/P 범위에 기여하며
별도의 중복 연구 캠페인을 만들지 않는다.

실행 결과는 108개 기록, 2,137개 수치 assertion PASS다. 최대 scaled 차는
`3.9452419428893457e-16`이며 유한 f64 comparator 기준은 `4e-14`다.
이 기준은 기존 local `<2e-4`와 public width `<2e-3`를 대체하지 않는다.

- L: 실제 charge-derived 전자밀도, 종 사건률, photon/atom/energy 장부,
  순수 H 재결합 RHS를 검사했다. exact static curve의 18점에서 RHS만
  평가했다. 적분이나 implicit step은 실행하지 않았다. fixed-ne 대체가
  dynamic-ne와 다름을 12개 음성대조에서 확인했다.
- P: F01 comoving-to-proper 변환과 photon loss/volume=종 event 합을
  검사하고 같은 density/energy/sigma 입력의 F03 event와 대조했다.
  sigma는 raw-value provider의 출력이다. 기존 F01 원자 fit accuracy
  suite는 재실행하지 않았고 새 physical accuracy를 주장하지 않는다.
- Edge: `N_nu=A exp(-nu)`, physical edges `[1,2,4,8,16]`을 잠갔다.
  내부 edge cancellation, lower-threshold loss와 실제 API source 인자를
  통한 명시적 upper inflow를 검사했다. 상단 유입 누락 및 임의 계수
  `redshift_coeff=1`은 해당 profile 복원에 실패한다. 현재 API에 새
  edge hook이 생겼다는 뜻은 아니다. lowgroup effective-MFP 흡수는
  실제 유한 값으로 장부에 남겼다.
- Empty photons: emissivity가 있어도 초기 Gamma는 정확히 0이며 photon
  inventory derivative에 source가 남는다. 기존 homogeneous F03 map에
  external/diffuse source가 구현됐다고 표시하지 않는다.

팽창에 따른 분율 dilution 상쇄는 정확 대수만 검사했다. 실제 F03는
H=0이며 H!=0 consumer 검증이 아니다. Q/phase averaging API가 없어
`Q_lane=NOT_APPLICABLE_TO_HOMOGENEOUS_STATE`로 남긴다. 분율을 QV로
재명명하지 않는다. diffuse ionizing-photon number, full FLRW consumer,
Peebles closure, uniform remainder/root certification과 physical admission은
완료하지 않았다. CR off는 F00 선언으로 확인했지만 실제 dispatch/load/
callback 계측이 없어 CR-F0 acceptance를 만들지 않았다.

재현 명령은 아래와 같다. 새 output directory를 사용하며 source hash가
다르면 실행을 거절한다. 원 실행은 Rust 1.94.1, opt-level=0,
codegen-units=1, CPU affinity 한 개였다. compiler/library/native SHA와
각 명령의 exit/log는 `evidence/` 및 `RESULTS.json`에 있다.

```bash
python3 verify.py \
  --receiver /absolute/pinned/rei_bianchi \
  --rustc /absolute/rustc \
  --output /absolute/new/finite_regression
```

G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN,
b_grid=NO_GO 유지. 기존 m64/9점/M9/중심점/full-K 및 과거 suites,
소모된 승인과 318 patch는 재사용하지 않았다. Bianchi dynamics와
수신측 interval/production 구현은 rei_bianchi 소유다. 독립 agent/human
review는 수행하지 않았고, 같은 agent가 원 구현과 다른 유리수 비교를
실행한 범위다.

ChatGPT 대상은 기존 사용자 지정
`https://chatgpt.com/c/6abfa205-dbe8-83ee-969b-0e00111c9404`를 유지한다.
직접 대화 전달은 미확인이다. 같은 Git branch의 코드·반환·실제 원격
backup receipt를 통해 파일 기반 상태를 동기화한다.
