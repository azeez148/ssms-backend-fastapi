from enum import Enum

class SaleStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"
    RETURNED = "RETURNED"

class UserRole(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    STAFF = "STAFF"