import { useState, useEffect } from 'react';
import { JobList } from '../components/jobs/JobList';
import { JobForm } from '../components/jobs/JobForm';
import { useJobs } from '../hooks/useJob';

export const JobsPage = () => {
  const { 
    jobs, 
    recommendedJobs,
    loading, 
    error, 
    addJob, 
    fetchRecommendedJobs 
  } = useJobs();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showRecommended, setShowRecommended] = useState(false);

  const handleRecommend = () => {
    if (searchQuery.trim()) {
      fetchRecommendedJobs(searchQuery);
      setShowRecommended(true);
    }
  };

  if (loading) return <div className="p-4 text-center">加载中...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">我的职位管理</h1>

      {/* 推荐搜索 */}
      <div className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="输入关键词获取职位推荐..."
            className="flex-1 p-2 border rounded"
          />
          <button 
            type="button"
            onClick={handleRecommend}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            获取推荐
          </button>
        </div>
      </div>

      {/* 推荐职位 */}
      {showRecommended && recommendedJobs.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-3">推荐职位</h2>
          <JobList jobs={recommendedJobs} />
        </div>
      )}

      {/* 添加新职位 */}
      <div className="mb-8 p-4 bg-white rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-3">添加新职位</h2>
        <JobForm onSubmit={addJob} />
      </div>

      {/* 我的职位列表 */}
      <div>
        <h2 className="text-xl font-semibold mb-3">我的申请记录</h2>
        <JobList jobs={jobs} />
      </div>
    </div>
  );
};