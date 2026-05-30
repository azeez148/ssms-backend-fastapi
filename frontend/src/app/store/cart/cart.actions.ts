import { createAction, props } from '@ngrx/store';
import { CartItem, Product } from '../../models';

export const addToCart = createAction(
  '[Cart] Add To Cart',
  props<{ product: Product; quantity: number; size?: string }>()
);

export const removeFromCart = createAction(
  '[Cart] Remove From Cart',
  props<{ productId: number; size?: string }>()
);

export const updateQuantity = createAction(
  '[Cart] Update Quantity',
  props<{ productId: number; size?: string; quantity: number }>()
);

export const clearCart = createAction('[Cart] Clear Cart');

export const loadCart = createAction('[Cart] Load Cart');

export const cartLoaded = createAction(
  '[Cart] Cart Loaded',
  props<{ items: CartItem[] }>()
);
