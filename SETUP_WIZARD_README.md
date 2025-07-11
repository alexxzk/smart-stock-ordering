# Setup Wizard - Restaurant Onboarding System

## Overview

The Setup Wizard is a comprehensive restaurant onboarding system that allows super admins to quickly set up new restaurants with all necessary data including profiles, menu items, ingredients, suppliers, and initial stock levels.

## Features

### 🏪 Restaurant Profile Setup
- Restaurant name, address, and contact information
- Owner details and credentials
- Business hours and operational settings
- Tax rates and currency configuration

### 📋 Menu Items & Recipes
- Bulk upload menu items via CSV
- Individual menu item creation
- Recipe management with ingredient breakdowns
- Category organization and pricing

### 🥘 Ingredients Management
- Ingredient catalog with units and costs
- Stock level tracking (current, min, max)
- Supplier associations
- Cost per unit calculations

### 🏢 Supplier Setup
- Supplier contact information
- Specialties and product categories
- Payment terms and delivery schedules
- Contact person details

### 📦 Initial Stock Configuration
- Set starting inventory levels
- Cost tracking for initial purchases
- Supplier assignment for stock items
- Notes and documentation

## API Endpoints

### Session Management
- `POST /api/setup-wizard/create-session` - Create new setup session
- `GET /api/setup-wizard/session/{session_id}` - Get session details
- `DELETE /api/setup-wizard/session/{session_id}` - Delete session

### Step-by-Step Data Collection
- `POST /api/setup-wizard/restaurant-profile/{session_id}` - Save restaurant profile
- `POST /api/setup-wizard/menu-items/{session_id}` - Save menu items
- `POST /api/setup-wizard/ingredients/{session_id}` - Save ingredients
- `POST /api/setup-wizard/suppliers/{session_id}` - Save suppliers
- `POST /api/setup-wizard/initial-stock/{session_id}` - Save initial stock

### Progress & Validation
- `GET /api/setup-wizard/progress/{session_id}` - Get setup progress
- `GET /api/setup-wizard/validation/{session_id}/{step}` - Validate specific step

### Completion
- `POST /api/setup-wizard/complete/{session_id}` - Complete setup process

### CSV Upload & Templates
- `POST /api/setup-wizard/upload-csv` - Upload CSV data
- `POST /api/setup-wizard/upload-file` - Upload CSV file
- `GET /api/setup-wizard/templates/{file_type}` - Get CSV templates

## Data Models

### SetupWizardSession
```typescript
{
  session_id: string;
  current_step: SetupStep;
  completed_steps: SetupStep[];
  restaurant_profile?: RestaurantProfile;
  menu_items?: MenuItemUpload[];
  ingredients?: IngredientUpload[];
  suppliers?: SupplierUpload[];
  initial_stock?: InitialStockUpload[];
  is_completed: boolean;
  restaurant_id?: string;
  created_at: datetime;
  updated_at: datetime;
}
```

### RestaurantProfile
```typescript
{
  name: string;
  address: string;
  phone: string;
  email: string;
  owner_email: string;
  owner_name: string;
  cuisine_type: string;
  business_hours: Record<string, string>;
  tax_rate: number;
  currency: string;
}
```

### MenuItemUpload
```typescript
{
  name: string;
  description: string;
  price: number;
  category: string;
  is_available: boolean;
  ingredients: Array<{
    name: string;
    quantity: number;
    unit: string;
  }>;
}
```

### IngredientUpload
```typescript
{
  name: string;
  unit: string;
  current_stock: number;
  min_stock_level: number;
  max_stock_level?: number;
  cost_per_unit: number;
  supplier_name: string;
}
```

### SupplierUpload
```typescript
{
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  specialties: string[];
  payment_terms: string;
  delivery_schedule: string;
}
```

### InitialStockUpload
```typescript
{
  ingredient_id: string;
  quantity: number;
  cost: number;
  supplier_id?: string;
  notes: string;
}
```

## Setup Process

### Step 1: Restaurant Profile
1. Enter restaurant basic information
2. Add owner contact details
3. Configure business settings
4. Set tax rates and currency

### Step 2: Menu Items
1. Upload CSV file or add manually
2. Define menu categories
3. Set pricing and availability
4. Add ingredient breakdowns

### Step 3: Ingredients
1. Upload ingredients CSV or add manually
2. Set units and stock levels
3. Configure costs and suppliers
4. Define minimum stock alerts

### Step 4: Suppliers
1. Add supplier contact information
2. Define specialties and categories
3. Set payment terms
4. Configure delivery schedules

### Step 5: Initial Stock
1. Set starting inventory levels
2. Record initial purchase costs
3. Assign suppliers to stock items
4. Add notes and documentation

### Completion
1. Review all data for accuracy
2. Validate all steps
3. Complete setup process
4. Create restaurant and owner accounts

## CSV Templates

### Menu Items Template
```csv
name,description,price,category
Cappuccino,Classic Italian coffee drink,4.50,Beverages
Grilled Cheese,Classic grilled cheese sandwich,8.50,Food
```

### Ingredients Template
```csv
name,unit,current_stock,min_stock_level,max_stock_level,cost_per_unit,supplier_name
Coffee Beans,kg,15.5,5.0,50.0,12.50,Coffee Bean Co.
Milk,liters,8.0,3.0,20.0,2.50,Dairy Delights
```

### Suppliers Template
```csv
name,contact_person,email,phone,address,specialties
Coffee Bean Co.,John Smith,john@coffeebeanco.com,+1-555-0101,456 Coffee St,Coffee Beans,Sugar
Dairy Delights,Mary Johnson,mary@dairydelights.com,+1-555-0102,789 Milk Ave,Milk,Cheese
```

## Validation Rules

### Restaurant Profile
- Restaurant name is required
- Address is required
- Phone number is required
- Owner email is required
- Valid email format for all email fields

### Menu Items
- At least one menu item required
- Name is required for each item
- Price must be greater than 0
- Valid category assignment

### Ingredients
- At least one ingredient required
- Name is required for each ingredient
- Minimum stock level must be greater than 0
- Cost per unit cannot be negative
- Valid unit specification

### Suppliers
- Name is required for each supplier
- Email is required for each supplier
- Valid email format

### Initial Stock
- Quantity must be greater than 0
- Cost cannot be negative
- Valid ingredient association

## Security Considerations

### Authentication
- All endpoints require valid Firebase JWT token
- Super admin role verification
- Session-based access control

### Data Validation
- Input sanitization and validation
- Type checking for all data
- Business rule enforcement

### Error Handling
- Comprehensive error messages
- Graceful failure handling
- Data integrity protection

## Performance Optimization

### Caching
- Session data caching
- Template caching
- Validation result caching

### Batch Operations
- Bulk CSV processing
- Batch database operations
- Efficient data validation

### Progress Tracking
- Real-time progress updates
- Step completion tracking
- Validation status monitoring

## Usage Guide

### For Super Admins

1. **Access Setup Wizard**
   - Navigate to `/setup-wizard` in the application
   - Ensure you have super admin privileges

2. **Start New Setup**
   - Click "Create Session" to begin
   - Session ID will be generated automatically

3. **Complete Each Step**
   - Follow the step-by-step process
   - Use CSV upload for bulk data
   - Validate each step before proceeding

4. **Review and Complete**
   - Review all entered data
   - Fix any validation errors
   - Complete the setup process

### For Restaurant Owners

1. **Account Creation**
   - Owner account created automatically
   - Password reset email sent
   - Login credentials provided

2. **Data Verification**
   - Review all imported data
   - Verify menu items and recipes
   - Check ingredient stock levels

3. **System Access**
   - Full access to restaurant dashboard
   - Inventory management capabilities
   - Menu and recipe management

## Troubleshooting

### Common Issues

1. **Session Not Found**
   - Check session ID validity
   - Ensure proper authentication
   - Recreate session if needed

2. **CSV Upload Errors**
   - Verify CSV format and headers
   - Check data types and values
   - Ensure required fields are present

3. **Validation Failures**
   - Review error messages
   - Fix data inconsistencies
   - Re-validate after corrections

4. **Setup Completion Errors**
   - Check all required data
   - Verify database connectivity
   - Ensure proper permissions

### Error Messages

- `Session not found`: Invalid or expired session
- `Validation failed`: Data doesn't meet requirements
- `Authentication error`: Invalid or missing token
- `CSV processing error`: Invalid file format or data

## Future Enhancements

### Planned Features
- Multi-language support
- Advanced validation rules
- Integration with external systems
- Automated data verification
- Enhanced reporting and analytics

### Potential Improvements
- Real-time collaboration
- Template customization
- Advanced CSV processing
- Bulk operations optimization
- Enhanced error handling

## Support

For technical support or questions about the Setup Wizard:

1. Check the validation messages for specific errors
2. Review the CSV templates for correct format
3. Ensure all required fields are completed
4. Contact the development team for assistance

## Version History

- **v1.0.0**: Initial release with basic setup wizard
- **v1.1.0**: Added CSV upload functionality
- **v1.2.0**: Enhanced validation and error handling
- **v1.3.0**: Added progress tracking and completion summary

---

The Setup Wizard provides a streamlined onboarding experience for new restaurants, ensuring all necessary data is collected and validated before the restaurant becomes operational. 