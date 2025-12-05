import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Quotes from './pages/Quotes'
import Analytics from './pages/Analytics'
import Files from './pages/Files'
import System from './pages/System'
import Login from './pages/Login'
import Logout from './pages/Logout'
import { AuthProvider, useAuth } from './contexts/AuthContext'

function AppRoutes() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/logout" element={<Logout />} />
      
      {/* Protected routes */}
      {isAuthenticated ? (
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/quotes" element={<Quotes />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/files" element={<Files />} />
          <Route path="/system" element={<System />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      ) : (
        <Route path="*" element={<Navigate to="/login" replace />} />
      )}
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App
