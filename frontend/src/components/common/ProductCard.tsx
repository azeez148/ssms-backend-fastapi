import React from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  IconButton,
  Button,
  Chip,
  Box,
} from '@mui/material';
import { AddShoppingCart, FavoriteBorder, Favorite } from '@mui/icons-material';
import { Product } from '../../types';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onToggleFavorite?: (product: Product) => void;
  isFavorite?: boolean;
  imageBaseUrl?: string;
}

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onAddToCart,
  onToggleFavorite,
  isFavorite = false,
  imageBaseUrl = '/api/public',
}) => {
  const hasOffer = product.offer_price || product.discounted_price;
  const displayPrice = product.offer_price || product.discounted_price || product.selling_price;

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ position: 'relative' }}>
        <CardMedia
          component="img"
          height="200"
          image={`${imageBaseUrl}/${product.id}/image`}
          alt={product.name}
          sx={{ objectFit: 'cover' }}
        />
        {hasOffer && (
          <Chip
            label={product.offer_name || 'Sale'}
            color="secondary"
            size="small"
            sx={{ position: 'absolute', top: 8, left: 8 }}
          />
        )}
        {onToggleFavorite && (
          <IconButton
            onClick={() => onToggleFavorite(product)}
            sx={{ position: 'absolute', top: 4, right: 4, bgcolor: 'rgba(255,255,255,0.8)' }}
            size="small"
          >
            {isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
          </IconButton>
        )}
      </Box>
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Typography gutterBottom variant="subtitle1" component="div" noWrap fontWeight={600}>
          {product.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          {product.category?.name}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
          <Typography variant="h6" color="primary" fontWeight={700}>
            ₹{displayPrice}
          </Typography>
          {hasOffer && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ textDecoration: 'line-through' }}
            >
              ₹{product.selling_price}
            </Typography>
          )}
        </Box>
      </CardContent>
      <CardActions sx={{ px: 2, pb: 2 }}>
        <Button
          variant="contained"
          size="small"
          startIcon={<AddShoppingCart />}
          onClick={() => onAddToCart(product)}
          fullWidth
        >
          Add to Cart
        </Button>
      </CardActions>
    </Card>
  );
};

export default ProductCard;
