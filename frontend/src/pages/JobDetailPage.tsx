import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { JobDetail } from '../components/jobs/JobDetail';
import {useAuth} from "../hooks/useAuth";
import {Job} from "../types/job.types";
import api from "../api/axios";


export const JobDetailPage = () => {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    const fetchJob = async () => {
      try {
        const response = await api.get(`/jobs/${id}`);
        setJob(response.data);
      } catch (err) {
        setError('获取职位详情失败');
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
  }, [id, user, navigate]);

  const handleFavorite = async () => {
    if (!job) return;
    
    try {
      const response = await api.patch(`/jobs/${job.id}/favorite`);
      setJob({ ...job, isFavorite: response.data.isFavorite });
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

  if (!job) {
    return <div>职位不存在</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <JobDetail job={job} onFavorite={handleFavorite} showFavoriteButton />
    </div>
  );
};