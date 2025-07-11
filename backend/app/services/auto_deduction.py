from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import logging
from firebase_admin import firestore
import uuid
import collections.abc
import os

from app.models.sales_with_deduction import (
    SalesRecord, SaleItem, IngredientDeduction, 
    LowStockWarning, IngredientStockUpdate
)
from app.models.restaurants import Recipe, Ingredient

logger = logging.getLogger(__name__)

# Utility to recursively convert date/datetime to ISO strings
def serialize_dates(obj):
    if isinstance(obj, dict):
        return {k: serialize_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dates(v) for v in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

class AutoDeductionService:
    """Service for automatic ingredient deduction and stock management"""
    
    def __init__(self):
        # Check if we're in dev mode
        if os.getenv("DEV_MODE", "false").lower() == "true":
            self.db = None
            logger.info("AutoDeductionService initialized in dev mode")
        else:
            self.db = firestore.client()
    
    async def process_sale_with_deduction(
        self, 
        restaurant_id: str,
        sale_items: List[SaleItem],
        sale_date: date,
        notes: Optional[str] = None
    ) -> Tuple[SalesRecord, List[IngredientDeduction], List[LowStockWarning]]:
        """
        Process a sale and automatically deduct ingredients from stock
        
        Args:
            restaurant_id: ID of the restaurant
            sale_items: List of items sold
            sale_date: Date of the sale
            notes: Optional notes for the sale
            
        Returns:
            Tuple of (sales_record, deductions, low_stock_warnings)
        """
        # Return mock data in dev mode
        if self.db is None:
            logger.info("Returning mock data in dev mode")
            sale_id = str(uuid.uuid4())
            now = datetime.now()
            mock_sales_record = SalesRecord(
                sale_id=sale_id,
                restaurant_id=restaurant_id,
                date=sale_date,
                timestamp=now,
                items=sale_items,
                total_sales_amount=sum(item.total_price for item in sale_items),
                total_items_sold=sum(item.quantity for item in sale_items),
                ingredients_deducted={},
                low_stock_warnings=[],
                created_at=now,
                updated_at=now
            )
            return mock_sales_record, [], []
        
        try:
            # Calculate total sales
            total_sales_amount = sum(item.total_price for item in sale_items)
            total_items_sold = sum(item.quantity for item in sale_items)
            
            # Get recipes for each menu item
            deductions = []
            low_stock_warnings = []
            total_ingredients_deducted = {}
            
            for sale_item in sale_items:
                # Get recipe for this menu item
                recipe = await self._get_recipe_for_menu_item(sale_item.menu_item_id, restaurant_id)
                
                if recipe:
                    # Calculate ingredients needed for this sale
                    item_deductions = await self._calculate_ingredient_deductions(
                        recipe, sale_item.quantity, restaurant_id
                    )
                    
                    # Update sale item with ingredients used
                    sale_item.ingredients_used = {
                        deduction.ingredient_name: deduction.quantity_deducted 
                        for deduction in item_deductions
                    }
                    
                    # Accumulate total deductions
                    for deduction in item_deductions:
                        ingredient_id = deduction.ingredient_id
                        if ingredient_id in total_ingredients_deducted:
                            total_ingredients_deducted[ingredient_id] += deduction.quantity_deducted
                        else:
                            total_ingredients_deducted[ingredient_id] = deduction.quantity_deducted
                    
                    deductions.extend(item_deductions)
                    
                    # Check for low stock warnings
                    item_warnings = await self._check_low_stock_warnings(item_deductions)
                    low_stock_warnings.extend(item_warnings)
            
            # Create sales record
            sale_id = str(uuid.uuid4())
            now = datetime.now()
            
            sales_record = SalesRecord(
                sale_id=sale_id,
                restaurant_id=restaurant_id,
                date=sale_date,
                timestamp=now,
                items=sale_items,
                total_sales_amount=total_sales_amount,
                total_items_sold=total_items_sold,
                ingredients_deducted=total_ingredients_deducted,
                low_stock_warnings=[warning.ingredient_name for warning in low_stock_warnings],
                created_at=now,
                updated_at=now
            )
            
            # Save sales record
            await self._save_sales_record(sales_record)
            
            # Save deductions
            await self._save_deductions(deductions)
            
            # Save low stock warnings
            await self._save_low_stock_warnings(low_stock_warnings)
            
            # Update ingredient stock levels
            await self._update_ingredient_stock(deductions)
            
            logger.info(f"Processed sale {sale_id} with {len(deductions)} ingredient deductions")
            
            return sales_record, deductions, low_stock_warnings
            
        except Exception as e:
            logger.error(f"Error processing sale with deduction: {e}")
            raise
    
    async def _get_recipe_for_menu_item(self, menu_item_id: str, restaurant_id: str) -> Optional[Recipe]:
        """Get recipe for a menu item"""
        if self.db is None:
            return None
            
        try:
            # Get recipe from Firestore
            recipe_docs = self.db.collection('recipes').where('menu_item_id', '==', menu_item_id).stream()
            
            for doc in recipe_docs:
                recipe_data = doc.to_dict()
                recipe_data['recipe_id'] = doc.id
                return Recipe(**recipe_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting recipe for menu item {menu_item_id}: {e}")
            return None
    
    async def _calculate_ingredient_deductions(
        self, 
        recipe: Recipe, 
        quantity_sold: int, 
        restaurant_id: str
    ) -> List[IngredientDeduction]:
        """Calculate ingredient deductions for a recipe"""
        deductions = []
        now = datetime.now()
        
        try:
            for recipe_ingredient in recipe.ingredients:
                # Get current ingredient stock
                ingredient = await self._get_ingredient(recipe_ingredient.ingredient_id, restaurant_id)
                
                if ingredient:
                    # Calculate total quantity needed
                    total_quantity_needed = recipe_ingredient.quantity * quantity_sold
                    
                    # Check if we have enough stock
                    if ingredient.current_stock >= total_quantity_needed:
                        # Calculate new stock
                        new_stock = ingredient.current_stock - total_quantity_needed
                        is_low_stock = new_stock <= ingredient.min_stock_level
                        
                        deduction = IngredientDeduction(
                            ingredient_id=ingredient.ingredient_id,
                            ingredient_name=ingredient.name,
                            quantity_deducted=total_quantity_needed,
                            unit=ingredient.unit,
                            previous_stock=ingredient.current_stock,
                            new_stock=new_stock,
                            min_stock_level=ingredient.min_stock_level,
                            is_low_stock=is_low_stock,
                            deduction_timestamp=now
                        )
                        
                        deductions.append(deduction)
                    else:
                        # Not enough stock - log warning but still deduct what we have
                        logger.warning(f"Insufficient stock for {ingredient.name}. Need {total_quantity_needed}, have {ingredient.current_stock}")
                        
                        deduction = IngredientDeduction(
                            ingredient_id=ingredient.ingredient_id,
                            ingredient_name=ingredient.name,
                            quantity_deducted=ingredient.current_stock,
                            unit=ingredient.unit,
                            previous_stock=ingredient.current_stock,
                            new_stock=0,
                            min_stock_level=ingredient.min_stock_level,
                            is_low_stock=True,
                            deduction_timestamp=now
                        )
                        
                        deductions.append(deduction)
        
        except Exception as e:
            logger.error(f"Error calculating ingredient deductions: {e}")
        
        return deductions
    
    async def _get_ingredient(self, ingredient_id: str, restaurant_id: str) -> Optional[Ingredient]:
        """Get ingredient from Firestore"""
        if self.db is None:
            return None
            
        try:
            doc = self.db.collection('ingredients').document(ingredient_id).get()
            
            if doc.exists:
                ingredient_data = doc.to_dict()
                ingredient_data['ingredient_id'] = doc.id
                return Ingredient(**ingredient_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting ingredient {ingredient_id}: {e}")
            return None
    
    async def _check_low_stock_warnings(self, deductions: List[IngredientDeduction]) -> List[LowStockWarning]:
        """Check for low stock warnings after deductions"""
        warnings = []
        now = datetime.now()
        
        for deduction in deductions:
            if deduction.is_low_stock:
                # Determine urgency level
                stock_ratio = deduction.new_stock / deduction.min_stock_level
                
                if stock_ratio <= 0.25:
                    urgency = "critical"
                elif stock_ratio <= 0.5:
                    urgency = "high"
                elif stock_ratio <= 0.75:
                    urgency = "medium"
                else:
                    urgency = "low"
                
                warning = LowStockWarning(
                    ingredient_id=deduction.ingredient_id,
                    ingredient_name=deduction.ingredient_name,
                    current_stock=deduction.new_stock,
                    min_stock_level=deduction.min_stock_level,
                    unit=deduction.unit,
                    urgency=urgency,
                    warning_timestamp=now,
                    is_resolved=False
                )
                
                warnings.append(warning)
        
        return warnings
    
    async def _save_sales_record(self, sales_record: SalesRecord):
        """Save sales record to Firestore"""
        if self.db is None:
            logger.info("Skipping save_sales_record in dev mode")
            return
            
        try:
            data = serialize_dates(sales_record.dict())
            self.db.collection('sales').document(sales_record.sale_id).set(data)
        except Exception as e:
            logger.error(f"Error saving sales record: {e}")
            raise
    
    async def _save_deductions(self, deductions: List[IngredientDeduction]):
        """Save ingredient deductions to Firestore"""
        if self.db is None:
            logger.info("Skipping save_deductions in dev mode")
            return
            
        try:
            batch = self.db.batch()
            
            for deduction in deductions:
                doc_ref = self.db.collection('ingredient_deductions').document()
                data = serialize_dates(deduction.dict())
                batch.set(doc_ref, data)
            
            batch.commit()
            
        except Exception as e:
            logger.error(f"Error saving deductions: {e}")
            raise
    
    async def _save_low_stock_warnings(self, warnings: List[LowStockWarning]):
        """Save low stock warnings to Firestore"""
        if self.db is None:
            logger.info("Skipping save_low_stock_warnings in dev mode")
            return
            
        try:
            batch = self.db.batch()
            
            for warning in warnings:
                doc_ref = self.db.collection('low_stock_warnings').document()
                data = serialize_dates(warning.dict())
                batch.set(doc_ref, data)
            
            batch.commit()
            
        except Exception as e:
            logger.error(f"Error saving low stock warnings: {e}")
            raise
    
    async def _update_ingredient_stock(self, deductions: List[IngredientDeduction]):
        """Update ingredient stock levels in Firestore"""
        if self.db is None:
            logger.info("Skipping update_ingredient_stock in dev mode")
            return
            
        try:
            batch = self.db.batch()
            
            for deduction in deductions:
                doc_ref = self.db.collection('ingredients').document(deduction.ingredient_id)
                batch.update(doc_ref, {
                    'current_stock': deduction.new_stock,
                    'updated_at': datetime.now()
                })
            
            batch.commit()
            
        except Exception as e:
            logger.error(f"Error updating ingredient stock: {e}")
            raise
    
    async def get_low_stock_warnings(self, restaurant_id: str) -> List[LowStockWarning]:
        """Get current low stock warnings for a restaurant"""
        if self.db is None:
            logger.info("Returning empty low stock warnings in dev mode")
            return []
            
        try:
            warnings = []
            
            # Get all ingredients for the restaurant
            ingredient_docs = self.db.collection('ingredients').where('restaurant_id', '==', restaurant_id).stream()
            
            for doc in ingredient_docs:
                ingredient_data = doc.to_dict()
                ingredient_data['ingredient_id'] = doc.id
                ingredient = Ingredient(**ingredient_data)
                
                if ingredient.current_stock <= ingredient.min_stock_level:
                    # Determine urgency
                    stock_ratio = ingredient.current_stock / ingredient.min_stock_level
                    
                    if stock_ratio <= 0.25:
                        urgency = "critical"
                    elif stock_ratio <= 0.5:
                        urgency = "high"
                    elif stock_ratio <= 0.75:
                        urgency = "medium"
                    else:
                        urgency = "low"
                    
                    warning = LowStockWarning(
                        ingredient_id=ingredient.ingredient_id,
                        ingredient_name=ingredient.name,
                        current_stock=ingredient.current_stock,
                        min_stock_level=ingredient.min_stock_level,
                        unit=ingredient.unit,
                        urgency=urgency,
                        warning_timestamp=datetime.now(),
                        is_resolved=False
                    )
                    
                    warnings.append(warning)
            
            return warnings
            
        except Exception as e:
            logger.error(f"Error getting low stock warnings: {e}")
            return []
    
    async def restock_ingredient(self, ingredient_id: str, quantity: float, reason: str = "Restock"):
        """Restock an ingredient"""
        if self.db is None:
            logger.info("Skipping restock_ingredient in dev mode")
            return
            
        try:
            # Get current ingredient
            ingredient = await self._get_ingredient(ingredient_id, "")
            
            if ingredient:
                new_stock = ingredient.current_stock + quantity
                
                # Update ingredient stock
                self.db.collection('ingredients').document(ingredient_id).update({
                    'current_stock': new_stock,
                    'updated_at': datetime.now()
                })
                
                # Create stock adjustment record
                adjustment = {
                    'ingredient_id': ingredient_id,
                    'adjustment_amount': quantity,
                    'reason': reason,
                    'adjustment_timestamp': datetime.now(),
                    'previous_stock': ingredient.current_stock,
                    'new_stock': new_stock
                }
                
                self.db.collection('stock_adjustments').add(adjustment)
                
                logger.info(f"Restocked {ingredient.name} with {quantity} {ingredient.unit}")
                
        except Exception as e:
            logger.error(f"Error restocking ingredient: {e}")
            raise
    
    async def get_ingredient_usage_report(
        self, 
        restaurant_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict]:
        """Get ingredient usage report for a date range"""
        if self.db is None:
            logger.info("Returning empty ingredient usage report in dev mode")
            return []
            
        try:
            # Get all sales records for the date range
            sales_docs = self.db.collection('sales').where('restaurant_id', '==', restaurant_id).stream()
            
            usage_summary = {}
            
            for doc in sales_docs:
                sale_data = doc.to_dict()
                # Convert string date to date object for comparison
                sale_date_str = sale_data['date']
                if isinstance(sale_date_str, str):
                    sale_date = datetime.fromisoformat(sale_date_str).date()
                else:
                    sale_date = sale_date_str
                
                if start_date <= sale_date <= end_date:
                    ingredients_deducted = sale_data.get('ingredients_deducted', {})
                    
                    for ingredient_id, quantity in ingredients_deducted.items():
                        if ingredient_id in usage_summary:
                            usage_summary[ingredient_id] += quantity
                        else:
                            usage_summary[ingredient_id] = quantity
            
            # Get ingredient details
            reports = []
            for ingredient_id, total_used in usage_summary.items():
                ingredient = await self._get_ingredient(ingredient_id, restaurant_id)
                
                if ingredient:
                    days_in_period = (end_date - start_date).days + 1
                    average_daily_usage = total_used / days_in_period
                    
                    days_until_stockout = None
                    if average_daily_usage > 0:
                        days_until_stockout = ingredient.current_stock / average_daily_usage
                    
                    report = {
                        'ingredient_id': ingredient_id,
                        'ingredient_name': ingredient.name,
                        'total_used': total_used,
                        'unit': ingredient.unit,
                        'usage_period': f"{start_date} to {end_date}",
                        'average_daily_usage': average_daily_usage,
                        'current_stock': ingredient.current_stock,
                        'min_stock_level': ingredient.min_stock_level,
                        'days_until_stockout': days_until_stockout
                    }
                    
                    reports.append(report)
            
            return reports
            
        except Exception as e:
            logger.error(f"Error getting ingredient usage report: {e}")
            return [] 