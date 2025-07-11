#!/usr/bin/env python3
"""
Setup script to create a super admin user in Firebase
This script should be run once to set up the initial super admin user.
"""

import firebase_admin
from firebase_admin import firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

def setup_super_admin():
    """Set up a super admin user in Firebase"""
    
    # Initialize Firebase
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    
    db = firestore.client()
    
    # Super admin user details
    super_admin_uid = "super-admin-123"  # You can change this
    super_admin_email = "admin@ordix.ai"  # You can change this
    
    # Create super admin user document
    super_admin_data = {
        "uid": super_admin_uid,
        "email": super_admin_email,
        "role": "super_admin",
        "name": "Super Administrator",
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "permissions": [
            "create_restaurants",
            "manage_restaurants", 
            "manage_menu_items",
            "manage_recipes",
            "manage_ingredients",
            "manage_suppliers",
            "manage_initial_stock",
            "view_all_data"
        ],
        "is_active": True
    }
    
    try:
        # Create the super admin user document
        db.collection('users').document(super_admin_uid).set(super_admin_data)
        print(f"✅ Super admin user created successfully!")
        print(f"   UID: {super_admin_uid}")
        print(f"   Email: {super_admin_email}")
        print(f"   Role: super_admin")
        print("\n📝 Note: You'll need to create this user in Firebase Authentication manually")
        print("   or use the Firebase Admin SDK to create the auth user.")
        
        # Create a sample restaurant for testing
        sample_restaurant = {
            "restaurant_id": "sample-restaurant-123",
            "name": "Sample Restaurant",
            "owner_user_id": super_admin_uid,
            "address": "123 Main St, City, State 12345",
            "phone": "+1-555-123-4567",
            "email": "info@samplerestaurant.com",
            "cuisine_type": "American",
            "status": "active",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "settings": {
                "timezone": "America/New_York",
                "currency": "USD",
                "language": "en"
            }
        }
        
        db.collection('restaurants').document(sample_restaurant["restaurant_id"]).set(sample_restaurant)
        print(f"\n✅ Sample restaurant created successfully!")
        print(f"   Restaurant ID: {sample_restaurant['restaurant_id']}")
        print(f"   Name: {sample_restaurant['name']}")
        
        print("\n🎉 Setup complete! You can now test the Super Admin functionality.")
        print("   Make sure to create the Firebase Auth user with the same UID.")
        
    except Exception as e:
        print(f"❌ Error setting up super admin: {e}")
        return False
    
    return True

def create_sample_data():
    """Create sample data for testing"""
    
    db = firestore.client()
    restaurant_id = "sample-restaurant-123"
    
    # Sample ingredients
    ingredients = [
        {
            "ingredient_id": "ing-001",
            "restaurant_id": restaurant_id,
            "name": "Tomatoes",
            "unit": "kg",
            "cost_per_unit": 2.50,
            "current_stock": 10.0,
            "min_stock_level": 5.0,
            "category": "Vegetables",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        },
        {
            "ingredient_id": "ing-002", 
            "restaurant_id": restaurant_id,
            "name": "Ground Beef",
            "unit": "kg",
            "cost_per_unit": 8.00,
            "current_stock": 15.0,
            "min_stock_level": 8.0,
            "category": "Meat",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        },
        {
            "ingredient_id": "ing-003",
            "restaurant_id": restaurant_id,
            "name": "Onions",
            "unit": "kg", 
            "cost_per_unit": 1.50,
            "current_stock": 8.0,
            "min_stock_level": 4.0,
            "category": "Vegetables",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
    ]
    
    # Sample suppliers
    suppliers = [
        {
            "supplier_id": "sup-001",
            "restaurant_id": restaurant_id,
            "name": "Fresh Foods Co.",
            "contact_person": "John Smith",
            "email": "john@freshfoods.com",
            "phone": "+1-555-123-4567",
            "address": "456 Supplier St, City, State 12345",
            "website": "https://freshfoods.com",
            "payment_terms": "Net 30",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        },
        {
            "supplier_id": "sup-002",
            "restaurant_id": restaurant_id,
            "name": "Quality Meats Inc.",
            "contact_person": "Sarah Johnson",
            "email": "sarah@qualitymeats.com",
            "phone": "+1-555-987-6543",
            "address": "789 Meat Ave, City, State 12345",
            "website": "https://qualitymeats.com",
            "payment_terms": "Net 15",
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
    ]
    
    # Sample menu items
    menu_items = [
        {
            "item_id": "menu-001",
            "restaurant_id": restaurant_id,
            "name": "Classic Burger",
            "description": "Juicy beef burger with fresh vegetables",
            "category": "Main Course",
            "price": 12.99,
            "cost": 6.50,
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        },
        {
            "item_id": "menu-002",
            "restaurant_id": restaurant_id,
            "name": "Caesar Salad",
            "description": "Fresh romaine lettuce with caesar dressing",
            "category": "Appetizer",
            "price": 8.99,
            "cost": 3.50,
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
    ]
    
    try:
        # Create ingredients
        for ingredient in ingredients:
            db.collection('ingredients').document(ingredient["ingredient_id"]).set(ingredient)
        
        # Create suppliers
        for supplier in suppliers:
            db.collection('suppliers').document(supplier["supplier_id"]).set(supplier)
        
        # Create menu items
        for menu_item in menu_items:
            db.collection('menu_items').document(menu_item["item_id"]).set(menu_item)
        
        print("✅ Sample data created successfully!")
        print(f"   - {len(ingredients)} ingredients")
        print(f"   - {len(suppliers)} suppliers") 
        print(f"   - {len(menu_items)} menu items")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Setting up Super Admin functionality...")
    
    # Set up super admin user
    if setup_super_admin():
        # Create sample data
        print("\n📊 Creating sample data...")
        create_sample_data()
        
        print("\n✨ Setup complete! You can now:")
        print("   1. Access the Super Admin panel at /super-admin")
        print("   2. Create and manage restaurants")
        print("   3. Add menu items, recipes, and ingredients")
        print("   4. Manage suppliers and initial stock")
    else:
        print("❌ Setup failed. Please check your Firebase configuration.") 