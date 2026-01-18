# Phase 1B: 프론트엔드 코어

## ✅ 선행조건 체크리스트

### 필수 사전 준비사항
- [ ] Phase 0 완료 확인
  - [ ] 프로젝트 구조 생성 완료
  - [ ] API 스펙 정의 완료
  - [ ] 공통 설정 파일 생성 완료
- [ ] 개발 환경 확인
  - [ ] Node.js 18+ 설치 확인
  - [ ] npm 또는 yarn 설치 확인

### 의존성 확인
- [ ] **의존성**: Phase 0 완료 필수
- [ ] **병렬 가능**: Phase 1A와 병렬 개발 가능
- [ ] **주의**: 실제 API 호출은 Mock 데이터 사용 (Phase 1A 완료 전)

### 이전 Phase 완료 확인
- [ ] Phase 0 완료 확인
  - [ ] `frontend/` 폴더 존재
  - [ ] `docs/api-spec.yaml` 존재 (API 스펙 참조용)
  - [ ] `.env.example` 확인 완료

### Phase 1A 상태 확인 (선택사항)
- [ ] Phase 1A API 스펙 공유 확인 (완료되면 실제 API 사용 가능)
- [ ] Mock 데이터 준비 (Phase 1A 완료 전)

---

## Phase 개요

**목적**: 기본 UI 구조 및 상태 관리 구축

**예상 소요 시간**: 3-5일

**완료 기준**: 
- Next.js 프로젝트 설정 완료
- UI 컴포넌트 라이브러리 설정 완료
- 상태 관리 설정 완료
- 기본 페이지 구조 구현 완료
- 모든 테스트 통과

---

## 작업 내용

### 1. Next.js 프로젝트 설정

#### 1.1 Next.js 14+ 프로젝트 초기화
**명령어**:
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
```

**설정 파일**:
- `package.json` - 프로젝트 의존성
- `tsconfig.json` - TypeScript 설정
- `next.config.js` - Next.js 설정
- `tailwind.config.ts` - Tailwind CSS 설정

#### 1.2 Tailwind CSS 설정
**확인 사항**:
- Tailwind CSS 설치 확인
- PostCSS 설정 확인
- 기본 스타일 파일 생성

#### 1.3 기본 라우팅 구조
**폴더 구조**:
```
frontend/
├── app/
│   ├── layout.tsx          # 루트 레이아웃
│   ├── page.tsx            # 홈 페이지
│   ├── login/
│   │   └── page.tsx        # 로그인 페이지
│   ├── dashboard/
│   │   └── page.tsx        # 대시보드 페이지
│   └── api/                # API 라우트 (필요시)
```

### 2. UI 컴포넌트 라이브러리

#### 2.1 shadcn/ui 설치 및 설정
**설정 단계**:
1. shadcn/ui 초기화
2. 기본 컴포넌트 설치:
   - Button
   - Input
   - Card
   - Table
   - Dialog
   - Toast

**설정 파일**: `components.json`

#### 2.2 기본 컴포넌트 생성
**컴포넌트 위치**: `frontend/components/ui/`

**필수 컴포넌트**:
- `Button` - 버튼 컴포넌트
- `Input` - 입력 필드
- `Card` - 카드 컨테이너
- `Table` - 테이블
- `Dialog` - 모달 다이얼로그
- `Toast` - 알림 토스트

#### 2.3 레이아웃 컴포넌트
**컴포넌트 위치**: `frontend/components/layout/`

**컴포넌트**:
- `Header` - 헤더 네비게이션
- `Sidebar` - 사이드바 (필요시)
- `Footer` - 푸터 (필요시)
- `MainLayout` - 메인 레이아웃 래퍼

### 3. 상태 관리 설정

#### 3.1 Zustand 또는 React Query 설정
**선택**: Zustand (간단한 상태 관리) 또는 React Query (서버 상태 관리)

**Zustand 설정**:
- `frontend/lib/store/auth.ts` - 인증 상태
- `frontend/lib/store/trading.ts` - 트레이딩 상태

**React Query 설정** (선택):
- `frontend/lib/react-query.ts` - React Query 클라이언트 설정

#### 3.2 API 클라이언트 설정
**파일**: `frontend/lib/api/client.ts`

**기능**:
- axios 또는 fetch 래퍼
- 인증 토큰 자동 추가
- 에러 핸들링
- 인터셉터 설정

**Mock 데이터 설정** (Phase 1A 완료 전):
- `frontend/lib/api/mock.ts` - Mock 데이터 제공

#### 3.3 환경 변수 설정
**파일**: `frontend/.env.local`

**환경 변수**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. 기본 페이지 구조

#### 4.1 로그인 페이지
**파일**: `frontend/app/login/page.tsx`

**기능** (UI만, 실제 인증은 Phase 2):
- 로그인 폼 UI
- 입력 필드 (앱키, 앱시크릿)
- 로그인 버튼
- 에러 메시지 표시 영역

#### 4.2 대시보드 레이아웃
**파일**: `frontend/app/dashboard/page.tsx`

**구성 요소**:
- 헤더 (네비게이션)
- 메인 콘텐츠 영역
- 사이드바 (필요시)
- 포트폴리오 요약 카드 (Mock 데이터)
- 최근 거래 내역 테이블 (Mock 데이터)

#### 4.3 네비게이션 메뉴
**컴포넌트**: `frontend/components/layout/Navigation.tsx`

**메뉴 항목**:
- 대시보드
- 자동매매 설정 (Phase 2)
- 백테스팅 (Phase 4)
- 설정

---

## 테스트 항목

### 프로젝트 설정 테스트
- [ ] Next.js 프로젝트 실행 확인 (`npm run dev`)
- [ ] Tailwind CSS 스타일 적용 확인
- [ ] TypeScript 컴파일 확인

### UI 컴포넌트 테스트
- [ ] shadcn/ui 컴포넌트 렌더링 확인
- [ ] 기본 컴포넌트 동작 확인
- [ ] 레이아웃 컴포넌트 확인

### 상태 관리 테스트
- [ ] Zustand/React Query 설정 확인
- [ ] 상태 저장/조회 테스트
- [ ] API 클라이언트 설정 확인

### 페이지 구조 테스트
- [ ] 로그인 페이지 접근 확인
- [ ] 대시보드 페이지 접근 확인
- [ ] 라우팅 동작 확인
- [ ] Mock 데이터 표시 확인

---

## Mock 데이터 준비

Phase 1A 완료 전까지 사용할 Mock 데이터:

**파일**: `frontend/lib/api/mock.ts`

**Mock 데이터 예시**:
```typescript
export const mockPriceData = {
  stockCode: "005930",
  stockName: "삼성전자",
  currentPrice: 75000,
  // ...
};

export const mockAccountData = {
  balance: 10000000,
  positions: [
    // ...
  ],
};
```

---

## 완료 후 다음 단계

이 Phase 완료 후 다음 Phase로 진행:
- **Phase 2B**: 프론트엔드 기능 구현 시작 가능
- **Phase 1A**: 백엔드 코어와 병렬 개발 중 (완료되면 실제 API 연동)

**다음 Phase 시작 전 확인사항**:
- [ ] Phase 1A 완료 시 실제 API 연동 준비
- [ ] Mock 데이터에서 실제 API로 전환 계획 수립
- [ ] API 스펙과 UI 컴포넌트 매핑 확인

---

## 참고 문서
- `PHASE_0_INFRASTRUCTURE.md` - Phase 0 문서
- `PHASE_1A_BACKEND_CORE.md` - Phase 1A 문서 (API 스펙 참조)
- `prd.md` - 제품 요구사항 문서
- [Next.js 공식 문서](https://nextjs.org/docs)
- [shadcn/ui 문서](https://ui.shadcn.com)

---

## 변경 이력
- 2026-01-18: 초안 작성
