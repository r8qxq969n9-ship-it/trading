# Phase 2A: 백엔드 비즈니스 로직

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 1A 완료 확인
  - [ ] 인증 모듈 구현 완료
  - [ ] API 클라이언트 구현 완료
  - [ ] 데이터베이스 설정 완료
  - [ ] 기본 API 엔드포인트 구현 완료
- [ ] 한국투자증권 API 테스트 완료
  - [ ] 현재가 조회 테스트 성공
  - [ ] 계좌 정보 조회 테스트 성공

### 의존성 확인
- [ ] **의존성**: Phase 1A 완료 필수
- [ ] **병렬 가능**: Phase 2B와 병렬 개발 가능

### 이전 Phase 완료 확인
- [ ] Phase 1A 완료 확인
  - [ ] `/api/auth` 엔드포인트 작동 확인
  - [ ] `/api/price` 엔드포인트 작동 확인
  - [ ] `/api/account` 엔드포인트 작동 확인
  - [ ] 데이터베이스 연결 확인

---

## Phase 개요

**목적**: 자동매매 전략 및 주문 관리 구현

**예상 소요 시간**: 5-7일

**완료 기준**: 
- 전략 모듈 구현 및 테스트 완료
- 주문 관리 모듈 구현 및 테스트 완료
- 리스크 관리 모듈 구현 및 테스트 완료
- API 엔드포인트 확장 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. 전략 모듈

#### 1.1 전략 인터페이스 정의
**파일**: `backend/app/trading/strategy/base.py`

**인터페이스**:
```python
class Strategy(ABC):
    @abstractmethod
    def analyze(self, data: MarketData) -> Signal:
        """시장 데이터 분석 및 신호 생성"""
        pass
    
    @abstractmethod
    def should_buy(self, signal: Signal) -> bool:
        """매수 조건 확인"""
        pass
    
    @abstractmethod
    def should_sell(self, signal: Signal) -> bool:
        """매도 조건 확인"""
        pass
```

#### 1.2 이동평균선 교차 전략 구현
**파일**: `backend/app/trading/strategy/ma_cross.py`

**전략 로직**:
- 단기 이동평균선 (예: 5일)
- 장기 이동평균선 (예: 20일)
- 골든크로스 (단기 > 장기): 매수 신호
- 데드크로스 (단기 < 장기): 매도 신호

**파라미터**:
- 단기 이동평균 기간
- 장기 이동평균 기간
- 거래량 필터 (선택)

#### 1.3 RSI 전략 구현
**파일**: `backend/app/trading/strategy/rsi.py`

**전략 로직**:
- RSI 계산 (14일 기준)
- RSI < 30: 과매도 (매수 신호)
- RSI > 70: 과매수 (매도 신호)

**파라미터**:
- RSI 기간
- 과매수/과매도 기준선

#### 1.4 전략 레지스트리
**파일**: `backend/app/trading/strategy/registry.py`

**기능**:
- 전략 등록 및 관리
- 전략 팩토리 패턴
- 전략 설정 저장/로드

### 2. 주문 관리

#### 2.1 주문 실행 모듈
**파일**: `backend/app/trading/order/executor.py`

**기능**:
- 시장가 주문 실행
- 지정가 주문 실행
- 주문 요청 검증
- 주문 결과 저장

**참고 자료**:
- `docs/API/` 폴더의 주문 관련 CSV 파일
- 한국투자증권 Open API 주문 API 문서

#### 2.2 주문 취소/수정 기능
**파일**: `backend/app/trading/order/manager.py`

**기능**:
- 주문 취소
- 주문 수정 (가격/수량)
- 주문 상태 조회
- 주문 내역 관리

#### 2.3 주문 내역 저장
**데이터베이스 모델**: `backend/app/database/models.py`

**테이블**:
- `orders` - 주문 내역
- `executions` - 체결 내역

**저장 정보**:
- 주문 번호
- 종목 코드
- 주문 유형 (시장가/지정가)
- 주문 방향 (매수/매도)
- 가격, 수량
- 주문 상태
- 주문 시간

### 3. 리스크 관리

#### 3.1 손절매/익절매 로직
**파일**: `backend/app/trading/risk/stop_loss.py`

**기능**:
- 손절매 조건 확인 (손실률 도달 시)
- 익절매 조건 확인 (수익률 도달 시)
- 자동 청산 실행
- 리스크 알림

#### 3.2 포지션 크기 관리
**파일**: `backend/app/trading/risk/position.py`

**기능**:
- 계좌 자산 대비 포지션 크기 제한
- 종목별 포지션 크기 제한
- 포지션 크기 초과 시 경고/차단

#### 3.3 일일 손실 한도 체크
**파일**: `backend/app/trading/risk/daily_limit.py`

**기능**:
- 일일 손실 한도 설정
- 실시간 손실 모니터링
- 한도 도달 시 자동 거래 중단
- 알림 전송

### 4. API 엔드포인트 확장

#### 4.1 전략 관리 API
**파일**: `backend/app/api/strategy.py`

**엔드포인트**:
- `GET /api/strategy/list` - 전략 목록 조회
- `POST /api/strategy/create` - 전략 생성
- `PUT /api/strategy/{id}` - 전략 수정
- `DELETE /api/strategy/{id}` - 전략 삭제
- `POST /api/strategy/{id}/start` - 전략 시작
- `POST /api/strategy/{id}/stop` - 전략 중지

#### 4.2 주문 관리 API
**파일**: `backend/app/api/order.py`

**엔드포인트**:
- `POST /api/order` - 주문 실행
- `GET /api/order/list` - 주문 내역 조회
- `POST /api/order/{id}/cancel` - 주문 취소
- `PUT /api/order/{id}` - 주문 수정
- `GET /api/order/{id}` - 주문 상세 조회

#### 4.3 리스크 관리 API
**파일**: `backend/app/api/risk.py`

**엔드포인트**:
- `GET /api/risk/config` - 리스크 설정 조회
- `PUT /api/risk/config` - 리스크 설정 수정
- `GET /api/risk/status` - 리스크 상태 조회
- `GET /api/risk/daily-loss` - 일일 손실 현황

---

## 테스트 항목

### 전략 로직 테스트
- [ ] 이동평균선 교차 전략 로직 테스트
- [ ] RSI 전략 로직 테스트
- [ ] 전략 인터페이스 구현 확인
- [ ] 전략 레지스트리 동작 확인

### 주문 실행 테스트
- [ ] 시장가 주문 실행 테스트 (모의투자)
- [ ] 지정가 주문 실행 테스트 (모의투자)
- [ ] 주문 취소 테스트
- [ ] 주문 수정 테스트
- [ ] 주문 내역 저장 확인

### 리스크 관리 테스트
- [ ] 손절매 로직 테스트
- [ ] 익절매 로직 테스트
- [ ] 포지션 크기 관리 테스트
- [ ] 일일 손실 한도 체크 테스트
- [ ] 리스크 알림 테스트

### API 엔드포인트 테스트
- [ ] `/api/strategy/*` 엔드포인트 테스트
- [ ] `/api/order/*` 엔드포인트 테스트
- [ ] `/api/risk/*` 엔드포인트 테스트
- [ ] 에러 핸들링 확인

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 3A**: 백엔드 실시간 기능 개발 시작 가능
- **Phase 2B**: 프론트엔드 기능 구현과 병렬 개발 중 (이미 시작 가능)

**다음 Phase 시작 전 확인사항**:
- [ ] 전략 모듈이 정상 작동함
- [ ] 주문 실행이 정상 작동함 (모의투자 환경에서 테스트)
- [ ] 리스크 관리가 정상 작동함
- [ ] API 엔드포인트가 Phase 2B 팀에 공유됨

---

## 참고 문서
- `PHASE_1A_BACKEND_CORE.md` - Phase 1A 문서
- `prd.md` - 제품 요구사항 문서
- `docs/API/` - 한국투자증권 API 문서 (주문 관련 CSV 파일)
- [한국투자증권 Open Trading API](https://github.com/koreainvestment/open-trading-api)

---

## 변경 이력
- 2026-01-18: 초안 작성
