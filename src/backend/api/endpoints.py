from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/inpaint")
async def inpaint_image(image: str):
    return {"message": "Inpainting not implemented yet."}