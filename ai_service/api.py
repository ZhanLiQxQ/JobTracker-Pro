# ai_service/api.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import docx
import io
import os

# --- Import components from rag_core ---
from rag_core import ingest_jobs_to_vector_db, vector_store, llm, agent_executor
from langchain.schema import HumanMessage, SystemMessage

app = Flask(__name__)
# Enable CORS for frontend debugging
CORS(app)

# ==========================================
# 1. Modified utility function: receive bytes data directly instead of stream
# ==========================================
def extract_text(file_bytes, filename):
    """
    Extract plain text from file bytes
    :param file_bytes: Binary content of the file (bytes)
    :param filename: Filename (used to determine file type)
    """
    text = ""
    try:
        if filename.lower().endswith('.pdf'):
            # fitz.open accepts bytes directly
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()

        elif filename.lower().endswith('.docx'):
            # python-docx requires a file-like object, so we wrap bytes with io.BytesIO
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + '\n'
        else:
            return None
    except Exception as e:
        print(f"Error parsing file: {e}")
        # Throw the specific error for troubleshooting
        raise e
    return text



def perform_vector_search(query_text, top_k=3):
    """
    General search logic: only responsible for querying vector database, not AI generation.
    Very fast.
    """
    if not query_text:
        return []

    print(f"[RAG] Searching: {query_text[:50]}...", flush=True)

    # 1. Vector search
    results = vector_store.similarity_search_with_score(query_text, k=top_k)

    recommendations = []
    for doc, score in results:
        # Extract data
        recommendations.append({
            "job_id": doc.metadata.get('job_id'),
            "title": doc.page_content.split('\n')[0], # Simple extraction of first line as title
            "description": doc.page_content,           # Full content, frontend will pass this back to AI interface later
            "match_score": float(score),               # Similarity score
            "url": doc.metadata.get('url'),
            "source": doc.metadata.get('source'),
            "ai_reason": None                          # Placeholder, to be filled by frontend later
        })

    return recommendations

# ==========================================
# 2. Core route interfaces
# ==========================================

# --- Interface A: Data ingestion (called by crawler) ---
@app.route('/rag/ingest_jobs', methods=['POST'])
def rag_ingest_jobs():
    data = request.json
    jobs = data.get('jobs') # This is a List

    if not jobs:
        return jsonify({"error": "No jobs provided"}), 400

    try:
        # Call function in rag_core to save to Postgres
        ingest_jobs_to_vector_db(jobs)
        return jsonify({"status": "success", "count": len(jobs)})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# --- Interface B: Fast text search (frontend: called when user enters keywords) ---
@app.route('/rag/search_only', methods=['POST'])
def search_only_endpoint():
    data = request.json
    query_text = data.get('query', '')
    top_k = data.get('k', 3)

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # Only perform fast retrieval
    results = perform_vector_search(query_text, top_k)
    return jsonify({"results": results})



# ==========================================
# 2. Modified route interface: read bytes first, ensure not empty
# ==========================================
@app.route('/recommend_file', methods=['POST'])
def recommend_from_file():
    if 'resume_file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['resume_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        print(f"Received file: {file.filename}")

        # --- Key modification point ---
        # 1. Explicitly read file content into memory
        file_content = file.read()

        # 2. Print file size, this is the most important debug information!
        # If this prints 0, it means the file was not uploaded or the stream is broken
        file_size = len(file_content)
        print(f"File size: {file_size} bytes")

        if file_size == 0:
            return jsonify({"error": "Uploaded file is empty"}), 400

        # 3. Pass the read bytes to the parsing function
        resume_text = extract_text(file_content, file.filename)

        if not resume_text:
            return jsonify({"error": "Could not extract text from file"}), 400

        print(f"Successfully extracted text, length: {len(resume_text)}")

        # 4. Fast retrieval
        results = perform_vector_search(resume_text, top_k=5)

        return jsonify({
            "results": results,
            "extracted_text_snippet": resume_text[:200],
            "full_resume_text": resume_text
        })

    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc() # Print full stack trace to see which line failed
        return jsonify({"error": str(e)}), 500


# --- Interface D: AI explanation (frontend: called asynchronously/lazy-loaded after getting list) ---
@app.route('/rag/agent_chat', methods=['POST'])
def agent_chat_endpoint():
    data = request.json
    user_input = data.get('query', '')

    # 接收前端传过来的解析后的简历文本（如果没有传，就是空字符串）
    resume_text = data.get('resume_text', '')

    if not user_input:
        return jsonify({"error": "请输入你的求职需求"}), 400

    # 动态组装 Agent 的输入：把简历作为上帝视角的“背景”塞进去
    agent_input = user_input
    if resume_text:
        # 截取前 2000 个字符防超载
        agent_input = f"以下是我的个人简历背景：\n---\n{resume_text[:2000]}\n---\n我的问题/需求是：{user_input}"

    print(f"\n[Agent API] 收到用户请求，启动 Agent...", flush=True)

    try:
        # 启动 Agent
        result = agent_executor.invoke({"input": agent_input})

        return jsonify({
            "status": "success",
            "agent_response": result["output"]
        })
    except Exception as e:
        print(f"Agent 执行失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- (可选保留) 旧的单点解释接口，为了兼容老前端代码 ---
@app.route('/rag/explain_job', methods=['POST'])
def explain_job_endpoint():
    data = request.json
    job_desc = data.get('job_description', '')
    user_query = data.get('user_query', '')
    if not job_desc or not user_query:
        return jsonify({"error": "Missing params"}), 400
    try:
        prompt = f"[User Background]\n{user_query[:600]}...\n[Target Position]\n{job_desc[:800]}...\nPlease use English, in one sentence (within 50 words) like a professional headhunter consultant, tell the user why this position is suitable for them."
        response = llm.invoke([SystemMessage(content="You are a precise and concise career consultant."), HumanMessage(content=prompt)])
        return jsonify({"ai_reason": response.content})
    except Exception as e:
        return jsonify({"ai_reason": "AI analysis temporarily unavailable"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)