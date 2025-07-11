from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import logging
import os
from pathlib import Path

from app.services.supplier_api_integrations import (
    SupplierIntegrationManager, OrderRequest, OrderItem, SupplierProduct,
    create_supplier_integration, OrderSheetGenerator
)
from app.firebase_init import get_firestore_client

router = APIRouter(prefix="/api/supplier-api-integrations", tags=["Supplier API Integrations"])
security = HTTPBearer()

logger = logging.getLogger(__name__)

# Initialize supplier integration manager
supplier_manager = SupplierIntegrationManager()

# Pydantic models
class SupplierConfig(BaseModel):
    supplier_id: str
    api_key: str
    location_id: Optional[str] = None
    account_number: Optional[str] = None
    restaurant_id: Optional[str] = None

class ProductRequest(BaseModel):
    supplier_id: str
    category: Optional[str] = None

class OrderItemRequest(BaseModel):
    product_id: str
    name: str
    quantity: int
    unit: str
    unit_price: float
    notes: str = ""

class OrderRequestModel(BaseModel):
    supplier_id: str
    items: List[OrderItemRequest]
    delivery_address: str
    delivery_date: datetime
    contact_person: str
    contact_phone: str
    contact_email: str
    notes: str = ""
    urgent: bool = False

class OrderSheetRequest(BaseModel):
    supplier_name: str
    supplier_email: Optional[str] = None
    items: List[OrderItemRequest]
    delivery_address: str
    delivery_date: datetime
    contact_person: str
    contact_phone: str
    contact_email: str
    notes: str = ""
    urgent: bool = False

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

@router.post("/configure")
async def configure_supplier_integration(
    config: SupplierConfig,
    current_user: Dict = Depends(get_current_user)
):
    """Configure a supplier API integration"""
    try:
        # Create integration based on supplier ID
        integration = create_supplier_integration(
            supplier_id=config.supplier_id,
            config=config.dict()
        )
        
        if not integration:
            raise HTTPException(status_code=400, detail=f"Unsupported supplier: {config.supplier_id}")
        
        # Register integration with manager
        supplier_manager.register_integration(config.supplier_id, integration)
        
        # Save configuration to database
        db = get_firestore_client()
        if db:
            config_data = {
                **config.dict(),
                "user_id": current_user.get("uid"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }
            
            db.collection("supplier_api_configs").document(config.supplier_id).set(config_data)
        
        return {
            "message": f"Integration configured successfully for {config.supplier_id}",
            "supplier_id": config.supplier_id,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error configuring supplier integration: {e}")
        raise HTTPException(status_code=500, detail=f"Error configuring integration: {str(e)}")

@router.get("/products/{supplier_id}")
async def get_supplier_products(
    supplier_id: str,
    category: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get products from a supplier"""
    try:
        products = await supplier_manager.get_products(supplier_id, category)
        
        return {
            "supplier_id": supplier_id,
            "category": category,
            "products": [
                {
                    "product_id": p.product_id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "unit": p.unit,
                    "category": p.category,
                    "in_stock": p.in_stock,
                    "min_order_qty": p.min_order_qty,
                    "lead_time_days": p.lead_time_days,
                    "last_updated": p.last_updated.isoformat()
                }
                for p in products
            ],
            "total_products": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error getting supplier products: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting products: {str(e)}")

@router.post("/order")
async def place_supplier_order(
    order_request: OrderRequestModel,
    current_user: Dict = Depends(get_current_user)
):
    """Place an order with a supplier via API"""
    try:
        # Convert to internal order format
        order_items = [
            OrderItem(
                product_id=item.product_id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
                notes=item.notes
            )
            for item in order_request.items
        ]
        
        order = OrderRequest(
            order_id=f"order_{uuid.uuid4().hex[:8]}",
            supplier_id=order_request.supplier_id,
            items=order_items,
            delivery_address=order_request.delivery_address,
            delivery_date=order_request.delivery_date,
            contact_person=order_request.contact_person,
            contact_phone=order_request.contact_phone,
            contact_email=order_request.contact_email,
            notes=order_request.notes,
            urgent=order_request.urgent
        )
        
        # Place order
        confirmation = await supplier_manager.place_order(order_request.supplier_id, order)
        
        # Save order to database
        db = get_firestore_client()
        if db:
            order_data = {
                "order_id": order.order_id,
                "supplier_id": order.supplier_id,
                "supplier_order_id": confirmation.supplier_order_id,
                "items": [
                    {
                        "product_id": item.product_id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price,
                        "notes": item.notes
                    }
                    for item in order.items
                ],
                "delivery_address": order.delivery_address,
                "delivery_date": order.delivery_date.isoformat(),
                "contact_person": order.contact_person,
                "contact_phone": order.contact_phone,
                "contact_email": order.contact_email,
                "notes": order.notes,
                "urgent": order.urgent,
                "status": confirmation.status,
                "estimated_delivery": confirmation.estimated_delivery.isoformat(),
                "total_amount": confirmation.total_amount,
                "confirmation_message": confirmation.confirmation_message,
                "user_id": current_user.get("uid"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            db.collection("supplier_orders").document(order.order_id).set(order_data)
        
        return {
            "success": True,
            "order_id": order.order_id,
            "supplier_order_id": confirmation.supplier_order_id,
            "status": confirmation.status,
            "estimated_delivery": confirmation.estimated_delivery.isoformat(),
            "total_amount": confirmation.total_amount,
            "message": confirmation.confirmation_message
        }
        
    except Exception as e:
        logger.error(f"Error placing supplier order: {e}")
        raise HTTPException(status_code=500, detail=f"Error placing order: {str(e)}")

@router.post("/order-sheet/pdf")
async def generate_pdf_order_sheet(
    order_request: OrderSheetRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Generate PDF order sheet for suppliers without APIs"""
    try:
        # Convert to internal order format
        order_items = [
            OrderItem(
                product_id=item.product_id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
                notes=item.notes
            )
            for item in order_request.items
        ]
        
        order = OrderRequest(
            order_id=f"order_{uuid.uuid4().hex[:8]}",
            supplier_id="manual",
            items=order_items,
            delivery_address=order_request.delivery_address,
            delivery_date=order_request.delivery_date,
            contact_person=order_request.contact_person,
            contact_phone=order_request.contact_phone,
            contact_email=order_request.contact_email,
            notes=order_request.notes,
            urgent=order_request.urgent
        )
        
        # Generate PDF
        order_generator = OrderSheetGenerator()
        pdf_path = order_generator.generate_pdf_order_sheet(order, order_request.supplier_name)
        
        # Save order to database
        db = get_firestore_client()
        if db:
            order_data = {
                "order_id": order.order_id,
                "supplier_name": order_request.supplier_name,
                "supplier_email": order_request.supplier_email,
                "items": [
                    {
                        "product_id": item.product_id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price,
                        "notes": item.notes
                    }
                    for item in order.items
                ],
                "delivery_address": order.delivery_address,
                "delivery_date": order.delivery_date.isoformat(),
                "contact_person": order.contact_person,
                "contact_phone": order.contact_phone,
                "contact_email": order.contact_email,
                "notes": order.notes,
                "urgent": order.urgent,
                "pdf_path": pdf_path,
                "user_id": current_user.get("uid"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            db.collection("manual_orders").document(order.order_id).set(order_data)
        
        return {
            "success": True,
            "order_id": order.order_id,
            "pdf_path": pdf_path,
            "message": "PDF order sheet generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating PDF order sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating order sheet: {str(e)}")

@router.post("/order-sheet/email")
async def send_email_order_sheet(
    order_request: OrderSheetRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Generate and send email order sheet"""
    try:
        if not order_request.supplier_email:
            raise HTTPException(status_code=400, detail="Supplier email is required")
        
        # Convert to internal order format
        order_items = [
            OrderItem(
                product_id=item.product_id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
                notes=item.notes
            )
            for item in order_request.items
        ]
        
        order = OrderRequest(
            order_id=f"order_{uuid.uuid4().hex[:8]}",
            supplier_id="email",
            items=order_items,
            delivery_address=order_request.delivery_address,
            delivery_date=order_request.delivery_date,
            contact_person=order_request.contact_person,
            contact_phone=order_request.contact_phone,
            contact_email=order_request.contact_email,
            notes=order_request.notes,
            urgent=order_request.urgent
        )
        
        # Send email in background
        order_generator = OrderSheetGenerator()
        background_tasks.add_task(
            order_generator.generate_email_order_sheet,
            order,
            order_request.supplier_name,
            order_request.supplier_email
        )
        
        # Save order to database
        db = get_firestore_client()
        if db:
            order_data = {
                "order_id": order.order_id,
                "supplier_name": order_request.supplier_name,
                "supplier_email": order_request.supplier_email,
                "items": [
                    {
                        "product_id": item.product_id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "unit": item.unit,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price,
                        "notes": item.notes
                    }
                    for item in order.items
                ],
                "delivery_address": order.delivery_address,
                "delivery_date": order.delivery_date.isoformat(),
                "contact_person": order.contact_person,
                "contact_phone": order.contact_phone,
                "contact_email": order.contact_email,
                "notes": order.notes,
                "urgent": order.urgent,
                "email_sent": True,
                "user_id": current_user.get("uid"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            db.collection("email_orders").document(order.order_id).set(order_data)
        
        return {
            "success": True,
            "order_id": order.order_id,
            "supplier_email": order_request.supplier_email,
            "message": "Email order sheet sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending email order sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending order sheet: {str(e)}")

@router.get("/download/{order_id}")
async def download_order_sheet(
    order_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Download a generated order sheet PDF"""
    try:
        db = get_firestore_client()
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get order data
        doc = db.collection("manual_orders").document(order_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_data = doc.to_dict()
        pdf_path = order_data.get("pdf_path")
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            path=pdf_path,
            filename=f"order_{order_id}.pdf",
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading order sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.get("/orders")
async def get_supplier_orders(
    supplier_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get supplier orders"""
    try:
        db = get_firestore_client()
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get orders from different collections
        orders = []
        
        # API orders
        api_orders_ref = db.collection("supplier_orders")
        if supplier_id:
            api_orders_ref = api_orders_ref.where("supplier_id", "==", supplier_id)
        if status:
            api_orders_ref = api_orders_ref.where("status", "==", status)
        
        for doc in api_orders_ref.stream():
            order_data = doc.to_dict()
            order_data["id"] = doc.id
            order_data["type"] = "api"
            orders.append(order_data)
        
        # Manual orders
        manual_orders_ref = db.collection("manual_orders")
        for doc in manual_orders_ref.stream():
            order_data = doc.to_dict()
            order_data["id"] = doc.id
            order_data["type"] = "manual"
            orders.append(order_data)
        
        # Email orders
        email_orders_ref = db.collection("email_orders")
        for doc in email_orders_ref.stream():
            order_data = doc.to_dict()
            order_data["id"] = doc.id
            order_data["type"] = "email"
            orders.append(order_data)
        
        # Sort by creation date
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "orders": orders,
            "total_orders": len(orders)
        }
        
    except Exception as e:
        logger.error(f"Error getting supplier orders: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting orders: {str(e)}")

@router.get("/suppliers")
async def get_available_suppliers():
    """Get list of available suppliers for API integration"""
    suppliers = {
        "bidfood": {
            "id": "bidfood",
            "name": "Bidfood",
            "description": "Leading foodservice distributor in Australia",
            "api_url": "https://api.bidfood.com.au/v1",
            "website_url": "https://www.bidfood.com.au",
            "features": ["real_time_pricing", "automated_ordering", "inventory_sync", "delivery_tracking"],
            "categories": ["food", "beverages", "supplies", "equipment"],
            "delivery_areas": ["australia_wide"],
            "minimum_order": 200.0,
            "delivery_lead_time": 2,
            "integration_type": "api",
            "required_config": ["api_key", "location_id"]
        },
        "pfd": {
            "id": "pfd",
            "name": "PFD (Professional Food Distributors)",
            "description": "Professional food distribution services",
            "api_url": "https://api.pfd.com.au/v2",
            "website_url": "https://www.pfd.com.au",
            "features": ["real_time_pricing", "automated_ordering", "inventory_sync"],
            "categories": ["food", "beverages", "supplies"],
            "delivery_areas": ["australia_wide"],
            "minimum_order": 150.0,
            "delivery_lead_time": 1,
            "integration_type": "api",
            "required_config": ["api_key", "account_number"]
        },
        "ordermentum": {
            "id": "ordermentum",
            "name": "Ordermentum",
            "description": "Digital ordering platform for hospitality",
            "api_url": "https://api.ordermentum.com/v1",
            "website_url": "https://www.ordermentum.com",
            "features": ["real_time_pricing", "automated_ordering", "supplier_network"],
            "categories": ["food", "beverages", "supplies"],
            "delivery_areas": ["australia_wide"],
            "minimum_order": 100.0,
            "delivery_lead_time": 2,
            "integration_type": "api",
            "required_config": ["api_key", "restaurant_id"]
        },
        "manual_supplier": {
            "id": "manual_supplier",
            "name": "Manual Supplier",
            "description": "Suppliers without API integration",
            "features": ["pdf_order_sheets", "email_orders", "manual_tracking"],
            "categories": ["custom"],
            "delivery_areas": ["custom"],
            "minimum_order": 0.0,
            "delivery_lead_time": 0,
            "integration_type": "manual",
            "required_config": ["supplier_name", "supplier_email"]
        }
    }
    
    return {
        "suppliers": suppliers,
        "total_suppliers": len(suppliers)
    }

@router.get("/test-connection/{supplier_id}")
async def test_supplier_connection(
    supplier_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Test connection to a supplier API"""
    try:
        if supplier_id not in ["bidfood", "pfd", "ordermentum"]:
            raise HTTPException(status_code=400, detail="Invalid supplier ID")
        
        # Get configuration from database
        db = get_firestore_client()
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc = db.collection("supplier_api_configs").document(supplier_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier configuration not found")
        
        config = doc.to_dict()
        
        # Create integration and test
        integration = create_supplier_integration(supplier_id, config)
        if not integration:
            raise HTTPException(status_code=400, detail="Failed to create integration")
        
        # Test by getting products
        async with integration:
            products = await integration.get_products()
        
        return {
            "success": True,
            "supplier_id": supplier_id,
            "message": "Connection test successful",
            "products_available": len(products)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing supplier connection: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}") 