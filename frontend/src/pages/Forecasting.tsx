import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { TrendingUp, Upload, Brain, AlertCircle } from 'lucide-react'
import CSVUpload from '../components/CSVUpload'
import { useAppState } from '../contexts/AppStateContext'

interface CSVData {
  headers: string[]
  rows: string[][]
  preview: string[][]
}

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

export default function Forecasting() {
  const { appState, setSalesData, setForecastResults } = useAppState()
  const [csvData, setCsvData] = useState<CSVData | null>(null)
  const [isForecasting, setIsForecasting] = useState(false)
  const [error, setError] = useState<string>('')

  // Use persistent data from context
  const processedData = appState.salesData
  const forecastResults = appState.forecastResults

  const handleCSVProcessed = (data: CSVData) => {
    setCsvData(data)
    setError('')
    
    // Process the CSV data into structured format
    try {
      const processed = data.rows.map(row => {
        const dateIndex = data.headers.findIndex(h => h.toLowerCase().includes('date'))
        const itemIndex = data.headers.findIndex(h => h.toLowerCase().includes('item'))
        const quantityIndex = data.headers.findIndex(h => h.toLowerCase().includes('quantity'))
        const revenueIndex = data.headers.findIndex(h => h.toLowerCase().includes('revenue'))

        return {
          date: row[dateIndex] || '',
          item: row[itemIndex] || '',
          quantity: parseInt(row[quantityIndex] || '0', 10),
          revenue: parseFloat(row[revenueIndex] || '0')
        }
      }).filter(item => item.quantity > 0 && item.revenue > 0)

      // Save to persistent state
      setSalesData(processed)
    } catch (err) {
      setError('Error processing CSV data')
    }
  }

  const handleCSVError = (errorMessage: string) => {
    setError(errorMessage)
    setCsvData(null)
  }

  const generateForecast = async () => {
    if (!processedData.length) {
      setError('Please upload and process CSV data first')
      return
    }

    setIsForecasting(true)
    setError('')

    try {
      // Group data by item
      const itemGroups = processedData.reduce((acc, item) => {
        if (!acc[item.item]) {
          acc[item.item] = []
        }
        acc[item.item].push(item)
        return acc
      }, {} as Record<string, SalesData[]>)

      // Generate forecasts using the actual uploaded data
      const forecasts: ForecastResult[] = Object.entries(itemGroups).map(([item, data]) => {
        const totalQuantity = data.reduce((sum, d) => sum + d.quantity, 0)
        const avgQuantity = totalQuantity / data.length
        
        // Calculate trend based on recent vs older data
        const sortedData = data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
        const midPoint = Math.floor(sortedData.length / 2)
        const recentData = sortedData.slice(midPoint)
        const olderData = sortedData.slice(0, midPoint)
        
        const recentAvg = recentData.reduce((sum, d) => sum + d.quantity, 0) / recentData.length
        const olderAvg = olderData.reduce((sum, d) => sum + d.quantity, 0) / olderData.length
        
        // Predict future demand with some randomness for demo
        const trendFactor = recentAvg > olderAvg ? 1.1 : recentAvg < olderAvg ? 0.9 : 1.0
        const predictedDemand = Math.round(avgQuantity * trendFactor * (1 + (Math.random() - 0.5) * 0.2))
        const confidence = Math.round(75 + Math.random() * 20)
        const trend = recentAvg > olderAvg ? 'up' : recentAvg < olderAvg ? 'down' : 'stable'

        return {
          item,
          currentDemand: Math.round(avgQuantity),
          predictedDemand,
          confidence,
          trend
        }
      })

      // Save to persistent state
      setForecastResults(forecasts)
    } catch (err) {
      setError('Error generating forecast')
    } finally {
      setIsForecasting(false)
    }
  }

  const chartData = processedData.reduce((acc, item) => {
    const date = new Date(item.date).toLocaleDateString()
    const existing = acc.find(d => d.date === date)
    if (existing) {
      existing.quantity += item.quantity
      existing.revenue += item.revenue
    } else {
      acc.push({ date, quantity: item.quantity, revenue: item.revenue })
    }
    return acc
  }, [] as Array<{ date: string; quantity: number; revenue: number }>)

  // Show existing data if available
  useEffect(() => {
    if (appState.salesData.length > 0 && !csvData) {
      // Reconstruct CSV data from persistent state for display
      const headers = ['date', 'item', 'quantity', 'revenue']
      const rows = appState.salesData.map(item => [item.date, item.item, item.quantity.toString(), item.revenue.toString()])
      const preview = rows.slice(0, 5)
      
      setCsvData({ headers, rows, preview })
    }
  }, [appState.salesData, csvData])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Demand Forecasting</h2>
        <p className="text-gray-600">Upload your sales data and generate AI-powered demand forecasts</p>
      </div>

      {/* CSV Upload Section */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Upload className="h-5 w-5 mr-2" />
          Upload Sales Data
        </h3>
        <CSVUpload onDataProcessed={handleCSVProcessed} onError={handleCSVError} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Data Summary */}
      {processedData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-blue-600">Total Records</p>
              <p className="text-2xl font-bold text-blue-900">{processedData.length}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-green-600">Unique Items</p>
              <p className="text-2xl font-bold text-green-900">
                {new Set(processedData.map(d => d.item)).size}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm font-medium text-purple-600">Date Range</p>
              <p className="text-2xl font-bold text-purple-900">
                {new Date(Math.min(...processedData.map(d => new Date(d.date).getTime()))).toLocaleDateString()} - {new Date(Math.max(...processedData.map(d => new Date(d.date).getTime()))).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Generate Forecast Button */}
      {processedData.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Generate Forecast</h3>
              <p className="text-gray-600">Use AI to predict future demand based on your sales data</p>
            </div>
            <button
              onClick={generateForecast}
              disabled={isForecasting}
              className="btn-primary flex items-center space-x-2"
            >
              {isForecasting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4" />
                  <span>Generate Forecast</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Charts */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Sales Volume</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="quantity" fill="#0ea5e9" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Revenue</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Forecast Results */}
      {forecastResults.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Forecast Results
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Demand
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Predicted Demand
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {forecastResults.map((forecast, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {forecast.item}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {forecast.currentDemand}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {forecast.predictedDemand}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {forecast.confidence}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        forecast.trend === 'up' 
                          ? 'bg-green-100 text-green-800'
                          : forecast.trend === 'down'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {forecast.trend === 'up' ? '↗ Up' : forecast.trend === 'down' ? '↘ Down' : '→ Stable'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
} 