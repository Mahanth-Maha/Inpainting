from fastapi import APIRouter, UploadFile, File
from PIL import Image, ImageFilter
import io

from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/inpaint")
async def inpaint_image(image: str):
    return {"message": "Inpainting not implemented yet."}


@router.post("/invertimage")
async def invert_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        inverted_img = Image.eval(img, lambda x: 255 - x)
        buffer = io.BytesIO()
        inverted_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}


@router.post("/blurimage")
async def blur_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        blurred_img = img.filter(ImageFilter.BLUR)
        buffer = io.BytesIO()
        blurred_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}    

@router.post("/blackandwhite")
async def black_and_white_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        bw_img = img.convert("L")
        buffer = io.BytesIO()
        bw_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        buffer = io.BytesIO()
        bw_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}