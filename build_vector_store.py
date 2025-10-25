# build_vector_store.py
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

JSON_PATH = "loans_bom.json"
INDEX_PATH = r"D:\Test\Chatbot\faiss_index"

# Step 1: Load the JSON file
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

def flatten_json_to_docs(data):
    docs = []
    for category_key, category in data["loan_categories"].items():
        for scheme in category.get("schemes", []):
            text_parts = []
            for k, v in scheme.items():
                if isinstance(v, dict) or isinstance(v, list):
                    text_parts.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
                else:
                    text_parts.append(f"{k}: {v}")
            full_text = "\n".join(text_parts)
            docs.append(
                Document(
                    page_content=full_text,
                    metadata={"category": category["category_name"], "scheme": scheme["scheme_name"], "url": scheme["url"]}
                )
            )
    return docs

print("Flattening JSON to documents...")
docs = flatten_json_to_docs(data)

# Step 2: Split text into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks")

# Step 3: Create embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 4: Build and save FAISS vector store
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local(INDEX_PATH)

print(f"✅ Vector store built and saved at: {INDEX_PATH}")
