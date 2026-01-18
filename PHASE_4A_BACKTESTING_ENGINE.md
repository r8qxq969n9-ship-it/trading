# Phase 4A: 백테스팅 엔진

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 2A 완료 확인
  - [ ] 전략 모듈 구현 완료
  - [ ] 주문 관리 모듈 구현 완료
  - [ ] 데이터베이스 설정 완료
- [ ] 과거 시세 데이터 준비
  - [ ] 시세 데이터 수집 방법 확인
  - [ ] 데이터 저장 형식 확인

### 의존성 확인
- [ ] **의존성**: Phase 2A 완료 필수
- [ ] **병렬 가능**: Phase 4B와 병렬 개발 가능

### 이전 Phase 완료 확인
- [ ] Phase 2A 완료 확인
  - [ ] 전략 모듈 정상 작동 확인
  - [ ] 주문 실행 로직 확인
  - [ ] 데이터베이스 연결 확인

---

## Phase 개요

**목적**: 전략 백테스팅 기능 구현

**예상 소요 시간**: 5-7일

**완료 기준**: 
- 백테스팅 엔진 구현 완료
- 과거 데이터 로드 기능 완료
- 전략 시뮬레이션 완료
- 성과 지표 계산 완료
- 백테스팅 API 구현 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. 백테스팅 엔진

#### 1.1 과거 데이터 로드
**파일**: `backend/app/backtesting/data_loader.py`

**기능**:
- 데이터베이스에서 과거 시세 데이터 로드
- CSV 파일에서 데이터 로드 (초기)
- 데이터 형식 변환
- 데이터 유효성 검증

**데이터 형식**:
```python
class PriceData:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
```

#### 1.2 전략 시뮬레이션
**파일**: `backend/app/backtesting/simulator.py`

**기능**:
- 전략 실행 시뮬레이션
- 시간 순서대로 데이터 처리
- 매수/매도 신호 생성
- 주문 실행 시뮬레이션
- 체결 시뮬레이션

**시뮬레이션 로직**:
1. 과거 데이터를 시간 순서대로 순회
2. 각 시점에서 전략 분석 실행
3. 매수/매도 신호 생성
4. 주문 실행 및 체결 시뮬레이션
5. 포지션 및 잔고 업데이트

#### 1.3 성과 지표 계산
**파일**: `backend/app/backtesting/metrics.py`

**성과 지표**:
- 총 수익률
- 연환산 수익률
- 승률 (Win Rate)
- 평균 수익/손실
- 최대 낙폭 (Maximum Drawdown)
- 샤프 비율 (Sharpe Ratio)
- 승리 거래 수 / 패배 거래 수
- 평균 보유 기간

**계산 예시**:
```python
class PerformanceMetrics:
    total_return: float
    annualized_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    # ...
```

### 2. 백테스팅 API

#### 2.1 백테스팅 실행 API
**파일**: `backend/app/api/backtest.py`

**엔드포인트**: `POST /api/backtest/run`

**요청 형식**:
```json
{
  "strategy_id": "ma_cross",
  "strategy_params": {
    "short_period": 5,
    "long_period": 20
  },
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "initial_capital": 10000000,
  "stock_codes": ["005930", "000660"]
}
```

**응답 형식**:
```json
{
  "backtest_id": "uuid",
  "status": "running",
  "progress": 0.5
}
```

#### 2.2 백테스팅 결과 조회 API
**엔드포인트**: `GET /api/backtest/results/{backtest_id}`

**응답 형식**:
```json
{
  "backtest_id": "uuid",
  "status": "completed",
  "metrics": {
    "total_return": 0.15,
    "annualized_return": 0.18,
    "win_rate": 0.65,
    "max_drawdown": 0.12,
    "sharpe_ratio": 1.5
  },
  "trades": [
    {
      "entry_date": "2025-01-15",
      "exit_date": "2025-01-20",
      "stock_code": "005930",
      "entry_price": 70000,
      "exit_price": 75000,
      "quantity": 100,
      "profit": 500000,
      "return": 0.071
    }
  ],
  "equity_curve": [
    {
      "date": "2025-01-01",
      "value": 10000000
    }
  ]
}
```

#### 2.3 백테스팅 히스토리 조회 API
**엔드포인트**: `GET /api/backtest/history`

**기능**:
- 이전 백테스팅 결과 목록 조회
- 필터링 (전략별, 기간별)
- 정렬 (날짜순, 수익률순)

---

## 테스트 항목

### 백테스팅 로직 테스트
- [ ] 과거 데이터 로드 확인
- [ ] 전략 시뮬레이션 실행 확인
- [ ] 매수/매도 신호 생성 확인
- [ ] 주문 실행 시뮬레이션 확인
- [ ] 포지션 관리 확인

### 성과 지표 계산 테스트
- [ ] 총 수익률 계산 확인
- [ ] 승률 계산 확인
- [ ] 최대 낙폭 계산 확인
- [ ] 샤프 비율 계산 확인
- [ ] 모든 지표 정확성 검증

### 백테스팅 API 테스트
- [ ] 백테스팅 실행 API 테스트
- [ ] 백테스팅 결과 조회 API 테스트
- [ ] 백테스팅 히스토리 조회 API 테스트
- [ ] 에러 핸들링 확인
- [ ] 대용량 데이터 처리 확인

### 성능 테스트
- [ ] 1년 데이터 백테스팅 시간 확인 (< 5분)
- [ ] 메모리 사용량 확인
- [ ] 동시 백테스팅 요청 처리 확인

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 5**: ML/AI 전략 개발 시작 가능 (향후 확장)
- **Phase 4B**: 백테스팅 UI 및 시각화와 병렬 개발 중 (이미 시작 가능)

**다음 Phase 시작 전 확인사항**:
- [ ] 백테스팅 API가 Phase 4B 팀에 공유됨
- [ ] 성과 지표가 정확하게 계산됨
- [ ] 백테스팅 결과가 저장됨

---

## 참고 문서
- `PHASE_2A_BACKEND_BUSINESS.md` - Phase 2A 문서
- `prd.md` - 제품 요구사항 문서
- 백테스팅 관련 자료 및 논문

---

## 변경 이력
- 2026-01-18: 초안 작성
