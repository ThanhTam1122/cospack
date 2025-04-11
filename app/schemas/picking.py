from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PickingStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class PickingDetailStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SHORT = "short"


class PickingWorkStatus(str, Enum):
    ASSIGNED = "assigned"
    STARTED = "started"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Picking Detail Schemas
class PickingDetailBase(BaseModel):
    PickingID: str
    LineNumber: int
    ItemCode: str
    ItemDescription: Optional[str] = None
    UOM: str
    LocationCode: Optional[str] = None
    OrderQuantity: float
    PickedQuantity: float = 0
    Status: PickingDetailStatus
    BatchNumber: Optional[str] = None
    SerialNumber: Optional[str] = None
    ExpiryDate: Optional[datetime] = None
    AssignedTo: Optional[str] = None
    IsCompleted: bool = False
    CompletedDate: Optional[datetime] = None
    Notes: Optional[str] = None


class PickingDetailCreate(PickingDetailBase):
    CreatedBy: str


class PickingDetailUpdate(BaseModel):
    ItemDescription: Optional[str] = None
    LocationCode: Optional[str] = None
    PickedQuantity: Optional[float] = None
    Status: Optional[PickingDetailStatus] = None
    BatchNumber: Optional[str] = None
    SerialNumber: Optional[str] = None
    ExpiryDate: Optional[datetime] = None
    AssignedTo: Optional[str] = None
    IsCompleted: Optional[bool] = None
    CompletedDate: Optional[datetime] = None
    Notes: Optional[str] = None
    ModifiedBy: str


class PickingDetail(PickingDetailBase):
    ID: int
    CreatedBy: str
    CreatedDate: datetime
    ModifiedBy: Optional[str] = None
    ModifiedDate: Optional[datetime] = None

    class Config:
        orm_mode = True


# Picking Work Schemas
class PickingWorkBase(BaseModel):
    WorkID: str
    PickingID: str
    EmployeeID: str
    EmployeeName: Optional[str] = None
    StartTime: Optional[datetime] = None
    EndTime: Optional[datetime] = None
    Status: PickingWorkStatus
    ItemsAssigned: int = 0
    ItemsCompleted: int = 0
    WorkZone: Optional[str] = None
    DeviceID: Optional[str] = None
    SupervisorID: Optional[str] = None
    SupervisorName: Optional[str] = None
    IsVerified: bool = False
    VerifiedBy: Optional[str] = None
    VerifiedDate: Optional[datetime] = None
    Notes: Optional[str] = None


class PickingWorkCreate(PickingWorkBase):
    CreatedBy: str


class PickingWorkUpdate(BaseModel):
    EmployeeName: Optional[str] = None
    StartTime: Optional[datetime] = None
    EndTime: Optional[datetime] = None
    Status: Optional[PickingWorkStatus] = None
    ItemsAssigned: Optional[int] = None
    ItemsCompleted: Optional[int] = None
    WorkZone: Optional[str] = None
    DeviceID: Optional[str] = None
    SupervisorID: Optional[str] = None
    SupervisorName: Optional[str] = None
    IsVerified: Optional[bool] = None
    VerifiedBy: Optional[str] = None
    VerifiedDate: Optional[datetime] = None
    Notes: Optional[str] = None
    ModifiedBy: str


class PickingWork(PickingWorkBase):
    ID: int
    CreatedBy: str
    CreatedDate: datetime
    ModifiedBy: Optional[str] = None
    ModifiedDate: Optional[datetime] = None

    class Config:
        orm_mode = True


# Picking Management Schemas
class PickingManagementBase(BaseModel):
    PickingID: str
    CustomerID: str
    CustomerName: Optional[str] = None
    OrderNumber: str
    OrderDate: Optional[datetime] = None
    RequestDate: Optional[datetime] = None
    ShipDate: Optional[datetime] = None
    Status: PickingStatus
    WarehouseID: str
    TotalItems: int = 0
    TotalQuantity: float = 0
    CompletedItems: int = 0
    CompletedQuantity: float = 0
    Priority: int = 0
    IsUrgent: bool = False
    Notes: Optional[str] = None
    IsActive: bool = True


class PickingManagementCreate(PickingManagementBase):
    CreatedBy: str
    details: Optional[List[PickingDetailCreate]] = None


class PickingManagementUpdate(BaseModel):
    CustomerName: Optional[str] = None
    OrderDate: Optional[datetime] = None
    RequestDate: Optional[datetime] = None
    ShipDate: Optional[datetime] = None
    Status: Optional[PickingStatus] = None
    TotalItems: Optional[int] = None
    TotalQuantity: Optional[float] = None
    CompletedItems: Optional[int] = None
    CompletedQuantity: Optional[float] = None
    Priority: Optional[int] = None
    IsUrgent: Optional[bool] = None
    Notes: Optional[str] = None
    IsActive: Optional[bool] = None
    ModifiedBy: str


class PickingManagement(PickingManagementBase):
    ID: int
    CreatedBy: str
    CreatedDate: datetime
    ModifiedBy: Optional[str] = None
    ModifiedDate: Optional[datetime] = None
    details: Optional[List[PickingDetail]] = None
    works: Optional[List[PickingWork]] = None

    class Config:
        orm_mode = True 