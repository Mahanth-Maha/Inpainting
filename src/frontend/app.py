import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Image Inpainting",
    page_icon="🎨",
    # layout="wide"
)

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #4F8BF9;
        color: #4F8BF9;
        background-color: transparent;
    }
    .stButton>button:hover {
        border-color: #FFFFFF;
        color: #FFFFFF;
        background-color: #4F8BF9;
    }
    .centered-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stSpinner > div > div {
        border-top-color: #4F8BF9;
    }
</style>
""", unsafe_allow_html=True)


API_URL = "http://localhost:8000/v1"

if 'step' not in st.session_state:
    st.session_state.step = "upload"
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'detected_objects' not in st.session_state:
    st.session_state.detected_objects = []
if 'inpainted_image' not in st.session_state:
    st.session_state.inpainted_image = None
if 'error' not in st.session_state:
    st.session_state.error = None


def restart_app():
    """Resets the entire session state to start over."""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

def try_again():
    """Resets the inpainting and error state to allow another attempt."""
    st.session_state.step = "select_objects"
    st.session_state.inpainted_image = None
    st.session_state.error = None
    st.rerun()

st.title("Image Inpainting")

if st.session_state.step == "upload":
    st.session_state.uploaded_file = st.file_uploader(
        "Choose an image to get started...",
        type=["jpg", "jpeg", "png"]
    )
    if st.session_state.uploaded_file:
        st.session_state.step = "detect_objects"
        st.rerun()

if st.session_state.step in ["detect_objects", "select_objects", "inpaint"]:
    st.image(st.session_state.uploaded_file, caption='Uploaded Image', use_container_width=True)

    if st.session_state.step == "detect_objects":
        if st.button("Detect Objects"):
            with st.spinner("Analyzing image to find objects... This may take a moment."):
                try:
                    files = {
                        "image": (
                            st.session_state.uploaded_file.name,
                            st.session_state.uploaded_file.getvalue(),
                            st.session_state.uploaded_file.type
                        )
                    }
                    # We make the request only ONCE.
                    response = requests.post(f"{API_URL}/detectobjects", files=files)

                    if response.status_code == 200:
                        if 'error' in response.json():
                            st.session_state.error = response.json()['error']
                            st.rerun()
                        else :
                            st.success("Objects detected successfully!")
                            # The response body itself contains the detected objects
                            st.session_state.detected_objects = response.json().get("X-Objects", [])
                            st.session_state.step = "select_objects"
                            st.session_state.error = None
                            st.rerun()
                    else:
                        st.session_state.error = f"Error detecting objects (Status: {response.status_code}). Please try again."
                        st.rerun()
                except requests.exceptions.RequestException as e:
                    st.session_state.error = f"Failed to connect to the server: {e}"
                    st.rerun()

    if st.session_state.error:
        st.error(st.session_state.error)
        if st.button("Restart"):
            restart_app()

if st.session_state.step == "select_objects":
    st.subheader("Select Objects to Inpaint")
    if not st.session_state.detected_objects:
        st.warning("No objects were detected in the image. You can try restarting with a different image.")
    else:
        selected_objects = st.multiselect(
            "Choose the objects you want to remove from the image:",
            st.session_state.detected_objects
        )

        if st.button("Inpaint Image"):
            if selected_objects:
                with st.spinner("Inpainting the image... Please wait."):
                    try:
                        files = {
                            "image": (
                                st.session_state.uploaded_file.name,
                                st.session_state.uploaded_file.getvalue(),
                                st.session_state.uploaded_file.type
                            )
                        }
                        data = {"object": json.dumps(selected_objects)}
                        response = requests.post(f"{API_URL}/inpaint", files=files, data=data)

                        if response.status_code == 200:
                            st.session_state.inpainted_image = response.content
                            st.session_state.step = "inpaint"
                            st.session_state.error = None
                            st.rerun()
                        else:
                            st.session_state.error = f"Error inpainting image (Status: {response.status_code})."
                            st.rerun()

                    except requests.exceptions.RequestException as e:
                        st.session_state.error = f"Failed to connect to the server: {e}"
                        st.rerun()
            else:
                st.warning("Please select at least one object to inpaint.")

    if st.session_state.error:
        st.error(st.session_state.error)

    if st.button("Restart App"):
        restart_app()


if st.session_state.step == "inpaint":
    st.subheader("Inpainting Result")
    if st.session_state.inpainted_image:
        st.success("Image inpainted successfully!")
        st.image(st.session_state.inpainted_image, caption='Inpainted Image', use_container_width=True)
        st.download_button(
            label="Download Inpainted Image",
            data=st.session_state.inpainted_image,
            file_name=f"{st.session_state.uploaded_file.name.replace('.', '_')}_inpainted.png",
            mime="image/png"
        )
    else:
        st.error("Something went wrong during inpainting. Please try again.")

    st.write('<div class="centered-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try Again", key="try_again_button"):
            try_again()
    with col2:
        if st.button("Restart", key="restart_button"):
            restart_app()
    st.write('</div>', unsafe_allow_html=True)


# uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# def invert_image(image):
#     files = {
#         "image": (
#             image.name,
#             image.getvalue(),
#             image.type
#         )
#     }
#     invert_response = requests.post(f"{API_URL}/invertimage", files=files)
#     return invert_response

# def blur_image(image):
#     files = {
#         "image": (
#             image.name,
#             image.getvalue(),
#             image.type
#         )
#     }
#     blur_response = requests.post(f"{API_URL}/blurimage", files=files)
#     return blur_response

# def black_and_white_image(image):
#     files = {
#         "image": (
#             image.name,
#             image.getvalue(),
#             image.type
#         )
#     }
#     bw_response = requests.post(f"{API_URL}/blackandwhite", files=files)
#     return bw_response


# if uploaded_file is not None:
#     st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
#     files = {
#         "image": (
#             uploaded_file.name,
#             uploaded_file.getvalue(),
#             uploaded_file.type
#         )
#     }
#     obj_detect_response = requests.post(f"{API_URL}/detectobjects", files=files)
#     with st.spinner("Detecting objects..."):
#         while obj_detect_response.status_code == 202:
#             obj_detect_response = requests.post(f"{API_URL}/detectobjects", files=files)
#         if obj_detect_response.status_code == 200:
#             st.success("Objects detected successfully!")
#             # st.image(obj_detect_response.content, caption='Detected Objects', use_column_width=True)
#         else:
#             st.error("Error detecting objects.")

#     if obj_detect_response.status_code == 200:
#         detected_objects = []
#         try:
#             detected_objects = obj_detect_response.json().get("X-Objects")
#             # if detected_objects:
#             #     detected_objects = json.loads(detected_objects)
#             # else:
#             #     detected_objects = []
#         except Exception:
#             detected_objects = []
#         selected_objects = st.multiselect(
#             "Select objects to inpaint:",
#             detected_objects
#         )
    
#     if st.button("Inpaint Image"):
#         if selected_objects:
#             st.subheader("Inpainting Image")
#             inpaint_response = requests.post(
#                 f"{API_URL}/inpaint",
#                 files=files,
#                 data={"object": json.dumps(selected_objects)}
#             )
#             if inpaint_response.status_code == 200:
#                 st.success("Image inpainted successfully!")
#                 st.image(inpaint_response.content, caption='Inpainted Image', use_column_width=True)
#             else:
#                 st.error("Error inpainting image.")
#         else:
#             st.warning("Please select at least one object to inpaint.")
    
    # if st.button("Invert Image"):
    #     st.subheader("Inverting Image")
    #     invert_response = invert_image(uploaded_file)
    #     if invert_response.status_code == 200:
    #         st.success("Image inverted successfully!")
    #         st.image(invert_response.content, caption='Inverted Image', use_column_width=True)
    #     else:
    #         st.info("response status code: " + str(invert_response.status_code))
    #         st.error("Error inverting image.")
    # if st.button("Blur Image"):
    #     st.subheader("Blurring Image")
    #     blur_response = blur_image(uploaded_file)
    #     if blur_response.status_code == 200:
    #         st.success("Image blurred successfully!")
    #         st.image(blur_response.content, caption='Blurred Image', use_column_width=True)
    #     else:
    #         st.info("response status code: " + str(blur_response.status_code))
    #         st.error("Error blurring image.")
    # if st.button("Black and White Image"):
    #     st.subheader("Converting to Black and White")
    #     bw_response = black_and_white_image(uploaded_file)
    #     if bw_response.status_code == 200:
    #         st.success("Image converted to black and white successfully!")
    #         st.image(bw_response.content, caption='Black and White Image', use_column_width=True)
    #     else:
    #         st.info("response status code: " + str(bw_response.status_code))
    #         st.error("Error converting image to black and white.")
        

