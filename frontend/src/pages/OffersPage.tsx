import React, { useEffect, useState, useMemo } from 'react';
import {
  Container,
  Typography,
  Grid,
  Box,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import { Product, Category, EventOffer } from '../types';
import { productService } from '../services/productService';
import { ProductCard, SearchBar, FilterBar, LoadingSpinner } from '../components/common';
import { useCart } from '../context/CartContext';

const OffersPage: React.FC = () => {
  const { addToCart } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [events, setEvents] = useState<EventOffer[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [weeklyOffers, eventsData, categoriesData] = await Promise.all([
          productService.getWeeklyOffers(),
          productService.getEvents(),
          productService.getCategories(),
        ]);
        setProducts(weeklyOffers || []);
        setEvents(eventsData?.filter((e: EventOffer) => e.is_active) || []);
        setCategories(categoriesData || []);
      } catch (error) {
        console.error('Failed to load offers:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredProducts = useMemo(() => {
    let result = [...products];

    if (search) {
      const searchLower = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(searchLower) ||
          p.offer_name?.toLowerCase().includes(searchLower)
      );
    }

    if (selectedCategory) {
      result = result.filter((p) => String(p.category_id) === selectedCategory);
    }

    switch (sortBy) {
      case 'price_low':
        result.sort((a, b) => (a.offer_price || a.selling_price) - (b.offer_price || b.selling_price));
        break;
      case 'price_high':
        result.sort((a, b) => (b.offer_price || b.selling_price) - (a.offer_price || a.selling_price));
        break;
      case 'name_asc':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name_desc':
        result.sort((a, b) => b.name.localeCompare(a.name));
        break;
    }

    return result;
  }, [products, search, selectedCategory, sortBy]);

  if (loading) return <LoadingSpinner message="Loading offers..." />;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Offers & Events
      </Typography>

      {/* Active Events */}
      {events.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={2}>
            {events.map((event) => (
              <Grid item xs={12} sm={6} md={4} key={event.id}>
                <Card sx={{ background: 'linear-gradient(135deg, #ff6f00, #ff8f00)', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700}>
                      {event.name}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                      {event.description}
                    </Typography>
                    <Chip
                      label={`${event.rate}${event.rate_type === 'PERCENTAGE' ? '%' : '₹'} OFF`}
                      sx={{ bgcolor: 'rgba(255,255,255,0.3)', color: 'white', fontWeight: 700 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      <Box sx={{ mb: 3, display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <SearchBar value={search} onChange={setSearch} placeholder="Search offers..." />
        </Box>
        <FilterBar
          categories={categories}
          selectedCategory={selectedCategory}
          sortBy={sortBy}
          onCategoryChange={setSelectedCategory}
          onSortChange={setSortBy}
        />
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {filteredProducts.length} offer product{filteredProducts.length !== 1 ? 's' : ''} found
      </Typography>

      <Grid container spacing={3}>
        {filteredProducts.map((product) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
            <ProductCard product={product} onAddToCart={addToCart} />
          </Grid>
        ))}
      </Grid>

      {filteredProducts.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            No offer products available right now
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default OffersPage;
