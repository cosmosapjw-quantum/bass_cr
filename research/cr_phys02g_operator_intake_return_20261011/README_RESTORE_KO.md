이 outer return은 manifest 자신을 제외한 모든 regular member의 bytes/SHA256을 기록한다.
새 빈 root에 안전하게 복구하고 RETURN_MANIFEST.json의 정확 membership을 검증한다.
originals/CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip은 원본 완전 전달본이다.
58470931 bytes / SHA256 2920fd78632ba41dce1f2d428db328862d4ad121f1b97bc746962ae847117707.
그 outer manifest의 79 payload+manifest1과 모든 bytes/hash를 검증한 후 내장 G core와
원래 F 실패 tar를 각각 빈 root에 복구한다. G core 안에 완전 F 준비본·E 자료·두 canonical
Astra v4.0.0 하네스가 있다. original_F_family/에는 원래 실제 F family8개+manifest1을
별도로 보존했다. 모두 원래 bytes이며 과거 tar와 47-file publication snapshot 차이는 유지했다.

독립 판정 범위는 PASS_SCOPED_READ_ONLY_INTAKE다. MISSING_PERSISTED_OPERATOR_VALUES와
F HOLD/G BLOCKED는 유지된다. 원래 CSC 비교/재구축이나 물리 실행은 허용하지 않는다.
code/compare_saved_csc.py는 미실행·수치 미검증이다. Diagnostic 창은 종료되었다.
사용되지 않은 G frontier 1회/90초 준비 예산은 비활성이며 재사용 승인으로 보지 않는다.
source_integrity/는 이 수신 호스트의 실제 R3 복구·identity 대조 기록이다.
새 백업의 R1 provider/metadata 확인은 publication receipt에서 따로 제공한다.
