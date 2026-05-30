import { createAction, props } from '@ngrx/store';

export const toggleFavorite = createAction(
  '[Favorites] Toggle Favorite',
  props<{ productId: number }>()
);

export const loadFavorites = createAction('[Favorites] Load Favorites');

export const favoritesLoaded = createAction(
  '[Favorites] Favorites Loaded',
  props<{ ids: number[] }>()
);
