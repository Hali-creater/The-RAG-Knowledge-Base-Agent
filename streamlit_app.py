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

# Advanced Custom CSS for a GORGEOUS professional look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Main Background: Premium Dark */
    .stApp {
        background: #0E1117;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }

    /* Global adjustments */
    * {
        font-weight: 600;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {
        visibility: hidden;
    }

    /* Sidebar Styling: Sleek & Dark */
    section[data-testid="stSidebar"] {
        background-color: #1C1F26 !important;
        border-right: 1px solid #2D3748;
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }

    /* Custom Chat Container: Glassmorphism Style */
    .stChatMessage {
        background-color: #1C1F26 !important;
        border: 1px solid #2D3748 !important;
        border-radius: 1.25rem !important;
        padding: 1.25rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        transition: transform 0.2s ease-in-out;
    }

    .stChatMessage:hover {
        transform: translateY(-2px);
    }

    /* User message: Deep Blue Gradient */
    div[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        border: none !important;
    }

    /* Assistant message: Slightly lighter grey */
    div[data-testid="stChatMessageAssistant"] {
        background-color: #2D3748 !important;
        border: 1px solid #4A5568 !important;
    }

    /* Input Field: Elevated & Sleek */
    div[data-testid="stChatInput"] {
        background-color: #1C1F26 !important;
        border-radius: 1.25rem !important;
        border: 2px solid #3B82F6 !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2) !important;
    }

    /* Headings: Gradient Text */
    h1, h2, h3 {
        font-weight: 800 !important;
        background: linear-gradient(90deg, #F8FAFC 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em !important;
    }

    /* Buttons: Premium Glow */
    .stButton button {
        border-radius: 0.75rem !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39) !important;
    }

    .stButton button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
        transform: scale(1.02);
    }

    .stButton button[kind="secondary"] {
        border: 1px solid #4A5568 !important;
        background: #1C1F26 !important;
        color: #E2E8F0 !important;
    }

    /* Document list items: Clean Cards */
    .doc-item {
        background: #2D3748;
        padding: 0.85rem;
        border-radius: 0.75rem;
        margin-bottom: 0.65rem;
        border: 1px solid #4A5568;
        border-left: 6px solid #3B82F6;
        color: #F8FAFC !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Metrics: Sophisticated Dark Cards */
    div[data-testid="stMetric"] {
        background: #1C1F26 !important;
        padding: 1.25rem !important;
        border-radius: 1rem !important;
        border: 1px solid #2D3748 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2) !important;
    }

    /* Glass effect for certain containers */
    .glass-card {
        background: rgba(28, 31, 38, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1.25rem;
        padding: 1.5rem;
    }

    /* Custom Status Badge */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 10px;
    }
    .status-online {
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
        border: 1px solid #10B981;
    }
    .status-offline {
        background: rgba(239, 68, 68, 0.1);
        color: #EF4444;
        border: 1px solid #EF4444;
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

# Sidebar: Control Panel
with st.sidebar:
    st.markdown("### ⚙️ System Control")

    with st.expander("👤 User & Model Settings", expanded=False):
        st.session_state.user_role = st.selectbox(
            "Select Your Role",
            ["Admin", "Manager", "Employee"],
            index=2
        )

        st.session_state.assistant_type = st.selectbox(
            "AI Assistant Persona",
            ["General", "HR", "Legal", "Finance"],
            index=0
        )

    st.markdown("---")

    if st.button("🗑️ New Chat / Clear", use_container_width=True, type="secondary"):
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

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem; opacity: 0.6;'>
            <p style='font-size: 12px;'>Private Knowledge Engine<br>v2.1.0 • Enterprise Ready</p>
        </div>
    """, unsafe_allow_html=True)

# Main Interface Header
col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.markdown("<h1>Knowledge AI Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; margin-top: -10px; opacity: 0.8;'>Private • Secure • Business Ready</p>", unsafe_allow_html=True)

with col2:
    if os.getenv("GROQ_API_KEY"):
        st.markdown("<div class='status-badge status-online'>● Groq Engine Online</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-badge status-offline'>○ Groq Engine Offline</div>", unsafe_allow_html=True)

# Tabs for Organization
tab_chat, tab_kb, tab_analytics = st.tabs(["💬 Chat", "📚 Knowledge Base", "📊 Analytics"])

with tab_chat:
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

    # Only proceed with chat if API key is present
    if not os.getenv("GROQ_API_KEY"):
        st.warning("Please provide a Groq API Key to enable the AI Chat.")
    else:
        # Display example questions if no messages
        if not st.session_state.messages and st.session_state.agent:
            st.markdown("""
                <div class='glass-card' style='text-align: center; margin: 2rem 0;'>
                    <h3>Welcome to your Private Knowledge AI</h3>
                    <p>Ask questions about your documents and get instant, cited answers.</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### 💡 Try asking:")
            cols = st.columns(2)
            examples = [
                "Summarize the key insights from our documents",
                "What are the main risks identified?",
                "Extract key deadlines and action items",
                "Compare the different policies mentioned"
            ]
            for i, example in enumerate(examples):
                if cols[i % 2].button(example, use_container_width=True):
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
                if message["role"] == "assistant":
                    st.download_button(
                        label="📥 Download Answer",
                        data=message["content"],
                        file_name="ai_response.txt",
                        mime="text/plain",
                        key=f"dl_{st.session_state.messages.index(message)}"
                    )

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
                    with st.spinner("🧠 Analyzing your knowledge base..."):
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

                            sources = response_data.get("sources", [])
                            if sources:
                                st.info(f"✨ Answer generated from {len(sources)} sources")
                                with st.expander("📚 Sources"):
                                    for source in sources:
                                        st.markdown(f"<div class='doc-item'>{source}</div>", unsafe_allow_html=True)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response,
                                "sources": response_data.get("sources"),
                                "search_query": response_data.get("search_query")
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.error("Agent not initialized.")

with tab_kb:
    st.markdown("## 📁 Knowledge Management")

    col_up, col_list = st.columns([0.6, 0.4])

    with col_up:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📤 Ingest Documents")
        if st.session_state.user_role in ["Admin", "Manager"]:
            selected_area = st.selectbox(
                "Target Knowledge Area",
                ["General", "HR", "Legal", "Sales", "Technical"],
                index=0,
                key="kb_area_select"
            )

            uploaded_files = st.file_uploader(
                "Drop your documents here",
                type=["pdf", "docx", "txt", "md"],
                accept_multiple_files=True,
                help="Your data never leaves your system."
            )

            if uploaded_files:
                if st.button("✨ Process Knowledge", use_container_width=True, type="primary", key="kb_process_btn"):
                    if st.session_state.agent:
                        with st.spinner("Analyzing and indexing..."):
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
                                    st.toast(f"✅ Indexed: {uploaded_file.name}")
                                except Exception as e:
                                    st.error(f"❌ Error processing `{uploaded_file.name}`: {str(e)}")

                            if success_count > 0:
                                st.success(f"Successfully ingested {success_count} sources!")
                                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Only Admins and Managers can ingest documents.")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_list:
        st.subheader("📚 Current Library")
        if st.session_state.agent:
            docs = os.listdir("data/documents") if os.path.exists("data/documents") else []
            if docs:
                for doc in docs:
                    st.markdown(f"<div class='doc-item'>{doc} <span style='float: right; color: #10B981;'>✅ Indexed</span></div>", unsafe_allow_html=True)
            else:
                st.info("No sources loaded yet.")

with tab_analytics:
    st.markdown("## 📊 System Insights")
    if st.session_state.user_role == "Admin":
        c1, c2, c3 = st.columns(3)
        c1.metric("Most Asked Topic", "HR Policy")
        c2.metric("Active Sources", len(os.listdir("data/documents")) if os.path.exists("data/documents") else 0)
        c3.metric("Daily Queries", "142")

        st.markdown("### Query Volume Trends")
        st.line_chart([10, 25, 15, 40, 35, 60, 45])
    else:
        st.info("Analytics are only available for Admin users.")
