#!/usr/bin/env python3
"""
Test script for POS and Supplier Integrations
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "test-token"  # In dev mode, any token works

def test_pos_integrations():
    """Test POS integration endpoints"""
    print("🧪 Testing POS Integrations...")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    # Test 1: Get available POS systems
    print("\n1. Testing GET /api/pos-integrations/systems")
    response = requests.get(f"{BASE_URL}/api/pos-integrations/systems", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {data['total_systems']} POS systems")
        for pos_id, pos_data in data['pos_systems'].items():
            print(f"   - {pos_data['name']} ({pos_id})")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 2: Create a test POS connection
    print("\n2. Testing POST /api/pos-integrations/connect")
    test_connection = {
        "pos_type": "square",
        "name": "Test Square Store",
        "config": {
            "access_token": "test_token_123",
            "store_id": "test_store_456"
        },
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/pos-integrations/connect",
        headers={**headers, "Content-Type": "application/json"},
        json=test_connection
    )
    
    if response.status_code == 200:
        data = response.json()
        connection_id = data['id']
        print(f"✅ Success! Created connection: {connection_id}")
        
        # Test 3: Test the connection
        print("\n3. Testing POST /api/pos-integrations/connections/{id}/test")
        response = requests.post(
            f"{BASE_URL}/api/pos-integrations/connections/{connection_id}/test",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection test result: {data['test_result']['message']}")
        else:
            print(f"❌ Connection test failed: {response.status_code}")
        
        # Test 4: Sync data
        print("\n4. Testing POST /api/pos-integrations/connections/{id}/sync")
        response = requests.post(
            f"{BASE_URL}/api/pos-integrations/connections/{connection_id}/sync?sync_type=all",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sync completed: {data['sync_result']['sales_synced']} sales, {data['sync_result']['inventory_synced']} inventory items")
        else:
            print(f"❌ Sync failed: {response.status_code}")
        
        # Test 5: Get sales data
        print("\n5. Testing GET /api/pos-integrations/connections/{id}/sales")
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        response = requests.get(
            f"{BASE_URL}/api/pos-integrations/connections/{connection_id}/sales?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sales data retrieved: {len(data['sales_data'])} records, total: ${data['total_sales']}")
        else:
            print(f"❌ Sales data failed: {response.status_code}")
        
        # Test 6: Get inventory data
        print("\n6. Testing GET /api/pos-integrations/connections/{id}/inventory")
        response = requests.get(
            f"{BASE_URL}/api/pos-integrations/connections/{connection_id}/inventory",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inventory data retrieved: {len(data['inventory_data'])} items")
        else:
            print(f"❌ Inventory data failed: {response.status_code}")
        
        # Clean up: Delete the test connection
        print("\n7. Cleaning up test connection")
        response = requests.delete(
            f"{BASE_URL}/api/pos-integrations/connections/{connection_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Test connection deleted")
        else:
            print(f"❌ Failed to delete test connection: {response.status_code}")
            
    else:
        print(f"❌ Failed to create connection: {response.status_code} - {response.text}")

def test_supplier_integrations():
    """Test supplier integration endpoints"""
    print("\n🛒 Testing Supplier Integrations...")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    # Test 1: Get available suppliers
    print("\n1. Testing GET /api/supplier-integrations/suppliers")
    response = requests.get(f"{BASE_URL}/api/supplier-integrations/suppliers", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {data['total_suppliers']} suppliers")
        for supplier_id, supplier_data in data['suppliers'].items():
            print(f"   - {supplier_data['name']} ({supplier_id}) - {supplier_data['integration_type']}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    # Test 2: Get pricing for items
    print("\n2. Testing POST /api/supplier-integrations/pricing")
    pricing_request = {
        "supplier_id": "sysco",
        "items": ["coffee beans", "milk", "sugar", "bread"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/supplier-integrations/pricing",
        headers={**headers, "Content-Type": "application/json"},
        json=pricing_request
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Pricing retrieved: {len(data['pricing'])} items")
        for item in data['pricing']:
            print(f"   - {item['itemName']}: ${item['price']} {item['currency']} per {item['unit']}")
    else:
        print(f"❌ Pricing failed: {response.status_code} - {response.text}")
    
    # Test 3: Place an order
    print("\n3. Testing POST /api/supplier-integrations/order")
    order_request = {
        "supplier_id": "sysco",
        "items": [
            {"name": "coffee beans", "quantity": 5, "unit": "kg", "price": 25.00},
            {"name": "milk", "quantity": 10, "unit": "L", "price": 15.00}
        ],
        "deliveryAddress": "123 Main St, City, State 12345",
        "deliveryDate": "2024-01-20",
        "notes": "Test order from integration test"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/supplier-integrations/order",
        headers={**headers, "Content-Type": "application/json"},
        json=order_request
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Order placed successfully! Order ID: {data['orderId']}")
        print(f"   Total amount: ${data['order']['totalAmount']}")
        print(f"   Status: {data['order']['status']}")
    else:
        print(f"❌ Order placement failed: {response.status_code} - {response.text}")

def test_health_check():
    """Test basic API health"""
    print("🏥 Testing API Health...")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API is healthy! Status: {data['status']}, Dev mode: {data['dev_mode']}")
    else:
        print(f"❌ API health check failed: {response.status_code}")

def main():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests")
    print("=" * 50)
    
    try:
        # Test API health first
        test_health_check()
        
        # Test POS integrations
        test_pos_integrations()
        
        # Test supplier integrations
        test_supplier_integrations()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main() 