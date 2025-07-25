import streamlit as st
import requests
import json

st.title("Inpainting Application")

API_URL = "http://localhost:8000"

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# if uploaded_file is not None:
#     st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

#     files = {"file": uploaded_file.getvalue()}
#     response = requests.post(f"{API_URL}/process", files=files)

#     if response.status_code == 200:
#         st.success("Image processed successfully!")
#         st.image(response.content, caption='Processed Image', use_column_width=True)
#     else:
#         st.error("Error processing image.")

def invert_image(image):
    files = {
        "image": (
            image.name,
            image.getvalue(),
            image.type
        )
    }
    invert_response = requests.post(f"{API_URL}/invertimage", files=files)
    return invert_response

def blur_image(image):
    files = {
        "image": (
            image.name,
            image.getvalue(),
            image.type
        )
    }
    blur_response = requests.post(f"{API_URL}/blurimage", files=files)
    return blur_response

def black_and_white_image(image):
    files = {
        "image": (
            image.name,
            image.getvalue(),
            image.type
        )
    }
    bw_response = requests.post(f"{API_URL}/blackandwhite", files=files)
    return bw_response
        
if uploaded_file is not None:
    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
    files = {
        "image": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }
    obj_detect_response = requests.post(f"{API_URL}/detectobjects", files=files)
    with st.spinner("Detecting objects..."):
        while obj_detect_response.status_code == 202:
            obj_detect_response = requests.post(f"{API_URL}/detectobjects", files=files)
        if obj_detect_response.status_code == 200:
            st.success("Objects detected successfully!")
            st.image(obj_detect_response.content, caption='Detected Objects', use_column_width=True)
        else:
            st.error("Error detecting objects.")

    if obj_detect_response.status_code == 200:
        detected_objects = []
        try:
            detected_objects = obj_detect_response.headers.get("X-Objects")
            if detected_objects:
                detected_objects = json.loads(detected_objects)
            else:
                detected_objects = []
        except Exception:
            detected_objects = []
        selected_objects = st.multiselect(
            "Select objects to inpaint:",
            detected_objects
        )
    
    if st.button("Inpaint Image"):
        if selected_objects:
            st.subheader("Inpainting Image")
            inpaint_response = requests.post(
                f"{API_URL}/inpaint",
                files=files,
                data={"object": json.dumps(selected_objects)}
            )
            if inpaint_response.status_code == 200:
                st.success("Image inpainted successfully!")
                st.image(inpaint_response.content, caption='Inpainted Image', use_column_width=True)
            else:
                st.error("Error inpainting image.")
        else:
            st.warning("Please select at least one object to inpaint.")
    
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
        

