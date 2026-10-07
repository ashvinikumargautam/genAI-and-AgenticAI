from pathlib import Path
from dotenv import load_dotenv

# Load .env from D:\genAI&AgenticAI\.env
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

openai_client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model = "text-embedding-3-small", 
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url  = 'http://localhost:6333',
    collection_name = "learning RAG"
)


def process_query(query:str):
    print("searching chunk")
    search_result = vector_db.similarity_search(query=query)
    context = "\n\n\n".join([f"page content : {result.page_content} \n Page Number : {result.metadata['page_label']}\n file location : {result.metadata['source']}" for result in search_result])
    SYESTEM_PROMPT = f"""
    you are a helpful ai assistant who answers user querry based on available context 
    retrived from a PDF file along with page_contents and page number.

    you should only ans the user based on the following context and navigate the user to
    open the right page number to know more.
    Context : {context} 
    """
    response = openai_client.chat.completions.create(
        model = "gpt-5",
        messages = [
            {"role":"system","content":SYESTEM_PROMPT},
            {"role":"user","content": query}
        ]
) 
    print("response : ", response.choices[0].message.content)
    return response.choices[0].message.content
