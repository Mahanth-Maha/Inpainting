import streamlit as st
import requests

st.title("Inpainting Application")

API_URL = "http://localhost:8000/api"

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

    files = {"file": uploaded_file.getvalue()}
    response = requests.post(f"{API_URL}/process", files=files)

    if response.status_code == 200:
        st.success("Image processed successfully!")
        st.image(response.content, caption='Processed Image', use_column_width=True)
    else:
        st.error("Error processing image.")