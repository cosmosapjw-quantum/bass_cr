# CR-PHYS01 후속 Codex 시작문

`HANDOFF.json`, `DAG.json`, `REPORT_KO.md`, `review/INDEPENDENT_REVIEW.json`, `publication/PUBLICATION.json`부터 읽어라. 새 provider의 존재와 전 우주론 이력의 admission을 구분하라. 이전 R17 photon source 또는 p/H CX 장부로 되돌아가지 마라.

이번 전달물은 이미 구현된 실제 CR proton source → H/He proton impact → secondary electron → 종별 ionization/excitation/heat → REI local derivative다. 기존 frozen HM12 계약의 CR=OFF와 원 정밀 atomic lane은 보존했다. 동일한 코드에 대한 완료된 검사를 무조건 반복하지 말고 먼저 exact source와 새 환경을 확인하라.

## 빠른 재개

1. PUBLICATION.json의 bass_cr 및 rei_bianchi branch/commit을 checkout한다. bass_cr의 `research/cr_phys01_20261010/`가 provider 패키지다.
2. Python은 NumPy가 필요하고 비교 검산은 SciPy를 사용한다. provider 폴더에서 `python src/provider.py`를 실행하면 `evidence/CR_PACKET.json`, `SOURCE_MANIFEST.json`, `PROVIDER_AUDIT.json`이 생성된다. 새 환경에서 출력을 바꾸면 기존 Rust pin을 그대로 채택하지 않는다.
3. 필요한 변경이 있을 때에만 `python -m unittest discover -s tests -p 'test_injection.py'` 및 `python tests/check_provider.py`로 영향 범위를 검증한다. 원자료 해시 거절이나 영역 밖 입력 실패를 fallback으로 우회하지 않는다.
4. REI의 `rust/rei_microphysics`에서 `cargo test --locked --test axisym_cr_deposition`와 `cargo run --locked --example cr_deposition_probe`를 이용한다. 정확한 테스트 target 이름은 Cargo의 실제 파일과 전달된 native command receipt를 따른다. inherited warm binary receipt는 source가 바뀐 새 binary 승인으로 재사용하지 않는다.
5. 공개 ON receiver는 전달된 gas/time/background/source packet 한 점을 소비한다. 이를 전체 source-dependent solver 또는 history loop로 오인하지 않는다. 무리한 자동 루프 전에 DAG의 state-dependent provider/secondary-delay 작업을 택한다.

## 다음 병렬 작업

- `CR-PHYS02-DELAY`: secondary e− 수송 또는 시간 응답을 계산해 현재 quasistatic terminal model의 국소성·시간 지연 조건을 검증한다. 317년 turn-on에 FS10 침적이 순간 발생한다고 가정하지 않는다.
- `CR-PHYS03-COMPOSITION`: 실제 공급원과 재배포 조건을 확인한 독립 H/He 분율·온도·abundance response로 확장한다. 원 FS10 생성 YHe가 정확히 .248이었다고 채우지 않는다.
- `CR-PHYS04-LOSSES`: CR proton Coulomb, primary excitation, HeII target 및 1–4 MeV 밖 채널을 추가한다. 현재 원장을 all-energy stopping으로 승격하지 않는다.
- `CR-PHYS05-RECEIVER`: 위 공급원 계약에 맞춰 one-point pin을 state-dependent opt-in receiver로 일반화한다. frozen HM12 warm ON/OFF 계약을 수정해 우회하지 않는다.

원 핵/원자 정밀 연구는 별도 확장 lane으로 남겨 둔다. H/He table-assisted CR provider 완료를 RCT/HH gate 완료로 전달하지 말고, BASS에는 실제 새 history가 생긴 후 새 source identity의 electron snapshots를 전달하라. repo push는 사용자가 이번에 승인했지만 main merge·새 대규모 캠페인·물리 accuracy certificate를 의미하지 않는다.
