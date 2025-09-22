# ai_service/matcher.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load your fine-tuned model from local folder
MODEL_PATH = './fine-tuned-english-bert'
print(f"Loading model from local path: {MODEL_PATH}")
model = SentenceTransformer(MODEL_PATH)
print("AI model loaded successfully! Service is ready.")

def find_best_matches(resume_text, jobs):
    """
    Input user resume and job list, return jobs sorted by match score.
    """
    print(f"find_best_matches called with resume_text length: {len(resume_text) if resume_text else 0}")
    print(f"find_best_matches called with jobs count: {len(jobs) if jobs else 0}")
    
    if not resume_text or not jobs:
        print("Empty resume_text or jobs, returning empty list")
        return []

    try:
        # Encode user resume and all job descriptions into semantic vectors
        print("Encoding resume text...")
        resume_embedding = model.encode([resume_text])
        print(f"Resume embedding shape: {resume_embedding.shape}")

        # Filter out None job objects and extract descriptions
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

        # Calculate cosine similarity
        print("Calculating similarities...")
        similarities = cosine_similarity(resume_embedding, job_embeddings)
        print(f"Similarities shape: {similarities.shape}")

        # Sort and return results
        job_scores = []
        for i, job in enumerate(valid_jobs):
            if i < similarities.shape[1]:  # Ensure index does not go out of bounds
                score = similarities[0][i]
                # Attach match score to original job object
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