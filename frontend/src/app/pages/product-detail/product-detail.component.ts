import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { Product, ProductSize } from '../../models';
import { ProductService } from '../../services/product.service';
import { environment } from '../../../environments/environment';
import * as CartActions from '../../store/cart/cart.actions';

@Component({
  selector: 'app-product-detail',
  standalone: false,
  template: `
    <div class="container" *ngIf="product; else loadingTpl">
      <button mat-button class="back-btn" (click)="goBack()">
        <mat-icon>arrow_back</mat-icon> Back to Products
      </button>

      <div class="detail-layout">
        <!-- Product Image -->
        <div class="image-section">
          <img [src]="imageUrl" [alt]="product.name" class="product-image" />
          <mat-chip-set *ngIf="hasOffer" class="offer-badge">
            <mat-chip color="accent" highlighted>{{ product.offer_name || 'Sale' }}</mat-chip>
          </mat-chip-set>
        </div>

        <!-- Product Info -->
        <div class="info-section">
          <h1 class="product-name">{{ product.name }}</h1>
          <p class="category">{{ product.category?.name }}</p>

          <div class="price-section">
            <span class="price-main">₹{{ displayPrice }}</span>
            <span *ngIf="hasOffer" class="price-original">₹{{ product.selling_price }}</span>
            <span *ngIf="hasOffer" class="discount-badge">
              {{ discountPercent }}% OFF
            </span>
          </div>

          <mat-divider class="divider"></mat-divider>

          <!-- Description -->
          <div class="description-section" *ngIf="product.description">
            <h3>Description</h3>
            <p>{{ product.description }}</p>
          </div>

          <!-- Size Selection -->
          <div *ngIf="hasSizes" class="size-section">
            <h3>Select Size</h3>
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
                <span class="stock-info" *ngIf="sizeItem.quantity > 0 && sizeItem.quantity <= 5">
                  ({{ sizeItem.quantity }} left)
                </span>
              </button>
            </div>
            <p class="size-hint" *ngIf="hasSizes && !selectedSize">Please select a size</p>
          </div>

          <!-- Tags -->
          <div *ngIf="product.tags && product.tags.length > 0" class="tags-section">
            <h3>Tags</h3>
            <mat-chip-set>
              <mat-chip *ngFor="let tag of product.tags">{{ tag.name }}</mat-chip>
            </mat-chip-set>
          </div>

          <!-- Available At -->
          <div *ngIf="product.shops && product.shops.length > 0" class="shops-section">
            <h3>Available At</h3>
            <mat-chip-set>
              <mat-chip *ngFor="let shop of product.shops">
                <mat-icon matChipAvatar>store</mat-icon>
                {{ shop.name }}
              </mat-chip>
            </mat-chip-set>
          </div>

          <mat-divider class="divider"></mat-divider>

          <!-- Add to Cart -->
          <div class="cart-section">
            <div class="quantity-control">
              <button mat-icon-button (click)="decreaseQty()" [disabled]="quantity <= 1">
                <mat-icon>remove</mat-icon>
              </button>
              <span class="qty">{{ quantity }}</span>
              <button mat-icon-button (click)="increaseQty()">
                <mat-icon>add</mat-icon>
              </button>
            </div>
            <button
              mat-raised-button
              color="primary"
              class="add-to-cart-btn"
              (click)="addToCart()"
              [disabled]="hasSizes && !selectedSize"
            >
              <mat-icon>add_shopping_cart</mat-icon>
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>

    <ng-template #loadingTpl>
      <app-loading-spinner message="Loading product details..."></app-loading-spinner>
    </ng-template>
  `,
  styles: [`
    .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
    .back-btn { margin-bottom: 16px; }
    .detail-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
    @media (max-width: 768px) { .detail-layout { grid-template-columns: 1fr; } }
    .image-section { position: relative; }
    .product-image { width: 100%; max-height: 500px; object-fit: cover; border-radius: 12px; }
    .offer-badge { position: absolute; top: 12px; left: 12px; }
    .info-section { display: flex; flex-direction: column; gap: 8px; }
    .product-name { font-size: 2rem; font-weight: 700; margin: 0; }
    .category { color: #666; font-size: 1rem; margin: 0; }
    .price-section { display: flex; align-items: center; gap: 12px; margin: 12px 0; }
    .price-main { font-size: 1.8rem; font-weight: 700; color: #1a237e; }
    .price-original { font-size: 1.1rem; color: #999; text-decoration: line-through; }
    .discount-badge { background: #e8f5e9; color: #2e7d32; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }
    .divider { margin: 16px 0; }
    .description-section p { color: #444; line-height: 1.6; }
    h3 { font-size: 1rem; font-weight: 600; margin: 0 0 8px; }
    .size-section { margin: 8px 0; }
    .size-chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .size-chip {
      min-width: 48px;
      height: 36px;
      border: 2px solid #ccc;
      border-radius: 6px;
      background: white;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all 0.2s;
      padding: 0 12px;
      display: flex;
      align-items: center;
      gap: 4px;
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
    .stock-info { font-size: 0.7rem; opacity: 0.8; }
    .size-hint { color: #f44336; font-size: 0.8rem; margin: 8px 0 0; }
    .tags-section, .shops-section { margin: 8px 0; }
    .cart-section { display: flex; align-items: center; gap: 16px; margin-top: 8px; }
    .quantity-control { display: flex; align-items: center; gap: 8px; border: 1px solid #ccc; border-radius: 8px; padding: 4px; }
    .qty { font-size: 1.1rem; font-weight: 600; min-width: 24px; text-align: center; }
    .add-to-cart-btn { flex: 1; height: 48px; font-size: 1rem; }
  `],
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  selectedSize: string | null = null;
  quantity = 1;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productService: ProductService,
    private store: Store
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.productService.getAllProducts().subscribe((products) => {
      this.product = products.find((p) => p.id === id) || null;
    });
  }

  get imageUrl(): string {
    return this.product ? `${environment.apiUrl}/public/${this.product.id}/image` : '';
  }

  get hasOffer(): boolean {
    return !!(this.product?.offer_price || this.product?.discounted_price);
  }

  get displayPrice(): number {
    if (!this.product) return 0;
    return this.product.offer_price ?? this.product.discounted_price ?? this.product.selling_price;
  }

  get discountPercent(): number {
    if (!this.product) return 0;
    const original = this.product.selling_price;
    const discounted = this.displayPrice;
    return Math.round(((original - discounted) / original) * 100);
  }

  get hasSizes(): boolean {
    return !!(this.product?.size_map && this.product.size_map.length > 0);
  }

  selectSize(sizeItem: ProductSize): void {
    if (sizeItem.quantity > 0) {
      this.selectedSize = sizeItem.size;
    }
  }

  increaseQty(): void {
    this.quantity++;
  }

  decreaseQty(): void {
    if (this.quantity > 1) this.quantity--;
  }

  addToCart(): void {
    if (!this.product) return;
    this.store.dispatch(
      CartActions.addToCart({
        product: this.product,
        quantity: this.quantity,
        size: this.selectedSize || undefined,
      })
    );
  }

  goBack(): void {
    this.router.navigate(['/products']);
  }
}
