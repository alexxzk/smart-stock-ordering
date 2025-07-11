import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import os
from pathlib import Path

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Email functionality
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

@dataclass
class SupplierProduct:
    """Represents a product from a supplier"""
    product_id: str
    name: str
    description: str
    price: float
    unit: str
    category: str
    supplier_id: str
    in_stock: bool
    min_order_qty: int
    lead_time_days: int
    last_updated: datetime

@dataclass
class OrderItem:
    """Represents an item in an order"""
    product_id: str
    name: str
    quantity: int
    unit: str
    unit_price: float
    total_price: float
    notes: str = ""

@dataclass
class OrderRequest:
    """Represents an order request to a supplier"""
    order_id: str
    supplier_id: str
    items: List[OrderItem]
    delivery_address: str
    delivery_date: datetime
    contact_person: str
    contact_phone: str
    contact_email: str
    notes: str = ""
    urgent: bool = False

@dataclass
class OrderConfirmation:
    """Represents an order confirmation from a supplier"""
    order_id: str
    supplier_order_id: str
    status: str
    estimated_delivery: datetime
    total_amount: float
    confirmation_message: str

class SupplierAPIIntegration:
    """Base class for supplier API integrations"""
    
    def __init__(self, supplier_id: str, api_key: str, base_url: str):
        self.supplier_id = supplier_id
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to supplier API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {"error": str(e)}

class BidfoodIntegration(SupplierAPIIntegration):
    """Bidfood API integration"""
    
    def __init__(self, api_key: str, location_id: str):
        super().__init__(
            supplier_id="bidfood",
            api_key=api_key,
            base_url="https://api.bidfood.com.au/v1"
        )
        self.location_id = location_id
    
    async def get_products(self, category: str = None) -> List[SupplierProduct]:
        """Get products from Bidfood"""
        endpoint = f"/products"
        params = {"location_id": self.location_id}
        if category:
            params["category"] = category
        
        data = await self._make_request("GET", endpoint)
        
        if "error" in data:
            return []
        
        products = []
        for item in data.get("products", []):
            products.append(SupplierProduct(
                product_id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                price=float(item["price"]),
                unit=item["unit"],
                category=item["category"],
                supplier_id="bidfood",
                in_stock=item.get("in_stock", True),
                min_order_qty=item.get("min_order_qty", 1),
                lead_time_days=item.get("lead_time_days", 2),
                last_updated=datetime.fromisoformat(item["last_updated"])
            ))
        
        return products
    
    async def get_pricing(self, product_ids: List[str]) -> Dict[str, float]:
        """Get pricing for specific products"""
        endpoint = f"/pricing"
        data = {"product_ids": product_ids, "location_id": self.location_id}
        
        result = await self._make_request("POST", endpoint, data)
        
        if "error" in result:
            return {}
        
        return {item["product_id"]: float(item["price"]) for item in result.get("pricing", [])}
    
    async def place_order(self, order: OrderRequest) -> OrderConfirmation:
        """Place order with Bidfood"""
        endpoint = f"/orders"
        
        order_data = {
            "location_id": self.location_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
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
            "urgent": order.urgent
        }
        
        result = await self._make_request("POST", endpoint, order_data)
        
        if "error" in result:
            return OrderConfirmation(
                order_id=order.order_id,
                supplier_order_id="",
                status="failed",
                estimated_delivery=datetime.now() + timedelta(days=7),
                total_amount=0.0,
                confirmation_message=f"Order failed: {result['error']}"
            )
        
        return OrderConfirmation(
            order_id=order.order_id,
            supplier_order_id=result["supplier_order_id"],
            status=result["status"],
            estimated_delivery=datetime.fromisoformat(result["estimated_delivery"]),
            total_amount=float(result["total_amount"]),
            confirmation_message=result["confirmation_message"]
        )

class PFDIntegration(SupplierAPIIntegration):
    """PFD (Professional Food Distributors) API integration"""
    
    def __init__(self, api_key: str, account_number: str):
        super().__init__(
            supplier_id="pfd",
            api_key=api_key,
            base_url="https://api.pfd.com.au/v2"
        )
        self.account_number = account_number
    
    async def get_products(self, category: str = None) -> List[SupplierProduct]:
        """Get products from PFD"""
        endpoint = f"/catalog"
        params = {"account_number": self.account_number}
        if category:
            params["category"] = category
        
        data = await self._make_request("GET", endpoint)
        
        if "error" in data:
            return []
        
        products = []
        for item in data.get("products", []):
            products.append(SupplierProduct(
                product_id=item["product_code"],
                name=item["product_name"],
                description=item.get("description", ""),
                price=float(item["unit_price"]),
                unit=item["unit_of_measure"],
                category=item["category"],
                supplier_id="pfd",
                in_stock=item.get("available", True),
                min_order_qty=item.get("minimum_order", 1),
                lead_time_days=item.get("lead_time", 1),
                last_updated=datetime.fromisoformat(item["last_updated"])
            ))
        
        return products
    
    async def place_order(self, order: OrderRequest) -> OrderConfirmation:
        """Place order with PFD"""
        endpoint = f"/orders"
        
        order_data = {
            "account_number": self.account_number,
            "order_lines": [
                {
                    "product_code": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_notes": item.notes
                }
                for item in order.items
            ],
            "delivery_address": order.delivery_address,
            "delivery_date": order.delivery_date.strftime("%Y-%m-%d"),
            "contact_name": order.contact_person,
            "contact_phone": order.contact_phone,
            "contact_email": order.contact_email,
            "order_notes": order.notes,
            "priority": "urgent" if order.urgent else "standard"
        }
        
        result = await self._make_request("POST", endpoint, order_data)
        
        if "error" in result:
            return OrderConfirmation(
                order_id=order.order_id,
                supplier_order_id="",
                status="failed",
                estimated_delivery=datetime.now() + timedelta(days=7),
                total_amount=0.0,
                confirmation_message=f"Order failed: {result['error']}"
            )
        
        return OrderConfirmation(
            order_id=order.order_id,
            supplier_order_id=result["pfd_order_number"],
            status=result["order_status"],
            estimated_delivery=datetime.fromisoformat(result["estimated_delivery"]),
            total_amount=float(result["order_total"]),
            confirmation_message=result["confirmation_message"]
        )

class OrdermentumIntegration(SupplierAPIIntegration):
    """Ordermentum API integration"""
    
    def __init__(self, api_key: str, restaurant_id: str):
        super().__init__(
            supplier_id="ordermentum",
            api_key=api_key,
            base_url="https://api.ordermentum.com/v1"
        )
        self.restaurant_id = restaurant_id
    
    async def get_products(self, category: str = None) -> List[SupplierProduct]:
        """Get products from Ordermentum"""
        endpoint = f"/products"
        params = {"restaurant_id": self.restaurant_id}
        if category:
            params["category"] = category
        
        data = await self._make_request("GET", endpoint)
        
        if "error" in data:
            return []
        
        products = []
        for item in data.get("products", []):
            products.append(SupplierProduct(
                product_id=item["product_id"],
                name=item["name"],
                description=item.get("description", ""),
                price=float(item["price"]),
                unit=item["unit"],
                category=item["category"],
                supplier_id="ordermentum",
                in_stock=item.get("available", True),
                min_order_qty=item.get("minimum_order", 1),
                lead_time_days=item.get("lead_time", 2),
                last_updated=datetime.fromisoformat(item["updated_at"])
            ))
        
        return products
    
    async def place_order(self, order: OrderRequest) -> OrderConfirmation:
        """Place order with Ordermentum"""
        endpoint = f"/orders"
        
        order_data = {
            "restaurant_id": self.restaurant_id,
            "order_items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "notes": item.notes
                }
                for item in order.items
            ],
            "delivery_address": order.delivery_address,
            "delivery_date": order.delivery_date.isoformat(),
            "contact": {
                "name": order.contact_person,
                "phone": order.contact_phone,
                "email": order.contact_email
            },
            "notes": order.notes,
            "priority": "high" if order.urgent else "normal"
        }
        
        result = await self._make_request("POST", endpoint, order_data)
        
        if "error" in result:
            return OrderConfirmation(
                order_id=order.order_id,
                supplier_order_id="",
                status="failed",
                estimated_delivery=datetime.now() + timedelta(days=7),
                total_amount=0.0,
                confirmation_message=f"Order failed: {result['error']}"
            )
        
        return OrderConfirmation(
            order_id=order.order_id,
            supplier_order_id=result["ordermentum_order_id"],
            status=result["status"],
            estimated_delivery=datetime.fromisoformat(result["estimated_delivery"]),
            total_amount=float(result["total"]),
            confirmation_message=result["message"]
        )

class OrderSheetGenerator:
    """Generate PDF and email order sheets for suppliers without APIs"""
    
    def __init__(self, output_dir: str = "order_sheets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_pdf_order_sheet(self, order: OrderRequest, supplier_name: str) -> str:
        """Generate PDF order sheet"""
        filename = f"order_{order.order_id}_{supplier_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        title = Paragraph(f"Order Sheet - {supplier_name}", title_style)
        story.append(title)
        
        # Order details
        order_details = [
            ["Order ID:", order.order_id],
            ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Delivery Date:", order.delivery_date.strftime("%Y-%m-%d")],
            ["Contact Person:", order.contact_person],
            ["Contact Phone:", order.contact_phone],
            ["Contact Email:", order.contact_email],
            ["Delivery Address:", order.delivery_address],
            ["Urgent:", "Yes" if order.urgent else "No"]
        ]
        
        if order.notes:
            order_details.append(["Notes:", order.notes])
        
        order_table = Table(order_details, colWidths=[2*inch, 4*inch])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(order_table)
        story.append(Spacer(1, 20))
        
        # Items table
        items_data = [["Item", "Quantity", "Unit", "Unit Price", "Total Price", "Notes"]]
        total_amount = 0
        
        for item in order.items:
            items_data.append([
                item.name,
                str(item.quantity),
                item.unit,
                f"${item.unit_price:.2f}",
                f"${item.total_price:.2f}",
                item.notes
            ])
            total_amount += item.total_price
        
        items_data.append(["", "", "", "TOTAL:", f"${total_amount:.2f}", ""])
        
        items_table = Table(items_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch, 1.4*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue)
        ]))
        
        story.append(items_table)
        
        # Build PDF
        doc.build(story)
        return str(filepath)
    
    def generate_email_order_sheet(self, order: OrderRequest, supplier_name: str, supplier_email: str) -> bool:
        """Generate and send email order sheet"""
        try:
            # Generate PDF
            pdf_path = self.generate_pdf_order_sheet(order, supplier_name)
            
            # Email configuration
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            if not all([smtp_username, smtp_password]):
                logger.error("SMTP credentials not configured")
                return False
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = supplier_email
            msg['Subject'] = f"Order Request - {order.order_id} - {supplier_name}"
            
            # Email body
            body = f"""
            Dear {supplier_name} Team,
            
            Please find attached our order request (Order ID: {order.order_id}).
            
            Order Details:
            - Order ID: {order.order_id}
            - Delivery Date: {order.delivery_date.strftime('%Y-%m-%d')}
            - Contact: {order.contact_person} ({order.contact_phone})
            - Delivery Address: {order.delivery_address}
            - Urgent: {'Yes' if order.urgent else 'No'}
            
            {f'Notes: {order.notes}' if order.notes else ''}
            
            Please confirm receipt of this order and provide delivery confirmation.
            
            Best regards,
            {order.contact_person}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(pdf_path)}'
            )
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Order email sent to {supplier_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending order email: {e}")
            return False

class SupplierIntegrationManager:
    """Manages all supplier integrations"""
    
    def __init__(self):
        self.integrations = {}
        self.order_generator = OrderSheetGenerator()
    
    def register_integration(self, supplier_id: str, integration: SupplierAPIIntegration):
        """Register a supplier integration"""
        self.integrations[supplier_id] = integration
    
    async def get_products(self, supplier_id: str, category: str = None) -> List[SupplierProduct]:
        """Get products from a supplier"""
        if supplier_id not in self.integrations:
            logger.error(f"No integration found for supplier: {supplier_id}")
            return []
        
        integration = self.integrations[supplier_id]
        async with integration:
            return await integration.get_products(category)
    
    async def place_order(self, supplier_id: str, order: OrderRequest) -> OrderConfirmation:
        """Place order with a supplier"""
        if supplier_id not in self.integrations:
            logger.error(f"No integration found for supplier: {supplier_id}")
            return OrderConfirmation(
                order_id=order.order_id,
                supplier_order_id="",
                status="failed",
                estimated_delivery=datetime.now() + timedelta(days=7),
                total_amount=0.0,
                confirmation_message=f"No integration available for {supplier_id}"
            )
        
        integration = self.integrations[supplier_id]
        async with integration:
            return await integration.place_order(order)
    
    def generate_order_sheet(self, order: OrderRequest, supplier_name: str, supplier_email: str = None) -> str:
        """Generate order sheet for suppliers without APIs"""
        pdf_path = self.order_generator.generate_pdf_order_sheet(order, supplier_name)
        
        if supplier_email:
            self.order_generator.generate_email_order_sheet(order, supplier_name, supplier_email)
        
        return pdf_path

# Factory function to create integrations
def create_supplier_integration(supplier_id: str, config: Dict[str, str]) -> Optional[SupplierAPIIntegration]:
    """Create a supplier integration based on supplier ID and configuration"""
    
    if supplier_id == "bidfood":
        return BidfoodIntegration(
            api_key=config["api_key"],
            location_id=config["location_id"]
        )
    
    elif supplier_id == "pfd":
        return PFDIntegration(
            api_key=config["api_key"],
            account_number=config["account_number"]
        )
    
    elif supplier_id == "ordermentum":
        return OrdermentumIntegration(
            api_key=config["api_key"],
            restaurant_id=config["restaurant_id"]
        )
    
    else:
        logger.error(f"Unknown supplier ID: {supplier_id}")
        return None 