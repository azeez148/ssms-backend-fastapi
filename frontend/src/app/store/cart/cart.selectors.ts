import { createFeatureSelector, createSelector } from '@ngrx/store';
import { CartState } from './cart.reducer';

export const selectCartState = createFeatureSelector<CartState>('cart');

export const selectCartItems = createSelector(selectCartState, (state) => state.items);

export const selectCartItemCount = createSelector(selectCartItems, (items) =>
  items.reduce((count, item) => count + item.quantity, 0)
);

export const selectCartTotal = createSelector(selectCartItems, (items) =>
  items.reduce((total, item) => {
    const price =
      item.product.offer_price ??
      item.product.discounted_price ??
      item.product.selling_price;
    return total + price * item.quantity;
  }, 0)
);
