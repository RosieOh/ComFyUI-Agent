"""
서비스 제어 라우터
"""
from fastapi import APIRouter, HTTPException, status
from app.models.responses import ServiceStatusResponse, ServiceControlResponse
from app.services.service_control import ServiceControlService
from app.dependencies.service_manager import ServiceManagerDep

router = APIRouter()


@router.get(
    "/status",
    response_model=ServiceStatusResponse,
    summary="서비스 상태 조회",
    description="모든 서비스의 상태를 조회합니다"
)
def get_service_status(
    service_manager: ServiceManagerDep
) -> ServiceStatusResponse:
    """
    서비스 상태 조회
    
    Args:
        service_manager: 서비스 매니저 의존성
        
    Returns:
        서비스 상태 정보
    """
    service = ServiceControlService(service_manager)
    status_info = service.get_status()
    
    return ServiceStatusResponse(**status_info)


@router.post(
    "/comfyui/start",
    response_model=ServiceControlResponse,
    summary="ComfyUI 시작",
    description="ComfyUI 서비스를 시작합니다"
)
def start_comfyui(
    service_manager: ServiceManagerDep
) -> ServiceControlResponse:
    """
    ComfyUI 서비스 시작
    
    Args:
        service_manager: 서비스 매니저 의존성
        
    Returns:
        서비스 제어 결과
        
    Raises:
        HTTPException: 시작 실패 시
    """
    service = ServiceControlService(service_manager)
    success = service.start_comfyui()
    
    if success:
        return ServiceControlResponse(
            success=True,
            message="ComfyUI가 시작되었습니다"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ComfyUI 시작 실패"
        )


@router.post(
    "/comfyui/stop",
    response_model=ServiceControlResponse,
    summary="ComfyUI 중지",
    description="ComfyUI 서비스를 중지합니다"
)
def stop_comfyui(
    service_manager: ServiceManagerDep
) -> ServiceControlResponse:
    """
    ComfyUI 서비스 중지
    
    Args:
        service_manager: 서비스 매니저 의존성
        
    Returns:
        서비스 제어 결과
    """
    service = ServiceControlService(service_manager)
    service.stop_comfyui()
    
    return ServiceControlResponse(
        success=True,
        message="ComfyUI가 중지되었습니다"
    )


@router.post(
    "/webui/start",
    response_model=ServiceControlResponse,
    summary="WebUI 시작",
    description="Stable Diffusion WebUI 서비스를 시작합니다"
)
def start_webui(
    service_manager: ServiceManagerDep
) -> ServiceControlResponse:
    """
    WebUI 서비스 시작
    
    Args:
        service_manager: 서비스 매니저 의존성
        
    Returns:
        서비스 제어 결과
        
    Raises:
        HTTPException: 시작 실패 시
    """
    service = ServiceControlService(service_manager)
    success = service.start_webui()
    
    if success:
        return ServiceControlResponse(
            success=True,
            message="WebUI가 시작되었습니다"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebUI 시작 실패"
        )


@router.post(
    "/webui/stop",
    response_model=ServiceControlResponse,
    summary="WebUI 중지",
    description="Stable Diffusion WebUI 서비스를 중지합니다"
)
def stop_webui(
    service_manager: ServiceManagerDep
) -> ServiceControlResponse:
    """
    WebUI 서비스 중지
    
    Args:
        service_manager: 서비스 매니저 의존성
        
    Returns:
        서비스 제어 결과
    """
    service = ServiceControlService(service_manager)
    service.stop_webui()
    
    return ServiceControlResponse(
        success=True,
        message="WebUI가 중지되었습니다"
    )

