Bank of Maharashtra Loan Chatbot (RAG)

This project is a retrieval-augmented generation (RAG) chatbot designed to answer questions about the loan schemes offered by the Bank of Maharashtra. It uses a local vector store built from bank data and leverages the OpenAI API to provide natural language answers.

The project is a 4-part pipeline:

scraping.py: A Selenium/BeautifulSoup script that scrapes dynamic web pages from the bank's website. It saves the raw, unstructured data (a mix of tables and text) to data_raw/loans_raw.json (Note: script currently saves to data_raw/loans_bom.json).

data_processing.py (Not included): A script that reads the raw scraped data, cleans it, and transforms it into the final, structured knowledge base.

loans_bom.json: The final, clean, and structured JSON file that acts as the "single source of truth" for the chatbot.

build_vector_store.py: This script reads the clean loans_bom.json, flattens it into Document objects, creates text chunks, generates embeddings, and saves them into a local FAISS vector store (faiss_index).

chat_with_rag.py: This script loads the pre-built FAISS index and runs an interactive command-line chatbot that uses a LangChain RAG pipeline to answer user queries.

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

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate


Install Dependencies
Install all required Python libraries from requirements.txt.

pip install -r requirements.txt


Set Up Environment Variables
Create a file named .env in the root directory. Add your OpenAI API key to this file:

OPENAI_API_KEY="sk-YourActualOpenAI_API_KeyGoesHere"


(Note: The .gitignore file is configured to prevent this file from being committed.)

Build the Vector Store
The clean loans_bom.json is included in this repository. Run the build_vector_store.py script to create the local FAISS index.

python build_vector_store.py


Output:

Flattening JSON to documents...
Created 37 chunks
✅ Vector store built and saved at: D:\Test\Chatbot\faiss_index


(Note: You may need to update the INDEX_PATH in build_vector_store.py and chat_with_rag.py to use a relative path like "faiss_index" for better portability.)

Run the Chatbot
You can now start the interactive chatbot.

python chat_with_rag.py


Output:

🔹 Loading FAISS index and embeddings...

🤖 RAG Chatbot ready! Ask anything about Bank of Maharashtra loan schemes.
Type 'exit' to quit.

You: 


Optional: Re-generating the Data

If you want to re-scrape and re-process the data from the live website, you would follow these steps (requires chromedriver to be set up):

python scraping.py - This scrapes the website and creates the raw data file.

python data_processing.py - This (your script) cleans the raw data and outputs the final loans_bom.json.

python build_vector_store.py - This rebuilds the index from the new data.

Architectural Decisions

This section explains the reasoning behind the key technical choices in this project.

Libraries

Web Scraping (scraping.py):

selenium: Chosen because the Bank of Maharashtra website relies heavily on JavaScript-powered tabs to display loan information. A static library like requests would only get the HTML for the default tab and miss all other content. Selenium controls a real browser, allowing the script to click each tab and wait for the content to load.

beautifulsoup4 & pandas: Used in conjunction with Selenium. BeautifulSoup parses the page source, and pandas.read_html is the most efficient way to parse HTML <table> elements into a clean Python format.

Data Processing (data_processing.py):

This script is the crucial "transform" step. It is responsible for taking the messy, mixed-format output from the scraper (tables and raw text) and converting it into the clean, predictable, structured loans_bom.json that the RAG pipeline can reliably use.

RAG Pipeline (build_vector_store.py, chat_with_rag.py):

langchain: Chosen as the primary framework. It provides a high-level "glue" that connects the LLM, vector store, and retriever into a single RetrievalQA chain, significantly reducing boilerplate code.

faiss-cpu: Selected for the vector store. It's extremely fast, runs entirely locally (no API keys or network latency), and is a memory-efficient solution for similarity search.

python-dotenv: Used for securely managing the OPENAI_API_KEY by loading it from a .env file, keeping it out of the source code.

Data Strategy (Chunking)

The data strategy is centered on converting the structured loans_bom.json into effective chunks for retrieval.

1. Flattening: The flatten_json_to_docs function in build_vector_store.py is a key step. It converts each structured loan scheme (which is a JSON object) into a single, long text Document. This ensures all information for one loan is co-located.

2. Chunking:

Method: RecursiveCharacterTextSplitter from LangChain.

Parameters: chunk_size=800, chunk_overlap=100.

Rationale: This splitter is semantically aware. It tries to split text on logical boundaries first (paragraphs \n\n, then newlines \n, then spaces). A chunk_size of 800 is a balance—large enough to contain meaningful context (e.g., eligibility and interest rate) but small enough to be a specific, relevant snippet. The overlap of 100 ensures that a concept split at a boundary is still captured in full by one of the chunks.

3. Metadata: Crucially, metadata (category, scheme, url) is preserved with each chunk. This allows the chatbot to cite its sources (📘 Sources:), which is vital for user trust and verification.

Model Selection

Embedding Model: sentence-transformers/all-MiniLM-L6-v2

Rationale: This is one of the most popular and best-performing "all-rounder" embedding models. It's lightweight, runs entirely locally via the HuggingFaceEmbeddings class, and is highly effective at capturing the semantic meaning of sentences. Its speed is a major advantage for quickly building the vector store.

LLM (Language Model): gpt-3.5-turbo (via ChatOpenAI)

Rationale: This model provides the best balance of speed, cost, and high-quality reasoning. For a RAG task—where the "ground truth" is provided directly in the prompt as context—gpt-3.5-turbo is more than capable of synthesizing the retrieved chunks into a factual, coherent answer. A temperature=0.2 is set to ensure responses are deterministic and factual, avoiding creative "hallucinations."

AI Tools Used

Selenium: A browser automation tool used to gather the initial data by mimicking a user to defeat simple dynamic-content hurdles.

HuggingFace sentence-transformers: Used to generate the vector embeddings that power the similarity search.

FAISS (Facebook AI Similarity Search): Used as the high-speed, local vector database to store and retrieve document chunks.

LangChain: The core AI orchestration framework used to build the pipeline (RetrievalQA) that connects the user's query, the FAISS retriever, and the OpenAI LLM.

OpenAI API: The generative AI model (gpt-3.5-turbo) that synthesizes the final, human-readable answer from the context.

Challenges Faced

Dynamic Web Content: The single biggest challenge. The bank's website hides most of its loan information inside JavaScript-powered tabs. A static requests call would only get the HTML for the default, often empty, tab.

Solution: selenium was used to control a web driver (like Chrome). The script programmatically finds all tabs, clicks each one, and waits for the content to load before passing the rendered HTML to BeautifulSoup for parsing.

Messy Data Formats: The scraper extracts a mix of structured tables (parsed by pandas) and unstructured text (<p>, <li> tags). This raw data is inconsistent and unusable for a RAG pipeline.

Solution: A dedicated data_processing.py script was created. This script is responsible for the critical "Transform" step of the ETL process. It parses the raw scraped file, applies rules and logic to extract information, and formats it into the clean, predictable, and hierarchical loans_bom.json file.

Trust and Verification: A chatbot that just gives an answer is a "black box." A user needs to trust the information.

Solution: By adding metadata (category, scheme, url) to each Document before chunking, this metadata is passed along to the chunks. The RetrievalQA chain was configured with return_source_documents=True, allowing the chat_with_rag.py script to access and print which document chunks were used to generate the answer.

Potential Improvements

Web Interface: Replace the command-line interface with a user-friendly web UI using Streamlit or Flask. This would make the chatbot accessible to anyone.

Automated Knowledge Base Updates: Implement a CI/CD pipeline (e.g., using GitHub Actions) that runs the scraping.py and data_processing.py scripts on a schedule (e.g., weekly). If it detects changes, it automatically triggers build_vector_store.py to rebuild the index with fresh data.

Conversational Memory: Integrate ConversationBufferMemory into the LangChain pipeline. This would allow the chatbot to remember the context of the conversation and answer follow-up questions (e.g., "What is the interest rate for that first one?").

Advanced Retrieval: Implement a re-ranking step. Instead of just taking the top 3 documents (k: 3), retrieve the top 10 and then use a more sophisticated model (like a cross-encoder) to re-rank them for relevance before sending the best 3 to the LLM.

Formal Evaluation: Create a test set of questions and expected answers ("golden set"). Use an evaluation framework like RAGAs or LangChain's evaluation tools to quantitatively measure the chatbot's performance on metrics like faithfulness (is the answer based on the context?) and answer relevance.