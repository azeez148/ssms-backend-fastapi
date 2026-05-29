# Adrenaline Sports Store - Frontend

A customer-facing React application for the Adrenaline Sports Store retail shop.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Material UI (MUI)** for UI components
- **React Router** for navigation
- **Axios** for API communication
- **Context API** for state management (Auth + Cart)

## Features

1. **Home Page** - Hero banner, new products, weekly offers, customer reviews
2. **Products Page** - All products with search, filter by category, sort options, add to cart, favorites
3. **Offers Page** - Active events/offers with product listings, search, filter, sort
4. **Cart Page** - Add/remove items, update quantity, 3-step checkout (Cart → Address → WhatsApp order)
5. **Login/Register** - Mobile number based authentication
6. **Profile** - View/edit profile, logout (protected - login required)
7. **Floating WhatsApp** - Quick contact button on all pages

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Configuration

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Environment variables:
- `VITE_API_URL` - Backend API URL (default: `/api` which proxies to `http://localhost:8000`)
- `VITE_WHATSAPP_NUMBER` - Admin WhatsApp number for order messages

### Development

```bash
npm run dev
```

The app runs on `http://localhost:3000` and proxies API requests to the FastAPI backend on port 8000.

### Production Build

```bash
npm run build
```

Build output will be in the `dist/` directory.

## Architecture

```
src/
├── components/
│   ├── common/          # Reusable components (ProductCard, SearchBar, FilterBar, etc.)
│   └── layout/          # Layout components (Header, Footer, Layout)
├── context/             # React Context (AuthContext, CartContext)
├── pages/               # Page components
├── services/            # API service layer
├── theme/               # MUI theme customization
└── types/               # TypeScript type definitions
```

## Theme Customization

The app uses a customizable MUI theme defined in `src/theme/index.ts`. Key customization points:
- **Primary color**: Deep blue (`#1a237e`)
- **Secondary color**: Orange (`#ff6f00`)
- **Font**: Poppins
- **Border radius**: 8px
- **Card hover effects**: Elevation + translateY animation

## Flow

1. Users can browse Home, Products, and Offers pages without logging in
2. Profile page requires authentication
3. Cart checkout redirects to login if not authenticated
4. Order placement sends a formatted WhatsApp message to the admin with order details
