import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  FileText, 
  Download, 
  Upload, 
  Eye, 
  Edit, 
  Trash2,
  Copy,
  RefreshCw,
  X
} from 'lucide-react'

// Mock data
const mockFiles = [
  { name: 'quotes.txt', size: 45678, modified: '2024-01-15T10:30:00Z', lines: 1247 },
  { name: 'quotes_es.txt', size: 32145, modified: '2024-01-14T15:20:00Z', lines: 892 },
  { name: 'quotes_pt.txt', size: 28934, modified: '2024-01-13T09:15:00Z', lines: 756 },
  { name: 'quotes_it.txt', size: 21567, modified: '2024-01-12T14:45:00Z', lines: 634 },
]

export default function Files() {
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const { data: files = mockFiles, isLoading, refetch } = useQuery({
    queryKey: ['quote-files'],
    queryFn: async () => {
      // Replace with actual API call
      return mockFiles
    }
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">File Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage quote files and backups
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            className="btn-outline"
            onClick={() => refetch()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
          <button className="btn-outline">
            <Upload className="h-4 w-4 mr-2" />
            Upload File
          </button>
        </div>
      </div>

      {/* Files Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full text-center text-gray-500">
            Loading files...
          </div>
        ) : (
          files.map((file) => (
            <div key={file.name} className="card p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-500" />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{file.name}</h3>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Lines:</span>
                  <span className="text-gray-900">{file.lines.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Modified:</span>
                  <span className="text-gray-900">{formatDate(file.modified)}</span>
                </div>
              </div>
              
              <div className="mt-4 flex space-x-2">
                <button 
                  className="flex-1 btn-outline text-xs"
                  onClick={() => setSelectedFile(file.name)}
                >
                  <Eye className="h-3 w-3 mr-1" />
                  View
                </button>
                <button className="flex-1 btn-outline text-xs">
                  <Download className="h-3 w-3 mr-1" />
                  Download
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* File Preview Modal */}
      {selectedFile && (
        <FilePreviewModal 
          filename={selectedFile} 
          onClose={() => setSelectedFile(null)} 
        />
      )}
    </div>
  )
}

interface FilePreviewModalProps {
  filename: string
  onClose: () => void
}

function FilePreviewModal({ filename, onClose }: FilePreviewModalProps) {
  const { data: fileContent, isLoading } = useQuery({
    queryKey: ['file-content', filename],
    queryFn: async () => {
      // Replace with actual API call
      return {
        filename,
        quote_count: 150,
        quotes: [
          "The only way to do great work is to love what you do. - Steve Jobs",
          "Innovation distinguishes between a leader and a follower. - Steve Jobs",
          "Stay hungry, stay foolish. - Steve Jobs"
        ]
      }
    }
  })

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">{filename}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-6 w-6" />
          </button>
        </div>
        
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">Loading file content...</div>
        ) : (
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              Total quotes: {fileContent?.quote_count}
            </div>
            <div className="max-h-96 overflow-y-auto border rounded-md p-4 bg-gray-50">
              {fileContent?.quotes.map((quote, index) => (
                <div key={index} className="py-2 border-b border-gray-200 last:border-b-0">
                  <p className="text-sm text-gray-900">{quote}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
