# CR-PHYS02B: CCC excitation 원천 확보

## 인계 결론

HI와 HeI의 ground-state → n=2,3,4 모든 l 채널을 확보했다. HI는 9개, HeI는 singlet/triplet을 구분한 18개 채널이다. HeII 9개는 optional 원자료로 별도 보존했다. 총 36개 채널, 12,142행이다. 원 ZIP, 선택한 원문, SI 단위 열을 덧붙인 CSV, 채널별 해시와 출처를 모두 보관했다.

**필수 두 species의 공통 표본 상한은 968.6058 eV다.** 요청한 1000 eV까지 남는 31.3942 eV를 외삽하지 않았다. 원천의 공통 상한이 실제 cascade의 채택 구간이나 전역 유효성 인증을 뜻하지 않는다. 모형 구간, 보간, 전이 에너지, 손실 장부는 연구 owner가 결정한다.

이 작업은 source acquisition 역할이다. 기존 과학 suite 재실행 0, 새로운 cascade/열화 계산 0, 외부 write API 0이다. 원자료 추출·단위 변환·해시 재현만 확인했다.

## 현재 입력 identity

읽기 전용 Git ref metadata에서 `refs/heads/research/cr-phys02a-causal-subthreshold-20261010`의 HEAD는 요청된 `58c8e1cda5c8f8ca8b83269cb89899ea40ab91fe`와 정확히 일치했다. PR26 상태와 최근 PR/branch metadata를 확인했고, 원 응답은 `git_metadata/`에 보관했다. 기존 연구 lane 원문 재다운로드·재감사는 수행하지 않았다.

후속 입력 PR25/`research/cr-phys03-fs10-xi01-20261010`는 존재하며 HEAD는 `c55cd78bade16d95bf140456c6036b406c9356ea`다. 이는 FS10의 xi=0.1 단일 knot다. 이번 owner 지정 xi=0.01과 다르므로 자동 채택하지 않는다. 유지 예정인 nH=140 m⁻³, YHe=0.248, xi=0.01, T=100 K는 parent의 연구 조건이며, 여기서는 이 조건으로 어떠한 rate나 evolution도 계산하지 않았다.

## 공식 데이터와 문헌

원 ZIP 링크는 [Curtin CCC 공식 index](https://atom.curtin.edu.au/CCC-WWW/)의 실제 HTML에서 읽었다. 보관한 index는 HI August/2026, HeI April/2026, HeII May/2026 edition으로 표시한다. 이 표시는 각 HTTP Last-Modified와 구분한다. 정확한 분석 입력 identity는 아래 다운로드 바이트의 SHA-256이다.

| Species | 원 ZIP | 원본 bytes | SHA-256 | 채널 | 단위 | 선택 채널 상한 |
|---|---|---:|---|---:|---|---:|
| HI | e-H_XSEC_LS.zip | 7,010,330 | 17f44cbbc0bb03a59f2366f50dd19a03e7f0296ccc5b8dbf869d9dbf3762a9a1 | 9 | a₀² | 968.6058 eV |
| HeI | e-He_sig.zip | 1,502,872 | d68ba39d81c8252043e12f92155c1a9ab73117b55abfd971b98d6a65c6993a85 | 18 | cm² | 2000 eV |
| HeII | e-HeII_XSEC_LS.zip | 9,596,492 | e32f7d22a3dc54e7981e93369bb98ddd38109a784cff608e59e9657b3a3558db | 9, optional | a₀² | 10290 eV |

각 `*_acquisition.json`에 관측 URL, HTTP status/headers, 취득 시각, ZIP member 목록을 기록했다. 선택 raw bytes는 HI 166,807, HeI 247,211, HeII 365,271이다. 원 ZIP과 raw member를 보존하므로 이후 사이트 업데이트와 분리해서 동일 입력을 재현할 수 있다.

공식 index의 방법론 문헌은 [Bray & Stelbovics, PRA 46, 6995 (1992)](https://doi.org/10.1103/PhysRevA.46.6995), [Fursa & Bray, PRA 52, 1279 (1995)](https://doi.org/10.1103/PhysRevA.52.1279), [HeII method DOI](https://doi.org/10.1088/0953-4075/26/23/006)다. 앞의 두 논문은 공식 초록을 읽었고, 유료 전문을 읽었다고 주장하지 않는다. HeII DOI의 전문 내용은 이번 작업에서 확보하지 않았다. 특히 HeI README는 2026-04-13 기준 미출판 수치 결과이며 1995년 이론을 기반으로 한다고 명시한다. 2026년 표 전체가 1995년 논문에 출판된 것이라는 의미가 아니다.

[Furlanetto & Stoever, arXiv:0910.4410v1 §3–4](https://arxiv.org/html/0910.4410v1)은 낮은 에너지의 CCC 표, n=2–4의 l 및 HeI singlet/triplet 분리, 높은 에너지의 Bethe 연장을 설명한다. 이 문헌은 확보 범위의 선행 근거다. 현재 공식 2026년 ZIP을 FS10가 실제 사용한 과거 바이트와 동일하다고 인증하지 않는다. 여기서는 Bethe fitting, n>4 enhancement, 방사 cascade, photon reabsorption을 구성하지 않았다.

## 열, 방향, 단위의 의미

원 filename은 **FINAL.INITIAL**이다. 예를 들어 `2P.1S`의 헤더는 ground 1S → 2P이고, `1S.2P`는 반대 과정이다. HeI는 `s2P.s1S`, `t2P.s1S`처럼 singlet/triplet 최종 상태가 분리된다. 36개 파일 모두 헤더에서 초기/최종 상태와 단위를 확인했다. n-summed 또는 initial-l-averaged 파일을 중복 합산하지 않았다.

`E(eV)`는 해당 초기 target에 입사하는 전자의 운동 에너지이고, 이번 선택은 모두 ground-state 초기 target이다. outgoing electron energy 열이 아니다. 이 해석은 표의 입사 에너지 표기, 각 전이 onset, ground-state 파일의 계산 에너지 식별자와 일치한다. README가 산란 좌표계/유한 핵 질량에 대한 완전한 정의를 제공하지 않으므로 이를 추가로 인증하지 않는다.

`sig`는 해당 전이의 절대 각적분 cross section이다. `asym`은 별도 비대칭 열이며 반응 cross section이나 추가 excitation 채널이 아니다. 원문 전체를 남겼고 CSV에는 E, sig, native unit, SI 변환값, 원문 line number만 썼다. 원 단면적에 임의의 통계중률, 밀도 또는 π를 곱하지 않았다.

수치 입력은 각 원문 행의 \(\sigma_c(E_k)\) 자체다. analytic fitted coefficients를 대체로 꾸며 넣지 않았다. 수행한 변환은 다음뿐이다.

\[
\sigma_{c,\mathrm{SI}}(E_k)=
\begin{cases}
\sigma_{c,\mathrm{native}}(E_k)\,a_0^2,&\mathrm{HI,HeII},\\
\sigma_{c,\mathrm{native}}(E_k)\,10^{-4}\ \mathrm{m^2/cm^2},&\mathrm{HeI}.
\end{cases}
\]

[NIST CODATA 2022](https://physics.nist.gov/cuu/pdf/wallet_2022.pdf)의 \(a_0=5.29177210544(82)\times10^{-11}\,\mathrm m\)를 사용했다. 표기된 중심값의 제곱은 \(2.80028520159128904775936\times10^{-21}\,\mathrm{m^2}\)다. a₀는 정확한 정의 상수가 아니며, 괄호의 1σ 불확도는 \(8.2\times10^{-21}\,\mathrm m\)다. CSV는 이 중심값을 Decimal precision 50으로 곱한 결과이며 물리적 유효숫자의 증가를 뜻하지 않는다. NIST 원 PDF와 취득 metadata도 보존했다.

## Threshold와 공통 유효 상한의 한계

HI/HeI 파일에는 별도의 전이 에너지 선언 없이 첫 σ=0 행이 있다. `CHANNELS.json`의 `threshold_eV_source_value`는 그 **원문 시작 zero marker**다. 이를 독립 검증된 분광학적 threshold 또는 모든 충돌에서 손실되는 정확한 광자 에너지라고 주장하지 않는다. HeI 일부 n=3,4 파일은 이 뒤에도 여러 0 행을 갖는다. 이 표의 onset과 별도 원자 에너지 자료를 연결하거나 문턱을 이동할지는 이번 확보 작업에서 결정하지 않았다.

README와 같은 ZIP의 member inventory에서 별도 target-state 에너지 표가 있는지 1회 확인했다. HI의 두 README와 `nf.1`(cross-section series), HeI README, HeII README와 plotting script에는 그런 표가 없다. 상태는 `NO_EXPLICIT_TARGET_ENERGY_METADATA`이며 근거는 `TARGET_ENERGY_METADATA_CHECK.json`에 보존했다. 이 확인은 외부 CCC 구현이나 비공개 upstream 파일 전체에 대한 부재 주장이 아니다.

HeII에는 threshold 주석이 있다. n=3은 주석 48.3761778 eV에서 첫 표본 48.3762000 eV까지, n=4는 51.0217500 eV에서 51.0262000 eV까지 짧은 공백을 남긴다. n=2의 첫 표본은 주석 threshold와 같고 σ가 0이 아니다. 획일적인 threshold-zero 규칙을 적용하지 않았다.

각 채널의 marker, 첫 양의 표본, 마지막 표본은 `THRESHOLDS.csv`와 `CHANNELS.json`에 있다. n=2,3,4의 l 채널은 모두 보존했으며 HeI의 s/t 상태를 합치지 않았다. 낮은 에너지의 closed-channel 처리, marker와 첫 양의 표본 사이의 보간, species 간 기준 에너지 차이, 마지막 표본 이후의 값은 owner가 명시할 사항이다. **공통 데이터 상한 968.6058 eV 아래라고 해서 이러한 문턱 해석과 보간 결정이 자동으로 해결되는 것은 아니다.**

## 재현, 검사, 라이선스 기록

`CHANNELS.json`에는 각 ZIP/member, 헤더, native unit, raw bytes/SHA-256, CSV SHA-256, 행 수, energy bounds와 marker provenance가 있다. `reproduce_tables.py`는 표준 라이브러리만 사용해서 원 ZIP에서 CSV 바이트를 다시 만들며 기본 실행에서는 파일을 바꾸지 않는다. 36개 CSV의 SHA-256이 모두 기존 manifest와 일치했다. 12,142행의 에너지는 채널별로 엄격히 증가하고 σ는 모두 유한·비음수였다. 이는 입력 형식과 바이트 재현 검사이며, 산란 계산의 정확도 검증이나 독립 과학 판정이 아니다. 결과는 `SOURCE_REPRODUCTION_RESULT.json`에 있다.

```sh
python /workspace/scratch/584ff08e1634/phys02b_sources/excitation/reproduce_tables.py
```

공식 index, 각 README, ZIP member 이름에서 별도 data license 또는 명시적 재배포 허가를 찾지 못했다. 따라서 데이터 라이선스 상태는 `NO_EXPLICIT_DATA_LICENSE_FOUND_IN_INDEX_OR_README`다. 공개 다운로드 가능 여부를 public-domain/CC-BY 허가로 바꾸지 않았다. FS10 arXiv 페이지는 arXiv perpetual non-exclusive license로 표시되며 이것은 CCC ZIP의 라이선스가 아니다. 원천 취득과 연구 이용을 위한 현황을 기록했으며 출판 처리의 최종 결정은 owner에게 남긴다.

실행 환경에서는 처음 시도한 `requests` import가 없어서 실패했다. 패키지 설치 없이 표준 라이브러리 `urllib.request`로 공식 관측 URL에서 HTTP 200 원 바이트를 취득했다. 웹 reader의 ZIP 미지원은 형식 제한으로 기록하며, 내려받은 데이터의 오류로 해석하지 않았다. 과학 코드 실패나 과학 결과 재현 실패는 발생하지 않았다.

## 남은 owner 결정

이번 인계는 절대 단면적 원천과 그 표기 범위까지다. 실제 에너지 구간, 보간 함수, 물리적 excitation 에너지와 표 onset의 연결, 제외한 source-energy ledger, photon bookkeeping, causal evolution, 모형 채택 또는 과학 claim 판정은 수행하지 않았다. HeII는 요청대로 optional 데이터만 보존했다.

### 후속 owner 지시 기록

Owner는 HI 9개와 HeI 18개 채널을 사용하고 첫 σ=0 marker를 truncated CCC 모형의 effective excitation cost Δ_j로 명시 채택할 예정이라고 전달했다. HeI n≥3의 여러 원문 0 행도 그대로 보간한다는 지시다. 이 결정은 source acquirer가 만든 물리적 인증이 아니며, 원천에 명시적인 target 에너지 표가 없다는 조사 결과와 함께 인계한다.
