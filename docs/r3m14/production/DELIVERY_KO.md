# R3M14 최종 전달

수치 실행·반환 및 새 archive 이중 백업을 완료했다. **과학 판정은 NO_GO**다.

- 준비 쌍 d=0.00044669380764377305 > d_star=0.00043930987793803502; 조건부 충분조건은 미충족이다.
- 실제 P_span(n≤3)=0.0077575635652400738, 지정 R3M12 분모 대비 변화는 0.009200678%다. 실제 충돌 비교는 1% 이내이지만 준비 쌍 NO_GO를 바꾸지 않는다.
- 52개 테스트 PASS, v2 실제 초기상태 바이트·norm·환경 binding PASS, 897 step / 8 chunk / 7 sealed restart 완료. MLflow 10 traces·10 spans readback을 확인했다.
- Archive: 1,465,397,891 bytes, SHA-256 `d31982250ae7e1e04ce45680632405d4b09bef189c27c4d04e01b67e4231ad1d`. 내부 119개 파일의 manifest를 검증했다.
- Dropbox: `id:BSpOijBcT10AAAAAADtR1A`. 원격 크기와 provider content hash를 로컬 계산과 대조했다. 전체 archive raw 재다운로드는 하지 않았다.
- Drive: 44/44 조각을 전부 raw readback하고 조각 SHA 및 순서 재조립 SHA를 대조했다. [복원 manifest](https://drive.google.com/file/d/1CwAgRqeWLnOHLyFCGZ-T3UoTsXbG9XYi/view?usp=drivesdk)에 모든 실제 ID·크기·SHA가 있다. 이 manifest 자체도 양쪽 provider에서 검증했다.

이중 백업 완료는 R3M14 production archive에만 해당한다. R3M12 Drive 1/19 문제는 이번 작업에서 해결하지 않았다. 최초 3번째 조각의 HTTP/2 readback 실패·부분 파일은 보존했고, 같은 원격 객체에 대한 한 번의 HTTP/1.1 재시도가 검증됐다. 초기 Git 기록의 BACKUP_PENDING은 당시 상태이며, 최종 상태는 DELIVERY_RECEIPT.json이다.

main merge·force push·기존 증거/소스 변경 없이 전용 branch를 사용했다. 큰 배열은 Git에서 제외했다. 상세 과학 보고서는 REPORT_KO.md, 최종 기계 판정은 FINAL_DECISION.json, 백업 증거는 DELIVERY_RECEIPT.json을 참조한다. inherited spatial NO_GO와 b-grid NO_GO를 유지한다. dx=.20은 실행하지 않았으며 R3M15로 자동 진입하지 않는다.
