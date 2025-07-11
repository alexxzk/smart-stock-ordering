import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
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
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Api as ApiIcon,
  Email as EmailIcon,
  PictureAsPdf as PdfIcon,
  Download as DownloadIcon,
  Send as SendIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ShoppingCart as CartIcon,
  Business as BusinessIcon,
  LocalShipping as ShippingIcon
} from '@mui/icons-material';

interface Supplier {
  id: string;
  name: string;
  description: string;
  integration_type: string;
  features: string[];
  categories: string[];
  minimum_order: number;
  delivery_lead_time: number;
  required_config: string[];
}

interface Product {
  product_id: string;
  name: string;
  description: string;
  price: number;
  unit: string;
  category: string;
  in_stock: boolean;
  min_order_qty: number;
  lead_time_days: number;
  last_updated: string;
}

interface OrderItem {
  product_id: string;
  name: string;
  quantity: number;
  unit: string;
  unit_price: number;
  notes: string;
}

interface Order {
  order_id: string;
  supplier_id: string;
  status: string;
  total_amount: number;
  delivery_date: string;
  created_at: string;
  type: string;
}

const SupplierAPIIntegrations: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [selectedSupplier, setSelectedSupplier] = useState<string>('');
  const [products, setProducts] = useState<Product[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Configuration dialog
  const [showConfigDialog, setShowConfigDialog] = useState(false);
  const [configSupplier, setConfigSupplier] = useState<string>('');
  const [configData, setConfigData] = useState({
    api_key: '',
    location_id: '',
    account_number: '',
    restaurant_id: ''
  });
  
  // Order dialog
  const [showOrderDialog, setShowOrderDialog] = useState(false);
  const [orderType, setOrderType] = useState<'api' | 'pdf' | 'email'>('api');
  const [orderData, setOrderData] = useState({
    supplier_id: '',
    supplier_name: '',
    supplier_email: '',
    items: [] as OrderItem[],
    delivery_address: '',
    delivery_date: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    notes: '',
    urgent: false
  });
  
  // Active tab
  const [activeTab, setActiveTab] = useState(0);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    loadSuppliers();
    loadOrders();
  }, []);

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/supplier-api-integrations/suppliers`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuppliers(Object.values(data.suppliers));
      } else {
        setError('Failed to load suppliers');
      }
    } catch (error) {
      setError('Error loading suppliers');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOrders = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/supplier-api-integrations/orders`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrders(data.orders);
      }
    } catch (error) {
      console.error('Error loading orders:', error);
    }
  };

  const configureSupplier = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/supplier-api-integrations/configure`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          supplier_id: configSupplier,
          ...configData
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuccess(`Integration configured successfully for ${data.supplier_id}`);
        setShowConfigDialog(false);
        resetConfigData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to configure integration');
      }
    } catch (error) {
      setError('Error configuring integration');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProducts = async (supplierId: string, category?: string) => {
    try {
      setLoading(true);
      const url = new URL(`${API_BASE_URL}/api/supplier-api-integrations/products/${supplierId}`);
      if (category) {
        url.searchParams.append('category', category);
      }
      
      const response = await fetch(url.toString(), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products);
        setSelectedSupplier(supplierId);
      } else {
        setError('Failed to load products');
      }
    } catch (error) {
      setError('Error loading products');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const placeOrder = async () => {
    try {
      setLoading(true);
      let endpoint = '';
      let requestData = {};
      
      if (orderType === 'api') {
        endpoint = '/order';
        requestData = {
          supplier_id: orderData.supplier_id,
          items: orderData.items,
          delivery_address: orderData.delivery_address,
          delivery_date: orderData.delivery_date,
          contact_person: orderData.contact_person,
          contact_phone: orderData.contact_phone,
          contact_email: orderData.contact_email,
          notes: orderData.notes,
          urgent: orderData.urgent
        };
      } else if (orderType === 'pdf') {
        endpoint = '/order-sheet/pdf';
        requestData = {
          supplier_name: orderData.supplier_name,
          items: orderData.items,
          delivery_address: orderData.delivery_address,
          delivery_date: orderData.delivery_date,
          contact_person: orderData.contact_person,
          contact_phone: orderData.contact_phone,
          contact_email: orderData.contact_email,
          notes: orderData.notes,
          urgent: orderData.urgent
        };
      } else if (orderType === 'email') {
        endpoint = '/order-sheet/email';
        requestData = {
          supplier_name: orderData.supplier_name,
          supplier_email: orderData.supplier_email,
          items: orderData.items,
          delivery_address: orderData.delivery_address,
          delivery_date: orderData.delivery_date,
          contact_person: orderData.contact_person,
          contact_phone: orderData.contact_phone,
          contact_email: orderData.contact_email,
          notes: orderData.notes,
          urgent: orderData.urgent
        };
      }
      
      const response = await fetch(`${API_BASE_URL}/api/supplier-api-integrations${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuccess(`Order placed successfully! Order ID: ${data.order_id}`);
        setShowOrderDialog(false);
        resetOrderData();
        loadOrders();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to place order');
      }
    } catch (error) {
      setError('Error placing order');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (supplierId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/supplier-api-integrations/test-connection/${supplierId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuccess(`Connection test successful for ${supplierId}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Connection test failed');
      }
    } catch (error) {
      setError('Error testing connection');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetConfigData = () => {
    setConfigData({
      api_key: '',
      location_id: '',
      account_number: '',
      restaurant_id: ''
    });
    setConfigSupplier('');
  };

  const resetOrderData = () => {
    setOrderData({
      supplier_id: '',
      supplier_name: '',
      supplier_email: '',
      items: [],
      delivery_address: '',
      delivery_date: '',
      contact_person: '',
      contact_phone: '',
      contact_email: '',
      notes: '',
      urgent: false
    });
  };

  const addOrderItem = () => {
    setOrderData(prev => ({
      ...prev,
      items: [...prev.items, {
        product_id: '',
        name: '',
        quantity: 1,
        unit: 'kg',
        unit_price: 0,
        notes: ''
      }]
    }));
  };

  const updateOrderItem = (index: number, field: string, value: any) => {
    setOrderData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const removeOrderItem = (index: number) => {
    setOrderData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const getSupplierIcon = (type: string) => {
    switch (type) {
      case 'api':
        return <ApiIcon color="primary" />;
      case 'manual':
        return <BusinessIcon color="secondary" />;
      default:
        return <InfoIcon color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
      case 'completed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Supplier API Integrations
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Connect with supplier APIs for automated ordering and real-time pricing
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

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Available Suppliers" />
        <Tab label="Products" />
        <Tab label="Orders" />
        <Tab label="Configuration" />
      </Tabs>

      {/* Available Suppliers Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {suppliers.map((supplier) => (
            <Grid item xs={12} md={6} lg={4} key={supplier.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getSupplierIcon(supplier.integration_type)}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      {supplier.name}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    {supplier.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Features:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {supplier.features.map((feature) => (
                        <Chip
                          key={feature}
                          label={feature.replace(/_/g, ' ')}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>Min Order:</strong> ${supplier.minimum_order}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Lead Time:</strong> {supplier.delivery_lead_time} days
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => {
                        setConfigSupplier(supplier.id);
                        setShowConfigDialog(true);
                      }}
                    >
                      Configure
                    </Button>
                    
                    {supplier.integration_type === 'api' && (
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => testConnection(supplier.id)}
                        disabled={loading}
                      >
                        Test
                      </Button>
                    )}
                    
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => getProducts(supplier.id)}
                      disabled={loading}
                    >
                      View Products
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Products Tab */}
      {activeTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Products - {selectedSupplier || 'Select a supplier'}
            </Typography>
            
            {selectedSupplier && (
              <Button
                variant="contained"
                startIcon={<CartIcon />}
                onClick={() => {
                  setOrderType('api');
                  setOrderData(prev => ({ ...prev, supplier_id: selectedSupplier }));
                  setShowOrderDialog(true);
                }}
              >
                Place Order
              </Button>
            )}
          </Box>
          
          {products.length > 0 ? (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>Stock</TableCell>
                    <TableCell>Min Order</TableCell>
                    <TableCell>Lead Time</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {products.map((product) => (
                    <TableRow key={product.product_id}>
                      <TableCell>{product.name}</TableCell>
                      <TableCell>{product.category}</TableCell>
                      <TableCell>${product.price}</TableCell>
                      <TableCell>{product.unit}</TableCell>
                      <TableCell>
                        <Chip
                          label={product.in_stock ? 'In Stock' : 'Out of Stock'}
                          color={product.in_stock ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{product.min_order_qty}</TableCell>
                      <TableCell>{product.lead_time_days} days</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Alert severity="info">
              No products loaded. Select a supplier to view products.
            </Alert>
          )}
        </Box>
      )}

      {/* Orders Tab */}
      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Order History
          </Typography>
          
          {orders.length > 0 ? (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Order ID</TableCell>
                    <TableCell>Supplier</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Total</TableCell>
                    <TableCell>Delivery Date</TableCell>
                    <TableCell>Created</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.map((order) => (
                    <TableRow key={order.order_id}>
                      <TableCell>{order.order_id}</TableCell>
                      <TableCell>{order.supplier_id}</TableCell>
                      <TableCell>
                        <Chip
                          label={order.type}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={order.status}
                          color={getStatusColor(order.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>${order.total_amount}</TableCell>
                      <TableCell>{new Date(order.delivery_date).toLocaleDateString()}</TableCell>
                      <TableCell>{new Date(order.created_at).toLocaleDateString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Alert severity="info">
              No orders found.
            </Alert>
          )}
        </Box>
      )}

      {/* Configuration Tab */}
      {activeTab === 3 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            API Configuration
          </Typography>
          
          <Card>
            <CardContent>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Configure API credentials for supplier integrations. Contact your suppliers to obtain API access.
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Supplier</InputLabel>
                    <Select
                      value={configSupplier}
                      onChange={(e) => setConfigSupplier(e.target.value)}
                    >
                      {suppliers.filter(s => s.integration_type === 'api').map((supplier) => (
                        <MenuItem key={supplier.id} value={supplier.id}>
                          {supplier.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="API Key"
                    value={configData.api_key}
                    onChange={(e) => setConfigData({ ...configData, api_key: e.target.value })}
                    type="password"
                  />
                </Grid>
                
                {configSupplier === 'bidfood' && (
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Location ID"
                      value={configData.location_id}
                      onChange={(e) => setConfigData({ ...configData, location_id: e.target.value })}
                    />
                  </Grid>
                )}
                
                {configSupplier === 'pfd' && (
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Account Number"
                      value={configData.account_number}
                      onChange={(e) => setConfigData({ ...configData, account_number: e.target.value })}
                    />
                  </Grid>
                )}
                
                {configSupplier === 'ordermentum' && (
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Restaurant ID"
                      value={configData.restaurant_id}
                      onChange={(e) => setConfigData({ ...configData, restaurant_id: e.target.value })}
                    />
                  </Grid>
                )}
              </Grid>
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  onClick={configureSupplier}
                  disabled={!configSupplier || !configData.api_key || loading}
                >
                  {loading ? <CircularProgress size={20} /> : 'Configure Integration'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Configuration Dialog */}
      <Dialog open={showConfigDialog} onClose={() => setShowConfigDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Configure {configSupplier} Integration</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Enter your API credentials for {configSupplier}. Contact your supplier to obtain these credentials.
          </Typography>
          
          <TextField
            fullWidth
            label="API Key"
            value={configData.api_key}
            onChange={(e) => setConfigData({ ...configData, api_key: e.target.value })}
            type="password"
            sx={{ mb: 2 }}
          />
          
          {configSupplier === 'bidfood' && (
            <TextField
              fullWidth
              label="Location ID"
              value={configData.location_id}
              onChange={(e) => setConfigData({ ...configData, location_id: e.target.value })}
              sx={{ mb: 2 }}
            />
          )}
          
          {configSupplier === 'pfd' && (
            <TextField
              fullWidth
              label="Account Number"
              value={configData.account_number}
              onChange={(e) => setConfigData({ ...configData, account_number: e.target.value })}
              sx={{ mb: 2 }}
            />
          )}
          
          {configSupplier === 'ordermentum' && (
            <TextField
              fullWidth
              label="Restaurant ID"
              value={configData.restaurant_id}
              onChange={(e) => setConfigData({ ...configData, restaurant_id: e.target.value })}
              sx={{ mb: 2 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfigDialog(false)}>Cancel</Button>
          <Button
            onClick={configureSupplier}
            variant="contained"
            disabled={!configData.api_key || loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Configure'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Order Dialog */}
      <Dialog open={showOrderDialog} onClose={() => setShowOrderDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Place Order - {orderType === 'api' ? 'API Order' : orderType === 'pdf' ? 'PDF Order Sheet' : 'Email Order'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Order Type</InputLabel>
                <Select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value as any)}
                >
                  <MenuItem value="api">API Order</MenuItem>
                  <MenuItem value="pdf">PDF Order Sheet</MenuItem>
                  <MenuItem value="email">Email Order</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {orderType === 'api' ? (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Supplier</InputLabel>
                  <Select
                    value={orderData.supplier_id}
                    onChange={(e) => setOrderData({ ...orderData, supplier_id: e.target.value })}
                  >
                    {suppliers.filter(s => s.integration_type === 'api').map((supplier) => (
                      <MenuItem key={supplier.id} value={supplier.id}>
                        {supplier.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            ) : (
              <>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Supplier Name"
                    value={orderData.supplier_name}
                    onChange={(e) => setOrderData({ ...orderData, supplier_name: e.target.value })}
                  />
                </Grid>
                
                {orderType === 'email' && (
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Supplier Email"
                      value={orderData.supplier_email}
                      onChange={(e) => setOrderData({ ...orderData, supplier_email: e.target.value })}
                      type="email"
                    />
                  </Grid>
                )}
              </>
            )}
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1">Order Items</Typography>
                <Button startIcon={<AddIcon />} onClick={addOrderItem}>
                  Add Item
                </Button>
              </Box>
              
              {orderData.items.map((item, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                  <TextField
                    label="Product Name"
                    value={item.name}
                    onChange={(e) => updateOrderItem(index, 'name', e.target.value)}
                    sx={{ flexGrow: 1 }}
                  />
                  <TextField
                    label="Quantity"
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateOrderItem(index, 'quantity', parseInt(e.target.value))}
                    sx={{ width: 100 }}
                  />
                  <TextField
                    label="Unit"
                    value={item.unit}
                    onChange={(e) => updateOrderItem(index, 'unit', e.target.value)}
                    sx={{ width: 80 }}
                  />
                  <TextField
                    label="Unit Price"
                    type="number"
                    value={item.unit_price}
                    onChange={(e) => updateOrderItem(index, 'unit_price', parseFloat(e.target.value))}
                    sx={{ width: 120 }}
                  />
                  <IconButton onClick={() => removeOrderItem(index)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Delivery Address"
                value={orderData.delivery_address}
                onChange={(e) => setOrderData({ ...orderData, delivery_address: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Delivery Date"
                type="date"
                value={orderData.delivery_date}
                onChange={(e) => setOrderData({ ...orderData, delivery_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Contact Person"
                value={orderData.contact_person}
                onChange={(e) => setOrderData({ ...orderData, contact_person: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Contact Phone"
                value={orderData.contact_phone}
                onChange={(e) => setOrderData({ ...orderData, contact_phone: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Contact Email"
                value={orderData.contact_email}
                onChange={(e) => setOrderData({ ...orderData, contact_email: e.target.value })}
                type="email"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                value={orderData.notes}
                onChange={(e) => setOrderData({ ...orderData, notes: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowOrderDialog(false)}>Cancel</Button>
          <Button
            onClick={placeOrder}
            variant="contained"
            disabled={loading || orderData.items.length === 0}
          >
            {loading ? <CircularProgress size={20} /> : 'Place Order'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SupplierAPIIntegrations; 