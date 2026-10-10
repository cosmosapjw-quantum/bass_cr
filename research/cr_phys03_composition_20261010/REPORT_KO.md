# CR-PHYS03: 고정 조성 FS10 `xi=0.1` 성분 확장

상태: `PASS_SCOPED` (독립 Astra xhigh 검토 승인).

기존 100 K, `x_HII=x_HeII=0.01`, `x_HeIII=0` 조건부 CR 성분에, 같은
FS10 표의 별도 획득 knot `x_HII=x_HeII=0.1`, `x_HeIII=0`만 추가했다.
보간, 임의 조성/온도, 유한 지연, CR/IGM 시간 history는 추가하지 않았다.

입력 표는 21cmFAST `c01373543fb83a721c48cdcbcd0a08ea53afe78c`의
`log_xi_-1.0.dat`이며 SHA-256은
`3a83d09a3741d11f7d667156d8bd2a6d026fb7f624cbea98e58b789b0a9deea5`이다.
표 header `(fHI,fHeI,fHeII,z,T)=(.9,.9,.1,10,100)`도 source adapter가
정확히 검사한다. 생성 패킷은
`CRP_L17_MD14_RUDD_FS10_XI010_CONDITIONAL_V1`이고 packet SHA-256은
`2ecb1413c93f5cbc9ab64689ac17c191020320c9734138ea4bfaf291e10b6d46`이다.

최초 focused test 실패는 manifest의 dictionary key 전체 경로에 대해 파일명만
검색한 테스트 assertion이었다. provider/source 산출물의 오류가 아니었으며,
경로 suffix 검증으로 고친 뒤 17개 focused Python test가 통과했다.

다음 최소 작업은 CR-PHYS02의 실제 causal secondary-delay kernel이다. 이
composition knot는 그 지연 부재를 해소하지 않으며 단독으로 history 실행을
허용하지 않는다.

독립 검토는 upstream 원본 19,811 bytes, packet/Rust fixture 전 필드, 30개
독립 adaptive quadrature 비교(최대 상대오차 `2.67e-13`), 48/8/8→64/12/12
해상도 비교(최대 secondary-rate 상대차 `5.68e-8`)를 확인했다. 이는 terminal
component의 수치 일관성만 뒷받침하며 cascade 물리나 history를 새로 승인하지 않는다.
