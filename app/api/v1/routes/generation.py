"""
이미지 생성 라우터
"""
from fastapi import APIRouter, HTTPException, status
from app.models.requests import PromptRequest
from app.models.responses import ImageGenerationResponse
from app.services.image_generation import ImageGenerationService
from app.dependencies.service_manager import ServiceManagerDep
from service_manager import ServiceManager

router = APIRouter()


@router.post(
    "",
    response_model=ImageGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="이미지 생성",
    description="프롬프트를 기반으로 이미지를 생성합니다"
)
def generate_image(
    request: PromptRequest,
    service_manager: ServiceManagerDep
) -> ImageGenerationResponse:
    """
    이미지 생성 요청
    
    Args:
        request: 이미지 생성 요청 데이터
        service_manager: 서비스 매니저 의존성
        
    Returns:
        생성된 이미지 정보
        
    Raises:
        HTTPException: ComfyUI가 실행 중이 아니거나 생성 실패 시
    """
    # ComfyUI 상태 확인
    status_info = service_manager.get_status()
    if not status_info["comfyui"]["running"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ComfyUI 서비스가 실행 중이지 않습니다. 잠시 후 다시 시도해주세요."
        )
    
    try:
        # 이미지 생성 서비스 호출
        service = ImageGenerationService()
        files = service.generate_product_image(request.prompt, mode=request.mode)
        
        return ImageGenerationResponse(
            success=True,
            images=files,
            message=f"{len(files)}개의 이미지가 생성되었습니다"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 생성 실패: {str(e)}"
        )

