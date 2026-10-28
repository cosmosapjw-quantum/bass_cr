# R2 근거와 재사용 대응

## 적용할 입력

이번 단위는 PR112의 실제 저장된 He atomic attribution과 event-union consumer를 byte identity로 재사용한다. `inputs/INPUT_MANIFEST.json`의 열 파일은 복원한 불변 SOURCE에서 가져왔으며 매 단계 preflight에서 bytes/SHA를 다시 확인한다. 이것은 저장된 데이터의 확인이며 source fit, proton quadrature, source projection, RR 계산의 재실행이 아니다. 3200 active atoms와 cutoff ghost는 원래 키·에너지·가중치·birth partition을 유지한다.

| 재사용 근거 | 이번 대응 | 바뀌지 않는 경계 |
|---|---|---|
| `cr_parent_event_native25.../ATTRIBUTION_ARRAYS.npz` | He atom coefficient `A_a`, energy, four birth bins | 저장 binary64를 정확한 유리수로 읽는다. 새 연속 분포를 추정하지 않는다. |
| `cr_proper_injection.../ACTUAL_SOURCE_RECORDS.json` | canonical source identity와 `q_a(t)=t A_a` | proper `[0,10^10]s` 밖은 unknown; source normalization과 target factors 추가 적용 없음 |
| `cr_he_event_union.../implementation/event_union.py` | `AtomBundle`, `Event`, pinned loader, `binding`, `claims_by_partition`, `consume_event_union` | 같은 상태·frame·clock·source와 once-only 규약을 그대로 사용 |
| PR112 CONTRACT/ADMISSION/SCIENTIFIC_SUMMARY/C09/primary | 완전 graph 상한, `(C,0,-C)` species correction, native conversion | 기존 판정은 바뀌지 않은 가정 아래 재사용; 새 graph 제약의 검증은 별도로 수행 |
| PR112 BUDGET_CLOSEOUT와 actual final receipt | 과거 완료·실패·전달·예산 기록 | 과거 charge4.710179/40, 잔여 NONTRANSFERABLE, science allowance0 유지 |
| saved RR primary result | 별도 once-only recombination port | 새 source-parent correction에 다시 더하거나 RR를 재계산하지 않음 |

`load_pinned_source`는 NPZ SHA 및 형태를 확인한 뒤 저장된 binary64 각 값을 `Fraction.from_float`로 정확히 올린다. 원래 `AtomBundle`의 process-local attestation과 content digest를 새 wrapper에서도 통과해야 한다. 같은 SHA 문자열만 복사한 synthetic fixture를 canonical source로 승격할 수 없다. 새 계산의 부동소수점 잔차 0은 물리적 source-model 오차 0이라는 뜻이 아니다.

## 최신 owner와 백업의 종합

관련 repo의 현재 본문에서는 같은 retained CR source에 맞는 exclusive atomic-He kernel 또는 outside-partner response를 새로 확보하지 못했다. 이는 읽은 source 집합의 관측 결과다. 세계 문헌이나 모든 비공개 대화에 데이터가 없다는 주장을 하지 않는다.

중앙의 `df806909aee8f25efcfa4faeefca77a5271f546c`는 이전 M 뒤에 REC 반환을 추가한 commit이다. DAG blob은 그대로이고 현재 반환의 `/preservation`이 **28/88**, delta0을 명시한다. 다른 owner의 로컬 완료 수와 중앙 qualified 수는 구별한다. REI 실제 C8 본문이 오래된 C7 백업보다 최신이며, REC recovery commit이 오래된 PR 설명의 미게시 상태를 정정한다. HE bare-alpha angular reference, BASS periodic-lapse transport, WU molecular rate closure, VigilODE preregistered solver는 각각의 입력·상태·예산을 가진다. 이들을 CR100K atomic joint data로 가져오지 않는다.

접근 가능 repo/branch pagination, 관련 owner 본문, 지정 backup tree, 저장 문서 및 latest metadata를 조사했다. 원본 전체 대화 검색은 실제 서비스 오류였다. 전체 Drive all-file inventory는 PARTIAL이다. 소유 파일의 최신 관련 구간과 전역 과거 목록의 terminal 여부도 `BACKUP_AND_DIALOGUE_SURVEY.json`에서 분리한다. 개인·무관 raw inventory와 signed URL은 공개 Git 또는 전달 archive에 수록하지 않는다.

## 문헌에서 직접 채택하는 범위

SciSpace와 Exa의 실제 검색 및 원전 fetch를 `PRIMARY_SOURCE_MAP.json`과 `SEARCH_COVERAGE.json`으로 추적한다. Native projectile1–4MeV는 선행 source mapping의 재사용이다. 이번에 원시 projectile weight 함수를 재유도하거나 joint kernel을 적분하지 않았다.

- Andersen et al. 1986의 publisher abstract는0.5–5MeV proton/antiproton single/double total cross sections를 다룬다. Source 에너지와의 겹침만으로 selected0.1–10eV 두 전자의 joint 분할이 정해지지 않는다. [원전](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.57.2147)
- Ambrosio2015의 읽은 theory Eq.(13),(14)와700keV 사례는 두 전자 joint observable의 정규화·자유도 구별에 쓰인다. 실제 native source bytes로 채택하지 않는다. [원전](https://doi.org/10.1103/PhysRevA.92.042704)
- Behrend의 fractional b-matching 원고 §§1.1–1.5는 비음수 edge assignment와 vertex incidence 조건의 선행 수학이다. §1.3은 loop를 한 번 세므로, 여기의 물리적 diagonal double event에는 두 electron legs를 명시적으로 적용한다. 일반적인 fractional matching 정리를 새 최초 성과로 주장하지 않는다. [저자 원고](https://orca.cardiff.ac.uk/id/eprint/43147/7/BehrendFractionalPerfectbMatchingPolytopesFinal.pdf)

Root는 Behrend 원고와 Andersen abstract를 별도로 직접 열어 위 범위를 확인했다. Root web의 Ambrosio DOI open은 접근 오류였고, 이미 확보한 Exa 본문 읽기를 재사용한다. 원전별 abstract/full-text/발견-only의 차이를 보존한다. Wolfram context 요청의 초기 일반 entity 응답은 이 연구의 증명 근거로 채택하지 않았다. R7의 명시적 bounded CAS 출력은 별도로 기록한다.

## 이번에 새로 닫아야 할 의무

주어진 graph의 정확한 상한과 primal/dual 증명서, 모든 허용 C 및 조건부 fixed-d의 atomic 구성, unchanged consumer에 연결되는 유리수 conservation, graph/source/state binding 거절 규약을 새로 증명·구현·독립 검증한다. 실제 kernel, 물리적으로 관측된 graph, actual C/D, outside partner, donor work, EOS/T, full physical native25는 이번 수학적 witness와 별개로 null을 유지한다.
