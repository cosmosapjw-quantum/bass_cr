# R17B2A 물리 루프: 임의 birth의 gas–photon response

## 범위와 결정
- bass_cr만 변경. R17B1 actual source plan와 R16B/BRIDGE13 FT03 방정식을 불변 donor로 선택한다.
- 이번 결과는 정확한 선형응답 유도 + nominal six-birth background의 경량 진단이다. homotopy 전체 인증/새 source 상계는 수행하지 않는다.
- 기존 photons의 opacity-induced survival memory와 직접 probe를 분리하고, 전체 전방 tangent와 후방 photon-adjoint를 비교한다.
- 자연단위를 도입하지 않음. w[ eV/H ]는 W0로 정규화, p[photons/H], u=t/T; 물리 출력을 다시 SI/cgs 계약에 맞춘다.

## 작업 단위
1. 실제 source/모형 상수/데이터 identity 고정. 기존 source 증명과 full suites 반복 없음.
2. 선형 gas–photon block에서 기존 photon response를 누락하는 assertion RED를 남긴 뒤 구현.
3. 새 nominal base를 한 번 적분하고 arbitrary birth 0, interior, known birth, endpoint에서 전방/후방 response; photon/heat memory 장부와 positive-dose 차분.
4. source birth에서 K,K',K''의 jump cancellation 직접 유도. 단순 HI 모형에서 K''' 비영 반례를 exact symbolic 검산. 이 모형으로 FT03 숫자를 대신하지 않음.
5. donor point/AD 경로, 새 단위시험, 별도 probe kernel 적분 검산. 완전한 interval certification으로 승격하지 않음.
6. 보고서/실행기/NCP 후속 계약/불변 ZIP. 새 bass_cr branch 게시와 기존 dual backup; 결과 없는 ACK 금지.
