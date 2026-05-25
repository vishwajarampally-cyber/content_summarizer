import os
import tempfile
from datetime import datetime
import streamlit as st

# Set page configuration first
st.set_page_config(
    page_title="AI Content Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header gradient banner style */
    .header-container {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.15);
    }
    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.025em;
    }
    .header-subtitle {
        font-size: 1.15rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        margin-bottom: 0;
        font-weight: 400;
    }
    
    /* Metric styling */
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .dark .metric-card {
        background-color: #1e293b;
        border-color: #334155;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4f46e5;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
    
    /* History card styling */
    .history-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #4f46e5;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .dark .history-card {
        background-color: #1e293b;
        border-color: #334155;
        border-left-color: #06b6d4;
    }
    .history-meta {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 0.75rem;
    }
    .history-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    
    /* Badge element */
    .custom-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.5rem;
    }
    .badge-primary { background-color: #e0e7ff; color: #4338ca; }
    .badge-secondary { background-color: #ecfeff; color: #0891b2; }
    .badge-info { background-color: #f0fdf4; color: #166534; }
    
    /* Global scrollbar and font refinement */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Load configuration safely
from utils.env_loader import load_project_env
load_project_env()

# Sidebar - Configuration and API Settings
st.sidebar.image("https://img.icons8.com/gradient/100/document.png", width=60)
st.sidebar.title("Configuration")

# Capture initial environment configuration to preserve secure keys
if "initial_grok_key" not in st.session_state:
    st.session_state.initial_grok_key = os.getenv("GROK_API_KEY", "").strip()
if "initial_mongo_url" not in st.session_state:
    st.session_state.initial_mongo_url = os.getenv("MONGODB_URL", "").strip()

has_env_grok = bool(st.session_state.initial_grok_key)
has_env_mongo = bool(st.session_state.initial_mongo_url and "localhost" not in st.session_state.initial_mongo_url)

user_grok_key = ""
user_mongo_url = ""

st.sidebar.subheader("Security & Environment")

# --- Grok Key UI (Secure & Encapsulated) ---
if has_env_grok:
    st.sidebar.info("🔒 **Grok API Key** is securely loaded from Cloud Secrets.")
    override_grok = st.sidebar.checkbox("Override with custom Grok Key", key="override_grok")
    if override_grok:
        user_grok_key = st.sidebar.text_input(
            "Enter custom Grok API Key",
            type="password",
            help="Enter a custom xAI/Groq key to override the system key."
        )
    else:
        user_grok_key = st.session_state.initial_grok_key
else:
    user_grok_key = st.sidebar.text_input(
        "Grok API Key",
        value="",
        type="password",
        help="Enter your xAI Grok or Groq API Key. Format starts with 'gsk_' for Groq."
    )

# --- MongoDB URL UI (Secure & Encapsulated) ---
if has_env_mongo:
    st.sidebar.info("🔒 **MongoDB Database** is connected securely via Secrets.")
    override_mongo = st.sidebar.checkbox("Override with custom MongoDB URL", key="override_mongo")
    if override_mongo:
        user_mongo_url = st.sidebar.text_input(
            "Enter custom MongoDB URL",
            type="password",
            help="Enter a custom MongoDB Atlas connection string."
        )
    else:
        user_mongo_url = st.session_state.initial_mongo_url
else:
    override_mongo_options = st.sidebar.checkbox("Provide custom MongoDB URL", key="override_mongo_options")
    if override_mongo_options:
        user_mongo_url = st.sidebar.text_input(
            "MongoDB Connection URL",
            type="password",
            help="Enter your custom MongoDB connection string."
        )
    else:
        user_mongo_url = ""

# Apply selected configurations back to environment variables for backend consumption
if user_grok_key:
    os.environ["GROK_API_KEY"] = user_grok_key
else:
    if "GROK_API_KEY" in os.environ:
        del os.environ["GROK_API_KEY"]

if user_mongo_url:
    os.environ["MONGODB_URL"] = user_mongo_url
else:
    # Set to a dummy fallback to let the mongodb client initiate and trigger its mongomock fallback
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017"

# Summary Settings
st.sidebar.subheader("Summary Settings")
from utils.prompts import SUMMARY_STYLE_OPTIONS, DOCUMENT_STYLE_OPTIONS

summary_style = st.sidebar.selectbox(
    "Summary Style",
    options=list(SUMMARY_STYLE_OPTIONS.values()),
    index=0
)

document_style = st.sidebar.selectbox(
    "Content / Document Type",
    options=list(DOCUMENT_STYLE_OPTIONS.values()),
    index=3 # General Content default
)

# Lazy initialization of SummaryService
@st.cache_resource(show_spinner=False)
def get_summary_service(grok_key_trigger, mongo_url_trigger):
    # This function uses triggers so that if the user edits the sidebar, cache invalidates and reinstantiates
    if not os.getenv("GROK_API_KEY"):
        return None, "GROK_API_KEY is missing. Please set it in the sidebar or env."
    
    from services.summary_service import SummaryService
    try:
        service = SummaryService()
        is_mock = getattr(service.db_client, "_in_memory", False)
        return service, is_mock
    except Exception as exc:
        return None, f"Initialization error: {exc}"

# Initialize service
service, service_status = get_summary_service(user_grok_key, user_mongo_url)

# Header Banner
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">AI Content Summarizer</h1>
        <p class="header-subtitle">Instantly distill long documents, websites, and custom texts into beautiful, styled insights using Grok intelligence.</p>
    </div>
""", unsafe_allow_html=True)

# Main Application Layout
if service is None:
    st.error(f"⚠️ **Configuration Required**: {service_status}")
    st.info("💡 **How to proceed**:\n"
            "1. Enter your **Grok/Groq API Key** in the sidebar.\n"
            "2. (Optional) Provide a **MongoDB Connection URL** to persist summaries. If not provided, the app will run with a temporary, in-memory MongoDB mock, which works perfectly for testing!")
    st.stop()

# Show dynamic environment banner
if service_status is True:
    st.warning("⚡ **Running with temporary database**: MongoDB URL not set or offline. Saving summaries in-memory (history will reset on app restart).", icon="ℹ️")
else:
    st.success("☁️ **Connected to Cloud Database**: Summaries are securely saved and synced with MongoDB Atlas.", icon="✅")

# Create Tabs
tab_text, tab_pdf, tab_url, tab_history = st.tabs([
    "📝 Paste Text", 
    "📄 Upload PDF Document", 
    "🔗 Extract from URL", 
    "📜 History & Saved Summaries"
])

def display_summary_results(record):
    """Utility to display summary results with statistics in a premium grid."""
    st.markdown("### ✨ Generated Summary")
    st.markdown(f'<div style="background-color: #f1f5f9; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #4f46e5; margin-bottom: 1.5rem; font-size: 1.05rem; line-height: 1.6; color: #1e293b;">{record.get("summary", "")}</div>', unsafe_allow_html=True)
    
    # Metadata badges
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <span class="custom-badge badge-primary">Style: {record.get("summary_type", "N/A")}</span>
            <span class="custom-badge badge-secondary">Type: {record.get("document_style", "N/A")}</span>
            <span class="custom-badge badge-info">Created: {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Grid of metrics
    stats = record.get("statistics", {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats.get("word_count", 0):,}</div>
                <div class="metric-label">Source Words</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats.get("character_count", 0):,}</div>
                <div class="metric-label">Source Characters</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats.get("reading_time_minutes", 0.0):.1f}m</div>
                <div class="metric-label">Est. Reading Time</div>
            </div>
        """, unsafe_allow_html=True)

# ----------------- Tab 1: Paste Text -----------------
with tab_text:
    st.markdown("### Paste Content for Summarization")
    text_content = st.text_area(
        "Enter or paste the content you want to summarize:", 
        height=300,
        placeholder="Type or paste your articles, reports, transcripts, or long paragraphs here..."
    )
    
    if text_content:
        words = len(text_content.split())
        chars = len(text_content)
        st.caption(f"📊 Live Stats: {words:,} words | {chars:,} characters")
        
    btn_summarize_text = st.button("🚀 Summarize Text", key="btn_text", use_container_width=True)
    
    if btn_summarize_text:
        if not text_content.strip():
            st.error("Please paste some text content first!")
        else:
            with st.spinner("Analyzing text and generating summary via Grok..."):
                try:
                    record = service.create_summary(
                        source_type="text",
                        source_content=text_content,
                        summary_style=summary_style,
                        document_style=document_style,
                        title="Pasted Text Summary"
                    )
                    st.toast("Summary generated successfully!", icon="🎉")
                    display_summary_results(record)
                    # Force history update on next load
                    st.cache_resource.clear()
                except Exception as e:
                    st.error(f"Failed to generate summary: {e}")

# ----------------- Tab 2: Upload PDF -----------------
with tab_pdf:
    st.markdown("### Summarize PDF Documents")
    uploaded_file = st.file_uploader("Choose a PDF file to upload and extract text:", type=["pdf"])
    
    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")
        
        btn_summarize_pdf = st.button("🚀 Summarize PDF Document", key="btn_pdf", use_container_width=True)
        
        if btn_summarize_pdf:
            with st.spinner("Extracting text from PDF and generating summary..."):
                try:
                    # Write to a secure temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    try:
                        extracted_text = extract_text_from_pdf(tmp_path)
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    
                    if not extracted_text.strip():
                        st.error("Could not extract any text content from this PDF file.")
                    else:
                        record = service.create_summary(
                            source_type="pdf",
                            source_content=extracted_text,
                            summary_style=summary_style,
                            document_style=document_style,
                            title=uploaded_file.name
                        )
                        st.toast("PDF successfully summarized!", icon="🎉")
                        display_summary_results(record)
                        st.cache_resource.clear()
                except Exception as e:
                    st.error(f"Failed to process PDF: {e}")

# ----------------- Tab 3: Extract from URL -----------------
with tab_url:
    st.markdown("### Summarize Web Article URL")
    article_url = st.text_input("Enter the article or blog URL (http/https):", placeholder="https://example.com/some-interesting-article")
    
    btn_summarize_url = st.button("🚀 Fetch and Summarize URL", key="btn_url", use_container_width=True)
    
    if btn_summarize_url:
        if not article_url.strip():
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Fetching page source and extracting article text..."):
                try:
                    title, extracted_text = extract_text_from_url(article_url)
                    
                    with st.spinner("Generating summary via Grok..."):
                        record = service.create_summary(
                            source_type="url",
                            source_content=extracted_text,
                            summary_style=summary_style,
                            document_style=document_style,
                            title=title
                        )
                        st.toast("URL article successfully summarized!", icon="🎉")
                        st.markdown(f"**Extracted Article Title**: *{title}*")
                        display_summary_results(record)
                        st.cache_resource.clear()
                except Exception as e:
                    st.error(f"Failed to process URL: {e}")

# ----------------- Tab 4: History & Logs -----------------
with tab_history:
    st.markdown("### 📜 Saved Summaries & History")
    
    # Fetch recent history
    try:
        history_records = service.get_history(limit=30)
    except Exception as e:
        st.error(f"Failed to retrieve history: {e}")
        history_records = []
        
    if not history_records:
        st.info("No saved summaries found. Generate your first summary above to see it listed here!")
    else:
        st.caption(f"Showing the latest {len(history_records)} saved summary sessions.")
        
        for record in history_records:
            # Format datetime
            created_at_val = record.get("created_at")
            if isinstance(created_at_val, datetime):
                formatted_time = created_at_val.strftime("%Y-%m-%d %H:%M UTC")
            elif isinstance(created_at_val, str):
                try:
                    # Parse standard ISO string
                    dt = datetime.fromisoformat(created_at_val.replace("Z", "+00:00"))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    formatted_time = created_at_val
            else:
                formatted_time = "N/A"
                
            title_text = record.get("title") or "Untitled Summary"
            source_icon = "📝"
            if record.get("source_type") == "pdf":
                source_icon = "📄"
            elif record.get("source_type") == "url":
                source_icon = "🔗"
                
            stats = record.get("statistics", {})
            words_count = stats.get("word_count", 0)
            
            with st.expander(f"{source_icon} **{title_text}** — *{formatted_time}* ({words_count} words)"):
                st.markdown(f"**Style**: `{record.get('summary_type', 'N/A')}` | **Category**: `{record.get('document_style', 'N/A')}`")
                st.markdown(f'<div style="background-color: #f8fafc; border-left: 3px solid #06b6d4; padding: 1rem; border-radius: 6px; font-size: 0.98rem; margin: 1rem 0;">{record.get("summary")}</div>', unsafe_allow_html=True)
                
                # Show source text in expander if requested
                with st.expander("Show Original Source Text"):
                    st.text_area("Original Content", value=record.get("original_text"), height=200, disabled=True, key=f"orig_{record.get('id') or record.get('_id')}")
