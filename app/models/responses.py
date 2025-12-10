"""
응답 모델
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    """서비스 정보"""
    running: bool = Field(..., description="서비스 실행 여부")
    port: int = Field(..., description="서비스 포트")
    url: str = Field(..., description="서비스 URL")


class ServiceStatusResponse(BaseModel):
    """서비스 상태 응답"""
    services: Dict[str, ServiceInfo] = Field(..., description="서비스 상태 정보")
    health_check: bool = Field(..., description="헬스체크 실행 여부")


class ImageGenerationResponse(BaseModel):
    """이미지 생성 응답"""
    success: bool = Field(..., description="성공 여부")
    images: List[str] = Field(..., description="생성된 이미지 경로 목록")
    message: str = Field(..., description="응답 메시지")


class ServiceControlResponse(BaseModel):
    """서비스 제어 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str = Field(..., description="서비스 상태")
    services: Optional[Dict[str, ServiceInfo]] = Field(None, description="서비스 상태 정보")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "HyperWise Llama Agent running",
                "services": {
                    "comfyui": {
                        "running": True,
                        "port": 8188,
                        "url": "http://127.0.0.1:8188"
                    },
                    "webui": {
                        "running": True,
                        "port": 7860,
                        "url": "http://127.0.0.1:7860"
                    }
                }
            }
        }

