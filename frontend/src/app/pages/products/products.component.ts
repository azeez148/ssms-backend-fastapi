import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { forkJoin, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Product, Category } from '../../models';
import { ProductService } from '../../services/product.service';
import * as CartActions from '../../store/cart/cart.actions';
import * as FavoritesActions from '../../store/favorites/favorites.actions';
import { selectFavoriteIds } from '../../store/favorites/favorites.selectors';

@Component({
  selector: 'app-products',
  standalone: false,
  template: `
    <div class="container">
      <h1 class="page-title">All Products</h1>

      <div class="toolbar">
        <div class="search-wrapper">
          <app-search-bar placeholder="Search products..." (search)="onSearch($event)"></app-search-bar>
        </div>
        <app-filter-bar
          [categories]="categories"
          [selectedCategory]="selectedCategory"
          [sortBy]="sortBy"
          (categoryChange)="onCategoryChange($event)"
          (sortChange)="onSortChange($event)"
        ></app-filter-bar>
      </div>

      <app-loading-spinner *ngIf="loading" message="Loading products..."></app-loading-spinner>

      <ng-container *ngIf="!loading">
        <p class="result-count">{{ filteredProducts.length }} product{{ filteredProducts.length !== 1 ? 's' : '' }} found</p>

        <div class="product-grid" *ngIf="filteredProducts.length > 0; else noProducts">
          <app-product-card
            *ngFor="let product of filteredProducts"
            [product]="product"
            [isFavorite]="favorites.includes(product.id)"
            [showFavorite]="true"
            (addToCart)="onAddToCart($event)"
            (toggleFavorite)="onToggleFavorite($event)"
            (viewDetails)="onViewDetails($event)"
          ></app-product-card>
        </div>

        <ng-template #noProducts>
          <div class="empty-state">
            <mat-icon class="empty-icon">search_off</mat-icon>
            <p>No products found matching your criteria</p>
          </div>
        </ng-template>
      </ng-container>
    </div>
  `,
  styles: [`
    .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
    .page-title { font-size: 2rem; font-weight: 700; margin: 0 0 24px; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; }
    .search-wrapper { flex: 1; min-width: 200px; }
    .result-count { color: #666; margin: 0 0 16px; }
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 24px; }
    .empty-state { text-align: center; padding: 64px; color: #999; }
    .empty-icon { font-size: 64px; width: 64px; height: 64px; margin-bottom: 16px; }
  `],
})
export class ProductsComponent implements OnInit, OnDestroy {
  products: Product[] = [];
  categories: Category[] = [];
  loading = true;
  search = '';
  selectedCategory = '';
  sortBy = '';
  favorites: number[] = [];
  private destroy$ = new Subject<void>();

  constructor(
    private productService: ProductService,
    private store: Store,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.store.select(selectFavoriteIds).pipe(takeUntil(this.destroy$))
      .subscribe((ids) => (this.favorites = ids));

    forkJoin({
      products: this.productService.getAllProducts(),
      categories: this.productService.getCategories(),
    }).subscribe({
      next: ({ products, categories }) => {
        this.products = products.filter((p) => p.is_active && p.can_listed);
        this.categories = categories;
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
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.description?.toLowerCase().includes(q) ||
          p.category?.name.toLowerCase().includes(q)
      );
    }

    if (this.selectedCategory) {
      result = result.filter((p) => String(p.category_id) === this.selectedCategory);
    }

    switch (this.sortBy) {
      case 'price_low': result.sort((a, b) => a.selling_price - b.selling_price); break;
      case 'price_high': result.sort((a, b) => b.selling_price - a.selling_price); break;
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

  onToggleFavorite(product: Product): void {
    this.store.dispatch(FavoritesActions.toggleFavorite({ productId: product.id }));
  }

  onViewDetails(product: Product): void {
    this.router.navigate(['/products', product.id]);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
