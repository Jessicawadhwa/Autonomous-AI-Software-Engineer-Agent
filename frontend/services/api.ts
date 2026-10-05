import axios from 'axios';
import { Project, LLMSettings, DashboardStats, FileNode } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const projectApi = {
  list: async (): Promise<Project[]> => {
    const res = await api.get('/projects');
    return res.data;
  },

  create: async (data: {
    name: string;
    description?: string;
    requirement: string;
    options?: Record<string, any>;
    provider?: string;
    api_key?: string;
    model?: string;
  }): Promise<Project> => {
    const res = await api.post('/projects', data);
    return res.data;
  },

  get: async (id: string) => {
    const res = await api.get(`/projects/${id}`);
    return res.data;
  },

  delete: async (id: string) => {
    const res = await api.delete(`/projects/${id}`);
    return res.data;
  },

  startRun: async (id: string, config?: { provider?: string; api_key?: string; model?: string }) => {
    const res = await api.post(`/projects/${id}/run`, config);
    return res.data;
  },

  stopRun: async (id: string) => {
    const res = await api.post(`/projects/${id}/stop`);
    return res.data;
  },

  resolveApproval: async (projectId: string, approvalId: string, decision: 'approve' | 'reject') => {
    const res = await api.post(`/projects/${projectId}/approvals/${approvalId}`, { decision });
    return res.data;
  },

  getFiles: async (projectId: string): Promise<FileNode[]> => {
    const res = await api.get(`/projects/${projectId}/files`);
    return res.data;
  },

  getFileContent: async (projectId: string, path: string): Promise<{ content: string; path: string }> => {
    const res = await api.get(`/projects/${projectId}/files/content`, { params: { path } });
    return res.data;
  },

  saveFileContent: async (projectId: string, path: string, content: string) => {
    const res = await api.post(`/projects/${projectId}/files/content`, { path, content });
    return res.data;
  },

  getDownloadUrl: (id: string) => `/api/projects/${id}/download`,

  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/projects/dashboard/stats');
    return res.data;
  }
};

export const settingsApi = {
  get: async (): Promise<LLMSettings> => {
    const res = await api.get('/settings');
    return res.data;
  },

  update: async (settings: LLMSettings): Promise<LLMSettings> => {
    const res = await api.post('/settings', settings);
    return res.data;
  },

  testConnection: async (settings: LLMSettings) => {
    const res = await api.post('/settings/test-connection', settings);
    return res.data;
  }
};

export const mcpApi = {
  getTools: async () => {
    const res = await api.get('/mcp/tools');
    return res.data;
  },

  callTool: async (name: string, args: Record<string, any>) => {
    const res = await api.post('/mcp/call', { name, arguments: args });
    return res.data;
  }
};

export default api;
