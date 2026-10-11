# 부정 결과와 주장 상한

- 실제 PR33: launcher exit1, 103.79789273899951 s. fullBED G 생성자 1회 반환 후 exact-grid 검사가 실패했으며 pulse는 시작하지 않았다. wrapper의 수집 성공 exit0을 수치 성공으로 해석하지 않는다.
- 저장 E와 재생성 E는 340/9600 nodes에서 다르다. 최대1 ULP, 최대절대차 1.1368683772161603e-13 eV. 이 작은 수치 자체는 물리적 허용/불허 판정을 제공하지 않는다.
- 전체 G는 저장되어 있지 않다. PHYS02E에서 옛 G와 새 G의 전체 원소 동등성을 주장하지 않는다.
- 사후 E 치환은 에너지 검사만으로 검출되지 않는 수 장부 결함을 만들 수 있다. 문서의 2상태 exact toy는 실제 G의 오차값/상계가 아니다.
- endpoint R,S만으로 uncapped mean을 식별하지 못한다는 PHYS02D 한계는 유지한다. 이번 루프는 새 pulse/CDF 또는 uncapped moment 값을 생성하지 않았다.
- 준비 환경 Py3.12.14/NumPy2.3.5와 NCP 계약 Py3.12.3/NumPy2.4.2는 다르다. 실제 NCP runtime preflight는 별도 필수 gate다.
