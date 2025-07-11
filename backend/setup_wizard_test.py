#!/usr/bin/env python3
"""
Setup Wizard Test Script
Tests the Setup Wizard functionality by creating a sample restaurant setup
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.setup_wizard import SetupWizardService
from app.models.setup_wizard import (
    RestaurantProfile, MenuItemUpload, IngredientUpload, 
    SupplierUpload, InitialStockUpload
)

async def test_setup_wizard():
    """Test the Setup Wizard functionality"""
    print("🧪 Testing Setup Wizard...")
    
    # Initialize service
    service = SetupWizardService()
    
    try:
        # Step 1: Create session
        print("\n1️⃣ Creating setup session...")
        session = await service.create_session("test-admin-user")
        print(f"✅ Session created: {session.session_id}")
        
        # Step 2: Restaurant Profile
        print("\n2️⃣ Adding restaurant profile...")
        restaurant_profile = RestaurantProfile(
            name="Test Coffee Shop",
            address="123 Coffee Street, Test City, TC 12345",
            phone="+1-555-0123",
            email="info@testcoffeeshop.com",
            owner_email="owner@testcoffeeshop.com",
            owner_name="John Coffee",
            cuisine_type="Coffee Shop",
            business_hours={
                "monday": "7:00 AM - 6:00 PM",
                "tuesday": "7:00 AM - 6:00 PM",
                "wednesday": "7:00 AM - 6:00 PM",
                "thursday": "7:00 AM - 6:00 PM",
                "friday": "7:00 AM - 8:00 PM",
                "saturday": "8:00 AM - 8:00 PM",
                "sunday": "8:00 AM - 5:00 PM"
            },
            tax_rate=0.08,
            currency="USD"
        )
        
        validation = await service.save_restaurant_profile(session.session_id, restaurant_profile)
        print(f"✅ Restaurant profile saved: {validation.is_valid}")
        
        # Step 3: Menu Items
        print("\n3️⃣ Adding menu items...")
        menu_items = [
            MenuItemUpload(
                name="Cappuccino",
                description="Classic Italian coffee drink with steamed milk",
                price=4.50,
                category="Beverages",
                is_available=True,
                ingredients=[
                    {"name": "Coffee Beans", "quantity": 0.02, "unit": "kg"},
                    {"name": "Milk", "quantity": 0.12, "unit": "liters"},
                    {"name": "Sugar", "quantity": 0.01, "unit": "kg"}
                ]
            ),
            MenuItemUpload(
                name="Grilled Cheese Sandwich",
                description="Classic grilled cheese with tomato soup",
                price=8.50,
                category="Food",
                is_available=True,
                ingredients=[
                    {"name": "Bread", "quantity": 0.15, "unit": "kg"},
                    {"name": "Cheese", "quantity": 0.08, "unit": "kg"},
                    {"name": "Butter", "quantity": 0.02, "unit": "kg"}
                ]
            )
        ]
        
        validation = await service.save_menu_items(session.session_id, menu_items)
        print(f"✅ Menu items saved: {validation.is_valid}")
        
        # Step 4: Ingredients
        print("\n4️⃣ Adding ingredients...")
        ingredients = [
            IngredientUpload(
                name="Coffee Beans",
                unit="kg",
                current_stock=15.5,
                min_stock_level=5.0,
                max_stock_level=50.0,
                cost_per_unit=12.50,
                supplier_name="Coffee Bean Co."
            ),
            IngredientUpload(
                name="Milk",
                unit="liters",
                current_stock=8.0,
                min_stock_level=3.0,
                max_stock_level=20.0,
                cost_per_unit=2.50,
                supplier_name="Dairy Delights"
            ),
            IngredientUpload(
                name="Bread",
                unit="kg",
                current_stock=5.0,
                min_stock_level=2.0,
                max_stock_level=15.0,
                cost_per_unit=3.00,
                supplier_name="Bakery Fresh"
            ),
            IngredientUpload(
                name="Cheese",
                unit="kg",
                current_stock=3.5,
                min_stock_level=1.5,
                max_stock_level=10.0,
                cost_per_unit=8.00,
                supplier_name="Dairy Delights"
            )
        ]
        
        validation = await service.save_ingredients(session.session_id, ingredients)
        print(f"✅ Ingredients saved: {validation.is_valid}")
        
        # Step 5: Suppliers
        print("\n5️⃣ Adding suppliers...")
        suppliers = [
            SupplierUpload(
                name="Coffee Bean Co.",
                contact_person="John Smith",
                email="john@coffeebeanco.com",
                phone="+1-555-0101",
                address="456 Coffee Street, Bean City, BC 12345",
                specialties=["Coffee Beans", "Sugar", "Syrups"],
                payment_terms="Net 30",
                delivery_schedule="Weekly on Mondays"
            ),
            SupplierUpload(
                name="Dairy Delights",
                contact_person="Mary Johnson",
                email="mary@dairydelights.com",
                phone="+1-555-0102",
                address="789 Milk Avenue, Dairy Town, DT 67890",
                specialties=["Milk", "Cheese", "Butter"],
                payment_terms="Net 15",
                delivery_schedule="Daily"
            ),
            SupplierUpload(
                name="Bakery Fresh",
                contact_person="Bob Baker",
                email="bob@bakeryfresh.com",
                phone="+1-555-0103",
                address="321 Bread Boulevard, Bakery City, BC 11111",
                specialties=["Bread", "Pastries", "Cakes"],
                payment_terms="Net 7",
                delivery_schedule="Daily at 6 AM"
            )
        ]
        
        validation = await service.save_suppliers(session.session_id, suppliers)
        print(f"✅ Suppliers saved: {validation.is_valid}")
        
        # Step 6: Initial Stock
        print("\n6️⃣ Setting initial stock...")
        initial_stock = [
            InitialStockUpload(
                ingredient_id="coffee-beans-id",  # This would be the actual ID
                quantity=15.5,
                cost=193.75,
                supplier_id="coffee-bean-co-id",
                notes="Initial coffee bean stock"
            ),
            InitialStockUpload(
                ingredient_id="milk-id",
                quantity=8.0,
                cost=20.00,
                supplier_id="dairy-delights-id",
                notes="Initial milk stock"
            )
        ]
        
        validation = await service.save_initial_stock(session.session_id, initial_stock)
        print(f"✅ Initial stock saved: {validation.is_valid}")
        
        # Step 7: Complete Setup
        print("\n7️⃣ Completing setup...")
        completion = await service.complete_setup(session.session_id)
        print(f"✅ Setup completed successfully!")
        print(f"   Restaurant ID: {completion.restaurant_id}")
        print(f"   Owner User ID: {completion.owner_user_id}")
        print(f"   Summary: {completion.summary}")
        
        # Test progress
        print("\n8️⃣ Testing progress...")
        progress = await service.get_progress(session.session_id)
        print(f"✅ Progress: {progress.progress_percentage}% complete")
        print(f"   Current step: {progress.current_step}")
        print(f"   Can proceed: {progress.can_proceed}")
        
        print("\n🎉 Setup Wizard test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during setup wizard test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_setup_wizard()) 