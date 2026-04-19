import streamlit as st
import os
import shutil
import time
from streamlit_javascript import st_javascript
from src.rag_agent import RAGAgent
from src.connectors import ConnectorManager
from src.utils import ensure_dirs, allowed_file, ROLE_PERMISSIONS
from src.audit_logger import get_audit_logs
from src.translations import TRANSLATIONS

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

    /* Refined Visibility: Hide only unnecessary Streamlit elements */
    footer {
        visibility: hidden;
    }

    /* Hide Deploy button and Main Menu but keep sidebar toggle */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    header[data-testid="stHeader"] > div:nth-child(n+2) {
        display: none !important;
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

    /* Trust Indicator Bar */
    .trust-bar-container {
        width: 100%;
        background-color: #E2E8F0;
        border-radius: 10px;
        height: 6px;
        margin-top: 5px;
        margin-bottom: 10px;
        overflow: hidden;
    }
    .trust-bar-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease-in-out;
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

if "language" not in st.session_state:
    # Auto-detection logic
    user_lang = st_javascript("""window.navigator.language""")
    if user_lang:
        if user_lang.startswith("de"):
            st.session_state.language = "🇩🇪 German"
        elif user_lang.startswith("fr"):
            st.session_state.language = "🇫🇷 French"
        else:
            st.session_state.language = "🇺🇸 English"
    else:
        st.session_state.language = "🇺🇸 English"

# Sidebar: Control Panel
with st.sidebar:
    st.markdown("### ⚙️ System Control")

    # Language Selector
    selected_lang = st.selectbox(
        "🌐 Language",
        options=list(TRANSLATIONS.keys()),
        index=list(TRANSLATIONS.keys()).index(st.session_state.language)
    )
    st.session_state.language = selected_lang
    t = TRANSLATIONS[st.session_state.language]

    with st.expander(t["sidebar_settings"], expanded=False):
        st.session_state.user_role = st.selectbox(
            t["sidebar_role"],
            ["Admin", "Manager", "Employee"],
            index=2
        )

        persona_options = ["General", "HR", "Legal", "Finance", "Comparative"]
        # Find index if already in session_state, else 0
        current_persona = st.session_state.get("assistant_type", "General")
        p_idx = persona_options.index(current_persona) if current_persona in persona_options else 0

        st.session_state.assistant_type = st.selectbox(
            t["sidebar_persona"],
            persona_options,
            index=p_idx
        )

        selected_model = st.selectbox(
            t["sidebar_model"],
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0
        )
        if st.session_state.agent.model_name != selected_model:
             st.session_state.agent.model_name = selected_model
             st.session_state.agent._llm = None # Force re-init

    st.markdown("---")

    if st.button(t["sidebar_new_chat"], use_container_width=True, type="secondary"):
        st.session_state.messages = []
        if st.session_state.agent:
            st.session_state.agent.memory_manager.clear_memory()
        st.rerun()

    # Chat Memory Search
    st.markdown("---")
    chat_search = st.text_input(t["sidebar_search_chats"], placeholder="...")

    if st.session_state.user_role in ["Admin", "Manager"]:
        with st.expander(t["sidebar_ingestion"], expanded=False):
            selected_area = st.selectbox(
                t["sidebar_target_area"],
                ROLE_PERMISSIONS.get(st.session_state.user_role, ["General"]),
                index=0,
                key="side_kb_area"
            )

            st.markdown("---")
            st.markdown(f"**{t['sidebar_connectors']}**")

            with st.expander(t["connector_cloud_title"], expanded=False):
                conn_type = st.radio(t["connector_provider"], ["GDrive", "OneDrive", "SharePoint"])

                if conn_type == "GDrive":
                    creds_path = st.text_input(t["connector_gdrive_creds"], placeholder="credentials.json", key="gdrive_creds_path")
                    token_path = st.text_input(t["connector_gdrive_token"], placeholder="token.json", key="gdrive_token_path")

                    is_connected = os.path.exists(token_path if token_path else "token.json")
                    status_color = "green" if is_connected else "red"
                    status_text = t["connector_status_connected"] if is_connected else t["connector_status_disconnected"]
                    st.markdown(f"Status: <span style='color:{status_color}'>{status_text}</span>", unsafe_allow_html=True)

                    if st.button(t["connector_gdrive_btn"], use_container_width=True):
                        try:
                            auth_url = ConnectorManager.get_gdrive_auth_url(creds_path if creds_path else "credentials.json")
                            st.markdown(f"1. [Click here to authorize]({auth_url})")
                            st.info("2. Copy the code and paste it below.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    auth_code = st.text_input(t["connector_gdrive_code_label"], type="password")
                    if auth_code:
                        if st.button("Confirm Code"):
                            try:
                                ConnectorManager.exchange_gdrive_code(creds_path if creds_path else "credentials.json", auth_code, token_path if token_path else "token.json")
                                st.success("Connected successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                    st.markdown("---")
                    gdrive_input = st.text_input(t["connector_gdrive_id"])
                    if st.button(t["connector_process"], key="btn_gdrive"):
                        with st.spinner(t["analyzing"]):
                            try:
                                params = {
                                    "input_id": gdrive_input,
                                    "token_path": token_path if token_path else "token.json"
                                }
                                res = st.session_state.agent.ingest_from_connector("GDrive", params, knowledge_area=selected_area)
                                if res['chunks'] > 0:
                                    st.success(f"Ingested {res['chunks']} chunks!")
                                else:
                                    st.warning("No document content found. Please check permissions or the link.")
                            except Exception as e:
                                if "metadata.google.internal" in str(e):
                                    st.error("Authentication Error: Google Cloud metadata server unavailable. Please provide 'credentials.json' or a Service Account key for local authentication.")
                                else:
                                    st.error(f"Error: {e}")

                elif conn_type == "OneDrive":
                    ms_client_id = st.text_input("Microsoft Client ID", value=os.getenv("MS_CLIENT_ID", ""), type="password")
                    ms_client_secret = st.text_input("Microsoft Client Secret", value=os.getenv("MS_CLIENT_SECRET", ""), type="password")

                    is_ms_connected = os.path.exists("o365_token.txt")
                    ms_status_color = "green" if is_ms_connected else "red"
                    ms_status_text = t["connector_status_connected"] if is_ms_connected else t["connector_status_disconnected"]
                    st.markdown(f"Status: <span style='color:{ms_status_color}'>{ms_status_text}</span>", unsafe_allow_html=True)

                    if st.button(t["connector_ms_btn"], use_container_width=True):
                        try:
                            auth_url = ConnectorManager.get_ms_auth_url(ms_client_id, ms_client_secret)
                            st.markdown(f"1. [Click here to authorize]({auth_url})")
                            st.info("2. After authorizing, you will be redirected to a blank page. Copy the FULL URL of that page and paste it below.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    ms_code_url = st.text_input(t["connector_ms_url_label"])
                    if ms_code_url:
                        if st.button("Confirm Microsoft Connection"):
                            try:
                                if ConnectorManager.exchange_ms_code(ms_client_id, ms_client_secret, ms_code_url):
                                    st.success("Microsoft Connected!")
                                    st.rerun()
                                else:
                                    st.error("Failed to authenticate.")
                            except Exception as e:
                                st.error(f"Error: {e}")

                    st.markdown("---")
                    drive_id = st.text_input(t["connector_onedrive_id"])
                    if st.button(t["connector_process"], key="btn_onedrive"):
                         with st.spinner(t["analyzing"]):
                            try:
                                params = {
                                    "drive_id": drive_id,
                                    "ms_client_id": ms_client_id,
                                    "ms_client_secret": ms_client_secret
                                }
                                res = st.session_state.agent.ingest_from_connector("OneDrive", params, knowledge_area=selected_area)
                                if res['chunks'] > 0:
                                    st.success(f"Ingested {res['chunks']} chunks!")
                                else:
                                    st.warning("No document content found. Please check permissions or ID.")
                            except Exception as e:
                                st.error(f"Error: {e}")

                elif conn_type == "SharePoint":
                    ms_client_id = st.text_input("Microsoft Client ID", value=os.getenv("MS_CLIENT_ID", ""), type="password")
                    ms_client_secret = st.text_input("Microsoft Client Secret", value=os.getenv("MS_CLIENT_SECRET", ""), type="password")

                    is_ms_connected = os.path.exists("o365_token.txt")
                    ms_status_color = "green" if is_ms_connected else "red"
                    ms_status_text = t["connector_status_connected"] if is_ms_connected else t["connector_status_disconnected"]
                    st.markdown(f"Status: <span style='color:{ms_status_color}'>{ms_status_text}</span>", unsafe_allow_html=True)

                    # (Same logic as OneDrive for auth)
                    if st.button(t["connector_ms_btn"], key="btn_ms_auth_sp", use_container_width=True):
                        try:
                            auth_url = ConnectorManager.get_ms_auth_url(ms_client_id, ms_client_secret)
                            st.markdown(f"1. [Click here to authorize]({auth_url})")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    st.markdown("---")
                    site_id = st.text_input(t["connector_sharepoint_id"])
                    if st.button(t["connector_process"], key="btn_sharepoint"):
                         with st.spinner(t["analyzing"]):
                            try:
                                params = {
                                    "site_id": site_id,
                                    "ms_client_id": ms_client_id,
                                    "ms_client_secret": ms_client_secret
                                }
                                res = st.session_state.agent.ingest_from_connector("SharePoint", params, knowledge_area=selected_area)
                                if res['chunks'] > 0:
                                    st.success(f"Ingested {res['chunks']} chunks!")
                                else:
                                    st.warning("No document content found. Please check permissions or ID.")
                            except Exception as e:
                                st.error(f"Error: {e}")

            uploaded_files = st.file_uploader(
                t["sidebar_drop"],
                type=["pdf", "docx", "txt", "md"],
                accept_multiple_files=True,
                key="side_uploader"
            )

            if uploaded_files:
                if st.button(t["sidebar_process"], use_container_width=True, type="primary", key="side_process_btn"):
                    if st.session_state.agent:
                        with st.spinner("Analyzing..."):
                            success_count = 0
                            for uploaded_file in uploaded_files:
                                try:
                                    # Use the actual filename from the uploaded object
                                    original_name = uploaded_file.name
                                    safe_filename = os.path.basename(original_name)
                                    file_path = os.path.join("uploads", safe_filename)

                                    # Ensure uploads directory exists
                                    os.makedirs("uploads", exist_ok=True)

                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())

                                    # Explicitly pass the knowledge_area and metadata
                                    result = st.session_state.agent.ingest_document(
                                        file_path,
                                        knowledge_area=selected_area,
                                        user_role=st.session_state.user_role
                                    )

                                    # Move to data/documents for persistence
                                    dest_path = os.path.join("data/documents", safe_filename)
                                    os.makedirs("data/documents", exist_ok=True)
                                    shutil.move(file_path, dest_path)

                                    success_count += 1
                                    st.toast(f"✅ Indexed: {original_name}")
                                except Exception as e:
                                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")

                            if success_count > 0:
                                st.session_state.ingestion_feedback = f"✅ Successfully ingested {success_count} sources!"
                                st.rerun()

            if "ingestion_feedback" in st.session_state:
                st.success(st.session_state.ingestion_feedback)
                # Clear after showing once if desired, but user asked for a note under button

    if st.session_state.user_role == "Admin":
        if st.button(t["sidebar_reset"], use_container_width=True, type="secondary"):
            if st.session_state.agent:
                if st.session_state.agent.clear_database():
                    st.success("Knowledge base cleared successfully!")
                    st.rerun()

    st.markdown("---")
    with st.expander(t["sidebar_local"]):
        st.info(t["sidebar_vpc_info"])

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <p style='font-size: 12px; color: #64748B; font-weight: 700;'>Private Knowledge Engine<br>v2.1.0 • Enterprise Ready</p>
        </div>
    """, unsafe_allow_html=True)

# Main Interface Header
col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.markdown(f"<h1>{t['header_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 18px; margin-top: -10px; color: #475569; font-weight: 800;'>{t['header_subtitle']}</p>", unsafe_allow_html=True)

with col2:
    if os.getenv("GROQ_API_KEY"):
        st.markdown(f"<div class='status-badge status-online'>{t['status_online']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='status-badge status-offline'>{t['status_offline']}</div>", unsafe_allow_html=True)

# Tabs for Organization
tab_chat, tab_kb, tab_analytics = st.tabs([t["tab_chat"], t["tab_kb"], t["tab_analytics"]])

# Side-by-Side Viewer Logic
if "view_doc" in st.session_state and st.session_state.view_doc:
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### {t['doc_viewer']}")
        st.info(f"{t['viewing']}: **{st.session_state.view_doc['file']}** ({t['page']} {st.session_state.view_doc['page']})")
        # Placeholder for actual PDF rendering
        st.markdown("""
            <div style='height: 300px; background: #eee; border: 1px solid #ccc; display: flex; align-items: center; justify-content: center; color: #666; font-weight: 700; text-align: center; padding: 10px;'>
                PDF Preview Content with Highlighted Text<br>(VPC Deployment Required for Full PDF Rendering)
            </div>
        """, unsafe_allow_html=True)
        if st.button(t["close_viewer"]):
            st.session_state.view_doc = None
            st.rerun()

with tab_chat:
    # Area Selection for Queries
    area_options = ROLE_PERMISSIONS.get(st.session_state.user_role, ["General"])
    default_area = "General"

    # Contextual Role Switching logic:
    if st.session_state.get("assistant_type") in area_options:
        default_area = st.session_state.assistant_type

    st.session_state.knowledge_area = st.segmented_control(
        t["query_area"],
        area_options,
        default=default_area
    )

    # Groq API Key Check
    if not os.getenv("GROQ_API_KEY"):
        st.info(t["api_key_welcome"])
        groq_key = st.text_input(t["api_key_label"], type="password")
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            st.success(t["api_key_success"])
            st.rerun()

    # Only proceed with chat if API key is present
    if not os.getenv("GROQ_API_KEY"):
        st.warning(t["api_key_warning"])
    else:
        # Display example questions if no messages
        if not st.session_state.messages and st.session_state.agent:
            st.markdown(f"""
                <div class='glass-card' style='text-align: center; margin: 2rem 0;'>
                    <h3>{t['welcome_title']}</h3>
                    <p>{t['welcome_subtitle']}</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"### {t['try_asking']}")
            cols = st.columns(2)
            examples = [
                t["example_1"],
                t["example_2"],
                t["example_3"],
                t["example_4"]
            ]
            for i, example in enumerate(examples):
                if cols[i % 2].button(example, use_container_width=True):
                    st.session_state.temp_prompt = example
                    st.rerun()

        # Filter messages if search is active
        display_messages = st.session_state.messages
        if chat_search:
            display_messages = [m for m in st.session_state.messages if chat_search.lower() in m["content"].lower()]

        # Display chat messages
        for message in display_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("search_query"):
                    st.caption(f"{t['search_query']} _{message['search_query']}_")

                if message["role"] == "assistant":
                    # Trust Indicator Logic for history
                    faith_str = message.get("faithfulness", "0%").replace("%", "")
                    try:
                        faith_val = int(faith_str)
                    except:
                        faith_val = 0

                    if faith_val > 0:
                        bar_color = "#10B981" if faith_val >= 90 else "#F59E0B" if faith_val >= 70 else "#EF4444"
                        st.markdown(f"""
                            <div class='trust-bar-container'>
                                <div class='trust-bar-fill' style='width: {faith_val}%; background-color: {bar_color};'></div>
                            </div>
                        """, unsafe_allow_html=True)

                if message.get("sources"):
                    with st.expander(t["sources"]):
                        for source in message["sources"]:
                            st.markdown(f"<div class='doc-item'>{source}</div>", unsafe_allow_html=True)

                if message["role"] == "assistant":
                    st.download_button(
                        label=t["download_answer"],
                        data=message["content"],
                        file_name="ai_response.txt",
                        mime="text/plain",
                        key=f"dl_{st.session_state.messages.index(message)}"
                    )

        # Chat input
        prompt = st.chat_input(t["cta"])
        if "temp_prompt" in st.session_state:
            prompt = st.session_state.temp_prompt
            del st.session_state.temp_prompt

        if prompt:
            if st.session_state.agent:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner(t["analyzing"]):
                        try:
                            response_data = st.session_state.agent.answer_question(
                                prompt,
                                knowledge_area=st.session_state.knowledge_area,
                                assistant_type=st.session_state.assistant_type,
                                language=st.session_state.language
                            )
                            full_response = response_data["answer"]
                            st.markdown(full_response)

                            if response_data.get("search_query"):
                                st.caption(f"{t['search_query']} _{response_data['search_query']}_")

                            # Trust Indicator Logic
                            faith_str = response_data.get("faithfulness", "0%").replace("%", "")
                            try:
                                faith_val = int(faith_str)
                            except:
                                faith_val = 0

                            bar_color = "#10B981" if faith_val >= 90 else "#F59E0B" if faith_val >= 70 else "#EF4444"

                            st.markdown(f"""
                                <div class='trust-bar-container'>
                                    <div class='trust-bar-fill' style='width: {faith_val}%; background-color: {bar_color};'></div>
                                </div>
                            """, unsafe_allow_html=True)

                            sources = response_data.get("sources", [])
                            if sources:
                                metrics_cols = st.columns(2)
                                metrics_cols[0].metric(t["confidence"], response_data.get("confidence", "N/A"))
                                metrics_cols[1].metric(t["faithfulness"], response_data.get("faithfulness", "N/A"))

                                st.info(f"{t['answer_generated_from']} {len(sources)} {t['sources'].lower()}")
                                with st.expander(t["sources_and_deep_link"]):
                                    for source in sources:
                                        # Parse source to get filename and page
                                        try:
                                            # Format: "filename.pdf (Page X)"
                                            parts = source.split(" (Page ")
                                            fname = parts[0]
                                            page_num = parts[1].replace(")", "") if len(parts) > 1 else "1"
                                        except:
                                            fname = source
                                            page_num = "1"

                                        st.markdown(f"<div class='doc-item'>{source}</div>", unsafe_allow_html=True)
                                        if st.button(f"{t['view_source']} {source}", key=f"view_{source}_{len(st.session_state.messages)}"):
                                            st.session_state.view_doc = {"file": fname, "page": page_num}

                            if st.session_state.user_role == "Admin":
                                if st.button(t["verify_gold"], key=f"verify_{len(st.session_state.messages)}"):
                                    st.session_state.agent.verify_answer(prompt, full_response)
                                    st.success(t["gold_saved"])

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response,
                                "sources": response_data.get("sources"),
                                "confidence": response_data.get("confidence"),
                                "faithfulness": response_data.get("faithfulness"),
                                "search_query": response_data.get("search_query")
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.error("Agent not initialized.")

with tab_kb:
    st.markdown(f"## {t['kb_management']}")

    st.subheader(t["kb_library"])
    if st.session_state.agent:
        docs_path = "data/documents"
        docs = os.listdir(docs_path) if os.path.exists(docs_path) else []
        if docs:
            # Grid layout for library
            cols = st.columns(3)
            for i, doc in enumerate(docs):
                fpath = os.path.join(docs_path, doc)
                stats = os.stat(fpath)
                mtime = time.strftime('%Y-%m-%d', time.localtime(stats.st_mtime))
                fsize = f"{stats.st_size / 1024:.1f} KB"

                with cols[i % 3]:
                    st.markdown(f"""
                        <div class='doc-item' title='{t["uploaded_date"]}: {mtime} | {t["file_size"]}: {fsize}'>
                            {doc} <br>
                            <span style='font-size: 10px; color: #10B981;'>✅ Indexed</span>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(t["kb_empty"])

with tab_analytics:
    st.markdown(f"## {t['analytics_title']}")
    if st.session_state.user_role == "Admin":
        c1, c2, c3 = st.columns(3)
        c1.metric(t["most_asked_topic"], "HR Policy")
        c2.metric(t["active_sources"], len(os.listdir("data/documents")) if os.path.exists("data/documents") else 0)
        c3.metric(t["daily_queries"], "142")

        st.markdown(f"### {t['recent_audit_logs']}")
        logs = get_audit_logs(limit=10)
        if logs:
            st.table(logs)
        else:
            st.info(t["no_audit_logs"])

        st.markdown(f"### {t['query_trends']}")
        st.line_chart([10, 25, 15, 40, 35, 60, 45])
    else:
        st.info(t["analytics_admin_only"])

# GDPR Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; padding: 1rem;'>
        <p style='font-size: 14px; color: #64748B; font-weight: 700;'>{t['gdpr_footer']}</p>
        <p style='font-size: 12px; color: #64748B; font-weight: 700;'>Private Knowledge Engine<br>v2.1.0 • Enterprise Ready</p>
    </div>
""", unsafe_allow_html=True)
