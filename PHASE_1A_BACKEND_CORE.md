# Phase 1A: 백엔드 코어

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 0 완료 확인
  - [ ] 프로젝트 구조 생성 완료
  - [ ] API 스펙 정의 완료
  - [ ] 공통 설정 파일 생성 완료
- [ ] 한국투자증권 Open API 인증 정보 준비
  - [ ] 실전투자 앱키(App Key) 발급
  - [ ] 실전투자 앱시크릿(App Secret) 발급
  - [ ] 모의투자 앱키 발급 (선택)
  - [ ] 모의투자 앱시크릿 발급 (선택)
  - [ ] 계좌 번호 확인
- [ ] 개발 환경 확인
  - [ ] Python 3.9+ 설치 확인
  - [ ] pip 또는 uv 설치 확인

### 의존성 확인
- [ ] **의존성**: Phase 0 완료 필수
- [ ] **병렬 가능**: Phase 1B와 병렬 개발 가능

### 이전 Phase 완료 확인
- [ ] Phase 0 완료 확인
  - [ ] `backend/` 폴더 존재
  - [ ] `docs/api-spec.yaml` 존재
  - [ ] `.env.example` 업데이트 완료

---

## Phase 개요

**목적**: 한국투자증권 API 통합 및 기본 백엔드 인프라 구축

**예상 소요 시간**: 3-5일

**완료 기준**: 
- 인증 모듈 구현 및 테스트 완료
- API 클라이언트 구현 및 테스트 완료
- 데이터베이스 설정 완료
- 기본 API 엔드포인트 구현 및 테스트 완료
- OpenAPI 문서 자동 생성 확인

---

## 작업 내용

### 1. 인증 모듈

#### 1.1 한국투자증권 Open API 인증 구현
**파일**: `backend/app/auth/kis_auth.py`

**기능**:
- 앱키/앱시크릿 기반 인증
- 접근 토큰 발급
- 토큰 유효성 검증

**참고 자료**:
- `docs/API/` 폴더의 인증 관련 CSV 파일
- [한국투자증권 Open API 포털](https://apiportal.koreainvestment.com)
- [open-trading-api 레포지토리](https://github.com/koreainvestment/open-trading-api)

#### 1.2 토큰 관리 및 자동 갱신
**파일**: `backend/app/auth/token_manager.py`

**기능**:
- 토큰 저장 및 관리
- 토큰 만료 시간 체크
- 자동 갱신 로직
- 토큰 캐싱

#### 1.3 실전/모의투자 환경 전환
**파일**: `backend/app/config/settings.py`

**기능**:
- 환경 변수 기반 환경 전환
- 실전투자(prod) / 모의투자(vps) URL 관리
- 환경별 설정 관리

### 2. API 클라이언트

#### 2.1 REST API 클라이언트 구현
**파일**: `backend/app/kis/client.py`

**기능**:
- HTTP 클라이언트 래퍼
- 인증 헤더 자동 추가
- 에러 핸들링
- 재시도 로직

#### 2.2 현재가 조회 API
**파일**: `backend/app/kis/price.py`

**기능**:
- 종목 현재가 조회
- 호가창 조회
- 체결 내역 조회

**API 엔드포인트 참고**:
- `docs/API/` 폴더의 시세 관련 CSV 파일

#### 2.3 계좌 정보 조회 API
**파일**: `backend/app/kis/account.py`

**기능**:
- 계좌 잔고 조회
- 보유 종목 조회
- 평가손익 조회

### 3. 데이터베이스 설정

#### 3.1 데이터베이스 선택 및 설정
**초기 개발**: SQLite 사용
**프로덕션**: PostgreSQL (Supabase 또는 Railway)

**파일**: `backend/app/database/connection.py`

#### 3.2 기본 스키마 생성
**파일**: `backend/app/database/models.py`

**주요 테이블**:
- `users` - 사용자 정보 (향후 확장)
- `accounts` - 계좌 정보
- `price_history` - 시세 이력
- `orders` - 주문 내역
- `executions` - 체결 내역
- `trading_logs` - 트레이딩 로그

#### 3.3 데이터 모델 정의
**파일**: `backend/app/models/database.py`

**SQLAlchemy 모델 정의**

### 4. 기본 API 엔드포인트

#### 4.1 FastAPI 애플리케이션 설정
**파일**: `backend/app/main.py`

**설정 내용**:
- FastAPI 앱 초기화
- CORS 설정
- 라우터 등록
- OpenAPI 문서 설정

#### 4.2 인증 API 엔드포인트
**파일**: `backend/app/api/auth.py`

**엔드포인트**:
- `POST /api/auth/login` - 로그인 (인증 토큰 발급)
- `POST /api/auth/refresh` - 토큰 갱신
- `GET /api/auth/status` - 인증 상태 확인

#### 4.3 시세 조회 API 엔드포인트
**파일**: `backend/app/api/price.py`

**엔드포인트**:
- `GET /api/price/current/{stock_code}` - 현재가 조회
- `GET /api/price/quote/{stock_code}` - 호가창 조회
- `GET /api/price/execution/{stock_code}` - 체결 내역 조회

#### 4.4 계좌 정보 API 엔드포인트
**파일**: `backend/app/api/account.py`

**엔드포인트**:
- `GET /api/account/balance` - 계좌 잔고 조회
- `GET /api/account/positions` - 보유 종목 조회
- `GET /api/account/profit` - 평가손익 조회

#### 4.5 OpenAPI 문서 자동 생성
- FastAPI 자동 생성 기능 활용
- `http://localhost:8000/docs` 접속 확인
- `http://localhost:8000/redoc` 접속 확인

---

## 테스트 항목

### 인증 테스트
- [ ] 앱키/앱시크릿 기반 인증 성공
- [ ] 토큰 발급 확인
- [ ] 토큰 자동 갱신 확인
- [ ] 실전/모의투자 환경 전환 확인

### API 호출 테스트
- [ ] 현재가 조회 API 호출 성공
- [ ] 호가창 조회 API 호출 성공
- [ ] 계좌 정보 조회 API 호출 성공
- [ ] 에러 핸들링 확인

### 데이터베이스 연동 테스트
- [ ] 데이터베이스 연결 확인
- [ ] 스키마 생성 확인
- [ ] 데이터 저장/조회 테스트

### API 엔드포인트 테스트
- [ ] `/api/auth/login` 테스트
- [ ] `/api/price/current/{stock_code}` 테스트
- [ ] `/api/account/balance` 테스트
- [ ] OpenAPI 문서 접근 확인

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 2A**: 백엔드 비즈니스 로직 개발 시작 가능
- **Phase 1B**: 프론트엔드 코어와 병렬 개발 중 (이미 시작 가능)

**다음 Phase 시작 전 확인사항**:
- [ ] OpenAPI 문서가 Phase 1B 팀에 공유됨
- [ ] API 엔드포인트가 정상 작동함
- [ ] 인증 플로우가 완성됨

---

## 참고 문서
- `PHASE_0_INFRASTRUCTURE.md` - Phase 0 문서
- `prd.md` - 제품 요구사항 문서
- `docs/API/` - 한국투자증권 API 문서 (CSV 파일들)
- [한국투자증권 Open Trading API](https://github.com/koreainvestment/open-trading-api)

---

## 변경 이력
- 2026-01-18: 초안 작성
