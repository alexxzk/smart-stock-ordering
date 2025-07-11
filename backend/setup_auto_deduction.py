#!/usr/bin/env python3
"""
Setup script for the Ingredient Auto-Deduction System
Creates sample data for testing the auto-deduction functionality
"""

import os
import sys
import uuid
from datetime import datetime, date
from typing import Dict, List

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.firebase_init import get_firestore_client
from app.models.restaurants import Restaurant, MenuItem, Recipe, Ingredient, Supplier
from app.models.sales_with_deduction import SalesRecord, SaleItem

def create_sample_restaurant() -> str:
    """Create a sample restaurant"""
    db = get_firestore_client()
    
    restaurant_data = {
        "restaurant_id": "restaurant-1",
        "name": "Sample Coffee Shop",
        "address": "123 Main St, City, State",
        "phone": "+1-555-0123",
        "email": "info@samplecoffee.com",
        "owner_id": "owner-123",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    doc_ref = db.collection('restaurants').document('restaurant-1')
    doc_ref.set(restaurant_data)
    
    print(f"✅ Created restaurant: {restaurant_data['name']}")
    return "restaurant-1"

def create_sample_ingredients(restaurant_id: str) -> Dict[str, str]:
    """Create sample ingredients"""
    db = get_firestore_client()
    
    ingredients = [
        {
            "ingredient_id": "ingredient-1",
            "name": "Coffee Beans",
            "unit": "kg",
            "current_stock": 15.5,
            "min_stock_level": 5.0,
            "max_stock_level": 50.0,
            "cost_per_unit": 12.50,
            "supplier_id": "supplier-1",
            "restaurant_id": restaurant_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "ingredient_id": "ingredient-2",
            "name": "Milk",
            "unit": "liters",
            "current_stock": 8.0,
            "min_stock_level": 3.0,
            "max_stock_level": 20.0,
            "cost_per_unit": 2.50,
            "supplier_id": "supplier-2",
            "restaurant_id": restaurant_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "ingredient_id": "ingredient-3",
            "name": "Sugar",
            "unit": "kg",
            "current_stock": 12.0,
            "min_stock_level": 2.0,
            "max_stock_level": 25.0,
            "cost_per_unit": 1.20,
            "supplier_id": "supplier-1",
            "restaurant_id": restaurant_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "ingredient_id": "ingredient-4",
            "name": "Bread",
            "unit": "slices",
            "current_stock": 40,
            "min_stock_level": 10,
            "max_stock_level": 100,
            "cost_per_unit": 0.15,
            "supplier_id": "supplier-3",
            "restaurant_id": restaurant_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "ingredient_id": "ingredient-5",
            "name": "Cheese",
            "unit": "kg",
            "current_stock": 3.2,
            "min_stock_level": 1.0,
            "max_stock_level": 10.0,
            "cost_per_unit": 8.00,
            "supplier_id": "supplier-2",
            "restaurant_id": restaurant_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    ingredient_ids = {}
    batch = db.batch()
    
    for ingredient in ingredients:
        doc_ref = db.collection('ingredients').document(ingredient['ingredient_id'])
        batch.set(doc_ref, ingredient)
        ingredient_ids[ingredient['name']] = ingredient['ingredient_id']
        print(f"✅ Created ingredient: {ingredient['name']}")
    
    batch.commit()
    return ingredient_ids

def create_sample_menu_items(restaurant_id: str) -> Dict[str, str]:
    """Create sample menu items"""
    db = get_firestore_client()
    
    menu_items = [
        {
            "menu_item_id": "menu-item-1",
            "name": "Cappuccino",
            "description": "Classic Italian coffee drink",
            "price": 4.50,
            "category": "Beverages",
            "restaurant_id": restaurant_id,
            "is_available": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "menu_item_id": "menu-item-2",
            "name": "Latte",
            "description": "Smooth espresso with steamed milk",
            "price": 4.00,
            "category": "Beverages",
            "restaurant_id": restaurant_id,
            "is_available": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "menu_item_id": "menu-item-3",
            "name": "Grilled Cheese Sandwich",
            "description": "Classic grilled cheese with tomato soup",
            "price": 8.50,
            "category": "Food",
            "restaurant_id": restaurant_id,
            "is_available": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    menu_item_ids = {}
    batch = db.batch()
    
    for item in menu_items:
        doc_ref = db.collection('menu_items').document(item['menu_item_id'])
        batch.set(doc_ref, item)
        menu_item_ids[item['name']] = item['menu_item_id']
        print(f"✅ Created menu item: {item['name']}")
    
    batch.commit()
    return menu_item_ids

def create_sample_recipes(menu_item_ids: Dict[str, str], ingredient_ids: Dict[str, str], restaurant_id: str) -> None:
    """Create sample recipes linking menu items to ingredients"""
    db = get_firestore_client()
    
    recipes = [
        {
            "recipe_id": "recipe-1",
            "menu_item_id": menu_item_ids["Cappuccino"],
            "name": "Cappuccino Recipe",
            "description": "Traditional cappuccino preparation",
            "ingredients": [
                {
                    "ingredient_id": ingredient_ids["Coffee Beans"],
                    "quantity": 0.02,  # 20g per cup
                    "unit": "kg"
                },
                {
                    "ingredient_id": ingredient_ids["Milk"],
                    "quantity": 0.12,  # 120ml per cup
                    "unit": "liters"
                }
            ],
            "instructions": "1. Grind coffee beans\n2. Brew espresso\n3. Steam milk\n4. Combine in 1:1:1 ratio",
            "prep_time_minutes": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "restaurant_id": restaurant_id
        },
        {
            "recipe_id": "recipe-2",
            "menu_item_id": menu_item_ids["Latte"],
            "name": "Latte Recipe",
            "description": "Smooth latte preparation",
            "ingredients": [
                {
                    "ingredient_id": ingredient_ids["Coffee Beans"],
                    "quantity": 0.02,  # 20g per cup
                    "unit": "kg"
                },
                {
                    "ingredient_id": ingredient_ids["Milk"],
                    "quantity": 0.18,  # 180ml per cup
                    "unit": "liters"
                }
            ],
            "instructions": "1. Grind coffee beans\n2. Brew espresso\n3. Steam milk\n4. Combine with more milk than cappuccino",
            "prep_time_minutes": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "restaurant_id": restaurant_id
        },
        {
            "recipe_id": "recipe-3",
            "menu_item_id": menu_item_ids["Grilled Cheese Sandwich"],
            "name": "Grilled Cheese Recipe",
            "description": "Classic grilled cheese sandwich",
            "ingredients": [
                {
                    "ingredient_id": ingredient_ids["Bread"],
                    "quantity": 2,  # 2 slices per sandwich
                    "unit": "slices"
                },
                {
                    "ingredient_id": ingredient_ids["Cheese"],
                    "quantity": 0.08,  # 80g per sandwich
                    "unit": "kg"
                }
            ],
            "instructions": "1. Butter bread slices\n2. Add cheese between slices\n3. Grill until golden brown",
            "prep_time_minutes": 8,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "restaurant_id": restaurant_id
        }
    ]
    
    batch = db.batch()
    
    for recipe in recipes:
        doc_ref = db.collection('recipes').document(recipe['recipe_id'])
        batch.set(doc_ref, recipe)
        print(f"✅ Created recipe: {recipe['name']}")
    
    batch.commit()

def create_sample_suppliers() -> None:
    """Create sample suppliers"""
    db = get_firestore_client()
    
    suppliers = [
        {
            "supplier_id": "supplier-1",
            "name": "Coffee Bean Co.",
            "contact_person": "John Smith",
            "email": "john@coffeebeanco.com",
            "phone": "+1-555-0101",
            "address": "456 Coffee St, Bean City",
            "specialties": ["Coffee Beans", "Sugar"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "supplier_id": "supplier-2",
            "name": "Dairy Delights",
            "contact_person": "Mary Johnson",
            "email": "mary@dairydelights.com",
            "phone": "+1-555-0102",
            "address": "789 Milk Ave, Dairy Town",
            "specialties": ["Milk", "Cheese"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "supplier_id": "supplier-3",
            "name": "Bakery Supplies",
            "contact_person": "Bob Wilson",
            "email": "bob@bakerysupplies.com",
            "phone": "+1-555-0103",
            "address": "321 Bread Blvd, Bakery City",
            "specialties": ["Bread", "Pastries"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    batch = db.batch()
    
    for supplier in suppliers:
        doc_ref = db.collection('suppliers').document(supplier['supplier_id'])
        batch.set(doc_ref, supplier)
        print(f"✅ Created supplier: {supplier['name']}")
    
    batch.commit()

def create_sample_sales(restaurant_id: str, menu_item_ids: Dict[str, str]) -> None:
    """Create sample sales records for testing"""
    db = get_firestore_client()
    
    # Create a sample sale
    sale_items = [
        {
            "menu_item_id": menu_item_ids["Cappuccino"],
            "menu_item_name": "Cappuccino",
            "quantity": 2,
            "unit_price": 4.50,
            "total_price": 9.00,
            "ingredients_used": {
                "Coffee Beans": 0.04,
                "Milk": 0.24
            }
        },
        {
            "menu_item_id": menu_item_ids["Grilled Cheese Sandwich"],
            "menu_item_name": "Grilled Cheese Sandwich",
            "quantity": 1,
            "unit_price": 8.50,
            "total_price": 8.50,
            "ingredients_used": {
                "Bread": 2,
                "Cheese": 0.08
            }
        }
    ]
    
    sale_record = {
        "sale_id": "sample-sale-1",
        "restaurant_id": restaurant_id,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "items": sale_items,
        "total_sales_amount": 17.50,
        "total_items_sold": 3,
        "ingredients_deducted": {
            "ingredient-1": 0.04,  # Coffee Beans
            "ingredient-2": 0.24,  # Milk
            "ingredient-4": 2,     # Bread
            "ingredient-5": 0.08   # Cheese
        },
        "low_stock_warnings": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    doc_ref = db.collection('sales').document('sample-sale-1')
    doc_ref.set(sale_record)
    print(f"✅ Created sample sale: ${sale_record['total_sales_amount']}")

def main():
    """Main setup function"""
    print("🚀 Setting up Ingredient Auto-Deduction System...")
    
    try:
        # Initialize Firestore
        db = get_firestore_client()
        if not db:
            print("❌ Failed to initialize Firestore")
            return
        
        print("✅ Firestore initialized")
        
        # Create sample data
        restaurant_id = create_sample_restaurant()
        ingredient_ids = create_sample_ingredients(restaurant_id)
        menu_item_ids = create_sample_menu_items(restaurant_id)
        create_sample_recipes(menu_item_ids, ingredient_ids, restaurant_id)
        create_sample_suppliers()
        create_sample_sales(restaurant_id, menu_item_ids)
        
        print("\n🎉 Auto-Deduction System setup completed successfully!")
        print("\n📋 Sample Data Created:")
        print(f"   • Restaurant: Sample Coffee Shop")
        print(f"   • Ingredients: {len(ingredient_ids)} items")
        print(f"   • Menu Items: {len(menu_item_ids)} items")
        print(f"   • Recipes: 3 recipes")
        print(f"   • Suppliers: 3 suppliers")
        print(f"   • Sample Sale: $17.50")
        
        print("\n🔗 Next Steps:")
        print("   1. Start the backend server: python -m uvicorn app.main:app --reload")
        print("   2. Start the frontend: npm run dev")
        print("   3. Navigate to /sales-auto-deduction in the frontend")
        print("   4. Test the auto-deduction functionality")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 