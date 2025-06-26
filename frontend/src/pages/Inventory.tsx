import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Package, AlertTriangle, CheckCircle, Upload } from 'lucide-react'
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
  currentStock: number
  minStock: number
  maxStock: number
  unit: string
  costPerUnit: number
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
  const [showForm, setShowForm] = useState(false)
  const [showImport, setShowImport] = useState(false)
  const [editingItem, setEditingItem] = useState<InventoryItemType | null>(null)
  const [formData, setFormData] = useState<InventoryFormData>({
    name: '',
    category: 'Beverages',
    currentStock: 0,
    minStock: 0,
    maxStock: 100,
    unit: 'kg',
    costPerUnit: 0,
    supplierId: ''
  })

  useEffect(() => {
    if (currentUser) {
      loadInventory()
    }
  }, [currentUser])

  const loadInventory = async () => {
    try {
      setLoading(true)
      const items = await getInventoryItems(currentUser!.uid)
      setInventory(items)
    } catch (error) {
      console.error('Error loading inventory:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!currentUser) return

    try {
      if (editingItem) {
        await updateInventoryItem(editingItem.id!, {
          ...formData,
          userId: currentUser.uid
        })
      } else {
        await addInventoryItem({
          ...formData,
          userId: currentUser.uid
        })
      }
      
      setShowForm(false)
      setEditingItem(null)
      resetForm()
      loadInventory()
    } catch (error) {
      console.error('Error saving inventory item:', error)
    }
  }

  const handleEdit = (item: InventoryItemType) => {
    setEditingItem(item)
    setFormData({
      name: item.name,
      category: item.category,
      currentStock: item.currentStock,
      minStock: item.minStock,
      maxStock: item.maxStock,
      unit: item.unit,
      costPerUnit: item.costPerUnit,
      supplierId: item.supplierId
    })
    setShowForm(true)
  }

  const handleDelete = async (itemId: string) => {
    if (confirm('Are you sure you want to delete this item?')) {
      try {
        await deleteInventoryItem(itemId)
        loadInventory()
      } catch (error) {
        console.error('Error deleting inventory item:', error)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      category: 'Beverages',
      currentStock: 0,
      minStock: 0,
      maxStock: 100,
      unit: 'kg',
      costPerUnit: 0,
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
          >
            <Plus className="h-4 w-4" />
            <span>Add Item</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Items</p>
              <p className="text-2xl font-semibold text-gray-900">{inventory.length}</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Low Stock</p>
              <p className="text-2xl font-semibold text-gray-900">{lowStockItems}</p>
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
                  onChange={(e) => setFormData({...formData, currentStock: Number(e.target.value)})}
                  className="input-field"
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
                  onChange={(e) => setFormData({...formData, minStock: Number(e.target.value)})}
                  className="input-field"
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
                  onChange={(e) => setFormData({...formData, maxStock: Number(e.target.value)})}
                  className="input-field"
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
                  onChange={(e) => setFormData({...formData, costPerUnit: Number(e.target.value)})}
                  className="input-field"
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
        
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : inventory.length === 0 ? (
          <div className="text-center py-8">
            <Package className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-500">No inventory items found</p>
            <div className="mt-4 space-x-3">
              <button
                onClick={() => {
                  setShowForm(true)
                  setShowImport(false)
                }}
                className="btn-primary"
              >
                Add your first item
              </button>
              <button
                onClick={() => {
                  setShowImport(true)
                  setShowForm(false)
                }}
                className="btn-secondary"
              >
                Import from CSV
              </button>
            </div>
          </div>
        ) : (
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
        )}
      </div>
    </div>
  )
} 