# CR source binding — 최신 REI 소비자 국소 조사

조회: 2026-10-12 11:31–11:35 UTC. **기존 실제 consumer는 그대로 재사용할 수 있으며, 이번에 확인한 최신 자료에는 새 \(Q_e(W,t)=tA(W)\) 소비자 결속이나 CR 관측량의 절대 오차 예산이 추가되지 않았다.** 이 결론의 범위는 CR·RUX·source 관련 PR/branch 검색과 아래 고정 source이다. 저장소·클라우드 전체에 자료가 없다는 판정은 아니다.

## 1. 이전 조사 이후 실제 변경

| 대상 | 이번 조회의 정확한 head | 이전 소비자 조사와 비교 |
| --- | --- | --- |
| REI PR110 | 17f8d0daa72e0f76a49cde01b110f650a6688c42 | 동일. draft/open/unmerged, PR updated 2026-10-11 07:58:33 UTC |
| CR PHYS03 xi=.1 branch | 8d9526a75e85202764e845c7d5d79d7f903e7c55 | 동일 |
| 원 CR receiver branch | 69541be1a88f32468494e33158a96d5341e4572c | 동일 |
| PR97 integration | 1400093cdd121d8e6adb51ffeb360102a48653bf | warm conditional lane; PR 본문이 CR/RCT/HH OFF를 명시 |

RUX PR/branch 검색은 각각 0건이었다. source 검색의 PR112·113은 각각 RCT synthetic stepper와 RCT-OFF saved-epoch rate diagnostic이며 CR electron-source 선택을 공급하는 문서가 아니다. PR83의 최신 metadata도 확인했지만 본문의 CR 관련 최종 반환은 기존 SYNC03 범위다. 직접 도구 응답 11개를 tool_responses에 보존했다. 비교 기준은 보고서 작성 시각을 추정한 값이 아니라, 보고서에 사용한 **07:51:41 UTC 소비자 intake의 exact heads**다.

## 2. 이미 실제로 공급된 입력

현재 [native pin 원문](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/17f8d0daa72e0f76a49cde01b110f650a6688c42/rust/rei_microphysics/src/axisym_cr_deposition_pin.rs)과 [PHYS01 source manifest](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d9526a75e85202764e845c7d5d79d7f903e7c55/docs/research_sync/CR-PHYS01-20261010/evidence/SOURCE_MANIFEST.json)는 다음 값을 고정한다.

| 입력 | 실제 값 |
| --- | --- |
| proper-clock snapshot | \(t=10^{10}\,\mathrm{s}\) |
| bath | \(T=100\,\mathrm{K}\), \(n_H=140\,\mathrm{m}^{-3}\), \(n_{He}=11.542553191489361\,\mathrm{m}^{-3}\) |
| composition | \(Y_{He}=0.248\), \(x_{HII}=x_{HeII}=\xi\), \(x_{HeIII}=0\); 정확한 \(\xi=0.01,0.1\) 두 knot, 보간 없음 |
| geometry | \(H=3.3\times10^{-17}\,\mathrm{s}^{-1}\), shear \(=3.3\times10^{-18}\,\mathrm{s}^{-1}\), \(a_{rel}=e^{Ht}, b=st\) |
| source / collision range | \(z_{source}=8\), proton \(1\)–\(4\,\mathrm{MeV}\) |
| 실제 manifest quadrature | energy 48, mu 8, age 8 |
| closure | FS10 local terminal deposition, excitation/continuum prompt escape, photon 재주입 없음 |

이는 고정 collisionless proton snapshot에 적용하는 **순간 terminal packet**이다. 현재 [public 함수](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/17f8d0daa72e0f76a49cde01b110f650a6688c42/rust/rei_microphysics/src/axisym_cr_deposition.rs)는 임의의 \(Q_e(W,t)\) history를 받는 API가 아니며 exact packet·gas·time·geometry를 검사한다.

### 원문에 기록된 실제 국소 물리값

| 양 / 단위 | \(\xi=.01\) | \(\xi=.1\) |
| --- | ---: | ---: |
| heat / J m⁻³ s⁻¹ | 1.2093044641845817e−42 | 1.8054996515543073e−42 |
| stored ionization / J m⁻³ s⁻¹ | 1.3963750685843803e−42 | 9.476115446294631e−43 |
| excitation escape / J m⁻³ s⁻¹ | 6.613224299070425e−43 | 2.1689058806714367e−43 |
| modelled ionization loss / J m⁻³ s⁻¹ | 3.2670019626760045e−42 | 2.970001784250914e−42 |
| full proton injection / J m⁻³ s⁻¹ | 5.315371751092545e−34 | 5.315371751092545e−34 |

[보존된 receiver report](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8d9526a75e85202764e845c7d5d79d7f903e7c55/docs/research_sync/CR-PHYS01-20261010/research/REI_RECEIVER_REPORT_KO.md)의 \(\xi=.01\) electron source는 \(5.979293938079537\times10^{-25}\,\mathrm{m}^{-3}\mathrm{s}^{-1}\), source-only 온도 항은 \(+3.811186545594215\times10^{-22}\,\mathrm{K\,s}^{-1}\), geometry 포함 온도 변화율은 \(-6.599999618881346\times10^{-15}\,\mathrm{K\,s}^{-1}\)다. 이번 실행값으로 다시 계산하지 않고 원 기록을 수신했다.

## 3. 아직 공급되지 않은 결속

선택한 CR-on history와 최종 observable, observable의 절대·상대 tolerance, 분모, CR heat contribution fraction은 **null**로 보존했다. 현재 C12 handoff의 Time9 2e−6·spectral24 1e−3 기준은 다른 whole-history gate이며 이 CR 오차 예산으로 쓰지 않는다. packet의 수치적 heat-projection bound도 downstream 물리 예산이 아니다.

실제 native packet과 source-manifest scenario는 존재한다. 그러나 새 proton source constructor 호출 인자 receipt는 이번 범위에서 공급되지 않았다. 이전에 읽은 injection.py의 \(\alpha=2.2\), CR efficiency .1 등은 source의 **default**라는 기존 근거 상태를 유지하며, 별도 실제 호출값으로 승격하지 않는다. injection.py digest c5eda0e60302339af1bbdd0603ae1cd8a8921d9e6489c22d954e0bc92968c27d는 REI manifest에 들어 있다.

이전 source intake의 proton 정상화는 angle-integrated \(dN/(\mathrm{proper\ m^3\,s\,dK})\), \(d\mu/2\), 전체 \(10\,\mathrm{keV}\)–\(1\,\mathrm{PeV}\) energy integral이다. \(1\)–\(4\,\mathrm{MeV}\) active window에 재정상화하지 않는다. 이것만으로 \(Q_e=tA(W)\)의 두 electron birth tag와 M0 input weight가 같다고 할 수 없다. 해당 producer 결속은 부모와 dag_audit가 담당한다.

## 4. 이번 경량 응용에 넘길 경로

부모가 선택한 **독립 fixed-bath \(Q_e=tA(W)\) 응용**에는 위 bath·clock과 기존 원장 의미를 사용할 수 있다. 정확한 \(A(W)\) bytes, electron W 범위와 두 birth tag, proper-clock 원점·prehistory·초기 stock, M0의 bath/operator/selected_record 정규화를 먼저 결속한 뒤 causal heat power를 해당 범위의 새 BASS 결과로 보고하면 된다. REI가 새 최종 관측량을 이미 채택했다는 뜻은 아니다.

현재 receiver의 온도 source 항은 \(2P_{heat}/(3k_Bn_{particles})-T S_e/n_{particles}\)다. 온도 응용까지 확장하려면 새 causal heat와 **일치하는 electron/ionization event 원장**이 필요하다. 옛 terminal \(S_e\)를 새 heat에 조용히 혼합하지 않는다. FS10 terminal heat에 M0 \(p\)를 곱하거나 \(\xi\)를 CR efficiency·heat contribution fraction으로 대입하는 결속도 성립하지 않는다.

M3는 기존 국소 source-zero/provider-no-call 구현과 보존된 실행 근거를 유지하며 **추가 patch가 필요 없다**. 새로운 whole-history receipt를 확보했다고 쓰지 않는다.

## 5. 원문·실행 범위

5개 source 원문은 이전에 Git blob와 SHA256을 맞춘 intake에서 byte 그대로 복사했고 다시 digest를 확인했다. 원문 commit/path/URL/Git blob/SHA256, 직접 도구 응답, current read extent는 SOURCE_IDENTITY.json에 있다. pin·manifest·receiver report·C12 handoff는 이번에 전체를 읽었고 CR module은 정의와 호출부의 선택된 줄을 읽었다. 원격 변경, consumer 코드 변경, 과학 실행, suite 재실행은 모두 **0회**다.
