import os
import streamlit.components.v1 as components

# Get the directory of this file
_COMPONENT_ROOT = os.path.dirname(os.path.abspath(__file__))
_COMPONENT_BUILD_DIR = os.path.join(_COMPONENT_ROOT, "dist")

# Declare the component
_canvas_mask_component = components.declare_component(
    "canvas_mask",
    path=_COMPONENT_BUILD_DIR,
)

def st_canvas_mask(image_data_url, image_width, image_height, key=None):
    """
    Custom Streamlit component for canvas mask drawing
    
    Parameters:
    - image_data_url: Base64 encoded image data URL
    - image_width: Width of the image
    - image_height: Height of the image
    - key: Streamlit component key
    
    Returns:
    - mask_data_url: Base64 encoded mask image when confirmed
    """
    return _canvas_mask_component(
        imageUrl=image_data_url,
        imageWidth=image_width,
        imageHeight=image_height,
        key=key
    )