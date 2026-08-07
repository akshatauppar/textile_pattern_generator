
# routers/generation.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from schemas import GenerationRequest
from typing import Optional
import json
from PIL import Image
import io
import numpy as np
import torch
import base64

import app_state  # Import your global models and device

router = APIRouter()

@router.get("/api/styles")
async def get_styles():
    # Return textile styles with patterns for frontend compatibility
    return {"styles": [
        {
            "id": "bandhani",
            "name": "Bandhani",
            "description": "Traditional tie-dye patterns",
            "patterns": [
                {"id": "leheriya", "name": "Leheriya", "description": "Diagonal wavy lines"},
                {"id": "shikari", "name": "Shikari", "description": "Hunting pattern"},
                {"id": "mothra", "name": "Mothra", "description": "Circular motifs"},
                {"id": "rajasthani_tie", "name": "Rajasthani Tie", "description": "Traditional tie"},
                {"id": "mandala", "name": "Mandala", "description": "Circular mandala"},
            ]
        },
        {
            "id": "batik",
            "name": "Batik",
            "description": "Wax-resist dyeing technique",
            "patterns": [
                {"id": "geometric_batik", "name": "Geometric", "description": "Geometric patterns"},
                {"id": "floral_batik", "name": "Floral", "description": "Floral designs"},
                {"id": "traditional_batik", "name": "Traditional", "description": "Indonesian batik"},
                {"id": "wax_resist", "name": "Wax Resist", "description": "Wax resist"},
                {"id": "crackle", "name": "Crackle", "description": "Crackle effect"},
            ]
        },
        {
            "id": "ikat",
            "name": "Ikat",
            "description": "Resist-dyed textile patterns",
            "patterns": [
                {"id": "striped_ikat", "name": "Striped", "description": "Striped pattern"},
                {"id": "diamond_ikat", "name": "Diamond", "description": "Diamond motifs"},
                {"id": "blurred_motif", "name": "Blurred Motif", "description": "Blurred edges"},
                {"id": "traditional_ikat", "name": "Traditional", "description": "Traditional weave"},
                {"id": "woven_pattern", "name": "Woven Pattern", "description": "Woven patterns"},
            ]
        }
    ]}

@router.get("/api/history")
async def get_history(limit: int = 10, offset: int = 0):
    # Return empty history for now (no DB)
    return {"generations": []}

def pil_image_from_bytes(img_bytes):
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        return img
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to decode reference image!")

# CLIP text encoding (batch of size 1+)
def encode_text(prompt_list):
    tokens = app_state.clip_tokenizer(
        prompt_list, padding=True, truncation=True, max_length=77, return_tensors="pt"
    )
    tokens = {k: v.to(app_state.device) for k, v in tokens.items()}
    with torch.no_grad():
        out = app_state.clip_model.text_model(**tokens)
        pooled = out.pooler_output
        emb = app_state.clip_model.text_projection(pooled)
    return emb

# CLIP image encoding (single PIL image)
def encode_reference_image(img):
    # Resize, normalize, to tensor with CLIP preprocessing, then encode
    import torchvision.transforms as T
    preprocess = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711]
        )
    ])
    tensor = preprocess(img).unsqueeze(0).to(app_state.device)
    with torch.no_grad():
        out = app_state.clip_model.vision_model(pixel_values=tensor)
        pooled = out.pooler_output
        emb = app_state.clip_model.visual_projection(pooled)
    return emb

def format_colors(primary, secondary):
    # Convert RGB (0-255 ints) to float32 0-1, concatenate
    rgb1 = [float(x) / 255.0 for x in primary]
    rgb2 = [float(x) / 255.0 for x in secondary]
    return torch.tensor([rgb1 + rgb2], dtype=torch.float32, device=app_state.device)


@router.post("/api/generate")
async def generate_pattern(
    prompt: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    seed: Optional[int] = Form(None),
    num_samples: Optional[int] = Form(1),
    reference_image: Optional[UploadFile] = File(None)
):
    # Debug: log incoming data
    print(f"[API] /api/generate called with prompt={prompt}, primary_color={primary_color}, secondary_color={secondary_color}, seed={seed}, num_samples={num_samples}")
    # Parse and validate colors
    try:
        # Accept both JSON string and direct list for color fields
        def parse_color(val):
            if isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            if isinstance(val, list):
                return val
            raise ValueError(f"Color must be a JSON list or list, got: {val}")
        primary_color_list = parse_color(primary_color)
        secondary_color_list = parse_color(secondary_color)
        req = GenerationRequest(
            prompt=prompt,
            primary_color=primary_color_list,
            secondary_color=secondary_color_list,
            seed=seed,
            num_samples=num_samples
        )
    except Exception as e:
        print(f"[API] /api/generate validation error: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")

    # Handle prompt, batch setup
    batch_size = req.num_samples

    # Handle seeding for reproducibility
    if req.seed is not None:
        torch.manual_seed(req.seed)
        np.random.seed(req.seed)

    # Encode text batch
    text_embed = encode_text([req.prompt] * batch_size)
    # Encode reference (if any)
    img_embed = None
    if reference_image is not None:
        if reference_image.content_type not in ["image/png", "image/jpeg"]:
            raise HTTPException(status_code=400, detail="reference_image must be PNG/JPEG")
        img_bytes = await reference_image.read()
        pil_img = pil_image_from_bytes(img_bytes)
        img_embed = encode_reference_image(pil_img).repeat(batch_size, 1)
    # Format colors
    colors = format_colors(req.primary_color, req.secondary_color).repeat(batch_size, 1)
    # Noise input
    noise = torch.randn(batch_size, app_state.generator.latent_dim, device=app_state.device)

    # Run generator
    with torch.no_grad():
        output = app_state.generator(text_embed, colors, noise, img_embed)
    
    # Convert output to images
    results = []
    for i in range(batch_size):
        img = output[i]
        # Clamp, rescale, convert to uint8 image
        img_tensor = (img.clamp(-1, 1) + 1) * 127.5
        img_np = img_tensor.cpu().numpy().astype(np.uint8)
        img_np = np.transpose(img_np, (1, 2, 0))  # CHW to HWC
        img_pil = Image.fromarray(img_np)
        # To base64 for web frontend response
        buffered = io.BytesIO()
        img_pil.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        results.append({
            "image_base64": img_b64
        })

    return JSONResponse(content={"results": results, "count": batch_size})