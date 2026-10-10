# NIST 경계 crossing flux

동결된 excitation graph의 column generator에서 F_B=Q_BA p_A를 읽는다.
각 경계 상태의 정수 meV 에너지, H/He event 수, 초기 전자당 초당 flux,
누적 crossing count를 proper-time epoch에서 반환한다. 부피 또는 bin-width
정규화는 사용하지 않는다. crossing 에너지는 미할당으로 보존하고 HeI
singlet 2^1P는 기존 23s closure와 별도다.

첫 25-row campaign은 1.563초에 exit 0, 모든 계약 검증 행 PASS다. Focused
test 5개도 통과했다. 최대 GL16/32 차이는 1.352e-12로 2e-11 기준 이하다.
독립 Astra review는 PASS_SCOPED다. reviewer는 25개 frozen pair, 1770 boundary entry,
source hash·acceptance rows·receipt accounting을 read-only로 대조했다. stdout packet capture truncation 최초 capture와
당시 HOLD를 그대로 남겼다. Astra 승인으로 acceptance campaign을 반복하지
않고 고정 25개 epoch의 packet만 1회 materialize했다. 원래 소실된 bytes는
NOT_RETAINED이며 새 artifact는 RECOMPUTED_SAME_PINNED_METHOD다. 실제 새 JSON
249337 bytes를 exclusive-create하고 readback pair/count/bytes를 검증했다.
packet SHA256은 df8b917a4fffe665e698d32f1ccf7763200d150f565c24e63a72f33a82da6005다.

P02B coupling 및 전체 CR/IGM history와 global admission은 HOLD다.
