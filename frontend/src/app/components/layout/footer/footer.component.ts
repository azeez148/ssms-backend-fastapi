import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: false,
  template: `
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-grid">
          <div class="footer-section">
            <h3 class="footer-title">🏆 ADRENALINE STORE</h3>
            <p class="footer-text">
              Your one-stop destination for premium sports gear, jerseys, and accessories.
            </p>
          </div>
          <div class="footer-section">
            <h4 class="footer-subtitle">Quick Links</h4>
            <a routerLink="/products" class="footer-link">All Products</a>
            <a routerLink="/offers" class="footer-link">Offers &amp; Events</a>
            <a routerLink="/cart" class="footer-link">My Cart</a>
          </div>
          <div class="footer-section">
            <h4 class="footer-subtitle">Contact Us</h4>
            <div class="contact-row">
              <mat-icon class="contact-icon">phone</mat-icon>
              <span>+91 XXXXXXXXXX</span>
            </div>
            <div class="contact-row">
              <mat-icon class="contact-icon">email</mat-icon>
              <span>info&#64;adrenalinestore.com</span>
            </div>
            <div class="contact-row">
              <mat-icon class="contact-icon">location_on</mat-icon>
              <span>Sports City, India</span>
            </div>
          </div>
        </div>
        <mat-divider class="footer-divider"></mat-divider>
        <p class="footer-copy">
          &copy; {{ currentYear }} Adrenaline Sports Store. All rights reserved.
        </p>
      </div>
    </footer>
  `,
  styles: [`
    .footer { background-color: #000051; color: white; padding: 32px 0 16px; margin-top: auto; }
    .footer-content { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
    .footer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 32px; }
    .footer-section { display: flex; flex-direction: column; }
    .footer-title { font-size: 1.2rem; font-weight: 700; margin: 0 0 12px; }
    .footer-subtitle { font-size: 1rem; font-weight: 600; margin: 0 0 12px; }
    .footer-text { opacity: 0.8; font-size: 0.9rem; line-height: 1.5; }
    .footer-link { color: white; opacity: 0.8; text-decoration: none; display: block; margin-bottom: 6px; font-size: 0.9rem; }
    .footer-link:hover { opacity: 1; }
    .contact-row { display: flex; align-items: center; gap: 8px; opacity: 0.8; margin-bottom: 8px; font-size: 0.9rem; }
    .contact-icon { font-size: 18px; width: 18px; height: 18px; }
    .footer-divider { border-color: rgba(255,255,255,0.2); margin: 24px 0 16px; }
    .footer-copy { text-align: center; opacity: 0.6; font-size: 0.85rem; margin: 0; }
  `],
})
export class FooterComponent {
  currentYear = new Date().getFullYear();
}
