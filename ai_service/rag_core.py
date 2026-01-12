# ai_service/rag_core.py
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# 1. 配置数据库连接 (复用你 docker-compose 里的配置)
db_user = os.getenv("DB_USERNAME", "jobtracker")
db_password = os.getenv("DB_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "db")
db_name = os.getenv("DB_NAME", "jobtracker")

DB_CONNECTION = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}"
# 2. 初始化模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 3. 连接向量数据库 (LangChain 会自动帮你建表！)
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="job_resume_vectors",
    connection=DB_CONNECTION,
    use_jsonb=True,
)

# --- 修改点 1: 专门用于存 JD 的函数 ---
def ingest_jobs_to_vector_db(jobs_data: list):
    """
    功能：把爬虫爬到的 JD 批量存入向量库
    入参：jobs_data 是一个列表，每个元素是 dict: {'id': 1, 'title': '...', 'description': '...'}
    """
    documents = []
    for job in jobs_data:
        # 1. 构造存入向量库的内容：通常是 Title + Description
        # 这样搜索时既能搜到标题也能搜到内容
        full_text = f"Job Title: {job['title']}\nJob Description: {job['description']}"

        # 2. 构造元数据 (Metadata)：存 ID 和其他过滤字段
        # 这一点至关重要！以后你才能用 SQL 过滤 "created_at > 7 days"
        metadata = {
            "job_id": job['id'],
            "source": job.get('source', 'unknown'),
            "url": job.get('url', '')
        }

        doc = Document(page_content=full_text, metadata=metadata)
        documents.append(doc)

    if documents:
        # 批量写入，效率更高
        vector_store.add_documents(documents)
        print(f"✅ 成功存入 {len(documents)} 个岗位到 pgvector")

# --- 修改点 2: 简历匹配函数 (Job Matching) ---
def match_resume_to_jobs(resume_text: str, top_k=5):
    """
    功能：拿简历去搜职位
    """
    # 1. 直接把简历文本作为“查询词”
    # 向量数据库会自动把这就一大段话变成向量，去库里找相似的 JD
    results = vector_store.similarity_search_with_score(resume_text, k=top_k)

    matches = []
    for doc, score in results:
        matches.append({
            "job_id": doc.metadata["job_id"],
            "title": doc.page_content.split('\n')[0], # 简单提取标题
            "score": score, # 相似度分数
            "url": doc.metadata["url"]
        })

    return matches