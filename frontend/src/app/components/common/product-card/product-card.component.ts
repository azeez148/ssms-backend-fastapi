import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Product } from '../../../models';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-product-card',
  standalone: false,
  template: `
    <mat-card class="product-card">
      <div class="img-wrapper">
        <img mat-card-image [src]="imageUrl" [alt]="product.name" class="product-img" />
        <mat-chip-set *ngIf="hasOffer" class="offer-badge">
          <mat-chip color="accent" highlighted>{{ product.offer_name || 'Sale' }}</mat-chip>
        </mat-chip-set>
        <button
          *ngIf="showFavorite"
          mat-icon-button
          class="fav-btn"
          (click)="toggleFavorite.emit(product)"
        >
          <mat-icon [color]="isFavorite ? 'warn' : ''">
            {{ isFavorite ? 'favorite' : 'favorite_border' }}
          </mat-icon>
        </button>
      </div>

      <mat-card-content>
        <p class="product-name">{{ product.name }}</p>
        <p class="category-name">{{ product.category?.name }}</p>
        <div class="price-row">
          <span class="price-main">₹{{ displayPrice }}</span>
          <span *ngIf="hasOffer" class="price-original">₹{{ product.selling_price }}</span>
        </div>
      </mat-card-content>

      <mat-card-actions>
        <button mat-raised-button color="primary" class="add-btn" (click)="addToCart.emit(product)">
          <mat-icon>add_shopping_cart</mat-icon>
          Add to Cart
        </button>
      </mat-card-actions>
    </mat-card>
  `,
  styles: [`
    .product-card { height: 100%; display: flex; flex-direction: column; }
    .img-wrapper { position: relative; }
    .product-img { height: 200px; object-fit: cover; width: 100%; }
    .offer-badge { position: absolute; top: 8px; left: 8px; }
    .fav-btn { position: absolute; top: 4px; right: 4px; background: rgba(255,255,255,0.8); }
    mat-card-content { flex: 1; }
    .product-name { font-weight: 600; margin: 8px 0 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .category-name { color: #666; font-size: 0.85rem; margin: 0; }
    .price-row { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
    .price-main { font-size: 1.2rem; font-weight: 700; color: #1a237e; }
    .price-original { font-size: 0.9rem; color: #999; text-decoration: line-through; }
    .add-btn { width: 100%; }
    mat-card-actions { padding: 0 16px 16px; }
  `],
})
export class ProductCardComponent {
  @Input() product!: Product;
  @Input() isFavorite = false;
  @Input() showFavorite = false;
  @Output() addToCart = new EventEmitter<Product>();
  @Output() toggleFavorite = new EventEmitter<Product>();

  get hasOffer(): boolean {
    return !!(this.product.offer_price || this.product.discounted_price);
  }

  get displayPrice(): number {
    return this.product.offer_price ?? this.product.discounted_price ?? this.product.selling_price;
  }

  get imageUrl(): string {
    return `${environment.apiUrl}/public/${this.product.id}/image`;
  }
}
