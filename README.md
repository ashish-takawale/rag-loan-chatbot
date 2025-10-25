Bank of Maharashtra Loan Chatbot (RAG)

This project is a retrieval-augmented generation (RAG) chatbot designed to answer questions about the loan schemes offered by the Bank of Maharashtra. It uses a local vector store built from bank data and leverages the OpenAI API to provide natural language answers.

A video demonstration of the project is available in the VIDEO_Walkthrough.txt file.

Project Pipeline

The project operates in three main stages:

scraping.py: A Selenium/BeautifulSoup script that scrapes dynamic web pages from the bank's website. It is designed to handle JavaScript-powered tabs and extract raw text and table data.

Manual Data Curation: A manual data cleaning and structuring step was performed on the raw scraped data. This was a critical step to ensure 100% data quality and create the final, structured knowledge base.

loans_bom.json: The final, clean, and structured JSON file that acts as the "single source of truth" for the chatbot, a result of the manual curation.

build_vector_store.py: This script reads the clean loans_bom.json, flattens it into Document objects, creates text chunks, generates embeddings, and saves them into a local FAISS vector store (faiss_index).

chat_with_rag.py: This is the main application. It loads the pre-built FAISS index and the OpenAI LLM to run an interactive command-line chatbot that answers user questions and cites its sources.

Project Setup

Follow these instructions to set up and run the chatbot.

Prerequisites

Git

Python 3.8+

An OpenAI API Key

Step-by-Step Instructions

Clone the Repository

git clone <your-repository-url>
cd <your-project-directory>


Create a Virtual Environment

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate


Install Dependencies
Install all required Python libraries from requirements.txt.

pip install -r requirements.txt


Set Up Environment Variables
Create a file named .env in the root directory. Add your OpenAI API key to this file (this is required to run the chatbot).

OPENAI_API_KEY="sk-YourActualOpenAI_API_KeyGoesHere"


(Note: The .gitignore file is configured to prevent this sensitive file from ever being uploaded.)

Run the Chatbot
This repository includes a pre-built FAISS index (faiss_index folder) for convenience. You can run the chatbot immediately.

python chat_with_rag.py


Output:

🔹 Loading FAISS index and embeddings...

🤖 RAG Chatbot ready! Ask anything about Bank of Maharashtra loan schemes.
Type 'exit' to quit.

You: 


Architectural Decisions

Data Source: loans_bom.json is the manually curated "source of truth." This was a deliberate choice to prioritize data accuracy, as the raw scraped data was too inconsistent for a simple script to handle reliably.

Vector Store: FAISS (faiss-cpu) was chosen as it is a fast, lightweight, and completely local vector store, perfect for this project's scale.

Embedding Model: sentence-transformers/all-MiniLM-L6-v2 is used for its excellent balance of performance and size, running locally.

RAG Framework: LangChain is used to orchestrate the pipeline, connecting the retriever (FAISS), the prompt, and the LLM (gpt-3.5-turbo).

Chatbot: gpt-3.5-turbo is used for its speed, low cost, and strong ability to synthesize answers from provided context. A low temperature=0.2 is set to ensure factual, non-creative responses.

Source Citing: The RetrievalQA chain is set to return_source_documents=True, allowing the chatbot to cite the specific loan scheme it used to find the answer, which is crucial for user trust.