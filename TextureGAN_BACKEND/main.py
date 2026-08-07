# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.generation import router as generation_router
from routers.auth import auth_router
import app_state
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
app = FastAPI(title="GAN Pattern Generator API")

# CORS for all origins (adapt to production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_models_on_startup():
    print("🔄 Loading Generator and CLIP for inference...")
    app_state.generator = app_state.load_generator()
    app_state.clip_model, app_state.clip_tokenizer = app_state.load_clip()
    print("✅ Models loaded and ready!")

@app.get("/api/health")
def healthcheck():
    return {"status": "ok"}

# Mount all routers (including /api/generate, /api/styles, /api/history, /api/login, /api/register)
app.include_router(generation_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "GAN Pattern Generator Backend is up!"}
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"error": exc.detail}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(content={"error": exc.errors()}, status_code=422)