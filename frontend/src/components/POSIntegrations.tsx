import { useState, useEffect } from 'react'
import { 
  CreditCard, 
  Database, 
  Zap, 
  CheckCircle, 
  AlertCircle,
  ExternalLink,
  RefreshCw,
  Settings,
  BarChart3,
  TrendingUp,
  Package,
  Calendar
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

interface POSSystem {
  id: string
  name: string
  description: string
  api_base: string
  features: string[]
  auth_type: string
  webhook_support: boolean
}

interface POSConnection {
  id: string
  pos_type: string
  name: string
  config: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
  last_sync?: string
  sync_status: string
}

interface SalesData {
  date: string
  total_sales: number
  items_sold: Record<string, number>
  revenue_by_item: Record<string, number>
}

interface InventoryData {
  item_id: string
  item_name: string
  current_stock: number
  unit: string
  last_updated: string
}

export default function POSIntegrations() {
  const { currentUser } = useAuth()
  const [posSystems, setPosSystems] = useState<POSSystem[]>([])
  const [connections, setConnections] = useState<POSConnection[]>([])
  const [selectedConnection, setSelectedConnection] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [showConnectForm, setShowConnectForm] = useState(false)
  const [selectedPOS, setSelectedPOS] = useState<string>('')
  const [connectionForm, setConnectionForm] = useState({
    name: '',
    api_key: '',
    access_token: '',
    store_id: '',
    webhook_url: ''
  })
  const [salesData, setSalesData] = useState<SalesData[]>([])
  const [inventoryData, setInventoryData] = useState<InventoryData[]>([])

  useEffect(() => {
    loadPOSSystems()
    loadConnections()
  }, [])

  const loadPOSSystems = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/pos-integrations/systems', {
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      setPosSystems(Object.values(data.pos_systems))
    } catch (error) {
      console.error('Error loading POS systems:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadConnections = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/pos-integrations/connections', {
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      setConnections(data)
    } catch (error) {
      console.error('Error loading connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const createConnection = async () => {
    try {
      setLoading(true)
      
      const config: Record<string, any> = {}
      if (connectionForm.api_key) config.api_key = connectionForm.api_key
      if (connectionForm.access_token) config.access_token = connectionForm.access_token
      if (connectionForm.store_id) config.store_id = connectionForm.store_id
      if (connectionForm.webhook_url) config.webhook_url = connectionForm.webhook_url

      const response = await fetch('/api/pos-integrations/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        },
        body: JSON.stringify({
          pos_type: selectedPOS,
          name: connectionForm.name,
          config: config,
          is_active: true
        })
      })

      if (response.ok) {
        const data = await response.json()
        setConnections(prev => [...prev, data])
        setShowConnectForm(false)
        setConnectionForm({ name: '', api_key: '', access_token: '', store_id: '', webhook_url: '' })
        setSelectedPOS('')
        alert('POS connection created successfully!')
      } else {
        const error = await response.json()
        alert(`Error creating connection: ${error.detail}`)
      }
    } catch (error) {
      console.error('Error creating connection:', error)
      alert('Error creating connection. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const testConnection = async (connectionId: string) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/pos-integrations/connections/${connectionId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      
      if (data.test_result.success) {
        alert('Connection test successful!')
      } else {
        alert(`Connection test failed: ${data.test_result.error}`)
      }
    } catch (error) {
      console.error('Error testing connection:', error)
      alert('Error testing connection. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const syncData = async (connectionId: string, syncType: string = 'all') => {
    try {
      setLoading(true)
      const response = await fetch(`/api/pos-integrations/connections/${connectionId}/sync?sync_type=${syncType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      
      if (data.status === 'success') {
        alert(`Data sync completed! ${data.sync_result.sales_synced} sales records, ${data.sync_result.inventory_synced} inventory items`)
        loadConnections() // Refresh connections to update last_sync
      } else {
        alert('Data sync failed. Please try again.')
      }
    } catch (error) {
      console.error('Error syncing data:', error)
      alert('Error syncing data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getSalesData = async (connectionId: string) => {
    try {
      setLoading(true)
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 30 days ago
      const endDate = new Date().toISOString().split('T')[0] // Today
      
      const response = await fetch(`/api/pos-integrations/connections/${connectionId}/sales?start_date=${startDate}&end_date=${endDate}`, {
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      setSalesData(data.sales_data)
      setSelectedConnection(connectionId)
    } catch (error) {
      console.error('Error fetching sales data:', error)
      alert('Error fetching sales data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getInventoryData = async (connectionId: string) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/pos-integrations/connections/${connectionId}/inventory`, {
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      setInventoryData(data.inventory_data)
      setSelectedConnection(connectionId)
    } catch (error) {
      console.error('Error fetching inventory data:', error)
      alert('Error fetching inventory data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const deleteConnection = async (connectionId: string) => {
    if (!confirm('Are you sure you want to delete this connection?')) return
    
    try {
      setLoading(true)
      const response = await fetch(`/api/pos-integrations/connections/${connectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      
      if (response.ok) {
        setConnections(prev => prev.filter(conn => conn.id !== connectionId))
        alert('Connection deleted successfully!')
      } else {
        alert('Error deleting connection. Please try again.')
      }
    } catch (error) {
      console.error('Error deleting connection:', error)
      alert('Error deleting connection. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getPOSIcon = (posType: string) => {
    switch (posType) {
      case 'square':
        return <CreditCard className="h-5 w-5 text-green-600" />
      case 'toast':
        return <Database className="h-5 w-5 text-blue-600" />
      case 'clover':
        return <Zap className="h-5 w-5 text-orange-600" />
      case 'lightspeed':
        return <BarChart3 className="h-5 w-5 text-purple-600" />
      case 'shopify':
        return <Package className="h-5 w-5 text-indigo-600" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  const getSyncStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'text-green-600 bg-green-50'
      case 'syncing':
        return 'text-blue-600 bg-blue-50'
      case 'error':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">POS Integrations</h2>
        <p className="text-gray-600">Connect your Point of Sale system for real-time inventory updates</p>
      </div>

      {/* Available POS Systems */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Available POS Systems</h3>
          <button
            onClick={() => setShowConnectForm(true)}
            className="btn-primary"
          >
            Connect New POS
          </button>
        </div>
        
        {loading ? (
          <div className="flex justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {posSystems.map((pos) => (
              <div
                key={pos.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center space-x-2 mb-3">
                  {getPOSIcon(pos.id)}
                  <h4 className="font-medium text-gray-900">{pos.name}</h4>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{pos.description}</p>
                
                <div className="space-y-2">
                  <div className="text-sm text-gray-600">
                    <strong>Features:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {pos.features.map((feature, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {feature.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    <strong>Auth:</strong> {pos.auth_type.toUpperCase()}
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    <strong>Webhooks:</strong> {pos.webhook_support ? 'Supported' : 'Not supported'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* POS Connections */}
      {connections.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Your POS Connections</h3>
          
          <div className="space-y-4">
            {connections.map((connection) => (
              <div
                key={connection.id}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    {getPOSIcon(connection.pos_type)}
                    <div>
                      <h4 className="font-medium text-gray-900">{connection.name}</h4>
                      <p className="text-sm text-gray-500">{connection.pos_type.toUpperCase()}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSyncStatusColor(connection.sync_status)}`}>
                      {connection.sync_status}
                    </span>
                    <button
                      onClick={() => deleteConnection(connection.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 mb-4">
                  <button
                    onClick={() => testConnection(connection.id)}
                    className="btn-secondary text-sm"
                  >
                    Test Connection
                  </button>
                  <button
                    onClick={() => syncData(connection.id, 'sales')}
                    className="btn-secondary text-sm"
                  >
                    Sync Sales
                  </button>
                  <button
                    onClick={() => syncData(connection.id, 'inventory')}
                    className="btn-secondary text-sm"
                  >
                    Sync Inventory
                  </button>
                  <button
                    onClick={() => syncData(connection.id, 'all')}
                    className="btn-secondary text-sm"
                  >
                    Sync All
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <button
                    onClick={() => getSalesData(connection.id)}
                    className="btn-secondary text-sm"
                  >
                    View Sales Data
                  </button>
                  <button
                    onClick={() => getInventoryData(connection.id)}
                    className="btn-secondary text-sm"
                  >
                    View Inventory Data
                  </button>
                </div>
                
                {connection.last_sync && (
                  <p className="text-xs text-gray-500 mt-2">
                    Last sync: {new Date(connection.last_sync).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connect Form Modal */}
      {showConnectForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Connect POS System</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  POS System
                </label>
                <select
                  value={selectedPOS}
                  onChange={(e) => setSelectedPOS(e.target.value)}
                  className="input-field"
                >
                  <option value="">Select a POS system</option>
                  {posSystems.map((pos) => (
                    <option key={pos.id} value={pos.id}>{pos.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Connection Name
                </label>
                <input
                  type="text"
                  value={connectionForm.name}
                  onChange={(e) => setConnectionForm(prev => ({ ...prev, name: e.target.value }))}
                  className="input-field"
                  placeholder="My Square Store"
                />
              </div>
              
              {selectedPOS && (
                <>
                  {posSystems.find(p => p.id === selectedPOS)?.auth_type === 'api_key' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Key
                      </label>
                      <input
                        type="password"
                        value={connectionForm.api_key}
                        onChange={(e) => setConnectionForm(prev => ({ ...prev, api_key: e.target.value }))}
                        className="input-field"
                        placeholder="Enter API key"
                      />
                    </div>
                  )}
                  
                  {posSystems.find(p => p.id === selectedPOS)?.auth_type === 'oauth2' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Access Token
                      </label>
                      <input
                        type="password"
                        value={connectionForm.access_token}
                        onChange={(e) => setConnectionForm(prev => ({ ...prev, access_token: e.target.value }))}
                        className="input-field"
                        placeholder="Enter access token"
                      />
                    </div>
                  )}
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Store ID (Optional)
                    </label>
                    <input
                      type="text"
                      value={connectionForm.store_id}
                      onChange={(e) => setConnectionForm(prev => ({ ...prev, store_id: e.target.value }))}
                      className="input-field"
                      placeholder="Enter store ID"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Webhook URL (Optional)
                    </label>
                    <input
                      type="url"
                      value={connectionForm.webhook_url}
                      onChange={(e) => setConnectionForm(prev => ({ ...prev, webhook_url: e.target.value }))}
                      className="input-field"
                      placeholder="https://your-domain.com/webhook"
                    />
                  </div>
                </>
              )}
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowConnectForm(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={createConnection}
                disabled={loading || !selectedPOS || !connectionForm.name}
                className="btn-primary flex-1"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : 'Connect'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sales Data Display */}
      {salesData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sales Data</h3>
          
          <div className="space-y-4">
            {salesData.map((sale, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-gray-900">{sale.date}</h4>
                  <span className="text-lg font-bold text-green-600">
                    ${sale.total_sales.toFixed(2)}
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium text-gray-700 mb-2">Items Sold</h5>
                    <div className="space-y-1">
                      {Object.entries(sale.items_sold).map(([item, quantity]) => (
                        <div key={item} className="flex justify-between text-sm">
                          <span>{item}</span>
                          <span>{quantity}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-gray-700 mb-2">Revenue by Item</h5>
                    <div className="space-y-1">
                      {Object.entries(sale.revenue_by_item).map(([item, revenue]) => (
                        <div key={item} className="flex justify-between text-sm">
                          <span>{item}</span>
                          <span>${revenue.toFixed(2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Inventory Data Display */}
      {inventoryData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Inventory Data</h3>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Updated
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {inventoryData.map((item) => (
                  <tr key={item.item_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.item_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.current_stock}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(item.last_updated).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Integration Benefits */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <h4 className="font-medium text-gray-900">Real-time Updates</h4>
            <p className="text-sm text-gray-600">Automatic inventory updates from your POS system</p>
          </div>
          <div className="text-center">
            <BarChart3 className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <h4 className="font-medium text-gray-900">Sales Analytics</h4>
            <p className="text-sm text-gray-600">Track sales patterns and optimize inventory</p>
          </div>
          <div className="text-center">
            <CheckCircle className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <h4 className="font-medium text-gray-900">Accurate Forecasting</h4>
            <p className="text-sm text-gray-600">Better predictions with real sales data</p>
          </div>
        </div>
      </div>
    </div>
  )
} 