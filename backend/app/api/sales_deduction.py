from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import date, datetime
import logging

from app.models.sales_with_deduction import (
    SalesCreateRequest, SalesRecord, SaleItem, 
    IngredientDeduction, LowStockWarning, 
    IngredientStockUpdate, StockAdjustment,
    IngredientUsageReport, SalesAnalytics
)
from app.services.auto_deduction import AutoDeductionService
from app.firebase_init import get_firestore_client

router = APIRouter(prefix="/api/sales-deduction", tags=["Sales Auto-Deduction"])
security = HTTPBearer()

# Set up logging
logger = logging.getLogger(__name__)

# Initialize auto-deduction service
auto_deduction_service = AutoDeductionService()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase JWT token"""
    try:
        from firebase_admin import auth
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/process-sale", response_model=Dict)
async def process_sale_with_deduction(
    sale_request: SalesCreateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Process a sale and automatically deduct ingredients from stock
    
    This endpoint:
    1. Records the sale
    2. Looks up recipes for each menu item
    3. Calculates ingredient requirements
    4. Deducts ingredients from stock
    5. Triggers low stock warnings if needed
    """
    try:
        # Process the sale with automatic deduction
        sales_record, deductions, low_stock_warnings = await auto_deduction_service.process_sale_with_deduction(
            restaurant_id=sale_request.restaurant_id,
            sale_items=sale_request.items,
            sale_date=sale_request.date,
            notes=sale_request.notes
        )
        
        return {
            "message": "Sale processed successfully with ingredient deduction",
            "sale_id": sales_record.sale_id,
            "total_sales_amount": sales_record.total_sales_amount,
            "total_items_sold": sales_record.total_items_sold,
            "ingredients_deducted": len(deductions),
            "low_stock_warnings": len(low_stock_warnings),
            "deductions": [deduction.dict() for deduction in deductions],
            "warnings": [warning.dict() for warning in low_stock_warnings],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing sale with deduction: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing sale: {str(e)}")

@router.get("/low-stock-warnings/{restaurant_id}", response_model=List[LowStockWarning])
async def get_low_stock_warnings(
    restaurant_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get current low stock warnings for a restaurant"""
    try:
        warnings = await auto_deduction_service.get_low_stock_warnings(restaurant_id)
        return warnings
        
    except Exception as e:
        logger.error(f"Error getting low stock warnings: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting low stock warnings: {str(e)}")

@router.post("/restock-ingredient")
async def restock_ingredient(
    ingredient_id: str,
    quantity: float,
    reason: str = "Restock",
    current_user: Dict = Depends(get_current_user)
):
    """Restock an ingredient and resolve low stock warnings"""
    try:
        await auto_deduction_service.restock_ingredient(ingredient_id, quantity, reason)
        
        return {
            "message": "Ingredient restocked successfully",
            "ingredient_id": ingredient_id,
            "quantity_added": quantity,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error restocking ingredient: {e}")
        raise HTTPException(status_code=500, detail=f"Error restocking ingredient: {str(e)}")

@router.get("/usage-report/{restaurant_id}")
async def get_ingredient_usage_report(
    restaurant_id: str,
    start_date: date,
    end_date: date,
    current_user: Dict = Depends(get_current_user)
):
    """Get ingredient usage report for a date range"""
    try:
        usage_report = await auto_deduction_service.get_ingredient_usage_report(
            restaurant_id, start_date, end_date
        )
        
        return {
            "restaurant_id": restaurant_id,
            "period": f"{start_date} to {end_date}",
            "total_ingredients": len(usage_report),
            "usage_report": usage_report,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting usage report: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting usage report: {str(e)}")

@router.get("/sales/{restaurant_id}", response_model=List[SalesRecord])
async def get_sales_records(
    restaurant_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get sales records with ingredient deduction details"""
    try:
        db = get_firestore_client()
        sales_ref = db.collection('sales').where('restaurant_id', '==', restaurant_id)
        
        # Add date filters if provided
        if start_date:
            sales_ref = sales_ref.where('date', '>=', start_date)
        if end_date:
            sales_ref = sales_ref.where('date', '<=', end_date)
        
        sales_records = []
        for doc in sales_ref.stream():
            sale_data = doc.to_dict()
            sale_data['sale_id'] = doc.id
            sales_records.append(SalesRecord(**sale_data))
        
        return sales_records
        
    except Exception as e:
        logger.error(f"Error getting sales records: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting sales records: {str(e)}")

@router.get("/deductions/{restaurant_id}", response_model=List[IngredientDeduction])
async def get_ingredient_deductions(
    restaurant_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get ingredient deduction records"""
    try:
        db = get_firestore_client()
        deductions_ref = db.collection('ingredient_deductions')
        
        # Note: This would need a more complex query to filter by restaurant_id
        # For now, we'll get all deductions and filter in memory
        deductions = []
        for doc in deductions_ref.stream():
            deduction_data = doc.to_dict()
            deduction_data['ingredient_id'] = doc.id
            
            # Check if this deduction is for the specified restaurant
            # This would require storing restaurant_id in deduction records
            deductions.append(IngredientDeduction(**deduction_data))
        
        return deductions
        
    except Exception as e:
        logger.error(f"Error getting ingredient deductions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting ingredient deductions: {str(e)}")

@router.post("/adjust-stock")
async def adjust_ingredient_stock(
    adjustment: StockAdjustment,
    current_user: Dict = Depends(get_current_user)
):
    """Manually adjust ingredient stock levels"""
    try:
        db = get_firestore_client()
        
        # Get current ingredient
        ingredient_doc = db.collection('ingredients').document(adjustment.ingredient_id).get()
        
        if not ingredient_doc.exists:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        
        ingredient_data = ingredient_doc.to_dict()
        current_stock = ingredient_data.get('current_stock', 0)
        new_stock = current_stock + adjustment.adjustment_amount
        
        # Update ingredient stock
        db.collection('ingredients').document(adjustment.ingredient_id).update({
            'current_stock': new_stock,
            'updated_at': datetime.now()
        })
        
        # Create adjustment record
        adjustment_record = {
            'ingredient_id': adjustment.ingredient_id,
            'adjustment_amount': adjustment.adjustment_amount,
            'reason': adjustment.reason,
            'notes': adjustment.notes,
            'adjustment_timestamp': datetime.now(),
            'previous_stock': current_stock,
            'new_stock': new_stock,
            'user_id': current_user.get('uid')
        }
        
        db.collection('stock_adjustments').add(adjustment_record)
        
        return {
            "message": "Stock adjusted successfully",
            "ingredient_id": adjustment.ingredient_id,
            "adjustment_amount": adjustment.adjustment_amount,
            "previous_stock": current_stock,
            "new_stock": new_stock,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting stock: {e}")
        raise HTTPException(status_code=500, detail=f"Error adjusting stock: {str(e)}")

@router.get("/analytics/{restaurant_id}")
async def get_sales_analytics(
    restaurant_id: str,
    start_date: date,
    end_date: date,
    current_user: Dict = Depends(get_current_user)
):
    """Get comprehensive sales analytics with ingredient tracking"""
    try:
        db = get_firestore_client()
        
        # Get sales records for the period
        sales_docs = db.collection('sales').where('restaurant_id', '==', restaurant_id).stream()
        
        sales_data = []
        total_sales = 0
        total_items_sold = 0
        item_sales = {}
        category_sales = {}
        
        for doc in sales_docs:
            sale_data = doc.to_dict()
            sale_date = sale_data['date']
            
            if start_date <= sale_date <= end_date:
                sales_data.append(sale_data)
                total_sales += sale_data.get('total_sales_amount', 0)
                total_items_sold += sale_data.get('total_items_sold', 0)
                
                # Track item sales
                for item in sale_data.get('items', []):
                    item_name = item.get('menu_item_name', 'Unknown')
                    item_sales[item_name] = item_sales.get(item_name, 0) + item.get('quantity', 0)
                    
                    # Track category sales (you'd need to add category to menu items)
                    category = item.get('category', 'Uncategorized')
                    category_sales[category] = category_sales.get(category, 0) + item.get('total_price', 0)
        
        # Get ingredient usage report
        usage_report = await auto_deduction_service.get_ingredient_usage_report(
            restaurant_id, start_date, end_date
        )
        
        # Get low stock warnings
        low_stock_warnings = await auto_deduction_service.get_low_stock_warnings(restaurant_id)
        
        # Calculate average order value
        average_order_value = total_sales / len(sales_data) if sales_data else 0
        
        # Get top selling items
        top_selling_items = sorted(item_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analytics = SalesAnalytics(
            period_start=start_date,
            period_end=end_date,
            total_sales=total_sales,
            total_items_sold=total_items_sold,
            top_selling_items=[{"item": item, "quantity": qty} for item, qty in top_selling_items],
            ingredient_usage_summary=usage_report,
            low_stock_alerts=low_stock_warnings,
            revenue_by_category=category_sales,
            average_order_value=average_order_value,
            peak_sales_hours=[12, 13, 18, 19]  # Placeholder - would need time data
        )
        
        return analytics.dict()
        
    except Exception as e:
        logger.error(f"Error getting sales analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting sales analytics: {str(e)}")

@router.get("/dashboard/{restaurant_id}")
async def get_sales_dashboard(
    restaurant_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get dashboard summary for sales and ingredient tracking"""
    try:
        # Get today's date
        today = date.today()
        
        # Get today's sales
        db = get_firestore_client()
        today_sales = db.collection('sales').where('restaurant_id', '==', restaurant_id).where('date', '==', today).stream()
        
        today_total = 0
        today_items = 0
        today_deductions = 0
        
        for doc in today_sales:
            sale_data = doc.to_dict()
            today_total += sale_data.get('total_sales_amount', 0)
            today_items += sale_data.get('total_items_sold', 0)
            today_deductions += len(sale_data.get('ingredients_deducted', {}))
        
        # Get low stock warnings
        low_stock_warnings = await auto_deduction_service.get_low_stock_warnings(restaurant_id)
        
        # Get ingredient count
        ingredient_docs = db.collection('ingredients').where('restaurant_id', '==', restaurant_id).stream()
        total_ingredients = len(list(ingredient_docs))
        
        return {
            "restaurant_id": restaurant_id,
            "date": today.isoformat(),
            "today_sales": {
                "total_amount": today_total,
                "total_items": today_items,
                "ingredients_deducted": today_deductions
            },
            "inventory": {
                "total_ingredients": total_ingredients,
                "low_stock_warnings": len(low_stock_warnings),
                "critical_warnings": len([w for w in low_stock_warnings if w.urgency == "critical"])
            },
            "alerts": {
                "low_stock_items": [w.ingredient_name for w in low_stock_warnings if w.urgency in ["high", "critical"]]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting sales dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting sales dashboard: {str(e)}") 