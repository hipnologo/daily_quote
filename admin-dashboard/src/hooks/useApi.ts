import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  quotesApi, 
  filesApi, 
  sentimentApi, 
  systemApi, 
  authApi,
  Quote
} from '../services/api'

// Auth hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['current-user'],
    queryFn: authApi.getCurrentUser,
    retry: false,
  })
}

export const useLogin = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      authApi.login(username, password),
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.access_token)
      queryClient.setQueryData(['current-user'], data.user)
      queryClient.invalidateQueries({ queryKey: ['current-user'] })
    },
  })
}

// Quotes hooks
export const useQuotes = (params?: {
  skip?: number
  limit?: number
  search?: string
  language?: string
  category?: string
}) => {
  return useQuery({
    queryKey: ['quotes', params],
    queryFn: () => quotesApi.getQuotes(params),
    placeholderData: (previousData) => previousData,
  })
}

export const useQuote = (id: number) => {
  return useQuery({
    queryKey: ['quote', id],
    queryFn: () => quotesApi.getQuote(id),
    enabled: !!id,
  })
}

export const useQuoteStats = () => {
  return useQuery({
    queryKey: ['quote-stats'],
    queryFn: quotesApi.getStats,
  })
}

export const useCreateQuote = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: quotesApi.createQuote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
      queryClient.invalidateQueries({ queryKey: ['quote-stats'] })
    },
  })
}

export const useUpdateQuote = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, quote }: { id: number; quote: Partial<Quote> }) =>
      quotesApi.updateQuote(id, quote),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
      queryClient.setQueryData(['quote', data.id], data)
    },
  })
}

export const useDeleteQuote = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: quotesApi.deleteQuote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
      queryClient.invalidateQueries({ queryKey: ['quote-stats'] })
    },
  })
}

export const useImportQuotes = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ file, language }: { file: File; language: string }) =>
      quotesApi.importQuotes(file, language),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotes'] })
      queryClient.invalidateQueries({ queryKey: ['quote-stats'] })
    },
  })
}

// Files hooks
export const useFiles = () => {
  return useQuery({
    queryKey: ['quote-files'],
    queryFn: filesApi.getFiles,
  })
}

export const useFileContent = (filename: string) => {
  return useQuery({
    queryKey: ['file-content', filename],
    queryFn: () => filesApi.getFileContent(filename),
    enabled: !!filename,
  })
}

export const useBackupFile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: filesApi.backupFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quote-files'] })
    },
  })
}

// Sentiment hooks
export const useSentimentStats = () => {
  return useQuery({
    queryKey: ['sentiment-stats'],
    queryFn: sentimentApi.getStats,
  })
}

export const useSentimentDistribution = (language?: string, author?: string) => {
  return useQuery({
    queryKey: ['sentiment-distribution', language, author],
    queryFn: () => sentimentApi.getDistribution(language, author),
  })
}

export const useStartSentimentAnalysis = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ language, forceReanalyze }: { language: string; forceReanalyze: boolean }) =>
      sentimentApi.startAnalysis(language, forceReanalyze),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sentiment-stats'] })
    },
  })
}

export const useSentimentJobStatus = (jobId: string) => {
  return useQuery({
    queryKey: ['sentiment-job', jobId],
    queryFn: () => sentimentApi.getJobStatus(jobId),
    enabled: !!jobId,
    refetchInterval: 2000, // Poll every 2 seconds
  })
}

// System hooks
export const useSystemHealth = () => {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: systemApi.getHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export const useSystemProcesses = () => {
  return useQuery({
    queryKey: ['system-processes'],
    queryFn: systemApi.getProcesses,
    refetchInterval: 60000, // Refresh every minute
  })
}

export const useSystemLogs = (level: string = 'INFO', limit: number = 100) => {
  return useQuery({
    queryKey: ['system-logs', level, limit],
    queryFn: () => systemApi.getLogs(level, limit),
  })
}

export const useSystemMetrics = (hours: number = 24) => {
  return useQuery({
    queryKey: ['system-metrics', hours],
    queryFn: () => systemApi.getMetrics(hours),
  })
}

// Dashboard hooks (combining multiple data sources)
export const useDashboardStats = () => {
  const { data: quoteStats } = useQuoteStats()
  const { data: sentimentStats } = useSentimentStats()
  const { data: systemHealth } = useSystemHealth()
  const { data: files } = useFiles()

  return {
    totalQuotes: quoteStats?.total_quotes || 0,
    totalFiles: files?.files?.length || 0,
    languages: quoteStats?.languages || 0,
    authors: quoteStats?.authors || 0,
    categories: quoteStats?.categories || 0,
    sentimentAnalyzed: sentimentStats?.total_analyzed || 0,
    systemStatus: systemHealth?.status || 'unknown',
    cpuUsage: systemHealth?.cpu_usage || 0,
    memoryUsage: systemHealth?.memory_usage || 0,
    diskUsage: systemHealth?.disk_usage || 0,
  }
}
