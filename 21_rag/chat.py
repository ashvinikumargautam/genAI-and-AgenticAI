from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# retrival code
embedding_model = OpenAIEmbeddings(
    model = "text-embedding-3-small", 
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url  = 'http://localhost:6333',
    collection_name = "learning RAG"
)

# take user input
user_querry = input("Ask something : ")

# relevent chunks from vector db
search_result = vector_db.similarity_search(query=user_querry)

context = "\n\n\n".join([f"page content : {result.page_content} \n Page Number : {result.metadata['page_label']}\n file location : {result.metadata['source']}"
for result in search_result])


SYESTEM_PROMPT = f"""
you are a helpful ai assistant who answers user querry based on available context 
retrived from a PDF file along with page_contents and page number.

you should only ans the user based on the following context and navigate the user to
open the right page number to know more.
Context : {context} 
"""

openai_client = OpenAI()

response = openai_client.chat.completions.create(
    model = "gpt-5",
    messages = [
        {"role":"system","content":SYESTEM_PROMPT},
        {"role":"user","content": user_querry}
    ]
)

print("Response : ",response.choices[0].message.content)