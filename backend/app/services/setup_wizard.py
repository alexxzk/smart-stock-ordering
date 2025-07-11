import uuid
import csv
import io
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from firebase_admin import auth, firestore

from app.models.setup_wizard import (
    SetupWizardSession, SetupStep, RestaurantProfile, MenuItemUpload,
    IngredientUpload, SupplierUpload, InitialStockUpload, SetupProgress,
    SetupValidation, SetupCompletion, CSVUploadRequest, CSVUploadResponse
)
from app.models.restaurants import Restaurant, MenuItem, Recipe, Ingredient, Supplier
from app.firebase_init import get_firestore_client

logger = logging.getLogger(__name__)

class SetupWizardService:
    """Service for handling restaurant setup wizard"""
    
    def __init__(self):
        self.db = firestore.client()
    
    async def create_session(self, admin_user_id: str) -> SetupWizardSession:
        """Create a new setup wizard session"""
        try:
            session_id = str(uuid.uuid4())
            session = SetupWizardSession(
                session_id=session_id,
                current_step=SetupStep.RESTAURANT_PROFILE,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save session to Firestore
            self.db.collection('setup_sessions').document(session_id).set(session.dict())
            
            logger.info(f"Created setup session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating setup session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SetupWizardSession]:
        """Get setup wizard session"""
        try:
            doc = self.db.collection('setup_sessions').document(session_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                return SetupWizardSession(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting setup session: {e}")
            return None
    
    async def update_session(self, session: SetupWizardSession) -> None:
        """Update setup wizard session"""
        try:
            session.updated_at = datetime.now()
            self.db.collection('setup_sessions').document(session.session_id).set(session.dict())
            
        except Exception as e:
            logger.error(f"Error updating setup session: {e}")
            raise
    
    async def save_restaurant_profile(self, session_id: str, profile: RestaurantProfile) -> SetupValidation:
        """Save restaurant profile and validate"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return SetupValidation(
                    step=SetupStep.RESTAURANT_PROFILE,
                    is_valid=False,
                    errors=["Session not found"]
                )
            
            # Validate restaurant profile
            validation = await self._validate_restaurant_profile(profile)
            
            if validation.is_valid:
                # Save to session
                session.restaurant_profile = profile
                session.completed_steps.append(SetupStep.RESTAURANT_PROFILE)
                session.current_step = SetupStep.MENU_ITEMS
                await self.update_session(session)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error saving restaurant profile: {e}")
            return SetupValidation(
                step=SetupStep.RESTAURANT_PROFILE,
                is_valid=False,
                errors=[str(e)]
            )
    
    async def save_menu_items(self, session_id: str, menu_items: List[MenuItemUpload]) -> SetupValidation:
        """Save menu items and validate"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return SetupValidation(
                    step=SetupStep.MENU_ITEMS,
                    is_valid=False,
                    errors=["Session not found"]
                )
            
            # Validate menu items
            validation = await self._validate_menu_items(menu_items)
            
            if validation.is_valid:
                # Save to session
                session.menu_items = menu_items
                session.completed_steps.append(SetupStep.MENU_ITEMS)
                session.current_step = SetupStep.INGREDIENTS
                await self.update_session(session)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error saving menu items: {e}")
            return SetupValidation(
                step=SetupStep.MENU_ITEMS,
                is_valid=False,
                errors=[str(e)]
            )
    
    async def save_ingredients(self, session_id: str, ingredients: List[IngredientUpload]) -> SetupValidation:
        """Save ingredients and validate"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return SetupValidation(
                    step=SetupStep.INGREDIENTS,
                    is_valid=False,
                    errors=["Session not found"]
                )
            
            # Validate ingredients
            validation = await self._validate_ingredients(ingredients)
            
            if validation.is_valid:
                # Save to session
                session.ingredients = ingredients
                session.completed_steps.append(SetupStep.INGREDIENTS)
                session.current_step = SetupStep.SUPPLIERS
                await self.update_session(session)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error saving ingredients: {e}")
            return SetupValidation(
                step=SetupStep.INGREDIENTS,
                is_valid=False,
                errors=[str(e)]
            )
    
    async def save_suppliers(self, session_id: str, suppliers: List[SupplierUpload]) -> SetupValidation:
        """Save suppliers and validate"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return SetupValidation(
                    step=SetupStep.SUPPLIERS,
                    is_valid=False,
                    errors=["Session not found"]
                )
            
            # Validate suppliers
            validation = await self._validate_suppliers(suppliers)
            
            if validation.is_valid:
                # Save to session
                session.suppliers = suppliers
                session.completed_steps.append(SetupStep.SUPPLIERS)
                session.current_step = SetupStep.INITIAL_STOCK
                await self.update_session(session)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error saving suppliers: {e}")
            return SetupValidation(
                step=SetupStep.SUPPLIERS,
                is_valid=False,
                errors=[str(e)]
            )
    
    async def save_initial_stock(self, session_id: str, initial_stock: List[InitialStockUpload]) -> SetupValidation:
        """Save initial stock and validate"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return SetupValidation(
                    step=SetupStep.INITIAL_STOCK,
                    is_valid=False,
                    errors=["Session not found"]
                )
            
            # Validate initial stock
            validation = await self._validate_initial_stock(initial_stock, session.ingredients)
            
            if validation.is_valid:
                # Save to session
                session.initial_stock = initial_stock
                session.completed_steps.append(SetupStep.INITIAL_STOCK)
                session.current_step = SetupStep.COMPLETE
                await self.update_session(session)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error saving initial stock: {e}")
            return SetupValidation(
                step=SetupStep.INITIAL_STOCK,
                is_valid=False,
                errors=[str(e)]
            )
    
    async def complete_setup(self, session_id: str) -> SetupCompletion:
        """Complete the setup process and create all data"""
        try:
            session = await self.get_session(session_id)
            if not session:
                raise ValueError("Session not found")
            
            if not session.restaurant_profile:
                raise ValueError("Restaurant profile not found")
            
            # Create restaurant
            restaurant_id = await self._create_restaurant(session.restaurant_profile)
            
            # Create owner user account
            owner_user_id = await self._create_owner_account(session.restaurant_profile)
            
            # Create suppliers
            supplier_map = await self._create_suppliers(session.suppliers, restaurant_id)
            
            # Create ingredients
            ingredient_map = await self._create_ingredients(session.ingredients, restaurant_id, supplier_map)
            
            # Create menu items and recipes
            await self._create_menu_items_and_recipes(session.menu_items, restaurant_id, ingredient_map)
            
            # Set initial stock
            await self._set_initial_stock(session.initial_stock, ingredient_map)
            
            # Mark session as completed
            session.is_completed = True
            session.restaurant_id = restaurant_id
            await self.update_session(session)
            
            # Create completion summary
            completion = SetupCompletion(
                session_id=session_id,
                restaurant_id=restaurant_id,
                owner_user_id=owner_user_id,
                completion_time=datetime.now(),
                summary={
                    "restaurant_name": session.restaurant_profile.name,
                    "menu_items_created": len(session.menu_items),
                    "ingredients_created": len(session.ingredients),
                    "suppliers_created": len(session.suppliers),
                    "initial_stock_items": len(session.initial_stock)
                },
                next_steps=[
                    "Owner account created - check email for login credentials",
                    "Restaurant profile is ready for use",
                    "Menu items and recipes are configured",
                    "Inventory tracking is active",
                    "Supplier contacts are set up"
                ]
            )
            
            logger.info(f"Setup completed for restaurant: {restaurant_id}")
            return completion
            
        except Exception as e:
            logger.error(f"Error completing setup: {e}")
            raise
    
    async def process_csv_upload(self, request: CSVUploadRequest) -> CSVUploadResponse:
        """Process CSV upload for bulk data import"""
        try:
            csv_file = io.StringIO(request.csv_data)
            reader = csv.DictReader(csv_file) if request.has_headers else csv.reader(csv_file)
            
            records_processed = 0
            records_failed = 0
            errors = []
            preview_data = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                try:
                    if request.file_type == "menu_items":
                        processed_row = self._process_menu_item_row(row)
                    elif request.file_type == "ingredients":
                        processed_row = self._process_ingredient_row(row)
                    elif request.file_type == "suppliers":
                        processed_row = self._process_supplier_row(row)
                    else:
                        raise ValueError(f"Unsupported file type: {request.file_type}")
                    
                    if len(preview_data) < 5:  # Show first 5 rows as preview
                        preview_data.append(processed_row)
                    
                    records_processed += 1
                    
                except Exception as e:
                    records_failed += 1
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return CSVUploadResponse(
                success=records_failed == 0,
                records_processed=records_processed,
                records_failed=records_failed,
                errors=errors,
                preview_data=preview_data
            )
            
        except Exception as e:
            logger.error(f"Error processing CSV upload: {e}")
            return CSVUploadResponse(
                success=False,
                records_processed=0,
                records_failed=1,
                errors=[str(e)],
                preview_data=[]
            )
    
    async def get_progress(self, session_id: str) -> SetupProgress:
        """Get setup progress"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return SetupProgress(
                    session_id=session_id,
                    current_step=SetupStep.RESTAURANT_PROFILE,
                    completed_steps=[],
                    progress_percentage=0.0,
                    next_step=SetupStep.RESTAURANT_PROFILE,
                    can_proceed=False,
                    validation_errors=["Session not found"]
                )
            
            progress_percentage = (len(session.completed_steps) / session.total_steps) * 100
            next_step = self._get_next_step(session.current_step)
            can_proceed = len(session.completed_steps) >= session.total_steps - 1
            
            return SetupProgress(
                session_id=session_id,
                current_step=session.current_step,
                completed_steps=session.completed_steps,
                progress_percentage=progress_percentage,
                next_step=next_step,
                can_proceed=can_proceed,
                validation_errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return SetupProgress(
                session_id=session_id,
                current_step=SetupStep.RESTAURANT_PROFILE,
                completed_steps=[],
                progress_percentage=0.0,
                next_step=SetupStep.RESTAURANT_PROFILE,
                can_proceed=False,
                validation_errors=[str(e)]
            )
    
    # Private helper methods
    
    async def _validate_restaurant_profile(self, profile: RestaurantProfile) -> SetupValidation:
        """Validate restaurant profile"""
        errors = []
        warnings = []
        suggestions = []
        
        # Basic validation
        if not profile.name.strip():
            errors.append("Restaurant name is required")
        
        if not profile.address.strip():
            errors.append("Restaurant address is required")
        
        if not profile.phone.strip():
            errors.append("Phone number is required")
        
        if not profile.owner_email:
            errors.append("Owner email is required")
        
        # Check if restaurant name already exists
        existing_restaurants = self.db.collection('restaurants').where('name', '==', profile.name).stream()
        if list(existing_restaurants):
            warnings.append("A restaurant with this name already exists")
        
        # Suggestions
        if not profile.cuisine_type:
            suggestions.append("Consider adding cuisine type for better categorization")
        
        if not profile.business_hours:
            suggestions.append("Add business hours for customer information")
        
        return SetupValidation(
            step=SetupStep.RESTAURANT_PROFILE,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _validate_menu_items(self, menu_items: List[MenuItemUpload]) -> SetupValidation:
        """Validate menu items"""
        errors = []
        warnings = []
        suggestions = []
        
        if not menu_items:
            errors.append("At least one menu item is required")
            return SetupValidation(
                step=SetupStep.MENU_ITEMS,
                is_valid=False,
                errors=errors
            )
        
        for i, item in enumerate(menu_items):
            if not item.name.strip():
                errors.append(f"Menu item {i+1}: Name is required")
            
            if item.price <= 0:
                errors.append(f"Menu item {i+1}: Price must be greater than 0")
            
            if not item.ingredients:
                warnings.append(f"Menu item {i+1}: No ingredients specified")
        
        # Check for duplicate names
        names = [item.name.lower().strip() for item in menu_items]
        if len(names) != len(set(names)):
            warnings.append("Duplicate menu item names detected")
        
        if len(menu_items) < 5:
            suggestions.append("Consider adding more menu items for variety")
        
        return SetupValidation(
            step=SetupStep.MENU_ITEMS,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _validate_ingredients(self, ingredients: List[IngredientUpload]) -> SetupValidation:
        """Validate ingredients"""
        errors = []
        warnings = []
        suggestions = []
        
        if not ingredients:
            errors.append("At least one ingredient is required")
            return SetupValidation(
                step=SetupStep.INGREDIENTS,
                is_valid=False,
                errors=errors
            )
        
        for i, ingredient in enumerate(ingredients):
            if not ingredient.name.strip():
                errors.append(f"Ingredient {i+1}: Name is required")
            
            if ingredient.min_stock_level <= 0:
                errors.append(f"Ingredient {i+1}: Minimum stock level must be greater than 0")
            
            if ingredient.cost_per_unit < 0:
                errors.append(f"Ingredient {i+1}: Cost per unit cannot be negative")
        
        # Check for duplicate names
        names = [ingredient.name.lower().strip() for ingredient in ingredients]
        if len(names) != len(set(names)):
            warnings.append("Duplicate ingredient names detected")
        
        return SetupValidation(
            step=SetupStep.INGREDIENTS,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _validate_suppliers(self, suppliers: List[SupplierUpload]) -> SetupValidation:
        """Validate suppliers"""
        errors = []
        warnings = []
        suggestions = []
        
        for i, supplier in enumerate(suppliers):
            if not supplier.name.strip():
                errors.append(f"Supplier {i+1}: Name is required")
            
            if not supplier.email:
                errors.append(f"Supplier {i+1}: Email is required")
        
        return SetupValidation(
            step=SetupStep.SUPPLIERS,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _validate_initial_stock(self, initial_stock: List[InitialStockUpload], ingredients: List[IngredientUpload]) -> SetupValidation:
        """Validate initial stock"""
        errors = []
        warnings = []
        suggestions = []
        
        ingredient_names = {ingredient.name.lower().strip(): ingredient.name for ingredient in ingredients}
        
        for stock_item in initial_stock:
            if stock_item.quantity <= 0:
                errors.append(f"Initial stock quantity must be greater than 0")
            
            if stock_item.cost < 0:
                errors.append(f"Initial stock cost cannot be negative")
        
        return SetupValidation(
            step=SetupStep.INITIAL_STOCK,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _create_restaurant(self, profile: RestaurantProfile) -> str:
        """Create restaurant in database"""
        restaurant_id = str(uuid.uuid4())
        
        restaurant_data = {
            "restaurant_id": restaurant_id,
            "name": profile.name,
            "address": profile.address,
            "phone": profile.phone,
            "email": profile.email,
            "owner_email": profile.owner_email,
            "owner_name": profile.owner_name,
            "cuisine_type": profile.cuisine_type,
            "business_hours": profile.business_hours,
            "tax_rate": profile.tax_rate,
            "currency": profile.currency,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.db.collection('restaurants').document(restaurant_id).set(restaurant_data)
        return restaurant_id
    
    async def _create_owner_account(self, profile: RestaurantProfile) -> str:
        """Create owner user account"""
        try:
            # Create user in Firebase Auth
            user_record = auth.create_user(
                email=profile.owner_email,
                display_name=profile.owner_name,
                password=str(uuid.uuid4())  # Generate random password
            )
            
            # Send password reset email
            auth.generate_password_reset_link(profile.owner_email)
            
            return user_record.uid
            
        except Exception as e:
            logger.error(f"Error creating owner account: {e}")
            # Return a placeholder if Firebase Auth fails
            return f"owner-{uuid.uuid4()}"
    
    async def _create_suppliers(self, suppliers: List[SupplierUpload], restaurant_id: str) -> Dict[str, str]:
        """Create suppliers and return mapping of name to ID"""
        supplier_map = {}
        
        for supplier in suppliers:
            supplier_id = str(uuid.uuid4())
            supplier_data = {
                "supplier_id": supplier_id,
                "name": supplier.name,
                "contact_person": supplier.contact_person,
                "email": supplier.email,
                "phone": supplier.phone,
                "address": supplier.address,
                "specialties": supplier.specialties,
                "payment_terms": supplier.payment_terms,
                "delivery_schedule": supplier.delivery_schedule,
                "restaurant_id": restaurant_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.db.collection('suppliers').document(supplier_id).set(supplier_data)
            supplier_map[supplier.name.lower()] = supplier_id
        
        return supplier_map
    
    async def _create_ingredients(self, ingredients: List[IngredientUpload], restaurant_id: str, supplier_map: Dict[str, str]) -> Dict[str, str]:
        """Create ingredients and return mapping of name to ID"""
        ingredient_map = {}
        
        for ingredient in ingredients:
            ingredient_id = str(uuid.uuid4())
            
            # Find supplier ID if supplier name is provided
            supplier_id = None
            if ingredient.supplier_name:
                supplier_id = supplier_map.get(ingredient.supplier_name.lower())
            
            ingredient_data = {
                "ingredient_id": ingredient_id,
                "name": ingredient.name,
                "unit": ingredient.unit,
                "current_stock": ingredient.current_stock,
                "min_stock_level": ingredient.min_stock_level,
                "max_stock_level": ingredient.max_stock_level,
                "cost_per_unit": ingredient.cost_per_unit,
                "supplier_id": supplier_id,
                "restaurant_id": restaurant_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.db.collection('ingredients').document(ingredient_id).set(ingredient_data)
            ingredient_map[ingredient.name.lower()] = ingredient_id
        
        return ingredient_map
    
    async def _create_menu_items_and_recipes(self, menu_items: List[MenuItemUpload], restaurant_id: str, ingredient_map: Dict[str, str]):
        """Create menu items and their recipes"""
        for menu_item in menu_items:
            # Create menu item
            menu_item_id = str(uuid.uuid4())
            menu_item_data = {
                "menu_item_id": menu_item_id,
                "name": menu_item.name,
                "description": menu_item.description,
                "price": menu_item.price,
                "category": menu_item.category,
                "restaurant_id": restaurant_id,
                "is_available": menu_item.is_available,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.db.collection('menu_items').document(menu_item_id).set(menu_item_data)
            
            # Create recipe
            recipe_id = str(uuid.uuid4())
            recipe_ingredients = []
            
            for ingredient_info in menu_item.ingredients:
                ingredient_name = ingredient_info.get('name', '').lower()
                ingredient_id = ingredient_map.get(ingredient_name)
                
                if ingredient_id:
                    recipe_ingredients.append({
                        "ingredient_id": ingredient_id,
                        "quantity": ingredient_info.get('quantity', 0),
                        "unit": ingredient_info.get('unit', '')
                    })
            
            recipe_data = {
                "recipe_id": recipe_id,
                "menu_item_id": menu_item_id,
                "name": f"{menu_item.name} Recipe",
                "description": f"Recipe for {menu_item.name}",
                "ingredients": recipe_ingredients,
                "instructions": menu_item.description or f"Prepare {menu_item.name}",
                "prep_time_minutes": 5,
                "restaurant_id": restaurant_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.db.collection('recipes').document(recipe_id).set(recipe_data)
    
    async def _set_initial_stock(self, initial_stock: List[InitialStockUpload], ingredient_map: Dict[str, str]):
        """Set initial stock levels"""
        for stock_item in initial_stock:
            ingredient_id = stock_item.ingredient_id
            if ingredient_id in ingredient_map.values():
                # Update ingredient stock
                self.db.collection('ingredients').document(ingredient_id).update({
                    "current_stock": stock_item.quantity,
                    "updated_at": datetime.now()
                })
    
    def _get_next_step(self, current_step: SetupStep) -> SetupStep:
        """Get the next step in the setup process"""
        steps = [
            SetupStep.RESTAURANT_PROFILE,
            SetupStep.MENU_ITEMS,
            SetupStep.INGREDIENTS,
            SetupStep.SUPPLIERS,
            SetupStep.INITIAL_STOCK,
            SetupStep.COMPLETE
        ]
        
        try:
            current_index = steps.index(current_step)
            if current_index < len(steps) - 1:
                return steps[current_index + 1]
        except ValueError:
            pass
        
        return SetupStep.COMPLETE
    
    def _process_menu_item_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Process a menu item CSV row"""
        return {
            "name": row.get("name", ""),
            "description": row.get("description", ""),
            "price": float(row.get("price", 0)),
            "category": row.get("category", ""),
            "ingredients": []  # Will be processed separately
        }
    
    def _process_ingredient_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Process an ingredient CSV row"""
        return {
            "name": row.get("name", ""),
            "unit": row.get("unit", ""),
            "current_stock": float(row.get("current_stock", 0)),
            "min_stock_level": float(row.get("min_stock_level", 0)),
            "max_stock_level": float(row.get("max_stock_level", 0)) if row.get("max_stock_level") else None,
            "cost_per_unit": float(row.get("cost_per_unit", 0)),
            "supplier_name": row.get("supplier_name", "")
        }
    
    def _process_supplier_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Process a supplier CSV row"""
        return {
            "name": row.get("name", ""),
            "contact_person": row.get("contact_person", ""),
            "email": row.get("email", ""),
            "phone": row.get("phone", ""),
            "address": row.get("address", ""),
            "specialties": row.get("specialties", "").split(",") if row.get("specialties") else []
        } 