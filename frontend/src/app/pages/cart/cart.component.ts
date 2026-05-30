import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { CartItem } from '../../models';
import { selectCartItems, selectCartItemCount, selectCartTotal } from '../../store/cart/cart.selectors';
import { selectUser, selectIsAuthenticated } from '../../store/auth/auth.selectors';
import * as CartActions from '../../store/cart/cart.actions';
import * as AuthActions from '../../store/auth/auth.actions';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-cart',
  standalone: false,
  template: `
    <!-- Empty cart -->
    <div *ngIf="items.length === 0 && activeStep === 0" class="empty-cart">
      <mat-icon class="empty-icon">shopping_bag</mat-icon>
      <h2>Your cart is empty</h2>
      <p>Browse our products and add items to your cart</p>
      <a mat-raised-button color="primary" routerLink="/products">Browse Products</a>
    </div>

    <!-- Cart with items -->
    <div *ngIf="items.length > 0 || activeStep > 0" class="container">
      <h1 class="page-title">Shopping Cart</h1>

      <mat-stepper [selectedIndex]="activeStep" class="stepper">
        <!-- Step 1: Cart -->
        <mat-step label="Cart">
          <div *ngFor="let item of items" class="cart-item">
            <mat-card>
              <mat-card-content>
                <div class="item-row">
                  <div class="item-info">
                    <p class="item-name">{{ item.product.name }}</p>
                    <p class="item-cat">{{ item.product.category?.name }}</p>
                    <p *ngIf="item.selectedSize" class="item-size">Size: {{ item.selectedSize }}</p>
                  </div>
                  <div class="item-controls">
                    <button mat-icon-button (click)="updateQty(item, item.quantity - 1)">
                      <mat-icon>remove</mat-icon>
                    </button>
                    <span class="qty">{{ item.quantity }}</span>
                    <button mat-icon-button (click)="updateQty(item, item.quantity + 1)">
                      <mat-icon>add</mat-icon>
                    </button>
                  </div>
                  <div class="item-price">
                    <p class="price">₹{{ getItemPrice(item) * item.quantity }}</p>
                    <p class="unit-price">₹{{ getItemPrice(item) }} each</p>
                  </div>
                  <button mat-icon-button color="warn" (click)="removeItem(item)">
                    <mat-icon>delete</mat-icon>
                  </button>
                </div>
              </mat-card-content>
            </mat-card>
          </div>

          <mat-card class="summary-card">
            <mat-card-content>
              <div class="summary-row">
                <span>Total ({{ itemCount }} items)</span>
                <strong>₹{{ total }}</strong>
              </div>
            </mat-card-content>
            <mat-card-actions>
              <button mat-raised-button color="primary" (click)="continueToBuy()">
                Continue to Buy
              </button>
            </mat-card-actions>
          </mat-card>
        </mat-step>

        <!-- Step 2: Delivery -->
        <mat-step label="Delivery Address">
          <div class="address-form">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Address</mat-label>
              <textarea matInput rows="2" [(ngModel)]="address.address"></textarea>
            </mat-form-field>
            <div class="address-row">
              <mat-form-field appearance="outline">
                <mat-label>City</mat-label>
                <input matInput [(ngModel)]="address.city" />
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>State</mat-label>
                <input matInput [(ngModel)]="address.state" />
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>ZIP Code</mat-label>
                <input matInput [(ngModel)]="address.zip_code" />
              </mat-form-field>
            </div>
          </div>
          <div class="step-actions">
            <button mat-button (click)="activeStep = 0">Back</button>
            <button mat-raised-button color="primary" [disabled]="!isAddressValid()" (click)="activeStep = 2">
              Review Order
            </button>
          </div>
        </mat-step>

        <!-- Step 3: Confirm -->
        <mat-step label="Confirm Order">
          <mat-card class="confirm-card">
            <mat-card-content>
              <h3>Order Summary</h3>
              <div *ngFor="let item of items" class="confirm-item">
                <span>{{ item.product.name }}{{ item.selectedSize ? ' (' + item.selectedSize + ')' : '' }} × {{ item.quantity }}</span>
                <span>₹{{ getItemPrice(item) * item.quantity }}</span>
              </div>
              <mat-divider class="divider"></mat-divider>
              <div class="confirm-total">
                <strong>Total</strong>
                <strong>₹{{ total }}</strong>
              </div>
              <h3>Delivery To</h3>
              <p>{{ address.address }}, {{ address.city }}, {{ address.state }} - {{ address.zip_code }}</p>
            </mat-card-content>
          </mat-card>
          <div class="step-actions">
            <button mat-button (click)="activeStep = 1">Back</button>
            <button mat-raised-button color="primary" (click)="placeOrder()">
              <mat-icon>whatsapp</mat-icon> Place Order via WhatsApp
            </button>
          </div>
        </mat-step>
      </mat-stepper>
    </div>
  `,
  styles: [`
    .empty-cart { text-align: center; padding: 64px 24px; }
    .empty-icon { font-size: 80px; width: 80px; height: 80px; color: #999; margin-bottom: 16px; }
    .container { max-width: 800px; margin: 0 auto; padding: 32px 24px; }
    .page-title { font-size: 2rem; font-weight: 700; margin: 0 0 24px; }
    .stepper { background: transparent; }
    .cart-item { margin-bottom: 16px; }
    .item-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
    .item-info { flex: 1; min-width: 150px; }
    .item-name { font-weight: 600; margin: 0 0 4px; }
    .item-cat, .item-size { color: #666; font-size: 0.85rem; margin: 0; }
    .item-controls { display: flex; align-items: center; gap: 8px; }
    .qty { font-size: 1.1rem; font-weight: 600; min-width: 24px; text-align: center; }
    .item-price { text-align: right; }
    .price { font-weight: 700; color: #1a237e; margin: 0; }
    .unit-price { color: #999; font-size: 0.8rem; margin: 0; }
    .summary-card { margin-top: 24px; }
    .summary-row { display: flex; justify-content: space-between; font-size: 1.1rem; }
    .address-form { padding: 16px 0; }
    .full-width { width: 100%; }
    .address-row { display: flex; gap: 16px; flex-wrap: wrap; }
    .address-row mat-form-field { flex: 1; min-width: 120px; }
    .step-actions { display: flex; gap: 16px; padding: 16px 0; }
    .confirm-card { margin: 16px 0; }
    .confirm-item { display: flex; justify-content: space-between; padding: 4px 0; }
    .divider { margin: 12px 0; }
    .confirm-total { display: flex; justify-content: space-between; font-size: 1.1rem; padding: 8px 0; }
  `],
})
export class CartComponent implements OnInit, OnDestroy {
  items: CartItem[] = [];
  activeStep = 0;
  address = { address: '', city: '', state: '', zip_code: '' };
  itemCount = 0;
  total = 0;
  private isAuthenticated = false;
  private userName = '';
  private userMobile = '';
  private destroy$ = new Subject<void>();

  constructor(private store: Store, private router: Router) {}

  ngOnInit(): void {
    this.store.select(selectCartItems).pipe(takeUntil(this.destroy$))
      .subscribe((items) => (this.items = items));
    this.store.select(selectCartItemCount).pipe(takeUntil(this.destroy$))
      .subscribe((count) => (this.itemCount = count));
    this.store.select(selectCartTotal).pipe(takeUntil(this.destroy$))
      .subscribe((total) => (this.total = total));
    this.store.select(selectIsAuthenticated).pipe(takeUntil(this.destroy$))
      .subscribe((auth) => {
        this.isAuthenticated = auth;
        if (auth) {
          this.store.dispatch(AuthActions.loadProfile());
        }
      });

    this.store.select(selectUser).pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        if (user) {
          this.address = {
            address: user.address || '',
            city: user.city || '',
            state: user.state || '',
            zip_code: user.zip_code || '',
          };
          this.userName = `${user.first_name} ${user.last_name}`;
          this.userMobile = user.mobile;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getItemPrice(item: CartItem): number {
    return item.product.offer_price ?? item.product.discounted_price ?? item.product.selling_price;
  }

  updateQty(item: CartItem, qty: number): void {
    this.store.dispatch(CartActions.updateQuantity({
      productId: item.product.id,
      size: item.selectedSize,
      quantity: qty,
    }));
  }

  removeItem(item: CartItem): void {
    this.store.dispatch(CartActions.removeFromCart({
      productId: item.product.id,
      size: item.selectedSize,
    }));
  }

  continueToBuy(): void {
    if (!this.isAuthenticated) {
      this.router.navigate(['/login']);
      return;
    }
    this.activeStep = 1;
  }

  isAddressValid(): boolean {
    return !!(this.address.address && this.address.city && this.address.state && this.address.zip_code);
  }

  placeOrder(): void {
    const orderItems = this.items
      .map((i) => {
        const sizeInfo = i.selectedSize ? ` (${i.selectedSize})` : '';
        return `• ${i.product.name}${sizeInfo} (x${i.quantity}) - ₹${this.getItemPrice(i) * i.quantity}`;
      })
      .join('\n');
    const message =
      `🛒 *New Order*\n\n${orderItems}\n\n💰 *Total: ₹${this.total}*\n\n` +
      `📍 *Delivery Address:*\n${this.address.address}, ${this.address.city}, ${this.address.state} - ${this.address.zip_code}\n\n` +
      `👤 *Customer:* ${this.userName}\n📱 *Mobile:* ${this.userMobile}`;
    const encoded = encodeURIComponent(message);
    window.open(`https://wa.me/${environment.whatsappNumber}?text=${encoded}`, '_blank');
    this.store.dispatch(CartActions.clearCart());
    this.activeStep = 0;
    this.router.navigate(['/']);
  }
}
