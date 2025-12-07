import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => 
    axios.post(`${API_BASE_URL}/token/`, { email, password }),
  
  register: (userData) => 
    axios.post(`${API_BASE_URL}/register/`, userData),
};

// Notes API
export const notesAPI = {
  getPublicNotes: (params) => 
    api.get('/notes/public_notes/', { params }),
  
  getMyNotes: (params) => 
    api.get('/notes/my_notes/', { params }),
  
  getNote: (id) => 
    api.get(`/notes/${id}/`),
  
  createNote: (data) => 
    api.post('/notes/', data),
  
  updateNote: (id, data) => 
    api.patch(`/notes/${id}/`, data),
  
  deleteNote: (id) => 
    api.delete(`/notes/${id}/`),
  
  voteNote: (id, voteType) => 
    api.post(`/notes/${id}/vote/`, { vote_type: voteType }),
  
  getNoteHistory: (id) => 
    api.get(`/notes/${id}/history/`),
  
  restoreNote: (id, historyId) => 
    api.post(`/notes/${id}/restore/`, { history_id: historyId }),
};

// Tags API
export const tagsAPI = {
  getTags: (params) => 
    api.get('/tags/', { params }),
};

// Workspaces API
export const workspacesAPI = {
  getWorkspaces: (params) => 
    api.get('/workspaces/', { params }),
  
  getWorkspace: (id) => 
    api.get(`/workspaces/${id}/`),
  
  createWorkspace: (data) => 
    api.post('/workspaces/', data),
  
  updateWorkspace: (id, data) => 
    api.patch(`/workspaces/${id}/`, data),
  
  deleteWorkspace: (id) => 
    api.delete(`/workspaces/${id}/`),
};

// Companies API
export const companiesAPI = {
  getCompanies: (params) => 
    api.get('/companies/', { params }),
  
  getCompany: (id) => 
    api.get(`/companies/${id}/`),
};

export default api;