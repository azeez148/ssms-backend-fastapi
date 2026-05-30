import { createReducer, on } from '@ngrx/store';
import { CartItem } from '../../models';
import * as CartActions from './cart.actions';

export interface CartState {
  items: CartItem[];
}

export const initialState: CartState = {
  items: [],
};

export const cartReducer = createReducer(
  initialState,

  on(CartActions.cartLoaded, (state, { items }) => ({
    ...state,
    items,
  })),

  on(CartActions.addToCart, (state, { product, quantity, size }) => {
    const idx = state.items.findIndex(
      (i) => i.product.id === product.id && i.selectedSize === size
    );
    if (idx >= 0) {
      const items = state.items.map((item, i) =>
        i === idx ? { ...item, quantity: item.quantity + quantity } : item
      );
      return { ...state, items };
    }
    return { ...state, items: [...state.items, { product, quantity, selectedSize: size }] };
  }),

  on(CartActions.removeFromCart, (state, { productId, size }) => ({
    ...state,
    items: state.items.filter((i) => !(i.product.id === productId && i.selectedSize === size)),
  })),

  on(CartActions.updateQuantity, (state, { productId, size, quantity }) => {
    if (quantity <= 0) {
      return { ...state, items: state.items.filter((i) => !(i.product.id === productId && i.selectedSize === size)) };
    }
    return {
      ...state,
      items: state.items.map((i) =>
        i.product.id === productId && i.selectedSize === size ? { ...i, quantity } : i
      ),
    };
  }),

  on(CartActions.clearCart, () => ({
    ...initialState,
  }))
);
