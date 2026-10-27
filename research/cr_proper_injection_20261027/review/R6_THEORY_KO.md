# R6 독립 이론 검토

**판정: 명시된 조건부 이론 범위 PASS_SCOPED.** 발견한 두 적용 조건 누락을 root가 본문에 보완했고 수정된 파일을 다시 읽었다. 최종 `THEORY_KO.md` SHA256은 `591396d2d49c549f4f67de590ffc8365ae0b12c95581c5cfb3c1d94e501da6ad`다. 새로운 source 수치 계산·source quadrature·projection·RHS·solver·Wolfram 호출은 모두 0이다. C6–C9 구현 및 수치 판정은 별도다.

검토자는 `/root/source_qualification`이다. 앞서 source qualification과 WU delta 메타데이터를 작성한 사실을 공개한다. 이번 검토 대상 유도는 `/root/theory_review`와 root가 작성했다. 기존 자체 메타데이터를 독립 증명으로 세지 않고 원 source 코드와 저장 NPZ metadata, 직접 대수 유도로 확인했다.

## 핵심 검토

원 `q_proper`에는 z=8의729와 angle-integrated normalization이 이미 들어 있고, `DirectElectronSource`에서 중성 target 밀도를 한 번 곱한다. 원 Rudd cross-section의4π는 source 각도 적분을 다시 하라는 인자가 아니다. 저장 source projection에는 energy quadrature가 이미 포함되므로 b/E에 새 bin width도 곱하지 않는다.

원 코드에서 [A(W)]=m⁻³s⁻²eV⁻¹, Qe=tA이다. U*=eV m⁻³이고 S=U*/T²이므로 active energy row b와 cutoff_E는 무차원, b/E와 cutoff_N은 eV⁻¹이다. 따라서
`N=M*S*(sum(b/E)+cutoff_N)`,
`U_eV=M*S*(sum(b)+cutoff_E)`
의 차원과 정규화가 맞는다. 원 source의 heat/binding/excitation 및 ionization-counter row는 0이다. cutoff9605/9608은 포함하고 existing projection을 중복 기록하는 low_cross9609/9610은 제외한다. fullBED/legacy의 source 배열은 실제 byte hash가 같으며 두 donor source로 합산하지 않는다.

M(a,b)=(b−a)(b+a)/2는 0≤a≤b≤T에서 직접 적분된다. 두 반구간의1/4와3/4, zero-width 적분0, 구간 가법성이 따른다. 이 결과는 원 구현이 선언한 finite local-ramp history에 의존한다. T 이후 continuation/shutoff와 conditional mean time exposure는 도입하지 않는다.

RR backward reward와 forward density의 duality로 finite return의 f_(T−s) convolution을 얻는다. K⁻¹r는 eventual cohort reward다. n′=j−kn의 scalar 사례에서도 eventual−finite=n(T)가 되어 두 horizon을 구별한다. PHYS02 100 K·HeIII0과 기존 PR107 10000 K·nHeIII.01 cm⁻³의 mismatch를 finite history만으로 없애지 않는다.

직접 quotient rule은 dY/dτ=(R_i−Y_i R_B)/n_b를 주며 같은 부피의 finite change는 (Δn_i−Y_iΔn_b)/(n_b+Δn_b)다. 실제 nb가 없으므로 native25는 null이다. 원 RR의 조건부 He4III→He4II 부호와 -E−I+(E+I)=0, retained-photon 별도 port도 일관된다. 이 검토는 caloric/cutoff 항을 physical heating으로 승격하지 않는다.

## 발견 및 교정

| ID | 발견 | 교정·종료 |
|---|---|---|
| R6-F01 | 일반 polynomial coefficient 공식의 affine clock·공통 영점·상수 인자 전제가 본문에서 불명확했다. | §11에 각 segment s=c_tau(τ−τ_start), c_tau>0 상수, c_V/target 상수, 같은 시간 영점과 time-dependent Jacobian 지원 제외를 명시했다. 수정 확인 후 CLOSED. |
| R6-F02 | generalized quotient의 양의 초기·최종 denominator 및 removal domain을 명시할 필요가 있었다. | §5에 n_b>0, n_b+Δn_b>0, removal 시 final species≥0을 명시했다. 수정 확인 후 CLOSED. |

## Source revision의 정확한 의미

`4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`는 이 source를 고정한 **이전 snapshot**이다. 최초 생성 또는 실제 원 worker 실행 commit이라고 판정하지 않는다. 이번에 original Git 경로의 `injection.py`, `causal_subthreshold.py`, `causal_cascade.py`를4ca5와D에서 각각 읽었다. 두 revision의 Git blob SHA1, 원문 SHA256 및 D에 보존된 lineage bytes가 모두 일치한다. 해당 세 파일의 bytes/원 경로/두 ref/두 hash와 원 NPZ identity는 JSON에 담았다.

남은 actual RR·retained output과 nb/native25 입력 gate는 유지한다. 검토는 현재 이론을 채택할 근거이며 아직 실행하지 않은 새 adapter 수치나 전역 물리 완료를 채택하는 근거가 아니다. 중앙 원 집계27/88, 이번 효과0, L4=false 및 전역 null들을 유지한다.

