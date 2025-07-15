# Agentica
Agentica 및 Fast Api

## 환경 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. 애플리케이션 실행
```bash
uvicorn app.main:app --reload
```

## API 엔드포인트

- `POST /register_project/`: 프로젝트 컨텍스트 등록
- `POST /generate_email/`: 이메일 생성
