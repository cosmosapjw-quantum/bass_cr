# HeIII pulse/bin correlated exporter candidate

## 범위와 상태

이 후보는 C5의 scalar event adapter만 구현한다. 저장된 HeIII pulse의 RR count 구간 N과 kinetic-energy 구간 E를 받아 동일한 기저에 결속된 부호·단위·native25 투영을 반환한다. source 생성, RR/provider 재평가, solver/ODE 실행, native 상태 변경, source history 재구성은 수행하지 않는다.

현재 산출은 export_adapter.py와 이 README뿐이며 새 연구 unit에는 복사하지 않았다. 구문 AST 검사는 통과했다. 모듈을 import하거나 이벤트를 계산하지 않았고, 수치 확인·독립 검토는 부모의 C6/C9 단계에 남아 있다.

실제 읽은 계약과 근거:

- bass_cr/research/cr_rr_causal_clock_20261027/RESEARCH_CONTRACT.md
- theory_candidate/THEORY_KO.md 전체, 특히 §7–8 및 FORMULA_CONTRACT.json
- 기존 cr_heiii_ground_rr_20261027/implementation/export_adapter.py
- 최신 로컬 AGENTS.md와 R02 preflight의 provider/parallel 변경
- PR108 실제 조회: head 08186920c58cea4cc01969710152bdf608a3ed77, open draft, unmerged

로컬 Git HEAD는 API로 게시된 최신 own ref와 별개인 ec463db0c7e5c7fb5070796071c926caa4db6445였다. 새 unit index와 부모의 미완료 R02 receipt를 관찰했으며 수정하지 않았다.

## API

    export_event(
        *,
        case_id,
        source_id,
        source_identity,
        time_start_s,
        time_end_s,
        count_cm3,
        kinetic_eV_cm3,
        frame,
        clock_metadata,
        observation_kind="finite_bin",
        nb_m3=None,
        frame_gamma=1.0,
    ) -> dict

- count_cm3=[NL, NU], kinetic_eV_cm3=[EL, EU].
- finite_age는 start=0, end>=0이다. end=0이면 두 구간 모두 정확한 [0,0]이어야 한다.
- finite_bin은 0<=start<end<infinity이다. 시간은 선언된 pulse 이후 proper seconds이다.
- frame은 기존 bath_frame_rest_target만 받는다. comoving/rest frame의 Lorentz gamma=1만 허용하며, 이는 Erlang auxiliary clock의 gamma와 다른 필드다.
- nb_m3=None이 실제 연구 export다. 명시적으로 양수인 nb를 준 control/소비자만 native25 interval 투영을 받는다.
- nominal basis 값, interval midpoint, 조건부 평균 kinetic energy 또는 단색 스펙트럼을 만들지 않는다.

수치 입력은 finite Python float 또는 binary64로 정확히 표현되는 int다. bool, NaN, infinity, 음수, 역전 구간을 거부한다. 큰 정수를 binary64로 반올림해 interval 경계를 조용히 바꾸지 않고 거부한다. 출력이 유한 binary64 구간으로 표현될 수 없으면 overflow를 실패로 반환한다. 영벡터와 정확한 zero-age는 허용한다.

## source_identity

필수 구조는 다음과 같다. 해시는 실제 input/manifest에서 가져온 lowercase SHA256이어야 한다.

    {
      "distribution_id": "<실제 저장 distribution 식별자>",
      "count_projection_sha256": "<64 hex>",
      "operator_sha256": "<64 hex>",
      "bath_sha256": "<64 hex>",
      "raw_atom_sha256": "<64 hex>"
    }

추가 provenance 필드는 JSON으로 보존한다. NaN/Infinity 및 JSON으로 표현되지 않는 값은 거부한다. frozen scope와 같은 이름의 필드를 추가하면 정확히 같은 타입·값이어야 한다.

고정 scope는 기존 source-qualified ground spontaneous HeIII→HeII, 조건부 elemental-He→He4 mapping, 54.42 eV threshold, native photon support 최대 50000 eV, stationary heavy target/zero recoil, scalar isotropic ensemble이다. exporter는 공급자 파일을 읽거나 validity를 새로 인증하지 않는다. 실제 원본 바이트·배스·표·operator의 admission은 upstream input binding의 책임이며 output에서도 이를 명시한다.

## clock_metadata

여러 m/level 및 monotonic tightening에 사용된 여러 horizon record를 함께 보존할 수 있다. source_time_frontier 엔진의 metadata에서 다음 subset을 전달한다.

    {
      "time_units": "proper_s",
      "gamma_units": "s^-1",
      "records": [
        {
          "horizon_s": "<finite positive float>",
          "m": "<positive int>",
          "delta_requested": "<optional float, 0<delta<1>",
          "clocks": {
            "minus": {
              "gamma_s_inverse": "<positive float>",
              "gamma_hex": "<gamma.hex()>",
              "a_numerator": "<positive int>",
              "a_denominator": "<positive int>",
              "tail_upper": "<0<q<1>"
            },
            "plus": {
              "gamma_s_inverse": "<positive float>",
              "gamma_hex": "<gamma.hex()>",
              "a_numerator": "<positive int>",
              "a_denominator": "<positive int>",
              "tail_upper": "<0<q<1>"
            }
          },
          "arithmetic_certificate": "<optional original JSON metadata>"
        }
      ]
    }

여기서 위 괄호 안 문자열은 형식 설명이며 실제 입력은 기재된 숫자 타입이다. 양의 관측 endpoint마다 최소 하나의 horizon record가 있어야 한다. zero horizon은 clocks=null인 별도 record 또는 records에서 생략할 수 있다.

adapter는 gamma의 정확한 binary64 hex와 exact rational a=gamma*T/m의 결속, minus a>1 및 plus 0<a<1, 명시된 단위를 검사한다. tail/log/exp/shifted solve를 다시 계산하지 않으며, 전달된 N/E 구간의 과학적 certificate가 유효하다고 자동 선언하지 않는다. zero horizon을 위해 무한 gamma를 만들지 않는다.

## 공통 N/E와 directed rounding

원래 입력 N[cm^-3], E[eV cm^-3]를 정확한 binary64 값으로 해석한다. scalar 계산은 Fraction.from_float와 exact rational coefficient를 사용한다.

    internal = -(2721/50) * N
    fast_kinetic = -E
    retained_photon = E + (2721/50) * N

thermal_kinetic, recoil, escaped, external은 이 선택 모델에서 정확한 0이다.

각 선형 row의 정확한 구간을 먼저 계산한 뒤, Fraction→float 변환 결과를 정확한 rational과 대조하여 필요한 방향으로 math.nextafter를 한 번 적용한다. 따라서 정상값·subnormal·underflow 근방에서도 최종 endpoint가 안쪽으로 반올림되지 않는다. 유한 outward endpoint가 없으면 오류다.

SI 변환 역시 원래 N/E 기저에서 직접 한 번 수행한다.

    count_m3 = 10^6 * N
    energy_J_m3 = (10^6 * 1.602176634e-19) * energy_eV_cm3

eV_J는 부동소수점 상수가 아닌 정확한 SI 유리수로 보관한다. 출력에는 original common_basis, 모든 exact rational linear_map, 각 outward interval 및 exact conversion coefficients가 들어간다.

보존식은 동일한 N/E에 대해 다음과 같다.

    -E - 54.42*N + (E + 54.42*N) = 0

각 reservoir 구간의 끝점을 독립적으로 택한 모든 조합이 보존한다는 뜻은 아니다. output은 independent_interval_corners_conserve=false와 floating_endpoint_sum_asserted_zero=false를 명시한다. interval corner 합을 scalar closure test로 바꾸지 않는다. 각 구간의 물리적 joint feasibility를 새로 판정하는 기능도 없다.

## Native 21+4 및 retained-photon port

동일한 N으로 He4III(index12)→He4II(index11), fast electron 감소, photon 증가를 기록한다.

nb가 명시될 때만 다음 native25 interval과 정확한 sparse linear map을 생성한다.

    a = 10^6*N/nb
    DeltaY[11] = +a
    DeltaY[12] = -a
    Delta_zeta = -a
    Delta_w_nt = -(10^6*eV_J)*E/nb
    Delta_w_ext = 0
    Delta_logT = 0

native binding energy는 ionization-energy vector와 DeltaY가 소유한다. retained photon은 별도 port이며 native w_ext에 중복 넣지 않는다. SI photon count/energy port는 nb 없이도 존재하지만, per_baryon port와 native25 projection은 명시적 nb가 있을 때만 생성한다.

실제 nb=null에서는 native25=null, photon per_baryon=null이다. 어떤 경우에도 state_update_applied=false, native25_rhs=null이다. thermal particle/electron count의 선택 모델 변화는 0이며 이것을 heating 완료로 해석하지 않는다.

## 시간 bin 평균

finite_bin에 한해서 조건부 평균을 반환한다.

    conditional bin average = interval / (time_end_s - time_start_s)

두 binary64 endpoint의 차를 먼저 exact rational로 계산하고, 원래 N/E 선형계수를 그 정확한 폭으로 나눈 뒤 outward rounding한다. 이미 반올림된 SI interval을 다시 나누어 correlation을 버리지 않는다.

출력 이름은 CONDITIONAL_DECLARED_PULSE_BIN_AVERAGE_RETURN이다. 실제 continuous injection rate 또는 pointwise rate를 뜻하지 않는다. finite_age에는 이 평균 필드가 null이다.

모든 출력에서 다음은 null로 남는다.

- 실제 연속 injection history와 source time history
- exposure
- instantaneous physical rate, event_rate_m3_s
- instantaneous_rhs 및 native25_rhs
- emission time history와 spectrum
- physical heating 및 physical stopping rate

N4/N5 partial, N6/N7 gated, L4=false를 유지한다.

## 식별자와 중복 방지

canonical_event_id는 unit, case/source ID, distribution 및 네 source SHA, frame, exact proper-time window에 결속한다.

구간 bounds, m/gamma, nb, finite-age/bin 라벨은 ID에서 제외한다. 같은 pulse와 [0,T]에 대한 더 좋은 certificate, 다른 m 계산, 다른 명시적 nb control 또는 finite-age/bin 이름 변경을 새 물리 이벤트로 중복 누적하지 못하게 하기 위해서다.

validate_event는 원래 common basis에서 전체 scalar map을 재구성하여 부호·단위·native index·photon owner·금지된 scope 변경을 검사한다. strict JSON comparison으로 numerical zero와 Boolean false를 구분한다.

PulseReturnBook(frame, case_id=..., source_id=...)는 같은 source/operator/bath만 허용하고 이미 수용한 canonical ID를 거부한다. 저장된 목록의 deepcopy를 반환한다. 합산 기능은 없으며 서로 겹치는 finite-age 누적값을 합산해도 된다고 주장하지 않는다.

## 부모에게 남기는 실행·검토

이 후보의 실제 수치 실행 수는 0이다. 다음은 부모의 동결된 C6 control 예산 안에서 확인할 항목이다.

1. 정확한 zero 및 zero-age, 유한 positive interval, 부호와 SI 변환의 outward 포함
2. directed conversion의 subnormal·overflow 동작
3. 같은 N/E를 사용한 symbolic ledger 및 independent corners를 보존으로 오인하지 않는지
4. nb=null과 explicit positive nb, native11/12/21/22, w_ext/logT zero, 별도 photon owner
5. invalid numeric/provenance/frame/gamma/clock 입력의 거부
6. 같은 source/window의 중복 및 대안 case/source의 혼합 거부

과거 과학 suite, source projection, H1/HeI/HeIII provider 또는 old generator를 재실행할 필요가 없다.

