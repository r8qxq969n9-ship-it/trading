# 배포 가이드 (Deployment Guide)

## 1. 개요

이 문서는 주식 자동매매 웹 애플리케이션의 배포 방법을 설명합니다.

## 2. 배포 아키텍처

```
┌─────────────────────────────────────────┐
│     사용자 (웹 브라우저)                  │
│  - Chrome, Safari, Firefox 등           │
│  - 모바일 브라우저 지원                   │
└──────────────┬──────────────────────────┘
               │ HTTPS
               │
┌──────────────▼──────────────────────────┐
│     Vercel (프론트엔드)                   │
│  - Next.js 애플리케이션                   │
│  - URL: https://your-app.vercel.app     │
│  - 무료 플랜 활용                         │
└──────────────┬──────────────────────────┘
               │ API 호출
               │
┌──────────────▼──────────────────────────┐
│  Railway/Render (백엔드)                 │
│  - FastAPI 서버                          │
│  - URL: https://your-api.railway.app    │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐         ┌──────▼──────┐
│PostgreSQL│       │Slack Webhook│
│(Supabase)│       │             │
└──────────┘       └─────────────┘
```

## 3. 프론트엔드 배포 (Vercel)

### 3.1 사전 준비
1. GitHub 레포지토리에 코드가 푸시되어 있어야 함
   - 레포지토리: https://github.com/r8qxq969n9-ship-it/trading.git
2. Vercel 계정 생성 (GitHub 계정으로 로그인 가능)

### 3.2 배포 단계

#### Step 1: Vercel 프로젝트 생성
1. [Vercel](https://vercel.com) 접속
2. "Add New Project" 클릭
3. GitHub 레포지토리 선택
4. 프로젝트 설정:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (프론트엔드 폴더가 별도인 경우)
   - **Build Command**: `npm run build` (또는 `yarn build`)
   - **Output Directory**: `.next`

#### Step 2: 환경 변수 설정
Vercel 대시보드에서 환경 변수 추가:
```
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

#### Step 3: 배포
1. "Deploy" 버튼 클릭
2. 자동으로 빌드 및 배포 진행
3. 배포 완료 후 URL 확인 (예: `https://trading-app.vercel.app`)

### 3.3 자동 배포 설정
- GitHub에 푸시하면 자동으로 재배포됨
- `main` 브랜치에 푸시 시 프로덕션 배포
- 다른 브랜치는 프리뷰 배포

### 3.4 커스텀 도메인 (선택사항)
1. Vercel 대시보드 → Settings → Domains
2. 도메인 추가
3. DNS 설정 (Vercel 가이드 따름)

## 4. 백엔드 배포 (Railway)

### 4.1 사전 준비
1. GitHub 레포지토리에 코드가 푸시되어 있어야 함
   - 레포지토리: https://github.com/r8qxq969n9-ship-it/trading.git
2. Railway 계정 생성 (GitHub 계정으로 로그인 가능)

### 4.2 배포 단계

#### Step 1: Railway 프로젝트 생성
1. [Railway](https://railway.app) 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. 레포지토리 선택

#### Step 2: 서비스 설정
1. "New Service" → "Python" 선택
2. Root Directory: `backend`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Step 3: 환경 변수 설정
Railway 대시보드에서 환경 변수 추가:
```
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
SLACK_WEBHOOK_URL=your_slack_webhook_url
DATABASE_URL=your_database_url
```

#### Step 4: 데이터베이스 추가
1. "New" → "Database" → "PostgreSQL" 선택
2. 자동으로 생성되고 `DATABASE_URL` 환경 변수에 추가됨

#### Step 5: 배포
1. 자동으로 빌드 및 배포 진행
2. 배포 완료 후 URL 확인 (예: `https://trading-api.railway.app`)

### 4.3 대안: Render 배포
Render도 유사한 방식으로 배포 가능:
1. [Render](https://render.com) 접속
2. "New Web Service" 선택
3. GitHub 레포지토리 연결
4. 설정 및 배포

## 5. 데이터베이스 설정

### 5.1 Supabase (추천)
1. [Supabase](https://supabase.com) 계정 생성
2. "New Project" 생성
3. PostgreSQL 데이터베이스 자동 생성
4. Connection String 복사하여 `DATABASE_URL`에 설정

### 5.2 Railway PostgreSQL
- Railway에서 데이터베이스 서비스 추가 시 자동 생성
- `DATABASE_URL` 환경 변수에 자동 설정

## 6. Slack 웹훅 설정

### 6.1 웹훅 생성
1. Slack 워크스페이스 접속
2. [Slack Apps](https://api.slack.com/apps) 접속
3. "Create New App" → "From scratch"
4. App 이름 및 워크스페이스 선택
5. "Incoming Webhooks" 활성화
6. "Add New Webhook to Workspace"
7. 알림을 받을 채널 선택
8. Webhook URL 복사

### 6.2 환경 변수 설정
백엔드 환경 변수에 추가:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 7. 접속 방법

### 7.1 사용자 접속
1. Vercel에서 제공하는 URL로 접속
   - 예: `https://trading-app.vercel.app`
2. 웹 브라우저에서 열기
3. 모바일 브라우저에서도 동일 URL로 접속 가능
4. 북마크 추가로 앱처럼 사용 가능

### 7.2 모바일 접속
- iOS Safari, Android Chrome 등 모든 모바일 브라우저 지원
- 반응형 디자인으로 모바일 최적화

## 8. 배포 체크리스트

### 배포 전
- [ ] 모든 테스트 통과
- [ ] 환경 변수 확인
- [ ] 데이터베이스 연결 테스트
- [ ] API 엔드포인트 테스트
- [ ] Slack 웹훅 테스트

### 배포 후
- [ ] 프론트엔드 접속 확인
- [ ] 백엔드 API 응답 확인
- [ ] 데이터베이스 연결 확인
- [ ] 실시간 기능 (WebSocket) 확인
- [ ] Slack 알림 테스트

## 9. 문제 해결

### 9.1 배포 실패
- 빌드 로그 확인 (Vercel/Railway 대시보드)
- 환경 변수 누락 확인
- 의존성 설치 오류 확인

### 9.2 API 연결 실패
- CORS 설정 확인
- 백엔드 URL 확인
- 환경 변수 `NEXT_PUBLIC_API_URL` 확인

### 9.3 데이터베이스 연결 실패
- `DATABASE_URL` 형식 확인
- 데이터베이스 서비스 상태 확인
- 방화벽 설정 확인

## 10. 비용

### 무료 플랜
- **Vercel**: 
  - 무료 플랜: 월 100GB 대역폭, 무제한 배포
  - 개인 프로젝트에 충분
- **Railway**: 
  - 무료 플랜: 월 $5 크레딧
  - 소규모 프로젝트에 충분
- **Supabase**: 
  - 무료 플랜: 500MB 데이터베이스, 2GB 대역폭

### 예상 비용 (무료 플랜으로 시작 가능)
- 초기 개발 및 소규모 사용: **무료**
- 트래픽 증가 시: 월 $10-20 정도

## 11. 참고 자료

- [Vercel 문서](https://vercel.com/docs)
- [Railway 문서](https://docs.railway.app/)
- [Supabase 문서](https://supabase.com/docs)
- [Slack Webhook 가이드](https://api.slack.com/messaging/webhooks)
