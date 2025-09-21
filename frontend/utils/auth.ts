import { api } from './api';

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const login = async (credentials: LoginCredentials) => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await api.post&lt;AuthResponse>('/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  localStorage.setItem('token', response.data.access_token);
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  window.location.href = '/login';
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};