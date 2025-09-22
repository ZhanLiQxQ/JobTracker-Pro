import { Job } from '../types/Job';
import { authService } from './authService';

// Use relative path, access backend through Vite proxy
const API_BASE_URL = '/api';

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
}

export const jobService = new JobService();

