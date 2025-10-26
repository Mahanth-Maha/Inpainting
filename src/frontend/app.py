import io
import os
import json
import time
import base64
import requests
import subprocess

import dotenv
import numpy as np
import streamlit as st
from PIL import Image
from io import BytesIO

from components.canvas_mask import st_canvas_mask

st.set_page_config(
    page_title="Image Editor",
    page_icon="🎨",
    layout="wide"
)

st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Sidebar styling */
    .st-emotion-cache-16txtl3 {
        padding: 1rem;
    }
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #4F8BF9;
        color: #4F8BF9;
        background-color: transparent;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #FFFFFF;
        color: #FFFFFF;
        background-color: #4F8BF9;
    }
    /* Make spinners more prominent */
    .stSpinner > div > div {
        border-top-color: #4F8BF9;
        border-width: 3px;
    }
</style>
""", unsafe_allow_html=True)


# Load environment variables
dotenv.load_dotenv()

find_dotenv_path = dotenv.find_dotenv()

DEBUG_LEVEL = dotenv.get_key(find_dotenv_path, "DEBUG_LEVEL")
VERBOSE = True if DEBUG_LEVEL == "DEBUG" else False

API_HOST = dotenv.get_key(find_dotenv_path, "API_HOST")
API_PORT = dotenv.get_key(find_dotenv_path, "API_PORT")
API_VERSION = dotenv.get_key(find_dotenv_path, "API_VERSION")

API_URL = f"http://{API_HOST}:{API_PORT}/{API_VERSION}"

def init_session_state():
    """Initializes all necessary session state variables."""
    if 'step' not in st.session_state:
        st.session_state.step = "upload"
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = "Object Repaint"
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'detected_objects' not in st.session_state:
        st.session_state.detected_objects = []
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'error' not in st.session_state:
        st.session_state.error = None

init_session_state()

def restart_app():
    """Resets the entire session state to start over."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


with st.sidebar:
    st.title("Image Editor 🎨")
    st.session_state.app_mode = st.radio(
        "Choose an editing mode:",
        (
            "Object Repaint", 
            "External Manual Mask", 
            "Embedded Manual Mask",
            "Classic Filters",
        ),
        captions=[
            "Auto-detect & replace objects.", 
            "Draw to erase/replace in external tool.", 
            "Draw directly on the image.",
            "Apply standard image filters."
        ]
    )
    
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Restart Application", key="restart_button"):
        restart_app()

st.header(f"Mode: {st.session_state.app_mode}")


if st.session_state.step == "upload":
    st.session_state.uploaded_file = st.file_uploader(
        "Choose an image to get started...",
        type=["jpg", "jpeg", "png"]
    )
    if st.session_state.uploaded_file:
        st.session_state.step = "edit"
        st.rerun()


if st.session_state.step == "edit":
    col1, col2 = st.columns(2)
    
    if st.session_state.app_mode == "Object Repaint":
        with col1:
            st.subheader("Original Image")
            st.image(st.session_state.uploaded_file, use_container_width=True)

            if not st.session_state.detected_objects and 'detection_triggered' not in st.session_state:
                st.session_state.detection_triggered = True
                with st.spinner("Analyzing image to find objects..."):
                    try:
                        files = {"image": (st.session_state.uploaded_file.name, st.session_state.uploaded_file.getvalue(), st.session_state.uploaded_file.type)}
                        response = requests.post(f"{API_URL}/detectobjects", files=files)
                        if response.status_code == 200:
                            st.session_state.detected_objects = response.json().get("X-Objects", [])
                            st.rerun()
                        else:
                            st.session_state.error = f"Error detecting objects (Status: {response.status_code})."
                    except requests.exceptions.RequestException as e:
                        st.session_state.error = f"Failed to connect to the server: {e}"

            st.subheader("Object Selection")
            if not st.session_state.detected_objects:
                st.warning("No objects were detected.")
            
            selected_objects = st.multiselect("Choose objects to remove or replace:", st.session_state.detected_objects)
            replacement_prompt = st.text_input("Optional: Describe what to replace the object with", placeholder="e.g., 'a vase of sunflowers'")

            if st.button("Apply Repaint"):
                if selected_objects:
                    with st.spinner("Repainting the image... Please wait."):
                        try:
                            files = {"image": (st.session_state.uploaded_file.name, st.session_state.uploaded_file.getvalue(), st.session_state.uploaded_file.type)}
                            data = {"object": json.dumps(selected_objects)}
                            if replacement_prompt:
                                data["prompt"] = replacement_prompt
                            else:
                                data["prompt"] = "Replace with a natural background."
                            response = requests.post(f"{API_URL}/inpaint", files=files, data=data)
                            if response.status_code == 200:
                                st.session_state.processed_image = response.content
                                st.session_state.error = None
                            else:
                                st.session_state.error = f"Error inpainting (Status: {response.status_code})."
                            st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.session_state.error = f"Failed to connect to server: {e}"
                            st.rerun()
                else:
                    st.warning("Please select at least one object.")

    elif st.session_state.app_mode == "External Manual Mask":
        st.warning("This mode is deprecated. Please use 'Embedded Manual Mask' instead.")
        os.makedirs("temp", exist_ok=True)
        
        with col1:
            st.subheader("Original Image")
            st.image(st.session_state.uploaded_file, use_container_width=True)
            

            MASK_PATH = "temp/manual_mask.png"
            IMG_PATH = "temp/input_image.png"
            st.subheader("🖌️ Draw Manual Mask")

            os.makedirs("temp", exist_ok=True)

            if not os.path.exists(IMG_PATH):
                uploaded_pil = Image.open(BytesIO(st.session_state.uploaded_file.getvalue())).convert("RGB")
                uploaded_pil.save(IMG_PATH)

            if "mask_ready" not in st.session_state:
                st.session_state.mask_ready = False

            if st.button("Open Drawing Tool"):
                try:
                    if os.path.exists(MASK_PATH):
                        os.remove(MASK_PATH)

                    process = subprocess.Popen(["python", "tk_mask_drawer.py"])
                    st.info("🎨 Drawing tool launched. Please draw and save the mask...")

                    start_time = time.time()
                    timeout = 60
                    while not os.path.exists(MASK_PATH):
                        if time.time() - start_time > timeout:
                            st.error("⏱️ Timed out waiting for the mask to be saved.")
                            break
                        time.sleep(1)

                    if os.path.exists(MASK_PATH):
                        try:
                            process.terminate()
                            process.wait(timeout=5)
                            st.session_state.mask_ready = True
                        except Exception as e:
                            st.warning(f"⚠️ Could not terminate drawing tool: {e}")

                except Exception as e:
                    st.error(f"❌ Error launching drawing tool: {e}")
                    st.stop()
        with col2:
            if st.session_state.mask_ready:
                if os.path.exists(MASK_PATH):
                    st.success("✅ Mask saved. Preview:")
                    mask_img = Image.open(MASK_PATH)
                    st.image(mask_img, caption="Drawn Mask", use_container_width=True)

                    if st.button("Inpaint Manual Mask"):
                        try:
                            files = {
                                "image": (
                                    st.session_state.uploaded_file.name,
                                    st.session_state.uploaded_file.getvalue(),
                                    st.session_state.uploaded_file.type
                                ),
                                "mask": (
                                    "manual_mask.png",
                                    open(MASK_PATH, "rb"),
                                    "image/png"
                                )
                            }
                            response = requests.post(f"{API_URL}/manualinpaint", files=files)
                            if response.status_code == 200:
                                st.session_state.processed_image = response.content
                                st.session_state.error = None

                            else:
                                st.session_state.error = f"Error applying filter (Status: {response.status_code})."
                                st.rerun()
                        except requests.exceptions.RequestException as e:
                            st.session_state.error = f"This is a demo endpoint. Failed to connect: {e}"
                            st.rerun()
                            
                        if os.path.exists("temp"):
                            try:
                                import shutil
                                shutil.rmtree("temp")
                                # st.info("🧹 Temporary folder 'temp/' deleted successfully.")
                            except Exception as e:
                                # st.warning(f"⚠️ Could not delete 'temp/' folder: {e}")
                                pass
                else:
                    st.warning("⚠️ Waiting for mask to be saved...")


    elif st.session_state.app_mode == "Embedded Manual Mask":
        with col1:
            st.subheader("Draw on Image")
            bg_image = Image.open(st.session_state.uploaded_file)
            buffered = io.BytesIO()
            bg_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            bg_image_data_url = f"data:image/png;base64,{img_str}"

            component_value = st_canvas_mask(
                image_data_url=bg_image_data_url,
                image_width=bg_image.width,
                image_height=bg_image.height,
                key="mask_drawing"
            )
            st.info("1. Draw your mask. 2. Click 'Confirm Mask' below the image. 3. Click 'Apply Manual Mask'.")

            if component_value:
                st.session_state.mask_data_url = component_value
            
            if 'mask_data_url' in st.session_state and st.session_state.mask_data_url:
                st.success("Mask confirmed! You can now apply it.")

            replacement_prompt = st.text_input("Optional: Describe what to replace the masked area with", placeholder="e.g., 'a calm blue sky'")

            if st.button("Apply Manual Mask"):
                if "mask_data_url" in st.session_state and st.session_state.mask_data_url:
                    mask_data_url = st.session_state.mask_data_url
                    # print(f"Mask Data URL: {type(mask_data_url) = }")
                    with st.spinner("Generating mask and repainting..."):
                        try:
                            if isinstance(mask_data_url, str) and mask_data_url.startswith('data:image/png;base64,'):
                                header, encoded = mask_data_url.split(",", 1)
                                mask_bytes = base64.b64decode(encoded)
                                mask_image_data = Image.open(io.BytesIO(mask_bytes)).convert('L')
                                
                                mask_np = np.array(mask_image_data) > 0
                                # print(f"{st.session_state.uploaded_file.name = }\n{st.session_state.uploaded_file.type =}\n")
                                if np.sum(mask_np) > 0:
                                    mask_img = Image.fromarray(mask_np)
                                    buf = io.BytesIO()
                                    mask_img.save(buf, format='PNG')
                                    final_mask_bytes = buf.getvalue()
                                    # print(f"Sent::\n> IMAGE\n\tImage: {st.session_state.uploaded_file.name},\n\tData Type: {st.session_state.uploaded_file.type},\n\tType : {type(st.session_state.uploaded_file.getvalue()) = }\n\tSIZE: {len(st.session_state.uploaded_file.getvalue())} bytes")
                                    # print(f"> MASK\n\tImage: mask.png\n\tData Type: image/png\n\tType : {type(final_mask_bytes) = }\n\tSIZE: {len(final_mask_bytes)} bytes")
                                    files = {
                                        "image": (
                                            st.session_state.uploaded_file.name,
                                            st.session_state.uploaded_file.getvalue(),
                                            st.session_state.uploaded_file.type
                                        ),
                                        "mask": (
                                            "mask.png", 
                                            final_mask_bytes, 
                                            "image/png"
                                        )
                                    }
                                    
                                    data = {}
                                    if replacement_prompt:
                                        data["prompt"] = replacement_prompt
                                    else:
                                        # data["prompt"] = "Replace with a natural background."
                                        data["prompt"] = ""
                                    
                                    response = requests.post(f"{API_URL}/manualinpaint", files=files, data=data)
                                    if response.status_code == 200:
                                        st.session_state.processed_image = response.content
                                        st.session_state.error = None
                                    else:
                                        st.session_state.error = f"Error inpainting with mask (Status: {response.status_code})."
                                    st.rerun()
                                else:
                                    st.warning("The confirmed mask was empty. Please draw on the image.")
                            else:
                                st.error("Received invalid data from the drawing canvas. Please try drawing again.")
                        except (ValueError, TypeError) as e:
                            st.error(f"Could not process the drawing from the canvas. Error: {e}")
                            st.rerun()
                else:
                    st.warning("Please draw on the image and click 'Confirm Mask' before applying.")

    elif st.session_state.app_mode == "Classic Filters":
        with col1:
            st.subheader("Original Image")
            st.image(st.session_state.uploaded_file, use_container_width=True)
            st.subheader("Filter Selection")
            filter_type = st.selectbox("Choose a filter:", ["None", "Invert", "Blur", "Black and White", "Sharpen"])
            if st.button("Apply Filter") and filter_type != "None":
                with st.spinner(f"Applying {filter_type} filter..."):
                    try:
                        files = {"image": (st.session_state.uploaded_file.name, st.session_state.uploaded_file.getvalue(), st.session_state.uploaded_file.type)}
                        data = {"filter_type": filter_type.lower().replace(" ", "_")}
                        response = requests.post(f"{API_URL}/filter", files=files, data=data)
                        if response.status_code == 200:
                            st.session_state.processed_image = response.content
                            st.session_state.error = None
                        else:
                            st.session_state.error = f"Error applying filter (Status: {response.status_code})."
                        st.rerun()
                    except requests.exceptions.RequestException as e:
                        st.session_state.error = f"This is a demo endpoint. Failed to connect: {e}"
                        st.rerun()

    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = None

    with col2:
        st.subheader("Result")
        if st.session_state.processed_image:
            st.image(st.session_state.processed_image, use_container_width=True)
            st.download_button(
                label="Download Result",
                data=st.session_state.processed_image,
                file_name=f"{st.session_state.uploaded_file.name}_edited.png",
                mime="image/png"
            )
        else:
            st.info("Your processed image will appear here.")
