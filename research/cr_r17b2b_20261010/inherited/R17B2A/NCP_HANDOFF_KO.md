# NCP: bass_cr R17B2A 수신과 R17B2B homotopy certification

담당은 cosmosapjw-quantum/bass_cr만. READONLY donor 외의 REI/BASS_HE/WU088_HH 코드를 변경하거나 대신 실행하지 않는다. parent eb692c19c7cef3e3721f1e044ca3d41151d9309d 및 실제 게시 branch/ZIP/receipt를 확인한다. 새 code는 R17B2A이며 complete R17B2 interval certification이라고 재명명하지 않는다.

## 1. 인계된 완료 작업

본 ZIP은 필요한 original source·BIRTH_PLAN·new code·point/tangent/adjoint results·시험을 포함한다. `reproduce.py --verify-only`로 SHA/CRC/선택 manifest를 확인하라. 새 환경에 대한 one-shot 재현만 필요하면 `python -B reproduce.py --output NEW_EMPTY_DIR`; 원 donor root/old R16B/R17A/B1 과학 suite는 돌리지 않는다.

NumPy point backend는 gas g=(h,y,z,w/W0), photons p/H, u=t/Tf다. donor의 p/P0와 photon gradient row/column scale을 혼동하지 않는다. `response.py`의 block에 gas→old photon C=-p grad(kappa)가 필요하다. photo gradient gas A와 full nonphoto Jacobian도 유지하라. `birth_response.py`는 같은-state nominal optical adjoint를 구하고 임의 b의 별도 survival/forcing ODE를 적분한다. K를 기존7개 photon adjoint의 birth시각 보간으로 만들지 않는다.

새 데이터는 η=0, nominal weight/energy point다. 모든12 query에서11 nonzero optical response positive/temperature negative인 것은 표본 진단이지 whole-b/eta 부호 정리가 아니다. 작은 opacity-memory correction을 버리지 마라. local-opacity-only control은 photon conservation을 깨는 negative-control이며 물리적 fallback이 아니다.

## 2. 다음 heavy 연구 R17B2B

mu_eta=(1-eta)mu_Q+eta Sdb, eta in[0,1]. 초기 photons와 source parameter theta를 일치시키고, 실제 continuous source photon density와 gas를 결합한 Volterra/sensitivity 시스템을 interval화하라. 더 촘촘한 finite births로 continuous source를 대신할 경우 그 추가 구적오차를 독립적으로 포함해야 한다. nominal K가 정확해도 ∫0^1(K_eta-K_0)deta remainder 없이 finite-source error에 사용하지 마라.

REPORT_KO.md의 photon memory 식과 adjoint를 구현된 baseline으로 사용한다. 새로운 numerical source coefficients/temperature floor를 추가하지 않는다. 새 same-model interval RHS를 독립 backend와 대조하되 R16B의 공유 AD 검산과 독립 RHS를 구분한다.

이번 physical lemma: cutoff/thermal branch-free smooth region에서, background birth와 arbitrary probe의 physical injection energy가 동일하면 K,K_b,K_bb의 known atom jump는0이다. 이는 gas continuity 및 additive source, photon-adjoint PDE의 energy trace smoothness를 요구한다. donor 전체 η에 이 전제가 실제 확보됐는지 먼저 검증하라. 그렇다면 known6 atom에서 J0,J1,J2 불확실한 box를 임의로 도입하지 말고 정확0을 써도 된다. 다만 서로 다른 energy channel 또는 다른 branch/cutoff 경계에는 이 소거가 적용되지 않는다. K_bbb jump와 regular K_bbbb는 여전히 필요하다. toy의 -93/20000을 실제 FT03 jump값으로 쓰지 마라.

기존 R17B1은 local x=(b-left)/width의 derivatives와 factorial-normalized moment defects를 받는다. global u=b/Tf derivative의 r차는 (width/Tf)^r로 변환하고 factorial을 다시 나누지 마라. 실제 첫 source cell의 coefficient가99.7754%인 것은 예산비이지 물리오차비가 아니다.

## 3. 결과/중단 판정

새 homotopy-uniform source signed interval, nonlinearity/source quadrature/birth regularity evidence를 별도 기록하고, 기존 R17A의 두 distinct derivations를 혼동하지 말라. 개선이 인증되면 선택한 같은 fallback source 상계를 교체하고 R16B time interval을 한 번만 더한다. 새로운 bound가 더 넓으면 NO_CERTIFIED_SOURCE_SHARPENING으로 종료한다. 물리적 heating/ionization/cosmic-ray 효과와 instantaneous derivative를 구분한다.

새 unit RED→GREEN, source/clock/channel corruption 거절, finite-dose vs tangent, full forward vs backward identity, interval inclusion을 실행하라. 새 heavy kernel 자원은 실제 NCP cgroup/CPU/RAM으로 admission하고 coordinator1CPU와 여유RAM16–24GiB, thread1, no fastmath를 유지한다. 기존 source/timing/atom 승인 ceiling은 유지한다.

새 branch에 nonforce push 및 create-only Drive+Dropbox backup, 실제ACK/name/size만 R1으로 기록한다. 원 source bytes·전체 연구코드·실행기·검산·실패로그·sourcebinding·결과·계약·복구목록을 봉인하라. 사용자에게 원래 파일이나 해시를 다시 묻기 전에 연결된 ZIP/manifest를 읽는다. 입력이 없다면 해당 단계만 BLOCKED로 남긴다.

보호: CR_OFF_FASTEST, precision atomic PARKED, physical/production HOLD, G02UNRESOLVED, b_gridNO_GO; Grackle와G02 다른lane은 수행하지 않는다. final `BASS_CR_NCP_R17B2B_RETURN_KO.md/json`, `RECOVERY_INVENTORY.json`, immutable ZIP, detached DELIVERY_RECEIPT.json.
