import { 
  Quote, 
  FileText, 
  TrendingUp, 
  Activity,
  Database
} from 'lucide-react'
import { useQuoteStats, useSystemHealth, useFiles } from '../hooks/useApi'

// Recent activity will be fetched from API in future version
const recentActivity = [
  { id: 1, action: 'Dashboard loaded', time: 'Just now', type: 'info' },
  { id: 2, action: 'API connection established', time: '1 minute ago', type: 'success' },
]

export default function Dashboard() {
  const { data: quoteStats } = useQuoteStats()
  const { data: systemHealth } = useSystemHealth()
  const { data: filesData } = useFiles()
  
  const stats = {
    totalQuotes: quoteStats?.total_quotes || 0,
    totalFiles: filesData?.files?.length || 0,
    languages: quoteStats?.languages || 0,
    systemHealth: systemHealth?.status || 'unknown'
  }

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
                  activity.type === 'success' ? 'bg-green-400' : 'bg-blue-400'
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
              icon={Quote}
              title="Add New Quote"
              description="Manually add a new quote to the collection"
            />
            <QuickActionButton
              icon={Database}
              title="Run Analysis"
              description="Start sentiment analysis on quotes"
            />
            <QuickActionButton
              icon={FileText}
              title="Backup Files"
              description="Create backup of all quote files"
            />
            <QuickActionButton
              icon={Activity}
              title="System Check"
              description="Run system health diagnostics"
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
}

function QuickActionButton({ icon: Icon, title, description }: QuickActionButtonProps) {
  return (
    <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
      <div className="flex items-center space-x-3">
        <Icon className="h-5 w-5 text-gray-400" />
        <div>
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
    </button>
  )
}
