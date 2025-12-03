import { useState } from 'react'
import { 
  FileText, 
  Download, 
  Upload, 
  Eye, 
  RefreshCw,
  X,
  BarChart3
} from 'lucide-react'
import { useFiles, useFileContent } from '../hooks/useApi'

export default function Files() {
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [previewLimit, setPreviewLimit] = useState(50)

  const { data: filesData, isLoading, refetch } = useFiles()
  const files = filesData?.files || []

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

  const getLanguageInfo = (filename: string) => {
    const langMap: Record<string, { name: string; flag: string; color: string }> = {
      'quotes.txt': { name: 'English', flag: '🇺🇸', color: 'bg-blue-100 text-blue-800' },
      'quotes_es.txt': { name: 'Spanish', flag: '🇪🇸', color: 'bg-red-100 text-red-800' },
      'quotes_pt.txt': { name: 'Portuguese', flag: '🇵🇹', color: 'bg-green-100 text-green-800' },
      'quotes_it.txt': { name: 'Italian', flag: '🇮🇹', color: 'bg-yellow-100 text-yellow-800' }
    }
    return langMap[filename] || { name: 'Unknown', flag: '❓', color: 'bg-gray-100 text-gray-800' }
  }

  const handleDownload = (filename: string) => {
    // Create download link
    const link = document.createElement('a')
    link.href = `/api/files/${filename}/download`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quote Files</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and preview your quote collection files
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            </div>
          ))
        ) : (
          files.map((file) => {
            const langInfo = getLanguageInfo(file.filename)
            return (
              <div key={file.filename} className="card p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">{file.filename}</h3>
                      <div className="flex items-center space-x-1 mt-1">
                        <span className="text-lg">{langInfo.flag}</span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${langInfo.color}`}>
                          {langInfo.name}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Size:</span>
                    <span className="text-gray-900 font-medium">{formatFileSize(file.size)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Quotes:</span>
                    <span className="text-gray-900 font-medium">{file.lines.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Modified:</span>
                    <span className="text-gray-900 font-medium">{formatDate(file.modified)}</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <button 
                    className="w-full btn-primary text-xs py-2"
                    onClick={() => setSelectedFile(file.filename)}
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View First {previewLimit} Quotes
                  </button>
                  <button 
                    className="w-full btn-outline text-xs py-2"
                    onClick={() => handleDownload(file.filename)}
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </button>
                  <button className="w-full btn-outline text-xs py-2">
                    <BarChart3 className="h-3 w-3 mr-1" />
                    Analyze
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Preview Limit Selector */}
      <div className="flex items-center justify-center space-x-4">
        <span className="text-sm text-gray-600">Preview limit:</span>
        <select
          className="input w-24"
          value={previewLimit}
          onChange={(e) => setPreviewLimit(Number(e.target.value))}
          title="Select preview limit"
        >
          <option value={10}>10</option>
          <option value={25}>25</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
        <span className="text-sm text-gray-600">quotes</span>
      </div>

      {/* File Preview Modal */}
      {selectedFile && (
        <FilePreviewModal 
          filename={selectedFile} 
          limit={previewLimit}
          onClose={() => setSelectedFile(null)} 
        />
      )}
    </div>
  )
}

interface FilePreviewModalProps {
  filename: string
  limit: number
  onClose: () => void
}

function FilePreviewModal({ filename, limit, onClose }: FilePreviewModalProps) {
  const { data: fileContent, isLoading } = useFileContent(filename)

  const displayedQuotes = fileContent?.quotes?.slice(0, limit) || []

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">{filename}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" title="Close preview">
            <X className="h-6 w-6" />
          </button>
        </div>
        
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">Loading file content...</div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center text-sm text-gray-600">
              <span>
                Showing first {Math.min(limit, fileContent?.quotes?.length || 0)} of {fileContent?.quote_count || 0} quotes
              </span>
              {fileContent && fileContent.quotes && fileContent.quotes.length > limit && (
                <span className="text-xs text-gray-500">
                  ({fileContent.quotes.length - limit} more quotes not shown)
                </span>
              )}
            </div>
            <div className="max-h-96 overflow-y-auto border rounded-md p-4 bg-gray-50">
              {displayedQuotes.length > 0 ? (
                displayedQuotes.map((quote: string, index: number) => (
                  <div key={index} className="py-2 border-b border-gray-200 last:border-b-0">
                    <p className="text-sm text-gray-900">{quote}</p>
                  </div>
                ))
              ) : (
                <div className="text-gray-500">No quotes found</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
