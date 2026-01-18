# Phase 4B: 백테스팅 UI 및 시각화

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 2B 완료 확인
  - [ ] API 연동 완료
  - [ ] 대시보드 구현 완료
  - [ ] 기본 UI 컴포넌트 구현 완료
- [ ] Phase 4A 완료 확인 (백테스팅 API 스펙 참조)
  - [ ] 백테스팅 엔진 구현 완료
  - [ ] 백테스팅 API 구현 완료
  - [ ] API 스펙 문서 확인

### 의존성 확인
- [ ] **의존성**: Phase 2B 완료 필수, Phase 4A API 스펙 참조 필요
- [ ] **병렬 가능**: Phase 4A와 병렬 개발 가능 (API 스펙 정의 후)

### 이전 Phase 완료 확인
- [ ] Phase 2B 완료 확인
  - [ ] 대시보드 정상 작동 확인
  - [ ] 차트 라이브러리 설정 확인
- [ ] Phase 4A 완료 확인
  - [ ] `/api/backtest/run` 엔드포인트 확인
  - [ ] `/api/backtest/results/{id}` 엔드포인트 확인
  - [ ] 백테스팅 결과 형식 확인

---

## Phase 개요

**목적**: 백테스팅 결과 시각화 및 성과 분석

**예상 소요 시간**: 4-6일

**완료 기준**: 
- 백테스팅 UI 구현 완료
- 백테스팅 결과 시각화 완료
- 성과 분석 그래프 구현 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. 백테스팅 UI

#### 1.1 백테스팅 설정 폼
**컴포넌트**: `frontend/components/backtest/BacktestConfig.tsx`

**설정 항목**:
- 전략 선택
- 전략 파라미터 설정
- 백테스팅 기간 설정 (시작일/종료일)
- 초기 자본금 설정
- 모니터링 종목 선택
- 백테스팅 실행 버튼

**폼 검증**:
- 날짜 유효성 검증
- 파라미터 범위 검증
- 필수 항목 확인

#### 1.2 결과 표시 페이지
**파일**: `frontend/app/backtest/results/[id]/page.tsx`

**구성 요소**:
- 백테스팅 상태 표시 (실행 중/완료/실패)
- 진행률 표시 (실행 중일 때)
- 성과 지표 요약 카드
- 상세 결과 섹션

#### 1.3 성과 지표 차트
**컴포넌트**: `frontend/components/backtest/PerformanceMetrics.tsx`

**표시 항목**:
- 총 수익률
- 연환산 수익률
- 승률
- 최대 낙폭
- 샤프 비율
- 거래 통계

**표시 형식**:
- 숫자 카드
- 게이지 차트
- 진행 바

### 2. 고급 시각화

#### 2.1 성과 분석 그래프
**컴포넌트**: `frontend/components/backtest/PerformanceChart.tsx`

**차트 유형**:
- 자산 추이 그래프 (Equity Curve)
- 일별 수익률 그래프
- 월별 수익률 그래프
- 누적 수익률 그래프

**라이브러리**: Recharts 또는 TradingView Lightweight Charts

#### 2.2 수익률 추이 차트
**컴포넌트**: `frontend/components/backtest/ReturnChart.tsx`

**기능**:
- 시간별 수익률 표시
- 벤치마크 비교 (코스피 지수 등)
- 색상 코딩 (수익/손실)
- 줌/팬 기능

#### 2.3 리스크 지표 시각화
**컴포넌트**: `frontend/components/backtest/RiskMetrics.tsx`

**표시 항목**:
- 최대 낙폭 그래프
- 변동성 지표
- 베타 값
- VaR (Value at Risk)

**시각화 형식**:
- 막대 그래프
- 영역 그래프
- 히트맵

#### 2.4 거래 내역 테이블
**컴포넌트**: `frontend/components/backtest/TradeTable.tsx`

**표시 정보**:
- 진입일/청산일
- 종목 코드
- 진입가/청산가
- 수량
- 수익/손실
- 수익률
- 보유 기간

**기능**:
- 정렬 (날짜, 수익률 등)
- 필터링 (수익/손실별)
- 상세 정보 모달
- CSV 내보내기

---

## 테스트 항목

### 백테스팅 UI 테스트
- [ ] 백테스팅 설정 폼 동작 확인
- [ ] 백테스팅 실행 확인
- [ ] 진행률 표시 확인
- [ ] 결과 표시 확인
- [ ] 에러 처리 확인

### 차트 렌더링 테스트
- [ ] 자산 추이 그래프 표시 확인
- [ ] 수익률 추이 차트 표시 확인
- [ ] 리스크 지표 시각화 확인
- [ ] 차트 인터랙션 확인 (줌/팬)
- [ ] 성능 확인

### 데이터 시각화 테스트
- [ ] 성과 지표 정확성 확인
- [ ] 거래 내역 테이블 표시 확인
- [ ] 데이터 필터링 확인
- [ ] 데이터 정렬 확인
- [ ] CSV 내보내기 확인

### 통합 테스트
- [ ] 전체 백테스팅 플로우 테스트
- [ ] 대용량 데이터 처리 확인
- [ ] 반응형 디자인 확인 (모바일)

---

## API 연동

Phase 4A에서 정의한 백테스팅 API 연동:

**API 엔드포인트**:
- `POST /api/backtest/run` - 백테스팅 실행
- `GET /api/backtest/results/{id}` - 결과 조회
- `GET /api/backtest/history` - 히스토리 조회

**파일**: `frontend/lib/api/backtest.ts`

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 5**: ML/AI 전략 개발 시작 가능 (향후 확장)

**다음 Phase 시작 전 확인사항**:
- [ ] 백테스팅 UI가 정상 작동함
- [ ] 시각화가 정확하고 직관적임
- [ ] 사용자 경험이 만족스러움

---

## 참고 문서
- `PHASE_2B_FRONTEND_FEATURES.md` - Phase 2B 문서
- `PHASE_4A_BACKTESTING_ENGINE.md` - Phase 4A 문서 (API 스펙 참조)
- `prd.md` - 제품 요구사항 문서
- [Recharts](https://recharts.org/)

---

## 변경 이력
- 2026-01-18: 초안 작성
