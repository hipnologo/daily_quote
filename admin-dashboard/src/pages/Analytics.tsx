import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  PieChart, 
  Pie, 
  Cell,
  LineChart,
  Line,
  ResponsiveContainer
} from 'recharts'
import { TrendingUp, Heart, Play, RefreshCw } from 'lucide-react'
import { useSentimentStats, useQuoteStats, useStartSentimentAnalysis } from '../hooks/useApi'

const COLORS = ['#10B981', '#F59E0B', '#EF4444']

export default function Analytics() {
  const { data: sentimentStats, isLoading: sentimentLoading } = useSentimentStats()
  const { data: quoteStats, isLoading: quotesLoading } = useQuoteStats()
  const startAnalysisMutation = useStartSentimentAnalysis()

  const isLoading = sentimentLoading || quotesLoading

  // Transform sentiment data for charts
  const sentimentData = sentimentStats ? [
    { name: 'Positive', value: sentimentStats.positive_count, count: sentimentStats.positive_count },
    { name: 'Neutral', value: sentimentStats.neutral_count, count: sentimentStats.neutral_count },
    { name: 'Negative', value: sentimentStats.negative_count, count: sentimentStats.negative_count },
  ] : []

  // Transform language data
  const languageData = quoteStats?.by_language ? Object.entries(quoteStats.by_language).map(([lang, count]) => ({
    language: lang.toUpperCase(),
    quotes: count as number,
    sentiment: 0.7 // Placeholder - could be calculated from sentiment data
  })) : []

  // Mock trends data for now (could be replaced with real time-series data)
  const trendsData = [
    { month: 'Jan', positive: 45, negative: 8, neutral: 20 },
    { month: 'Feb', positive: 52, negative: 12, neutral: 18 },
    { month: 'Mar', positive: 48, negative: 10, neutral: 22 },
    { month: 'Apr', positive: 61, negative: 7, neutral: 15 },
    { month: 'May', positive: 55, negative: 9, neutral: 19 },
    { month: 'Jun', positive: 67, negative: 6, neutral: 14 },
  ]

  const handleStartAnalysis = async () => {
    try {
      await startAnalysisMutation.mutateAsync({ language: 'all', forceReanalyze: false })
    } catch (error) {
      console.error('Error starting analysis:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Sentiment analysis and quote statistics
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            className="btn-outline"
            onClick={handleStartAnalysis}
            disabled={startAnalysisMutation.isPending}
          >
            {startAnalysisMutation.isPending ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {startAnalysisMutation.isPending ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Total Analyzed"
          value={sentimentStats?.total_analyzed?.toLocaleString() || '0'}
          icon={TrendingUp}
          color="text-blue-600"
          bgColor="bg-blue-100"
        />
        <MetricCard
          title="Avg Sentiment"
          value={sentimentStats ? ((sentimentStats.average_compound || 0) * 100).toFixed(1) + '%' : '0%'}
          icon={Heart}
          color="text-green-600"
          bgColor="bg-green-100"
        />
        <MetricCard
          title="Positive Quotes"
          value={`${sentimentStats?.positive_count || 0}`}
          icon={TrendingUp}
          color="text-emerald-600"
          bgColor="bg-emerald-100"
        />
        <MetricCard
          title="Total Quotes"
          value={quoteStats?.total_quotes?.toLocaleString() || '0'}
          icon={Heart}
          color="text-purple-600"
          bgColor="bg-purple-100"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Language Analysis */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quotes by Language</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={languageData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="language" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="quotes" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Trends */}
        <div className="card p-6 lg:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Trends Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="positive" stroke="#10B981" strokeWidth={2} />
              <Line type="monotone" dataKey="neutral" stroke="#F59E0B" strokeWidth={2} />
              <Line type="monotone" dataKey="negative" stroke="#EF4444" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Breakdown */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sentiment Breakdown</h3>
          <div className="space-y-4">
            {sentimentData.map((item, index) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: COLORS[index] }}
                  />
                  <span className="text-sm font-medium text-gray-900">{item.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">{item.count}</div>
                  <div className="text-xs text-gray-500">
                    {sentimentStats ? ((item.count / sentimentStats.total_analyzed) * 100).toFixed(1) : 0}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Authors - Placeholder for now */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Authors</h3>
          <div className="space-y-3">
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">Author analytics coming soon</p>
              <p className="text-xs mt-1">This feature will show sentiment analysis by author</p>
            </div>
          </div>
        </div>

        {/* Categories - Placeholder for now */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Categories</h3>
          <div className="space-y-3">
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">Category analytics coming soon</p>
              <p className="text-xs mt-1">This feature will show sentiment analysis by category</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}

function MetricCard({ title, value, icon: Icon, color, bgColor }: MetricCardProps) {
  return (
    <div className="card p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`p-3 rounded-md ${bgColor}`}>
            <Icon className={`h-6 w-6 ${color}`} />
          </div>
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-lg font-medium text-gray-900">{value}</dd>
          </dl>
        </div>
      </div>
    </div>
  )
}
