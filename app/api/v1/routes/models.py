"""
모델 관리 라우터
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.services.model_checker import ModelChecker

router = APIRouter()


@router.get(
    "/available",
    summary="사용 가능한 모델 목록",
    description="ComfyUI에 설치된 체크포인트 모델 목록을 조회합니다"
)
def get_available_models() -> Dict[str, Any]:
    """
    사용 가능한 모델 목록 조회
    
    Returns:
        모델 목록 및 정보
    """
    try:
        checker = ModelChecker()
        models = checker.get_available_models()
        
        model_info = []
        for model_name in models:
            info = checker.get_model_info(model_name)
            if info:
                model_info.append(info)
        
        return {
            "success": True,
            "models": model_info,
            "count": len(model_info)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 목록 조회 실패: {str(e)}"
        )


@router.get(
    "/check/{model_name:path}",
    summary="모델 파일 검증",
    description="특정 모델 파일의 존재 여부 및 유효성을 검증합니다"
)
def check_model(model_name: str) -> Dict[str, Any]:
    """
    모델 파일 검증
    
    Args:
        model_name: 모델 파일명
        
    Returns:
        검증 결과
    """
    try:
        checker = ModelChecker()
        result = checker.validate_model_file(model_name)
        
        return {
            "success": True,
            "model": model_name,
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 검증 실패: {str(e)}"
        )

