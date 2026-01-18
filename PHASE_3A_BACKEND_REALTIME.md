# Phase 3A: 백엔드 실시간 기능

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 2A 완료 확인
  - [ ] 전략 모듈 구현 완료
  - [ ] 주문 관리 모듈 구현 완료
  - [ ] 리스크 관리 모듈 구현 완료
- [ ] Slack 웹훅 설정 완료
  - [ ] Slack 워크스페이스 접근
  - [ ] Incoming Webhook 앱 추가
  - [ ] Webhook URL 생성

### 의존성 확인
- [ ] **의존성**: Phase 2A 완료 필수
- [ ] **병렬 가능**: Phase 3B와 부분 병렬 (WebSocket 스펙 정의 후)

### 이전 Phase 완료 확인
- [ ] Phase 2A 완료 확인
  - [ ] `/api/strategy` 엔드포인트 작동 확인
  - [ ] `/api/order` 엔드포인트 작동 확인
  - [ ] `/api/risk` 엔드포인트 작동 확인

---

## Phase 개요

**목적**: WebSocket 및 실시간 알림 구현

**예상 소요 시간**: 4-6일

**완료 기준**: 
- WebSocket 서버 구현 완료
- 한국투자증권 WebSocket 클라이언트 구현 완료
- Slack 알림 시스템 구현 완료
- 실시간 API 엔드포인트 구현 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. WebSocket 서버

#### 1.1 FastAPI WebSocket 구현
**파일**: `backend/app/api/websocket.py`

**기능**:
- WebSocket 엔드포인트 (`/ws`)
- 클라이언트 연결 관리
- 메시지 브로드캐스트
- 연결 상태 관리
- 재연결 처리

**구현 예시**:
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 연결 관리
    # 메시지 수신/전송
```

#### 1.2 한국투자증권 WebSocket 클라이언트
**파일**: `backend/app/kis/websocket_client.py`

**기능**:
- 한국투자증권 WebSocket 연결
- 실시간 시세 수신
- 실시간 호가 수신
- 실시간 체결 알림 수신
- 연결 끊김 시 자동 재연결

**참고 자료**:
- `docs/API/` 폴더의 WebSocket 관련 CSV 파일
- 한국투자증권 Open API WebSocket 문서

#### 1.3 실시간 시세 수신 및 브로드캐스트
**파일**: `backend/app/services/realtime_broadcast.py`

**기능**:
- 한국투자증권 WebSocket에서 시세 수신
- 클라이언트 WebSocket으로 브로드캐스트
- 종목별 구독 관리
- 메시지 큐 관리

### 2. 알림 시스템

#### 2.1 Slack Webhook 연동
**파일**: `backend/app/notifications/slack.py`

**기능**:
- Slack Webhook URL 설정
- 메시지 전송 함수
- 메시지 포맷팅
- 에러 핸들링

**메시지 포맷**:
```python
{
    "text": "알림 제목",
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "알림 내용"
            }
        }
    ]
}
```

#### 2.2 알림 전송 모듈
**파일**: `backend/app/notifications/manager.py`

**기능**:
- 알림 타입별 전송
- 알림 중요도 관리
- 알림 로깅
- 알림 히스토리 저장

**알림 타입**:
- 긴급: 주문 체결, 손실 한도 도달, 시스템 오류
- 일반: 리스크 경고, 포지션 변경
- 정보: 일일 수익률 요약, 전략 실행 결과

#### 2.3 이벤트 기반 알림
**파일**: `backend/app/notifications/events.py`

**이벤트 리스너**:
- 주문 체결 이벤트
- 손실 한도 도달 이벤트
- 리스크 경고 이벤트
- 전략 실행 이벤트
- 시스템 오류 이벤트

### 3. 실시간 API

#### 3.1 WebSocket 엔드포인트
**엔드포인트**: `/ws`

**메시지 프로토콜**:
```json
// 클라이언트 → 서버
{
  "action": "subscribe",
  "channel": "price",
  "stock_code": "005930"
}

// 서버 → 클라이언트
{
  "channel": "price",
  "stock_code": "005930",
  "data": {
    "current_price": 75000,
    "timestamp": "2026-01-18T10:00:00Z"
  }
}
```

#### 3.2 실시간 시세 스트리밍
**채널**: `price`

**데이터 형식**:
- 현재가
- 시가, 고가, 저가, 종가
- 거래량
- 타임스탬프

#### 3.3 체결 알림
**채널**: `execution`

**데이터 형식**:
- 주문 번호
- 종목 코드
- 체결 가격
- 체결 수량
- 체결 시간

---

## 테스트 항목

### WebSocket 연결 테스트
- [ ] WebSocket 서버 연결 확인
- [ ] 클라이언트 연결/해제 확인
- [ ] 다중 클라이언트 연결 확인
- [ ] 재연결 로직 확인

### 실시간 데이터 전송 테스트
- [ ] 한국투자증권 WebSocket 연결 확인
- [ ] 실시간 시세 수신 확인
- [ ] 클라이언트로 브로드캐스트 확인
- [ ] 종목별 구독 확인
- [ ] 메시지 지연 시간 확인 (< 1초)

### Slack 알림 테스트
- [ ] Slack Webhook 연결 확인
- [ ] 긴급 알림 전송 확인
- [ ] 일반 알림 전송 확인
- [ ] 정보 알림 전송 확인
- [ ] 알림 포맷 확인
- [ ] 에러 핸들링 확인

### 통합 테스트
- [ ] 주문 체결 시 Slack 알림 확인
- [ ] 손실 한도 도달 시 Slack 알림 확인
- [ ] 실시간 시세 스트리밍 확인
- [ ] 전체 플로우 테스트

---

## WebSocket 스펙 문서화

Phase 3B 개발을 위해 WebSocket 스펙을 문서화:

**파일**: `docs/websocket-spec.md`

**포함 내용**:
- 연결 방법
- 메시지 프로토콜
- 채널 목록
- 데이터 형식
- 에러 처리

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 4A**: 백테스팅 엔진 개발 시작 가능
- **Phase 3B**: 프론트엔드 실시간 UI와 병렬 개발 중 (WebSocket 스펙 정의 후)

**다음 Phase 시작 전 확인사항**:
- [ ] WebSocket 스펙이 Phase 3B 팀에 공유됨
- [ ] Slack 알림이 정상 작동함
- [ ] 실시간 데이터 전송이 정상 작동함

---

## 참고 문서
- `PHASE_2A_BACKEND_BUSINESS.md` - Phase 2A 문서
- `prd.md` - 제품 요구사항 문서
- `docs/API/` - 한국투자증권 API 문서 (WebSocket 관련 CSV 파일)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

---

## 변경 이력
- 2026-01-18: 초안 작성
