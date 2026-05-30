import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Product, Category, HomeData, OfferData, EventOffer } from '../models';

@Injectable({ providedIn: 'root' })
export class ProductService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getAllProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.baseUrl}/products/all`);
  }

  getHomeData(): Observable<HomeData> {
    return this.http.get<HomeData>(`${this.baseUrl}/public/all`);
  }

  getActiveOffers(): Observable<OfferData[]> {
    return this.http.get<OfferData[]>(`${this.baseUrl}/public/offers`);
  }

  getWeeklyOffers(): Observable<Product[]> {
    return this.http.get<Product[]>(`${this.baseUrl}/public/weeklyOffers`);
  }

  getProductImageUrl(productId: number): string {
    return `${this.baseUrl}/public/${productId}/image`;
  }

  getEvents(): Observable<EventOffer[]> {
    return this.http.get<EventOffer[]>(`${this.baseUrl}/events/all`);
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.baseUrl}/categories/all`);
  }
}
