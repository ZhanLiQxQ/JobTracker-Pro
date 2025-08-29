import { useState, useEffect } from 'react';
import axios from 'axios';
import type { Job, JobFormValues } from '../types/job.types';

export const useJobs = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [recommendedJobs, setRecommendedJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get('/api/jobs', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
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
      const { data } = await axios.get(`/api/jobs/search?title=${encodeURIComponent(title)}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setJobs(data);
    } catch (err) {
      setError('Failed to search jobs');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendedJobs = async (query: string) => {
    setLoading(true);
    try {
      const { data } = await axios.get(`/api/jobs/recommend?query=${encodeURIComponent(query)}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setRecommendedJobs(data);
    } catch (err) {
      setError('Failed to fetch recommended jobs');
    } finally {
      setLoading(false);
    }
  };

  const addJob = async (formData: JobFormValues) => {
    try {
      const { data } = await axios.post('/api/jobs', {
        ...formData,
        status: 'APPLIED',
        appliedAt: new Date().toISOString()
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setJobs(prev => [...prev, data]);
      return true;
    } catch (err) {
      setError('Failed to add job');
      return false;
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  return { 
    jobs, 
    recommendedJobs,
    loading, 
    error, 
    addJob, 
    searchJobs,
    fetchRecommendedJobs,
    refresh: fetchJobs 
  };
};