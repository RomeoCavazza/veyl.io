import axios from 'axios';

// Create axios instance
export const api = axios.create({
  baseURL: (import.meta.env && import.meta.env.VITE_API_URL) || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized (optional: redirect to login)
    if (error.response?.status === 401) {
      // localStorage.removeItem('token');
      // window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Custom mutator for Orval
export const customInstance = <T>(config: any, options?: any): Promise<T> => {
  const source = axios.CancelToken.source();
  const promise = api({
    ...config,
    ...options,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-ignore
  promise.cancel = () => {
    source.cancel('Query was cancelled');
  };

  return promise;
};
