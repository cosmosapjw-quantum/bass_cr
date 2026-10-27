# C10 최종 미시 공급자 확인

판정: **WU의 새 source-reference 진전 1건을 반영하고, 이번 고정 HeIII atomic RR consumer에는 material change가 없음을 분리했다.** REC·HE 선택 HEAD는 기존 pin과 정확히 같다. 과학·테스트·C9 reference 재실행은 0이다.

| 공급자 | 실제 summary에서 선택한 branch | 이번 HEAD | 판정 |
|---|---|---|---|
| WU | `research/provider-registry-20261025` | `bfdeed676617c8b75ed81ac5e79e800fa69f83db` | 기존 pin에서 2 commits 전진 |
| REC | `research/program-expansion-20261025` | `4a8e541030ee2cbd02e26ba671083b705d309d49` | 기존 pin과 exact equal |
| HE | `research/program-expansion-20261025` | `ac6042a6b0610b09d0576538767ee0299389a5eb` | 기존 pin과 exact equal |

## WU의 실제 변경

WU는 기존 `87933da5654bb2e4d93f7de4341df5e0fa0f8716` 뒤에 target6 EXFOR source와 별도 delivery commit을 추가했다. 실제 compare의 92개 changed files는 AGENTS와 `research/provider_registry_exfor_target6_20261027/` 아래에 있다. 새 AGENTS 상단과 현재 SCIENTIFIC_ADMISSION을 읽었다.

새 내용은 He4(gamma,d)D의 공식 EXFOR 공급자 4개·원 수치 36행이며 SIG24행, DA12행, 별도 보조 E2 7행을 구분한다. 원19 target/28방향의 primary-source 참조는 이제 **28/28**이다. 이는 자료 접근성의 진전이며 empirical rate, nuclear Q, state/branch/domain, deposition, consumer 및 activation은 계속 false다. 실제 MeV photon 소비자와 beam/angle/identical-D normalization 등의 결속이 남아 있다.

이번 CR의 고정 Verner HeII 표·point provider, 54.42eV/d=1, n_HeIII, 저장 HeI K0 및 조건부 isotope mapping을 교체하는 변경은 아니다. 따라서 새 핵반응 자료를 atomic <=50keV RR 공급자로 소비하거나 이번 계산을 다시 실행하지 않는다. Root의 최종 frontier 설명에는 WU source reference의 27/28→28/28 진전만 별도 반영하면 된다.

## REC·HE의 동일성 및 한계

REC는 같은 선택 commit에서 AGENTS.md를 다시 요청했으며 **HTTP404**를 받았다. 이를 unavailable로 보존하며 다른 브랜치의 지시로 대체하지 않았다. 기존 HD35Hz gate와 H5 physical bound/epsilon의 미완료 범위를 재사용한다.

HE는 commit 및 해당 AGENTS Git blob이 동일하다. 과거 로컬 snapshot에 serialization newline 하나가 더 있어 decoded text의 raw SHA는 다르지만, trailing newline을 제외한 내용은 같다. 이는 provider 변경이 아니다. Conditional Tstar50–50000K, physical provider 미채택, HE101 PARTIAL_EXPORT 및 remaining0을 유지한다.

PR236의 donor T/nb나 unmerged32/88를 CR bath 또는 central27/88에 옮기지 않았다. 중앙/전체 브랜치 재조사는 root의 작업으로 남겼고 중복하지 않았다. N6/N7·과거 UNKNOWN_NO_ACK·예산·caloric/heating 경계는 그대로다. 실제 URL, SHA/blob metadata, 404 원문, WU 새 범위와 미완료 의무는 REFRESH.json에 기록했다.
