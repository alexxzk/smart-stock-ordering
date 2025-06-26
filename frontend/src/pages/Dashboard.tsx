import { useState, useEffect } from 'react'
import { 
  Package, 
  TrendingUp, 
  Building, 
  AlertTriangle, 
  DollarSign,
  BarChart3,
  Calendar,
  ShoppingCart,
  FileText
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useAppState } from '../contexts/AppStateContext'
import { 
  getInventoryItems, 
  getSuppliers, 
  getSalesData 
} from '../services/firebaseService'

interface DashboardStats {
  totalInventoryItems: number
  totalSuppliers: number
  totalSalesRecords: number
  lowStockItems: number
  totalInventoryValue: number
  recentSales: any[]
}

export default function Dashboard() {
  const { currentUser } = useAuth()
  const { appState } = useAppState()
  const [stats, setStats] = useState<DashboardStats>({
    totalInventoryItems: 0,
    totalSuppliers: 0,
    totalSalesRecords: 0,
    lowStockItems: 0,
    totalInventoryValue: 0,
    recentSales: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (currentUser) {
      loadDashboardData()
    }
  }, [currentUser])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load all data in parallel
      const [inventoryItems, suppliers, salesData] = await Promise.all([
        getInventoryItems(currentUser!.uid),
        getSuppliers(currentUser!.uid),
        getSalesData(currentUser!.uid)
      ])

      // Calculate stats
      const lowStockItems = inventoryItems.filter(item => item.currentStock <= item.minStock).length
      const totalInventoryValue = inventoryItems.reduce((sum, item) => 
        sum + (item.currentStock * item.costPerUnit), 0
      )
      
      // Use persistent sales data if available, otherwise use Firebase data
      const recentSales = appState.salesData.length > 0 
        ? appState.salesData.slice(-5).reverse() // Last 5 sales from uploaded data
        : salesData.slice(0, 5) // Last 5 sales from Firebase

      setStats({
        totalInventoryItems: inventoryItems.length,
        totalSuppliers: suppliers.length,
        totalSalesRecords: appState.salesData.length || salesData.length,
        lowStockItems,
        totalInventoryValue,
        recentSales
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to your smart stock management system</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Inventory Items</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalInventoryItems}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <Building className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Suppliers</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalSuppliers}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Sales Records</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalSalesRecords}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Inventory Value</p>
              <p className="text-2xl font-semibold text-gray-900">
                {formatCurrency(stats.totalInventoryValue)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {appState.lastUploadDate && (
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              <p className="text-gray-600">Last data upload: {formatDate(appState.lastUploadDate)}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Uploaded Files</p>
              <p className="text-2xl font-semibold text-gray-900">{appState.uploadedFiles.length}</p>
            </div>
          </div>
        </div>
      )}

      {/* Charts and Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Sales */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Sales</h3>
            <TrendingUp className="h-5 w-5 text-gray-400" />
          </div>
          
          {stats.recentSales.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingCart className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-gray-500">No sales data yet</p>
              <p className="text-sm text-gray-400">Upload your sales data to see recent activity</p>
            </div>
          ) : (
            <div className="space-y-3">
              {stats.recentSales.map((sale, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{sale.item}</p>
                    <p className="text-sm text-gray-500">{formatDate(sale.date)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {sale.quantity} × {formatCurrency(sale.revenue / sale.quantity)}
                    </p>
                    <p className="text-sm text-gray-500">{formatCurrency(sale.revenue)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <a
              href="/forecasting"
              className="flex items-center p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-blue-600 mr-3" />
              <div>
                <p className="font-medium text-blue-900">Upload Sales Data</p>
                <p className="text-sm text-blue-700">Upload CSV and generate forecasts</p>
              </div>
            </a>

            <a
              href="/inventory"
              className="flex items-center p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
            >
              <Package className="h-5 w-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-green-900">Manage Inventory</p>
                <p className="text-sm text-green-700">Add, edit, or view inventory items</p>
              </div>
            </a>

            <a
              href="/orders"
              className="flex items-center p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
            >
              <ShoppingCart className="h-5 w-5 text-purple-600 mr-3" />
              <div>
                <p className="font-medium text-purple-900">AI Orders</p>
                <p className="text-sm text-purple-700">Generate smart supplier orders</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
} 