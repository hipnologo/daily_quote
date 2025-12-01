import { useQuery } from '@tanstack/react-query'
import { 
  Server, 
  AlertCircle,
  CheckCircle,
  Clock,
  Cpu,
  HardDrive,
  MemoryStick
} from 'lucide-react'

// Mock data
const mockSystemHealth = {
  status: 'healthy',
  uptime: '2 days, 14 hours',
  cpu_usage: 23.5,
  memory_usage: 67.2,
  disk_usage: 45.8,
  database_status: 'healthy'
}

const mockProcesses = [
  { name: 'Daily Quote Fetcher', status: 'active', last_run: '2024-01-15T08:00:00Z', success_rate: 98.5 },
  { name: 'Sentiment Analysis', status: 'idle', last_run: '2024-01-15T09:30:00Z', success_rate: 95.2 },
  { name: 'Vector Generation', status: 'idle', last_run: '2024-01-14T14:20:00Z', success_rate: 92.8 },
]

export default function System() {
  const { data: health = mockSystemHealth } = useQuery({
    queryKey: ['system-health'],
    queryFn: async () => mockSystemHealth
  })

  const { data: processes = mockProcesses } = useQuery({
    queryKey: ['system-processes'],
    queryFn: async () => mockProcesses
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return 'text-green-600 bg-green-100'
      case 'warning':
        return 'text-yellow-600 bg-yellow-100'
      case 'error':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return <CheckCircle className="h-4 w-4" />
      case 'warning':
        return <AlertCircle className="h-4 w-4" />
      case 'error':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">System Monitoring</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor system health and performance
        </p>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className={`p-3 rounded-md ${getStatusColor(health.status).split(' ')[1]}`}>
                <Server className={`h-6 w-6 ${getStatusColor(health.status).split(' ')[0]}`} />
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">System Status</dt>
                <dd className="flex items-center">
                  <span className="text-lg font-medium text-gray-900 capitalize">{health.status}</span>
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 rounded-md bg-blue-100">
                <Cpu className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">CPU Usage</dt>
                <dd className="text-lg font-medium text-gray-900">{health.cpu_usage}%</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 rounded-md bg-purple-100">
                <MemoryStick className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Memory Usage</dt>
                <dd className="text-lg font-medium text-gray-900">{health.memory_usage}%</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="p-3 rounded-md bg-orange-100">
                <HardDrive className="h-6 w-6 text-orange-600" />
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Disk Usage</dt>
                <dd className="text-lg font-medium text-gray-900">{health.disk_usage}%</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Uptime</dt>
              <dd className="text-sm text-gray-900">{health.uptime}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Database Status</dt>
              <dd className="flex items-center">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(health.database_status)}`}>
                  {getStatusIcon(health.database_status)}
                  <span className="ml-1 capitalize">{health.database_status}</span>
                </span>
              </dd>
            </div>
          </dl>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Background Processes</h3>
          <div className="space-y-3">
            {processes.map((process) => (
              <div key={process.name} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{process.name}</div>
                  <div className="text-xs text-gray-500">
                    Success rate: {process.success_rate}%
                  </div>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(process.status)}`}>
                  {getStatusIcon(process.status)}
                  <span className="ml-1 capitalize">{process.status}</span>
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
