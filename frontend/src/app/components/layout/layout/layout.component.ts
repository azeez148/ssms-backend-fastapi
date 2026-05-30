import { Component } from '@angular/core';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-layout',
  standalone: false,
  template: `
    <div class="app-shell">
      <app-header></app-header>
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
      <app-footer></app-footer>
      <app-whatsapp-button [phoneNumber]="whatsappNumber"></app-whatsapp-button>
    </div>
  `,
  styles: [`
    .app-shell { display: flex; flex-direction: column; min-height: 100vh; }
    .main-content { flex: 1; }
  `],
})
export class LayoutComponent {
  whatsappNumber = environment.whatsappNumber;
}
