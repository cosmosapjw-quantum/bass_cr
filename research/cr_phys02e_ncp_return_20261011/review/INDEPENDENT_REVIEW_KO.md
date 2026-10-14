# CR-PHYS02E 실제 반환 독립 심사

판정은 **PASS_SCOPED**다. 실제 fullBED와 legacy의 저장 9600점 격자 pulse 및 고정 연산자 모멘트를 계약 범위에서 수락한다. 후보 설계·구현·acceptance 구성에 참여하지 않은 별도 reviewer가 종료 후 원 산출물을 검토했다. 새로운 G, pulse, solver, preflight, 시험 또는 과거 suite를 실행하지 않았다. NPZ 읽기와 저장 배열의 사후 대조만 수행했다.

요청된 모델은 gpt-6-astra이며 이 reviewer에게 보이는 호스트 개발자 라벨은 GPT-6다. 실제 Astra backend 신원을 독립 인증했다는 주장은 하지 않는다. 역할 독립성과 backend 신원 인증은 별개다.

## 반환 identity

고정 family manifest SHA256은 `56273489b960aaa28f92f6571ea700d205141252687d5482647d4ec6c8fcde6d`다. numerical ZIP은 8,993,823 bytes, SHA256 `5048c325175a1c472a252ff1eddcea3c4d622c7611f5bd261c4a9b3258c24b4a`이며 520개 payload와 self manifest를 포함한 정확한 521개 entry를 대조했다. Family의17개 payload와 envelope18개 entry를 직접 읽어 전부 일치함을 확인했다. Envelope SHA256은 `ba2241b95c591acaafe09bc181395bb65840d12f366e41f2e3df97d2cb333fc1`다. 실제 run과 ZIP 내 대응 파일, 고정 source manifest67개 파일도 일치한다. Postcollection wrapper 영수증은 ZIP 외부 family에 보존돼 있다. 구체적인 원 파일 해시는 동반 JSON에 결속했다.

## 실제 실행과 검증

launcher/worker/wrapper/collector exit는 모두0이다. Launcher wall2720.582633553초는3600초 이내다. Wrapper 전체 wall2721.685590796초는 외부 process 영수증에 기록돼 있다. G 예약2와 완료2, pulse 예약2와 RESULT/NPZ 및 child 성공으로 확인한 완료2를 구별했다. 첫 실패나 timeout은 없으며 자동 재시도는 없다. 이전 PHYS02D의 실패·소비 예산은 변경하지 않는다.

Runtime은 Python3.12.3, NumPy2.4.2, SciPy1.17.0, 기록된 OpenBLAS pool1 thread다. 양쪽 BUILD 전 resource admission이 true이고 reserve 후 working memory는 각각115,692,015,104 및115,610,652,160 bytes다. 이 기록은 admission 증거이며 전체 실행 peak RSS나64-core 성능 측정은 아니다.

| 검증 | fullBED | legacy | 계약 한도 |
|---|---:|---:|---:|
| saved ramp 최대 상대잔차 | 7.6240e-15 | 4.1035e-14 | 1e-9 |
| terminal 상대잔차 | 1.1719e-15 | 2.2166e-15 | 1e-9 |
| active solve 최대 scaled 잔차 | 2.6216e-16 | 2.6807e-16 | 5e-11 |
| pulse energy 최대 절대잔차 | 2.5646e-14 | 5.2180e-15 | 5e-10 |
| 최소 state | 0 | 0 | scaled -2e-12 |

CDF의 monotonic/range와 저장 ramp endpoint 경계, finite/positive moments 및 variance 조건을 만족한다. 두 NPZ의 모든 배열이 finite이며 pulse shape은(17,9611,2), integrator shape은(17,2,2)다. source/E는 저장 입력과 정확히 같고 초기 pulse는 완전한 source와 같으며 적분 초기값은0이다. NPZ heat/H0 CDF 및 마지막 J1/J2는 JSON과 정확히 일치한다. 직접 합산한 에너지 잔차와 producer einsum 잔차 차이는 최대2.776e-15이며 합산 순서 차이 범위로 양쪽 모두 원 tolerance보다 충분히 작다.

## 수치 결과와 해석 한계

| selected 결과 | fullBED | legacy |
|---|---:|---:|
| F(1e10 s) | 0.06390638043 | 0.06376934057 |
| 고정 연산자 무한시간 평균 lag(s) | 4.6452767914e11 | 4.7567466188e11 |
| 2차 모멘트(s²) | 6.7992077674e23 | 7.1820091216e23 |
| variance(s²) | 4.6413481205e23 | 4.9193452820e23 |

이는 frozen operator에 조건부인 numerically checked 결과다. 유한 구간 CDF와 uncapped mean은 서로 다른 양이다. 출력 kernel_per_s는 정규화하지 않은 heat response이며 조건부 CDF의 시간미분은 H0로 나눠야 한다. Saved ramp 비교는 같은 연산자의 대수적 일관성 검사다. 독립적인 물리 oracle, pulse 격자수렴, old/new G 모든 원소 동일성 또는 우주 생산 이력 검증을 뜻하지 않는다. G 원 배열을 별도 보존하지 않은 것은 계약상 허용되며 실제 G hash receipt를 과거 G parity로 해석하지 않는다.

PHYS02_DELAY **OPEN**, production_history **HOLD**, atomic_G02 **UNRESOLVED**, b_grid **NO_GO**, all_bound **OPEN**, R17B2B **NO_CERTIFIED_SOURCE_SHARPENING**, CCC exporter **SOURCE_IDENTITY_UNRESOLVED**를 유지한다. 이번 named numerical node만 수락하며 상위 물리 gate와 그에 의존하는 승격을 열지 않는다. 수치 수락을 막는 material blocker는 발견하지 않았다.
