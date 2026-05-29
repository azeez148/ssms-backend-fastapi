import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Button,
  Skeleton,
} from '@mui/material';
import { ArrowForward, LocalOffer } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Product, OfferData } from '../types';
import { productService } from '../services/productService';
import { ProductCard } from '../components/common';
import { useCart } from '../context/CartContext';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [offers, setOffers] = useState<OfferData[]>([]);
  const [weeklyOffers, setWeeklyOffers] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [homeData, offersData, weeklyData] = await Promise.all([
          productService.getHomeData(),
          productService.getActiveOffers(),
          productService.getWeeklyOffers(),
        ]);
        setProducts(homeData.products || []);
        setOffers(offersData || []);
        setWeeklyOffers(weeklyData || []);
      } catch (error) {
        console.error('Failed to load home data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <Box>
      {/* Hero Banner */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1a237e 0%, #534bae 100%)',
          color: 'white',
          py: { xs: 6, md: 10 },
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" fontWeight={700} gutterBottom>
            Gear Up for Victory 🏆
          </Typography>
          <Typography variant="h5" sx={{ opacity: 0.9, mb: 4 }}>
            Premium sports gear, jerseys & accessories at the best prices
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            size="large"
            endIcon={<ArrowForward />}
            onClick={() => navigate('/products')}
          >
            Shop Now
          </Button>
        </Container>
      </Box>

      {/* Active Offers Banner */}
      {offers.length > 0 && (
        <Container maxWidth="lg" sx={{ mt: -3, position: 'relative', zIndex: 1 }}>
          <Paper
            sx={{
              p: 3,
              background: 'linear-gradient(90deg, #ff6f00, #ff8f00)',
              color: 'white',
              borderRadius: 3,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <LocalOffer sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h5" fontWeight={700}>
                    {offers[0]?.name || 'Special Offers'}
                  </Typography>
                  <Typography variant="body1">
                    {offers[0]?.description || 'Check out our latest deals!'}
                  </Typography>
                </Box>
              </Box>
              <Button
                variant="contained"
                sx={{ bgcolor: 'white', color: '#ff6f00', '&:hover': { bgcolor: '#f5f5f5' } }}
                onClick={() => navigate('/offers')}
              >
                View All Offers
              </Button>
            </Box>
          </Paper>
        </Container>
      )}

      {/* New Products Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" fontWeight={700}>
            New Arrivals
          </Typography>
          <Button endIcon={<ArrowForward />} onClick={() => navigate('/products')}>
            View All
          </Button>
        </Box>
        <Grid container spacing={3}>
          {loading
            ? Array.from({ length: 4 }).map((_, i) => (
                <Grid item xs={12} sm={6} md={3} key={i}>
                  <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
                </Grid>
              ))
            : products.slice(0, 8).map((product) => (
                <Grid item xs={12} sm={6} md={3} key={product.id}>
                  <ProductCard product={product} onAddToCart={addToCart} />
                </Grid>
              ))}
        </Grid>
      </Container>

      {/* Weekly Offers Section */}
      {weeklyOffers.length > 0 && (
        <Box sx={{ bgcolor: '#f0f4ff', py: 6 }}>
          <Container maxWidth="lg">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h4" fontWeight={700}>
                🔥 Weekly Offers
              </Typography>
              <Button endIcon={<ArrowForward />} onClick={() => navigate('/offers')}>
                View All
              </Button>
            </Box>
            <Grid container spacing={3}>
              {weeklyOffers.slice(0, 4).map((product) => (
                <Grid item xs={12} sm={6} md={3} key={product.id}>
                  <ProductCard product={product} onAddToCart={addToCart} />
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>
      )}

      {/* Reviews Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h4" fontWeight={700} textAlign="center" gutterBottom>
          What Our Customers Say
        </Typography>
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {[
            { name: 'Rahul S.', review: 'Amazing quality jerseys! Fast delivery and great prices.', rating: 5 },
            { name: 'Priya M.', review: 'Best sports store in town. Love the collection!', rating: 5 },
            { name: 'Amit K.', review: 'Great offers and excellent customer service.', rating: 4 },
          ].map((review, i) => (
            <Grid item xs={12} md={4} key={i}>
              <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  {'⭐'.repeat(review.rating)}
                </Typography>
                <Typography variant="body1" sx={{ mb: 2, fontStyle: 'italic' }}>
                  "{review.review}"
                </Typography>
                <Typography variant="subtitle2" color="primary" fontWeight={600}>
                  — {review.name}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default HomePage;
