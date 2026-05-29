import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  IconButton,
  Button,
  Divider,
  Grid,
  TextField,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { Add, Remove, Delete, ShoppingBag } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';

const CartPage: React.FC = () => {
  const navigate = useNavigate();
  const { items, updateQuantity, removeFromCart, getTotal, clearCart } = useCart();
  const { isAuthenticated, user } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [address, setAddress] = useState({
    address: user?.address || '',
    city: user?.city || '',
    state: user?.state || '',
    zip_code: user?.zip_code || '',
  });

  const steps = ['Cart', 'Delivery Address', 'Confirm Order'];

  const handleContinueToBuy = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setActiveStep(1);
  };

  const isAddressValid = () => {
    return address.address && address.city && address.state && address.zip_code;
  };

  const handlePlaceOrder = () => {
    const whatsappNumber = import.meta.env.VITE_WHATSAPP_NUMBER || '919999999999';
    const orderItems = items
      .map((item) => `• ${item.product.name} (x${item.quantity}) - ₹${(item.product.offer_price || item.product.selling_price) * item.quantity}`)
      .join('\n');
    const message = `🛒 *New Order*\n\n${orderItems}\n\n💰 *Total: ₹${getTotal()}*\n\n📍 *Delivery Address:*\n${address.address}, ${address.city}, ${address.state} - ${address.zip_code}\n\n👤 *Customer:* ${user?.first_name} ${user?.last_name}\n📱 *Mobile:* ${user?.mobile}`;
    const encodedMessage = encodeURIComponent(message);
    window.open(`https://wa.me/${whatsappNumber}?text=${encodedMessage}`, '_blank');
    clearCart();
    setActiveStep(0);
    navigate('/');
  };

  if (items.length === 0 && activeStep === 0) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <ShoppingBag sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          Your cart is empty
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Browse our products and add items to your cart
        </Typography>
        <Button variant="contained" onClick={() => navigate('/products')}>
          Browse Products
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Shopping Cart
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {activeStep === 0 && (
        <>
          {items.map((item) => (
            <Paper key={item.product.id} sx={{ p: 2, mb: 2 }}>
              <Grid container alignItems="center" spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {item.product.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.product.category?.name}
                    {item.selectedSize && ` | Size: ${item.selectedSize}`}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Typography variant="h6" color="primary">
                    ₹{item.product.offer_price || item.product.selling_price}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <IconButton
                      size="small"
                      onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                    >
                      <Remove />
                    </IconButton>
                    <Typography fontWeight={600}>{item.quantity}</Typography>
                    <IconButton
                      size="small"
                      onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                    >
                      <Add />
                    </IconButton>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={2} sx={{ textAlign: 'right' }}>
                  <IconButton color="error" onClick={() => removeFromCart(item.product.id)}>
                    <Delete />
                  </IconButton>
                </Grid>
              </Grid>
            </Paper>
          ))}

          <Divider sx={{ my: 3 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5" fontWeight={700}>
              Total: ₹{getTotal()}
            </Typography>
            <Button variant="contained" size="large" onClick={handleContinueToBuy}>
              Continue to Buy
            </Button>
          </Box>
        </>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Delivery Address
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                value={address.address}
                onChange={(e) => setAddress({ ...address, address: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="City"
                value={address.city}
                onChange={(e) => setAddress({ ...address, city: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="State"
                value={address.state}
                onChange={(e) => setAddress({ ...address, state: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="ZIP Code"
                value={address.zip_code}
                onChange={(e) => setAddress({ ...address, zip_code: e.target.value })}
                required
              />
            </Grid>
          </Grid>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button onClick={() => setActiveStep(0)}>Back</Button>
            <Button
              variant="contained"
              disabled={!isAddressValid()}
              onClick={() => setActiveStep(2)}
            >
              Continue
            </Button>
          </Box>
        </Paper>
      )}

      {activeStep === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Order Summary
          </Typography>
          {items.map((item) => (
            <Box key={item.product.id} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography>
                {item.product.name} x{item.quantity}
              </Typography>
              <Typography fontWeight={600}>
                ₹{(item.product.offer_price || item.product.selling_price) * item.quantity}
              </Typography>
            </Box>
          ))}
          <Divider sx={{ my: 2 }} />
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6" fontWeight={700}>Total</Typography>
            <Typography variant="h6" fontWeight={700}>₹{getTotal()}</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            📍 {address.address}, {address.city}, {address.state} - {address.zip_code}
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button onClick={() => setActiveStep(1)}>Back</Button>
            <Button variant="contained" color="success" onClick={handlePlaceOrder}>
              Place Order via WhatsApp
            </Button>
          </Box>
        </Paper>
      )}
    </Container>
  );
};

export default CartPage;
