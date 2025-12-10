"""
요청 모델
"""
from pydantic import BaseModel, Field
from app.core.config import DEFAULT_MODE


class PromptRequest(BaseModel):
    """이미지 생성 요청 모델"""
    prompt: str = Field(..., description="이미지 생성 프롬프트", min_length=1)
    mode: str = Field(
        default=DEFAULT_MODE,
        description="생성 모드",
        pattern="^(fast|balanced|high_quality)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "frosted glass vegan shampoo bottle product commercial",
                "mode": "high_quality"
            }
        }

