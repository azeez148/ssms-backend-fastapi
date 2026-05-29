import api from './api';
import { Product, HomeData, OfferData } from '../types';

export const productService = {
  async getAllProducts(): Promise<Product[]> {
    const response = await api.get('/products/all');
    return response.data;
  },

  async getHomeData(): Promise<HomeData> {
    const response = await api.get('/public/all');
    return response.data;
  },

  async getActiveOffers(): Promise<OfferData[]> {
    const response = await api.get('/public/offers');
    return response.data;
  },

  async getWeeklyOffers(): Promise<Product[]> {
    const response = await api.get('/public/weeklyOffers');
    return response.data;
  },

  getProductImageUrl(productId: number): string {
    return `${api.defaults.baseURL}/public/${productId}/image`;
  },

  async getEvents() {
    const response = await api.get('/events/all');
    return response.data;
  },

  async getCategories() {
    const response = await api.get('/categories/all');
    return response.data;
  },
};
