# C21N 연구 계약: 초기 mass-shell 응답과 원 계산식의 준비 연산 재사용

## 권위와 범위

시작점은 BASS PR92의 `645a7f1a960be10e10574a819d7fb35a4511d9fa`이다. 원 물리 source는 계속 REI `3b85dedce84d37b3e165da00685a8a984950aafe`이다. 최신 branch가 존재한다는 이유로 원 trajectory의 source identity를 바꾸지 않는다.

이번 단위는 non-tilted, collisionless LRS Bianchi I의 고정 FP64 40상태, DOP853 `rtol=3e-11`, `atol=3e-13`, 101개 저장 시점, z20→4 문제에 한정한다. 원 81개, 독립 초기응력 26개, NCP98은 재적분하지 않는다. 독립 125개는 26+98+원 중심 1개의 결합이며, 모든 raw/source를 보존한다.

## 독립적으로 닫을 질문

1. 기존 두 성분의 초기 응력이 상쇄될 때, 질량껍질의 서로 다른 적색이동률로 발생하는 국소 shear 응답을 원 moment에서 유도할 수 있는가?
2. 원 분포와 정규화를 매 A마다 재생성하면서 A와 무관한 생성 연산만 worker당 한 번 준비할 수 있는가?
3. 공유 자원 운영에서 디스크·inode와 완료된 125개 초기조건의 중복 실행을 실행 전에 차단할 수 있는가?

첫 질문은 기존 raw의 후처리, 두 번째는 원 constructor/fields/RHS와의 정적 동등성, 세 번째는 test double과 관측 preflight로 검증한다. 신규 ODE나 성능 벤치마크는 이 단위의 검증 수단에 포함하지 않는다.

## 관측량

`sigma=diag(-s,-s,2s)`, `pi_X=diag(-pi_s,X,-pi_s,X,2pi_s,X)`이며 `pi_s,X=(p_parallel-p_perp)/3`이다. Signed coordinates는 `S=sqrt(6)*s/H_t`, `P_X=sqrt(6)*(8*pi*G/c^2)*pi_s,X/H_t^2`; norms는 `Sigma=abs(S)`, `Pi_X=abs(P_X)`이다. 에너지 단위의 `kappa=8*pi*G/c^4`는 `H_geom=H_t/c`와 함께 쓰면 같은 정의가 된다. Photon과 massless neutrino를 더한 radiation tensor, 이어 matter+radiation tensor를 더한 total에 각각 norm을 취한다. `Pi_tot=Pi_m+Pi_r`를 가정하지 않는다.

도함수는 signed amplitudes에 대해 계산한다. norm의 영점 도함수는 쓰지 않는다. 초기 FLRW 중심의 실제 FP 잔차와 normalized-source/SI-component 연산 묶음 차이를 그대로 보존한다. 모델의 isotropic dust는 anisotropic stress가 0인 정의된 성분이고, UV와 baryonic anisotropic stress는 모델에 없는 성분이다.

## 수용과 중단 기준

외부 실행은 source/input/manifest/raw/receipt identity가 연결될 때만 scoped 수용한다. 문서 오기는 원문을 고치지 않고 추가 정정 기록으로 남긴다. 현재 NCP98의 raw identity는 검증됐으며, 문서 identity suffix·CSV 줄바꿈 byte·archive 파일 수의 정정은 `intake/NCP98_CORRECTION_RECORD.json`에 있다.

실제 source 충돌 또는 물리 P0가 발견되면 해당 노드의 promotion만 중단한다. 다른 독립 작업은 계속한다. 가용 자원 부족은 새 dispatch를 줄이고 완료된 raw를 보존하는 사유이며 다른 owner의 파일·프로세스·lease를 바꾸는 사유가 아니다.

`global_error_bound=null`. 초기 국소 Taylor 계수는 전체 시구간 오차보증이 아니다. General triaxial, tilt, fully coupled H/He/UV/stars reionization, 완성된 CMB 예측은 HOLD이다.

## 프로젝트 정책 적용

사용자는 상세 성능 벤치마크를 원하지 않는다. 따라서 정확도·source identity·공유 자원 계약을 검증하고 속도 향상률, 메모리 절감률, 64-core scaling은 `UNMEASURED`로 둔다. 기존 계산을 NCP에서 다시 돌려 성능을 측정하지 않는다. Python 구현은 샌드박스에서 완결하며 NCP에는 선택된 새로운 입력의 실행과 환경 경로 확인만 남긴다.

일상 content 게시에는 실제 ref 확인(R1), 배송에는 manifest/SHA checkpoint(R2), 새 외부 archive 수용에는 다운로드 후 byte 재검증(R3)을 적용한다. Provider ACK와 다운로드 검증은 별도 상태다. 이전 C21F–K의 과학·HOLD·실패·역사적 게시 상태는 변경하지 않는다.
