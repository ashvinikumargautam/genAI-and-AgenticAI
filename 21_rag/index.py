from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

pdf_path = Path(__file__).parent/"iso27001.pdf"

# Load this file in current progrram

# Initialize the loader with your PDF path
loader = PyPDFLoader( file_path= pdf_path)

# Load all pages as a list of Documents
docs = loader.load()

# split the docs into smaller chunks 
text_splitter =  RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 400
)

chunks = text_splitter.split_documents(documents=docs)

# vector embeddings

embedding_model = OpenAIEmbeddings(
    model = "text-embedding-3-small", 
)

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url  = 'http://localhost:6333',
    collection_name = "learning RAG"
)

print("indexing of documents done....")