import { Component, Input } from '@angular/core';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-whatsapp-button',
  standalone: false,
  template: `
    <button
      mat-fab
      class="whatsapp-fab"
      matTooltip="Chat with us on WhatsApp"
      matTooltipPosition="left"
      (click)="openWhatsApp()"
      aria-label="Chat on WhatsApp"
    >
      <span class="whatsapp-icon">💬</span>
    </button>
  `,
  styles: [`
    .whatsapp-fab {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      background-color: #25D366 !important;
      color: white !important;
      width: 60px;
      height: 60px;
    }
    .whatsapp-fab:hover { background-color: #128C7E !important; }
  `],
})
export class WhatsappButtonComponent {
  @Input() phoneNumber: string = environment.whatsappNumber;
  @Input() message = 'Hello! I would like to inquire about products.';

  openWhatsApp(): void {
    const encoded = encodeURIComponent(this.message);
    window.open(`https://wa.me/${this.phoneNumber}?text=${encoded}`, '_blank');
  }
}
