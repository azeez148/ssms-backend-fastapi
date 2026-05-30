# SSMS Frontend — Angular

This is the Angular frontend for the Adrenaline Sports Store Management System. It communicates with the FastAPI backend at `/api`.

## Tech Stack

- **Angular 17** (NgModule-based)
- **Angular Material** — UI component library
- **RxJS** — Reactive state management
- **TypeScript**

## Development Setup

```bash
npm install
npm start          # starts dev server at http://localhost:4200
                   # API requests proxied to http://localhost:8000
```

## Build

```bash
npm run build      # production build → dist/ssms-frontend/
```

## Project Structure

```
src/app/
├── models/          # TypeScript interfaces (Product, User, Cart…)
├── services/        # AuthService, CartService, ProductService, AuthInterceptor
├── guards/          # AuthGuard (protects /profile)
├── components/
│   ├── layout/      # Header, Footer, Layout (shell with router-outlet)
│   └── common/      # SearchBar, FilterBar, ProductCard, LoadingSpinner, WhatsAppButton
└── pages/           # Home, Products, Offers, Cart, Login, Register, Profile
```

## Environment Variables

Copy `src/environments/environment.ts` and set:
- `apiUrl` — backend API base URL (default: `/api`)
- `whatsappNumber` — WhatsApp phone number for order placement

## Proxy

In development, `/api/*` is proxied to `http://localhost:8000` via `proxy.conf.json`.
