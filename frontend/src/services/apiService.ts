import { getAuth } from 'firebase/auth'

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
const DEV_MODE = (import.meta as any).env?.VITE_DEV_MODE === 'true' || true // Default to true for development

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export class ApiService {
  private static async getAuthToken(): Promise<string | null> {
    if (DEV_MODE) {
      console.log('🔧 Development mode: bypassing authentication')
      return null // No token needed in dev mode
    }
    
    const auth = getAuth()
    const user = auth.currentUser
    if (!user) {
      throw new Error('User not authenticated')
    }
    return await user.getIdToken()
  }

  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const token = await this.getAuthToken()
      
      const headers: Record<string, string> = {}
      
      // Copy existing headers
      if (options.headers) {
        if (typeof options.headers === 'object' && !Array.isArray(options.headers)) {
          Object.entries(options.headers).forEach(([key, value]) => {
            if (typeof value === 'string') {
              headers[key] = value
            }
          })
        }
      }
      
      // Only add Authorization header if we have a token
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      return { success: true, data }
    } catch (error) {
      console.error('API request failed:', error)
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }
    }
  }

  static async uploadCSV(file: File): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)

    return this.makeRequest('/api/forecasting/upload-csv', {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header for FormData
    })
  }

  static async generateForecast(request: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/api/forecasting/forecast', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
  }

  static async getForecastModels(): Promise<ApiResponse<any>> {
    return this.makeRequest('/api/forecasting/models', {
      method: 'GET',
    })
  }

  static async getHealth(): Promise<ApiResponse<any>> {
    return this.makeRequest('/health', {
      method: 'GET',
    })
  }
} 