from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str
    name: str
    role: str = "user"


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    category: Optional[str] = None
    min_threshold: int = 5
    unit: str = "个"


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    min_threshold: Optional[int] = None
    unit: Optional[str] = None


class Item(ItemBase):
    id: int
    total_quantity: int
    available_quantity: int
    borrowed_quantity: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BorrowRecordBase(BaseModel):
    item_id: int
    quantity: int
    purpose: Optional[str] = None
    expected_return_date: Optional[datetime] = None


class BorrowRecordCreate(BorrowRecordBase):
    borrower_id: int


class BorrowRecord(BorrowRecordBase):
    id: int
    borrower_id: int
    actual_return_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    borrower: Optional[User] = None

    class Config:
        from_attributes = True


class StockRecordBase(BaseModel):
    item_id: int
    quantity: int
    type: str
    remark: Optional[str] = None


class StockRecordCreate(StockRecordBase):
    operator_id: int


class StockRecord(StockRecordBase):
    id: int
    operator_id: int
    created_at: datetime
    operator: Optional[User] = None

    class Config:
        from_attributes = True


class ApprovalBase(BaseModel):
    item_id: int
    record_type: str
    quantity: int
    remark: Optional[str] = None


class ApprovalCreate(ApprovalBase):
    applicant_id: int
    record_id: Optional[int] = None


class ApprovalProcess(BaseModel):
    status: str
    approval_remark: Optional[str] = None
    approver_id: int


class Approval(ApprovalBase):
    id: int
    applicant_id: int
    approver_id: Optional[int] = None
    status: str
    approval_remark: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None
    applicant: Optional[User] = None
    approver: Optional[User] = None

    class Config:
        from_attributes = True


class OperationLogBase(BaseModel):
    action: str
    target_type: str
    target_id: int
    detail: Optional[str] = None


class OperationLogCreate(OperationLogBase):
    operator_id: int
    ip_address: Optional[str] = None


class OperationLog(OperationLogBase):
    id: int
    operator_id: int
    ip_address: Optional[str] = None
    created_at: datetime
    operator: Optional[User] = None

    class Config:
        from_attributes = True


class StockInRequest(BaseModel):
    item_id: int
    quantity: int
    operator_id: int
    remark: Optional[str] = None
    need_approval: bool = False


class BorrowRequest(BaseModel):
    item_id: int
    quantity: int
    borrower_id: int
    purpose: Optional[str] = None
    expected_return_date: Optional[datetime] = None
    need_approval: bool = True


class ReturnRequest(BaseModel):
    record_id: int
    operator_id: int
    quantity: Optional[int] = None


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
