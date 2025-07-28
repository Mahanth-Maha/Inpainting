import numpy as np
import streamlit as st
import requests
import json
import time
from PIL import Image
import streamlit.components.v1 as components
from PIL import Image
from io import BytesIO
import subprocess
import io
import base64
import os

import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from PIL import Image
from io import BytesIO

# Ensure temp folder exists
os.makedirs("temp", exist_ok=True)

# --- Imports and Initial Setup ---
# --- Page Configuration and Styling ---
st.set_page_config(
    page_title="Image Editor",
    page_icon="🎨",
    layout="wide"
)

# --- Dependencies Check ---
# try:
#     from streamlit_drawable_canvas import st_canvas
# except ImportError:
#     st.error("This app requires streamlit-drawable-canvas. Please install it using: pip install streamlit-drawable-canvas")
#     st.stop()


# Custom CSS for better styling
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


# --- API Configuration ---
API_URL = "http://localhost:8000/v1"

# --- Session State Initialization ---
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

# --- Helper Functions ---
def restart_app():
    """Resets the entire session state to start over."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("🖼️ Image Editor")
    st.session_state.app_mode = st.radio(
        "Choose an editing mode:",
        (
            "Object Repaint", 
            "Manual Mask", 
            "Maha Manual",
            "Classic Filters",
        ),
        captions=[
            "Auto-detect & replace objects.", 
            "Draw a mask to erase/replace.", 
            "Draw a mask manually.",
            "Apply standard image filters."
        ]
    )
    st.markdown("---")
    if st.button("Restart Application", key="restart_button"):
        restart_app()

# --- Main Application Logic ---
st.header(f"Mode: {st.session_state.app_mode}")

# Step 1: File Upload (Common to all modes)
if st.session_state.step == "upload":
    st.session_state.uploaded_file = st.file_uploader(
        "Choose an image to get started...",
        type=["jpg", "jpeg", "png"]
    )
    if st.session_state.uploaded_file:
        st.session_state.step = "edit"
        st.rerun()

# Step 2: Edit and Display
if st.session_state.step == "edit":
    col1, col2 = st.columns(2)
    
    # --- OBJECT REPAINT MODE ---
    if st.session_state.app_mode == "Object Repaint":
        with col1:
            st.subheader("Original Image")
            st.image(st.session_state.uploaded_file, use_container_width=True)
            
            # Trigger object detection
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
            
            # Display controls for inpainting
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

    # --- MANUAL MASK MODE ---
    elif st.session_state.app_mode == "Manual Mask":
        # with col1:
        #     st.subheader("Draw on Image")
        #     st.info("Paint over the area you want to erase or replace.")
            
        #     # Load the background image
        #     bg_image = Image.open(st.session_state.uploaded_file).convert("RGB")
            
        #     # Configure the canvas
        #     canvas_result = st_canvas(
        #         fill_color="rgba(79, 139, 249, 0.3)",  # Semi-transparent light blue
        #         stroke_width=20,
        #         stroke_color="rgba(79, 139, 249, 0.8)",
        #         background_image=bg_image,
        #         update_streamlit=True,
        #         height=bg_image.height,
        #         width=bg_image.width,
        #         drawing_mode="freedraw",
        #         key="canvas",
        #     )
            
        #     replacement_prompt = st.text_input("Optional: Describe what to replace the masked area with", placeholder="e.g., 'a calm blue sky'")

        #     if st.button("Apply Manual Mask"):
        #         if canvas_result.image_data is not None:
        #             with st.spinner("Generating mask and repainting..."):
        #                 # The mask is the alpha channel of the canvas result
        #                 mask = canvas_result.image_data[:, :, 3] > 0
        #                 if np.sum(mask) > 0:
        #                     mask_img = Image.fromarray(mask)
                            
        #                     # Convert mask to bytes to send in request
        #                     buf = io.BytesIO()
        #                     mask_img.save(buf, format='PNG')
        #                     mask_bytes = buf.getvalue()
                            
        #                     try:
        #                         files = {
        #                             "image": (st.session_state.uploaded_file.name, st.session_state.uploaded_file.getvalue(), st.session_state.uploaded_file.type),
        #                             "mask": ("mask.png", mask_bytes, "image/png")
        #                         }
        #                         data = {}
        #                         if replacement_prompt:
        #                             data["prompt"] = replacement_prompt
                                
        #                         # This assumes the /inpaint endpoint can handle a 'mask' file
        #                         response = requests.post(f"{API_URL}/inpaint", files=files, data=data)
        #                         if response.status_code == 200:
        #                             st.session_state.processed_image = response.content
        #                             st.session_state.error = None
        #                         else:
        #                             st.session_state.error = f"Error inpainting with mask (Status: {response.status_code})."
        #                         st.rerun()
        #                     except requests.exceptions.RequestException as e:
        #                         st.session_state.error = f"Failed to connect to server: {e}"
        #                         st.rerun()
        #                 else:
        #                     st.warning("Please draw on the image to create a mask.")
        #         else:
        #             st.warning("Please draw on the image to create a mask.")
        with col1:
            st.subheader("Original Image")
            st.image(st.session_state.uploaded_file, use_container_width=True)
            

            MASK_PATH = "temp/manual_mask.png"
            IMG_PATH = "temp/input_image.png"
            st.subheader("🖌️ Draw Manual Mask")

            os.makedirs("temp", exist_ok=True)

            # Save uploaded image only once
            if not os.path.exists(IMG_PATH):
                uploaded_pil = Image.open(BytesIO(st.session_state.uploaded_file.getvalue())).convert("RGB")
                uploaded_pil.save(IMG_PATH)

            # State variable to control masking flow
            if "mask_ready" not in st.session_state:
                st.session_state.mask_ready = False

            if st.button("Open Drawing Tool"):
                try:
                    if os.path.exists(MASK_PATH):
                        os.remove(MASK_PATH)

                    process = subprocess.Popen(["python", "tk_mask_drawer.py"])
                    st.info("🎨 Drawing tool launched. Please draw and save the mask...")

                    # Wait for mask
                    start_time = time.time()
                    timeout = 60
                    while not os.path.exists(MASK_PATH):
                        if time.time() - start_time > timeout:
                            st.error("⏱️ Timed out waiting for the mask to be saved.")
                            break
                        time.sleep(1)

                    # Terminate process once done
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
            # Display and submit masked image
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


    # --- CLASSIC FILTERS MODE ---
    elif st.session_state.app_mode == "Maha Manual":
        # with col1:
        #     st.subheader("Draw on Image")
        #     st.info("Paint over the area you want to erase or replace.")
            
        #     # Convert uploaded image to a base64 string to pass to HTML
        #     bg_image = Image.open(st.session_state.uploaded_file)
        #     buffered = io.BytesIO()
        #     bg_image.save(buffered, format="PNG")
        #     img_str = base64.b64encode(buffered.getvalue()).decode()
        #     bg_image_data_url = f"data:image/png;base64,{img_str}"

            # Define the HTML/JS for the canvas component
            # canvas_html = f"""
            #     <!DOCTYPE html>
            #     <html>
            #     <head>
            #     <style>
            #       body {{ margin: 0; padding: 0; }}
            #       #canvas-container {{ 
            #           position: relative; 
            #           width: 100%; 
            #           max-width: {bg_image.width}px;
            #           max-height: {bg_image.height}px;
            #           border: 1px solid #ccc;
            #       }}
            #       canvas {{ position: absolute; top: 0; left: 0; }}
            #       #draw-canvas {{ cursor: crosshair; }}
            #     </style>
            #     </head>
            #     <body>
            #       <div id="canvas-container">
            #         <canvas id="image-canvas"></canvas>
            #         <canvas id="draw-canvas"></canvas>
            #       </div>

            #     <script>
            #         const bgImage = new Image();
            #         const imageCanvas = document.getElementById('image-canvas');
            #         const imageCtx = imageCanvas.getContext('2d');
            #         const drawCanvas = document.getElementById('draw-canvas');
            #         const drawCtx = drawCanvas.getContext('2d');
            #         let isDrawing = false;

            #         bgImage.onload = () => {{
            #             imageCanvas.width = drawCanvas.width = bgImage.width;
            #             imageCanvas.height = drawCanvas.height = bgImage.height;
                        
            #             const container = document.getElementById('canvas-container');
            #             container.style.height = bgImage.height + 'px';
                        
            #             imageCtx.drawImage(bgImage, 0, 0);

            #             drawCtx.strokeStyle = 'rgba(0, 150, 255, 0.7)';
            #             drawCtx.lineWidth = 25;
            #             drawCtx.lineCap = 'round';
            #             drawCtx.lineJoin = 'round';
            #         }};
            #         bgImage.src = "{bg_image_data_url}";

            #         function getMousePos(canvas, evt) {{
            #             const rect = canvas.getBoundingClientRect();
            #             return {{ x: evt.clientX - rect.left, y: evt.clientY - rect.top }};
            #         }}

            #         drawCanvas.addEventListener('mousedown', (e) => {{
            #             isDrawing = true;
            #             const pos = getMousePos(drawCanvas, e);
            #             drawCtx.beginPath();
            #             drawCtx.moveTo(pos.x, pos.y);
            #         }});

            #         drawCanvas.addEventListener('mousemove', (e) => {{
            #             if (!isDrawing) return;
            #             const pos = getMousePos(drawCanvas, e);
            #             drawCtx.lineTo(pos.x, pos.y);
            #             drawCtx.stroke();
            #         }});

            #         const stopDrawing = () => {{
            #             if (isDrawing) {{
            #                 isDrawing = false;
                            
            #                 // Create a new canvas to generate the black and white mask
            #                 const maskCanvas = document.createElement('canvas');
            #                 maskCanvas.width = drawCanvas.width;
            #                 maskCanvas.height = drawCanvas.height;
            #                 const maskCtx = maskCanvas.getContext('2d', {{ willReadFrequently: true }});

            #                 // Get pixel data from the drawing
            #                 const drawingData = drawCtx.getImageData(0, 0, drawCanvas.width, drawCanvas.height);
            #                 const pixels = drawingData.data;

            #                 // Create new image data for the mask
            #                 const maskImageData = maskCtx.createImageData(drawCanvas.width, drawCanvas.height);
            #                 const maskPixels = maskImageData.data;

            #                 for (let i = 0; i < pixels.length; i += 4) {{
            #                     // If the pixel in the drawing has any alpha, make the mask pixel white
            #                     if (pixels[i + 3] > 0) {{
            #                         maskPixels[i] = 255;      // R
            #                         maskPixels[i + 1] = 255;  // G
            #                         maskPixels[i + 2] = 255;  // B
            #                         maskPixels[i + 3] = 255;  // A
            #                     }} else {{
            #                         // Otherwise, make it black
            #                         maskPixels[i] = 0;
            #                         maskPixels[i + 1] = 0;
            #                         maskPixels[i + 2] = 0;
            #                         maskPixels[i + 3] = 255;
            #                     }}
            #                 }}

            #                 // Put the B&W data onto the new canvas and export it
            #                 maskCtx.putImageData(maskImageData, 0, 0);
            #                 const maskDataUrl = maskCanvas.toDataURL('image/png');
            #                 window.parent.postMessage({{"type": "streamlit:setComponentValue", "value": maskDataUrl}}, "*");
            #             }}
            #         }};
            #         drawCanvas.addEventListener('mouseup', stopDrawing);
            #         drawCanvas.addEventListener('mouseout', stopDrawing);
            #     </script>
            #     </body>
            #     </html>
            # """
#             canvas_html = f"""
# <!DOCTYPE html>
# <html>
# <head>
# <style>
#   body {{ margin: 0; padding: 0; }}
#   #canvas-container {{ 
#       position: relative; 
#       width: 100%; 
#       max-width: {bg_image.width}px;
#       max-height: {bg_image.height}px;
#       border: 1px solid #ccc;
#   }}
#   canvas {{ position: absolute; top: 0; left: 0; }}
#   #draw-canvas {{ cursor: crosshair; }}
#   #save-btn {{
#       margin-top: 10px;
#       padding: 8px 16px;
#       background-color: #2196f3;
#       color: white;
#       border: none;
#       cursor: pointer;
#   }}
# </style>
# </head>
# <body>
#   <div id="canvas-container">
#     <canvas id="image-canvas"></canvas>
#     <canvas id="draw-canvas"></canvas>
#   </div>
#   <button id="save-btn">Save Mask</button>

# <script>
#     const bgImage = new Image();
#     const imageCanvas = document.getElementById('image-canvas');
#     const imageCtx = imageCanvas.getContext('2d');
#     const drawCanvas = document.getElementById('draw-canvas');
#     const drawCtx = drawCanvas.getContext('2d');
#     let isDrawing = false;

#     bgImage.onload = () => {{
#         imageCanvas.width = drawCanvas.width = bgImage.width;
#         imageCanvas.height = drawCanvas.height = bgImage.height;

#         const container = document.getElementById('canvas-container');
#         container.style.height = bgImage.height + 'px';

#         imageCtx.drawImage(bgImage, 0, 0);

#         drawCtx.strokeStyle = 'rgba(0, 150, 255, 0.7)';
#         drawCtx.lineWidth = 25;
#         drawCtx.lineCap = 'round';
#         drawCtx.lineJoin = 'round';
#     }};
#     bgImage.src = "{bg_image_data_url}";

#     function getMousePos(canvas, evt) {{
#         const rect = canvas.getBoundingClientRect();
#         return {{ x: evt.clientX - rect.left, y: evt.clientY - rect.top }};
#     }}

#     drawCanvas.addEventListener('mousedown', (e) => {{
#         isDrawing = true;
#         const pos = getMousePos(drawCanvas, e);
#         drawCtx.beginPath();
#         drawCtx.moveTo(pos.x, pos.y);
#     }});

#     drawCanvas.addEventListener('mousemove', (e) => {{
#         if (!isDrawing) return;
#         const pos = getMousePos(drawCanvas, e);
#         drawCtx.lineTo(pos.x, pos.y);
#         drawCtx.stroke();
#     }});

#     drawCanvas.addEventListener('mouseup', () => {{ isDrawing = false; }});
#     drawCanvas.addEventListener('mouseout', () => {{ isDrawing = false; }});

#     // Convert the strokes to a binary mask and send it to Streamlit
#     document.getElementById("save-btn").addEventListener("click", () => {{
#         const maskCanvas = document.createElement('canvas');
#         maskCanvas.width = drawCanvas.width;
#         maskCanvas.height = drawCanvas.height;
#         const maskCtx = maskCanvas.getContext('2d', {{ willReadFrequently: true }});

#         // Get pixel data from the drawing
#         const drawingData = drawCtx.getImageData(0, 0, drawCanvas.width, drawCanvas.height);
#         const pixels = drawingData.data;

#         // Create new image data for the mask
#         const maskImageData = maskCtx.createImageData(drawCanvas.width, drawCanvas.height);
#         const maskPixels = maskImageData.data;

#         for (let i = 0; i < pixels.length; i += 4) {{
#             if (pixels[i + 3] > 0) {{
#                 maskPixels[i] = 255;
#                 maskPixels[i + 1] = 255;
#                 maskPixels[i + 2] = 255;
#                 maskPixels[i + 3] = 255;
#             }} else {{
#                 maskPixels[i] = 0;
#                 maskPixels[i + 1] = 0;
#                 maskPixels[i + 2] = 0;
#                 maskPixels[i + 3] = 255;
#             }}
#         }}

#         maskCtx.putImageData(maskImageData, 0, 0);
#         const maskDataUrl = maskCanvas.toDataURL('image/png');

#         // Send result to Streamlit component handler
#         window.parent.postMessage({{
#             isStreamlitMessage: true,
#             type: "streamlit:setComponentValue",
#             value: maskDataUrl
#         }}, "*");
#     }});
# </script>
# </body>
# </html>
# """

            
#             # Use a custom component to get data back from JS
#             component_value = components.html(canvas_html, height=bg_image.height + 10, width=bg_image.width + 10)
#             my_component = components.declare_component("draw_mask_component", path="path_to_my_component")
#             mask_data_url = my_component(bg_image=..., key="canvas")
#             # If the component returns a value (the drawing), store it in session state
#             if component_value:
#                 st.session_state.mask_data_url = component_value
            
#             replacement_prompt = st.text_input("Optional: Describe what to replace the masked area with", placeholder="e.g., 'a calm blue sky'")

#             if st.button("Apply Manual Mask"):
#                 # Retrieve the mask data from session state
#                 if "mask_data_url" in st.session_state and st.session_state.mask_data_url:
#                     mask_data_url = st.session_state.mask_data_url
#                     # Display the mask image before sending for inpainting
#                     st.subheader("Preview of Drawn Mask")
#                     print(f"{mask_data_url = }")
#                     # mask_data_url is a DeltaGenerator, so get the value from the component
#                     mask_data_url_value = None
#                     if hasattr(mask_data_url, "value"):
#                         mask_data_url_value = mask_data_url.value
#                     else:
#                         mask_data_url_value = mask_data_url

#                     if mask_data_url_value and isinstance(mask_data_url_value, str) and mask_data_url_value.startswith('data:image/png;base64,'):
#                         # Display the mask image preview
#                         st.image(mask_data_url_value, caption="Drawn Mask", use_container_width=True)
#                     else:
#                         st.warning("No valid mask data received from the drawing canvas.")
                        
                    
#                     with st.spinner("Generating mask and repainting..."):
#                         # Decode the base64 mask data URL from the component
#                         try:
#                             # Ensure we have a valid data URL string before splitting
#                             if isinstance(mask_data_url, str) and mask_data_url.startswith('data:image/png;base64,'):
#                                 st.info(f"Mask data received, processing... {mask_data_url = }")
#                                 header, encoded = mask_data_url.split(",", 1)
#                                 mask_bytes = base64.b64decode(encoded)
#                                 mask_image_data = Image.open(io.BytesIO(mask_bytes)).convert('L')
                                
#                                 # The mask is where the pixels are not black
#                                 mask_np = np.array(mask_image_data) > 0
                                
#                                 if np.sum(mask_np) > 0:
#                                     mask_img = Image.fromarray(mask_np)
#                                     buf = io.BytesIO()
#                                     mask_img.save(buf, format='PNG')
#                                     final_mask_bytes = buf.getvalue()
                                    
#                                     files = {{
#                                         "image": (st.session_state.uploaded_file.name, st.session_state.uploaded_file.getvalue(), st.session_state.uploaded_file.type),
#                                         "mask": ("mask.png", final_mask_bytes, "image/png")
#                                     }}
#                                     data = {{}}
#                                     if replacement_prompt:
#                                         data["prompt"] = replacement_prompt
                                    
#                                     response = requests.post(f"{{API_URL}}/inpaint", files=files, data=data)
#                                     if response.status_code == 200:
#                                         st.session_state.processed_image = response.content
#                                         st.session_state.error = None
#                                     else:
#                                         st.session_state.error = f"Error inpainting with mask (Status: {{response.status_code}})."
#                                     st.rerun()
#                                 else:
#                                     st.warning("Please draw on the image to create a mask.")
#                             else:
#                                 st.info(f"... {mask_data_url = }")
#                                 st.error("Received invalid data from the drawing canvas. Please try drawing again.")
#                         except (ValueError, TypeError) as e:
#                             st.error(f"Could not process the drawing from the canvas. Error: {e}")
#                             st.rerun()
#                 else:
#                     st.warning("Please draw on the image to create a mask.")
        

        # Load your background image and encode it
        bg_image = Image.open("temp/input_image.png").convert("RGB")
        buffer = BytesIO()
        bg_image.save(buffer, format="PNG")
        encoded_bg = base64.b64encode(buffer.getvalue()).decode()
        bg_image_data_url = f"data:image/png;base64,{encoded_bg}"

        canvas_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {{ margin: 0; padding: 0; }}
        #canvas-container {{
            position: relative;
            max-width: {bg_image.width}px;
            max-height: {bg_image.height}px;
            border: 1px solid #ccc;
        }}
        canvas {{ position: absolute; top: 0; left: 0; }}
        #draw-canvas {{ cursor: crosshair; }}
        #save-btn {{
            margin-top: 10px;
            padding: 8px 16px;
            background-color: #2196f3;
            color: white;
            border: none;
            cursor: pointer;
        }}
        </style>
        </head>
        <body>
        <div id="canvas-container">
            <canvas id="image-canvas"></canvas>
            <canvas id="draw-canvas"></canvas>
        </div>
        <button id="save-btn">Save Mask</button>

        <script>
            const bgImage = new Image();
            const imageCanvas = document.getElementById('image-canvas');
            const imageCtx = imageCanvas.getContext('2d');
            const drawCanvas = document.getElementById('draw-canvas');
            const drawCtx = drawCanvas.getContext('2d');
            let isDrawing = false;

            bgImage.onload = () => {{
                imageCanvas.width = drawCanvas.width = bgImage.width;
                imageCanvas.height = drawCanvas.height = bgImage.height;

                const container = document.getElementById('canvas-container');
                container.style.height = bgImage.height + 'px';

                imageCtx.drawImage(bgImage, 0, 0);

                drawCtx.strokeStyle = 'rgba(0, 150, 255, 0.7)';
                drawCtx.lineWidth = 25;
                drawCtx.lineCap = 'round';
                drawCtx.lineJoin = 'round';
            }};
            bgImage.src = "{bg_image_data_url}";

            function getMousePos(canvas, evt) {{
                const rect = canvas.getBoundingClientRect();
                return {{ x: evt.clientX - rect.left, y: evt.clientY - rect.top }};
            }}

            drawCanvas.addEventListener('mousedown', (e) => {{
                isDrawing = true;
                const pos = getMousePos(drawCanvas, e);
                drawCtx.beginPath();
                drawCtx.moveTo(pos.x, pos.y);
            }});

            drawCanvas.addEventListener('mousemove', (e) => {{
                if (!isDrawing) return;
                const pos = getMousePos(drawCanvas, e);
                drawCtx.lineTo(pos.x, pos.y);
                drawCtx.stroke();
            }});

            drawCanvas.addEventListener('mouseup', () => {{ isDrawing = false; }});
            drawCanvas.addEventListener('mouseout', () => {{ isDrawing = false; }});

            document.getElementById("save-btn").addEventListener("click", () => {{
                const maskCanvas = document.createElement('canvas');
                maskCanvas.width = drawCanvas.width;
                maskCanvas.height = drawCanvas.height;
                const maskCtx = maskCanvas.getContext('2d', {{ willReadFrequently: true }});

                const drawingData = drawCtx.getImageData(0, 0, drawCanvas.width, drawCanvas.height);
                const pixels = drawingData.data;

                const maskImageData = maskCtx.createImageData(drawCanvas.width, drawCanvas.height);
                const maskPixels = maskImageData.data;

                for (let i = 0; i < pixels.length; i += 4) {{
                    if (pixels[i + 3] > 0) {{
                        maskPixels[i] = 255;
                        maskPixels[i + 1] = 255;
                        maskPixels[i + 2] = 255;
                        maskPixels[i + 3] = 255;
                    }} else {{
                        maskPixels[i] = 0;
                        maskPixels[i + 1] = 0;
                        maskPixels[i + 2] = 0;
                        maskPixels[i + 3] = 255;
                    }}
                }}

                maskCtx.putImageData(maskImageData, 0, 0);
                const maskDataUrl = maskCanvas.toDataURL('image/png');

                // Send back to Streamlit
                window.parent.postMessage({{
                    isStreamlitMessage: true,
                    type: "streamlit:setComponentValue",
                    value: maskDataUrl
                }}, "*");
            }});
        </script>
        </body>
        </html>
        """

        # Render the HTML in Streamlit and get the base64 string when user clicks "Save Mask"
        mask_data_url = components.html(canvas_html, height=bg_image.height + 60, scrolling=False)

        # If the user saved a mask and JS posted the base64
        if isinstance(mask_data_url, str) and mask_data_url.startswith("data:image/png;base64,"):
            header, encoded = mask_data_url.split(",", 1)
            mask_bytes = base64.b64decode(encoded)

            with open("temp/manual_mask.png", "wb") as f:
                f.write(mask_bytes)

            # Auto-load into PIL for preview
            mask_img = Image.open(BytesIO(mask_bytes)).convert("L")
            st.success("Manual mask saved as temp/manual_mask.png")
            st.image(mask_img, caption="Drawn Mask", use_container_width=True)

    # --- CLASSIC FILTERS MODE ---
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

    # Display any errors that occurred
    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = None # Clear error after showing it

    # Display the processed image in the second column
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
