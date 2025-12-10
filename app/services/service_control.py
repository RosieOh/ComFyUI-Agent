"""
서비스 제어 서비스
"""
from typing import Dict, Any
from service_manager import ServiceManager


class ServiceControlService:
    """서비스 제어 서비스"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
    
    def get_status(self) -> Dict[str, Any]:
        """
        서비스 상태 조회
        
        Returns:
            서비스 상태 정보
        """
        return {
            "services": self.service_manager.get_status(),
            "health_check": self.service_manager.running
        }
    
    def start_comfyui(self) -> bool:
        """
        ComfyUI 서비스 시작
        
        Returns:
            성공 여부
        """
        return self.service_manager.start_comfyui()
    
    def stop_comfyui(self) -> None:
        """ComfyUI 서비스 중지"""
        self.service_manager.stop_comfyui()
    
    def start_webui(self) -> bool:
        """
        WebUI 서비스 시작
        
        Returns:
            성공 여부
        """
        return self.service_manager.start_webui()
    
    def stop_webui(self) -> None:
        """WebUI 서비스 중지"""
        self.service_manager.stop_webui()

