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

    /* Main Background: Premium Light */
    .stApp {
        background: #F8FAFC;
        color: #1E293B;
        font-family: 'Inter', sans-serif;
    }

    /* Global adjustments: Bolder text for maximum clarity */
    * {
        font-weight: 700 !important;
    }

    /* Hide Streamlit Header/Footer */
    header, footer {
        visibility: hidden;
    }

    /* Sidebar Styling: Crisp & Modern */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0F172A !important;
        font-weight: 800 !important;
    }

    /* Custom Chat Container: Clean White Card */
    .stChatMessage {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 1.25rem !important;
        padding: 1.25rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease-in-out;
    }

    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }

    /* User message: Vibrant Blue Gradient */
    div[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stChatMessageUser"] p,
    div[data-testid="stChatMessageUser"] span,
    div[data-testid="stChatMessageUser"] div {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Assistant message: Soft White Card */
    div[data-testid="stChatMessageAssistant"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* Input Field: Elevated & Bold */
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border-radius: 1.25rem !important;
        border: 2px solid #2563EB !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.1) !important;
    }

    /* Headings: High-Contrast Dark */
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.02em !important;
    }

    /* Buttons: Premium Blue */
    .stButton button {
        border-radius: 0.75rem !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }

    .stButton button[kind="primary"]:hover {
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4) !important;
        transform: scale(1.02);
    }

    .stButton button[kind="secondary"] {
        border: 2px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
    }

    /* Document list items: Clean White Cards */
    .doc-item {
        background: #FFFFFF;
        padding: 0.85rem;
        border-radius: 0.75rem;
        margin-bottom: 0.65rem;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #2563EB;
        color: #1E293B !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* Metrics: Sophisticated White Cards */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        padding: 1.25rem !important;
        border-radius: 1rem !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    /* Glass effect for light mode */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.5);
        border-radius: 1.25rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
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

    if st.session_state.user_role in ["Admin", "Manager"]:
        with st.expander("📁 Knowledge Ingestion", expanded=False):
            selected_area = st.selectbox(
                "Target Area",
                ["General", "HR", "Legal", "Sales", "Technical"],
                index=0,
                key="side_kb_area"
            )

            uploaded_files = st.file_uploader(
                "Drop documents here",
                type=["pdf", "docx", "txt", "md"],
                accept_multiple_files=True,
                key="side_uploader"
            )

            if uploaded_files:
                if st.button("✨ Process Knowledge", use_container_width=True, type="primary", key="side_process_btn"):
                    if st.session_state.agent:
                        with st.spinner("Analyzing..."):
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
                                    st.error(f"❌ Error: {str(e)}")

                            if success_count > 0:
                                st.session_state.ingestion_feedback = f"✅ Successfully ingested {success_count} sources!"
                                st.rerun()

            if "ingestion_feedback" in st.session_state:
                st.success(st.session_state.ingestion_feedback)
                # Clear after showing once if desired, but user asked for a note under button

    if st.session_state.user_role == "Admin":
        if st.button("🔥 Reset Knowledge Base", use_container_width=True, type="secondary"):
            if st.session_state.agent:
                if st.session_state.agent.clear_database():
                    st.success("Knowledge base cleared successfully!")
                    st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <p style='font-size: 12px; color: #64748B; font-weight: 700;'>Private Knowledge Engine<br>v2.1.0 • Enterprise Ready</p>
        </div>
    """, unsafe_allow_html=True)

# Main Interface Header
col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.markdown("<h1>Knowledge AI Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; margin-top: -10px; color: #475569; font-weight: 800;'>Private • Secure • Business Ready</p>", unsafe_allow_html=True)

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

    st.subheader("📚 Current Library")
    if st.session_state.agent:
        docs = os.listdir("data/documents") if os.path.exists("data/documents") else []
        if docs:
            # Grid layout for library
            cols = st.columns(3)
            for i, doc in enumerate(docs):
                with cols[i % 3]:
                    st.markdown(f"<div class='doc-item'>{doc} <br><span style='font-size: 10px; color: #10B981;'>✅ Indexed</span></div>", unsafe_allow_html=True)
        else:
            st.info("No sources loaded yet. Use the sidebar to upload documents.")

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
