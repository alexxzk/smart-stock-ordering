import { useState, useEffect } from 'react'
import { ShoppingCart, Brain, AlertTriangle, CheckCircle, Clock, Truck } from 'lucide-react'

interface AIRecommendation {
  ingredient_name: string
  ai_predicted_packs: number
  current_stock: number
  pack_size: number
  total_amount_needed: number
  total_cost: number
  supplier: string
  urgency: string
  explanation: string
  model_accuracy: number
}

interface SupplierOrder {
  id: string
  supplier_name: string
  order_items: Array<{
    ingredient: string
    packs_needed: number
    pack_size: number
    cost_per_pack: number
    total_cost: number
    urgency: string
  }>
  total_cost: number
  delivery_date: string
  order_status: 'pending' | 'confirmed' | 'delivered' | 'cancelled'
  created_at: string
  notes: string
}

const mockAIRecommendations: AIRecommendation[] = [
  {
    ingredient_name: 'Coffee Beans',
    ai_predicted_packs: 2,
    current_stock: 15.5,
    pack_size: 10,
    total_amount_needed: 20,
    total_cost: 240,
    supplier: 'Coffee Supply Co',
    urgency: 'medium',
    explanation: 'Based on your ordering patterns, particularly on Mondays and winter weather conditions',
    model_accuracy: 0.88
  },
  {
    ingredient_name: 'Milk',
    ai_predicted_packs: 3,
    current_stock: 8.0,
    pack_size: 4,
    total_amount_needed: 12,
    total_cost: 24,
    supplier: 'Dairy Fresh',
    urgency: 'high',
    explanation: 'Based on your ordering patterns, particularly on weekends and current low stock levels',
    model_accuracy: 0.92
  },
  {
    ingredient_name: 'Sugar',
    ai_predicted_packs: 1,
    current_stock: 12.0,
    pack_size: 25,
    total_amount_needed: 25,
    total_cost: 45,
    supplier: 'Sweet Supplies',
    urgency: 'low',
    explanation: 'Based on your ordering patterns, particularly on weekdays and current adequate stock',
    model_accuracy: 0.85
  }
]

const mockOrders: SupplierOrder[] = [
  {
    id: 'order_001',
    supplier_name: 'Coffee Supply Co',
    order_items: [
      {
        ingredient: 'Coffee Beans',
        packs_needed: 2,
        pack_size: 10,
        cost_per_pack: 120,
        total_cost: 240,
        urgency: 'high'
      }
    ],
    total_cost: 240,
    delivery_date: '2024-01-18',
    order_status: 'confirmed',
    created_at: '2024-01-15T10:30:00Z',
    notes: 'Regular weekly order'
  },
  {
    id: 'order_002',
    supplier_name: 'Dairy Fresh',
    order_items: [
      {
        ingredient: 'Milk',
        packs_needed: 3,
        pack_size: 4,
        cost_per_pack: 8,
        total_cost: 24,
        urgency: 'medium'
      },
      {
        ingredient: 'Cheese',
        packs_needed: 1,
        pack_size: 5,
        cost_per_pack: 35,
        total_cost: 35,
        urgency: 'low'
      }
    ],
    total_cost: 59,
    delivery_date: '2024-01-16',
    order_status: 'delivered',
    created_at: '2024-01-14T14:20:00Z',
    notes: 'Daily delivery'
  }
]

export default function Orders() {
  const [aiRecommendations, setAiRecommendations] = useState<AIRecommendation[]>(mockAIRecommendations)
  const [orders, setOrders] = useState<SupplierOrder[]>(mockOrders)
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([])
  const [isGeneratingOrder, setIsGeneratingOrder] = useState(false)

  const totalRecommendedCost = aiRecommendations.reduce((sum, rec) => sum + rec.total_cost, 0)
  const pendingOrders = orders.filter(order => order.order_status === 'pending')
  const deliveredOrders = orders.filter(order => order.order_status === 'delivered')

  const handleSelectRecommendation = (ingredientName: string) => {
    setSelectedRecommendations(prev => 
      prev.includes(ingredientName)
        ? prev.filter(name => name !== ingredientName)
        : [...prev, ingredientName]
    )
  }

  const handleGenerateOrder = () => {
    setIsGeneratingOrder(true)
    // Simulate API call
    setTimeout(() => {
      const newOrder: SupplierOrder = {
        id: `order_${Date.now()}`,
        supplier_name: 'AI Generated Order',
        order_items: aiRecommendations
          .filter(rec => selectedRecommendations.includes(rec.ingredient_name))
          .map(rec => ({
            ingredient: rec.ingredient_name,
            packs_needed: rec.ai_predicted_packs,
            pack_size: rec.pack_size,
            cost_per_pack: rec.total_cost / rec.ai_predicted_packs,
            total_cost: rec.total_cost,
            urgency: rec.urgency
          })),
        total_cost: aiRecommendations
          .filter(rec => selectedRecommendations.includes(rec.ingredient_name))
          .reduce((sum, rec) => sum + rec.total_cost, 0),
        delivery_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        order_status: 'pending',
        created_at: new Date().toISOString(),
        notes: 'AI-generated order based on learned patterns'
      }
      
      setOrders(prev => [newOrder, ...prev])
      setSelectedRecommendations([])
      setIsGeneratingOrder(false)
    }, 2000)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'confirmed':
        return <CheckCircle className="h-5 w-5 text-blue-500" />
      case 'delivered':
        return <Truck className="h-5 w-5 text-green-500" />
      case 'cancelled':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return 'text-red-600 bg-red-50'
      case 'high':
        return 'text-orange-600 bg-orange-50'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50'
      default:
        return 'text-green-600 bg-green-50'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">AI-Powered Orders</h2>
        <p className="text-gray-600">Smart supplier orders based on learned behavior</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <Brain className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">AI Recommendations</p>
              <p className="text-2xl font-semibold text-gray-900">{aiRecommendations.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <ShoppingCart className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Orders</p>
              <p className="text-2xl font-semibold text-gray-900">{orders.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending</p>
              <p className="text-2xl font-semibold text-gray-900">{pendingOrders.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <Truck className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Delivered</p>
              <p className="text-2xl font-semibold text-gray-900">{deliveredOrders.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">AI Recommendations</h3>
          <div className="flex space-x-3">
            <span className="text-sm text-gray-500">
              Total: ${totalRecommendedCost.toFixed(2)}
            </span>
            <button
              onClick={handleGenerateOrder}
              disabled={selectedRecommendations.length === 0 || isGeneratingOrder}
              className="btn-primary disabled:opacity-50"
            >
              {isGeneratingOrder ? 'Generating...' : 'Generate Order'}
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {aiRecommendations.map((recommendation) => (
            <div
              key={recommendation.ingredient_name}
              className={`border rounded-lg p-4 ${
                selectedRecommendations.includes(recommendation.ingredient_name)
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <input
                    type="checkbox"
                    checked={selectedRecommendations.includes(recommendation.ingredient_name)}
                    onChange={() => handleSelectRecommendation(recommendation.ingredient_name)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">
                      {recommendation.ingredient_name}
                    </h4>
                    <p className="text-sm text-gray-500">{recommendation.explanation}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {recommendation.ai_predicted_packs} packs
                      </p>
                      <p className="text-sm text-gray-500">
                        ${recommendation.total_cost.toFixed(2)}
                      </p>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getUrgencyColor(recommendation.urgency)}`}>
                      {recommendation.urgency}
                    </span>
                    <div className="text-xs text-gray-500">
                      {Math.round(recommendation.model_accuracy * 100)}% accuracy
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Order History */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Order History</h3>
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">
                    {order.supplier_name}
                  </h4>
                  <p className="text-sm text-gray-500">
                    Order #{order.id} • {new Date(order.created_at).toLocaleDateString()}
                  </p>
                  <div className="mt-2 space-y-1">
                    {order.order_items.map((item, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        {item.ingredient}: {item.packs_needed} packs (${item.total_cost.toFixed(2)})
                      </div>
                    ))}
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(order.order_status)}
                    <span className="text-sm font-medium capitalize text-gray-900">
                      {order.order_status}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-900 mt-1">
                    ${order.total_cost.toFixed(2)}
                  </p>
                  {order.delivery_date && (
                    <p className="text-xs text-gray-500">
                      Due: {order.delivery_date}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 