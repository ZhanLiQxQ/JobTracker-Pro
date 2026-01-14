# ai_service/rag_core.py
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# 1. Configure database connection (reuse configuration from docker-compose)
db_user = os.getenv("DB_USERNAME", "jobtracker")
db_password = os.getenv("DB_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "db")
db_name = os.getenv("DB_NAME", "jobtracker")

DB_CONNECTION = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}"
# 2. Initialize models
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 3. Connect to vector database (LangChain will automatically create tables for you!)
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="job_resume_vectors",
    connection=DB_CONNECTION,
    use_jsonb=True,
)

# --- Modification point 1: Function specifically for storing job descriptions ---
def ingest_jobs_to_vector_db(jobs_data: list):
    """
    Function: Batch store job descriptions scraped by crawler into vector database
    Input: jobs_data is a list, each element is a dict: {'id': 1, 'title': '...', 'description': '...'}
    """
    documents = []
    for job in jobs_data:
        # 1. Construct content to store in vector database: usually Title + Description
        # This way searches can find both title and content
        full_text = f"Job Title: {job['title']}\nJob Description: {job['description']}"

        # 2. Construct metadata: store ID and other filter fields
        # This is crucial! Later you can use SQL to filter like "created_at > 7 days"
        metadata = {
            "job_id": job['id'],
            "source": job.get('source', 'unknown'),
            "url": job.get('url', '')
        }

        doc = Document(page_content=full_text, metadata=metadata)
        documents.append(doc)

    if documents:
        # Batch write for better efficiency
        vector_store.add_documents(documents)
        print(f"Successfully stored {len(documents)} jobs to pgvector")

# --- Modification point 2: Resume matching function (Job Matching) ---
def match_resume_to_jobs(resume_text: str, top_k=5):
    """
    Function: Search for jobs using resume
    """
    # 1. Directly use resume text as "query"
    # Vector database will automatically convert this large text into vectors and find similar job descriptions in the database
    results = vector_store.similarity_search_with_score(resume_text, k=top_k)

    matches = []
    for doc, score in results:
        matches.append({
            "job_id": doc.metadata["job_id"],
            "title": doc.page_content.split('\n')[0], # Simple title extraction
            "score": score, # Similarity score
            "url": doc.metadata["url"]
        })

    return matches