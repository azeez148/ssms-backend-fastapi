import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { forkJoin } from 'rxjs';
import { Product, Category, EventOffer } from '../../models';
import { ProductService } from '../../services/product.service';
import * as CartActions from '../../store/cart/cart.actions';

@Component({
  selector: 'app-offers',
  standalone: false,
  template: `
    <div class="container">
      <h1 class="page-title">Offers &amp; Events</h1>

      <!-- Active Events -->
      <div class="events-grid" *ngIf="events.length > 0">
        <mat-card *ngFor="let event of events" class="event-card">
          <mat-card-content>
            <h3 class="event-name">{{ event.name }}</h3>
            <p class="event-desc">{{ event.description }}</p>
            <mat-chip-set>
              <mat-chip highlighted color="accent">
                {{ event.rate }}{{ event.rate_type === 'PERCENTAGE' ? '%' : '₹' }} OFF
              </mat-chip>
            </mat-chip-set>
          </mat-card-content>
        </mat-card>
      </div>

      <div class="toolbar">
        <div class="search-wrapper">
          <app-search-bar placeholder="Search offers..." (search)="onSearch($event)"></app-search-bar>
        </div>
        <app-filter-bar
          [categories]="categories"
          [selectedCategory]="selectedCategory"
          [sortBy]="sortBy"
          (categoryChange)="onCategoryChange($event)"
          (sortChange)="onSortChange($event)"
        ></app-filter-bar>
      </div>

      <app-loading-spinner *ngIf="loading" message="Loading offers..."></app-loading-spinner>

      <ng-container *ngIf="!loading">
        <p class="result-count">{{ filteredProducts.length }} offer product{{ filteredProducts.length !== 1 ? 's' : '' }} found</p>

        <div class="product-grid" *ngIf="filteredProducts.length > 0; else noOffers">
          <app-product-card
            *ngFor="let product of filteredProducts"
            [product]="product"
            (addToCart)="onAddToCart($event)"
            (viewDetails)="onViewDetails($event)"
          ></app-product-card>
        </div>

        <ng-template #noOffers>
          <div class="empty-state">
            <mat-icon class="empty-icon">local_offer</mat-icon>
            <p>No offer products available right now</p>
          </div>
        </ng-template>
      </ng-container>
    </div>
  `,
  styles: [`
    .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
    .page-title { font-size: 2rem; font-weight: 700; margin: 0 0 24px; }
    .events-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-bottom: 32px; }
    .event-card { background: linear-gradient(135deg, #ff6f00, #ff8f00) !important; color: white !important; }
    .event-name { margin: 0 0 8px; font-size: 1.1rem; font-weight: 700; color: white; }
    .event-desc { margin: 0 0 12px; color: white; opacity: 0.9; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; }
    .search-wrapper { flex: 1; min-width: 200px; }
    .result-count { color: #666; margin: 0 0 16px; }
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 24px; }
    .empty-state { text-align: center; padding: 64px; color: #999; }
    .empty-icon { font-size: 64px; width: 64px; height: 64px; margin-bottom: 16px; }
  `],
})
export class OffersComponent implements OnInit {
  products: Product[] = [];
  events: EventOffer[] = [];
  categories: Category[] = [];
  loading = true;
  search = '';
  selectedCategory = '';
  sortBy = '';

  constructor(
    private productService: ProductService,
    private store: Store,
    private router: Router
  ) {}

  ngOnInit(): void {
    forkJoin({
      weekly: this.productService.getWeeklyOffers(),
      events: this.productService.getEvents(),
      categories: this.productService.getCategories(),
    }).subscribe({
      next: ({ weekly, events, categories }) => {
        this.products = weekly || [];
        this.events = (events || []).filter((e: EventOffer) => e.is_active);
        this.categories = categories || [];
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
  }

  get filteredProducts(): Product[] {
    let result = [...this.products];

    if (this.search) {
      const q = this.search.toLowerCase();
      result = result.filter(
        (p) => p.name.toLowerCase().includes(q) || p.offer_name?.toLowerCase().includes(q)
      );
    }

    if (this.selectedCategory) {
      result = result.filter((p) => String(p.category_id) === this.selectedCategory);
    }

    switch (this.sortBy) {
      case 'price_low': result.sort((a, b) => (a.offer_price ?? a.selling_price) - (b.offer_price ?? b.selling_price)); break;
      case 'price_high': result.sort((a, b) => (b.offer_price ?? b.selling_price) - (a.offer_price ?? a.selling_price)); break;
      case 'name_asc': result.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'name_desc': result.sort((a, b) => b.name.localeCompare(a.name)); break;
    }

    return result;
  }

  onSearch(q: string): void { this.search = q; }
  onCategoryChange(cat: string): void { this.selectedCategory = cat; }
  onSortChange(sort: string): void { this.sortBy = sort; }

  onAddToCart(event: { product: Product; size?: string }): void {
    this.store.dispatch(CartActions.addToCart({ product: event.product, quantity: 1, size: event.size }));
  }

  onViewDetails(product: Product): void {
    this.router.navigate(['/products', product.id]);
  }
}
