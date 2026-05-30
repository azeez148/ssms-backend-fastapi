import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { Product, OfferData } from '../../models';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';

@Component({
  selector: 'app-home',
  standalone: false,
  template: `
    <!-- Hero Banner -->
    <div class="hero">
      <div class="hero-content">
        <h1 class="hero-title">Gear Up for Victory 🏆</h1>
        <p class="hero-sub">Premium sports gear, jerseys &amp; accessories at the best prices</p>
        <a mat-raised-button color="accent" routerLink="/products" class="hero-btn">
          Shop Now <mat-icon>arrow_forward</mat-icon>
        </a>
      </div>
    </div>

    <!-- Offers Banner -->
    <div class="container" *ngIf="offers.length > 0">
      <mat-card class="offers-banner">
        <mat-card-content>
          <div class="offers-row">
            <div class="offers-left">
              <mat-icon class="offer-icon">local_offer</mat-icon>
              <div>
                <h2 class="offer-name">{{ offers[0]?.name || 'Special Offers' }}</h2>
                <p class="offer-desc">{{ offers[0]?.description || 'Check out our latest deals!' }}</p>
              </div>
            </div>
            <a mat-raised-button routerLink="/offers" class="view-offers-btn">View All Offers</a>
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <!-- New Arrivals -->
    <div class="container section">
      <div class="section-header">
        <h2 class="section-title">New Arrivals</h2>
        <a mat-button routerLink="/products">View All <mat-icon>arrow_forward</mat-icon></a>
      </div>

      <div class="product-grid" *ngIf="!loading; else skeleton">
        <app-product-card
          *ngFor="let product of products.slice(0, 8)"
          [product]="product"
          (addToCart)="onAddToCart($event)"
        ></app-product-card>
      </div>

      <ng-template #skeleton>
        <div class="product-grid">
          <mat-card *ngFor="let i of [1,2,3,4]" class="skeleton-card">
            <div class="skeleton-img"></div>
            <mat-card-content>
              <div class="skeleton-text"></div>
              <div class="skeleton-text short"></div>
            </mat-card-content>
          </mat-card>
        </div>
      </ng-template>
    </div>

    <!-- Weekly Offers -->
    <div class="weekly-offers-section" *ngIf="weeklyOffers.length > 0">
      <div class="container section">
        <div class="section-header">
          <h2 class="section-title">🔥 Weekly Offers</h2>
          <a mat-button routerLink="/offers">View All <mat-icon>arrow_forward</mat-icon></a>
        </div>
        <div class="product-grid">
          <app-product-card
            *ngFor="let product of weeklyOffers.slice(0, 4)"
            [product]="product"
            (addToCart)="onAddToCart($event)"
          ></app-product-card>
        </div>
      </div>
    </div>

    <!-- Reviews -->
    <div class="container section">
      <h2 class="section-title text-center">What Our Customers Say</h2>
      <div class="reviews-grid">
        <mat-card *ngFor="let review of reviews" class="review-card">
          <mat-card-content>
            <p class="review-stars">{{ '⭐'.repeat(review.rating) }}</p>
            <p class="review-text">"{{ review.review }}"</p>
            <p class="review-author">— {{ review.name }}</p>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .hero {
      background: linear-gradient(135deg, #1a237e 0%, #534bae 100%);
      color: white;
      padding: 80px 24px;
      text-align: center;
    }
    .hero-content { max-width: 600px; margin: 0 auto; }
    .hero-title { font-size: 2.5rem; font-weight: 700; margin: 0 0 16px; }
    .hero-sub { font-size: 1.2rem; opacity: 0.9; margin: 0 0 32px; }
    .hero-btn { font-size: 1rem; padding: 12px 32px; }
    .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
    .section { padding: 48px 24px; }
    .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .section-title { font-size: 1.75rem; font-weight: 700; margin: 0; }
    .text-center { text-align: center; margin-bottom: 24px; }
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 24px; }
    .offers-banner { background: linear-gradient(90deg, #ff6f00, #ff8f00) !important; color: white; margin-top: -24px; position: relative; z-index: 1; border-radius: 12px !important; }
    .offers-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
    .offers-left { display: flex; align-items: center; gap: 16px; color: white; }
    .offer-icon { font-size: 40px; width: 40px; height: 40px; }
    .offer-name { margin: 0; font-size: 1.3rem; font-weight: 700; color: white; }
    .offer-desc { margin: 0; color: white; opacity: 0.9; }
    .view-offers-btn { background: white !important; color: #ff6f00 !important; }
    .weekly-offers-section { background: #f0f4ff; }
    .reviews-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; }
    .review-card { text-align: center; }
    .review-stars { font-size: 1.2rem; margin: 0 0 12px; }
    .review-text { font-style: italic; margin: 0 0 12px; }
    .review-author { color: #1a237e; font-weight: 600; margin: 0; }
    .skeleton-card { height: 280px; }
    .skeleton-img { height: 180px; background: #e0e0e0; border-radius: 4px 4px 0 0; }
    .skeleton-text { height: 16px; background: #e0e0e0; margin: 12px 0; border-radius: 4px; }
    .skeleton-text.short { width: 60%; }
  `],
})
export class HomeComponent implements OnInit {
  products: Product[] = [];
  offers: OfferData[] = [];
  weeklyOffers: Product[] = [];
  loading = true;

  reviews = [
    { name: 'Rahul S.', review: 'Amazing quality jerseys! Fast delivery and great prices.', rating: 5 },
    { name: 'Priya M.', review: 'Best sports store in town. Love the collection!', rating: 5 },
    { name: 'Amit K.', review: 'Great offers and excellent customer service.', rating: 4 },
  ];

  constructor(private productService: ProductService, private cart: CartService) {}

  ngOnInit(): void {
    forkJoin({
      home: this.productService.getHomeData(),
      offers: this.productService.getActiveOffers(),
      weekly: this.productService.getWeeklyOffers(),
    }).subscribe({
      next: ({ home, offers, weekly }) => {
        this.products = home.products || [];
        this.offers = offers || [];
        this.weeklyOffers = weekly || [];
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
  }

  onAddToCart(product: Product): void {
    this.cart.addToCart(product);
  }
}
