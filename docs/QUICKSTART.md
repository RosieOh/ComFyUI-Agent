# 빠른 시작 가이드 (macOS)

## 1단계: 의존성 설치

```bash
# 프로젝트 루트 디렉토리에서 실행
cd /Users/sirious920/Desktop/DevOps_RosieOh/Project/agent

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip3 install -r requirements.txt
```

## 2단계: 환경 변수 설정 (선택사항)

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 ComfyUI와 WebUI 경로 설정
# COMFYUI_PATH=/path/to/ComfyUI
# WEBUI_PATH=/path/to/stable-diffusion-webui
```

## 3단계: 서버 실행

**방법 1: 실행 스크립트 사용 (권장)**
```bash
./run.sh
```

**방법 2: 직접 실행**
```bash
# 프로젝트 루트에서 실행 (중요!)
python3 -m app.main
```

**방법 3: uvicorn 직접 실행**
```bash
# 프로젝트 루트에서 실행 (중요!)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## ⚠️ 중요 사항

1. **반드시 프로젝트 루트 디렉토리에서 실행하세요**
   ```bash
   # ✅ 올바른 위치
   cd /Users/sirious920/Desktop/DevOps_RosieOh/Project/agent
   python3 -m app.main
   
   # ❌ 잘못된 위치 (app 디렉토리 안에서 실행)
   cd app
   python3 -m app.main  # 이렇게 하면 안 됩니다!
   ```

2. **가상환경 활성화 확인**
   ```bash
   # 가상환경이 활성화되면 프롬프트에 (venv)가 표시됩니다
   (venv) sirious920@MacBook-Air agent %
   ```

3. **의존성 확인**
   ```bash
   python3 -c "import fastapi; print('✅ FastAPI 설치됨')"
   ```

## 접속 정보

서버가 시작되면:
- **API 문서**: http://localhost:8000/docs
- **API 엔드포인트**: http://localhost:8000/api/v1/

## 문제 해결

### ModuleNotFoundError: No module named 'fastapi'
```bash
# 가상환경 활성화 후 의존성 재설치
source venv/bin/activate
pip3 install -r requirements.txt
```

### ModuleNotFoundError: No module named 'app'
```bash
# 프로젝트 루트 디렉토리로 이동
cd /Users/sirious920/Desktop/DevOps_RosieOh/Project/agent
python3 -m app.main
```

### 포트가 이미 사용 중
```bash
# 포트 사용 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

