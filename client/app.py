import streamlit as st
from components.upload import render_upload_ui
from components.chatUI import render_chat_ui
from components.history_dload import render_history_download_ui


st.set_page_config(page_title="Ai Sensei", layout="wide")
st.title("Ai Sensei - Your Personal AI Assistant")
render_upload_ui()
render_chat_ui()
render_history_download_ui()