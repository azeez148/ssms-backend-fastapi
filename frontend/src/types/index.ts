export interface Product {
  id: number;
  name: string;
  description?: string;
  unit_price: number;
  selling_price: number;
  category_id: number;
  is_active: boolean;
  can_listed: boolean;
  size_map?: ProductSize[];
  category: Category;
  image_url?: string;
  offer_id?: number;
  discounted_price?: number;
  offer_price?: number;
  offer_name?: string;
  tags?: Tag[];
  shops?: Shop[];
}

export interface ProductSize {
  size: string;
  quantity: number;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface Shop {
  id: number;
  name: string;
}

export interface EventOffer {
  id: number;
  name: string;
  description?: string;
  type: string;
  is_active: boolean;
  start_date: string;
  end_date: string;
  rate_type: string;
  rate: number;
  product_ids: number[];
  category_ids: number[];
  code?: string;
}

export interface UserProfile {
  id: string;
  mobile: string;
  email?: string;
  role: string;
  first_name: string;
  last_name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  token: string;
  user: UserProfile;
}

export interface CartItem {
  product: Product;
  quantity: number;
  selectedSize?: string;
}

export interface HomeData {
  products: Product[];
}

export interface OfferData {
  id: number;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  rate: number;
  rate_type: string;
  type: string;
}
