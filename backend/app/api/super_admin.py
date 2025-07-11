from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, firestore
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from app.models.restaurants import (
    Restaurant, RestaurantCreateRequest, RestaurantStatus,
    MenuItem, MenuItemCreateRequest,
    Recipe, RecipeCreateRequest, RecipeIngredient,
    Ingredient, IngredientCreateRequest,
    Supplier, SupplierCreateRequest,
    SupplierIngredientLink,
    InitialStock, InitialStockCreateRequest
)

router = APIRouter(prefix="/api/super-admin", tags=["Super Admin"])
security = HTTPBearer()

# Set up logging
logger = logging.getLogger(__name__)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase JWT token and check if user is super admin"""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        
        # Check if user is super admin (you can implement your own logic here)
        # For now, we'll check if the user has a super_admin role in Firestore
        db = firestore.client()
        user_doc = db.collection('users').document(decoded_token['uid']).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=403, detail="User not found")
        
        user_data = user_doc.to_dict()
        if user_data.get('role') != 'super_admin':
            raise HTTPException(status_code=403, detail="Super admin access required")
        
        return decoded_token
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Restaurant Management
@router.post("/restaurants", response_model=Restaurant)
async def create_restaurant(
    restaurant_data: RestaurantCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new restaurant profile"""
    try:
        db = firestore.client()
        restaurant_id = str(uuid.uuid4())
        now = datetime.now()
        
        restaurant = Restaurant(
            restaurant_id=restaurant_id,
            name=restaurant_data.name,
            owner_user_id=restaurant_data.owner_user_id,
            address=restaurant_data.address,
            phone=restaurant_data.phone,
            email=restaurant_data.email,
            cuisine_type=restaurant_data.cuisine_type,
            status=RestaurantStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            settings=restaurant_data.settings
        )
        
        # Save to Firestore
        db.collection('restaurants').document(restaurant_id).set(restaurant.dict())
        
        return restaurant
    except Exception as e:
        logger.error(f"Error creating restaurant: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating restaurant: {str(e)}")

@router.get("/restaurants", response_model=List[Restaurant])
async def get_all_restaurants(
    current_user: Dict[str, Any] = Depends(get_current_user),
    status: Optional[RestaurantStatus] = None
):
    """Get all restaurants with optional status filter"""
    try:
        db = firestore.client()
        restaurants_ref = db.collection('restaurants')
        
        if status:
            restaurants_ref = restaurants_ref.where('status', '==', status.value)
        
        restaurants = []
        for doc in restaurants_ref.stream():
            restaurant_data = doc.to_dict()
            restaurant_data['restaurant_id'] = doc.id
            restaurants.append(Restaurant(**restaurant_data))
        
        return restaurants
    except Exception as e:
        logger.error(f"Error fetching restaurants: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")

@router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(
    restaurant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific restaurant by ID"""
    try:
        db = firestore.client()
        doc = db.collection('restaurants').document(restaurant_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        restaurant_data = doc.to_dict()
        restaurant_data['restaurant_id'] = doc.id
        return Restaurant(**restaurant_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching restaurant: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching restaurant: {str(e)}")

@router.put("/restaurants/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(
    restaurant_id: str,
    restaurant_data: RestaurantCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a restaurant profile"""
    try:
        db = firestore.client()
        doc_ref = db.collection('restaurants').document(restaurant_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        update_data = restaurant_data.dict()
        update_data['updated_at'] = datetime.now()
        
        doc_ref.update(update_data)
        
        # Return updated restaurant
        updated_doc = doc_ref.get()
        restaurant_data = updated_doc.to_dict()
        restaurant_data['restaurant_id'] = updated_doc.id
        return Restaurant(**restaurant_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating restaurant: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating restaurant: {str(e)}")

# Menu Items Management
@router.post("/menu-items", response_model=MenuItem)
async def create_menu_item(
    menu_item_data: MenuItemCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new menu item"""
    try:
        db = firestore.client()
        item_id = str(uuid.uuid4())
        now = datetime.now()
        
        menu_item = MenuItem(
            item_id=item_id,
            restaurant_id=menu_item_data.restaurant_id,
            name=menu_item_data.name,
            description=menu_item_data.description,
            category=menu_item_data.category,
            price=menu_item_data.price,
            cost=menu_item_data.cost,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        db.collection('menu_items').document(item_id).set(menu_item.dict())
        return menu_item
    except Exception as e:
        logger.error(f"Error creating menu item: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating menu item: {str(e)}")

@router.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItem])
async def get_restaurant_menu_items(
    restaurant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all menu items for a restaurant"""
    try:
        db = firestore.client()
        menu_items = []
        
        for doc in db.collection('menu_items').where('restaurant_id', '==', restaurant_id).stream():
            item_data = doc.to_dict()
            item_data['item_id'] = doc.id
            menu_items.append(MenuItem(**item_data))
        
        return menu_items
    except Exception as e:
        logger.error(f"Error fetching menu items: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching menu items: {str(e)}")

# Recipe Management
@router.post("/recipes", response_model=Recipe)
async def create_recipe(
    recipe_data: RecipeCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new recipe"""
    try:
        db = firestore.client()
        recipe_id = str(uuid.uuid4())
        now = datetime.now()
        
        recipe = Recipe(
            recipe_id=recipe_id,
            menu_item_id=recipe_data.menu_item_id,
            restaurant_id=recipe_data.restaurant_id,
            ingredients=recipe_data.ingredients,
            instructions=recipe_data.instructions,
            prep_time_minutes=recipe_data.prep_time_minutes,
            cook_time_minutes=recipe_data.cook_time_minutes,
            servings=recipe_data.servings,
            created_at=now,
            updated_at=now
        )
        
        db.collection('recipes').document(recipe_id).set(recipe.dict())
        return recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating recipe: {str(e)}")

@router.get("/menu-items/{menu_item_id}/recipe", response_model=Recipe)
async def get_menu_item_recipe(
    menu_item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get recipe for a specific menu item"""
    try:
        db = firestore.client()
        doc = db.collection('recipes').where('menu_item_id', '==', menu_item_id).limit(1).stream()
        
        for recipe_doc in doc:
            recipe_data = recipe_doc.to_dict()
            recipe_data['recipe_id'] = recipe_doc.id
            return Recipe(**recipe_data)
        
        raise HTTPException(status_code=404, detail="Recipe not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching recipe: {str(e)}")

# Ingredients Management
@router.post("/ingredients", response_model=Ingredient)
async def create_ingredient(
    ingredient_data: IngredientCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new ingredient"""
    try:
        db = firestore.client()
        ingredient_id = str(uuid.uuid4())
        now = datetime.now()
        
        ingredient = Ingredient(
            ingredient_id=ingredient_id,
            restaurant_id=ingredient_data.restaurant_id,
            name=ingredient_data.name,
            unit=ingredient_data.unit,
            cost_per_unit=ingredient_data.cost_per_unit,
            current_stock=ingredient_data.current_stock,
            min_stock_level=ingredient_data.min_stock_level,
            supplier_id=ingredient_data.supplier_id,
            category=ingredient_data.category,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        db.collection('ingredients').document(ingredient_id).set(ingredient.dict())
        return ingredient
    except Exception as e:
        logger.error(f"Error creating ingredient: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating ingredient: {str(e)}")

@router.get("/restaurants/{restaurant_id}/ingredients", response_model=List[Ingredient])
async def get_restaurant_ingredients(
    restaurant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all ingredients for a restaurant"""
    try:
        db = firestore.client()
        ingredients = []
        
        for doc in db.collection('ingredients').where('restaurant_id', '==', restaurant_id).stream():
            ingredient_data = doc.to_dict()
            ingredient_data['ingredient_id'] = doc.id
            ingredients.append(Ingredient(**ingredient_data))
        
        return ingredients
    except Exception as e:
        logger.error(f"Error fetching ingredients: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching ingredients: {str(e)}")

# Suppliers Management
@router.post("/suppliers", response_model=Supplier)
async def create_supplier(
    supplier_data: SupplierCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new supplier"""
    try:
        db = firestore.client()
        supplier_id = str(uuid.uuid4())
        now = datetime.now()
        
        supplier = Supplier(
            supplier_id=supplier_id,
            restaurant_id=supplier_data.restaurant_id,
            name=supplier_data.name,
            contact_person=supplier_data.contact_person,
            email=supplier_data.email,
            phone=supplier_data.phone,
            address=supplier_data.address,
            website=supplier_data.website,
            payment_terms=supplier_data.payment_terms,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        
        db.collection('suppliers').document(supplier_id).set(supplier.dict())
        return supplier
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating supplier: {str(e)}")

@router.get("/restaurants/{restaurant_id}/suppliers", response_model=List[Supplier])
async def get_restaurant_suppliers(
    restaurant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all suppliers for a restaurant"""
    try:
        db = firestore.client()
        suppliers = []
        
        for doc in db.collection('suppliers').where('restaurant_id', '==', restaurant_id).stream():
            supplier_data = doc.to_dict()
            supplier_data['supplier_id'] = doc.id
            suppliers.append(Supplier(**supplier_data))
        
        return suppliers
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching suppliers: {str(e)}")

# Initial Stock Management
@router.post("/initial-stock", response_model=InitialStock)
async def create_initial_stock(
    stock_data: InitialStockCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create initial stock for an ingredient"""
    try:
        db = firestore.client()
        now = datetime.now()
        
        initial_stock = InitialStock(
            restaurant_id=stock_data.restaurant_id,
            ingredient_id=stock_data.ingredient_id,
            initial_quantity=stock_data.initial_quantity,
            unit=stock_data.unit,
            cost_per_unit=stock_data.cost_per_unit,
            supplier_id=stock_data.supplier_id,
            notes=stock_data.notes,
            created_at=now
        )
        
        # Create a unique ID for the initial stock record
        stock_id = f"{stock_data.restaurant_id}_{stock_data.ingredient_id}_initial"
        db.collection('initial_stock').document(stock_id).set(initial_stock.dict())
        
        return initial_stock
    except Exception as e:
        logger.error(f"Error creating initial stock: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating initial stock: {str(e)}")

@router.get("/restaurants/{restaurant_id}/initial-stock", response_model=List[InitialStock])
async def get_restaurant_initial_stock(
    restaurant_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all initial stock records for a restaurant"""
    try:
        db = firestore.client()
        initial_stock_list = []
        
        for doc in db.collection('initial_stock').where('restaurant_id', '==', restaurant_id).stream():
            stock_data = doc.to_dict()
            initial_stock_list.append(InitialStock(**stock_data))
        
        return initial_stock_list
    except Exception as e:
        logger.error(f"Error fetching initial stock: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching initial stock: {str(e)}")

# Bulk Operations
@router.post("/restaurants/{restaurant_id}/setup")
async def setup_restaurant(
    restaurant_id: str,
    setup_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Complete restaurant setup with all components"""
    try:
        db = firestore.client()
        
        # Verify restaurant exists
        restaurant_doc = db.collection('restaurants').document(restaurant_id).get()
        if not restaurant_doc.exists:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Create ingredients
        ingredients = setup_data.get('ingredients', [])
        created_ingredients = []
        for ingredient_data in ingredients:
            ingredient_data['restaurant_id'] = restaurant_id
            ingredient = await create_ingredient(IngredientCreateRequest(**ingredient_data), current_user)
            created_ingredients.append(ingredient)
        
        # Create suppliers
        suppliers = setup_data.get('suppliers', [])
        created_suppliers = []
        for supplier_data in suppliers:
            supplier_data['restaurant_id'] = restaurant_id
            supplier = await create_supplier(SupplierCreateRequest(**supplier_data), current_user)
            created_suppliers.append(supplier)
        
        # Create menu items
        menu_items = setup_data.get('menu_items', [])
        created_menu_items = []
        for menu_item_data in menu_items:
            menu_item_data['restaurant_id'] = restaurant_id
            menu_item = await create_menu_item(MenuItemCreateRequest(**menu_item_data), current_user)
            created_menu_items.append(menu_item)
        
        # Create recipes
        recipes = setup_data.get('recipes', [])
        created_recipes = []
        for recipe_data in recipes:
            recipe_data['restaurant_id'] = restaurant_id
            recipe = await create_recipe(RecipeCreateRequest(**recipe_data), current_user)
            created_recipes.append(recipe)
        
        # Create initial stock
        initial_stock = setup_data.get('initial_stock', [])
        created_initial_stock = []
        for stock_data in initial_stock:
            stock_data['restaurant_id'] = restaurant_id
            stock = await create_initial_stock(InitialStockCreateRequest(**stock_data), current_user)
            created_initial_stock.append(stock)
        
        return {
            "message": "Restaurant setup completed successfully",
            "restaurant_id": restaurant_id,
            "created_ingredients": len(created_ingredients),
            "created_suppliers": len(created_suppliers),
            "created_menu_items": len(created_menu_items),
            "created_recipes": len(created_recipes),
            "created_initial_stock": len(created_initial_stock)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up restaurant: {e}")
        raise HTTPException(status_code=500, detail=f"Error setting up restaurant: {str(e)}")

# Dashboard Statistics
@router.get("/dashboard/stats")
async def get_super_admin_dashboard_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get dashboard statistics for super admin"""
    try:
        db = firestore.client()
        
        # Count restaurants
        restaurants_count = len(list(db.collection('restaurants').stream()))
        active_restaurants_count = len(list(db.collection('restaurants').where('status', '==', 'active').stream()))
        
        # Count menu items
        menu_items_count = len(list(db.collection('menu_items').stream()))
        
        # Count ingredients
        ingredients_count = len(list(db.collection('ingredients').stream()))
        
        # Count suppliers
        suppliers_count = len(list(db.collection('suppliers').stream()))
        
        # Count recipes
        recipes_count = len(list(db.collection('recipes').stream()))
        
        return {
            "total_restaurants": restaurants_count,
            "active_restaurants": active_restaurants_count,
            "total_menu_items": menu_items_count,
            "total_ingredients": ingredients_count,
            "total_suppliers": suppliers_count,
            "total_recipes": recipes_count
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}") 