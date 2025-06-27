import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getInventoryItems, getSuppliers } from '../services/firebaseService'

export default function TestPage() {
  const { currentUser } = useAuth()
  const [testResults, setTestResults] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const runTests = async () => {
    setLoading(true)
    setTestResults([])
    
    try {
      // Test 1: Check authentication
      addResult('🔍 Testing authentication...')
      if (currentUser) {
        addResult(`✅ User authenticated: ${currentUser.email}`)
      } else {
        addResult('❌ No user authenticated')
        return
      }

      // Test 2: Test Firebase connection
      addResult('🔍 Testing Firebase connection...')
      try {
        const inventory = await getInventoryItems(currentUser.uid)
        addResult(`✅ Firebase connected. Inventory items: ${inventory.length}`)
      } catch (error) {
        addResult(`❌ Firebase error: ${error}`)
        return
      }

      // Test 3: Test suppliers
      addResult('🔍 Testing suppliers...')
      try {
        const suppliers = await getSuppliers(currentUser.uid)
        addResult(`✅ Suppliers loaded: ${suppliers.length}`)
      } catch (error) {
        addResult(`❌ Suppliers error: ${error}`)
      }

      addResult('🎉 All tests completed!')
      
    } catch (error) {
      addResult(`❌ Test failed: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🔧 Debug Test Page</h1>
      
      <div className="mb-6">
        <button 
          onClick={runTests}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Running Tests...' : 'Run Debug Tests'}
        </button>
      </div>

      <div className="bg-gray-100 p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-4">Test Results:</h2>
        <div className="space-y-2">
          {testResults.length === 0 ? (
            <p className="text-gray-500">Click "Run Debug Tests" to start</p>
          ) : (
            testResults.map((result, index) => (
              <div key={index} className="text-sm font-mono">
                {result}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold mb-2">Current Status:</h3>
        <ul className="text-sm space-y-1">
          <li>• User: {currentUser ? currentUser.email : 'Not logged in'}</li>
          <li>• Backend: http://localhost:8000</li>
          <li>• Frontend: http://localhost:5174</li>
        </ul>
      </div>
    </div>
  )
} 