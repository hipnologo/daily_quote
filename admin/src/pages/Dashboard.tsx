import { 
  Quote, 
  FileText, 
  TrendingUp, 
  Activity,
  Plus,
  BarChart3,
  Settings
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useQuoteStats, useSystemHealth, useFiles, useSentimentStats } from '../hooks/useApi'



export default function Dashboard() {
  const navigate = useNavigate()
  const { data: quoteStats } = useQuoteStats()
  const { data: systemHealth } = useSystemHealth()
  const { data: filesData } = useFiles()
  const { data: sentimentStats } = useSentimentStats()
  
  const stats = {
    totalQuotes: quoteStats?.total_quotes || 0,
    totalFiles: filesData?.files?.length || 4, // Default to 4 known files
    languages: quoteStats?.languages || 0,
    systemHealth: systemHealth?.status || 'unknown'
  }

  // Generate recent activity based on actual data
  const recentActivity = [
    { id: 1, action: `${stats.totalQuotes.toLocaleString()} quotes loaded`, time: 'Just now', type: 'success' },
    { id: 2, action: `System status: ${stats.systemHealth}`, time: 'Just now', type: stats.systemHealth === 'healthy' ? 'success' : 'warning' },
    { id: 3, action: `${sentimentStats?.total_analyzed || 0} quotes analyzed for sentiment`, time: 'Recent', type: 'info' },
    { id: 4, action: `${stats.totalFiles} quote files available`, time: 'Recent', type: 'info' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to your Daily Quote admin dashboard
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Quotes"
          value={stats.totalQuotes.toLocaleString()}
          icon={Quote}
          color="text-blue-600"
          bgColor="bg-blue-100"
        />
        <StatCard
          title="Quote Files"
          value={stats.totalFiles}
          icon={FileText}
          color="text-green-600"
          bgColor="bg-green-100"
        />
        <StatCard
          title="Languages"
          value={stats.languages}
          icon={TrendingUp}
          color="text-purple-600"
          bgColor="bg-purple-100"
        />
        <StatCard
          title="System Health"
          value={stats.systemHealth}
          icon={Activity}
          color="text-emerald-600"
          bgColor="bg-emerald-100"
        />
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-3">
                <div className={`flex-shrink-0 w-2 h-2 rounded-full ${
                  activity.type === 'success' ? 'bg-green-400' : 
                  activity.type === 'warning' ? 'bg-yellow-400' : 'bg-blue-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <QuickActionButton
              icon={Plus}
              title="Add New Quote"
              description="Manually add a new quote to the collection"
              onClick={() => navigate('/quotes')}
            />
            <QuickActionButton
              icon={BarChart3}
              title="Run Analysis"
              description="Start sentiment analysis on quotes"
              onClick={() => navigate('/analytics')}
            />
            <QuickActionButton
              icon={FileText}
              title="View Files"
              description="Browse and manage quote files"
              onClick={() => navigate('/files')}
            />
            <QuickActionButton
              icon={Settings}
              title="System Status"
              description="View system health and logs"
              onClick={() => navigate('/system')}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}

function StatCard({ title, value, icon: Icon, color, bgColor }: StatCardProps) {
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

interface QuickActionButtonProps {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description: string
  onClick?: () => void
}

function QuickActionButton({ icon: Icon, title, description, onClick }: QuickActionButtonProps) {
  return (
    <button 
      className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-blue-300 transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center space-x-3">
        <Icon className="h-5 w-5 text-blue-500" />
        <div>
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
    </button>
  )
}
