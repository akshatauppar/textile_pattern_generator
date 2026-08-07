from fastapi import APIRouter
from fastapi.responses import JSONResponse

auth_router = APIRouter()

@auth_router.post("/api/login")
async def login():
    # Always return a dummy token
    return JSONResponse(content={"access_token": "dummy-token"})

@auth_router.post("/api/register")
async def register():
    # Always return success
    return JSONResponse(content={"message": "Registered successfully"})
