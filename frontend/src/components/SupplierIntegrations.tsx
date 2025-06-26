import { useState, useEffect } from 'react'
import { 
  Globe, 
  Database, 
  Mail, 
  Zap, 
  CheckCircle, 
  AlertCircle,
  ExternalLink,
  RefreshCw,
  ShoppingCart
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

interface SupplierIntegration {
  id: string
  name: string
  integration_type: 'api' | 'web_scraping' | 'manual' | 'email'
  api_url?: string
  website_url?: string
  features: string[]
}

interface PricingData {
  itemId: string
  itemName: string
  price: number
  currency: string
  unit: string
  lastUpdated: string
  supplierId: string
}

interface OrderRequest {
  items: Array<{
    name: string
    quantity: number
    unit: string
    price: number
  }>
  deliveryAddress: string
  deliveryDate?: string
  notes?: string
}

export default function SupplierIntegrations() {
  const { currentUser } = useAuth()
  const [suppliers, setSuppliers] = useState<SupplierIntegration[]>([])
  const [selectedSupplier, setSelectedSupplier] = useState<string>('')
  const [pricingData, setPricingData] = useState<PricingData[]>([])
  const [loading, setLoading] = useState(false)
  const [orderForm, setOrderForm] = useState<OrderRequest>({
    items: [],
    deliveryAddress: '',
    deliveryDate: '',
    notes: ''
  })

  useEffect(() => {
    loadSuppliers()
  }, [])

  const loadSuppliers = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/supplier-integrations/suppliers', {
        headers: {
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        }
      })
      const data = await response.json()
      setSuppliers(Object.values(data.suppliers))
    } catch (error) {
      console.error('Error loading suppliers:', error)
    } finally {
      setLoading(false)
    }
  }

  const getPricing = async (supplierId: string, items: string[]) => {
    try {
      setLoading(true)
      const response = await fetch('/api/supplier-integrations/pricing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        },
        body: JSON.stringify({
          supplier_id: supplierId,
          items: items
        })
      })
      const data = await response.json()
      setPricingData(data.pricing)
    } catch (error) {
      console.error('Error getting pricing:', error)
    } finally {
      setLoading(false)
    }
  }

  const placeOrder = async (supplierId: string, order: OrderRequest) => {
    try {
      setLoading(true)
      const response = await fetch('/api/supplier-integrations/order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        },
        body: JSON.stringify({
          supplier_id: supplierId,
          ...order
        })
      })
      const data = await response.json()
      alert(`Order placed successfully! Order ID: ${data.orderId}`)
      setOrderForm({ items: [], deliveryAddress: '', deliveryDate: '', notes: '' })
    } catch (error) {
      console.error('Error placing order:', error)
      alert('Error placing order. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getIntegrationIcon = (type: string) => {
    switch (type) {
      case 'api':
        return <Zap className="h-5 w-5 text-green-600" />
      case 'web_scraping':
        return <Globe className="h-5 w-5 text-blue-600" />
      case 'manual':
        return <Database className="h-5 w-5 text-orange-600" />
      case 'email':
        return <Mail className="h-5 w-5 text-purple-600" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  const getIntegrationStatus = (type: string) => {
    switch (type) {
      case 'api':
        return { status: 'Connected', color: 'text-green-600', bg: 'bg-green-50' }
      case 'web_scraping':
        return { status: 'Active', color: 'text-blue-600', bg: 'bg-blue-50' }
      case 'manual':
        return { status: 'Manual', color: 'text-orange-600', bg: 'bg-orange-50' }
      case 'email':
        return { status: 'Email', color: 'text-purple-600', bg: 'bg-purple-50' }
      default:
        return { status: 'Unknown', color: 'text-gray-600', bg: 'bg-gray-50' }
    }
  }

  const addItemToOrder = () => {
    setOrderForm(prev => ({
      ...prev,
      items: [...prev.items, { name: '', quantity: 1, unit: 'kg', price: 0 }]
    }))
  }

  const updateOrderItem = (index: number, field: string, value: any) => {
    setOrderForm(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }))
  }

  const removeOrderItem = (index: number) => {
    setOrderForm(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Supplier Integrations</h2>
        <p className="text-gray-600">Connect with your suppliers for automated pricing and ordering</p>
      </div>

      {/* Available Suppliers */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Suppliers</h3>
        
        {loading ? (
          <div className="flex justify-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {suppliers.map((supplier) => {
              const status = getIntegrationStatus(supplier.integration_type)
              return (
                <div
                  key={supplier.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelectedSupplier(supplier.id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {getIntegrationIcon(supplier.integration_type)}
                      <h4 className="font-medium text-gray-900">{supplier.name}</h4>
                    </div>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${status.bg} ${status.color}`}>
                      {status.status}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">
                      <strong>Integration:</strong> {supplier.integration_type.replace('_', ' ').toUpperCase()}
                    </div>
                    
                    {supplier.api_url && (
                      <div className="text-sm text-gray-600">
                        <strong>API:</strong> {supplier.api_url}
                      </div>
                    )}
                    
                    {supplier.website_url && (
                      <div className="text-sm text-gray-600">
                        <strong>Website:</strong> 
                        <a 
                          href={supplier.website_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 ml-1"
                        >
                          Visit <ExternalLink className="h-3 w-3 inline" />
                        </a>
                      </div>
                    )}
                    
                    <div className="text-sm text-gray-600">
                      <strong>Features:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {supplier.features.map((feature, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Pricing and Ordering */}
      {selectedSupplier && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Get Pricing */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Get Pricing</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Items (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="coffee beans, milk, sugar"
                  className="input-field"
                  onChange={(e) => {
                    const items = e.target.value.split(',').map(item => item.trim()).filter(Boolean)
                    if (items.length > 0) {
                      getPricing(selectedSupplier, items)
                    }
                  }}
                />
              </div>
              
              {pricingData.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Pricing Results:</h4>
                  {pricingData.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{item.itemName}</p>
                        <p className="text-sm text-gray-500">{item.unit}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">
                          ${item.price.toFixed(2)} {item.currency}
                        </p>
                        <p className="text-sm text-gray-500">
                          Updated: {new Date(item.lastUpdated).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Place Order */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Place Order</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Delivery Address
                </label>
                <input
                  type="text"
                  value={orderForm.deliveryAddress}
                  onChange={(e) => setOrderForm(prev => ({ ...prev, deliveryAddress: e.target.value }))}
                  className="input-field"
                  placeholder="123 Main St, City, State"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Delivery Date
                </label>
                <input
                  type="date"
                  value={orderForm.deliveryDate}
                  onChange={(e) => setOrderForm(prev => ({ ...prev, deliveryDate: e.target.value }))}
                  className="input-field"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={orderForm.notes}
                  onChange={(e) => setOrderForm(prev => ({ ...prev, notes: e.target.value }))}
                  className="input-field"
                  rows={3}
                  placeholder="Special instructions..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Order Items
                </label>
                <div className="space-y-2">
                  {orderForm.items.map((item, index) => (
                    <div key={index} className="flex space-x-2">
                      <input
                        type="text"
                        value={item.name}
                        onChange={(e) => updateOrderItem(index, 'name', e.target.value)}
                        className="input-field flex-1"
                        placeholder="Item name"
                      />
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateOrderItem(index, 'quantity', parseFloat(e.target.value))}
                        className="input-field w-20"
                        placeholder="Qty"
                      />
                      <input
                        type="text"
                        value={item.unit}
                        onChange={(e) => updateOrderItem(index, 'unit', e.target.value)}
                        className="input-field w-20"
                        placeholder="Unit"
                      />
                      <input
                        type="number"
                        value={item.price}
                        onChange={(e) => updateOrderItem(index, 'price', parseFloat(e.target.value))}
                        className="input-field w-24"
                        placeholder="Price"
                      />
                      <button
                        onClick={() => removeOrderItem(index)}
                        className="btn-secondary px-3"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={addItemToOrder}
                    className="btn-secondary"
                  >
                    Add Item
                  </button>
                </div>
              </div>
              
              <button
                onClick={() => placeOrder(selectedSupplier, orderForm)}
                disabled={loading || orderForm.items.length === 0}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <ShoppingCart className="h-4 w-4" />
                )}
                <span>Place Order</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Integration Benefits */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integration Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <Zap className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <h4 className="font-medium text-gray-900">Automated Pricing</h4>
            <p className="text-sm text-gray-600">Get real-time pricing from suppliers automatically</p>
          </div>
          <div className="text-center">
            <ShoppingCart className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <h4 className="font-medium text-gray-900">One-Click Ordering</h4>
            <p className="text-sm text-gray-600">Place orders directly from your inventory system</p>
          </div>
          <div className="text-center">
            <CheckCircle className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <h4 className="font-medium text-gray-900">Order Tracking</h4>
            <p className="text-sm text-gray-600">Track order status and delivery updates</p>
          </div>
        </div>
      </div>
    </div>
  )
} 