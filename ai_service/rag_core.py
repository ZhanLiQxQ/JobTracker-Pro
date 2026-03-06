# ai_service/rag_core.py
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Configure database connection (reuse configuration from docker-compose)
db_user = os.getenv("DB_USERNAME", "jobtracker")
db_password = os.getenv("DB_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "db")
db_name = os.getenv("DB_NAME", "jobtracker")

DB_CONNECTION = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}"
# 2. Initialize models
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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

# ==========================================
# Agent Core Module and Tool Definitions
# ==========================================

# Tool 1: Job Search Tool
@tool
def search_jobs_tool(query: str) -> str:
    """
    You must call this tool when the user needs to find a job, match job positions, or ask about suitable open roles.
    Input the user's expectations (e.g., "Java Backend Development"), and it will return matching job information from the vector database.
    """
    print(f"[Agent Tool] Searching jobs for: {query}")
    results = vector_store.similarity_search_with_score(query, k=3)

    if not results:
        return "No matching jobs found."

    formatted_results = []
    for doc, score in results:
        title = doc.page_content.split('\n')[0]
        # Truncate to first 150 chars to avoid token limit issues
        desc = doc.page_content[:150]
        formatted_results.append(f"Job Title: {title}\nMatch Score: {score:.2f}\nDetails: {desc}...")

    return "\n\n".join(formatted_results)

# Tool 2: Skill Gap Analysis Tool
@tool
def analyze_skill_gap_tool(user_background: str, target_job_requirements: str) -> str:
    """
    Call this tool when the user asks about the gap between their profile and a specific job, their pros/cons, or asks "what else do I need to learn".
    Input the user's background information and the target job requirements, and it will return a detailed skill gap analysis.
    """
    print(f"[Agent Tool] Analyzing skill gap...")
    prompt = f"User Background: {user_background}\nTarget Job Requirements: {target_job_requirements}\nPlease use professional and concise language to point out the user's core strengths and the skill gaps they still need to fill."
    response = llm.invoke(prompt)
    return response.content

# 5. Bind tools and assemble Agent
tools = [search_jobs_tool, analyze_skill_gap_tool]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior AI Career Planner (Agent).
You have access to tools for searching job positions and analyzing resume skill gaps.
Based on the user's input and background, autonomously decide which tools to call to perfectly answer the user's questions.
If you encounter job information you do not know, you must prioritize using the tools to query.
Please respond to the user in a professional and encouraging tone."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

job_agent = create_tool_calling_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=job_agent, tools=tools, verbose=True)