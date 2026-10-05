import os
import fitz  # PyMuPDF
from PIL import Image
import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# 1. SETUP & CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Mobile Multimodal Doc Q&A", layout="centered")

# Temporary folder for saved pages
IMAGE_DIR = "temp_pages"
os.makedirs(IMAGE_DIR, exist_ok=True)

# ---------------------------------------------------------
# 2. STREAMLIT FRONTEND & API SETUP
# ---------------------------------------------------------
st.title("📱 Multimodal Document Q&A (Pydroid 3)")
st.caption("Upload PDFs/Invoices & Ask visual questions on Android")

# API Key Input
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Using Gemini Multimodal Model (Vision + Text)
    model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.sidebar.file_uploader("Upload PDF Document", type=["pdf"])

if "pages_images" not in st.session_state:
    st.session_state.pages_images = []

# Process PDF inside Pydroid
if uploaded_file and st.sidebar.button("Process PDF"):
    with st.spinner("Processing PDF Pages..."):
        file_bytes = uploaded_file.read()
        pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        st.session_state.pages_images = []
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            pix = page.get_pixmap(dpi=100) # Compressed for mobile memory
            img_path = os.path.join(IMAGE_DIR, f"page_{page_num+1}.png")
            pix.save(img_path)
            st.session_state.pages_images.append(img_path)
            
        st.success(f"Processed {len(st.session_state.pages_images)} Pages successfully!")

# ---------------------------------------------------------
# 3. CHAT INTERFACE
# ---------------------------------------------------------
if st.session_state.pages_images:
    selected_page = st.selectbox(
        "Select Page to Analyze:", 
        options=range(1, len(st.session_state.pages_images) + 1),
        format_func=lambda x: f"Page {x}"
    )
    
    # Preview current page
    current_img_path = st.session_state.pages_images[selected_page - 1]
    st.image(current_img_path, caption=f"Page {selected_page} Preview", use_container_width=True)

    user_query = st.text_input("Ask a question about this page:")

    if st.button("Analyze & Answer"):
        if not api_key:
            st.error("Please enter your Gemini API Key in the sidebar!")
        elif not user_query:
            st.warning("Please type a question.")
        else:
            with st.spinner("Analyzing with Multimodal AI..."):
                img = Image.open(current_img_path)
                
                # Direct Visual Context Reasoning
                response = model.generate_content([user_query, img])
                
                st.subheader("Answer:")
                st.write(response.text)
