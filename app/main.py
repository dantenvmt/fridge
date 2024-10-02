import streamlit as st
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import sqlite3
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import PyPDF2

# API key for Langchain Groq
api_key = st.secrets['api_key']

# Function to extract text from an uploaded PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

# Streamlit application creation
def create_streamlit_app(llm, portfolio, clean_text):
    st.title("Cold Email & Cover Letter Generator")

    # Section 1: Cold Email Generator based on a URL
    st.subheader("Generate Cold Email Based on Job Description URL")
    url_input = st.text_input("Enter a URL for job scraping:", value="")
    submit_button = st.button("Submit URL")

    if submit_button and url_input:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")

    # Section 2: Cover Letter Generator based on Resume PDF upload
    st.subheader("Generate Cover Letter Based on Uploaded Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    job_description = st.text_area("Enter the job description")
    link = st.text_input("Enter your portfolio link")
    submit_resume_button = st.button("Generate Cover Letter")

    if submit_resume_button and uploaded_file and job_description:
        try:
            resume_text = extract_text_from_pdf(uploaded_file)
            st.write("Resume successfully uploaded and processed!")
            cover_letter = llm.analyze_resume(resume_text, job_description, link)
            st.write("Generated Cover Letter:")
            st.code(cover_letter, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    # Instantiate Chain and Portfolio objects
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email & Cover Letter Generator")
    create_streamlit_app(chain, portfolio, clean_text)
