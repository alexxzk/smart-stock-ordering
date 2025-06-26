import { 
  collection, 
  doc, 
  addDoc, 
  updateDoc, 
  deleteDoc, 
  getDocs, 
  getDoc, 
  query, 
  where, 
  orderBy,
  Timestamp 
} from 'firebase/firestore'
import { db } from '../config/firebase'

// Types
export interface SalesData {
  id?: string
  date: string
  item: string
  quantity: number
  revenue: number
  userId: string
  createdAt: Timestamp
}

export interface Supplier {
  id?: string
  name: string
  email: string
  phone: string
  address: string
  items: string[]
  userId: string
  createdAt: Timestamp
}

export interface InventoryItem {
  id?: string
  name: string
  category: string
  currentStock: number
  minStock: number
  maxStock: number
  unit: string
  costPerUnit: number
  supplierId: string
  userId: string
  lastUpdated: Timestamp
}

export interface MenuItem {
  id?: string
  name: string
  category: string
  price: number
  ingredients: {
    itemId: string
    itemName: string
    quantity: number
    unit: string
  }[]
  userId: string
  createdAt: Timestamp
}

// Sales Data Operations
export const saveSalesData = async (salesData: Omit<SalesData, 'id' | 'createdAt'>) => {
  try {
    const docRef = await addDoc(collection(db, 'sales'), {
      ...salesData,
      createdAt: Timestamp.now()
    })
    return { id: docRef.id, ...salesData }
  } catch (error) {
    console.error('Error saving sales data:', error)
    throw error
  }
}

export const getSalesData = async (userId: string, startDate?: string, endDate?: string) => {
  try {
    let q = query(
      collection(db, 'sales'),
      where('userId', '==', userId),
      orderBy('date', 'desc')
    )
    
    if (startDate && endDate) {
      q = query(
        collection(db, 'sales'),
        where('userId', '==', userId),
        where('date', '>=', startDate),
        where('date', '<=', endDate),
        orderBy('date', 'desc')
      )
    }
    
    const querySnapshot = await getDocs(q)
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    })) as SalesData[]
  } catch (error) {
    console.error('Error getting sales data:', error)
    throw error
  }
}

// Supplier Operations
export const addSupplier = async (supplier: Omit<Supplier, 'id' | 'createdAt'>) => {
  try {
    const docRef = await addDoc(collection(db, 'suppliers'), {
      ...supplier,
      createdAt: Timestamp.now()
    })
    return { id: docRef.id, ...supplier }
  } catch (error) {
    console.error('Error adding supplier:', error)
    throw error
  }
}

export const getSuppliers = async (userId: string) => {
  try {
    const q = query(
      collection(db, 'suppliers'),
      where('userId', '==', userId),
      orderBy('name')
    )
    const querySnapshot = await getDocs(q)
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    })) as Supplier[]
  } catch (error) {
    console.error('Error getting suppliers:', error)
    throw error
  }
}

export const updateSupplier = async (supplierId: string, updates: Partial<Supplier>) => {
  try {
    const supplierRef = doc(db, 'suppliers', supplierId)
    await updateDoc(supplierRef, updates)
    return { id: supplierId, ...updates }
  } catch (error) {
    console.error('Error updating supplier:', error)
    throw error
  }
}

export const deleteSupplier = async (supplierId: string) => {
  try {
    await deleteDoc(doc(db, 'suppliers', supplierId))
    return true
  } catch (error) {
    console.error('Error deleting supplier:', error)
    throw error
  }
}

// Inventory Operations
export const addInventoryItem = async (item: Omit<InventoryItem, 'id' | 'lastUpdated'>) => {
  try {
    const docRef = await addDoc(collection(db, 'inventory'), {
      ...item,
      lastUpdated: Timestamp.now()
    })
    return { id: docRef.id, ...item }
  } catch (error) {
    console.error('Error adding inventory item:', error)
    throw error
  }
}

export const getInventoryItems = async (userId: string) => {
  try {
    const q = query(
      collection(db, 'inventory'),
      where('userId', '==', userId),
      orderBy('name')
    )
    const querySnapshot = await getDocs(q)
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    })) as InventoryItem[]
  } catch (error) {
    console.error('Error getting inventory items:', error)
    throw error
  }
}

export const updateInventoryStock = async (itemId: string, newStock: number) => {
  try {
    const itemRef = doc(db, 'inventory', itemId)
    await updateDoc(itemRef, {
      currentStock: newStock,
      lastUpdated: Timestamp.now()
    })
    return true
  } catch (error) {
    console.error('Error updating inventory stock:', error)
    throw error
  }
}

export const updateInventoryItem = async (itemId: string, updates: Partial<InventoryItem>) => {
  try {
    const itemRef = doc(db, 'inventory', itemId)
    await updateDoc(itemRef, {
      ...updates,
      lastUpdated: Timestamp.now()
    })
    return { id: itemId, ...updates }
  } catch (error) {
    console.error('Error updating inventory item:', error)
    throw error
  }
}

export const deleteInventoryItem = async (itemId: string) => {
  try {
    await deleteDoc(doc(db, 'inventory', itemId))
    return true
  } catch (error) {
    console.error('Error deleting inventory item:', error)
    throw error
  }
}

// Menu Items Operations
export const addMenuItem = async (menuItem: Omit<MenuItem, 'id' | 'createdAt'>) => {
  try {
    const docRef = await addDoc(collection(db, 'menuItems'), {
      ...menuItem,
      createdAt: Timestamp.now()
    })
    return { id: docRef.id, ...menuItem }
  } catch (error) {
    console.error('Error adding menu item:', error)
    throw error
  }
}

export const getMenuItems = async (userId: string) => {
  try {
    const q = query(
      collection(db, 'menuItems'),
      where('userId', '==', userId),
      orderBy('name')
    )
    const querySnapshot = await getDocs(q)
    return querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    })) as MenuItem[]
  } catch (error) {
    console.error('Error getting menu items:', error)
    throw error
  }
}

export const updateMenuItem = async (menuItemId: string, updates: Partial<MenuItem>) => {
  try {
    const menuItemRef = doc(db, 'menuItems', menuItemId)
    await updateDoc(menuItemRef, updates)
    return { id: menuItemId, ...updates }
  } catch (error) {
    console.error('Error updating menu item:', error)
    throw error
  }
}

export const deleteMenuItem = async (menuItemId: string) => {
  try {
    await deleteDoc(doc(db, 'menuItems', menuItemId))
    return true
  } catch (error) {
    console.error('Error deleting menu item:', error)
    throw error
  }
} 