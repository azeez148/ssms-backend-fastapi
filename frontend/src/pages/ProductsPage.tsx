import React, { useEffect, useState, useMemo } from 'react';
import { Container, Typography, Grid, Box } from '@mui/material';
import { Product, Category } from '../types';
import { productService } from '../services/productService';
import { ProductCard, SearchBar, FilterBar, LoadingSpinner } from '../components/common';
import { useCart } from '../context/CartContext';

const ProductsPage: React.FC = () => {
  const { addToCart } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [favorites, setFavorites] = useState<number[]>(() => {
    const saved = localStorage.getItem('favorites');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsData, categoriesData] = await Promise.all([
          productService.getAllProducts(),
          productService.getCategories(),
        ]);
        setProducts(productsData.filter((p: Product) => p.is_active && p.can_listed));
        setCategories(categoriesData);
      } catch (error) {
        console.error('Failed to load products:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const toggleFavorite = (product: Product) => {
    setFavorites((prev) => {
      const updated = prev.includes(product.id)
        ? prev.filter((id) => id !== product.id)
        : [...prev, product.id];
      localStorage.setItem('favorites', JSON.stringify(updated));
      return updated;
    });
  };

  const filteredProducts = useMemo(() => {
    let result = [...products];

    if (search) {
      const searchLower = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(searchLower) ||
          p.description?.toLowerCase().includes(searchLower) ||
          p.category?.name.toLowerCase().includes(searchLower)
      );
    }

    if (selectedCategory) {
      result = result.filter((p) => String(p.category_id) === selectedCategory);
    }

    switch (sortBy) {
      case 'price_low':
        result.sort((a, b) => (a.selling_price) - (b.selling_price));
        break;
      case 'price_high':
        result.sort((a, b) => (b.selling_price) - (a.selling_price));
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

  if (loading) return <LoadingSpinner message="Loading products..." />;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        All Products
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <SearchBar value={search} onChange={setSearch} />
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
        {filteredProducts.length} product{filteredProducts.length !== 1 ? 's' : ''} found
      </Typography>

      <Grid container spacing={3}>
        {filteredProducts.map((product) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
            <ProductCard
              product={product}
              onAddToCart={addToCart}
              onToggleFavorite={toggleFavorite}
              isFavorite={favorites.includes(product.id)}
            />
          </Grid>
        ))}
      </Grid>

      {filteredProducts.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            No products found matching your criteria
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default ProductsPage;
