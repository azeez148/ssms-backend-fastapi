import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { CartItem, Product } from '../models';

@Injectable({ providedIn: 'root' })
export class CartService {
  private itemsSubject = new BehaviorSubject<CartItem[]>(this.loadCart());

  items$ = this.itemsSubject.asObservable();

  get items(): CartItem[] {
    return this.itemsSubject.value;
  }

  private loadCart(): CartItem[] {
    const raw = localStorage.getItem('cart');
    return raw ? JSON.parse(raw) : [];
  }

  private persist(items: CartItem[]): void {
    localStorage.setItem('cart', JSON.stringify(items));
    this.itemsSubject.next(items);
  }

  addToCart(product: Product, quantity = 1, size?: string): void {
    const current = this.items;
    const idx = current.findIndex(
      (i) => i.product.id === product.id && i.selectedSize === size
    );
    if (idx >= 0) {
      const updated = current.map((item, i) =>
        i === idx ? { ...item, quantity: item.quantity + quantity } : item
      );
      this.persist(updated);
    } else {
      this.persist([...current, { product, quantity, selectedSize: size }]);
    }
  }

  removeFromCart(productId: number): void {
    this.persist(this.items.filter((i) => i.product.id !== productId));
  }

  updateQuantity(productId: number, quantity: number): void {
    if (quantity <= 0) {
      this.removeFromCart(productId);
      return;
    }
    this.persist(
      this.items.map((i) => (i.product.id === productId ? { ...i, quantity } : i))
    );
  }

  clearCart(): void {
    this.persist([]);
  }

  getTotal(): number {
    return this.items.reduce((total, item) => {
      const price =
        item.product.offer_price ??
        item.product.discounted_price ??
        item.product.selling_price;
      return total + price * item.quantity;
    }, 0);
  }

  getItemCount(): number {
    return this.items.reduce((count, item) => count + item.quantity, 0);
  }
}
