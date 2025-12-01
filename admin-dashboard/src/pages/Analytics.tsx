import { useQuery } from '@tanstack/react-query'
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
import { TrendingUp, Heart } from 'lucide-react'

// Mock data for charts
const sentimentData = [
  { name: 'Positive', value: 65, count: 812 },
  { name: 'Neutral', value: 25, count: 312 },
  { name: 'Negative', value: 10, count: 123 },
]

const languageData = [
  { language: 'English', quotes: 650, sentiment: 0.7 },
  { language: 'Spanish', quotes: 280, sentiment: 0.6 },
  { language: 'Portuguese', quotes: 200, sentiment: 0.65 },
  { language: 'Italian', quotes: 117, sentiment: 0.68 },
]

const trendsData = [
  { month: 'Jan', positive: 45, negative: 8, neutral: 20 },
  { month: 'Feb', positive: 52, negative: 12, neutral: 18 },
  { month: 'Mar', positive: 48, negative: 10, neutral: 22 },
  { month: 'Apr', positive: 61, negative: 7, neutral: 15 },
  { month: 'May', positive: 55, negative: 9, neutral: 19 },
  { month: 'Jun', positive: 67, negative: 6, neutral: 14 },
]

const COLORS = ['#10B981', '#F59E0B', '#EF4444']

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      // Replace with actual API call
      return {
        totalAnalyzed: 1247,
        averageSentiment: 0.68,
        topAuthor: 'Steve Jobs',
        mostPositiveCategory: 'Motivation'
      }
    }
  })

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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Sentiment analysis and quote statistics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Total Analyzed"
          value={analytics?.totalAnalyzed.toLocaleString() || '0'}
          icon={TrendingUp}
          color="text-blue-600"
          bgColor="bg-blue-100"
        />
        <MetricCard
          title="Avg Sentiment"
          value={((analytics?.averageSentiment || 0) * 100).toFixed(1) + '%'}
          icon={Heart}
          color="text-green-600"
          bgColor="bg-green-100"
        />
        <MetricCard
          title="Top Author"
          value={analytics?.topAuthor || 'N/A'}
          icon={TrendingUp}
          color="text-purple-600"
          bgColor="bg-purple-100"
        />
        <MetricCard
          title="Best Category"
          value={analytics?.mostPositiveCategory || 'N/A'}
          icon={Heart}
          color="text-pink-600"
          bgColor="bg-pink-100"
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
                  <div className="text-xs text-gray-500">{item.value}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Authors */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Authors</h3>
          <div className="space-y-3">
            {[
              { name: 'Steve Jobs', quotes: 45, sentiment: 0.8 },
              { name: 'Albert Einstein', quotes: 32, sentiment: 0.7 },
              { name: 'Maya Angelou', quotes: 28, sentiment: 0.9 },
              { name: 'Winston Churchill', quotes: 24, sentiment: 0.6 },
            ].map((author) => (
              <div key={author.name} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{author.name}</div>
                  <div className="text-xs text-gray-500">{author.quotes} quotes</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {(author.sentiment * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">positive</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Categories */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Categories</h3>
          <div className="space-y-3">
            {[
              { name: 'Motivation', quotes: 156, sentiment: 0.85 },
              { name: 'Success', quotes: 134, sentiment: 0.78 },
              { name: 'Life', quotes: 98, sentiment: 0.65 },
              { name: 'Innovation', quotes: 87, sentiment: 0.72 },
            ].map((category) => (
              <div key={category.name} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{category.name}</div>
                  <div className="text-xs text-gray-500">{category.quotes} quotes</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {(category.sentiment * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">positive</div>
                </div>
              </div>
            ))}
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
