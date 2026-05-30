import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Observable, filter, map } from 'rxjs';
import { AuthService } from '../../../services/auth.service';
import { CartService } from '../../../services/cart.service';
import { UserProfile } from '../../../models';

@Component({
  selector: 'app-header',
  standalone: false,
  template: `
    <mat-toolbar color="primary" class="app-toolbar">
      <!-- Mobile menu button -->
      <button mat-icon-button class="mobile-menu-btn" (click)="drawerOpen = true">
        <mat-icon>menu</mat-icon>
      </button>

      <span class="brand" routerLink="/">🏆 ADRENALINE STORE</span>

      <span class="spacer"></span>

      <!-- Desktop nav -->
      <nav class="desktop-nav">
        <a mat-button routerLink="/" routerLinkActive="active-link" [routerLinkActiveOptions]="{exact:true}">Home</a>
        <a mat-button routerLink="/products" routerLinkActive="active-link">Products</a>
        <a mat-button routerLink="/offers" routerLinkActive="active-link">Offers</a>
      </nav>

      <!-- Cart -->
      <button mat-icon-button routerLink="/cart">
        <mat-icon [matBadge]="(itemCount$ | async) || null" matBadgeColor="accent">
          shopping_cart
        </mat-icon>
      </button>

      <!-- Auth -->
      <ng-container *ngIf="user$ | async as user; else loginBtn">
        <button mat-icon-button [matMenuTriggerFor]="profileMenu">
          <mat-icon>account_circle</mat-icon>
        </button>
        <mat-menu #profileMenu="matMenu">
          <button mat-menu-item routerLink="/profile">
            <mat-icon>person</mat-icon>
            <span>{{ user.first_name }} {{ user.last_name }}</span>
          </button>
          <mat-divider></mat-divider>
          <button mat-menu-item (click)="logout()">
            <mat-icon>logout</mat-icon>
            <span>Logout</span>
          </button>
        </mat-menu>
      </ng-container>
      <ng-template #loginBtn>
        <a mat-button routerLink="/login">
          <mat-icon>login</mat-icon> Login
        </a>
      </ng-template>
    </mat-toolbar>

    <!-- Mobile drawer -->
    <mat-sidenav-container *ngIf="drawerOpen" class="mobile-drawer-overlay">
      <mat-sidenav opened mode="over" (closedStart)="drawerOpen = false">
        <div class="drawer-header">
          <span class="brand-small">🏆 ADRENALINE</span>
          <button mat-icon-button (click)="drawerOpen = false"><mat-icon>close</mat-icon></button>
        </div>
        <mat-divider></mat-divider>
        <mat-nav-list>
          <a mat-list-item routerLink="/" (click)="drawerOpen = false">
            <mat-icon matListItemIcon>home</mat-icon> Home
          </a>
          <a mat-list-item routerLink="/products" (click)="drawerOpen = false">
            <mat-icon matListItemIcon>store</mat-icon> Products
          </a>
          <a mat-list-item routerLink="/offers" (click)="drawerOpen = false">
            <mat-icon matListItemIcon>local_offer</mat-icon> Offers
          </a>
        </mat-nav-list>
      </mat-sidenav>
    </mat-sidenav-container>
  `,
  styles: [`
    .app-toolbar { position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .brand { cursor: pointer; font-weight: 700; letter-spacing: 1px; font-size: 1.1rem; }
    .brand-small { font-weight: 700; font-size: 1rem; }
    .spacer { flex: 1; }
    .desktop-nav { display: flex; gap: 4px; }
    .active-link { border-bottom: 2px solid white; }
    .mobile-menu-btn { display: none; }
    .drawer-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; }
    .mobile-drawer-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 200; }
    @media (max-width: 768px) {
      .desktop-nav { display: none; }
      .mobile-menu-btn { display: inline-flex; }
    }
  `],
})
export class HeaderComponent {
  drawerOpen = false;
  user$: Observable<UserProfile | null>;
  itemCount$: Observable<number>;

  constructor(private auth: AuthService, private cart: CartService) {
    this.user$ = this.auth.user$;
    this.itemCount$ = this.cart.items$.pipe(
      map((items) => items.reduce((c, i) => c + i.quantity, 0))
    );
  }

  logout(): void {
    this.auth.logout();
  }
}
