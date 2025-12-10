"""
이미지 생성 서비스
"""
import os
import time
import base64
import requests
import ollama
from typing import List, Optional
from app.core.config import COMFYUI_URL, DOWNLOAD_DIR, OLLAMA_MODEL, OLLAMA_VISION_MODEL
from app.services.model_checker import ModelChecker


# MODE SETTINGS (Karras + Refiner + UpScale)
MODES = {
    "fast": {
        "width": 832,
        "height": 832,
        "steps": 28,
        "cfg": 6.5,
        "sampler": "dpmpp_sde_karras",
        "refiner_steps": 10,
        "upscale": False
    },
    "balanced": {
        "width": 1024,
        "height": 1024,
        "steps": 40,
        "cfg": 7.5,
        "sampler": "dpmpp_sde_karras",
        "refiner_steps": 15,
        "upscale": False
    },
    "high_quality": {
        "width": 1024,
        "height": 1024,
        "steps": 50,
        "cfg": 8.0,
        "sampler": "dpmpp_sde_karras",
        "refiner_steps": 20,
        "upscale": True
    }
}


class ImageGenerationService:
    """이미지 생성 서비스"""
    
    def __init__(self, base_model: Optional[str] = None, refiner_model: Optional[str] = None):
        """
        Args:
            base_model: 기본 모델 파일명 (None이면 기본값 사용)
            refiner_model: 리파이너 모델 파일명 (None이면 기본값 사용)
        """
        self.comfy_url = COMFYUI_URL
        self.download_dir = DOWNLOAD_DIR
        self.ollama_model = OLLAMA_MODEL
        self.ollama_vision_model = OLLAMA_VISION_MODEL
        
        # 모델 검증기 초기화
        self.model_checker = ModelChecker()
        
        # 모델 파일명 설정 (사용 가능한 모델 자동 탐지)
        if base_model:
            self.base_model = base_model
        else:
            # 기본 모델 자동 탐지
            available = self.model_checker.get_available_models()
            # sdxl-base, sdxl_base, sdxl-base-1.0 등 다양한 이름 패턴 시도
            base_candidates = [m for m in available if "sdxl" in m.lower() and ("base" in m.lower() or "1.0" in m.lower()) and "refiner" not in m.lower()]
            if base_candidates:
                self.base_model = base_candidates[0]
            else:
                self.base_model = "sdxl_base_1.0.safetensors"  # 기본값
        
        if refiner_model:
            self.refiner_model = refiner_model
        else:
            # 리파이너 모델 자동 탐지
            available = self.model_checker.get_available_models()
            refiner_candidates = [m for m in available if "sdxl" in m.lower() and "refiner" in m.lower()]
            if refiner_candidates:
                self.refiner_model = refiner_candidates[0]
            else:
                self.refiner_model = "sdxl_refiner_1.0.safetensors"  # 기본값
        
        # 모델 검증
        self._validate_models()
    
    def _validate_models(self):
        """모델 파일 검증"""
        base_result = self.model_checker.validate_model_file(self.base_model)
        refiner_result = self.model_checker.validate_model_file(self.refiner_model)
        
        if not base_result["exists"]:
            available = self.model_checker.get_available_models()
            raise ValueError(
                f"기본 모델을 찾을 수 없습니다: {self.base_model}\n"
                f"사용 가능한 모델: {', '.join(available[:5]) if available else '없음'}"
            )
        
        if not base_result["valid"]:
            raise ValueError(f"기본 모델 파일 오류: {base_result.get('error', '알 수 없는 오류')}")
        
        if not refiner_result["exists"]:
            # 리파이너는 선택사항이므로 경고만
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"리파이너 모델을 찾을 수 없습니다: {self.refiner_model}. 리파이너 없이 진행합니다.")
            self.refiner_model = None
        elif not refiner_result["valid"]:
            # 리파이너 모델이 손상되었으면 사용하지 않음
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"리파이너 모델 파일 오류: {refiner_result.get('error', '알 수 없는 오류')}. 리파이너 없이 진행합니다.")
            self.refiner_model = None
    
    def _llama_call(self, prompt: str, model: str = None) -> str:
        """LLaMA 모델 호출"""
        if model is None:
            model = self.ollama_model
        
        res = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return res["message"]["content"]
    
    def _build_prompt(self, user_text: str) -> str:
        """프롬프트 빌드"""
        system = """
        You are a world-class creative director.
        Generate cinematic, premium SDXL prompts with ultra sharp detail.
        Include: lighting, texture, lens, mood. Keep it compact.
        """
        return self._llama_call(system + "\nUser request: " + user_text)
    
    def _apply_hyperwise_style(self, prompt_text: str) -> str:
        """HyperWise 스타일 적용"""
        enhance = (
            "8k uhd, ultra-sharp detail, crisp edges, micro-texture, "
            "premium cinematic lighting, 100mm macro lens, soft rim light, "
            "studio-grade commercial photography, realistic reflections"
        )
        return f"{prompt_text}, {enhance}"
    
    def _wait_for_images(self, prompt_id: str) -> List[str]:
        """이미지 생성 완료 대기"""
        max_wait = 300  # 최대 5분 대기
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                response = requests.get(f"{self.comfy_url}/history/{prompt_id}", timeout=10)
                response.raise_for_status()  # HTTP 오류 확인
                
                # 빈 응답 체크
                if not response.text or not response.text.strip():
                    time.sleep(0.25)
                    wait_time += 0.25
                    continue
                
                res = response.json()
                if prompt_id in res:
                    try:
                        imgs = res[prompt_id]["outputs"]["save"]["images"]
                        return [img["filename"] for img in imgs]
                    except (KeyError, TypeError) as e:
                        # 출력 구조가 예상과 다를 수 있음
                        time.sleep(0.25)
                        wait_time += 0.25
                        continue
            except requests.exceptions.JSONDecodeError as e:
                # JSON 파싱 오류 - 빈 응답이나 HTML 응답일 수 있음
                time.sleep(0.25)
                wait_time += 0.25
                continue
            except requests.exceptions.RequestException as e:
                # 네트워크 오류
                time.sleep(0.25)
                wait_time += 0.25
                continue
            except Exception as e:
                # 기타 오류
                time.sleep(0.25)
                wait_time += 0.25
                continue
            
            time.sleep(0.25)
            wait_time += 0.25
        
        raise TimeoutError(f"이미지 생성 시간 초과 (prompt_id: {prompt_id})")
    
    def _download_image(self, filename: str, save_dir: str = None) -> str:
        """이미지 다운로드"""
        if save_dir is None:
            save_dir = self.download_dir
        
        os.makedirs(save_dir, exist_ok=True)
        url = f"{self.comfy_url}/view/{filename}"
        
        img = requests.get(url).content
        path = os.path.join(save_dir, filename)
        
        with open(path, "wb") as f:
            f.write(img)
            f.flush()
            os.fsync(f.fileno())
        
        # Wait until file is fully saved
        for _ in range(20):
            if os.path.exists(path) and os.path.getsize(path) > 1000:
                break
            time.sleep(0.1)
        
        if os.path.getsize(path) < 1000:
            raise Exception(f"Image incomplete: {path}")
        
        return path
    
    def _generate_image(self, prompt: str, mode: str = "high_quality", prefix: str = "hyperwise") -> List[str]:
        """이미지 생성 (내부 메서드)"""
        cfg = MODES[mode]
        
        graph = {
            "prompt": {
                "base_model": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": self.base_model}
                },
                "latent": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {
                        "width": cfg["width"],
                        "height": cfg["height"],
                        "batch_size": 1
                    }
                },
                "positive": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": prompt, "clip": ["base_model", 1]}
                },
                "negative": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "text": "blurry, low-resolution, messy, smudged",
                        "clip": ["base_model", 1]
                    }
                },
                "sampler_base": {
                    "class_type": "KSampler",
                    "inputs": {
                        "model": ["base_model", 0],
                        "seed": 1234,
                        "steps": cfg["steps"],
                        "cfg": cfg["cfg"],
                        "scheduler": "karras",
                        "sampler_name": cfg["sampler"],
                        "denoise": 1.0,
                        "latent_image": ["latent", 0],
                        "positive": ["positive", 0],
                        "negative": ["negative", 0]
                    }
                },
                "decode": {
                    "class_type": "VAEDecode",
                    "inputs": {"samples": ["sampler_base", 0], "vae": ["base_model", 2]}
                },
                "upscale": {
                    "class_type": "ESRGANUpscale",
                    "inputs": {
                        "image": ["decode", 0],
                        "scale": 2
                    }
                } if cfg["upscale"] else None,
                "save": {
                    "class_type": "SaveImage",
                    "inputs": {
                        "images": ["upscale", 0] if cfg["upscale"] else ["decode", 0],
                        "filename_prefix": prefix
                    }
                }
            }
        }
        
        # Remove None (if upscale is disabled)
        graph["prompt"] = {k: v for k, v in graph["prompt"].items() if v is not None}
        
        try:
            response = requests.post(f"{self.comfy_url}/prompt", json=graph, timeout=30)
            response.raise_for_status()
            
            # 빈 응답 체크
            if not response.text or not response.text.strip():
                raise Exception("ComfyUI가 빈 응답을 반환했습니다")
            
            res = response.json()
            
            if "prompt_id" not in res:
                error_msg = res.get("error", {}).get("message", str(res)) if isinstance(res, dict) else str(res)
                raise Exception(f"ComfyUI 오류: {error_msg}")
                
        except requests.exceptions.JSONDecodeError as e:
            raise Exception(f"ComfyUI 응답 파싱 오류: {e}. 응답 내용: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"ComfyUI 통신 오류: {e}")
        
        prompt_id = res["prompt_id"]
        files = self._wait_for_images(prompt_id)
        
        return [self._download_image(f) for f in files]
    
    def _evaluate_image(self, path: str) -> str:
        """이미지 평가 (비전 피드백)"""
        for _ in range(20):
            if os.path.exists(path) and os.path.getsize(path) > 1200:
                break
            time.sleep(0.1)
        
        img = base64.b64encode(open(path, "rb").read()).decode()
        res = ollama.chat(
            model=self.ollama_vision_model,
            messages=[{
                "role": "user",
                "content": "Analyze image clarity and suggest improvements.",
                "images": [img]
            }]
        )
        return res["message"]["content"]
    
    def _improve_prompt(self, prompt: str, feedback: str) -> str:
        """프롬프트 개선"""
        p = f"""
Improve this SDXL prompt using feedback.

Prompt:
{prompt}

Feedback:
{feedback}

Improved Prompt:
"""
        return self._llama_call(p)
    
    def _refine_loop(self, prompt: str, mode: str = "high_quality", rounds: int = 1, use_vision: bool = True) -> List[str]:
        """반복 개선 루프"""
        current = prompt
        
        for i in range(rounds):
            print(f"♻️ Refining Iteration {i+1}")
            images = self._generate_image(current, mode=mode)
            
            if use_vision:
                feedback = self._evaluate_image(images[0])
                current = self._improve_prompt(current, feedback)
        
        return images
    
    def generate_product_image(self, user_text: str, mode: str = "high_quality") -> List[str]:
        """
        제품 이미지 생성
        
        Args:
            user_text: 사용자 입력 텍스트
            mode: 생성 모드 (fast, balanced, high_quality)
            
        Returns:
            생성된 이미지 파일 경로 목록
        """
        base = self._build_prompt(user_text)
        styled = self._apply_hyperwise_style(base)
        return self._refine_loop(styled, mode=mode)

