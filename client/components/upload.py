import streamlit as st
from utils.api import upload_pdf_api

def render_upload_ui():
    st.sidebar.header("Upload PDF")
    uploaded_files = st.sidebar.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    if st.sidebar.button("Upload") and uploaded_files:
        response = upload_pdf_api(uploaded_files)
        if response.status_code == 200:
            st.sidebar.success("PDF(s) uploaded successfully!")
        else:
            st.sidebar.error("Failed to upload PDF(s). Please try again.")