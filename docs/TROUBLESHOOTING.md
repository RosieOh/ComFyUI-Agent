# 문제 해결 가이드

## BrokenPipeError: [Errno 32] Broken pipe

### 원인
ComfyUI가 subprocess로 실행될 때 stdout/stderr 파이프 버퍼가 가득 차거나, **부모 프로세스(Agent)가 종료되면서 파이프가 닫힐 때** 발생하는 오류입니다.

특히 다음과 같은 상황에서 자주 발생합니다:
1. **포트 충돌로 인해 Agent가 시작되자마자 종료될 때** (가장 흔한 원인)
2. tqdm (진행 표시줄)이 stderr에 출력할 때 파이프가 닫혀 있을 경우

**중요**: 이 오류는 **로깅 문제일 뿐**, 실제 이미지 생성은 정상적으로 완료될 수 있습니다. 로그에서 "Prompt executed in X seconds"가 보이면 작업은 성공한 것입니다.

### 해결 방법

**이미 해결됨**: 코드가 수정되어 stdout/stderr가 로그 파일로 리다이렉트됩니다.

- ComfyUI 로그: `logs/comfyui.log`
- WebUI 로그: `logs/webui.log`

### 로그 확인

```bash
# ComfyUI 로그 확인
tail -f logs/comfyui.log

# WebUI 로그 확인
tail -f logs/webui.log

# 최근 오류 확인
tail -50 logs/comfyui.log | grep -i error
```

### 참고사항

1. **이 오류는 무시해도 됩니다**: 로그가 파일로 저장되도록 수정되었으므로, BrokenPipeError는 로깅 문제일 뿐입니다.
2. **이미지 생성은 정상 작동**: 로그에서 "Prompt executed in X seconds"가 보이면 작업은 성공한 것입니다.
3. **tqdm 진행 표시줄**: 진행 표시줄이 표시되지 않을 수 있지만, 실제 작업은 계속 진행됩니다.

### 추가 해결 방법 (필요시)

만약 여전히 문제가 발생한다면:

1. **ComfyUI 재시작**:
   ```bash
   # 서비스 중지 후 재시작
   curl -X POST http://localhost:8000/api/v1/services/comfyui/stop
   curl -X POST http://localhost:8000/api/v1/services/comfyui/start
   ```

2. **로그 파일 확인**: `logs/comfyui.log`에서 실제 오류 메시지 확인

3. **ComfyUI 직접 실행 테스트**:
   ```bash
   cd ComfyUI
   python main.py --port 8188
   ```

## SafetensorError: Error while deserializing header: HeaderTooLarge

### 원인
이 오류는 ComfyUI가 모델 파일(.safetensors)을 로드할 때 발생합니다. 일반적인 원인:

1. **모델 파일이 손상됨**: 다운로드가 중단되거나 불완전함
2. **모델 파일이 너무 큼**: 메모리 부족
3. **모델 파일 경로 오류**: 잘못된 위치에 있음
4. **모델 파일 형식 오류**: 지원하지 않는 형식

### 해결 방법

#### 1. 사용 가능한 모델 확인

```bash
# API를 통해 확인
curl http://localhost:8000/api/v1/models/available

# 또는 Python으로 확인
python3.11 -c "from app.services.model_checker import ModelChecker; mc = ModelChecker(); print(mc.get_available_models())"
```

#### 2. 모델 파일 검증

```bash
# 특정 모델 검증
curl http://localhost:8000/api/v1/models/check/sdxl-base.safetensors
```

#### 3. 모델 파일 재다운로드

손상된 모델 파일을 삭제하고 다시 다운로드:

```bash
# ComfyUI 모델 디렉토리로 이동
cd $COMFYUI_PATH/models/checkpoints

# 손상된 모델 파일 확인 및 삭제
ls -lh *.safetensors
# 파일 크기가 비정상적으로 작거나 0이면 삭제
rm <손상된_모델_파일>

# 모델 재다운로드 (Hugging Face 등에서)
```

#### 4. 모델 파일 위치 확인

ComfyUI의 모델 파일은 다음 위치에 있어야 합니다:
- **체크포인트**: `ComfyUI/models/checkpoints/`
- **VAE**: `ComfyUI/models/vae/`
- **LoRA**: `ComfyUI/models/loras/`

#### 5. 메모리 확인

모델이 너무 크면 메모리 부족으로 오류가 발생할 수 있습니다:

```bash
# 메모리 사용량 확인
free -h  # Linux
vm_stat  # macOS
```

#### 6. 모델 자동 탐지

코드는 이제 자동으로 사용 가능한 모델을 탐지합니다:
- `sdxl-base.safetensors` 또는 유사한 이름의 모델을 자동으로 찾습니다
- 리파이너 모델이 없어도 기본 모델만으로 작동합니다

### 예방 방법

1. **모델 다운로드 완료 확인**: 다운로드가 100% 완료되었는지 확인
2. **파일 무결성 검증**: 다운로드 후 파일 크기 확인
3. **충분한 디스크 공간**: 모델 파일은 수 GB 크기일 수 있음
4. **안정적인 네트워크**: 다운로드 중 연결이 끊기지 않도록 주의

## ModuleNotFoundError: No module named 'fastapi'

### 해결
```bash
# 가상환경 활성화 후 의존성 재설치
source venv/bin/activate
pip3 install -r requirements.txt
```

## ModuleNotFoundError: No module named 'app'

### 해결
```bash
# 프로젝트 루트 디렉토리로 이동
cd /Users/sirious920/Desktop/DevOps_RosieOh/Project/agent
python3.11 -m app.main
```

## 포트 충돌

### 해결
```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :8188
lsof -i :7860

# 프로세스 종료
kill -9 <PID>
```

## JSON 파싱 오류

### 원인
- 서비스가 아직 시작되지 않음
- 빈 응답 반환
- HTML 응답 반환 (JSON이 아님)

### 해결
- 서비스가 완전히 시작될 때까지 대기
- ComfyUI/WebUI 로그 확인
- 서비스 상태 확인: `curl http://localhost:8000/api/v1/services/status`
