# FS2010 실제 표·코드 취득 및 사용 범위 감사

검토일: 2026-10-10 UTC. 런타임 모델 식별: UNKNOWN. 외부 저장소 변경·push 없음.

## 결론

FS2010은 더 이상 ‘표를 요청해야만 얻는 후보’가 아니다. 저자 연구그룹 공식 페이지가 전자 침적 표와 C 보간기를 공개하며, 이번 실행에서 실제 tar 310,272 bytes를 다운로드했다. 14개 이온화율 × 258개 전자 에너지 표이다. 에너지축이 8개뿐인 MEDEA 묶음보다 직접적인 수치 비교·에너지 적분에 적합한 자료를 확보했다. 다만 **원본 C의 이온화율 좌표와 일부 표 헤더가 모순**되므로 그대로 운영 코드에 편입하지 않는다. 정확한 일치 좌표만 우선 사용하는 독립 adapter가 가장 작은 검증 가능 경로이다. 이것은 전자 또는 생성된 2차 전자의 침적 provider이며, 입사 양성자의 감속·2차 전자 생성 provider는 아니다.

## 취득 증거와 라이선스

- 공식 설명: https://cosmicdawn.astro.ucla.edu/codes_and_tools.html
- 원본 tar: https://cosmicdawn.astro.ucla.edu/elec_interp.tar
- 원본 tar SHA256: `e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101`.
- 원본 위치: `../vendor/fs10/elec_interp.tar`; 실제 파일: `../vendor/fs10/official/`.
- 공식 tar에는 별도 LICENSE 파일이 없다. 공개 다운로드 가능성과 명시적 재배포 라이선스를 같은 주장으로 취급하지 않는다.
- 별도로 **21cmFAST 공식 MIT 저장소**의 동일 표 14개, C/H 보간기 및 MIT LICENSE를 취득했다. 저장소 commit `c01373543fb83a721c48cdcbcd0a08ea53afe78c`, commit UTC `2026-10-06T05:28:48Z`.
- 거울 위치: `../vendor/fs10/21cmfast/`. 17개 파일 290,985 bytes. 모든 파일의 Git blob SHA1 및 byte 길이를 조회된 tree와 대조하여 정확한 일치를 검증했다.
- **14개 표 모두 원본과 최종 newline만 제외하면 byte 단위 동일하다.** 21cmFAST 저장소 MIT 공지를 보존한다. 원저자의 별도 라이선스 선언이 tar 안에서 확인된 것은 아니다.
- 원본/거울 파일별 SHA256, Git blob, 물리 축, closure 잔차는 `FS10_ACQUISITION.json`에 기록했다. fetch envelope도 보존했다.

## 실제 파일의 물리 계약

각 표의 첫 두 줄은 `fHI fHeI fHeII z T(K)` 및 실제 값이다. 모든 표의 명시적 fiducial 조건은 **z=10, T=100 K**이다. 숫자 본문 9개 열은 다음과 같다.

| 열 | 의미 | 단위/중복 규칙 |
|---|---|---|
| 0 | 입사 전자 운동에너지 | eV. 헤더 문구는 `Photon Energy`이나 C/H 인터페이스는 전자 에너지이며 초기 광이온화 손실을 제외한다고 명시 |
| 1 | 총 이온화 에너지 분율 | 무차원; 종별 n_ion에서 다시 계산한 에너지를 더하여 이중 계수하지 않음 |
| 2 | heat 분율 | 무차원 |
| 3 | 전체 잔여 excitation 에너지 분율 | 무차원; Lyα는 부분집합 |
| 4 | 생성 HI Lyα 광자 수 | 입사 전자당 개수 |
| 5–7 | HI, HeI, HeII 이온화 수 | 입사 전자당 개수; 분율이 아님 |
| 8 | Shull heating 비교값 | 참고 열; 선택 provider의 heat로 대체하지 않음 |

실제 에너지 구간: **10.0 ≤ E/eV ≤ 9937.21**, 모든 표에서 같은 258개 격자. 모든 검사 대상 물리 채널은 비음수이다. `f_ion + f_heat + f_exc`의 최대 절대 잔차는 **3.9×10^-5**다. 원본의 반올림 및 Monte Carlo 오차를 드러내며 임의 renormalization으로 숨기지 않는다. Lyα 광자에 해당하는 에너지는 `10.2 eV × n_Lya`이며 excitation 총량에 다시 더하지 않는다.

원 C는 E와 xHII에 순서대로 선형 보간한다. E가 상한을 넘으면 상한 근처로 고정하고, 이온화율도 양 경계에 고정한다. 이는 공개 구현의 선택이며 새로운 물리적 외삽 검증은 아니다. 새 adapter는 구간 밖 입력을 명시적으로 거절하는 것이 좋다. 원본 C는 작은 문자열 버퍼에 fscanf를 수행하므로 raw C 실행보다 안전한 독립 파서를 권한다.

## 발견된 좌표 모순과 최소 사용 가능한 부분

1. `log_xi_-3.6/-2.6/-1.6.dat`의 표 헤더 HeII는 각각 `0.0002138, 0.002138, 0.02138`이다. 원 C와 현재 21cmFAST C의 대응 xHII 좌표는 `0.0002318, 0.002318, 0.02318`이다. 2.138 대 2.318의 전치가 어느 쪽의 오류인지 자료만으로 확정하지 않았다. 자동 수정 금지.
2. `log_xi_-4.0.dat`는 HI=HeI=0.9999이나 HeII=0.001이다. HeI+HeII=1.0009로 조성 합이 1을 넘는다. 이 헤더를 정상 조성으로 수용하면 안 된다.
3. `-3.3` 표의 HI 값은 소수 6자리로 반올림되어 1−HI와 HeII 사이 작은 차이가 있다. 헤더 precision 허용오차와 진짜 좌표 모순을 구분해야 한다.

즉시 통과시킬 수 있는 보수적 부분은 **xHII=0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999**의 원본 표이다. 이들에서는 C 좌표, HI=HeI=1−xHII, HeII=xHII가 일치한다. HeIII=0이며 임의 H/He 조성 공간의 검증이 아니다. 원표의 다른 좌표들은 값 자체를 변조하지 않고 `metadata_conflict`로 보존한다. 더 작은 smoke test는 xHII=0.001 또는 0.01 한 개를 고정하고 실제 E 격자점에서 수행할 수 있다. threshold 양쪽을 가로지르는 interpolation은 별도 검증 대상으로 둔다.

## 이론 연결과 한계

논문: Furlanetto & Stoever, *Secondary ionization and heating by fast electrons*, https://arxiv.org/abs/0910.4410 (MNRAS 2010). 모델은 고정된 primordial gas에서 전자 cascades를 계산하고, He excitation에서 발생한 이온화 광자를 다시 흡수시키는 근사를 사용한다. 따라서 이를 이미 포함한 최종 분율과 별도의 동일 He 광자 재흡수 source를 동시에 더하면 이중 계수가 된다. 저밀도 의존성이 약하다는 설명은 임의 T·z에서의 별도 수치 격자를 제공한다는 뜻이 아니다. 재이온화 계산에서는 침적시간·이동거리와 배경 변화시간을 비교한 국소성 조건을 추가해야 한다. 이 표는 자기장/각도/비등방성 축을 제공하지 않는다.

새로운 anisotropic IGM solver에서는 local matter frame의 전자 kinetic energy를 입력한다. FLRW/Bianchi 차이는 공급된 전자 분포와 수송에 두며, 표 자체에 임의 shear 계수를 곱하지 않는다. 양성자 source → 전자 생성 kernel → 전자 cascade의 각 에너지 ledger를 분리한다. 초기 proton ionization binding energy와 secondary-electron kinetic energy를 합한 값이 원 proton loss를 넘지 않아야 한다.

### 선택 권고

`fs10_reference_subset`을 **실제 수치 자료가 있는 electron terminal deposition adapter 후보**로 올린다. 메타데이터가 맞는 7개 xi 표, 명시적 electron source, table-knot 검증부터 진행한다. 21cmFAST MIT mirror의 해당 원자료와 공지·정확한 commit을 함께 pin한다. MEDEA 8점 표는 독립 비교 자료로 보존한다. 양성자 CR 전체경로가 이 표 획득만으로 완료되었다고 표시하지 않는다.
