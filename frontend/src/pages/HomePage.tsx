import { useState, useEffect } from 'react';
import { JobList } from '../components/jobs/JobList';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

export const HomePage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get('/api/jobs');
      setJobs(data);
    } catch (err) {
      setError('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const searchJobs = async (title: string) => {
    setLoading(true);
    try {
      const { data } = await axios.get(`/api/jobs?title=${encodeURIComponent(title)}`);
      setJobs(data);
    } catch (err) {
      setError('Failed to search jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = async (jobId: number) => {
    if (!isLoggedIn) {
      toast.info('请先登录');
      navigate('/login');
      return;
    }

    try {
      await axios.post(`/api/jobs/${jobId}/favorite`);
      toast.success('已添加到收藏');
      fetchJobs(); // 刷新列表
    } catch (err) {
      toast.error('添加收藏失败');
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchJobs(searchQuery);
    } else {
      fetchJobs();
    }
  };

  if (loading) return <div className="p-4 text-center">加载中...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">职位列表</h1>
        {!isLoggedIn && (
          <button 
            onClick={() => navigate('/login')}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            登录
          </button>
        )}
      </div>

      {/* 搜索栏 */}
      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索职位..."
            className="flex-1 p-2 border rounded"
          />
          <button 
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            搜索
          </button>
        </form>
      </div>

      {/* 职位列表 */}
      <div>
        <h2 className="text-xl font-semibold mb-3">所有职位</h2>
        <JobList 
          jobs={jobs} 
          onFavorite={handleFavorite}
          showFavoriteButton={true}
        />
      </div>
    </div>
  );
};