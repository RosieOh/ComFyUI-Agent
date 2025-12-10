"""
헬스체크 라우터
"""
from fastapi import APIRouter
from app.models.responses import HealthResponse
from app.dependencies.service_manager import ServiceManagerDep

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="헬스체크",
    description="서비스 상태를 확인합니다"
)
def health_check(
    service_manager: ServiceManagerDep
) -> HealthResponse:
    """
    헬스체크
    
    Args:
        service_manager: 서비스 매니저 의존성
        
    Returns:
        서비스 상태 정보
    """
    status_info = service_manager.get_status()
    
    return HealthResponse(
        status="HyperWise Llama Agent running",
        services=status_info
    )

