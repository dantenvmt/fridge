import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import PyPDF2

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=st.secrets['api_key'], model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        #extracting job postings
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

    def write_mail(self, job, resume_text, links):
        #generating cold email
        prompt_email = PromptTemplate.from_template(
            """
            ### Job Description:
            {job_description}
            ### Resume:
            {resume_text}

            ### Instruction:
            Draft a tailored cold email that highlights my relevant skills and experience from resume, based on the provided job description. 
            The email should open with a professional greeting and express genuine interest in the position, followed by a brief summary of how my background aligns with the job requirements. 
            For each key skill mentioned in the job description, provide a specific example of my experience that demonstrates proficiency in that area. Where applicable, include a related portfolio project with a link: {link}. 
            End with a polite call to action, expressing enthusiasm for further discussion and sign off with my name."
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link": links, "resume_text": resume_text})
        return res.content

    def analyze_resume(self, resume_text, job_description, link, skill):
        #generating a cover letter from resume text
        prompt_cover_letter = PromptTemplate.from_template(
            """
            ### Resume:
            {resume_text}
            ### Job Description:
            {job_description}
            ### Instruction:
            "Draft a highly personalized cover letter for a data science position, tailored to both the provided resume and the job description. The cover letter should address the following:

            Begin by acknowledging the specific skills or qualifications required in the job description, using the format: 'In your job description, you mentioned the need for {skill}.'

            For each listed skill, directly relate it to a specific and relevant experience from the resume, explaining how that experience demonstrates expertise in the required skill. Use concise, impactful sentences.

            For any skill that aligns with a portfolio project mentioned in the resume, provide a one-sentence reference to the project and include the project link {link}.

            Structure each skill explanation as a bullet point for clarity.

            Conclude with a professional closing, signed with the applicant's name as scraped from the resume."
            ### COVER LETTER (NO PREAMBLE):
            """
        )

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

