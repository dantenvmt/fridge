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

api_key = st.secrets['api_key']

#extract text from an uploaded PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("Cold email & Cover Letter Generator")
    #user input
    url_input = st.text_input("Enter a URL for job scraping:", value="")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    submit_button = st.button("Generate Cold Email & Cover Letter")

    if submit_button and url_input and uploaded_file:
        try:
            st.write("Scraping job description from the provided URL...")
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()

            jobs = llm.extract_jobs(data)
            if not jobs:
                st.error("No jobs found in the scraped data.")
                return
            
            job = jobs[0]
            skills = job.get('skills', [])
            links = portfolio.query_links(skills)
            resume_text = extract_text_from_pdf(uploaded_file)
            #generate cold email
            st.write("Generating cold email...")
            email = llm.write_mail(job,resume_text, links)
            st.code(email, language='markdown')

            #generating cover letter using uploaded resume
            st.write("Generating cover letter...")
            
            job_description = job.get('description', 'No description available')
            cover_letter = llm.analyze_resume(resume_text, job_description, links, skills)
            st.code(cover_letter, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email & Cover Letter Generator")
    create_streamlit_app(chain, portfolio, clean_text)
