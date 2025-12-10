"""
애플리케이션 설정
"""
import os
from pathlib import Path
from typing import Optional

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# ============================================
# ComfyUI 설정
# ============================================
_comfyui_default = os.getenv("COMFYUI_PATH") or (
    str(PROJECT_ROOT / "ComfyUI") if (PROJECT_ROOT / "ComfyUI").exists() else None
)
COMFYUI_PATH = _comfyui_default
COMFYUI_PORT = int(os.getenv("COMFYUI_PORT", "8188"))
COMFYUI_URL = os.getenv("COMFYUI_URL", f"http://127.0.0.1:{COMFYUI_PORT}")

# ============================================
# Stable Diffusion WebUI 설정
# ============================================
_webui_default = os.getenv("WEBUI_PATH") or (
    str(PROJECT_ROOT / "stable-diffusion-webui") if (PROJECT_ROOT / "stable-diffusion-webui").exists() else None
)
WEBUI_PATH = _webui_default
WEBUI_PORT = int(os.getenv("WEBUI_PORT", "7860"))
WEBUI_URL = os.getenv("WEBUI_URL", f"http://127.0.0.1:{WEBUI_PORT}")

# ============================================
# 서비스 매니저 설정
# ============================================
AUTO_START_SERVICES = os.getenv("AUTO_START_SERVICES", "true").lower() == "true"
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "10"))

# ============================================
# API 서버 설정
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_TITLE = os.getenv("API_TITLE", "HyperWise Agent API")
API_DESCRIPTION = os.getenv(
    "API_DESCRIPTION",
    "ComfyUI와 Stable Diffusion WebUI를 통합 관리하는 에이전트 API"
)
API_VERSION = os.getenv("API_VERSION", "0.1.0")

# ============================================
# 이미지 생성 설정
# ============================================
DEFAULT_MODE = os.getenv("DEFAULT_MODE", "high_quality")  # fast, balanced, high_quality
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", str(PROJECT_ROOT / "downloads"))

# ============================================
# Ollama 설정
# ============================================
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")

# ============================================
# 로깅 설정
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 설정 검증
def validate_config(strict: bool = False):
    """
    설정 값 검증
    
    Args:
        strict: True이면 경로가 없으면 에러 발생, False이면 경고만 출력
    """
    errors = []
    warnings = []
    
    if COMFYUI_PATH:
        if not Path(COMFYUI_PATH).exists():
            msg = f"ComfyUI 경로를 찾을 수 없습니다: {COMFYUI_PATH}"
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)
    else:
        warnings.append("ComfyUI 경로가 설정되지 않았습니다. 환경 변수 COMFYUI_PATH를 설정하세요.")
    
    if WEBUI_PATH:
        if not Path(WEBUI_PATH).exists():
            msg = f"WebUI 경로를 찾을 수 없습니다: {WEBUI_PATH}"
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)
    else:
        warnings.append("WebUI 경로가 설정되지 않았습니다. 환경 변수 WEBUI_PATH를 설정하세요.")
    
    if COMFYUI_PORT == WEBUI_PORT:
        errors.append(f"ComfyUI와 WebUI 포트가 동일합니다: {COMFYUI_PORT}")
    
    if COMFYUI_PORT < 1024 or COMFYUI_PORT > 65535:
        errors.append(f"ComfyUI 포트가 유효하지 않습니다: {COMFYUI_PORT}")
    
    if WEBUI_PORT < 1024 or WEBUI_PORT > 65535:
        errors.append(f"WebUI 포트가 유효하지 않습니다: {WEBUI_PORT}")
    
    if DEFAULT_MODE not in ["fast", "balanced", "high_quality"]:
        errors.append(f"기본 모드가 유효하지 않습니다: {DEFAULT_MODE}")
    
    # 경고 출력
    if warnings:
        import logging
        logger = logging.getLogger(__name__)
        for warning in warnings:
            logger.warning(f"⚠️ {warning}")
    
    # 에러 발생
    if errors:
        raise ValueError("설정 오류:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

