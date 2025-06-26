import React, { createContext, useContext, useEffect, useState } from 'react'
import { 
  signInWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  User
} from 'firebase/auth'
import { auth } from '../config/firebase'

const DEV_MODE = (import.meta as any).env?.VITE_DEV_MODE === 'true' || true // Default to true for development

interface AuthContextType {
  currentUser: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  function login(email: string, password: string) {
    if (DEV_MODE) {
      console.log('🔧 Development mode: mock login successful')
      // In dev mode, we don't actually need to authenticate with Firebase
      return Promise.resolve()
    }
    return signInWithEmailAndPassword(auth, email, password).then(() => {})
  }

  function logout() {
    if (DEV_MODE) {
      console.log('🔧 Development mode: mock logout')
      setCurrentUser(null)
      return Promise.resolve()
    }
    return signOut(auth)
  }

  useEffect(() => {
    if (DEV_MODE) {
      console.log('🔧 Development mode: setting mock user')
      // Create a mock user object for development
      const mockUser = {
        uid: 'dev-user-123',
        email: 'dev@example.com',
        displayName: 'Development User',
        // Add other required User properties as needed
      } as User
      
      setCurrentUser(mockUser)
      setLoading(false)
      return
    }

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      console.log('🔄 Auth state changed:', user ? `User logged in: ${user.email}` : 'No user')
      setCurrentUser(user)
      setLoading(false)
    })

    return unsubscribe
  }, [])

  const value = {
    currentUser,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
} 