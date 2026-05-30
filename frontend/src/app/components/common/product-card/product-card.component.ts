import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Product, ProductSize } from '../../../models';
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

        <!-- Size Selection -->
        <div *ngIf="hasSizes" class="size-section">
          <p class="size-label">Sizes:</p>
          <div class="size-chips">
            <button
              *ngFor="let sizeItem of product.size_map"
              class="size-chip"
              [class.selected]="selectedSize === sizeItem.size"
              [class.out-of-stock]="sizeItem.quantity <= 0"
              [disabled]="sizeItem.quantity <= 0"
              (click)="selectSize(sizeItem)"
            >
              {{ sizeItem.size }}
            </button>
          </div>
        </div>
      </mat-card-content>

      <mat-card-actions>
        <div class="action-buttons">
          <button
            mat-raised-button
            color="primary"
            class="action-btn"
            (click)="onAddToCart()"
            [disabled]="hasSizes && !selectedSize"
          >
            <mat-icon>add_shopping_cart</mat-icon>
            Add to Cart
          </button>
          <button
            mat-stroked-button
            color="primary"
            class="action-btn"
            (click)="viewDetails.emit(product)"
          >
            <mat-icon>visibility</mat-icon>
            View Details
          </button>
        </div>
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
    .size-section { margin-top: 12px; }
    .size-label { font-size: 0.8rem; color: #666; margin: 0 0 6px; font-weight: 500; }
    .size-chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .size-chip {
      min-width: 36px;
      height: 28px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background: white;
      font-size: 0.75rem;
      cursor: pointer;
      transition: all 0.2s;
      padding: 0 8px;
    }
    .size-chip:hover:not(.out-of-stock) { border-color: #1a237e; }
    .size-chip.selected { background: #1a237e; color: white; border-color: #1a237e; }
    .size-chip.out-of-stock {
      background: #f5f5f5;
      color: #bbb;
      border-color: #e0e0e0;
      cursor: not-allowed;
      text-decoration: line-through;
    }
    .action-buttons { display: flex; flex-direction: column; gap: 8px; width: 100%; }
    .action-btn { width: 100%; font-size: 0.8rem; }
    mat-card-actions { padding: 0 16px 16px; }
  `],
})
export class ProductCardComponent {
  @Input() product!: Product;
  @Input() isFavorite = false;
  @Input() showFavorite = false;
  @Output() addToCart = new EventEmitter<{ product: Product; size?: string }>();
  @Output() toggleFavorite = new EventEmitter<Product>();
  @Output() viewDetails = new EventEmitter<Product>();

  selectedSize: string | null = null;

  get hasOffer(): boolean {
    return !!(this.product.offer_price || this.product.discounted_price);
  }

  get displayPrice(): number {
    return this.product.offer_price ?? this.product.discounted_price ?? this.product.selling_price;
  }

  get imageUrl(): string {
    return `${environment.apiUrl}/public/${this.product.id}/image`;
  }

  get hasSizes(): boolean {
    return !!(this.product.size_map && this.product.size_map.length > 0);
  }

  selectSize(sizeItem: ProductSize): void {
    if (sizeItem.quantity > 0) {
      this.selectedSize = sizeItem.size;
    }
  }

  onAddToCart(): void {
    this.addToCart.emit({
      product: this.product,
      size: this.selectedSize || undefined,
    });
  }
}
