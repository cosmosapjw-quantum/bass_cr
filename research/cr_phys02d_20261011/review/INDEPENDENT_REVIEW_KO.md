# CR-PHYS02D 독립 Astra 심사

**판정: PASS_SCOPED.** 저장된 ramp endpoint의 새로운 열 지연 해석과 수치 분석, 그리고 동일 9,600점 NCP pulse 작업의 준비 코드를 제한된 범위에서 채택한다. **실제 NCP pulse 물리 실행은 NOT_EXECUTED**다. 이 판정은 새 pulse의 실제 CDF·무한구간 모멘트·동일 연산자 잔차가 통과했다는 판정이 아니다. 해당 실제 반환에는 새로운 독립 심사가 필요하다.

정확한 검토 파일별 byte 수와 SHA256은 `INDEPENDENT_DECISION.json`의 `reviewed_files`에 있다. 이 문서와 판정 JSON 자체, 이후 조립되는 NEXT_DAG·FILE_MANIFEST 및 판정을 인용하는 closeout은 그 목록에서 제외하여 해시 순환을 피한다.

## 1. 심사자의 독립성과 실제 수행 범위

심사자는 이 후보의 유도, 후보 선택, acceptance 설계 및 구현을 작성하지 않았다. 같은 에이전트가 앞서 수행한 역할은 기존 PR30/31 및 백업의 **읽기 전용 source intake**였다. 후보 설계·구현에 관여하지 않은 상태에서 별도 독립 심사 역할을 부여받았다. 발견한 결함은 root에게 보고했으며 root가 기존 계약을 유지하는 수정 범위를 분류하고 구현자가 수정했다. 심사자가 후보 코드를 직접 수정한 적은 없다.

표시된 실제 host metadata는 GPT-6 Astra Pro이고 연구 하네스는 GPT-6 Astra v4.0.0이다. 구현 작업에는 낮은 모델 경로가 요청됐지만, 요청한 `gpt-6.1-sol`과 표시된 inherited Astra host metadata가 충돌한다. 실제 backend 전환 여부를 이 기록만으로 증명할 수 없다. 작업자의 “no actual lower-model switch” 표현도 backend의 독립 관측으로 채택하지 않는다. 모델 비용·성능 절감은 NOT_EVALUATED다.

심사자는 후보 소스, frozen 계약, 실제 입력 schema, 보존된 원시 결과·실패·수정 종료 기록, 최종 보고서와 NCP 시작 문서를 읽었다. 후보 구현을 import하지 않는 Decimal 90자리 계산으로 fullBED 9,600점 원본 한 행을 별도 검산했고, Fraction으로 CDF 다항식의 경계 및 대표점 15개를 확인했다. 마지막으로 기존 CDF 후처리 함수만 호출하는 작은 독립 측도 검사를 했다. 0–1 범위 및 단조성은 만족하지만 실제 quadratic 하계를 어기는 예가 명시적으로 실패하는 것을 확인했다. 이 검사에는 연산자 생성과 expm 호출이 없다.

심사 과정에서 실제 bass_cr G 생성, 실제 물리 수송, 과거 suite 재실행, 전체 endpoint 분석 재실행은 모두 0회다. 새 독립 CDF 후처리 검사의 실제 exit는 0, wall은 약 0.416초다. 근거는 `INITIAL_THEORY_ARITHMETIC.json`, `independent_cdf_probe.py`, `INDEPENDENT_CDF_PROBE_RECEIPT.json`에 보존했다.

## 2. 고정한 입력과 과학 경계

직접 base는 PR31 `f98ed974c3f3158dabd16cd854ecc5e04b9f5b31`, tree는 `ae9c5ea98edd724423bfa8cb79db976908d1c123`이다. 실제 paired 9,600점 원본 JSON의 SHA256은 `0b33ad9af1be50297e54fa8b38570471c35b5e342ce771d834bb576458a91500`이다. 이전 실제 실행은 새 PHYS02D 실행으로 재분류하지 않았다. PHYS02C 후기 receipt commit `eecb9bd…`는 직접 조상이 아닌 별도 계보로 남는다.

| 고정 대상 | SHA256 |
| --- | --- |
| Scientific contract | `bc05614e9812f616c4a4bb45805e4c0359a171813f7329794b0c10c3bf37dde2` |
| NCP execution contract | `9dd8b098d828fcad5ddd5138afd29e9dce4805e26fbac897bd4c9a07779e8ff9` |
| 직접 입력 manifest | `fdc6eaa7813ff22585668a5e0fe629ca7e7b3912cbcfb68050a30542f9a09978` |
| 259개 의존성 payload manifest | `dd64b4b187ea9b12c147e2d6d50d71b2f94c61e43a2ad1d77bc4b486b6ca68f3` |
| 저장 endpoint 분석 RESULT | `0fc14f741d1236eac28110ca1df1309747e8f25d5104adfac88ce067172fe3ed` |

수정 01–04는 출력 연결, 표시, 입력 schema, 테스트 fixture, coordinator 및 반환 manifest 문제를 다뤘다. 물리 입력, 방정식, 원자 단면적, source/bath, 허용값, 격자와 실제 물리 호출 예산은 바뀌지 않았다. 과거 연구의 모든 파일을 다시 검증했다는 뜻도 아니다. 의존성 manifest와 기존 독립 반환을 연결하여 이번에 필요한 고정 입력 범위를 확인했다.

## 3. 물리 유도와 단위 심사

활성 블록 L이 Metzler/Hurwitz이고 원천 b 및 열률 행 h가 비음이며 직접 heat feedthrough가 없으면 K(τ)=hᵀexp(Lτ)b는 비음이다. 선형 ramp와 영 초기조건에서 Duhamel 식 및 적분 순서 교환으로 P(T)=α∫(T−τ)K(τ)dτ, Q(T)=α∫(T−τ)²K(τ)dτ/2를 얻는다. H0=hᵀ(−L)⁻¹b로 정규화하면 R=E[X], S=E[X²], X=(1−τ/T)₊가 정확하다.

따라서 0≤R≤1, R²≤S≤R, E[min(τ,T)]=T(1−R), Var[min(τ,T)]=T²(S−R²)가 성립한다. 현재 열률에 기여하는 **원래 원천 주입의 나이**는 T(1−S/R)=T−2Q/P다. 이 값을 딸전자의 수명, 전체 최종 열의 평균 지연, cutoff 도달 시간과 동일시하지 않았다. 출생 성분을 합친 나이는 실제 현재 열률에 따른 가중이며 단순 평균이 아니다.

CDF의 T 시점 하계 R²/S는 Cauchy–Schwarz로, 더 짧은 시간의 두 경계는 x(x−c)/(1−c)≤1{x≥c}≤x(1+c−x)/c의 직접 다항식 부등식으로 증명된다. c=1−u이고 u=1/4,1/2,3/4다. 이 경계들의 전역 최적성이나 FP64 입력·이산화 오차를 감싼 인증구간을 주장하지 않았다. T 하계의 sharpness는 일반 비음 측도에 한정한다.

고정 R,S를 유지하면서 T 이후 원자 질량의 위치를 바꾸는 반례는 일반 비음 측도에서 정확하다. 두 지수 성분을 쓰는 매끄러운 반례는 Decimal 90자리의 수치 증거이며, 해석적 또는 interval-certified parameter-family 증명으로 승격하지 않는다. 전체 L,b,h를 알면 그 고정 모형의 응답은 정해지지만 endpoint 두 스칼라만으로는 uncapped 평균의 유한 상계가 정해지지 않는다는 구분이 유지됐다.

NCP 구현의 G는 무차원 시간 u=t/T0에 대한 T0L이다. J1′=y_heat, J2′=J1을 붙이면 J1(1)은 저장된 normalized ramp 열률, J2(1)은 normalized 누적 열이다. SI 변환은 각각 scale_eV_m3×EV_J/T0 및 scale_eV_m3×EV_J이므로 계수와 차원이 맞다. 무한 모멘트는 A=−G_active의 삼각 solve 세 번에서 T0와 2T0²를 곱한다. 0 고유값이 있는 전체 누적 장부 행렬을 역산하지 않는다.

## 4. 저장 endpoint의 수치 판정

실제 저장 RESULT의 여섯 selected 행 모두 compatibility slack이 양수다. 9,600점 fullBED에서는 R=0.034185860052192825, S=0.023676021232690664, S−R²=0.02250734820518255이다. 현재 열의 원천 나이는 3,074,323,361.605178 s, 즉 97.4194286513년이다. T에서 잘라낸 평균은 9,658,141,399.478071 s이고 분산은 2.250734820518255×10¹⁸ s²다. 이 평균을 uncapped 평균으로 읽을 수 없다.

동일 행의 F(T/2) 경계는 [0.013166182413188503, 0.055205537691197154], F(T) 하계는 0.049361039847965166이다. 이들은 R이나 실제 ramp의 누적 열/주입 에너지 비율과 다른 양이다. 독립 Decimal 원본 검산에서도 같은 해석과 수치를 얻었다.

저장된 여섯 행에서 보고된 FP64–Decimal 비교의 최대 상대 차이는 약 1.72×10⁻¹⁶이고 SI terminal 교차 확인의 최대 상대 차이는 약 1.11×10⁻¹⁵다. 이는 산술 및 필드 매핑 일관성의 증거다. 물리적 정확도 또는 이산화 오차의 크기를 뜻하지 않는다. Legacy 2,400점 terminal SI 값의 재구성도 원본 normalized 행에 연결되어 있다. 18개 출생 성분 나이의 의미와 보고서의 연 환산·반올림이 일치한다.

4,800→9,600점 비교는 격자와 Python/NumPy 환경이 함께 달라지는 경험적 차이다. 새 수렴 인증이나 원자모형 불확실도 분포로 채택하지 않는다. 수정한 그림을 직접 확인했으며 CDF 경계는 이산 시간의 별도 수직 구간으로 표시된다. T 시점의 [하계,100%]는 글로 명시되어 있고 중간 시간의 미증명 직선 경계가 없다.

## 5. 실제 종료 기록과 결함의 처리

| 근거 | 실제 종료와 판정 |
| --- | --- |
| Endpoint 작은 검사 | 세 검사 exit 0 |
| Endpoint 첫 계산 | 실제 process exit 1; RESULT가 저장된 뒤 CSV heterogeneous header에서 실패 |
| Endpoint export 복구 | 저장 RESULT만 사용, exit 0; 수치 재평가 0회 |
| CDF 그림 수정 | 저장 RESULT만 사용, exit 0; RESULT SHA 불변 |
| 첫 pulse toy batch | exit 1; sparse augmentation zero-block shape 결함 |
| 첫 구현 복구 후 pulse batch | 다섯 검사 통과, cutoff propagated 값의 bitwise 비교만 실패 |
| Amendment01 제한 검사 | 정확한 초기 cutoff 및 기존 FP64 허용값 적용, NPZ schema/의존성 포함 검사 exit 0 |
| Amendment02 제한 검사 | CDF 후처리·고립된 HOLD·startup 실패 보존 통과; collector의 과거 ancestor manifest 선택은 실패하여 보존 |
| Amendment03 collector 검사 | 현재 manifest 선택 및 명시적 synthetic fixture, exit 0 |
| Amendment04 collector 검사 | ZIP 전체 entry 집합과 모든 entry byte/SHA256 대조, exit 0, 약 1.080초 |

원래 exit 1들을 exit 0으로 덮어쓰지 않았다. 첫 pulse shape 결함은 구현 오류, cutoff의 약 1.11×10⁻¹⁶ 차이에 대한 실패는 과도한 테스트 oracle, CSV 및 반환 manifest 문제는 운영 오류다. 실제 물리 모형이 실패했다는 증거로 재분류하지 않는다. final 전체 suite를 새로 실행했다는 주장도 하지 않는다. 원래 통과한 검사와 바뀐 부분의 실제 제한 검사들을 합쳐 현 코드의 검증 범위를 판단했다.

WORKER_RESULT의 `total_targeted_wall_s=1.57322585105896`은 최초 batch만 가리킨다. 네 amendment의 별도 추가 wall을 합친 작업자 보고 합계는 약 5.767191286초다. 이 숫자는 전체 연구 세션 wall이 아니다. 실제 명령별 wall/exit는 개별 raw receipt를 우선한다.

## 6. 독립 심사에서 확인하고 해소한 항목

| ID | 분류 | 최종 처리 |
| --- | --- | --- |
| N1 | 수치 출력 계약 | 저장 paired9600의 R,S를 사용해 u=.25,.5,.75,1의 실제 CDF, 하·상계, raw slack, source identity/field, 기존 1e-9 허용값을 기록하고 실패 시 전체 수치 성공을 거부 |
| O1 | 테스트 oracle | 현재 tree가 영구 HOLD라고 가정하던 검사를 고립된 synthetic HOLD/identity mismatch로 변경 |
| O2 | 실행 및 증거 | coordinator 시작부터 3600초 deadline, 남은 child 시간, 소유한 새 run의 startup 예외/command/cwd/UTC/관측 child exit/예약 수를 실제 receipt에 보존; 기존 run에는 쓰지 않음 |
| R1 | 반환 재구성 | 새 unit의 theory·보고서·시작문서·endpoint·tests·review와 259개 전이 의존성을 포함; 원본과 별도 actual run을 보존 |
| R2 | 정확한 ZIP manifest | 생성되는 복원 안내 두 파일도 정확한 UTF-8 byte/SHA256으로 manifest에 포함; RETURN_MANIFEST 자체만 제외 |

과거 ancestor manifest를 모두 검증하던 경로는 admission과 같은 첫 현재 BUNDLE 또는 unit/repository FILE 선택으로 제한했다. 반환의 `frozen_payload/BUNDLE_MANIFEST.json`은 원본 provenance이며 원래 전체 archive root가 반환에 복제됐다는 주장이 아니다. 복원 시에는 RETURN manifest, 복원한 unit FILE manifest, repository-relative 의존성 manifest와 독립 심사 결속을 확인하도록 안내한다.

## 7. NCP 준비 코드의 채택 범위

입력의 energy grid와 시간 배열 [0,10¹⁰]은 정확 비교하며 전체 source_vectors를 초기조건으로 사용한다. 두 실제 NPZ의 heat 초기 행이 정확히 0이고 cutoff·내부 counter 행이 포함됨을 확인했다. 활성 블록의 정확한 위삼각성·음 대각·비음 rate, 삼각 solve의 scaled residual/양성, pulse 에너지 보존/비음성, CDF 단조성과 모멘트 compatibility가 frozen 허용값으로 검사된다. 선택 전체 응답은 두 birth 열의 합으로 얻으며 세 번째 수송을 만들지 않는다.

fullBED 다음 legacy, 동일 (3200,6400) 격자, G 생성 최대 2회와 pulse expm 최대 2회만 준비되어 있다. private inherited pipe 및 parent PID로 coordinator 예약을 결속한다. 실제 작업자는 계약·입력·의존성·payload·DAG·독립 심사 해시를 다시 확인하고 Python 3.12.3/NumPy 2.4.2/SciPy 1.17.0과 실제 한 thread 수치 pool을 요구한다. 매 build 전에 기존 그대로인 자원 adapter로 reserve 후 작업 메모리 12 GiB, disk 8 GiB 및 CPU 조건을 확인한다. 예약 수는 완료한 물리 호출 수와 구분한다.

현재 환경에서 보존된 plan의 자원 HOLD는 새 물리 성공의 근거가 아니다. 최종 frozen payload와 DAG를 조립한 후 root가 실제 plan/readback으로 admission을 확인해야 한다. 이 독립 판정 자체가 부족한 메모리나 불일치 runtime을 허용하지 않는다. 여기서 승인하는 것은 정확히 심사한 준비 코드와 과학적 작업 범위다.

## 8. 최종 미해결 범위

실제 NCP pulse CDF 및 uncapped mean/variance, 그 저장 ramp와의 잔차는 아직 측정되지 않았다. 같은 9,600점 pulse만으로 pulse mesh convergence를 주장할 수 없다. 장기간 고정 연산자 모멘트는 우주적 source/bath 변화 이후의 실제 이력을 보증하지 않는다. 실제 반환의 성공/실패 및 후속 예산은 그때의 독립 심사가 결정한다.

PHYS02_DELAY는 OPEN, production_history는 HOLD, atomic_G02는 UNRESOLVED, b_grid는 NO_GO, all_bound는 OPEN, R17B2B는 NO_CERTIFIED_SOURCE_SHARPENING, CCC exporter/source identity는 SOURCE_IDENTITY_UNRESOLVED로 유지한다. Native marker, incident energy axis, state-energy cost의 의미를 바꾸거나 NCP64 scaling 및 production 승인을 부여하지 않는다. 현 후보 범위에 남은 물리·수치·운영 차단 결함은 발견되지 않았다.
