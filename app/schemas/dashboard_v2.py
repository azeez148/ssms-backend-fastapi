from pydantic import BaseModel
from typing import List, Optional


class KpiStats(BaseModel):
    total_revenue: float
    growth: float
    traffic: int
    avg_ticket_size: float
    store_performance_index: float

    class Config:
        from_attributes = True


class CategorySplit(BaseModel):
    footwear: float
    apparel: float
    other: float

    class Config:
        from_attributes = True


class Transaction(BaseModel):
    id: str
    customer: str
    item: str
    amount: float
    time: str
    status: str

    class Config:
        from_attributes = True


class BranchData(BaseModel):
    id: str
    name: str
    sales: float
    split: CategorySplit
    recent_transactions: List[Transaction]

    class Config:
        from_attributes = True


class TopProduct(BaseModel):
    name: str
    units: int

    class Config:
        from_attributes = True


class TrafficHeatmap(BaseModel):
    Mon: int
    Tue: int
    Wed: int
    Thu: int
    Fri: int
    Sat: int
    Sun: int

    class Config:
        from_attributes = True


class DashboardV2Response(BaseModel):
    view: str
    kpi_stats: KpiStats
    branch_data: List[BranchData]
    top_products: List[TopProduct]
    traffic_heatmap: TrafficHeatmap

    class Config:
        from_attributes = True
