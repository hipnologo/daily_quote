import axios from 'axios'

// Use relative URL - Nginx will proxy /api to the backend
const API_BASE_URL = '/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token && token !== 'mock_token') {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors - don't redirect, let the AuthContext handle it
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      // Don't redirect here - let AuthContext manage auth state
    }
    return Promise.reject(error)
  }
)

// Types
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'editor' | 'viewer'
  is_active: boolean
  created_at: string
  last_login?: string
}

export interface Quote {
  id: number
  text: string
  author: string
  language: string
  category?: string
  created_at: string
  updated_at: string
}

export interface QuoteFile {
  filename: string
  path: string
  size: number
  modified: string
  lines: number
}

export interface SentimentStats {
  total_analyzed: number
  positive_count: number
  negative_count: number
  neutral_count: number
  average_compound: number
  distribution: {
    positive: number
    negative: number
    neutral: number
  }
}

export interface SystemHealth {
  status: string
  uptime: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  database_status: string
}

// API Services
export const authApi = {
  login: async (username: string, password: string): Promise<{ access_token: string; user: User }> => {
    // OAuth2PasswordRequestForm expects form data, not JSON
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    // API returns { user, token: { access_token, ... } }
    return {
      access_token: response.data.token.access_token,
      user: response.data.user
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },
}

export const quotesApi = {
  getQuotes: async (params?: {
    skip?: number
    limit?: number
    search?: string
    language?: string
    category?: string
  }): Promise<{ quotes: Quote[]; total: number }> => {
    const response = await api.get('/quotes/', { params })
    // API returns array directly, wrap it
    const quotes = Array.isArray(response.data) ? response.data : response.data.quotes || []
    return {
      quotes,
      total: quotes.length
    }
  },

  getQuote: async (id: number): Promise<Quote> => {
    const response = await api.get(`/quotes/${id}`)
    return response.data
  },

  createQuote: async (quote: Omit<Quote, 'id' | 'created_at' | 'updated_at'>): Promise<Quote> => {
    const response = await api.post('/quotes', quote)
    return response.data
  },

  updateQuote: async (id: number, quote: Partial<Quote>): Promise<Quote> => {
    const response = await api.put(`/quotes/${id}`, quote)
    return response.data
  },

  deleteQuote: async (id: number): Promise<void> => {
    await api.delete(`/quotes/${id}`)
  },

  getStats: async (): Promise<{
    total_quotes: number
    languages: number
    authors: number
    categories: number
  }> => {
    const response = await api.get('/quotes/stats')
    return response.data
  },

  importQuotes: async (file: File, language: string): Promise<{ imported: number; duplicates: number }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)
    
    const response = await api.post('/quotes/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
}

export const filesApi = {
  getFiles: async (): Promise<{ files: QuoteFile[] }> => {
    const response = await api.get('/files')
    return response.data
  },

  getFileContent: async (filename: string): Promise<{
    filename: string
    quote_count: number
    quotes: string[]
    total_lines: number
  }> => {
    const response = await api.get(`/files/${filename}`)
    return response.data
  },

  backupFile: async (filename: string): Promise<{ message: string }> => {
    const response = await api.post(`/files/${filename}/backup`)
    return response.data
  },
}

export const sentimentApi = {
  getStats: async (): Promise<SentimentStats> => {
    const response = await api.get('/sentiment/stats')
    return response.data
  },

  startAnalysis: async (language: string = 'en', forceReanalyze: boolean = false): Promise<{
    job_id: string
    status: string
    progress: number
    message: string
  }> => {
    const response = await api.post('/sentiment/analyze', null, {
      params: { language, force_reanalyze: forceReanalyze }
    })
    return response.data
  },

  getJobStatus: async (jobId: string): Promise<{
    job_id: string
    status: string
    progress: number
    message: string
  }> => {
    const response = await api.get(`/sentiment/jobs/${jobId}`)
    return response.data
  },

  getDistribution: async (language?: string, author?: string): Promise<{
    distribution: Record<string, number>
    total: number
    counts: Record<string, number>
  }> => {
    const response = await api.get('/sentiment/distribution', {
      params: { language, author }
    })
    return response.data
  },
}

export const systemApi = {
  getHealth: async (): Promise<SystemHealth> => {
    const response = await api.get('/system/health')
    return response.data
  },

  getProcesses: async (): Promise<Array<{
    name: string
    status: string
    last_run: string
    next_run: string
    success_rate: number
  }>> => {
    const response = await api.get('/system/processes')
    return response.data
  },

  getLogs: async (level: string = 'INFO', limit: number = 100): Promise<{
    logs: Array<{
      timestamp: string
      level: string
      message: string
      module: string
    }>
    total: number
    level_filter: string
  }> => {
    const response = await api.get('/system/logs', {
      params: { level, limit }
    })
    return response.data
  },

  getMetrics: async (hours: number = 24): Promise<{
    metrics: Array<{
      timestamp: string
      cpu_usage: number
      memory_usage: number
      disk_usage: number
      api_requests: number
      response_time: number
    }>
    summary: Record<string, number>
    time_range: {
      start: string
      end: string
      hours: number
    }
  }> => {
    const response = await api.get('/system/metrics', {
      params: { hours }
    })
    return response.data
  },
}

export default api
