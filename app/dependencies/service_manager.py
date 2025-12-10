"""
서비스 매니저 의존성
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from service_manager import ServiceManager, get_service_manager as _get_service_manager


def get_service_manager() -> ServiceManager:
    """
    서비스 매니저 인스턴스를 반환하는 의존성
    
    Returns:
        ServiceManager: 서비스 매니저 인스턴스
        
    Raises:
        HTTPException: 서비스 매니저가 초기화되지 않은 경우
    """
    manager = _get_service_manager()
    if manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="서비스 매니저가 초기화되지 않았습니다"
        )
    return manager


# 타입 별칭
ServiceManagerDep = Annotated[ServiceManager, Depends(get_service_manager)]

