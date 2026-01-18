# Phase 3B: 프론트엔드 실시간 UI

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 2B 완료 확인
  - [ ] API 연동 완료
  - [ ] 대시보드 구현 완료
  - [ ] 자동매매 설정 UI 구현 완료
  - [ ] 주문 관리 UI 구현 완료
- [ ] Phase 3A 완료 확인 (WebSocket 스펙 참조)
  - [ ] WebSocket 서버 구현 완료
  - [ ] WebSocket 스펙 문서 확인
  - [ ] 실시간 데이터 전송 확인

### 의존성 확인
- [ ] **의존성**: Phase 2B 완료 필수, Phase 3A WebSocket 스펙 참조 필요
- [ ] **병렬 가능**: Phase 3A와 부분 병렬 (WebSocket 스펙 정의 후)

### 이전 Phase 완료 확인
- [ ] Phase 2B 완료 확인
  - [ ] 대시보드 정상 작동 확인
  - [ ] 주문 관리 UI 정상 작동 확인
- [ ] Phase 3A 완료 확인
  - [ ] WebSocket 엔드포인트 확인 (`/ws`)
  - [ ] WebSocket 스펙 문서 확인
  - [ ] 실시간 시세 스트리밍 확인

---

## Phase 개요

**목적**: 실시간 데이터 표시 및 차트 구현

**예상 소요 시간**: 4-6일

**완료 기준**: 
- WebSocket 클라이언트 구현 완료
- 실시간 차트 구현 완료
- 실시간 알림 UI 구현 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. WebSocket 클라이언트

#### 1.1 WebSocket 연결 관리
**파일**: `frontend/lib/websocket/client.ts`

**기능**:
- WebSocket 연결 생성
- 연결 상태 관리
- 연결 끊김 감지
- 자동 재연결 로직

**구현 예시**:
```typescript
class WebSocketClient {
  connect(url: string): void
  disconnect(): void
  subscribe(channel: string, stockCode: string): void
  unsubscribe(channel: string, stockCode: string): void
  onMessage(callback: (data: any) => void): void
}
```

#### 1.2 실시간 데이터 수신
**파일**: `frontend/lib/websocket/hooks.ts`

**React Hook**:
```typescript
function useRealtimePrice(stockCode: string) {
  // 실시간 가격 데이터 반환
}

function useRealtimeExecution() {
  // 실시간 체결 데이터 반환
}
```

#### 1.3 재연결 로직
**파일**: `frontend/lib/websocket/reconnect.ts`

**기능**:
- 연결 끊김 감지
- 자동 재연결 시도
- 재연결 지수 백오프
- 재연결 상태 표시

### 2. 실시간 차트

#### 2.1 차트 라이브러리 선택 및 설정
**옵션**:
- TradingView Lightweight Charts (권장)
- Recharts
- Chart.js

**설치**:
```bash
npm install lightweight-charts
# 또는
npm install recharts
```

#### 2.2 실시간 가격 업데이트
**컴포넌트**: `frontend/components/charts/RealtimePriceChart.tsx`

**기능**:
- 실시간 가격 표시
- 가격 변동 애니메이션
- 색상 코딩 (상승/하락)
- 타임스탬프 표시

#### 2.3 캔들스틱 차트
**컴포넌트**: `frontend/components/charts/CandlestickChart.tsx`

**기능**:
- 캔들스틱 차트 렌더링
- 실시간 데이터 업데이트
- 줌/팬 기능
- 시간축 표시

**데이터 형식**:
```typescript
interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
```

### 3. 실시간 알림 UI

#### 3.1 알림 토스트 컴포넌트
**컴포넌트**: `frontend/components/notifications/Toast.tsx`

**기능**:
- 알림 메시지 표시
- 알림 타입별 스타일 (긴급/일반/정보)
- 자동 사라짐 (일정 시간 후)
- 수동 닫기

**알림 타입**:
- 긴급: 빨간색, 긴 표시 시간
- 일반: 노란색, 중간 표시 시간
- 정보: 파란색, 짧은 표시 시간

#### 3.2 알림 히스토리
**컴포넌트**: `frontend/components/notifications/NotificationHistory.tsx`

**기능**:
- 알림 히스토리 목록 표시
- 알림 필터링 (타입별, 시간별)
- 알림 상세 정보 표시
- 알림 삭제

#### 3.3 알림 설정 UI
**컴포넌트**: `frontend/components/notifications/NotificationSettings.tsx`

**기능**:
- 알림 타입별 설정
- 알림 채널 선택
- 알림 소리 설정
- 알림 표시 시간 설정

---

## 테스트 항목

### WebSocket 클라이언트 테스트
- [ ] WebSocket 연결 확인
- [ ] 실시간 데이터 수신 확인
- [ ] 재연결 로직 확인
- [ ] 연결 끊김 처리 확인
- [ ] 다중 채널 구독 확인

### 차트 렌더링 테스트
- [ ] 실시간 가격 차트 표시 확인
- [ ] 캔들스틱 차트 표시 확인
- [ ] 실시간 데이터 업데이트 확인
- [ ] 차트 인터랙션 확인 (줌/팬)
- [ ] 성능 확인 (60fps 유지)

### 실시간 업데이트 테스트
- [ ] 가격 업데이트 지연 시간 확인 (< 1초)
- [ ] 차트 업데이트 부드러움 확인
- [ ] 다중 종목 동시 업데이트 확인
- [ ] 메모리 누수 확인

### 알림 UI 테스트
- [ ] 알림 토스트 표시 확인
- [ ] 알림 타입별 스타일 확인
- [ ] 알림 히스토리 표시 확인
- [ ] 알림 설정 저장 확인

### 통합 테스트
- [ ] 전체 실시간 플로우 테스트
- [ ] WebSocket 연결 끊김 시나리오 테스트
- [ ] 다중 브라우저 탭 테스트
- [ ] 모바일 반응형 테스트

---

## WebSocket 스펙 참조

Phase 3A에서 정의한 WebSocket 스펙을 참조:

**스펙 문서**: `docs/websocket-spec.md`

**주요 내용**:
- 연결 URL: `ws://localhost:8000/ws`
- 메시지 프로토콜
- 채널 목록
- 데이터 형식

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 4B**: 백테스팅 UI 및 시각화 개발 시작 가능
- **Phase 3A**: 백엔드 실시간 기능과 병렬 개발 중 (완료됨)

**다음 Phase 시작 전 확인사항**:
- [ ] 실시간 차트가 정상 작동함
- [ ] 실시간 알림이 정상 작동함
- [ ] 사용자 경험이 만족스러움

---

## 참고 문서
- `PHASE_2B_FRONTEND_FEATURES.md` - Phase 2B 문서
- `PHASE_3A_BACKEND_REALTIME.md` - Phase 3A 문서 (WebSocket 스펙 참조)
- `prd.md` - 제품 요구사항 문서
- [TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/)
- [Recharts](https://recharts.org/)

---

## 변경 이력
- 2026-01-18: 초안 작성
