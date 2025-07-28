from calendar import prmonth
import io
import json
import dotenv

from fastapi import APIRouter, UploadFile, File
from PIL import Image, ImageFilter

from fastapi.responses import StreamingResponse
from models.ddpm import PretrainedDDPM, CustomDDPM
from models.object_detect import PretrainedODM, CustomODM

dotenv.load_dotenv()
dot_env_file = dotenv.find_dotenv()

DEBUG_LEVEL = dotenv.get_key(dot_env_file, "DEBUG_LEVEL")
VERBOSE = True if DEBUG_LEVEL == "DEBUG" else False

router = APIRouter()
odm_model = PretrainedODM(pretrained_model_name=0)
ddpm_model = PretrainedDDPM(pretrained_model_name=0)


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/detectobjects")
async def detect_objects_v1(
    image: UploadFile = File(...),
    verbose: bool = VERBOSE,
):
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        if verbose:
            print(f"Image size: {img.size}")
            print(f"Type of image: {type(img)}")

        objects_detected = odm_model.get_objects(img)

        if verbose:
            print(f"Objects detected: {objects_detected}")

        return {"X-Objects": objects_detected}

    except Exception as e:
        return {"error": str(e)}


@router.post("/inpaint")
async def inpaint_image_v1(
    image: UploadFile = File(...),
    object: str = File(...),
    prompt: str = File(...),
    verbose: bool = VERBOSE,
):
    try:
        image_contents = await image.read()
        objects_selected = json.loads(object) 
        if verbose:
            print(f"Image contents type: {type(image_contents)}")
            print(f"Image size: {len(image_contents)} bytes")
            print(f"Objects selected: {objects_selected}")
            print(f"Type of objects_selected: {type(objects_selected)}")
            print(f"Prompt: {prompt}")
            
        img = Image.open(io.BytesIO(image_contents)).convert("RGB")
        mask_img = odm_model.get_mask(img, objects_selected)

        if verbose:
            print(f"Mask image size: {mask_img.size}, Image size: {img.size}")
            print(f"Type of mask image: {type(img)} : {img.size}")
            print(f"Type of mask image: {type(mask_img)} : {mask_img.size}")
        
        ddpm_model_input = {
            'image': img,
            'mask': mask_img,
        }
        
        # if prompt is None or prompt.strip() == "":
        #     inpainted_img = ddpm_model.inference({
        #         'image': img,
        #         'mask': mask_img,
        #     })
        # else:
        #     inpainted_img = ddpm_model.inference({
        #         'image': img,
        #         'mask': mask_img,
        #         'prompt': prompt,
        #     })
        
        if prompt and prompt.strip():
            ddpm_model_input['prompt'] = prompt
        
        inpainted_img = ddpm_model.inference(ddpm_model_input)
        if verbose:
            print(f"Inpainted image type: {type(inpainted_img)}")
        buffer = io.BytesIO()
        inpainted_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}


@router.post("/filter")
async def filter_image_v1(
    image: UploadFile = File(...),
    filter_type: str = File(...),
    verbose: bool = VERBOSE,
):
    try:
        if verbose:
            print(f"Filter type: {filter_type}")
        image_contents = await image.read()
        if verbose:
            print(f"Image contents type: {type(image_contents)}")
            print(f"Image size: {len(image_contents)} bytes")
        # filter_name = json.loads(filter_type)
        filter_name = filter_type.lower()
        img = Image.open(io.BytesIO(image_contents)).convert("RGB")
        if filter_name == "invert":
            filtered_img = Image.eval(img, lambda x: 255 - x)
        elif filter_name == "blur":
            filtered_img = img.filter(ImageFilter.BLUR)
        elif filter_name == "sharpen":
            filtered_img = img.filter(ImageFilter.SHARPEN)
        elif filter_name == "black_and_white":
            filtered_img = img.convert("L")
        else:
            return {"error": "Unknown filter"}
        if verbose:
            print(f"Filtered image size: {filtered_img.size}")
            print(f"Type of filtered image: {type(filtered_img)}")
        buffer = io.BytesIO()
        filtered_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}

@router.post("/manualinpaint")
async def inpaint_manual_mask_v1(
    image: UploadFile = File(...),
    mask: UploadFile = File(...),
    prompt: str = File(...),
    verbose: bool = VERBOSE,
):
    try:
        image_bytes = await image.read()
        mask_bytes = await mask.read()

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L").resize(img.size)

        ddpm_model_input = {
            'image': img,
            'mask': mask_img,
        }        
        if prompt and prompt.strip():
            ddpm_model_input['prompt'] = prompt

        inpainted_img = ddpm_model.inference(ddpm_model_input)

        buffer = io.BytesIO()
        inpainted_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}

