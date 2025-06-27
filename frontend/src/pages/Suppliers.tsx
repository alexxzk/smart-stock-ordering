import { useState, useEffect, useCallback } from 'react'
import { Plus, Edit, Trash2, Search, Building, Mail, Phone, MapPin, Loader2, AlertTriangle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { 
  getSuppliers, 
  addSupplier, 
  updateSupplier, 
  deleteSupplier,
  Supplier as SupplierType 
} from '../services/firebaseService'

interface SupplierFormData {
  name: string
  email: string
  phone: string
  address: string
  items: string[]
}

export default function Suppliers() {
  const { currentUser } = useAuth()
  const [suppliers, setSuppliers] = useState<SupplierType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingSupplier, setEditingSupplier] = useState<SupplierType | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [formData, setFormData] = useState<SupplierFormData>({
    name: '',
    email: '',
    phone: '',
    address: '',
    items: []
  })

  // Memoize loadSuppliers to prevent unnecessary re-renders
  const loadSuppliers = useCallback(async () => {
    if (!currentUser) return
    
    try {
      setLoading(true)
      setError(null)
      console.log('Loading suppliers...')
      const supplierList = await getSuppliers(currentUser.uid)
      console.log('Suppliers loaded:', supplierList.length, 'suppliers')
      setSuppliers(supplierList)
    } catch (error) {
      console.error('Error loading suppliers:', error)
      setError('Failed to load suppliers. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [currentUser])

  useEffect(() => {
    if (currentUser) {
      loadSuppliers()
    }
  }, [currentUser, loadSuppliers])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!currentUser) return

    try {
      setLoading(true)
      if (editingSupplier) {
        await updateSupplier(editingSupplier.id!, {
          ...formData,
          userId: currentUser.uid
        })
      } else {
        await addSupplier({
          ...formData,
          userId: currentUser.uid
        })
      }
      
      setShowForm(false)
      setEditingSupplier(null)
      resetForm()
      await loadSuppliers()
    } catch (error) {
      console.error('Error saving supplier:', error)
      setError('Failed to save supplier. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (supplier: SupplierType) => {
    setEditingSupplier(supplier)
    setFormData({
      name: supplier.name,
      email: supplier.email,
      phone: supplier.phone,
      address: supplier.address,
      items: supplier.items
    })
    setShowForm(true)
  }

  const handleDelete = async (supplierId: string) => {
    if (confirm('Are you sure you want to delete this supplier?')) {
      try {
        setLoading(true)
        await deleteSupplier(supplierId)
        await loadSuppliers()
      } catch (error) {
        console.error('Error deleting supplier:', error)
        setError('Failed to delete supplier. Please try again.')
      } finally {
        setLoading(false)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      address: '',
      items: []
    })
  }

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, '']
    })
  }

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index)
    })
  }

  const updateItem = (index: number, value: string) => {
    const newItems = [...formData.items]
    newItems[index] = value
    setFormData({
      ...formData,
      items: newItems
    })
  }

  const filteredSuppliers = suppliers.filter(supplier =>
    supplier.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    supplier.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Show loading state
  if (loading && suppliers.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading suppliers...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error && suppliers.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={loadSuppliers}
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
          <h2 className="text-2xl font-bold text-gray-900">Supplier Management</h2>
          <p className="text-gray-600">Manage your suppliers and their contact information</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center space-x-2"
          disabled={loading}
        >
          <Plus className="h-4 w-4" />
          <span>Add Supplier</span>
        </button>
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <Building className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Suppliers</p>
              <p className="text-2xl font-semibold text-gray-900">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : suppliers.length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <Mail className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Suppliers</p>
              <p className="text-2xl font-semibold text-gray-900">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : suppliers.filter(s => s.items.length > 0).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <MapPin className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Items</p>
              <p className="text-2xl font-semibold text-gray-900">
                {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : suppliers.reduce((sum, s) => sum + s.items.length, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search suppliers by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field pl-10"
          />
        </div>
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Supplier Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="input-field"
                  placeholder="e.g., ABC Coffee Supply"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="input-field"
                  placeholder="contact@supplier.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone *
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="input-field"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address *
                </label>
                <input
                  type="text"
                  required
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="input-field"
                  placeholder="123 Main St, City, State"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Items Supplied
              </label>
              <div className="space-y-2">
                {formData.items.map((item, index) => (
                  <div key={index} className="flex space-x-2">
                    <input
                      type="text"
                      value={item}
                      onChange={(e) => updateItem(index, e.target.value)}
                      className="input-field flex-1"
                      placeholder="e.g., Coffee Beans, Milk, Sugar"
                    />
                    <button
                      type="button"
                      onClick={() => removeItem(index)}
                      className="btn-secondary px-3"
                    >
                      Remove
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addItem}
                  className="btn-secondary"
                >
                  Add Item
                </button>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setEditingSupplier(null)
                  resetForm()
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {editingSupplier ? 'Update Supplier' : 'Add Supplier'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Suppliers Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">All Suppliers</h3>
        
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : filteredSuppliers.length === 0 ? (
          <div className="text-center py-8">
            <Building className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-500">
              {searchQuery ? 'No suppliers found matching your search' : 'No suppliers found'}
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowForm(true)}
                className="mt-2 btn-primary"
              >
                Add your first supplier
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Items
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredSuppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{supplier.name}</div>
                        <div className="text-sm text-gray-500">
                          Added {supplier.createdAt?.toDate?.()?.toLocaleDateString() || 'Recently'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{supplier.email}</div>
                      <div className="text-sm text-gray-500 flex items-center">
                        <Phone className="h-3 w-3 mr-1" />
                        {supplier.phone}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {supplier.address}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {supplier.items.slice(0, 3).map((item, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {item}
                          </span>
                        ))}
                        {supplier.items.length > 3 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            +{supplier.items.length - 3} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(supplier)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(supplier.id!)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
} 