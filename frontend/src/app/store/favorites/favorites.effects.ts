import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { tap, withLatestFrom } from 'rxjs/operators';
import * as FavoritesActions from './favorites.actions';
import { selectFavoriteIds } from './favorites.selectors';

@Injectable()
export class FavoritesEffects {
  persistFavorites$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(FavoritesActions.toggleFavorite),
        withLatestFrom(this.store.select(selectFavoriteIds)),
        tap(([_, ids]) => {
          localStorage.setItem('favorites', JSON.stringify(ids));
        })
      ),
    { dispatch: false }
  );

  constructor(private actions$: Actions, private store: Store) {}
}
