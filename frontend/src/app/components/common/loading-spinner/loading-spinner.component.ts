import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  standalone: false,
  template: `
    <div class="spinner-wrapper">
      <mat-spinner color="primary"></mat-spinner>
      <p class="spinner-message">{{ message }}</p>
    </div>
  `,
  styles: [`
    .spinner-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      gap: 16px;
    }
    .spinner-message { color: #666; }
  `],
})
export class LoadingSpinnerComponent {
  @Input() message = 'Loading...';
}
