import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Category } from '../../../models';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-filter-bar',
  standalone: false,
  template: `
    <div class="filter-bar">
      <mat-form-field appearance="outline" class="filter-select">
        <mat-label>Category</mat-label>
        <mat-select [(ngModel)]="selectedCategory" (ngModelChange)="categoryChange.emit($event)">
          <mat-option value="">All Categories</mat-option>
          <mat-option *ngFor="let cat of categories" [value]="cat.id.toString()">
            {{ cat.name }}
          </mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline" class="filter-select">
        <mat-label>Sort By</mat-label>
        <mat-select [(ngModel)]="sortBy" (ngModelChange)="sortChange.emit($event)">
          <mat-option value="">Default</mat-option>
          <mat-option value="price_low">Price: Low to High</mat-option>
          <mat-option value="price_high">Price: High to Low</mat-option>
          <mat-option value="name_asc">Name: A-Z</mat-option>
          <mat-option value="name_desc">Name: Z-A</mat-option>
        </mat-select>
      </mat-form-field>
    </div>
  `,
  styles: [`
    .filter-bar { display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }
    .filter-select { min-width: 150px; }
  `],
})
export class FilterBarComponent {
  @Input() categories: Category[] = [];
  @Input() selectedCategory = '';
  @Input() sortBy = '';
  @Output() categoryChange = new EventEmitter<string>();
  @Output() sortChange = new EventEmitter<string>();
}
