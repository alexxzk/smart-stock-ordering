import React, { useState, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  Card,
  CardContent,
  TextField,
  Grid,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Restaurant as RestaurantIcon,
  MenuBook as MenuIcon,
  Inventory as InventoryIcon,
  Business as BusinessIcon,
  Storage as StorageIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Edit as EditIcon
} from '@mui/icons-material';

interface RestaurantProfile {
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

interface MenuItem {
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

interface Ingredient {
  name: string;
  unit: string;
  current_stock: number;
  min_stock_level: number;
  max_stock_level?: number;
  cost_per_unit: number;
  supplier_name: string;
}

interface Supplier {
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  specialties: string[];
  payment_terms: string;
  delivery_schedule: string;
}

interface InitialStock {
  ingredient_id: string;
  quantity: number;
  cost: number;
  supplier_id?: string;
  notes: string;
}

const steps = [
  {
    label: 'Restaurant Profile',
    icon: <RestaurantIcon />,
    description: 'Add restaurant details and owner information'
  },
  {
    label: 'Menu Items',
    icon: <MenuIcon />,
    description: 'Upload menu items with recipes and ingredients'
  },
  {
    label: 'Ingredients',
    icon: <InventoryIcon />,
    description: 'Add ingredients with costs and stock levels'
  },
  {
    label: 'Suppliers',
    icon: <BusinessIcon />,
    description: 'Set up supplier contacts and specialties'
  },
  {
    label: 'Initial Stock',
    icon: <StorageIcon />,
    description: 'Set initial stock levels and costs'
  }
];

const SetupWizard: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form data
  const [restaurantProfile, setRestaurantProfile] = useState<RestaurantProfile>({
    name: '',
    address: '',
    phone: '',
    email: '',
    owner_email: '',
    owner_name: '',
    cuisine_type: '',
    business_hours: {},
    tax_rate: 0.0,
    currency: 'USD'
  });
  
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [initialStock, setInitialStock] = useState<InitialStock[]>([]);
  
  // CSV upload
  const [showCsvDialog, setShowCsvDialog] = useState(false);
  const [csvFileType, setCsvFileType] = useState('');
  const [csvData, setCsvData] = useState('');
  
  // Validation
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [validationWarnings, setValidationWarnings] = useState<string[]>([]);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    createSession();
  }, []);

  const createSession = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/setup-wizard/create-session`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setSuccess('Setup session created successfully');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create session');
      }
    } catch (error) {
      setError('Error creating setup session');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (activeStep === steps.length - 1) {
      await completeSetup();
    } else {
      await saveCurrentStep();
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setRestaurantProfile({
      name: '',
      address: '',
      phone: '',
      email: '',
      owner_email: '',
      owner_name: '',
      cuisine_type: '',
      business_hours: {},
      tax_rate: 0.0,
      currency: 'USD'
    });
    setMenuItems([]);
    setIngredients([]);
    setSuppliers([]);
    setInitialStock([]);
  };

  const saveCurrentStep = async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      let response;

      switch (activeStep) {
        case 0: // Restaurant Profile
          response = await fetch(`${API_BASE_URL}/api/setup-wizard/restaurant-profile/${sessionId}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(restaurantProfile)
          });
          break;

        case 1: // Menu Items
          response = await fetch(`${API_BASE_URL}/api/setup-wizard/menu-items/${sessionId}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(menuItems)
          });
          break;

        case 2: // Ingredients
          response = await fetch(`${API_BASE_URL}/api/setup-wizard/ingredients/${sessionId}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(ingredients)
          });
          break;

        case 3: // Suppliers
          response = await fetch(`${API_BASE_URL}/api/setup-wizard/suppliers/${sessionId}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(suppliers)
          });
          break;

        case 4: // Initial Stock
          response = await fetch(`${API_BASE_URL}/api/setup-wizard/initial-stock/${sessionId}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(initialStock)
          });
          break;
      }

      if (response && response.ok) {
        const data = await response.json();
        if (data.is_valid) {
          setSuccess(`Step ${activeStep + 1} saved successfully`);
          setValidationErrors(data.errors || []);
          setValidationWarnings(data.warnings || []);
        } else {
          setError('Validation failed');
          setValidationErrors(data.errors || []);
          setValidationWarnings(data.warnings || []);
        }
      }
    } catch (error) {
      setError('Error saving step');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeSetup = async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/setup-wizard/complete/${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess('Restaurant setup completed successfully!');
        // Show completion summary
        console.log('Setup completed:', data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to complete setup');
      }
    } catch (error) {
      setError('Error completing setup');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCsvUpload = async () => {
    if (!sessionId || !csvData.trim()) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/setup-wizard/upload-csv`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          file_type: csvFileType,
          csv_data: csvData,
          has_headers: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSuccess(`CSV uploaded successfully: ${data.records_processed} records processed`);
          setShowCsvDialog(false);
          setCsvData('');
        } else {
          setError(`CSV upload failed: ${data.errors.join(', ')}`);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to upload CSV');
      }
    } catch (error) {
      setError('Error uploading CSV');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = async (fileType: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/setup-wizard/templates/${fileType}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        // Create and download CSV file
        const blob = new Blob([data.csv_content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileType}_template.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      setError('Error downloading template');
      console.error('Error:', error);
    }
  };

  const renderRestaurantProfile = () => (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Restaurant Profile
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Restaurant Name"
            value={restaurantProfile.name}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, name: e.target.value})}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Cuisine Type"
            value={restaurantProfile.cuisine_type}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, cuisine_type: e.target.value})}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Address"
            value={restaurantProfile.address}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, address: e.target.value})}
            margin="normal"
            multiline
            rows={2}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Phone"
            value={restaurantProfile.phone}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, phone: e.target.value})}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={restaurantProfile.email}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, email: e.target.value})}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Owner Name"
            value={restaurantProfile.owner_name}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, owner_name: e.target.value})}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Owner Email"
            type="email"
            value={restaurantProfile.owner_email}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, owner_email: e.target.value})}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Tax Rate"
            type="number"
            value={restaurantProfile.tax_rate}
            onChange={(e) => setRestaurantProfile({...restaurantProfile, tax_rate: parseFloat(e.target.value) || 0})}
            margin="normal"
            inputProps={{ step: 0.01, min: 0, max: 1 }}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Currency</InputLabel>
            <Select
              value={restaurantProfile.currency}
              onChange={(e) => setRestaurantProfile({...restaurantProfile, currency: e.target.value})}
            >
              <MenuItem value="USD">USD ($)</MenuItem>
              <MenuItem value="EUR">EUR (€)</MenuItem>
              <MenuItem value="GBP">GBP (£)</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );

  const renderMenuItems = () => (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Menu Items
        </Typography>
        <Box>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => downloadTemplate('menu_items')}
            sx={{ mr: 1 }}
          >
            Download Template
          </Button>
          <Button
            startIcon={<UploadIcon />}
            onClick={() => {
              setCsvFileType('menu_items');
              setShowCsvDialog(true);
            }}
          >
            Upload CSV
          </Button>
        </Box>
      </Box>
      
      {menuItems.length === 0 ? (
        <Alert severity="info">
          No menu items added yet. Add items manually or upload a CSV file.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Ingredients</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {menuItems.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.category}</TableCell>
                  <TableCell>${item.price}</TableCell>
                  <TableCell>{item.ingredients.length} ingredients</TableCell>
                  <TableCell>
                    <IconButton size="small">
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="error">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );

  const renderIngredients = () => (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Ingredients
        </Typography>
        <Box>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => downloadTemplate('ingredients')}
            sx={{ mr: 1 }}
          >
            Download Template
          </Button>
          <Button
            startIcon={<UploadIcon />}
            onClick={() => {
              setCsvFileType('ingredients');
              setShowCsvDialog(true);
            }}
          >
            Upload CSV
          </Button>
        </Box>
      </Box>
      
      {ingredients.length === 0 ? (
        <Alert severity="info">
          No ingredients added yet. Add ingredients manually or upload a CSV file.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Unit</TableCell>
                <TableCell>Current Stock</TableCell>
                <TableCell>Min Stock</TableCell>
                <TableCell>Cost/Unit</TableCell>
                <TableCell>Supplier</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ingredients.map((ingredient, index) => (
                <TableRow key={index}>
                  <TableCell>{ingredient.name}</TableCell>
                  <TableCell>{ingredient.unit}</TableCell>
                  <TableCell>{ingredient.current_stock}</TableCell>
                  <TableCell>{ingredient.min_stock_level}</TableCell>
                  <TableCell>${ingredient.cost_per_unit}</TableCell>
                  <TableCell>{ingredient.supplier_name}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );

  const renderSuppliers = () => (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Suppliers
        </Typography>
        <Box>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => downloadTemplate('suppliers')}
            sx={{ mr: 1 }}
          >
            Download Template
          </Button>
          <Button
            startIcon={<UploadIcon />}
            onClick={() => {
              setCsvFileType('suppliers');
              setShowCsvDialog(true);
            }}
          >
            Upload CSV
          </Button>
        </Box>
      </Box>
      
      {suppliers.length === 0 ? (
        <Alert severity="info">
          No suppliers added yet. Add suppliers manually or upload a CSV file.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Contact Person</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell>Specialties</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {suppliers.map((supplier, index) => (
                <TableRow key={index}>
                  <TableCell>{supplier.name}</TableCell>
                  <TableCell>{supplier.contact_person}</TableCell>
                  <TableCell>{supplier.email}</TableCell>
                  <TableCell>{supplier.phone}</TableCell>
                  <TableCell>
                    {supplier.specialties.map((specialty, i) => (
                      <Chip key={i} label={specialty} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );

  const renderInitialStock = () => (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Initial Stock Levels
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Set initial stock levels for your ingredients. This will be used as the starting inventory.
      </Alert>
      
      {ingredients.length === 0 ? (
        <Alert severity="warning">
          No ingredients available. Please add ingredients first.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Ingredient</TableCell>
                <TableCell>Unit</TableCell>
                <TableCell>Initial Quantity</TableCell>
                <TableCell>Cost</TableCell>
                <TableCell>Supplier</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {ingredients.map((ingredient, index) => (
                <TableRow key={index}>
                  <TableCell>{ingredient.name}</TableCell>
                  <TableCell>{ingredient.unit}</TableCell>
                  <TableCell>
                    <TextField
                      type="number"
                      size="small"
                      defaultValue={ingredient.current_stock}
                      inputProps={{ min: 0 }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      type="number"
                      size="small"
                      defaultValue={ingredient.cost_per_unit}
                      inputProps={{ min: 0, step: 0.01 }}
                    />
                  </TableCell>
                  <TableCell>{ingredient.supplier_name}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderRestaurantProfile();
      case 1:
        return renderMenuItems();
      case 2:
        return renderIngredients();
      case 3:
        return renderSuppliers();
      case 4:
        return renderInitialStock();
      default:
        return null;
    }
  };

  if (loading && !sessionId) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Restaurant Setup Wizard
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Complete the setup process to get your restaurant up and running quickly.
      </Typography>

      {/* Success/Error Messages */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Validation Messages */}
      {validationErrors.length > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Validation Errors:</Typography>
          <List dense>
            {validationErrors.map((error, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <WarningIcon color="error" />
                </ListItemIcon>
                <ListItemText primary={error} />
              </ListItem>
            ))}
          </List>
        </Alert>
      )}

      {validationWarnings.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Warnings:</Typography>
          <List dense>
            {validationWarnings.map((warning, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <InfoIcon color="warning" />
                </ListItemIcon>
                <ListItemText primary={warning} />
              </ListItem>
            ))}
          </List>
        </Alert>
      )}

      {/* Stepper */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel
                  StepIconComponent={() => step.icon}
                  optional={
                    <Typography variant="caption" color="textSecondary">
                      {step.description}
                    </Typography>
                  }
                >
                  {step.label}
                </StepLabel>
                <StepContent>
                  {renderStepContent(index)}
                  <Box sx={{ mb: 2, mt: 2 }}>
                    <div>
                      <Button
                        variant="contained"
                        onClick={handleNext}
                        sx={{ mt: 1, mr: 1 }}
                        disabled={loading}
                      >
                        {index === steps.length - 1 ? 'Complete Setup' : 'Continue'}
                      </Button>
                      <Button
                        disabled={index === 0}
                        onClick={handleBack}
                        sx={{ mt: 1, mr: 1 }}
                      >
                        Back
                      </Button>
                    </div>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      {/* CSV Upload Dialog */}
      <Dialog open={showCsvDialog} onClose={() => setShowCsvDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Upload CSV File
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Upload a CSV file with {csvFileType} data. Make sure the file has the correct headers.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={10}
            label="CSV Data"
            value={csvData}
            onChange={(e) => setCsvData(e.target.value)}
            placeholder="Paste your CSV data here..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCsvDialog(false)}>
            Cancel
          </Button>
          <Button onClick={handleCsvUpload} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
        <Button onClick={handleReset} color="secondary">
          Reset Setup
        </Button>
      </Box>
    </Box>
  );
};

export default SetupWizard; 