# ai_service/api.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import docx
import io
import os

# --- 从 rag_core 导入组件 ---
from rag_core import ingest_jobs_to_vector_db, vector_store, llm
from langchain.schema import HumanMessage, SystemMessage

app = Flask(__name__)
# 允许跨域，方便前端调试
CORS(app)

# ==========================================
# 1. 修改工具函数：不再接收流，而是直接接收 bytes 数据
# ==========================================
def extract_text(file_bytes, filename):
    """
    从文件字节流中提取纯文本
    :param file_bytes: 文件的二进制内容 (bytes)
    :param filename: 文件名 (用于判断类型)
    """
    text = ""
    try:
        if filename.lower().endswith('.pdf'):
            # fitz.open 直接接收 bytes
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()

        elif filename.lower().endswith('.docx'):
            # python-docx 需要一个“类文件对象”，所以我们要用 io.BytesIO 包装一下 bytes
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + '\n'
        else:
            return None
    except Exception as e:
        print(f"❌ 解析文件底层报错: {e}")
        # 这里可以把具体的报错抛出去，方便排查
        raise e
    return text



def perform_vector_search(query_text, top_k=3):
    """
    通用搜索逻辑：只负责查向量库，不负责 AI 生成。
    速度极快。
    """
    if not query_text:
        return []

    print(f"🔍 [RAG] 正在检索: {query_text[:50]}...", flush=True)

    # 1. 向量搜索
    results = vector_store.similarity_search_with_score(query_text, k=top_k)

    recommendations = []
    for doc, score in results:
        # 提取数据
        recommendations.append({
            "job_id": doc.metadata.get('job_id'),
            "title": doc.page_content.split('\n')[0], # 简单提取第一行作为标题
            "description": doc.page_content,           # 完整内容，前端稍后需要传回给 AI 接口
            "match_score": float(score),               # 相似度分数
            "url": doc.metadata.get('url'),
            "source": doc.metadata.get('source'),
            "ai_reason": None                          # 占位符，由前端后续填充
        })

    return recommendations

# ==========================================
# 2. 核心路由接口
# ==========================================

# --- 接口 A: 数据入库 (爬虫调用) ---
@app.route('/rag/ingest_jobs', methods=['POST'])
def rag_ingest_jobs():
    data = request.json
    jobs = data.get('jobs') # 这是一个 List

    if not jobs:
        return jsonify({"error": "No jobs provided"}), 400

    try:
        # 调用 rag_core 里的函数存入 Postgres
        ingest_jobs_to_vector_db(jobs)
        return jsonify({"status": "success", "count": len(jobs)})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# --- 接口 B: 文本快速搜索 (前端：用户输入关键词时调用) ---
@app.route('/rag/search_only', methods=['POST'])
def search_only_endpoint():
    data = request.json
    query_text = data.get('query', '')
    top_k = data.get('k', 3)

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # 只执行快速检索
    results = perform_vector_search(query_text, top_k)
    return jsonify({"results": results})



# ==========================================
# 2. 修改路由接口：先读取 bytes，确保不为空
# ==========================================
@app.route('/recommend_file', methods=['POST'])
def recommend_from_file():
    if 'resume_file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['resume_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        print(f"📄 接收到文件: {file.filename}")

        # --- 关键修改点 ---
        # 1. 显式地读取文件内容到内存
        file_content = file.read()

        # 2. 打印文件大小，这是最重要的调试信息！
        # 如果这里打印是 0，说明文件根本没传上来，或者流坏了
        file_size = len(file_content)
        print(f"📊 文件大小: {file_size} bytes")

        if file_size == 0:
            return jsonify({"error": "Uploaded file is empty"}), 400

        # 3. 把读好的 bytes 传给解析函数
        resume_text = extract_text(file_content, file.filename)

        if not resume_text:
            return jsonify({"error": "Could not extract text from file"}), 400

        print(f"✅ 成功提取文本，长度: {len(resume_text)}")

        # 4. 快速检索
        results = perform_vector_search(resume_text, top_k=5)

        return jsonify({
            "results": results,
            "extracted_text_snippet": resume_text[:200],
            "full_resume_text": resume_text
        })

    except Exception as e:
        print(f"⚠️ 处理过程异常: {e}")
        import traceback
        traceback.print_exc() # 打印完整堆栈，方便看哪一行错了
        return jsonify({"error": str(e)}), 500


# --- 接口 D: AI 解释 (前端：拿到列表后，异步/懒加载调用) ---
@app.route('/rag/explain_job', methods=['POST'])
def explain_job_endpoint():
    data = request.json
    # 前端必须把这两样东西传回来，因为服务器是无状态的
    job_desc = data.get('job_description', '')
    user_query = data.get('user_query', '') # 用户的搜索词 或 简历全文

    if not job_desc or not user_query:
        return jsonify({"error": "Missing params"}), 400

    print(f"🤖 [AI] 正在生成解释...", flush=True)

    try:
        # 构造 Prompt：限制字数，聚焦匹配点
        prompt = f"""
        【用户背景】
        {user_query[:600]}... (截取部分)

        【目标岗位】
        {job_desc[:800]}... (截取部分)

        【任务】
        请用英语，用一句话（50字以内）像专业的猎头顾问一样，告诉用户为什么这个岗位适合他。
        请直接输出结论，不要说“根据您的简历”之类的废话。
        """

        # 调用 LLM
        response = llm.invoke([
            SystemMessage(content="你是一个精准、干练的职业顾问。"),
            HumanMessage(content=prompt)
        ])

        return jsonify({"ai_reason": response.content})

    except Exception as e:
        print(f"⚠️ AI 生成失败: {e}", flush=True)
        return jsonify({"ai_reason": "AI 分析暂时不可用（额度不足或网络波动）"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)