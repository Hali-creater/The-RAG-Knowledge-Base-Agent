import streamlit as st
import os
import shutil
from src.rag_agent import RAGAgent
from src.utils import ensure_dirs, allowed_file

# Set page config
st.set_page_config(
    page_title="RAG Intelligence Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stSidebar {
        background-color: #1e293b;
    }
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #f8fafc;
    }
    h1 {
        color: #1e293b;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# Ensure directories exist
ensure_dirs()

# Initialize session state for RAG Agent
if "agent" not in st.session_state:
    # Try to get API key from st.secrets, then env
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            api_key = None

    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.session_state.agent = RAGAgent()
    else:
        st.session_state.agent = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("🤖 RAG Agent")
    st.markdown("---")

    st.subheader("📁 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Process Documents", use_container_width=True, type="primary"):
            if st.session_state.agent:
                with st.spinner("Processing documents..."):
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join("uploads", uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        st.session_state.agent.ingest_document(file_path)
                        # Move to permanent storage
                        shutil.move(file_path, os.path.join("data/documents", uploaded_file.name))
                    st.success(f"Processed {len(uploaded_files)} documents!")
            else:
                st.error("OpenAI API Key not found. Please set it in secrets.")

    st.markdown("---")
    st.subheader("📜 Loaded Documents")
    if st.session_state.agent:
        docs = st.session_state.agent.vector_store.get_all_sources()
        for doc in docs:
            st.markdown(f"- {doc}")

    if st.button("Clear History", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.agent:
            st.session_state.agent.memory_manager.clear_memory()
        st.rerun()

# Main Interface
st.title("Intelligent Knowledge Assistant")
st.markdown("Ask anything based on your uploaded documents.")

# API Key check
if st.session_state.agent is None:
    st.warning("⚠️ Please provide an OpenAI API Key to start. You can set it in `.streamlit/secrets.toml` or as an environment variable.")
    api_key_input = st.text_input("Enter OpenAI API Key", type="password")
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
        st.session_state.agent = RAGAgent()
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is your question?"):
    if st.session_state.agent:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = st.session_state.agent.answer_question(prompt)
                full_response = response_data["answer"]

                # Format sources if available
                if response_data.get("sources"):
                    sources_str = ", ".join(response_data["sources"])
                    # We don't append to content if it's already in the answer by LLM
                    # but let's ensure it's displayed nicely.
                    # The prompt.md said cite sources.

                st.markdown(full_response)

        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.error("Agent not initialized. Please provide an API key.")
