from typing import Dict, List, Optional
from datetime import date, datetime
import json

class InventoryManager:
    """Convert sales forecasts into ingredient requirements"""
    
    def __init__(self):
        # Sample menu items and their ingredient requirements
        # In a real app, this would come from a database
        self.menu_items = {
            "coffee": {
                "coffee_beans": 0.025,  # kg per cup
                "milk": 0.1,  # liters per cup
                "sugar": 0.01,  # kg per cup
                "cup": 1,  # units per cup
                "lid": 1  # units per cup
            },
            "latte": {
                "coffee_beans": 0.025,
                "milk": 0.25,
                "sugar": 0.01,
                "cup": 1,
                "lid": 1
            },
            "cappuccino": {
                "coffee_beans": 0.025,
                "milk": 0.2,
                "sugar": 0.01,
                "cup": 1,
                "lid": 1
            },
            "sandwich": {
                "bread": 2,  # slices per sandwich
                "cheese": 0.05,  # kg per sandwich
                "ham": 0.08,  # kg per sandwich
                "lettuce": 0.02,  # kg per sandwich
                "tomato": 0.03,  # kg per sandwich
                "mayo": 0.02,  # kg per sandwich
                "wrapping_paper": 1  # units per sandwich
            },
            "croissant": {
                "flour": 0.08,  # kg per croissant
                "butter": 0.04,  # kg per croissant
                "sugar": 0.02,  # kg per croissant
                "yeast": 0.005,  # kg per croissant
                "egg": 0.5,  # units per croissant
                "wrapping_paper": 1
            },
            "muffin": {
                "flour": 0.06,  # kg per muffin
                "sugar": 0.03,  # kg per muffin
                "egg": 0.5,  # units per muffin
                "milk": 0.05,  # liters per muffin
                "butter": 0.02,  # kg per muffin
                "wrapping_paper": 1
            }
        }
        
        # Supplier information with pack sizes and costs
        self.suppliers = {
            "coffee_beans": {
                "supplier": "Coffee Supply Co",
                "pack_size": 10,  # kg
                "cost_per_pack": 120.0,
                "min_order": 1,
                "lead_time_days": 3
            },
            "milk": {
                "supplier": "Dairy Fresh",
                "pack_size": 4,  # liters
                "cost_per_pack": 8.0,
                "min_order": 1,
                "lead_time_days": 1
            },
            "sugar": {
                "supplier": "Sweet Supplies",
                "pack_size": 25,  # kg
                "cost_per_pack": 45.0,
                "min_order": 1,
                "lead_time_days": 2
            },
            "bread": {
                "supplier": "Bakery Direct",
                "pack_size": 20,  # slices
                "cost_per_pack": 3.5,
                "min_order": 1,
                "lead_time_days": 1
            },
            "cheese": {
                "supplier": "Dairy Fresh",
                "pack_size": 5,  # kg
                "cost_per_pack": 35.0,
                "min_order": 1,
                "lead_time_days": 2
            },
            "ham": {
                "supplier": "Meat Market",
                "pack_size": 2,  # kg
                "cost_per_pack": 18.0,
                "min_order": 1,
                "lead_time_days": 2
            },
            "lettuce": {
                "supplier": "Fresh Produce",
                "pack_size": 1,  # kg
                "cost_per_pack": 4.0,
                "min_order": 1,
                "lead_time_days": 1
            },
            "tomato": {
                "supplier": "Fresh Produce",
                "pack_size": 2,  # kg
                "cost_per_pack": 6.0,
                "min_order": 1,
                "lead_time_days": 1
            },
            "mayo": {
                "supplier": "Condiment Co",
                "pack_size": 2,  # kg
                "cost_per_pack": 12.0,
                "min_order": 1,
                "lead_time_days": 3
            },
            "flour": {
                "supplier": "Bakery Direct",
                "pack_size": 25,  # kg
                "cost_per_pack": 30.0,
                "min_order": 1,
                "lead_time_days": 2
            },
            "butter": {
                "supplier": "Dairy Fresh",
                "pack_size": 5,  # kg
                "cost_per_pack": 40.0,
                "min_order": 1,
                "lead_time_days": 2
            },
            "yeast": {
                "supplier": "Bakery Direct",
                "pack_size": 1,  # kg
                "cost_per_pack": 15.0,
                "min_order": 1,
                "lead_time_days": 2
            },
            "egg": {
                "supplier": "Dairy Fresh",
                "pack_size": 30,  # units
                "cost_per_pack": 12.0,
                "min_order": 1,
                "lead_time_days": 1
            },
            "cup": {
                "supplier": "Packaging Plus",
                "pack_size": 100,  # units
                "cost_per_pack": 25.0,
                "min_order": 1,
                "lead_time_days": 3
            },
            "lid": {
                "supplier": "Packaging Plus",
                "pack_size": 100,  # units
                "cost_per_pack": 20.0,
                "min_order": 1,
                "lead_time_days": 3
            },
            "wrapping_paper": {
                "supplier": "Packaging Plus",
                "pack_size": 500,  # units
                "cost_per_pack": 15.0,
                "min_order": 1,
                "lead_time_days": 3
            }
        }
    
    def calculate_ingredient_requirements(self, forecast_data: Dict, current_stock: Dict[str, float] = None) -> List[Dict]:
        """Calculate ingredient requirements based on sales forecast"""
        if current_stock is None:
            current_stock = {}
        
        # Aggregate menu items from forecast
        total_menu_items = {}
        for i, date_str in enumerate(forecast_data['dates']):
            # Estimate menu items based on predicted sales
            # This is a simplified approach - in reality, you'd have actual menu item breakdowns
            daily_sales = forecast_data['predicted_sales'][i]
            
            # Distribute sales across menu items (simplified)
            coffee_count = int(daily_sales * 0.4 / 4.5)  # 40% of sales, $4.5 avg price
            latte_count = int(daily_sales * 0.3 / 5.5)   # 30% of sales, $5.5 avg price
            sandwich_count = int(daily_sales * 0.2 / 8.0) # 20% of sales, $8.0 avg price
            pastry_count = int(daily_sales * 0.1 / 3.5)   # 10% of sales, $3.5 avg price
            
            total_menu_items['coffee'] = total_menu_items.get('coffee', 0) + coffee_count
            total_menu_items['latte'] = total_menu_items.get('latte', 0) + latte_count
            total_menu_items['sandwich'] = total_menu_items.get('sandwich', 0) + sandwich_count
            total_menu_items['croissant'] = total_menu_items.get('croissant', 0) + pastry_count
        
        # Calculate ingredient requirements
        ingredient_requirements = {}
        for menu_item, quantity in total_menu_items.items():
            if menu_item in self.menu_items:
                for ingredient, amount_per_item in self.menu_items[menu_item].items():
                    total_amount = quantity * amount_per_item
                    ingredient_requirements[ingredient] = ingredient_requirements.get(ingredient, 0) + total_amount
        
        # Generate supplier orders
        supplier_orders = []
        for ingredient, required_amount in ingredient_requirements.items():
            if ingredient in self.suppliers:
                supplier_info = self.suppliers[ingredient]
                current_stock_amount = current_stock.get(ingredient, 0)
                
                # Calculate how much we need to order
                net_requirement = max(0, required_amount - current_stock_amount)
                
                if net_requirement > 0:
                    # Calculate packs needed
                    pack_size = supplier_info['pack_size']
                    packs_needed = int((net_requirement + pack_size - 1) / pack_size)  # Ceiling division
                    
                    # Ensure minimum order
                    packs_needed = max(packs_needed, supplier_info['min_order'])
                    
                    total_cost = packs_needed * supplier_info['cost_per_pack']
                    
                    # Determine urgency based on lead time and current stock
                    days_until_stockout = current_stock_amount / (required_amount / len(forecast_data['dates']))
                    if days_until_stockout < supplier_info['lead_time_days']:
                        urgency = "critical"
                    elif days_until_stockout < supplier_info['lead_time_days'] + 3:
                        urgency = "high"
                    elif days_until_stockout < supplier_info['lead_time_days'] + 7:
                        urgency = "medium"
                    else:
                        urgency = "low"
                    
                    supplier_orders.append({
                        "ingredient_name": ingredient,
                        "current_stock": current_stock_amount,
                        "required_amount": required_amount,
                        "pack_size": pack_size,
                        "packs_needed": packs_needed,
                        "total_cost": total_cost,
                        "supplier": supplier_info['supplier'],
                        "urgency": urgency,
                        "lead_time_days": supplier_info['lead_time_days']
                    })
        
        return supplier_orders
    
    def generate_supplier_orders(self, ingredient_requirements: List[Dict]) -> List[Dict]:
        """Group ingredient requirements by supplier"""
        supplier_groups = {}
        
        for req in ingredient_requirements:
            supplier = req['supplier']
            if supplier not in supplier_groups:
                supplier_groups[supplier] = {
                    "supplier_name": supplier,
                    "order_items": [],
                    "total_cost": 0,
                    "delivery_date": None,
                    "order_status": "pending",
                    "created_at": datetime.now(),
                    "notes": ""
                }
            
            supplier_groups[supplier]["order_items"].append({
                "ingredient": req['ingredient_name'],
                "packs_needed": req['packs_needed'],
                "pack_size": req['pack_size'],
                "cost_per_pack": req['total_cost'] / req['packs_needed'],
                "total_cost": req['total_cost'],
                "urgency": req['urgency']
            })
            
            supplier_groups[supplier]["total_cost"] += req['total_cost']
        
        return list(supplier_groups.values())
    
    def update_menu_items(self, menu_items: Dict):
        """Update menu items configuration"""
        self.menu_items.update(menu_items)
    
    def update_suppliers(self, suppliers: Dict):
        """Update supplier configuration"""
        self.suppliers.update(suppliers) 