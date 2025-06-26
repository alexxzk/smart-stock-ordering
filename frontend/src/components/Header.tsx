import { useAuth } from '../contexts/AuthContext'
import { LogOut, User, Bell } from 'lucide-react'

export default function Header() {
  const { currentUser, logout } = useAuth()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex justify-between items-center px-6 py-4">
        <div className="flex items-center">
          <div className="flex flex-col items-start">
            <span className="text-xs font-bold text-blue-600 tracking-wide uppercase mb-1">ordix.ai</span>
            <h1 className="text-2xl font-semibold text-gray-900">
              Smart Stock Ordering
            </h1>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="p-2 text-gray-400 hover:text-gray-500">
            <Bell className="h-5 w-5" />
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-700">
                {currentUser?.email}
              </span>
            </div>
            
            <button
              onClick={logout}
              className="flex items-center space-x-1 text-sm text-gray-500 hover:text-gray-700"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
} 