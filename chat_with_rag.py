# chat_with_rag.py
import os
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()
# -----------------------------
# CONFIGURATION
# -----------------------------
INDEX_PATH = "faiss_index"  # Folder where your FAISS index is stored
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Step 1: Load embeddings and FAISS vector store
print("🔹 Loading FAISS index and embeddings...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
vectorstore = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# Step 2: Configure retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Step 3:LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, api_key=OPENAI_API_KEY)


# Step 4: Build RetrievalQA pipeline
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Step 5: Chat loop
print("\n🤖 RAG Chatbot ready! Ask anything about Bank of Maharashtra loan schemes.")
print("Type 'exit' to quit.\n")

while True:
    query = input("You: ").strip()
    if query.lower() in ["exit", "quit"]:
        print("👋 Exiting chatbot. Goodbye!")
        break

    try:
        result = qa_chain.invoke({"query": query})
        print(f"\nAI: {result['result']}\n")

        # Optional: show which documents were used
        print("📘 Sources:")
        for i, doc in enumerate(result["source_documents"], 1):
            meta = doc.metadata
            print(f"  {i}. {meta.get('scheme', 'Unknown Scheme')} ({meta.get('category', 'Unknown Category')})")
        print("-" * 60)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
