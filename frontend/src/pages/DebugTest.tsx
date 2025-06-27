import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { db } from '../config/firebase';
import { collection, getDocs, addDoc, deleteDoc, doc } from 'firebase/firestore';

const DebugTest = () => {
  const { currentUser } = useAuth();
  const [testResults, setTestResults] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const log = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setTestResults(prev => [...prev, `${timestamp}: ${message}`]);
  };

  const clearLog = () => {
    setTestResults([]);
  };

  const runTests = async () => {
    setIsLoading(true);
    clearLog();
    
    try {
      // Test authentication
      log('🔍 Testing authentication...');
      if (currentUser) {
        log(`✅ User authenticated: ${currentUser.email}`);
      } else {
        log('❌ No user authenticated');
        return;
      }

      // Test Firebase connection
      log('🔍 Testing Firebase connection...');
      const inventoryRef = collection(db, 'inventory');
      const inventorySnapshot = await getDocs(inventoryRef);
      log(`✅ Firebase connected. Inventory items: ${inventorySnapshot.size}`);

      // Test suppliers
      log('🔍 Testing suppliers...');
      const suppliersRef = collection(db, 'suppliers');
      const suppliersSnapshot = await getDocs(suppliersRef);
      log(`✅ Suppliers loaded: ${suppliersSnapshot.size}`);

      log('🎉 All tests completed!');
    } catch (error) {
      log(`❌ Error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const createSampleData = async () => {
    setIsLoading(true);
    clearLog();
    
    try {
      log('🔧 Creating sample data...');

      // Create sample inventory items
      const inventoryRef = collection(db, 'inventory');
      const sampleInventory = [
        {
          name: 'Coffee Beans',
          category: 'Beverages',
          current_stock: 50,
          unit: 'kg',
          min_stock: 10,
          cost_per_unit: 15.99,
          supplier: 'Coffee Supplier Co.',
          last_updated: new Date().toISOString()
        },
        {
          name: 'Milk',
          category: 'Dairy',
          current_stock: 20,
          unit: 'L',
          min_stock: 5,
          cost_per_unit: 2.50,
          supplier: 'Dairy Farm Ltd.',
          last_updated: new Date().toISOString()
        },
        {
          name: 'Sugar',
          category: 'Pantry',
          current_stock: 15,
          unit: 'kg',
          min_stock: 3,
          cost_per_unit: 1.20,
          supplier: 'Sweet Supplies Inc.',
          last_updated: new Date().toISOString()
        }
      ];

      for (const item of sampleInventory) {
        await addDoc(inventoryRef, item);
      }
      log(`✅ Created ${sampleInventory.length} inventory items`);

      // Create sample suppliers
      const suppliersRef = collection(db, 'suppliers');
      const sampleSuppliers = [
        {
          name: 'Coffee Supplier Co.',
          contact_person: 'John Smith',
          email: 'john@coffeesupplier.com',
          phone: '+1-555-0101',
          address: '123 Coffee St, Bean City, BC 12345',
          payment_terms: 'Net 30',
          delivery_schedule: 'Weekly',
          minimum_order: 100,
          rating: 4.5,
          notes: 'Reliable coffee supplier with good quality beans'
        },
        {
          name: 'Dairy Farm Ltd.',
          contact_person: 'Sarah Johnson',
          email: 'sarah@dairyfarm.com',
          phone: '+1-555-0102',
          address: '456 Milk Ave, Dairy Town, DT 67890',
          payment_terms: 'Net 15',
          delivery_schedule: 'Daily',
          minimum_order: 50,
          rating: 4.8,
          notes: 'Fresh dairy products delivered daily'
        },
        {
          name: 'Sweet Supplies Inc.',
          contact_person: 'Mike Brown',
          email: 'mike@sweetsupplies.com',
          phone: '+1-555-0103',
          address: '789 Sugar Rd, Sweet City, SC 11111',
          payment_terms: 'Net 30',
          delivery_schedule: 'Bi-weekly',
          minimum_order: 75,
          rating: 4.2,
          notes: 'Bulk sugar and sweetener supplier'
        }
      ];

      for (const supplier of sampleSuppliers) {
        await addDoc(suppliersRef, supplier);
      }
      log(`✅ Created ${sampleSuppliers.length} suppliers`);

      log('🎉 Sample data created successfully!');
    } catch (error) {
      log(`❌ Error creating sample data: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const clearAllData = async () => {
    setIsLoading(true);
    clearLog();
    
    try {
      log('🗑️ Clearing all data...');

      // Clear inventory
      const inventoryRef = collection(db, 'inventory');
      const inventorySnapshot = await getDocs(inventoryRef);
      for (const doc of inventorySnapshot.docs) {
        await deleteDoc(doc.ref);
      }
      log(`✅ Cleared ${inventorySnapshot.size} inventory items`);

      // Clear suppliers
      const suppliersRef = collection(db, 'suppliers');
      const suppliersSnapshot = await getDocs(suppliersRef);
      for (const doc of suppliersSnapshot.docs) {
        await deleteDoc(doc.ref);
      }
      log(`✅ Cleared ${suppliersSnapshot.size} suppliers`);

      log('🎉 All data cleared!');
    } catch (error) {
      log(`❌ Error clearing data: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Debug & Test Page</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <button
              onClick={runTests}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              {isLoading ? 'Running...' : 'Run Tests'}
            </button>
            
            <button
              onClick={createSampleData}
              disabled={isLoading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              {isLoading ? 'Creating...' : 'Create Sample Data'}
            </button>
            
            <button
              onClick={clearAllData}
              disabled={isLoading}
              className="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
            >
              {isLoading ? 'Clearing...' : 'Clear All Data'}
            </button>
          </div>

          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-96 overflow-y-auto">
            {testResults.length === 0 ? (
              <div className="text-gray-500">Click "Run Tests" to start testing...</div>
            ) : (
              testResults.map((result, index) => (
                <div key={index} className="mb-1">{result}</div>
              ))
            )}
          </div>

          <div className="mt-4 text-sm text-gray-600">
            <p><strong>Current User:</strong> {currentUser?.email || 'Not authenticated'}</p>
            <p><strong>User ID:</strong> {currentUser?.uid || 'N/A'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DebugTest; 