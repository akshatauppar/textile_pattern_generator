# schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=2, max_length=250, description="Text description for the pattern")
    primary_color: List[int] = Field(..., description="Primary RGB color as [R,G,B] (0-255)")
    secondary_color: List[int] = Field(..., description="Secondary RGB color as [R,G,B] (0-255)")
    seed: Optional[int] = Field(None, description="Random seed (optional)")
    num_samples: Optional[int] = Field(1, ge=1, le=8, description="How many variations to produce")
    # If your API expects the raw reference image as URL, base64, or file elsewhere, add here
    
    @validator('primary_color', 'secondary_color')
    def check_rgb(cls, v):
        assert isinstance(v, list), "Color must be a list"
        assert len(v) == 3, "Color list must be [R, G, B]"
        assert all(0 <= x <= 255 for x in v), "All RGB values must be in 0-255"
        return v

    @validator('prompt')
    def check_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt is required and can't be empty")
        return v.strip()