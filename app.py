import streamlit as st
import os
import PyPDF2
from utils.scraper import scrape_job_description
from utils.llm import generate_tailored_cv, generate_cover_letter
from utils.pdf_generator import generate_pdf
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Job Hunting Assistant", page_icon="💼", layout="wide")

st.title("💼 AI Job Hunting Assistant")
st.markdown("Tailor your CV and write human-sounding cover letters based on any job description URL.")

# API Key handling in session state or env
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.warning("No GEMINI_API_KEY found in environment variables. Please enter it below to begin.")
    user_api_key = st.text_input("Gemini API Key:", type="password")
    if user_api_key:
        os.environ["GEMINI_API_KEY"] = user_api_key
        st.rerun()
    else:
        st.stop()

# Helper to read PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

with st.sidebar:
    st.header("1. Upload Base CV")
    st.markdown("Upload your current comprehensive CV in PDF format, or paste the text below.")
    uploaded_file = st.file_uploader("Upload PDF CV", type=["pdf"])
    base_cv_text = st.text_area("Or Paste CV Text", height=200)

    st.header("2. Settings")
    model_choice = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview"], index=0)

base_cv_to_use = ""
if uploaded_file is not None:
    base_cv_to_use = extract_text_from_pdf(uploaded_file)
elif base_cv_text.strip():
    base_cv_to_use = base_cv_text

st.header("3. Target Job")
job_url = st.text_input("Job Posting URL:")
job_description_manual = st.text_area("Or Paste Job Description Manually (Optional)", height=150)

# Initialize session state variables
if "tailored_cv" not in st.session_state:
    st.session_state.tailored_cv = None
if "cv_pdf_bytes" not in st.session_state:
    st.session_state.cv_pdf_bytes = None
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = None
if "generate_requested" not in st.session_state:
    st.session_state.generate_requested = False

col_gen, col_reset = st.columns([2, 8])
with col_gen:
    if st.button("Generate Required Documents", type="primary"):
        st.session_state.generate_requested = True
        st.session_state.tailored_cv = None
        st.session_state.cv_pdf_bytes = None
        st.session_state.cover_letter = None

with col_reset:
    if st.session_state.tailored_cv is not None or st.session_state.cover_letter is not None:
        if st.button("Start Over / New Link"):
            st.session_state.tailored_cv = None
            st.session_state.cv_pdf_bytes = None
            st.session_state.cover_letter = None
            st.session_state.generate_requested = False
            st.rerun()

if st.session_state.generate_requested:
    if not base_cv_to_use:
        st.error("Please provide your Base CV (upload PDF or paste text).")
        st.session_state.generate_requested = False
        st.stop()
    
    if not job_url and not job_description_manual.strip():
        st.error("Please provide a Job URL or paste the job description manually.")
        st.session_state.generate_requested = False
        st.stop()

    job_text = job_description_manual.strip()

    if not job_text and job_url:
        with st.spinner("Scraping job description..."):
            job_text = scrape_job_description(job_url)
            if job_text.startswith("Error"):
                st.error(f"Could not scrape the URL. Direct message: {job_text}. Please paste the description manually.")
                st.session_state.generate_requested = False
                st.stop()
            st.success("Successfully extracted job posting!")
            
    with st.spinner("Generating documents... This may take a moment."):
        # Generate CV
        try:
            st.session_state.tailored_cv = generate_tailored_cv(base_cv_to_use, job_text, api_key=api_key, model=model_choice)
            # Try generating PDF as well
            try:
                st.session_state.cv_pdf_bytes = generate_pdf(st.session_state.tailored_cv)
            except Exception as pdf_err:
                st.error(f"Failed to generate PDF: {pdf_err}")
        except Exception as e:
            st.error(f"Error generating CV: {str(e)}")
        
        # Generate Cover Letter
        try:
            st.session_state.cover_letter = generate_cover_letter(base_cv_to_use, job_text, api_key=api_key, model=model_choice)
        except Exception as e:
            st.error(f"Error generating Cover Letter: {str(e)}")
            
    st.session_state.generate_requested = False
    st.rerun()

if st.session_state.tailored_cv or st.session_state.cover_letter:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tailored CV")
        if st.session_state.tailored_cv:
            st.text_area("Review your CV code:", st.session_state.tailored_cv, height=400)
            
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button("Download CV (LaTeX)", st.session_state.tailored_cv, file_name="tailored_cv.tex", key="cv_tex_dl")
            with dl_col2:
                if st.session_state.cv_pdf_bytes:
                    st.download_button("Download CV (PDF)", data=st.session_state.cv_pdf_bytes, file_name="tailored_cv.pdf", mime="application/pdf", key="cv_pdf_dl")

    with col2:
        st.subheader("Human-Like Cover Letter")
        if st.session_state.cover_letter:
            st.markdown(st.session_state.cover_letter)
            st.download_button("Download Cover Letter (Text)", st.session_state.cover_letter, file_name="cover_letter.txt", key="cl_txt_dl")
