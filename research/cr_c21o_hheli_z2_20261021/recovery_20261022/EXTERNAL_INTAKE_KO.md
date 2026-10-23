# C21O 재개: 최신 외부 결과의 범위를 구분한 수용

조사 마감: 2026-10-22 KST (실제 UTC 시각은 JSON에 기록).
선택 범위는 `physmath-research-loop 1.3.0`의 **C10 복원·인계**다. 새 ODE, 기존 과학 계산 재생, 네이티브 빌드, 성능 벤치마크, NCP 접속은 모두 0이다. 연구 source나 다른 owner의 작업을 변경하지 않았다.

## 1. 실제 조사 범위와 현재 권위

복원한 C21O의 2026-10-21 14:42:28 UTC 목록 1,246개와 현재 7개 repo의 advertised heads 1,255개를 대조했다. **추가 9, 기존 head 변경 0, 삭제 0**이다. Git CLI의 sandbox 프록시 접속 실패는 보존했고, 허용된 read-only network 경로에서 일곱 `ls-remote --heads`가 exit 0으로 끝났다. 이 결과는 해당 공개 refs 전체이며 모든 branch의 모든 파일을 읽었다는 뜻은 아니다.

| repo | 이전 head 수 | 현재 head 수 |
|---|---:|---:|
| bass_cr | 172 | 173 |
| rei_bianchi | 258 | 261 |
| bass | 264 | 265 |
| BASS_HE | 89 | 90 |
| WU088_HH | 141 | 142 |
| rec_bianchi | 136 | 137 |
| vigilode | 186 | 187 |

관련 8개 PR metadata head와 실제 branch SHA는 모두 일치한다. C21O PR96의 현재 head는 `f7ca6905729f7d8d36ca0605f7b1dd7ad5595819`, 원 content는 `6b6db06e8148e6826a2d5bf7dbc53d362126ca62`다. PR은 draft/open이며 merge되지 않았다. 다른 대화 조회는 실제 Personal Context 오류를 받아 **UNAVAILABLE**로 기록했다. 접근하지 못한 대화·미게시 실행의 부재를 선언하지 않는다.

41개 선택 source/manifest/report/receipt의 반환 내용을 그대로 저장하여 Git blob SHA와 대조했고 모두 일치했다. 아래 판정은 원전 읽기, Git byte identity, 이번에 실제 비교한 raw의 범위를 구분한다.

## 2. 새 결과와 C21O에 대한 의미

| 외부 작업 | 실제 확인한 게시·실행 | 이번 수용 범위 |
|---|---|---|
| REI PR220 / BASS PR180 | 공통 compact33 연구. REI head `8be7533cc97b3302bf42608699d6e8313ed6af8a`, BASS head `574c3af93810122af0a7977e00e34195e5251a09`. 125 격자 + 2 상쇄 + 2 full62 oracle, 각 193 epochs | 계약·source·입력·영수증을 읽고 **2쌍 4개 raw를 실제 회수·비교**했다. 두 repo는 같은 연구의 mirror이므로 두 배로 세지 않는다. |
| REI PR218 | head `4c8794e6e7c4ac553cc85fee728ef9ab6fe81fa8`, source/results `2fd46785ef2e7af8c25c01387c89e00b3edf9e9b`. 79 nominal + 3 controls, 각 257 epochs | 82-case manifest, controller, 보고서, 독립 최종 검토를 읽었다. 전체 raw 재검토는 이번에 하지 않았다. UV 5–60 eV, T 100–10000 K, photo+RR test fluid다. |
| REC PR119 | head `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`, science `8509ef6ba713279134c98f9f47464aa879069755`. 125 main + 1 opacity-off | 보고서·DAG·metadata의 scoped 결과로 수용한다. 첫 case의 serialization recovery duplicate는 별도 IVP가 아니다. 원래 Physical HOLD와 다음 thermal/ionic-yield 의무를 유지한다. |
| HH PR133 / PHYS78 | head `91d0846a940abf7817c900102dab488ff87e6a82`, science `b001e69668b2d2c2557b51830f5f732164b56ce0`. 31 pilot + 1 refinement + 2 failed debug = 34 attempts | 실제 ledger·contract·report를 읽었다. 기체·gray photons·finite source energy reservoir 결합을 갖지만 **Thomson/Compton이 없다**. C21O의 electron–Thomson 모형과 동일하지 않다. |
| REI PR219 | head `442b5fc38c895632e397d8a039ccabf605ac67ba` | isotope quotient의 Stage B precontrols만 수용한다. 최종 79+3 campaign·그림·과학 admission은 관측한 ledger에서 pending이다. |
| HE PR85 | head `0c016a11966547d81dbc61117ab45e8f0ab81790` | PR 본문은 preflight 5개와 392 nominal 진행을 말하지만 읽은 Git DAG는 F.C7–F.C10 pending이다. 구현·preflight metadata로 남기며 완료 campaign으로 승격하지 않는다. |
| VigilODE 새 branch | head `c4d9eb9f76ac1fbcbb4a12fb920d05e4c2317fa9`; P02 결과 `ae9bb6f5eaf1c2f21789eef2ea44082a57dadca6` | P02는 C6 reference-uncertainty criterion **FAIL**. P02b는 21:08 UTC에 harness와 사전등록만 추가됐다. 원 FAIL과 P03–P06/NCP_C1 BLOCKED를 유지한다. C21O solver 교체 근거로 쓰지 않는다. |

이들은 초기조건, UV, 온도, 원자율, 기하·반응 결합이 다르다. C21O의 51개와 합쳐 하나의 통계 ensemble로 만들거나, 유사한 축 정규화만으로 원 source identity를 바꾸지 않는다.

## 3. compact33의 실제 source·입력·구현·raw 검사

고정 donor REC source는 `a949529872eb5ba0e20c7e206fe893e5d544e48c`다. 현재 execution source base는
`ee7e9ae76c852079ce86cdd5165624ab2b7fc7a9c672016501ed5da5fb4341d3`,
CAMPAIGN.json SHA256은
`644000bf402a13afdd8ffa2862f8bc3ba0bc147ff1f3082e318440852b008ed3`다.

반사 짝수 부분공간의 23개 기하/복사 좌표와 같은 원소 isotope의 9개 공통 charge fraction, optical depth 하나로 62→33 좌표를 구성한다. 읽은 코드는 `f33(v)=R f62(Pv)`, `J33(v)=R J62(Pv)P`를 구현한다. 이는 그 불변부분공간의 대수적 차원 감소이며 속도 배수의 측정이 아니다. C21O에도 재사용 가능한 설계 근거지만, C21O의 source 위에서 별도 검증 없이 kernel을 교체하지 않았다.

실제 모형은 T=100+11900Q(z) K, Q=(1+tanh((7−z)/0.8))/2, 외부 UV 5–200 eV, photo+RR+DR, electron–Thomson test fluid다. C21O의 prescribed T/UV와 RR-only 원자망과 다르다. n/T inventory는 0이고 isotope의 전자율 동일성을 가정한다. 비영 n/T, isotope별 초기 fraction 차이, 홀수 multipole은 이 축약의 적용 조건을 벗어난다.

Solver는 SciPy BDF, rtol=2e−8, geometry atol=2e−11, scaled atomic atol=2e−10, tau atol=2e−11, max_step=0.025다. Python 3.12.14 / NumPy 2.3.5 / SciPy 1.17.0, 8-CPU quota/8-GiB sandbox의 4 workers였고 launcher wall 31.705687540001236 s가 기록되어 있다. 이 값은 실행 영수증이며 benchmark가 아니다.

대표 high corner `s04_m04_r04`와 `cancel_positive_matter`의 compact/full62 원 NPZ 네 개 **865,296 bytes**를 실제 GET 한 번씩 회수했다. 각 byte size/SHA256, RESULT↔COMPLETE↔trajectory identity가 일치했다. producer solver/analysis를 import하지 않고 NumPy와 표준 라이브러리만 쓰는 `verify_representative_raw.py`를 실제 실행해 exit 0을 얻었다.

| pair | max signed observable 차이 | max isotope charge fraction 차이 | max tau 차이 |
|---|---:|---:|---:|
| high corner | 1.2075369731912033e−9 | 2.0900165313747206e−8 | 4.3042097663814616e−11 |
| positive matter cancellation | 1.0450911755076152e−10 | 2.9287067020413277e−8 | 1.3193418579859895e−11 |
| 원래 고정 수용 한계 | 3e−7 | 3e−5 | 3e−7 |

동일한 193개의 x/z, species order, 초기 inventory를 확인했다. Full norm=abs(signed), half-contraction=full/√2가 정확히 맞았고 n/T는 두 구현 모두 정확히 0이다. signed radiation/total 합 잔차는 최대 2.1684e−19였다. 이는 두 saved pair의 **PASS_SCOPED**이며 127개 전체 원시 자료 재감사나 연속계 수렴 증명은 아니다. `global_error_bound=null`을 유지한다.

외부 report는 최초 127개 numerical raw가 생성된 뒤 마지막 JSON serialization이 실패했고, 수정 후 pilot_v2의 127개를 다시 적분했다고 명시한다. 따라서 **129는 authoritative 완료 집합의 수이며 전체 시도 수가 아니다.** 그 실패·재실행 역사를 숨기지 않는다. 이번 intake의 새 적분 수는 0이다.

## 4. DAG와 인계

`EXECUTION`: C21O 51 완료 이력 유지; 이번 saved-data 검사만 수행, ODE 0.

`PUBLICATION`: PR96 기존 D 재확인; 새 receipt의 게시 결정·실행은 root가 담당한다. 이 child의 remote mutation은 0이다.

`BACKUP`: 기존 provider 상태를 변경하지 않았다. 이 intake 파일들의 최종 bundle/ACK는 root의 보존 단계에 속한다.

`DAG`: 새 외부 결과 intake와 대표 pair 수용은 COMPLETE_SCOPED. 완전 thermal/UV-transfer/nuclear closure, 비-LRS, 전역 수렴과 NCP 신규 과학 실행의 상태는 변경하지 않는다. 다음은 root가 복원한 C21O 산출물과 이 receipt를 C10 문서·배송본에 반영하는 것이다.

핵심 파일은 `EXTERNAL_RESULTS_INTAKE.json`, `LIVE_REF_DELTA.json`, `ALL_TEXT_FETCH_BINDINGS.json`, `compact/REPRESENTATIVE_RAW_DOWNLOAD.json`, `compact/REPRESENTATIVE_RAW_COMPARISON.json`이다. 원 source와 외부 실행을 혼합하지 말고 이 파일들에 결속된 정확한 SHA와 scope를 이어받는다.
