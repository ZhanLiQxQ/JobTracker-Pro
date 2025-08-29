import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

export const useAuth = () => {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // 设置axios默认请求头
  axios.defaults.headers.common['Content-Type'] = 'application/json';

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    setError('');

    try {
      console.log('正在发送登录请求...', { email });
      const { data } = await axios.post('/api/auth/signin', {
        email,
        password
      });

      console.log('登录响应:', data);

      // 确保响应包含token
      if (!data.token) throw new Error('No token received');

      // 存储token到本地（Bearer格式）
      localStorage.setItem('token', data.token);
      // 存储用户角色
      localStorage.setItem('roles', JSON.stringify(data.roles));

      // 设置axios全局认证头
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;

      // 登录成功提示
      toast.success('登录成功！');
      navigate('/jobs');

    } catch (err: any) {
      console.error('登录错误:', err);
      console.error('错误详情:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      });

      const errorMessage = err.response?.data?.message || '登录失败，请检查账号密码!!';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email: string, password: string) => {
    setLoading(true);
    setError('');

    try {
      console.log('正在发送注册请求...', { email });
      const response = await axios.post('/api/auth/signup', {
        email,
        password
      });

      // 根据后端返回的响应显示不同的提示
      if (response.status === 200) {
        toast.success(response.data); // 显示"User registered successfully!"
        setTimeout(() => navigate('/login'), 2000); // 2秒后跳转到登录页
      }
    } catch (err: any) {
      console.error('注册错误:', err);
      console.error('错误详情:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      });

      // 显示后端返回的具体错误信息
      const errorMessage = err.response?.data || '注册失败，请重试';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { signIn, signUp, error, loading };
};