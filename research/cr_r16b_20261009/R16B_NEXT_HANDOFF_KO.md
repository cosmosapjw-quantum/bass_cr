R16B 조건부 인증 결과와 R16A 보존·source 단회 결합은 R16B_REPORT_KO.md 및 정확 rational JSON을 따른다. immutable ZIP 원본과 MANIFEST를 먼저 검증한다.

새 과학 재현(부모 suite 실행 없음):

```bash
python3 -m venv /tmp/r16b-venv
/tmp/r16b-venv/bin/pip install -r research/cr_r16b_20261009/requirements.txt
/tmp/r16b-venv/bin/python -B research/cr_r16b_20261009/reproduce.py --archive inputs/BASS_CR_R16_THEORY_20261009_v1.zip --output /tmp/r16b-fresh-output --workers 8
```

기존 package/source 검증과 새 시험만 실행하려면 `--verify-only`를 붙인다. output은 존재하지 않는 경로여야 한다. 원본 입력을 덮어쓰지 않는다. 24 GiB RAM/1 CPU reserve를 유지한다. 8 worker 상한, thread1, 각 step900초 timeout이다. 작은 호스트는 worker를 낮추되 실제 cgroup 제한도 별도로 확인한다. 동일 입력의 부모 완료 시험을 동기화 목적으로 반복하지 않는다.

새로운 연구는 independently bound RHS interval backend, 생략된 source/tail의 정당한 별도 증명, 또는 실제 same-model owner input이 들어왔을 때만 진행한다. precision atomic/physical/production과 G02 게이트는 그대로이며 이 결과로 승격하지 않는다. REI BRIDGE13/14/15는 read-only donor다.
