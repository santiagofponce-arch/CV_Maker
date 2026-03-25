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

if st.button("Generate Required Documents", type="primary"):
    if not base_cv_to_use:
        st.error("Please provide your Base CV (upload PDF or paste text).")
        st.stop()
    
    if not job_url and not job_description_manual.strip():
        st.error("Please provide a Job URL or paste the job description manually.")
        st.stop()

    job_text = job_description_manual.strip()

    if not job_text and job_url:
        with st.spinner("Scraping job description..."):
            job_text = scrape_job_description(job_url)
            if job_text.startswith("Error"):
                st.error(f"Could not scrape the URL. Direct message: {job_text}. Please paste the description manually.")
                st.stop()
            st.success("Successfully extracted job posting!")
            
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tailored CV")
        with st.spinner("Tailoring CV for this job..."):
            try:
                tailored_cv = generate_tailored_cv(base_cv_to_use, job_text, api_key=api_key, model=model_choice)
                st.markdown(tailored_cv)
                
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button("Download CV (Markdown)", tailored_cv, file_name="tailored_cv.md")
                with dl_col2:
                    try:
                        pdf_bytes = generate_pdf(tailored_cv)
                        st.download_button("Download CV (PDF)", data=pdf_bytes, file_name="tailored_cv.pdf", mime="application/pdf")
                    except Exception as pdf_err:
                        st.error(f"Failed to generate PDF: {pdf_err}")
            except Exception as e:
                st.error(f"Error generating CV: {str(e)}")

    with col2:
        st.subheader("Human-Like Cover Letter")
        with st.spinner("Drafting cover letter..."):
            try:
                cover_letter = generate_cover_letter(base_cv_to_use, job_text, api_key=api_key, model=model_choice)
                st.markdown(cover_letter)
                st.download_button("Download Cover Letter (Text)", cover_letter, file_name="cover_letter.txt")
            except Exception as e:
                st.error(f"Error generating Cover Letter: {str(e)}")
