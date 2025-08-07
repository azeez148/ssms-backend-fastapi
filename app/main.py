import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SSMS API")

# Mount the 'images' directory to serve static files
app.mount("/images", StaticFiles(directory="images"), name="images")
CORS_URLS = os.getenv("CORS_URLS", "http://localhost:4200").split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_URLS,  # Angular frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api import (
    products,
    categories,
    # attributes,
    sales,
    customers,
    purchases,
    shops,
    payments,
    vendors,
    delivery,
    dashboard,
    home,
    stock,
    system
)

# Include all routers
app.include_router(system.router, prefix="/system", tags=["system"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(purchases.router, prefix="/purchases", tags=["purchases"])
app.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
app.include_router(shops.router, prefix="/shops", tags=["shops"])
app.include_router(payments.router, prefix="/paymentType", tags=["payments"])
app.include_router(delivery.router, prefix="/deliveryType", tags=["delivery"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(home.router, prefix="/public", tags=["public"])

@app.get("/")
async def root():
    return {"message": "Welcome to SSMS API"}
