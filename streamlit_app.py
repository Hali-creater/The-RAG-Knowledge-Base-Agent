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

# Advanced Custom CSS for a professional look
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {
        visibility: hidden;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }

    /* Custom Chat Container */
    .stChatMessage {
        background-color: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 1.5rem !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }

    /* User message specific style */
    div[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        border: none !important;
    }

    div[data-testid="stChatMessageUser"] p {
        color: white !important;
    }

    /* Input Field */
    div[data-testid="stChatInput"] {
        background-color: #1e293b !important;
        border-radius: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Headings */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        color: #ffffff !important;
    }

    /* Sidebar components */
    .stButton button {
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }

    /* Document list items */
    .doc-item {
        background: rgba(255, 255, 255, 0.05);
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Ensure directories exist
ensure_dirs()

# Initialize session state for RAG Agent
if "agent" not in st.session_state:
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
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 2rem;'>
            <div style='background: #3b82f6; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 10px;'>
                <span style='font-size: 20px;'>🤖</span>
            </div>
            <h2 style='margin: 0; font-size: 24px;'>RAG Agent</h2>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📁 Knowledge Core")
    uploaded_files = st.file_uploader(
        "Upload proprietary documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Upload files to extend the agent's knowledge base."
    )

    if uploaded_files:
        if st.button("✨ Process Knowledge", use_container_width=True, type="primary"):
            if st.session_state.agent:
                with st.spinner("Analyzing and chunking..."):
                    for uploaded_file in uploaded_files:
                        safe_filename = os.path.basename(uploaded_file.name)
                        file_path = os.path.join("uploads", safe_filename)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        st.session_state.agent.ingest_document(file_path)
                        shutil.move(file_path, os.path.join("data/documents", safe_filename))
                    st.success(f"Successfully ingested {len(uploaded_files)} sources!")
            else:
                st.error("API Key required.")

    st.markdown("---")
    st.subheader("📚 Loaded Sources")
    if st.session_state.agent:
        docs = st.session_state.agent.vector_store.get_all_sources()
        if docs:
            for doc in docs:
                st.markdown(f"<div class='doc-item'>{doc}</div>", unsafe_allow_html=True)
        else:
            st.info("No sources loaded yet.")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.agent:
            st.session_state.agent.memory_manager.clear_memory()
        st.rerun()

# Main Interface
st.title("Intelligent Knowledge Assistant")
st.markdown("<p style='color: #94a3b8; font-size: 18px;'>Query your documents with precision and context-aware AI.</p>", unsafe_allow_html=True)

# API Key check
if st.session_state.agent is None:
    with st.container():
        st.info("💡 **Welcome!** To get started, please provide an OpenAI API Key.")
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
if prompt := st.chat_input("Ask a question about your knowledge core..."):
    if st.session_state.agent:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving and generating..."):
                response_data = st.session_state.agent.answer_question(prompt)
                full_response = response_data["answer"]
                st.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.error("Agent not initialized.")
