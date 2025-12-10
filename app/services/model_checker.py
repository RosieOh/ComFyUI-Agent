"""
모델 파일 검증 및 확인 서비스
"""
import os
import requests
from pathlib import Path
from typing import List, Dict, Optional
from app.core.config import COMFYUI_URL, COMFYUI_PATH


class ModelChecker:
    """ComfyUI 모델 파일 검증"""
    
    def __init__(self):
        self.comfy_url = COMFYUI_URL
        self.comfy_path = Path(COMFYUI_PATH) if COMFYUI_PATH else None
    
    def get_available_models(self) -> List[str]:
        """
        사용 가능한 체크포인트 모델 목록 조회
        
        Returns:
            모델 파일명 목록
        """
        if not self.comfy_path:
            return []
        
        checkpoints_dir = self.comfy_path / "models" / "checkpoints"
        if not checkpoints_dir.exists():
            return []
        
        models = []
        for file in checkpoints_dir.glob("*.safetensors"):
            models.append(file.name)
        for file in checkpoints_dir.glob("*.ckpt"):
            models.append(file.name)
        
        return sorted(models)
    
    def check_model_exists(self, model_name: str) -> bool:
        """
        모델 파일 존재 여부 확인
        
        Args:
            model_name: 모델 파일명
            
        Returns:
            존재 여부
        """
        if not self.comfy_path:
            return False
        
        checkpoints_dir = self.comfy_path / "models" / "checkpoints"
        model_path = checkpoints_dir / model_name
        
        return model_path.exists() and model_path.is_file()
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """
        모델 파일 정보 조회
        
        Args:
            model_name: 모델 파일명
            
        Returns:
            모델 정보 (크기, 수정일 등)
        """
        if not self.comfy_path:
            return None
        
        checkpoints_dir = self.comfy_path / "models" / "checkpoints"
        model_path = checkpoints_dir / model_name
        
        if not model_path.exists():
            return None
        
        stat = model_path.stat()
        return {
            "name": model_name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": stat.st_mtime
        }
    
    def validate_model_file(self, model_name: str) -> Dict[str, any]:
        """
        모델 파일 검증
        
        Args:
            model_name: 모델 파일명
            
        Returns:
            검증 결과
        """
        result = {
            "exists": False,
            "valid": False,
            "error": None,
            "info": None
        }
        
        if not self.check_model_exists(model_name):
            result["error"] = f"모델 파일을 찾을 수 없습니다: {model_name}"
            return result
        
        result["exists"] = True
        result["info"] = self.get_model_info(model_name)
        
        # 파일 크기 검증 (최소 100MB 이상이어야 함)
        if result["info"] and result["info"]["size_mb"] < 100:
            result["error"] = f"모델 파일이 너무 작습니다: {result['info']['size_mb']}MB (최소 100MB 필요)"
            return result
        
        result["valid"] = True
        return result

