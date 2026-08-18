import streamlit as st

def render_history_download_ui():
    if st.session_state.get("chat_history"):
        st.header("Download Chat History")
        chat_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history])
        st.download_button("Download Chat History", chat_history, file_name="chat_history.txt", mime="text/plain")

        