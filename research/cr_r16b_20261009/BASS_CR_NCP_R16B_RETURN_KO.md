# BASS_CR NCP R16B 연구 반환

R16B는 원 FT03 fixed-birth shadow 모형의 32개 cell과 여섯 birth를 그대로 사용하여 실제 전시간 signed Jacobian, residual, secant 비선형 remainder 및 후방 adjoint를 구간산술로 계산했다. variant=0, proper-time [0,1.25e9] s, 원 photon energy와 원자상수를 유지했다. 2,048개 dyadic 패널에서 전방 affine 오차와 후방 adjoint를 따로 전파했다.

조건부 signed optical-depth 시간오차 인증구간:

`[1.93952149246122105640334464568857077003923403510713337451052e-17, 2.00673392521469305112644147185875600842764948764166993310174e-17]`

폭은 R15의 0.26720162145448634배이며 약 73.28% 줄었다. `CERTIFIED_SHARPENING`이다. 개선은 전시간 패널 세분화, signed adjoint 및 secant remainder 제한의 결합 결과다. 같은 패널 수의 ablation을 수행하지 않았으므로 개선 전체를 adjoint 하나에 귀속하지 않는다. nonlinear optical-depth radius는 `7.44045776368821266851229368497515764686656060953364792728887e-26`이다.

초기 상태만 원 입력에 따라 정확하다. 그 이후 모든 incoming state error를 전파하며, 여섯 birth의 같은 theta generator를 상태와 누적 목표량에 유지한다. birth interface는 원 embedding B와 B^T를 사용한다. 첫 cell의 기존 Picard 증명과 donor 과학 suite는 재실행하지 않았다. R16 midpoint-Jacobian 값은 인증이 끝난 뒤 검산 대상으로만 비교했다.

MPFR256의 별도 전방·후방 구간 전파와 Decimal60 경로가 교차하며, 모든 32개 cell의 backward boundary가 Decimal 구간에 포함되었다. 독립 경로는 동일한 FT03 AD 패널을 입력으로 공유한다. 따라서 독립 전파 산술 검산이며 독립 RHS backend나 proof assistant 검증은 아니다. 인증은 원 donor의 all-prefix/Picard 및 directed Decimal exp/ln 조건에 의존한다.

원 R16A의 첫 macro, constant-S 연속 방출원 대 native 조건부 양성구간 `[8.277438669507532e-18,3.122831876267941e-17]`을 원본 bytes로 보존했다. 같은 source upper `1.021773e-17`을 새 시간오차에 정확히 한 번 합치면 `[9.17748492461221051e-18,3.02850692521469334e-17]`이다. 정확한 rational 값은 `results/final_math/COMBINED_TAU_R16B.json`에 있다. source 생산자·ledger를 대체하거나 source 오차를 이중 계산하지 않았다.

Xeon Gold 5220의 실제 CPU affinity는 64개, RAM 약 125 GiB다. coordinator CPU 1개와 RAM 24 GiB를 예약하고 각 worker의 라이브러리 thread를 1로 제한했다. 1/2/4/8 worker bounded kernel pilot 결과와 bitwise identity를 기록했으며 새 재현에서는 worker 8개만 사용한다. 초기 uncompressed affine 전파가 느려져 명시적으로 중단(exit130)한 실패 기록을 보존했다. 완료된 32-cell Jacobian과 adjoint 증거를 재사용하여 outward nonbirth generator compression으로 전방을 완료했다. 복구 완료 peak RSS는 119188 KiB, MPFR 검산은 90548 KiB, 중단 run은 147828 KiB였다. 실패를 과학 PASS로 바꾸지 않았다.

새 focused RED→GREEN 및 거절·반례 시험 15개가 통과했다. 잘못된 birth/clock/variant/source bytes, transpose dimension, source domain, 비정확 panel clock, birth correlation 소실을 검사한다. 마지막 원본 ZIP 기반 fresh reproduction도 exit0으로 통과했다. 265.57초, peak RSS147544 KiB였으며 과학 패널 전체, 후방·MPFR 과학 증거 및 최종 인증·source 결합 값이 일치했다. 전방 affine 증거는 generator 합산 순서에 따른 Decimal 마지막 자리 차이만 있으며 둘 다 outward 구간이다. 명령과 source SHA는 실행증거에 기록했다. 기존 R15·R16 완료 suite는 수행하지 않았다.

직접 rclone은 설치되지 않았으나 기존 인증된 Dropbox connector로 원 R16 ZIP을 회수했다. SHA-256 `b6a537d87e626831073ced6354ac20c13a6dc180f9fa846cef6a1d5b434d45d5`, 6654503 bytes, R16 manifest44개와 nested R15 manifest95개를 검증했다. 원 checkout의 두 미추적 기존 results 디렉터리는 보존했다. REI repository 및 다른 donor 저장소는 수정하지 않았다.

Grackle은 새 same-model/source/clock/owner accepted stage가 없어 `BLOCKED_OWNER_INPUT`이다. G02 authoritative bank의 고정 파일·native build가 없어 `BLOCKED_INPUT`, scientific PASS는 없다. 정확한 파일명과 SHA는 `G02_READINESS.json`에 있다. `CR_OFF_FASTEST`, `G02=UNRESOLVED`, `b_grid=NO_GO`, precision atomic `PARKED`, `physical/production=HOLD` 및 승인 제한은 그대로다. observer tail과 물리적 원자율 정확성은 이 첫 macro 시간오차 인증의 범위 밖이다.

배포는 bass_cr의 `research/ncp-r16b-20261009`에 non-force push하고 기존 Drive/Dropbox 폴더에 불변 ZIP을 create-only로 저장한다. 과학 패키지 seal 뒤의 실제 provider ACK/ID/size와 최종 Git HEAD는 별도 delivery receipt에 기록한다. 패키지 안의 PENDING 상태는 seal 시점의 상태이며, 백업 완료 판정은 최신 반환·receipt를 따른다.

배포 완료: 과학 commit `bab4d1527d6750040ad5d2618b565d494f1ed70a`를 `research/ncp-r16b-20261009`에 non-force push하고 `ls-remote` 일치를 확인했다. ZIP SHA-256은 `c753f152bd6ac55cf12ae264d25ab8297d74e8d15c230d0d73721ce8418be8a3`, 26999284 bytes다. Drive ID `1mQsDsV73buNoEQPNo6Vaqpn75hxPFu1K`, Dropbox ID `id:BSpOijBcT10AAAAAAD3jkg` 모두 실제 완료 ACK와 size 일치로 R1 완료이며 sealed artifact R2 metadata/manifest 대조를 기록했다. Provider SHA-256은 UNAVAILABLE이고 원격 본문 readback은 수행하지 않았다. 원 ZIP 내부 PENDING 상태는 seal 시점 상태다. 최신 상태와 최종 Git HEAD는 post-seal receipt/sidecar를 따른다. sealed ZIP 자체에서 157개 멤버·CRC, 원본 manifest 및 새 시험15개의 recovery verify-only가 통과했다.
