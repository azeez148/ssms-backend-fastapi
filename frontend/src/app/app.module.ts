import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

// NgRx
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { authReducer } from './store/auth/auth.reducer';
import { cartReducer } from './store/cart/cart.reducer';
import { favoritesReducer } from './store/favorites/favorites.reducer';
import { AuthEffects } from './store/auth/auth.effects';
import { CartEffects } from './store/cart/cart.effects';
import { FavoritesEffects } from './store/favorites/favorites.effects';
import { environment } from '../environments/environment';

// Angular Material
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatBadgeModule } from '@angular/material/badge';
import { MatMenuModule } from '@angular/material/menu';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthInterceptor } from './services/auth.interceptor';

// Layout
import { LayoutComponent } from './components/layout/layout/layout.component';
import { HeaderComponent } from './components/layout/header/header.component';
import { FooterComponent } from './components/layout/footer/footer.component';

// Common
import { SearchBarComponent } from './components/common/search-bar/search-bar.component';
import { FilterBarComponent } from './components/common/filter-bar/filter-bar.component';
import { ProductCardComponent } from './components/common/product-card/product-card.component';
import { LoadingSpinnerComponent } from './components/common/loading-spinner/loading-spinner.component';
import { WhatsappButtonComponent } from './components/common/whatsapp-button/whatsapp-button.component';

// Pages
import { HomeComponent } from './pages/home/home.component';
import { ProductsComponent } from './pages/products/products.component';
import { OffersComponent } from './pages/offers/offers.component';
import { CartComponent } from './pages/cart/cart.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { ProductDetailComponent } from './pages/product-detail/product-detail.component';

const MATERIAL_MODULES = [
  MatToolbarModule,
  MatButtonModule,
  MatIconModule,
  MatBadgeModule,
  MatMenuModule,
  MatSidenavModule,
  MatListModule,
  MatCardModule,
  MatFormFieldModule,
  MatInputModule,
  MatSelectModule,
  MatChipsModule,
  MatProgressSpinnerModule,
  MatDividerModule,
  MatStepperModule,
  MatTooltipModule,
  MatSnackBarModule,
];

@NgModule({
  declarations: [
    AppComponent,
    LayoutComponent,
    HeaderComponent,
    FooterComponent,
    SearchBarComponent,
    FilterBarComponent,
    ProductCardComponent,
    LoadingSpinnerComponent,
    WhatsappButtonComponent,
    HomeComponent,
    ProductsComponent,
    OffersComponent,
    CartComponent,
    LoginComponent,
    RegisterComponent,
    ProfileComponent,
    ProductDetailComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    AppRoutingModule,
    ...MATERIAL_MODULES,
    StoreModule.forRoot({
      auth: authReducer,
      cart: cartReducer,
      favorites: favoritesReducer,
    }),
    EffectsModule.forRoot([AuthEffects, CartEffects, FavoritesEffects]),
    StoreDevtoolsModule.instrument({
      maxAge: 25,
      logOnly: environment.production,
    }),
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}

