import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import PyPDF2  # To read PDF from resume uploads

class Chain:
    def __init__(self):
        # Initialize the LLM (ChatGroq with Llama 3.1)
        self.llm = ChatGroq(temperature=0, groq_api_key=st.secrets['api_key'], model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        # Define the prompt template for extracting job postings
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the careers page of a website.
            Your job is to extract job postings and return them in JSON format containing the following keys: `role`, 
            `experience`, `skills`, and `description`. Just give one role and return a dict.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):    
            """
        )
        # Chain the prompt with the LLM
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        # Define the prompt template for generating cold email
        prompt_email = PromptTemplate.from_template(
            """
            ### Job Description:
            {job_description}
            ### Instruction:
            Please draft a personalized cold email using this job description 
            and skills, and include my portfolio link: {link}.
            ### EMAIL (NO PREAMBLE):
            """
        )
        # Chain the prompt with the LLM
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link": links})
        return res.content

    def analyze_resume(self, resume_text, job_description, link, skill):
        # Define the prompt template for generating a cover letter from resume text
        prompt_cover_letter = PromptTemplate.from_template(
            """
            ### Resume:
            {resume_text}
            ### Job Description:
            {job_description}
            ### Instruction:
            Draft a personalized cover letter for a data science position based on the provided resume and job description.
            The format should follow:
            Your job description mentioned that you required: talk about the company required {skill}
            then use personalized experience that is relevant to the requirements in the resume to support your claim for each skills required by job description, after each skill.
            Include one of my portfolio project {link} that is related to the skills mentioned for each skills in job description if it's mentioned in the resume. 
            and lastly sign at the bottom with the name scraped from the resume
            ### COVER LETTER (NO PREAMBLE):
            """
        )
        # Chain the prompt with the LLM
        chain_cover_letter = prompt_cover_letter | self.llm
        res = chain_cover_letter.invoke({
            "resume_text": resume_text, 
            "job_description": job_description, 
            "link": link,
            "skill": skill
        })
        return res.content

# Function to extract text from an uploaded PDF resume
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

