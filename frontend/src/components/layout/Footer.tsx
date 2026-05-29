import React from 'react';
import { Box, Container, Typography, Grid, Link, Divider } from '@mui/material';
import { Phone, Email, LocationOn } from '@mui/icons-material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        bgcolor: 'primary.dark',
        color: 'white',
        py: 4,
        mt: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              🏆 ADRENALINE STORE
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Your one-stop destination for premium sports gear, jerseys, and accessories.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Quick Links
            </Typography>
            <Link href="/products" color="inherit" display="block" sx={{ opacity: 0.8, mb: 0.5 }}>
              All Products
            </Link>
            <Link href="/offers" color="inherit" display="block" sx={{ opacity: 0.8, mb: 0.5 }}>
              Offers & Events
            </Link>
            <Link href="/cart" color="inherit" display="block" sx={{ opacity: 0.8 }}>
              My Cart
            </Link>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Contact Us
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, opacity: 0.8 }}>
              <Phone fontSize="small" />
              <Typography variant="body2">+91 XXXXXXXXXX</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, opacity: 0.8 }}>
              <Email fontSize="small" />
              <Typography variant="body2">info@adrenalinestore.com</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, opacity: 0.8 }}>
              <LocationOn fontSize="small" />
              <Typography variant="body2">Sports City, India</Typography>
            </Box>
          </Grid>
        </Grid>
        <Divider sx={{ my: 3, borderColor: 'rgba(255,255,255,0.2)' }} />
        <Typography variant="body2" textAlign="center" sx={{ opacity: 0.6 }}>
          © {new Date().getFullYear()} Adrenaline Sports Store. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
