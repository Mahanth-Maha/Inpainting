from fastapi import APIRouter, UploadFile, File
from PIL import Image, ImageFilter
import io
from fastapi.responses import StreamingResponse
from models.ddpm import PretrainedDDPM, CustomDDPM
from models.object_detect import PretrainedODM, CustomODM

router = APIRouter()
odm_model = PretrainedODM(pretrained_model_name=0)
ddpm_model = PretrainedDDPM(pretrained_model_name=0)

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/detectobjects")
async def detect_objects(image: UploadFile = File(...), verbose: bool = True):
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        
        if verbose:
            print(f"Image size: {img.size}")
            print(f"Type of image: {type(img)}")
        
        odm_model = PretrainedODM(pretrained_model_name=0)
        objects_detected = odm_model.get_objects(img)
        
        if verbose:
            print(f"Objects detected: {objects_detected}")
        
        return {"X-objects": objects_detected}
    except Exception as e:
        return {"error": str(e)}
        # return {"message": "Object detection not implemented yet."}

@router.post("/inpaint")
async def inpaint_image(
        image: UploadFile = File(...), 
        # mask: UploadFile = File(...), 
        # prompt: str = "", 
        objects_selected :str = None,
        verbose: bool = True
    ):
    try:
        image_contents = await image.read()
        # mask_contents = await mask.read()
        
        img = Image.open(io.BytesIO(image_contents)).convert("RGB")        
        mask_img = odm_model.get_mask(img, objects_selected)
        
        if verbose:
            print(f"Mask image size: {mask_img.size}, Image size: {img.size}")
            # print(f"Prompt: {prompt}")
            print(f"Type of mask image: {type(img)}")
            print(f"Type of mask image: {type(mask_img)}")
        
        inpainted_img = ddpm_model.inference({
            'image': img,
            'mask': mask_img,
            # 'prompt': prompt
        })
        if verbose:
            print(f"Inpainted image type: {type(inpainted_img)}")
        buffer = io.BytesIO()
        inpainted_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}
        # return {"message": "Inpainting not implemented yet."}


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