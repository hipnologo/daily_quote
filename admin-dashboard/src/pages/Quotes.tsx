import { useState } from 'react'
import { Search, Filter, Plus, Edit, Trash2, Eye, Download, Upload, ChevronLeft, ChevronRight, X, Save } from 'lucide-react'
import { useQuotes, useQuoteStats, useCreateQuote, useUpdateQuote, useDeleteQuote } from '../hooks/useApi'
import { Quote } from '../services/api'

export default function Quotes() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState('all')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(100) // Show more than 50

  // CRUD state
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null)
  const [quoteForm, setQuoteForm] = useState({
    text: '',
    author: '',
    language: 'en' as 'en' | 'es' | 'pt' | 'it',
    category: ''
  })

  const { data: stats } = useQuoteStats()
  
  const { data: quotesResponse, isLoading } = useQuotes({
    search: searchTerm || undefined,
    language: selectedLanguage === 'all' ? undefined : selectedLanguage,
    skip: (currentPage - 1) * pageSize,
    limit: pageSize
  })
  
  const quotes = quotesResponse?.quotes || []
  const totalQuotes = stats?.total_quotes || 0
  const totalPages = Math.ceil(totalQuotes / pageSize)

  // CRUD hooks
  const createQuoteMutation = useCreateQuote()
  const updateQuoteMutation = useUpdateQuote()
  const deleteQuoteMutation = useDeleteQuote()

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handlePageSizeChange = (size: number) => {
    setPageSize(size)
    setCurrentPage(1) // Reset to first page
  }

  const handleCreateQuote = () => {
    setQuoteForm({ text: '', author: '', language: 'en', category: '' })
    setShowCreateModal(true)
  }

  const handleEditQuote = (quote: Quote) => {
    setSelectedQuote(quote)
    setQuoteForm({
      text: quote.text,
      author: quote.author,
      language: quote.language,
      category: quote.category || ''
    })
    setShowEditModal(true)
  }

  const handleDeleteQuote = (quote: Quote) => {
    setSelectedQuote(quote)
    setShowDeleteModal(true)
  }

  const handleSaveQuote = async () => {
    try {
      if (showCreateModal) {
        await createQuoteMutation.mutateAsync({
          text: quoteForm.text,
          author: quoteForm.author,
          language: quoteForm.language,
          category: quoteForm.category || undefined
        })
        setShowCreateModal(false)
      } else if (showEditModal && selectedQuote) {
        await updateQuoteMutation.mutateAsync({
          id: selectedQuote.id,
          quote: {
            text: quoteForm.text,
            author: quoteForm.author,
            language: quoteForm.language,
            category: quoteForm.category || undefined
          }
        })
        setShowEditModal(false)
      }
    } catch (error) {
      console.error('Error saving quote:', error)
    }
  }

  const handleConfirmDelete = async () => {
    if (selectedQuote) {
      try {
        await deleteQuoteMutation.mutateAsync(selectedQuote.id)
        setShowDeleteModal(false)
        setSelectedQuote(null)
      } catch (error) {
        console.error('Error deleting quote:', error)
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quotes Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your quote collection
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="btn-outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
          <button className="btn-outline">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </button>
          <button className="btn-primary" onClick={handleCreateQuote}>
            <Plus className="h-4 w-4 mr-2" />
            Add Quote
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search quotes or authors..."
              className="input pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <select
            className="input"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            title="Filter by language"
          >
            <option value="all">All Languages</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="pt">Portuguese</option>
            <option value="it">Italian</option>
          </select>
          
          <select
            className="input"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            title="Filter by category"
            disabled // Disabled since backend doesn't support category filtering yet
          >
            <option value="all">All Categories</option>
            <option value="motivation">Motivation</option>
            <option value="innovation">Innovation</option>
            <option value="life">Life</option>
            <option value="success">Success</option>
          </select>
          
          <button className="btn-outline">
            <Filter className="h-4 w-4 mr-2" />
            Advanced Filters
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-2xl font-bold text-gray-900">{totalQuotes.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Total Quotes</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-gray-900">{stats?.languages || 0}</div>
          <div className="text-sm text-gray-500">Languages</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-gray-900">{stats?.verified_count || 0}</div>
          <div className="text-sm text-gray-500">Verified</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-gray-900">{Object.keys(stats?.by_sentiment || {}).length}</div>
          <div className="text-sm text-gray-500">Sentiment Types</div>
        </div>
      </div>

      {/* Quotes Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quote
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Author
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Language
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    Loading quotes...
                  </td>
                </tr>
              ) : quotes.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    No quotes found
                  </td>
                </tr>
              ) : (
                quotes.map((quote) => (
                  <tr key={quote.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-md truncate">
                        {quote.text}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {quote.author}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {quote.language.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 capitalize">
                        {quote.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium space-x-2">
                      <button 
                        className="text-blue-600 hover:text-blue-900" 
                        title="View quote"
                        onClick={() => handleEditQuote(quote)}
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button 
                        className="text-gray-600 hover:text-gray-900" 
                        title="Edit quote"
                        onClick={() => handleEditQuote(quote)}
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button 
                        className="text-red-600 hover:text-red-900" 
                        title="Delete quote"
                        onClick={() => handleDeleteQuote(quote)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-700">Show:</span>
          <select 
            className="input w-20"
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            title="Select number of items per page"
          >
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
            <option value={500}>500</option>
          </select>
          <span className="text-sm text-gray-700">per page</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-700">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalQuotes)} of {totalQuotes.toLocaleString()} results
          </div>
          <div className="flex space-x-2">
            <button 
              className="btn-outline" 
              disabled={currentPage === 1}
              onClick={() => handlePageChange(currentPage - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>
            <button 
              className="btn-outline" 
              disabled={currentPage === totalPages}
              onClick={() => handlePageChange(currentPage + 1)}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      <QuoteModal
        isOpen={showCreateModal || showEditModal}
        isEdit={showEditModal}
        quote={quoteForm}
        onChange={setQuoteForm}
        onSave={handleSaveQuote}
        onClose={() => {
          setShowCreateModal(false)
          setShowEditModal(false)
        }}
        isLoading={createQuoteMutation.isPending || updateQuoteMutation.isPending}
      />

      <DeleteModal
        quote={selectedQuote!}
        onConfirm={handleConfirmDelete}
        onClose={() => {
          setShowDeleteModal(false)
          setSelectedQuote(null)
        }}
        isLoading={deleteQuoteMutation.isPending}
      />
    </div>
  )
}

// Quote Modal Component
interface QuoteModalProps {
  isOpen: boolean
  isEdit: boolean
  quote: {
    text: string
    author: string
    language: string
    category: string
  }
  onChange: (quote: any) => void
  onSave: () => void
  onClose: () => void
  isLoading: boolean
}

function QuoteModal({ isOpen, isEdit, quote, onChange, onSave, onClose, isLoading }: QuoteModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {isEdit ? 'Edit Quote' : 'Add New Quote'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" title="Close">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quote Text *
            </label>
            <textarea
              className="input w-full h-32 resize-none"
              value={quote.text}
              onChange={(e) => onChange({ ...quote, text: e.target.value })}
              placeholder="Enter the quote text..."
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Author *
              </label>
              <input
                type="text"
                className="input w-full"
                value={quote.author}
                onChange={(e) => onChange({ ...quote, author: e.target.value })}
                placeholder="Enter the author name..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Language *
              </label>
              <select
                className="input w-full"
                value={quote.language}
                onChange={(e) => onChange({ ...quote, language: e.target.value })}
                required
                title="Select language"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="pt">Portuguese</option>
                <option value="it">Italian</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <input
              type="text"
              className="input w-full"
              value={quote.category}
              onChange={(e) => onChange({ ...quote, category: e.target.value })}
              placeholder="Enter category (optional)..."
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            className="btn-outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={onSave}
            disabled={isLoading || !quote.text.trim() || !quote.author.trim()}
          >
            {isLoading ? (
              'Saving...'
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {isEdit ? 'Update' : 'Create'}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

// Delete Confirmation Modal Component
interface DeleteModalProps {
  quote: Quote
  onConfirm: () => void
  onClose: () => void
  isLoading: boolean
}

function DeleteModal({ quote, onConfirm, onClose, isLoading }: DeleteModalProps) {
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-md shadow-lg rounded-md bg-white">
        <div className="mt-3 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Delete Quote</h3>
          <div className="mt-2 px-7 py-3">
            <p className="text-sm text-gray-500">
              Are you sure you want to delete this quote? This action cannot be undone.
            </p>
            <div className="mt-4 p-3 bg-gray-50 rounded-md">
              <p className="text-sm text-gray-900 font-medium">"{quote.text}"</p>
              <p className="text-xs text-gray-500 mt-1">— {quote.author}</p>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            className="btn-outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            className="btn-danger"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Deleting...' : 'Delete Quote'}
          </button>
        </div>
      </div>
    </div>
  )
}
