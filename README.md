# AI-Powered Cold Email Generator for Job Applications

## Overview

This project demonstrates how to use language models to create a cold email generator for job applications. It scrapes job postings from a website, processes the data to extract relevant job information, and generates personalized cold emails or cover letters based on a candidate's profile. The project leverages Langchain for language model interactions and ChromaDB for vector storage.

## Features

- **Job Post Extraction**: Uses web scraping to extract job postings from a careers page and convert them into structured JSON data.
- **Cold Email Generation**: Automatically generates tailored cold emails based on job descriptions and user portfolio links.
- **Vector Database**: Utilizes ChromaDB to store and query technical stack data for matching job requirements with personal projects.

## Technologies Used

- **Langchain**: For interacting with large language models (LLMs).
- **ChromaDB**: For vector storage and querying.
- **Python**: Scripting language used to manage the workflow.
- **Pandas**: For handling the CSV data of technical stacks.
- **Web Scraping**: Scrapes job information from websites for automated processing.

## How It Works

1. **Setup the LLM**: The `ChatGroq` model is initialized with the required API key and set to invoke responses from a pre-trained model.
2. **Web Scraping**: The code scrapes a careers page using `WebBaseLoader` to retrieve the raw content of job postings.
3. **Job Posting Extraction**: A `PromptTemplate` is created to extract specific job posting data such as role, experience, skills, and description from the scraped text.
4. **Data Matching**: A vector database, ChromaDB, stores technical stack information for comparison with job requirements.
5. **Cold Email Generation**: A new prompt is designed to generate personalized cold emails using the extracted job information, along with user portfolio links from the vector database.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repo/your-project.git
    ```

2. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set the environment variable for your API key:

    ```bash
    export USER_AGENT=your_user_agent
    ```

4. Set up your API key in the script:

    ```python
    api_key = "your_api_key"
    ```

## Usage

1. **Scrape job postings**: The script scrapes a career page to extract job postings using `WebBaseLoader`.
   
2. **Generate cold emails**: Run the script to generate a tailored cold email based on job descriptions, skills, and your project portfolio.

    ```python
    python your_script.py
    ```

## Example

The following job posting is scraped and processed:

```json
{
    "role": "AI Product Engineer (New Grad)",
    "experience": "New Grad",
    "skills": ["Strong software engineering skills", "Familiarity with AI-powered developer tools"],
    "description": "Propose and build AI-powered experiences for developers."
}
```

An email is automatically generated based on your background and skills:

```text
Subject: Expressed Interest in AI Product Engineer Role

Dear Hiring Manager,

I am excited to reach out to your team... [Rest of the email content]
```