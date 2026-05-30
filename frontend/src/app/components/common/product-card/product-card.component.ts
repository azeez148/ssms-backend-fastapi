import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { Product, ProductSize } from '../../../models';
import { environment } from '../../../../environments/environment';

const NO_IMAGE = 'assets/no-image.svg';

@Component({
  selector: 'app-product-card',
  standalone: false,
  template: `
    <mat-card class="product-card">
      <!-- Image Frame -->
      <div class="img-frame">
        <img
          [src]="imgSrc"
          [alt]="product.name"
          class="product-img"
          (error)="onImgError()"
        />
        <span *ngIf="hasOffer" class="offer-badge">{{ product.offer_name || 'Sale' }}</span>
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

      <mat-card-content class="card-body">
        <p class="product-name" [title]="product.name">{{ product.name }}</p>
        <p class="category-name">{{ product.category?.name }}</p>

        <div class="price-row">
          <span class="price-main">₹{{ displayPrice }}</span>
          <span *ngIf="hasOffer" class="price-original">₹{{ product.selling_price }}</span>
          <span *ngIf="hasOffer" class="discount-pct">{{ discountPct }}% OFF</span>
        </div>

        <!-- Compact Size Selection -->
        <div *ngIf="hasSizes" class="size-section">
          <span class="size-label">Sizes:</span>
          <div class="size-chips">
            <button
              *ngFor="let sizeItem of visibleSizes"
              class="size-chip"
              [class.selected]="selectedSize === sizeItem.size"
              [class.out-of-stock]="sizeItem.quantity <= 0"
              [disabled]="sizeItem.quantity <= 0"
              (click)="selectSize(sizeItem)"
              [title]="sizeItem.quantity <= 0 ? 'Out of stock' : sizeItem.size"
            >{{ sizeItem.size }}</button>
            <span *ngIf="extraSizeCount > 0" class="more-sizes">+{{ extraSizeCount }}</span>
          </div>
        </div>
      </mat-card-content>

      <mat-card-actions class="card-actions">
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
      </mat-card-actions>
    </mat-card>
  `,
  styles: [`
    :host { display: flex; }
    .product-card {
      width: 100%;
      display: flex;
      flex-direction: column;
      border-radius: 12px !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
      transition: box-shadow 0.2s, transform 0.2s;
      overflow: hidden;
    }
    .product-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important; transform: translateY(-2px); }

    /* Image Frame */
    .img-frame {
      position: relative;
      width: 100%;
      aspect-ratio: 4 / 3;
      overflow: hidden;
      background: #f5f5f5;
    }
    .product-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.3s;
    }
    .product-card:hover .product-img { transform: scale(1.04); }

    .offer-badge {
      position: absolute;
      top: 10px;
      left: 10px;
      background: #ff6f00;
      color: white;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 20px;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      pointer-events: none;
    }
    .fav-btn {
      position: absolute;
      top: 4px;
      right: 4px;
      background: rgba(255,255,255,0.85);
      border-radius: 50%;
    }

    /* Card body */
    .card-body { flex: 1; padding: 12px 14px 4px !important; }

    .product-name {
      font-size: 0.9rem;
      font-weight: 700;
      color: #1a1a1a;
      margin: 0 0 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.3;
    }
    .category-name {
      font-size: 0.75rem;
      color: #888;
      margin: 0 0 8px;
    }

    .price-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
    .price-main { font-size: 1.05rem; font-weight: 700; color: #1a237e; }
    .price-original { font-size: 0.8rem; color: #aaa; text-decoration: line-through; }
    .discount-pct { font-size: 0.72rem; font-weight: 600; color: #2e7d32; background: #e8f5e9; padding: 1px 6px; border-radius: 4px; }

    /* Sizes */
    .size-section { display: flex; align-items: flex-start; gap: 6px; flex-wrap: nowrap; overflow: hidden; }
    .size-label { font-size: 0.72rem; font-weight: 600; color: #666; white-space: nowrap; padding-top: 3px; flex-shrink: 0; }
    .size-chips { display: flex; gap: 4px; flex-wrap: nowrap; overflow: hidden; align-items: center; }
    .size-chip {
      height: 24px;
      min-width: 28px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background: white;
      font-size: 0.7rem;
      cursor: pointer;
      padding: 0 5px;
      white-space: nowrap;
      flex-shrink: 0;
      transition: background 0.15s, border-color 0.15s;
    }
    .size-chip:hover:not(.out-of-stock):not(:disabled) { border-color: #1a237e; background: #e8eaf6; }
    .size-chip.selected { background: #1a237e; color: white; border-color: #1a237e; }
    .size-chip.out-of-stock { background: #fafafa; color: #ccc; border-color: #eee; cursor: not-allowed; text-decoration: line-through; }
    .more-sizes { font-size: 0.7rem; color: #888; white-space: nowrap; flex-shrink: 0; padding-top: 3px; }

    /* Actions */
    .card-actions { display: flex; flex-direction: column; gap: 6px; padding: 8px 12px 12px !important; }
    .action-btn { width: 100%; font-size: 0.78rem; line-height: 32px; }
  `],
})
export class ProductCardComponent implements OnChanges {
  @Input() product!: Product;
  @Input() isFavorite = false;
  @Input() showFavorite = false;
  @Output() addToCart = new EventEmitter<{ product: Product; size?: string }>();
  @Output() toggleFavorite = new EventEmitter<Product>();
  @Output() viewDetails = new EventEmitter<Product>();

  selectedSize: string | null = null;
  imgSrc = '';

  private readonly MAX_VISIBLE_SIZES = 5;

  ngOnChanges(): void {
    this.imgSrc = `${environment.apiUrl}/public/${this.product.id}/image`;
    this.selectedSize = null;
  }

  onImgError(): void {
    this.imgSrc = NO_IMAGE;
  }

  get hasOffer(): boolean {
    return !!(this.product.offer_price || this.product.discounted_price);
  }

  get displayPrice(): number {
    return this.product.offer_price ?? this.product.discounted_price ?? this.product.selling_price;
  }

  get discountPct(): number {
    const orig = this.product.selling_price;
    const disc = this.displayPrice;
    return orig > disc ? Math.round(((orig - disc) / orig) * 100) : 0;
  }

  get hasSizes(): boolean {
    return !!(this.product.size_map && this.product.size_map.length > 0);
  }

  get visibleSizes(): ProductSize[] {
    return (this.product.size_map || []).slice(0, this.MAX_VISIBLE_SIZES);
  }

  get extraSizeCount(): number {
    const total = this.product.size_map?.length ?? 0;
    return Math.max(0, total - this.MAX_VISIBLE_SIZES);
  }

  selectSize(sizeItem: ProductSize): void {
    if (sizeItem.quantity > 0) {
      this.selectedSize = this.selectedSize === sizeItem.size ? null : sizeItem.size;
    }
  }

  onAddToCart(): void {
    this.addToCart.emit({ product: this.product, size: this.selectedSize || undefined });
  }
}
