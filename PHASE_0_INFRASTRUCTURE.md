# Phase 0: 공통 인프라 및 인터페이스 정의

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Git 레포지토리 초기화 완료
- [ ] 프로젝트 루트 폴더 생성 완료
- [ ] 개발 환경 설정 완료
  - [ ] Python 3.9+ 설치 확인
  - [ ] Node.js 18+ 설치 확인
  - [ ] Git 설치 확인
  - [ ] Cursor IDE 사용 가능

### 의존성 확인
- [ ] **의존성**: 없음 (최초 Phase)
- [ ] **병렬 가능**: 아니오 (모든 Phase의 기반)

### 이전 Phase 완료 확인
- [ ] 이전 Phase 없음 (최초 Phase)

---

## Phase 개요

**목적**: 프론트엔드와 백엔드가 독립적으로 개발할 수 있도록 인터페이스 정의

**예상 소요 시간**: 1-2일

**완료 기준**: 
- 프로젝트 구조 생성 완료
- API 스펙 문서 작성 완료
- 공통 설정 파일 생성 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. 프로젝트 기본 구조 생성

#### 1.1 폴더 구조 생성
```bash
trading/
├── frontend/             # Next.js 프론트엔드
├── backend/              # FastAPI 백엔드
├── docs/                 # 문서 (이미 존재)
│   └── API/              # API 문서 (이미 존재)
├── tests/                # 테스트 코드
└── README.md             # 프로젝트 설명
```

**작업 단계**:
1. `frontend/` 폴더 생성
2. `backend/` 폴더 생성
3. `tests/` 폴더 생성
4. 기본 README.md 작성

#### 1.2 기본 설정 파일 생성
- `backend/requirements.txt` (초기 버전)
- `frontend/package.json` (초기 버전)
- `.gitignore` 업데이트 (이미 존재, 확인 필요)

### 2. API 인터페이스 스펙 정의

#### 2.1 OpenAPI/Swagger 스펙 작성
**파일**: `docs/api-spec.yaml` 또는 `docs/api-spec.json`

**포함 내용**:
- 서버 정보 (개발/프로덕션)
- 인증 방식 (Bearer Token)
- API 엔드포인트 정의:
  - `/api/auth` - 인증 관련
  - `/api/price` - 시세 조회
  - `/api/account` - 계좌 정보
  - `/api/strategy` - 전략 관리 (Phase 2)
  - `/api/order` - 주문 관리 (Phase 2)
  - `/api/risk` - 리스크 관리 (Phase 2)
  - `/api/backtest` - 백테스팅 (Phase 4)
  - `/ws` - WebSocket 엔드포인트 (Phase 3)

#### 2.2 데이터 모델 정의
**파일**: `backend/app/models/schemas.py`

**주요 모델**:
- `AuthRequest` - 인증 요청
- `AuthResponse` - 인증 응답
- `PriceRequest` - 시세 조회 요청
- `PriceResponse` - 시세 조회 응답
- `AccountInfo` - 계좌 정보
- `OrderRequest` - 주문 요청
- `OrderResponse` - 주문 응답
- `StrategyConfig` - 전략 설정
- `RiskConfig` - 리스크 설정

#### 2.3 공통 타입 정의
**파일**: `backend/app/models/types.py`

**타입 정의**:
- `Environment` - 실전/모의투자 환경
- `OrderType` - 주문 유형 (시장가/지정가)
- `OrderSide` - 매수/매도
- `StrategyType` - 전략 유형
- `RiskLevel` - 리스크 레벨

### 3. 공통 설정 및 유틸리티

#### 3.1 환경 변수 템플릿
**파일**: `.env.example` (이미 존재, 업데이트 필요)

**필수 환경 변수**:
```env
# 한국투자증권 API
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_NO=your_account_no
KIS_ENV=prod  # 또는 vps (모의투자)

# 데이터베이스
DATABASE_URL=sqlite:///./trading.db  # 또는 PostgreSQL URL

# Slack 알림
SLACK_WEBHOOK_URL=your_slack_webhook_url

# 백엔드 서버
BACKEND_URL=http://localhost:8000

# 프론트엔드
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 3.2 로깅 설정
**파일**: `backend/app/config/logging.py`

**설정 내용**:
- 로그 레벨: DEBUG, INFO, WARNING, ERROR, CRITICAL
- 로그 포맷: JSON 또는 구조화된 텍스트
- 로그 출력: 콘솔 + 파일
- 로그 로테이션: 일별 로그 파일, 30일 보관

#### 3.3 에러 핸들링 표준
**파일**: `backend/app/utils/errors.py`

**에러 타입**:
- `APIError` - API 통신 오류
- `AuthError` - 인증 오류
- `ValidationError` - 데이터 검증 오류
- `TradingError` - 거래 관련 오류

**에러 응답 형식**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지",
    "details": {}
  }
}
```

---

## 테스트 항목

### 구조 검증
- [ ] 프로젝트 폴더 구조 확인
- [ ] 필수 파일 존재 확인
- [ ] Git 레포지토리 상태 확인

### API 스펙 검증
- [ ] OpenAPI 스펙 파일 유효성 검증
- [ ] 모든 엔드포인트 정의 확인
- [ ] 데이터 모델 정의 확인

### 설정 검증
- [ ] 환경 변수 템플릿 완성도 확인
- [ ] 로깅 설정 테스트
- [ ] 에러 핸들링 테스트

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 1A**: 백엔드 코어 개발 시작 가능
- **Phase 1B**: 프론트엔드 코어 개발 시작 가능 (병렬)

**다음 Phase 시작 전 확인사항**:
- [ ] API 스펙 문서가 Phase 1A, 1B 팀에 공유됨
- [ ] 데이터 모델이 정의되어 있음
- [ ] 환경 변수 템플릿이 완성됨

---

## 참고 문서
- `prd.md` - 제품 요구사항 문서
- `DEVELOPMENT.md` - 개발 프로세스 문서
- `docs/API/` - 한국투자증권 API 문서 (CSV 파일들)

---

## 변경 이력
- 2026-01-18: 초안 작성
