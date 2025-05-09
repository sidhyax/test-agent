import streamlit as st
import os
import base64
import json
import time
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the MISTRAL API key
api_key = os.getenv("MISTRAL_API_KEY")

# Custom CSS for better styling
st.set_page_config(
    layout="wide",
    page_title="Mistral OCR App",
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
        text-align: center;
    }
    .subheader {
        font-size: 1.5rem;
        color: #4b6cb7;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        border: 1px solid #4b6cb7;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .result-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4b6cb7;
        color: white;
        border-radius: 8px;
        padding: 10px 25px;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #182848;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stRadio>div {
        display: flex;
        gap: 15px;
    }
    .stRadio>div>div {
        background-color: #f8f9fa;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stRadio>div>div:hover {
        background-color: #e9ecef;
    }
    .download-btn {
        display: inline-block;
        background-color: #4b6cb7;
        color: white;
        text-decoration: none;
        padding: 8px 15px;
        border-radius: 5px;
        margin-right: 10px;
        margin-bottom: 10px;
        transition: all 0.3s;
    }
    .download-btn:hover {
        background-color: #182848;
        transform: translateY(-2px);
    }
    .api-status {
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    .api-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .api-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .file-uploader {
        border: 2px dashed #4b6cb7;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .progress-bar {
        height: 10px;
        background-color: #e9ecef;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .progress-bar div {
        height: 100%;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        border-radius: 5px;
    }
    .tabs-container {
        display: flex;
        margin-bottom: 20px;
    }
    .tab {
        padding: 10px 20px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        cursor: pointer;
    }
    .tab.active {
        background-color: #4b6cb7;
        color: white;
        border-color: #4b6cb7;
    }
    .tab:first-child {
        border-radius: 8px 0 0 8px;
    }
    .tab:last-child {
        border-radius: 0 8px 8px 0;
    }
    iframe {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# App Header with logo and title
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<h1 class="main-header">🔍 Mistral OCR App</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">Extract text from images and PDFs with powerful AI technology</p>', unsafe_allow_html=True)

# API key status
if api_key:
    st.markdown('<div class="api-status api-connected">✅ API Key Connected</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="api-status api-disconnected">❌ API Key Missing</div>', unsafe_allow_html=True)
    st.info("Please enter your API key in the .env file to continue.")
    st.stop()

# Initialize session state variables for persistence
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = []
if "preview_src" not in st.session_state:
    st.session_state["preview_src"] = []
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = []
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "settings"

# Main content area with tabs
tab1, tab2 = st.tabs(["📝 Process Documents", "📊 Results"])

with tab1:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### How to use this app")
    st.markdown("""
    1. Select the file type (PDF or Image)
    2. Choose your source (URL or Local Upload)
    3. Enter URLs or upload files
    4. Click 'Process' to extract text
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File configuration section
    st.markdown('<h3 class="subheader">Document Settings</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        file_type = st.radio("Select file type", ("PDF", "Image"), horizontal=True)
    
    with col2:
        source_type = st.radio("Select source type", ("URL", "Local Upload"), horizontal=True)

    # Input section
    st.markdown('<h3 class="subheader">Input Source</h3>', unsafe_allow_html=True)
    
    input_url = ""
    uploaded_files = []
    
    if source_type == "URL":
        input_url = st.text_area("Enter one or multiple URLs (separate with new lines)", 
                            placeholder="https://example.com/document.pdf\nhttps://example.com/image.jpg",
                            height=100)
    else:
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Drop your files here", 
                                    type=["pdf", "jpg", "jpeg", "png"], 
                                    accept_multiple_files=True)
        if not uploaded_files:
            st.markdown("📁 Upload PDFs or images (.pdf, .jpg, .jpeg, .png)")
        else:
            st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("🔍 Process Documents", use_container_width=True)
    
    if process_button:
        if source_type == "URL" and not input_url.strip():
            st.error("⚠️ Please enter at least one valid URL.")
        elif source_type == "Local Upload" and not uploaded_files:
            st.error("⚠️ Please upload at least one file.")
        else:
            client = Mistral(api_key=api_key)
            st.session_state["ocr_result"] = []
            st.session_state["preview_src"] = []
            st.session_state["image_bytes"] = []
            st.session_state["active_tab"] = "results"
            
            sources = input_url.split("\n") if source_type == "URL" else uploaded_files
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, source in enumerate(sources):
                progress = (idx) / len(sources)
                progress_bar.progress(progress)
                
                file_name = source.strip() if source_type == "URL" else source.name
                status_text.text(f"Processing {idx+1}/{len(sources)}: {file_name}")
                
                if file_type == "PDF":
                    if source_type == "URL":
                        document = {"type": "document_url", "document_url": source.strip()}
                        preview_src = source.strip()
                    else:
                        file_bytes = source.read()
                        encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")
                        document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                        preview_src = f"data:application/pdf;base64,{encoded_pdf}"
                else:
                    if source_type == "URL":
                        document = {"type": "image_url", "image_url": source.strip()}
                        preview_src = source.strip()
                    else:
                        file_bytes = source.read()
                        mime_type = source.type
                        encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                        document = {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded_image}"}
                        preview_src = f"data:{mime_type};base64,{encoded_image}"
                        st.session_state["image_bytes"].append(file_bytes)
                
                try:
                    ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                    time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                    
                    pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                    result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                except Exception as e:
                    result_text = f"Error extracting result: {e}"
                
                st.session_state["ocr_result"].append(result_text)
                st.session_state["preview_src"].append(preview_src)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")
            time.sleep(1)
            st.rerun()

with tab2:
    if st.session_state["ocr_result"]:
        for idx, result in enumerate(st.session_state["ocr_result"]):
            with st.expander(f"Document {idx+1} Results", expanded=(idx==0)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h4 style="color: #4b6cb7;">📄 Input Document</h4>', unsafe_allow_html=True)
                    
                    # Safely fetch preview_src list and current index item
                    preview_list = st.session_state.get("preview_src", [])
                    preview_src = preview_list[idx] if idx < len(preview_list) else None

                    if file_type == "PDF":
                        if preview_src:
                            pdf_embed_html = f'<iframe src="{preview_src}" width="100%" height="600" frameborder="0"></iframe>'
                            st.markdown(pdf_embed_html, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ PDF preview not available.")
                    else:
                        if source_type == "Local Upload":
                            image_list = st.session_state.get("image_bytes", [])
                            if idx < len(image_list):
                                st.image(image_list[idx], use_container_width =True)
                            elif preview_src:
                                st.image(preview_src, use_container_width =True)
                            else:
                                st.warning("⚠️ Image preview not available.")
                        else:
                            if preview_src:
                                st.image(preview_src, use_container_width =True)
                            else:
                                st.warning("⚠️ Image preview not available.")
                
                with col2:
                    st.markdown(f'<h4 style="color: #4b6cb7;">📝 Extracted Text</h4>', unsafe_allow_html=True)
                    
                    # Display extracted text in a scrollable area
                    st.markdown(f"""
                    <div style="height: 400px; overflow-y: auto; padding: 15px; 
                         background-color: white; border-radius: 10px; 
                         border: 1px solid #dee2e6; margin-bottom: 20px;">
                        {result.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download options
                    st.markdown(f'<h4 style="color: #4b6cb7;">💾 Download Options</h4>', unsafe_allow_html=True)
                    
                    def create_download_link(data, filetype, filename, button_text):
                        b64 = base64.b64encode(data.encode()).decode()
                        href = f'<a href="data:{filetype};base64,{b64}" download="{filename}" class="download-btn">{button_text}</a>'
                        return href
                    
                    download_buttons = ""
                    
                    # JSON download
                    json_data = json.dumps({"ocr_result": result}, ensure_ascii=False, indent=2)
                    download_buttons += create_download_link(json_data, "application/json", f"OCR_Result_{idx+1}.json", "📊 JSON")
                    
                    # TXT download
                    download_buttons += create_download_link(result, "text/plain", f"OCR_Result_{idx+1}.txt", "📝 TXT")
                    
                    # MD download
                    download_buttons += create_download_link(result, "text/markdown", f"OCR_Result_{idx+1}.md", "📑 Markdown")
                    
                    st.markdown(download_buttons, unsafe_allow_html=True)
    else:
        st.info("Process documents to see results here.")

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center;">Powered by Mistral AI OCR | Created with Streamlit</p>', unsafe_allow_html=True)