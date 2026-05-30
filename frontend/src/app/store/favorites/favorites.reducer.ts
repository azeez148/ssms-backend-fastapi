import { createReducer, on } from '@ngrx/store';
import * as FavoritesActions from './favorites.actions';

export interface FavoritesState {
  ids: number[];
}

export const initialState: FavoritesState = {
  ids: [],
};

export const favoritesReducer = createReducer(
  initialState,

  on(FavoritesActions.favoritesLoaded, (state, { ids }) => ({
    ...state,
    ids,
  })),

  on(FavoritesActions.toggleFavorite, (state, { productId }) => {
    const idx = state.ids.indexOf(productId);
    if (idx >= 0) {
      return { ...state, ids: state.ids.filter((id) => id !== productId) };
    }
    return { ...state, ids: [...state.ids, productId] };
  })
);
