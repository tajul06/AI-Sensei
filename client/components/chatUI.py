import streamlit as st
from utils.api import ask_question_api, upload_pdf_api

def render_chat_ui():
    st.header("Chat with Ai Sensei")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # render chat history
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # user input
    user_input = st.chat_input("Ask a question or upload a PDF...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        response = ask_question_api(user_input)
        if response.status_code == 200:
            data =response.json() 
            answer=data["result"]
            sources = [doc["metadata"].get("source", "unknown") for doc in data.get("source_documents", [])]
            st.chat_message("assistant").markdown(answer)
            if sources:
                st.markdown(" ❔ **Sources:**")
                for source in sources:
                    st.markdown(f"- {source}")
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
        else:
            st.chat_message("assistant").markdown("Sorry, I couldn't process your question at the moment.")
            st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I couldn't process your question at the moment."})