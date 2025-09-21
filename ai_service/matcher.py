# ai_service/matcher.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 从本地文件夹加载您微调好的模型
MODEL_PATH = './fine-tuned-english-bert'
print(f"正在从本地路径加载模型: {MODEL_PATH}")
model = SentenceTransformer(MODEL_PATH)
print("AI模型加载成功！服务已准备就绪。")

def find_best_matches(resume_text, jobs):
    """
    输入用户简历和职位列表，返回按匹配度排序的职位。
    """
    print(f"find_best_matches called with resume_text length: {len(resume_text) if resume_text else 0}")
    print(f"find_best_matches called with jobs count: {len(jobs) if jobs else 0}")
    
    if not resume_text or not jobs:
        print("Empty resume_text or jobs, returning empty list")
        return []

    try:
        # 将用户简历和所有职位描述，都编码成语义向量
        print("Encoding resume text...")
        resume_embedding = model.encode([resume_text])
        print(f"Resume embedding shape: {resume_embedding.shape}")

        # 过滤掉None的job对象，并提取描述
        valid_jobs = []
        job_descriptions = []
        for i, job in enumerate(jobs):
            if job is None:
                print(f"Warning: job at index {i} is None, skipping")
                continue
            if not isinstance(job, dict):
                print(f"Warning: job at index {i} is not a dict, skipping")
                continue
            valid_jobs.append(job)
            description = job.get('description', '') if job else ''
            job_descriptions.append(description)
        
        print(f"Valid jobs count: {len(valid_jobs)}")
        print(f"Job descriptions count: {len(job_descriptions)}")
        
        if not job_descriptions:
            print("No valid job descriptions found")
            return []

        print("Encoding job descriptions...")
        job_embeddings = model.encode(job_descriptions)
        print(f"Job embeddings shape: {job_embeddings.shape}")

        # 计算余弦相似度
        print("Calculating similarities...")
        similarities = cosine_similarity(resume_embedding, job_embeddings)
        print(f"Similarities shape: {similarities.shape}")

        # 排序并返回结果
        job_scores = []
        for i, job in enumerate(valid_jobs):
            if i < similarities.shape[1]:  # 确保索引不越界
                score = similarities[0][i]
                # 将匹配分数附加到原始job对象上
                job_with_score = job.copy()
                job_with_score['matchScore'] = float(score)
                job_scores.append(job_with_score)

        print(f"Generated {len(job_scores)} job scores")
        sorted_jobs = sorted(job_scores, key=lambda x: x['matchScore'], reverse=True)
        print(f"Returning {len(sorted_jobs)} sorted jobs")

        return sorted_jobs
        
    except Exception as e:
        print(f"Error in find_best_matches: {e}")
        import traceback
        traceback.print_exc()
        raise