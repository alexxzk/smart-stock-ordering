import { useState, useEffect, useCallback } from 'react'
import { Plus, Edit, Trash2, Package, AlertTriangle, CheckCircle, Upload, Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { 
  getInventoryItems, 
  addInventoryItem, 
  updateInventoryItem, 
  deleteInventoryItem,
  InventoryItem as InventoryItemType 
} from '../services/firebaseService'
import InventoryImport from '../components/InventoryImport'

interface InventoryFormData {
  name: string
  category: string
  currentStock: string
  minStock: string
  maxStock: string
  unit: string
  costPerUnit: string
  supplierId: string
}

const categories = [
  'Beverages', 'Food', 'Dairy', 'Produce', 'Meat', 'Pantry', 
  'Cleaning', 'Paper Goods', 'Equipment', 'Other'
]

const units = ['kg', 'g', 'l', 'ml', 'pcs', 'boxes', 'bags', 'units']

export default function Inventory() {
  const { currentUser } = useAuth()
  const [inventory, setInventory] = useState<InventoryItemType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [showImport, setShowImport] = useState(false)
  const [editingItem, setEditingItem] = useState<InventoryItemType | null>(null)
  const [formData, setFormData] = useState<InventoryFormData>({
    name: '',
    category: 'Beverages',
    currentStock: '',
    minStock: '',
    maxStock: '',
    unit: 'kg',
    costPerUnit: '',
    supplierId: ''
  })

  // Memoize loadInventory to prevent unnecessary re-renders
  const loadInventory = useCallback(async () => {
    if (!currentUser) return
    
    try {
      setLoading(true)
      setError(null)
      console.log('Loading inventory...')
      const items = await getInventoryItems(currentUser.uid)
      console.log('Inventory loaded:', items.length, 'items')
      setInventory(items)
    } catch (error) {
      console.error('Error loading inventory:', error)
      setError('Failed to load inventory. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [currentUser])

  useEffect(() => {
    if (currentUser) {
      loadInventory()
    }
  }, [currentUser, loadInventory])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!currentUser) return

    try {
      setLoading(true)
      const itemData = {
        ...formData,
        currentStock: Number(formData.currentStock),
        minStock: Number(formData.minStock),
        maxStock: Number(formData.maxStock),
        costPerUnit: Number(formData.costPerUnit),
        userId: currentUser.uid
      }
      if (editingItem) {
        await updateInventoryItem(editingItem.id!, itemData)
      } else {
        await addInventoryItem(itemData)
      }
      
      setShowForm(false)
      setEditingItem(null)
      resetForm()
      await loadInventory()
    } catch (error) {
      console.error('Error saving inventory item:', error)
      setError('Failed to save item. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (item: InventoryItemType) => {
    setEditingItem(item)
    setFormData({
      name: item.name,
      category: item.category,
      currentStock: String(item.currentStock),
      minStock: String(item.minStock),
      maxStock: String(item.maxStock),
      unit: item.unit,
      costPerUnit: String(item.costPerUnit),
      supplierId: item.supplierId
    })
    setShowForm(true)
  }

  const handleDelete = async (itemId: string) => {
    if (confirm('Are you sure you want to delete this item?')) {
      try {
        setLoading(true)
        await deleteInventoryItem(itemId)
        await loadInventory()
      } catch (error) {
        console.error('Error deleting inventory item:', error)
        setError('Failed to delete item. Please try again.')
      } finally {
        setLoading(false)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      category: 'Beverages',
      currentStock: '',
      minStock: '',
      maxStock: '',
      unit: 'kg',
      costPerUnit: '',
      supplierId: ''
    })
  }

  const getStockStatus = (item: InventoryItemType) => {
    if (item.currentStock <= item.minStock) {
      return { status: 'low', icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' }
    } else if (item.currentStock >= item.maxStock * 0.8) {
      return { status: 'high', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' }
    } else {
      return { status: 'normal', icon: Package, color: 'text-blue-600', bg: 'bg-blue-50' }
    }
  }

  const totalValue = inventory.reduce((sum, item) => sum + (item.currentStock * item.costPerUnit), 0)
  const lowStockItems = inventory.filter(item => item.currentStock <= item.minStock).length

  const handleImportComplete = (count: number) => {
    loadInventory() // Reload inventory after import
  }

  // Show loading state
  if (loading && inventory.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading inventory...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error && inventory.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={loadInventory}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Inventory Management</h2>
          <p className="text-gray-600">Track your stock levels and manage inventory</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {
              setShowImport(true)
              setShowForm(false)
            }}
            className="btn-secondary flex items-center space-x-2"
            disabled={loading}
          >
            <Upload className="h-4 w-4" />
            <span>Import CSV</span>
          </button>
          <button
            onClick={() => {
              setShowForm(true)
              setShowImport(false)
            }}
            className="btn-primary flex items-center space-x-2"
            disabled={loading}
          >
            <Plus className="h-4 w-4" />
            <span>Add Item</span>
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <p className="ml-2 text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Items</p>
              <p className="text-2xl font-semibold text-gray-900">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : inventory.length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Low Stock</p>
              <p className="text-2xl font-semibold text-gray-900">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : lowStockItems}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">In Stock</p>
              <p className="text-2xl font-semibold text-gray-900">
                {inventory.filter(item => item.currentStock > item.minStock).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Value</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${totalValue.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Import Section */}
      {showImport && (
        <InventoryImport 
          onImportComplete={handleImportComplete}
          onError={(error) => console.error('Import error:', error)}
        />
      )}

      {/* Add/Edit Form */}
      {showForm && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingItem ? 'Edit Inventory Item' : 'Add New Item'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Item Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="input-field"
                  placeholder="e.g., Coffee Beans"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="input-field"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Stock *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  value={formData.currentStock}
                  onChange={e => setFormData({ ...formData, currentStock: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400 appearance-none transition"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit *
                </label>
                <select
                  value={formData.unit}
                  onChange={(e) => setFormData({...formData, unit: e.target.value})}
                  className="input-field"
                >
                  {units.map(unit => (
                    <option key={unit} value={unit}>{unit}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Stock *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  value={formData.minStock}
                  onChange={e => setFormData({ ...formData, minStock: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400 appearance-none transition"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Maximum Stock *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  value={formData.maxStock}
                  onChange={e => setFormData({ ...formData, maxStock: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400 appearance-none transition"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cost per Unit ($) *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={formData.costPerUnit}
                  onChange={e => setFormData({ ...formData, costPerUnit: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder-gray-400 appearance-none transition"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Supplier ID
                </label>
                <input
                  type="text"
                  value={formData.supplierId}
                  onChange={(e) => setFormData({...formData, supplierId: e.target.value})}
                  className="input-field"
                  placeholder="Optional"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setEditingItem(null)
                  resetForm()
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {editingItem ? 'Update Item' : 'Add Item'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Inventory Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Inventory</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Item
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {inventory.map((item) => {
                const stockStatus = getStockStatus(item)
                const StatusIcon = stockStatus.icon
                
                return (
                  <tr key={item.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{item.name}</div>
                        <div className="text-sm text-gray-500">${item.costPerUnit}/{item.unit}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {item.currentStock} {item.unit}
                      </div>
                      <div className="text-sm text-gray-500">
                        Min: {item.minStock} | Max: {item.maxStock}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${stockStatus.bg}`}>
                        <StatusIcon className={`h-3 w-3 mr-1 ${stockStatus.color}`} />
                        {stockStatus.status === 'low' ? 'Low Stock' : 
                         stockStatus.status === 'high' ? 'High Stock' : 'Normal'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${(item.currentStock * item.costPerUnit).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(item)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id!)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
} 