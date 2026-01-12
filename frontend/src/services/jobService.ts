import { Job } from '../types/Job';
import { authService } from './authService';

// Use relative path, access backend through Vite proxy
const API_BASE_URL = '/api';
// Python AI 服务地址
const AI_SERVICE_URL = 'http://localhost:5001';
class JobService {
  async getAllJobs(query: string = '', url: string = ''): Promise<Job[]> {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (url) params.append('url', url);

    const response = await fetch(`${API_BASE_URL}/jobs?${params.toString()}`);
    if (!response.ok) {
      throw new Error('Failed to load jobs');
    }

    const jobs: Job[] = await response.json();
    
    // If user is logged in, get favorite status
    if (authService.isAuthenticated()) {
      try {
        const favorites = await this.getUserFavorites();
        const favoriteJobIds = new Set(favorites.map(job => job.id));
        
        return jobs.map(job => ({
          ...job,
          isFavorite: favoriteJobIds.has(job.id)
        }));
      } catch (error) {
        console.error('Failed to get favorite status:', error);
        return jobs;
      }
    }

    return jobs;
  }

  async getUserFavorites(): Promise<Job[]> {
    const response = await fetch(`${API_BASE_URL}/jobs/favorites`, {
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to load favorites');
    }

    const jobs: Job[] = await response.json();
    return jobs.map(job => ({ ...job, isFavorite: true }));
  }

  async addToFavorites(jobId: number, notes?: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/favorite`, {
      method: 'POST',
      headers: {
        ...authService.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: notes ? JSON.stringify(notes) : "{}",
    });

    if (!response.ok) {
      throw new Error('Failed to add to favorites');
    }
  }

  async removeFromFavorites(jobId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/favorite`, {
      method: 'DELETE',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to remove from favorites');
    }
  }

  async getRecommendationsFromResume(file: File): Promise<Job[]> {
    const formData = new FormData();
    formData.append('resume', file);

    const response = await fetch(`${API_BASE_URL}/jobs/recommend-file`, {
      method: 'POST',
      headers: authService.getAuthHeaders(),
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to get job recommendations');
    }

    const recommendedJobs: Job[] = await response.json();
    
    // If user is logged in, get favorite status
    if (authService.isAuthenticated()) {
      try {
        const favorites = await this.getUserFavorites();
        const favoriteJobIds = new Set(favorites.map(job => job.id));
        
        return recommendedJobs.map(job => ({
          ...job,
          isFavorite: favoriteJobIds.has(job.id)
        }));
      } catch (error) {
        console.error('Failed to get favorite status:', error);
        return recommendedJobs;
      }
    }

    return recommendedJobs;
  }
  // --- 新增：调用 Python 接口上传简历 ---
  // 返回值不仅包含 Job 数组，还包含简历全文文本，供后续 AI 分析使用
  async uploadResumeToAI(file: File): Promise<{ jobs: Job[], resumeText: string }> {
    const formData = new FormData();
    formData.append('resume_file', file); // 对应 Python 的 request.files['resume_file']

    const response = await fetch(`${AI_SERVICE_URL}/recommend_file`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'AI Service Upload failed');
    }

    const data = await response.json();

    // 映射 Python 数据结构 -> 前端 Job 结构
    const mappedJobs: Job[] = data.results.map((item: any) => ({
      id: item.job_id,
      title: item.title,
      company: "Unknown Company", // Python 目前没爬取公司名，暂时写死
      location: "Remote/Hybrid",  // Python 目前没爬取地点
      source: item.source || "AI Match",
      url: item.url,
      description: item.description,
      matchScore: item.match_score,
      aiReason: null, // 初始化为 null，表示等待 AI 生成
      isFavorite: false // 默认为 false，如果需要同步状态需额外调用 Java 接口
    }));

    return {
      jobs: mappedJobs,
      resumeText: data.full_resume_text // 这是关键，下一步要传回去
    };
  }

  // --- 新增：单独请求 AI 解释 ---
  async getAIExplanation(jobDescription: string, resumeText: string): Promise<string> {
    const response = await fetch(`${AI_SERVICE_URL}/rag/explain_job`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        job_description: jobDescription,
        user_query: resumeText
      })
    });

    if (!response.ok) {
      return "AI analysis unavailable";
    }

    const data = await response.json();
    return data.ai_reason || "No reason provided";
  }


}

export const jobService = new JobService();

