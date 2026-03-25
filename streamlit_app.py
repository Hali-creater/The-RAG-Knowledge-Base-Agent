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
    /* Main Background with soft gradient */
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }

    /* Global bold for clarity and punch */
    * {
        font-weight: 600 !important;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {
        visibility: hidden;
    }

    /* Sidebar Styling: Modern Minimalist */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }

    /* Custom Chat Container: Glassmorphism Style */
    .stChatMessage {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 1.25rem !important;
        padding: 1.25rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        transition: transform 0.2s ease-in-out;
    }

    .stChatMessage:hover {
        transform: translateY(-2px);
    }

    /* User message: Vibrant Blue Gradient */
    div[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: none !important;
        color: white !important;
    }

    div[data-testid="stChatMessageUser"] p,
    div[data-testid="stChatMessageUser"] span,
    div[data-testid="stChatMessageUser"] div {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Input Field: Elevated & Sleek */
    div[data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border-radius: 1rem !important;
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
    }

    /* Headings: Premium Typography */
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(90deg, #0f172a 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.05em !important;
    }

    /* Sidebar components: High-Contrast Buttons */
    .stButton button {
        border-radius: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: none !important;
        letter-spacing: 0.01em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0.5rem 1rem !important;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        border: none !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4) !important;
    }

    .stButton button[kind="secondary"] {
        border: 2px solid #e2e8f0 !important;
        background: white !important;
        color: #0f172a !important;
    }

    /* Document list items: Clean Cards */
    .doc-item {
        background: #ffffff;
        padding: 0.85rem;
        border-radius: 0.75rem;
        margin-bottom: 0.65rem;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #3b82f6;
        color: #1e293b !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* Metrics: Sophisticated Cards */
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 1rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Ensure directories exist
ensure_dirs()

# Initialize session state for RAG Agent
if "agent" not in st.session_state:
    st.session_state.agent = RAGAgent()
# Force re-initialization if signature changed or object is stale
elif not hasattr(st.session_state.agent, 'ingest_document') or st.session_state.agent.__class__.__name__ != 'RAGAgent':
    st.session_state.agent = RAGAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_role" not in st.session_state:
    st.session_state.user_role = "Employee"

if "knowledge_area" not in st.session_state:
    st.session_state.knowledge_area = "General"

if "assistant_type" not in st.session_state:
    st.session_state.assistant_type = "General"

# Sidebar
with st.sidebar:
    st.markdown("### 👤 User Settings")
    st.session_state.user_role = st.selectbox(
        "Select Your Role",
        ["Admin", "Manager", "Employee"],
        index=2,
        help="Roles control access to management and ingestion tools."
    )

    st.session_state.assistant_type = st.selectbox(
        "AI Assistant Persona",
        ["General", "HR", "Legal", "Finance"],
        index=0,
        help="Specialized personas for different tasks."
    )

    st.markdown("---")
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 2rem;'>
            <div style='background: #3b82f6; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 10px;'>
                <span style='font-size: 20px;'>🤖</span>
            </div>
            <h2 style='margin: 0; font-size: 24px;'>RAG Agent</h2>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📁 Knowledge Core")

    # Restrict ingestion to Admin and Manager
    if st.session_state.user_role in ["Admin", "Manager"]:
        selected_area = st.selectbox(
            "Target Knowledge Area",
            ["General", "HR", "Legal", "Sales", "Technical"],
            index=0
        )

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
                        success_count = 0
                        for uploaded_file in uploaded_files:
                            try:
                                safe_filename = os.path.basename(uploaded_file.name)
                                file_path = os.path.join("uploads", safe_filename)
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                                result = st.session_state.agent.ingest_document(file_path, knowledge_area=selected_area)
                                shutil.move(file_path, os.path.join("data/documents", safe_filename))
                                success_count += 1
                                st.info(f"📄 **{uploaded_file.name} Summary:** {result['summary']}")
                            except Exception as e:
                                st.error(f"❌ Error processing `{uploaded_file.name}`: {str(e)}")

                        if success_count > 0:
                            st.success(f"Successfully ingested {success_count} sources into {selected_area}!")
                else:
                    st.error("Agent not initialized.")
    else:
        st.warning("Only Admins and Managers can ingest documents.")

    st.markdown("---")
    st.subheader("📚 Loaded Sources")
    if st.session_state.agent:
        # Note: onprem lib may not have a direct way to get all sources easily
        # but we can check the documents directory
        docs = os.listdir("data/documents") if os.path.exists("data/documents") else []
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

    if st.session_state.user_role == "Admin":
        if st.button("🔥 Reset Knowledge Base", use_container_width=True, type="secondary"):
            if st.session_state.agent:
                if st.session_state.agent.clear_database():
                    st.success("Knowledge base cleared successfully!")
                    st.rerun()
                else:
                    st.error("Failed to clear knowledge base.")

# Main Interface
st.title("Intelligent Knowledge Assistant")

# Quick Connectivity Check
if os.getenv("GROQ_API_KEY"):
    st.markdown("<span style='color: #10b981; font-size: 12px; font-weight: 800;'>● Groq Engine Online</span>", unsafe_allow_html=True)
else:
    st.markdown("<span style='color: #ef4444; font-size: 12px; font-weight: 800;'>○ Groq Engine Offline</span>", unsafe_allow_html=True)

st.markdown("<p style='color: #0f172a; font-size: 18px; font-weight: 800;'>Query your documents with precision and context-aware AI.</p>", unsafe_allow_html=True)

# Dashboard Mockup
if st.session_state.user_role == "Admin":
    with st.expander("📊 Admin Analytics Dashboard", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Most Asked", "HR Policy")
        c2.metric("Most Used Doc", "legal_template.pdf")
        c3.metric("Daily Queries", "142")
        st.line_chart([10, 25, 15, 40, 35, 60, 45])

# Area Selection for Queries
st.session_state.knowledge_area = st.segmented_control(
    "Query Knowledge Area",
    ["General", "HR", "Legal", "Sales", "Technical"],
    default="General"
)

# Groq API Key Check
if not os.getenv("GROQ_API_KEY"):
    st.info("💡 **Welcome!** To get started, please provide your Groq API Key.")
    groq_key = st.text_input("Enter Groq API Key", type="password")
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
        st.success("API Key set successfully!")
        st.rerun()
    st.stop()

# Display example questions if no messages
if not st.session_state.messages and st.session_state.agent:
    st.markdown("### 💡 Suggested Questions")
    cols = st.columns(2)
    examples = [
        "What are the key findings in the uploaded documents?",
        "Can you summarize the main points of the latest file?",
        "Are there any specific dates or deadlines mentioned?",
        "What is the overall tone of these documents?"
    ]
    for i, example in enumerate(examples):
        if cols[i % 2].button(example, use_container_width=True):
            # We'll handle this in the chat input logic by setting a temporary session state
            st.session_state.temp_prompt = example
            st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("search_query"):
            st.caption(f"🔍 **Standalone Search Query:** _{message['search_query']}_")
        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(f"<div class='doc-item'>{source}</div>", unsafe_allow_html=True)

# Chat input
prompt = st.chat_input("Ask a question about your knowledge core...")
if "temp_prompt" in st.session_state:
    prompt = st.session_state.temp_prompt
    del st.session_state.temp_prompt

if prompt:
    if st.session_state.agent:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"Assistant ({st.session_state.knowledge_area}) is thinking..."):
                try:
                    response_data = st.session_state.agent.answer_question(
                        prompt,
                        knowledge_area=st.session_state.knowledge_area,
                        assistant_type=st.session_state.assistant_type
                    )
                    full_response = response_data["answer"]
                    st.markdown(full_response)

                    if response_data.get("search_query"):
                        st.caption(f"🔍 **Standalone Search Query:** _{response_data['search_query']}_")

                    if response_data.get("sources"):
                        with st.expander("📚 Sources"):
                            for source in response_data["sources"]:
                                st.markdown(f"<div class='doc-item'>{source}</div>", unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "sources": response_data.get("sources"),
                        "search_query": response_data.get("search_query")
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.error("Agent not initialized.")
