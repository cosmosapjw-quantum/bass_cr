# BASS CR R4W — G02 미분 검증의 오차 원인 분리

2026-10-01. 범위는 기존 B0,100keV/u,b=2a0의 G02 한 단계다. 이전 R4V commit은 `cfb53b24217f5663008d44acc8305975320ab310`이다. 저장된72개 연산자와 실제 기저 계수에 대한 분석·정확 산술·고정밀 기준 계산을 수행했다. 새 native 연산자·궤적 호출은0회이며 기존 기저,연산자,허용오차와 G02 실패 결과는 바꾸지 않았다.

**핵심 결과는 잔차를 세 원인으로 분리하고, 가장 큰 동일 중심 잔차의 주원인을 저장된 기저 표현까지 추적한 것이다.** 교차 블록의 큰 잔차는 중앙차분 절단오차와 정합적이다. 동일 중심의 작은 잔차에는 단순 상쇄 산술 외에 저장 FEM polynomial의 경계 불연속이 들어 있다. 정확한 경계식과80/120자리 계산을 구현했고, 별도로 연속성을 회복하는 후보 표현도 검산했다. 이 국소 진전은 전체 G02 또는 production을 닫는 결과는 아니다.

| 구분 | 실제 관측 | 근거 상태 |
|---|---|---|
| 교차 TP/PT, h=0.05 | 원소 최대 잔차2.11465×10⁻⁶;32→40차 공간 적분의 FD 차이는 최대7.96713×10⁻¹⁶ | numerically checked;절단오차 해석을 지지하나 공간 적분의 인증 상계는 아님 |
| 동일 중심 TT/PP overlap | 시간에 따른 계산값 변화 최대2.22045×10⁻¹⁶;실제 구현은 핵 거리R에서 적분 구간을 다시 분할 | implementation-verified / numerically checked |
| 동일 중심 PP[9,13] | ±0.560931 항에서 약−1.65×10⁻¹⁴ 잔차;해당 FD는 모든 기존h에서0 | numerically checked |
| 저장된 FEM 계수 | 내부 경계 jump 최대1.5876189252×10⁻¹⁴ | exact rational check on binary64 input |
| 경계 결함의 독립 예측 | PP[9,13]에−1.7851470658×10⁻¹⁴;z=−32 캐시와의 차이1.3091475907×10⁻¹⁵ | derived / numerically checked |
| 연속성 회복 후보 |6개 s–p_z 쌍의 경계 합이 정확히0;radial 상대L² 변화 최대1.18274×10⁻¹⁴ | derived / implementation-verified;별도 후보이며 production 미채택 |

**직접 유도한 계산식.** 같은 중심에서는 공통 translation과 ETF phase가 overlap에서 상쇄되어 \(\dot S^{CC}=0\)이다. 이상적인 \(H_0^1\) 기저에서는 적분 부분적분으로 \(A_j+A_j^\dagger=0\)가 된다. 반면 구간별로 저장된 polynomial의 strong derivative만 적분하면 내부 경계 jump가 남을 수 있다. B0의 실수 s–p_z 채널에서는

\[
A_{sp}=\frac{I_{sp}+J_{sp}}{\sqrt3},\quad
A_{ps}=\frac{I_{ps}-J_{sp}}{\sqrt3},\quad
I_{ab}=\sum_e\int_e u_a u'_b\,dr,\quad J_{sp}=\sum_e\int_e\frac{u_su_p}{r}\,dr.
\]

따라서 큰 두 D 원소를 빼지 않는 독립식은

\[
D_{sp}+D_{ps}^{*}
=-\frac{v}{\sqrt3}\sum_e
\big[(u_su_p)(r_e^-)-(u_su_p)(r_{e-1}^+)\big].
\]

여기서 v=2.00798106651023a0/ta이고 D의 단위는ta⁻¹이다. \(t_a=\hbar/E_h\)이며 기저의 ETF에는 물리 단위로 \(m_e/\hbar\)가 들어간다. 기저·단위·각운동량 부호·경계조건 및 일반 교차 블록의 유도는 `DERIVATION_KO.md`에 있다.

모든 binary64 계수를 `Fraction.from_float`로 정확한 이진 유리수로 바꿔 경계 합을 계산했다. 각 I는 polynomial의 정확 적분, J는 정확 polynomial division 뒤 로그를 사용하는80/120자리 Decimal 적분으로 별도 계산했다. 수치 quadrature와 angular rule을 재사용하지 않는다. 소스와 입력은 실제 캐시의 문맥에 결합했으며, BASIS.json의 identity 문자열뿐 아니라 byte SHA도 확인했다.

| PP 전역 index, z=−32 기준 | 경계식의 D합 | 저장 D의 정확한 합 | 둘의 차이 |
|---|---:|---:|---:|
|9,13|−1.7851471×10⁻¹⁴|−1.6542323×10⁻¹⁴|+1.3091476×10⁻¹⁵|
|9,16|−6.6380088×10⁻¹⁵|−6.1617378×10⁻¹⁵|+4.7627101×10⁻¹⁶|
|10,13|−2.2121476×10⁻¹⁸|−8.9172273×10⁻¹⁶|−8.8951058×10⁻¹⁶|
|10,16|−2.0820827×10⁻¹⁵|−1.9845237×10⁻¹⁵|+9.7559089×10⁻¹⁷|
|11,13|+3.1529333×10⁻¹⁵|+3.0808689×10⁻¹⁵|−7.2064435×10⁻¹⁷|
|11,16|−6.5760384×10⁻¹⁷|−1.1102230×10⁻¹⁶|−4.5261918×10⁻¹⁷|

지배 원소9,13에서는 표현 결함이 관측 잔차와 같은 부호·크기를 설명한다. 다만10,13처럼 표현 결함보다 산술·적분 경로 차이가 큰 원소도 있다. 한 원인의 비율을 모든 원소에 적용하지 않는다.80자리와120자리 결과의 최대 차이는 약4.421×10⁻⁷⁶이었다. 이는 **반올림된 입력 계수에 대한 기준 계산의 수렴**이며 실제 물리 기저나 연산자가76자리 정확하다는 뜻이 아니다.

**실행한 개선 후보.** 각 셀의 원래 polynomial을 유지한 별도 정확 산술 복사본에 \(\delta_e s\)를 더했다. \(s\in[0,1]\), \(\delta_e=u_{e+1}(0)-u_e(1)\)이며 마지막 셀의 오른쪽 목표는0이다. 왼쪽 값과 모든 내부 경계가 정확히 연결되고 외곽 Dirichlet trace도0이 된다. 이 후보는 기존 nodal FEM의 원자료를 복구했다고 주장하지 않으며, 저장 원본에 덮어쓰지 않았다.

\[
\|\delta u\|_{L^2(dr)}^2=\sum_e\frac{h_e\delta_e^2}{3},\qquad
\|\partial_r\delta u\|_{L^2(\mathrm{cells})}^2=\sum_e\frac{\delta_e^2}{h_e}.
\]

두 번째 양은 **셀 내부 strong derivative의 broken norm**이다. 원본이 불연속이므로 전역 약미분/H¹ 차이노름으로 부를 수 없다. 이 작은 radial L² 변화가 전체 H,D,전파 또는 관측량의 오차 상계를 주는 것도 아니다. 연속성 자체와6개 경계 항의 정확한 소거만 이 후보의 검증 범위다. raw D를 반대칭 투영해서 잔차를 없앤 것은 아니다.

**단순 위상 제거는 이번 문제의 해법으로 채택하지 않았다.** ballistic 두 중심의 중점 좌표에서는 교차 overlap의 공통 시간 carrier가 이미 정확히 상쇄된다. lab-frame ETF의 \(-v^2t/2\)만 제거하면 인위적인 carrier를 다시 넣을 수 있다. 이 결과는 derived이며, geometric derivative를 쓰려면 저장 표현의 움직이는 interface 항까지 다뤄야 한다. 기존 R8 한 점을8차 수렴이나 연속 오차 상계로 해석하는 것도 허용되지 않는다.

**구현과 검증.** `cache_error_budget.py`는128개 블록 진단과64개 교차 resolution 비교를 수행했다. `exact_trace_oracle.py`는6개 s–p_z 쌍을 두 정밀도로 계산하고48개 저장 성분과 비교했다. 새 집중 테스트는 캐시 예산6개,정확 적분 기준8개로 총14개다. 독립 검토에서 derivative norm의 적용 범위와 metadata byte binding을 보완했고 해당 변경을 실제로 다시 검증했다. 최초 실행과 수정 전 소스는 `runs_r4w/initial_reference/`에 보존했다. 이전 R4V41개·R4U43개 테스트와184회 native 계산은 재실행하지 않았다.

**현재 결정.** G02의 동일 중심 잔차 원인 분리와 기준 계산 구현은 완료했다. 원래 raw FD gate는 UNRESOLVED로 유지한다. production=HOLD,capture=false,all_bound=OPEN,b_grid=NO_GO이며,NCP64 scaling과 MPI 물리 실행은 이번에도 수행하지 않았다. 이 작은 정확 산술 기준 문제에는 병렬 물리 적분을 다시 실행할 필요가 없었다.

다음 최소 구현은 shared endpoint/nodal 정보를 보존하는 새 기저 평가 표현을 별도 입력 identity로 만들고, 기존 bank와의 S/H/D 차이를 정량화하는 것이다. 그 후 교차 블록에서 interface-aware geometric derivative 또는 별도로 설계한 고차 차분 검증을 수행해야 한다. 현재의 h 사다리를 그대로 반복하거나 tolerance만 완화하는 작업은 이 원인을 해결하지 않는다.

결과 JSON·CSV와 DB 업데이트에는 원래 실패와 이번 국소 결론을 분리했다. 최종 독립 검토, DB 보존 검증, commit과 두 provider의 저장 상태는 패키지의 검토·검증 파일 및 외부 전달 영수증에 기록한다.

최종 독립 검토는 `PASS_LOCAL_DIAGNOSIS_REFERENCE_ONLY`다. 독립110자리 기하급수 적분은 핵심 원소를 약2.22×10⁻¹¹⁰ 차이로 재현했고,128개 블록·64개 resolution 비교의5,382개 scalar를 별도로 검산했다. 원래 G02 상태는 승격하지 않았다. DBv9은 DBv8의40개 테이블·3281행과 이전 상태 view를 보존하고 증거8개 및 G02 상태1개를 추가했다. SQLite integrity는ok,FK 위반은0이다. DBv9 SHA256은 `9bb4cf4f819b54e354a256f32b8b1a8d01fb98385867e2ae98c5005dfcb3bb58`다.
