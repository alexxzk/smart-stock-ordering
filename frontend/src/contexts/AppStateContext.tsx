import { createContext, useContext, useState, ReactNode } from 'react'

interface SalesData {
  date: string
  item: string
  quantity: number
  revenue: number
}

interface ForecastResult {
  item: string
  currentDemand: number
  predictedDemand: number
  confidence: number
  trend: 'up' | 'down' | 'stable'
}

interface AppState {
  salesData: SalesData[]
  forecastResults: ForecastResult[]
  uploadedFiles: string[]
  lastUploadDate: string | null
}

interface AppStateContextType {
  appState: AppState
  setSalesData: (data: SalesData[]) => void
  setForecastResults: (results: ForecastResult[]) => void
  addUploadedFile: (filename: string) => void
  clearData: () => void
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined)

export function useAppState() {
  const context = useContext(AppStateContext)
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppStateProvider')
  }
  return context
}

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [appState, setAppState] = useState<AppState>({
    salesData: [],
    forecastResults: [],
    uploadedFiles: [],
    lastUploadDate: null
  })

  const setSalesData = (data: SalesData[]) => {
    setAppState(prev => ({
      ...prev,
      salesData: data,
      lastUploadDate: new Date().toISOString()
    }))
  }

  const setForecastResults = (results: ForecastResult[]) => {
    setAppState(prev => ({
      ...prev,
      forecastResults: results
    }))
  }

  const addUploadedFile = (filename: string) => {
    setAppState(prev => ({
      ...prev,
      uploadedFiles: [...prev.uploadedFiles, filename]
    }))
  }

  const clearData = () => {
    setAppState({
      salesData: [],
      forecastResults: [],
      uploadedFiles: [],
      lastUploadDate: null
    })
  }

  const value = {
    appState,
    setSalesData,
    setForecastResults,
    addUploadedFile,
    clearData
  }

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  )
} 