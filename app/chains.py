import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv


load_dotenv()
class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=st.secrets["api_key"], model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
                ### SCRAPED TEXT FROM WEBSITE:
                {page_data}
                ### INSTRUCTION:
                The scraped text is from the career's page of a website.
                Your job is to extract the job postings and return them in JSON format containing the 
                following keys: `role`, `experience`, `skills` and `description`. just give one role, and return a dict
                Only return the valid JSON. 
                ### VALID JSON (NO PREAMBLE):    
             """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### job description:
            {job_description}
            ### instruction:

            I am Thuan Nguyen, a Master of Science in Business Analytics student at Texas A&M University-Commerce with a 4.0 GPA, expected to graduate in June 2025. My work experience includes a Graduate Research Assistant role and a Data Scientist Intern position at FPT Software, where I worked on projects related to AI-powered web applications, cybersecurity threat detection, and stock sentiment analysis. My technical expertise includes Python, R, SQL, machine learning, and data analysis tools like Excel Solver and Langchain. 
            I am looking to apply for a data science position. 
            The job description highlights the need for skills that will be provided in my portfolio {link}
            Please help me draft a cold email that highlights my skills, my project experience (such as cybersecurity detection and stock prediction projects), and my interest in the company, while requesting a conversation to discuss potential opportunities.

            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link": links})
        return res.content

if __name__ == "__main__":
    print(os.getenv("api_key"))