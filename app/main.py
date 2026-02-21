import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, orders
from app.core.logging import logger
from dotenv import load_dotenv

app = FastAPI(title="SSMS API")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception for request {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

# Mount the 'images' directory to serve static files
app.mount("/images", StaticFiles(directory="images"), name="images")

# Load .env variables
load_dotenv()

# Get CORS URLs as a list
cors_urls = os.getenv("CORS_URLS", "")
origins = [url.strip() for url in cors_urls.split(",") if url.strip()]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    auth,
    orders,
    payments,
    vendors,
    delivery,
    dashboard,
    home,
    stock,
    system,
    events,
    day_management,
    tags,
    users,
    pricelist
)

# Include all routers
app.include_router(system.router, prefix="/system", tags=["system"])
app.include_router(day_management.router, prefix="/day-management", tags=["day-management"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(events.router, prefix="/events", tags=["events"])
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
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(pricelist.router, prefix="/pricelists", tags=["pricelists"])

@app.get("/")
def read_root():
    return {"message": "CORS URLs configured", "allowed_origins": origins}
