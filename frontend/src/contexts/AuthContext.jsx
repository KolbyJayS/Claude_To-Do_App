import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { setLoading(false); return }
    api.get('/auth/me')
      .then((r) => setUser(r.data.user))
      .catch(() => localStorage.removeItem('access_token'))
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('access_token', data.access_token)
    setUser(data.user)
    return data.user
  }

  const register = async (email, password) => {
    const { data } = await api.post('/auth/register', { email, password })
    localStorage.setItem('access_token', data.access_token)
    setUser(data.user)
    return data.user
  }

  const logout = async () => {
    await api.post('/auth/logout').catch(() => {})
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
