import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobList } from '../components/jobs/JobList';
import { Job } from '../types/job.types';
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';

export const JobListPage = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { signIn, error: authError, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchJobs = async () => {
      try {
        const response = await axios.get('/api/jobs', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setJobs(response.data);
      } catch (err) {
        setError('获取职位列表失败');
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [navigate]);

  const handleFavorite = async (jobId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.patch(`/api/jobs/${jobId}/favorite`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setJobs(jobs.map(job => 
        job.id === jobId ? { ...job, isFavorite: response.data.isFavorite } : job
      ));
    } catch (err) {
      setError('更新收藏状态失败');
    }
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">职位列表</h1>
      <JobList jobs={jobs} onFavorite={handleFavorite} showFavoriteButton />
    </div>
  );
};