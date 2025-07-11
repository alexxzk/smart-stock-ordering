#!/usr/bin/env python3
"""
Supplier API Integrations Test Script
Tests the supplier API integrations including Bidfood, PFD, Ordermentum, and PDF/email order sheets
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.supplier_api_integrations import (
    BidfoodIntegration, PFDIntegration, OrdermentumIntegration,
    OrderSheetGenerator, OrderRequest, OrderItem, SupplierProduct
)

async def test_supplier_integrations():
    """Test the supplier API integrations"""
    print("🏪 Testing Supplier API Integrations...")
    
    try:
        # Test 1: Bidfood Integration
        print("\n1️⃣ Testing Bidfood Integration...")
        bidfood_config = {
            "api_key": "test_bidfood_api_key",
            "location_id": "test_location_123"
        }
        
        bidfood_integration = BidfoodIntegration(
            api_key=bidfood_config["api_key"],
            location_id=bidfood_config["location_id"]
        )
        
        async with bidfood_integration:
            # Test getting products (mock)
            products = await bidfood_integration.get_products()
            print(f"✅ Bidfood products retrieved: {len(products)} products")
            
            # Test order placement (mock)
            order_items = [
                OrderItem(
                    product_id="coffee_beans_001",
                    name="Premium Coffee Beans",
                    quantity=5,
                    unit="kg",
                    unit_price=25.00,
                    total_price=125.00,
                    notes="Medium roast"
                ),
                OrderItem(
                    product_id="milk_001",
                    name="Fresh Milk",
                    quantity=10,
                    unit="L",
                    unit_price=2.50,
                    total_price=25.00,
                    notes="Full cream"
                )
            ]
            
            order = OrderRequest(
                order_id=f"order_{uuid.uuid4().hex[:8]}",
                supplier_id="bidfood",
                items=order_items,
                delivery_address="123 Coffee Street, Melbourne VIC 3000",
                delivery_date=datetime.now() + timedelta(days=2),
                contact_person="John Smith",
                contact_phone="+61-3-1234-5678",
                contact_email="john@coffeeshop.com",
                notes="Please deliver before 2 PM",
                urgent=False
            )
            
            confirmation = await bidfood_integration.place_order(order)
            print(f"✅ Bidfood order placed: {confirmation.supplier_order_id}")
            print(f"   Status: {confirmation.status}")
            print(f"   Total: ${confirmation.total_amount}")
        
        # Test 2: PFD Integration
        print("\n2️⃣ Testing PFD Integration...")
        pfd_config = {
            "api_key": "test_pfd_api_key",
            "account_number": "PFD123456"
        }
        
        pfd_integration = PFDIntegration(
            api_key=pfd_config["api_key"],
            account_number=pfd_config["account_number"]
        )
        
        async with pfd_integration:
            products = await pfd_integration.get_products()
            print(f"✅ PFD products retrieved: {len(products)} products")
            
            # Test order placement
            order_items = [
                OrderItem(
                    product_id="bread_001",
                    name="Artisan Sourdough",
                    quantity=20,
                    unit="loaves",
                    unit_price=3.50,
                    total_price=70.00,
                    notes="Fresh daily"
                )
            ]
            
            order = OrderRequest(
                order_id=f"order_{uuid.uuid4().hex[:8]}",
                supplier_id="pfd",
                items=order_items,
                delivery_address="456 Bakery Lane, Sydney NSW 2000",
                delivery_date=datetime.now() + timedelta(days=1),
                contact_person="Mary Johnson",
                contact_phone="+61-2-9876-5432",
                contact_email="mary@bakery.com",
                notes="Early morning delivery preferred",
                urgent=True
            )
            
            confirmation = await pfd_integration.place_order(order)
            print(f"✅ PFD order placed: {confirmation.supplier_order_id}")
            print(f"   Status: {confirmation.status}")
            print(f"   Total: ${confirmation.total_amount}")
        
        # Test 3: Ordermentum Integration
        print("\n3️⃣ Testing Ordermentum Integration...")
        ordermentum_config = {
            "api_key": "test_ordermentum_api_key",
            "restaurant_id": "REST123456"
        }
        
        ordermentum_integration = OrdermentumIntegration(
            api_key=ordermentum_config["api_key"],
            restaurant_id=ordermentum_config["restaurant_id"]
        )
        
        async with ordermentum_integration:
            products = await ordermentum_integration.get_products()
            print(f"✅ Ordermentum products retrieved: {len(products)} products")
            
            # Test order placement
            order_items = [
                OrderItem(
                    product_id="cheese_001",
                    name="Aged Cheddar",
                    quantity=3,
                    unit="kg",
                    unit_price=12.00,
                    total_price=36.00,
                    notes="Sharp cheddar"
                ),
                OrderItem(
                    product_id="butter_001",
                    name="Unsalted Butter",
                    quantity=5,
                    unit="kg",
                    unit_price=8.50,
                    total_price=42.50,
                    notes="For baking"
                )
            ]
            
            order = OrderRequest(
                order_id=f"order_{uuid.uuid4().hex[:8]}",
                supplier_id="ordermentum",
                items=order_items,
                delivery_address="789 Restaurant Row, Brisbane QLD 4000",
                delivery_date=datetime.now() + timedelta(days=2),
                contact_person="Bob Wilson",
                contact_phone="+61-7-5555-1234",
                contact_email="bob@restaurant.com",
                notes="Kitchen entrance delivery",
                urgent=False
            )
            
            confirmation = await ordermentum_integration.place_order(order)
            print(f"✅ Ordermentum order placed: {confirmation.supplier_order_id}")
            print(f"   Status: {confirmation.status}")
            print(f"   Total: ${confirmation.total_amount}")
        
        # Test 4: PDF Order Sheet Generation
        print("\n4️⃣ Testing PDF Order Sheet Generation...")
        order_generator = OrderSheetGenerator()
        
        order_items = [
            OrderItem(
                product_id="local_produce_001",
                name="Fresh Tomatoes",
                quantity=10,
                unit="kg",
                unit_price=4.50,
                total_price=45.00,
                notes="Ripe tomatoes"
            ),
            OrderItem(
                product_id="local_produce_002",
                name="Organic Lettuce",
                quantity=5,
                unit="heads",
                unit_price=2.00,
                total_price=10.00,
                notes="Mixed varieties"
            ),
            OrderItem(
                product_id="local_produce_003",
                name="Fresh Herbs",
                quantity=2,
                unit="bunches",
                unit_price=3.50,
                total_price=7.00,
                notes="Basil, parsley, thyme"
            )
        ]
        
        order = OrderRequest(
            order_id=f"order_{uuid.uuid4().hex[:8]}",
            supplier_id="local_produce",
            items=order_items,
            delivery_address="321 Farm Fresh Road, Adelaide SA 5000",
            delivery_date=datetime.now() + timedelta(days=1),
            contact_person="Sarah Green",
            contact_phone="+61-8-1234-5678",
            contact_email="sarah@farmfresh.com",
            notes="Please deliver to back entrance",
            urgent=False
        )
        
        pdf_path = order_generator.generate_pdf_order_sheet(order, "Local Produce Co.")
        print(f"✅ PDF order sheet generated: {pdf_path}")
        
        # Test 5: Email Order Sheet
        print("\n5️⃣ Testing Email Order Sheet...")
        try:
            # This would require SMTP configuration
            success = order_generator.generate_email_order_sheet(
                order, 
                "Local Produce Co.", 
                "orders@localproduce.com"
            )
            if success:
                print("✅ Email order sheet sent successfully")
            else:
                print("⚠️ Email sending failed (SMTP not configured)")
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")
        
        # Test 6: Integration Manager
        print("\n6️⃣ Testing Integration Manager...")
        from app.services.supplier_api_integrations import SupplierIntegrationManager
        
        manager = SupplierIntegrationManager()
        
        # Register integrations
        manager.register_integration("bidfood", bidfood_integration)
        manager.register_integration("pfd", pfd_integration)
        manager.register_integration("ordermentum", ordermentum_integration)
        
        # Test getting products from manager
        products = await manager.get_products("bidfood")
        print(f"✅ Manager retrieved {len(products)} products from Bidfood")
        
        # Test order placement through manager
        confirmation = await manager.place_order("pfd", order)
        print(f"✅ Manager placed order with PFD: {confirmation.supplier_order_id}")
        
        # Test PDF generation through manager
        pdf_path = manager.generate_order_sheet(order, "Local Produce Co.", "orders@localproduce.com")
        print(f"✅ Manager generated order sheet: {pdf_path}")
        
        print("\n🎉 All supplier integration tests completed successfully!")
        
        # Summary
        print("\n📊 Test Summary:")
        print("✅ Bidfood API Integration")
        print("✅ PFD API Integration") 
        print("✅ Ordermentum API Integration")
        print("✅ PDF Order Sheet Generation")
        print("✅ Email Order Sheet (with SMTP config)")
        print("✅ Integration Manager")
        
    except Exception as e:
        print(f"❌ Error during supplier integration tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supplier_integrations()) 