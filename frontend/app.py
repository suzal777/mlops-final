import streamlit as st
import requests
import os

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="RAG Microservice",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 RAG Microservice - Document Q&A System")
st.markdown("---")

# Sidebar for file upload
with st.sidebar:
    st.header("�� Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a document (PDF or TXT)",
        type=["pdf", "txt"],
        help="Upload a document to index it in the vector database"
    )
    
    if st.button("Index Document", type="primary", disabled=uploaded_file is None):
        if uploaded_file:
            with st.spinner("Indexing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{API_URL}/index", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.info(f"Indexed {result['chunks_indexed']} chunks")
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### System Status")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            st.success("🟢 Backend Online")
        else:
            st.error("🔴 Backend Offline")
    except:
        st.error("🔴 Cannot connect to backend")

# Main chat interface
st.header("💬 Chat Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for idx, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {idx}** (Score: {source['score']:.4f})")
                    st.markdown(f"*From: {source['source']}*")
                    st.text(source['text'])
                    st.markdown("---")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"query": prompt, "max_length": 512}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    sources = result["sources"]
                    
                    st.markdown(answer)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                    # Display sources
                    if sources:
                        with st.expander("📚 View Sources"):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"**Source {idx}** (Score: {source['score']:.4f})")
                                st.markdown(f"*From: {source['source']}*")
                                st.text(source['text'])
                                st.markdown("---")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# Clear chat button
if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
