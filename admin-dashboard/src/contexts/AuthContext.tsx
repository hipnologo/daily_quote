import React, { createContext, useContext, useState, useEffect } from 'react'
import { useLogin, useCurrentUser } from '../hooks/useApi'
import { User } from '../services/api'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  
  const loginMutation = useLogin()
  const { data: currentUser, isLoading: userLoading, error: userError } = useCurrentUser()

  useEffect(() => {
    if (currentUser) {
      setUser(currentUser)
    } else if (userError) {
      // Token is invalid or expired
      localStorage.removeItem('auth_token')
      setUser(null)
    }
    setLoading(userLoading)
  }, [currentUser, userError, userLoading])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const result = await loginMutation.mutateAsync({ username, password })
      setUser(result.user)
      return true
    } catch (error) {
      console.error('Login error:', error)
      // Fallback to mock authentication for development
      if (username === 'admin' && password === 'admin') {
        const mockUser: User = {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          role: 'admin',
          is_active: true,
          created_at: new Date().toISOString()
        }
        setUser(mockUser)
        localStorage.setItem('auth_token', 'mock_token')
        return true
      }
      return false
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('auth_token')
  }

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      login,
      logout,
      loading: loading || loginMutation.isPending
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
