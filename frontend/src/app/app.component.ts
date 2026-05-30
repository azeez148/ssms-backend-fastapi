import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import * as AuthActions from './store/auth/auth.actions';
import { cartLoaded } from './store/cart/cart.actions';
import { favoritesLoaded } from './store/favorites/favorites.actions';
import { CartItem, UserProfile } from './models';

@Component({
  selector: 'app-root',
  template: `<router-outlet></router-outlet>`,
})
export class AppComponent implements OnInit {
  constructor(private store: Store) {}

  ngOnInit(): void {
    // Restore auth session from localStorage
    const token = localStorage.getItem('token');
    const userRaw = localStorage.getItem('user');
    if (token && userRaw) {
      const user: UserProfile = JSON.parse(userRaw);
      this.store.dispatch(AuthActions.restoreSession({ token, user }));
    }

    // Restore cart from localStorage
    const cartRaw = localStorage.getItem('cart');
    if (cartRaw) {
      const items: CartItem[] = JSON.parse(cartRaw);
      this.store.dispatch(cartLoaded({ items }));
    }

    // Restore favorites from localStorage
    const favRaw = localStorage.getItem('favorites');
    if (favRaw) {
      const ids: number[] = JSON.parse(favRaw);
      this.store.dispatch(favoritesLoaded({ ids }));
    }
  }
}
