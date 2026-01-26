# PRD: 국내주식 자동 트레이딩 프로그램

## 1. 목적
- 한국투자증권 Open Trading API를 활용해 국내주식 시세 조회, 주문, 포지션 관리까지 자동화하는 데스크톱/CLI 중심 툴을 만든다.
- 초기 버전은 모의투자 환경에서 신속히 검증하고, 동일한 코드 경로로 실전 전환을 지원한다.

## 2. 대상 사용자 & 문제
- 개인/법인 개발자: API 명세가 방대해 필요한 기능만 빠르게 연결하기 어렵다.
- 퀀트/트레이더: 시세 조회→신호 생성→주문 실행을 안정적으로 이어붙이는 표준 워크플로우가 필요하다.
- 운영 담당자: 토큰/웹소켓 키 관리, TR_ID 설정 등 환경 분리가 까다롭다.

## 3. 범위 (v0)
- 인증: REST 접근토큰 발급/폐기, 웹소켓 접속키 발급.
- 시세: 주식 현재가 단건 조회(FHKST01010100).
- 주문: 국내주식 현금주문(매수/매도) + 결과 수신(응답 기반).
- 계좌/체결: 주문번호 반환값으로 주문 상태 확인(추가 API는 후속).
- 환경 분리: 실전/모의 도메인 및 키를 설정 파일로 스위칭.

## 4. 주요 요구사항
1) 설정 관리
   - `kis_devlp.yaml` 형식 준용: 실전/모의 appkey/appsecret, 계좌 앞8자리+상품코드(뒤2자리), REST/WS 도메인 저장.
   - 사용자 User-Agent 입력 필드 포함.
2) 인증
   - REST 토큰 발급: `POST /oauth2/tokenP` (grant_type=client_credentials, appkey, appsecret).
   - REST 토큰 폐기: `POST /oauth2/revokeP`.
   - WS 접속키: `POST /oauth2/Approval` (approval_key 발급).
   - 토큰/키 만료 자동 갱신(유효기간 관리).
3) 시세 조회 (REST)
   - 엔드포인트: `/uapi/domestic-stock/v1/quotations/inquire-price`.
   - TR_ID: `FHKST01010100`; 쿼리 `FID_COND_MRKT_DIV_CODE`(J=KRX/NX/UN) + `FID_INPUT_ISCD`(종목코드).
   - 헤더: Bearer 토큰, appkey, appsecret, custtype(P/B), tr_id 등 명세 반영.
4) 주문 (REST)
   - 현금주문: `/uapi/domestic-stock/v1/trading/order-cash`.
   - TR_ID: 매도 `TTTC0011U`, 매수 `TTTC0012U`.
   - 바디 필수: `CANO`, `ACNT_PRDT_CD`, `PDNO`, `ORD_DVSN`(00 지정가, 01 시장가 등), `ORD_QTY`, `ORD_UNPR`; 선택 `SLL_TYPE`, `CNDT_PRIC`, `EXCG_ID_DVSN_CD`.
   - 응답 활용: `rt_cd`, `msg_cd`, `msg1`, `output.ODNO`(주문번호), `ORD_TMD`.
5) 모드 전환
   - 커맨드/환경변수 플래그로 실전 vs 모의 선택 시 베이스 URL, 키, 계좌 자동 교체.
6) 관측성
   - REST 요청/응답 로깅(민감정보 마스킹).
   - 토큰 발급/만료 시점 이벤트 로그.

## 5. 비기능 요구사항
- Python 3.9+; `requests` 기반 REST, `websockets` 또는 `websocket-client` 기반 WS.
- 재시도/백오프: 네트워크 오류 시 3회 재시도, 체결/주문 상태 조회 시 최소 쿨다운.
- 타임아웃: REST 기본 5s, WS 핑/퐁 주기 30s.
- 보안: 키/토큰은 파일 권한 600 권장, 로그에 노출 금지.

## 6. 플로우 (모의투자 기준)
1) 설정 로드 → 환경 선택(모의).
2) `tokenP` 호출로 접근토큰 획득 → 만료시간 기록.
3) 시세 조회(단건) → 신호 생성(후속 로직 자리).
4) 주문 요청(order-cash) → 주문번호 수신.
5) 주문번호 기반 상태 확인(후속 API 연동 예정) → 완료 후 토큰 폐기 선택.
6) 웹소켓 사용 시 `Approval`로 `approval_key` 획득 → 시세/체결 구독(후속).

## 7. 오픈 API 명세 출처 (로컬 CSV)
- `docs/API/접근토큰발급(P)-표 1.csv`, `접근토큰폐기(P)-표 1.csv`
- `docs/API/실시간 (웹소켓) 접속키 발급-표 1.csv`
- `docs/API/주식현재가 시세-표 1.csv`
- `docs/API/주식주문(현금)-표 1.csv`
- 전체 목록: `docs/API/API 목록-표 1.csv`

## 8. 성공 기준 (v0)
- 모의환경에서 토큰 발급→시세 조회→주문→주문번호 수신이 1분 내 완료.
- 키 만료 시 자동 갱신 후 동일 워크플로우 성공.
- 설정 전환만으로 실전 도메인 호출 가능(실거래는 별도 검증).

## 9. 후속 로드맵
- 주문/체결 조회 API 연동, 계좌잔고/포지션 관리.
- 웹소켓 기반 실시간 체결/호가 구독 및 전략 트리거.
- 백테스트/리스크 제한(일일 주문 금액, 허용 손실 한도).
