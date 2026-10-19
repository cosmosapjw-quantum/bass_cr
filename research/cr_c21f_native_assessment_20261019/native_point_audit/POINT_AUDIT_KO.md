# C21F 저장 native point 독립 감사

판정: **PASS_SCOPED_SAVED_NATIVE_POINT_AUDIT**. 저장된 26개 JSONL, 27,140개 요청·응답을 원시 텍스트에서 다시 읽었다. Rust/Python solver 실행이나 원래 과학 suite 재실행은 수행하지 않았다.

## 근거와 identity

- Evidence commit: `c4a502e0c931a201edfa3c7046f7a91230c2278f`.
- Native owner 기록: `6ea2b1b4b3875c9163cafc45efe720afded43fc4`.
- 각 point 파일의 바이트 SHA-256을 원 manifest와 비교하고, Git blob SHA-1을 길이 포함 원래 Git object 표현에서 계산하여 실제 intake 영수증과 대조했다.
- 모든 판정 tolerance는 `src/native_micro.py`와 `src/event_coupler.py`의 기존 수치를 유지했다. `math.fsum`을 사용한 독립 합산의 실제 잔차와 허용 budget 비율을 JSON에 함께 남겼다.
- Native binary SHA는 process metadata와 manifest 사이의 일치만 확인했다. 실행 파일 바이트를 받지 않았으므로 binary byte identity는 검증하지 않았다.

## 확인 항목

| 항목 | 통과 record / 전체 |
|---|---:|
| `valid_request` | 27,140 / 27,140 |
| `OK_23_finite_response` | 27,140 / 27,140 |
| `exact_zero_photo_and_expansion` | 27,140 / 27,140 |
| `nonnegative_ci_rr_dr_and_escape` | 27,140 / 27,140 |
| `no_error_response` | 27,140 / 27,140 |
| `fixture_density_exact` | 27,140 / 27,140 |
| `elapsed_metadata_valid` | 27,140 / 27,140 |

각 record에서 원래 strict state domain, request/fixture 밀도, 세 density echo, EOS, 23개 유한 출력, CI/RR/DR·escape의 비음성, 5개 photo/expansion 출력의 정확한 0을 확인했다. CI−RR−DR로 재구성한 종별 변화율과 결합에너지 변화율, `thermal + binding + escape − CMB = 0`을 독립 계산했다.

| Lane | 파일 | point records | result/reference count 일치 |
|---|---:|---:|---:|
| `common_ic` | 13 | 9,656 | 13 / 13 |
| `native_source` | 13 | 17,484 | 13 / 13 |

## 실제 잔차

| 항등식 | 최대 절대 잔차 | 원래 허용 budget 대비 최대 비율 |
|---|---:|---:|
| `density_0` | 0.000000e+00 | 0.000000e+00 |
| `density_1` | 5.421011e-20 | 5.206382e-03 |
| `density_2` | 3.388132e-21 | 4.002380e-03 |
| `temperature_K` | 7.275958e-12 | 1.942002e-03 |
| `fractions_per_s_0` | 7.703720e-34 | 3.771377e-06 |
| `fractions_per_s_1` | 3.081488e-33 | 1.808291e-05 |
| `fractions_per_s_2` | 1.155558e-33 | 7.564690e-06 |
| `binding_eV_H_s` | 4.930381e-32 | 2.888931e-05 |
| `energy_eV_H_s` | 1.602374e-31 | 1.001532e-05 |

## 적용 범위

이 결과는 저장된 C21F 두 fixture의 native 비광이온화 bridge 응답에 대한 사후 일관성 검사다. 원자 rate 함수의 외부 자료 정확성, native build의 현재 재현, 보존량 적분·시간 수렴, source-age/spectral/angular 수렴, Case B, Bianchi 또는 full EoR의 검증을 대신하지 않는다. 입력 Hubble 항과 photo 입력을 0으로 주는 것은 읽은 wrapper source에서 확인했고, 로그에서는 대응하는 다섯 출력이 정확히 0임을 검사했다.

Native handshake 문자열은 별도 원시 handshake 기록으로 저장돼 있지 않다. owner 문자열은 `native_process.json`의 기록이며, 해당 파일은 wrapper가 handshake를 성공 확인한 다음 기록하도록 구현돼 있다.

발견된 위반 수: **0**. 세부 위치·입력 hash·파일별 통계는 `POINT_AUDIT.json`에 있다.
