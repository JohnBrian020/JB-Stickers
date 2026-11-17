
import {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react'

import {
  loginAdmin,
  getCurrentAdmin,
  logoutAdmin,
} from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function checkSession() {
      try {
        const currentAdmin = await getCurrentAdmin()
        setAdmin(currentAdmin)
      } catch {
        setAdmin(null)
      } finally {
        setLoading(false)
      }
    }

    checkSession()
  }, [])

  async function login(identifier, password) {
    const adminData = await loginAdmin(identifier, password)
    setAdmin(adminData)
    return adminData
  }

  async function logout() {
    try {
      await logoutAdmin()
    } finally {
      setAdmin(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{ admin, loading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }

  return context
}
