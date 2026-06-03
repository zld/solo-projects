from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(50), unique=True, index=True)
    category = Column(String(50), index=True)
    total_quantity = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)
    borrowed_quantity = Column(Integer, default=0)
    min_threshold = Column(Integer, default=5)
    unit = Column(String(20), default="个")
    version = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    borrow_records = relationship("BorrowRecord", back_populates="item")
    stock_records = relationship("StockRecord", back_populates="item")
    approvals = relationship("Approval", back_populates="item")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    name = Column(String(50))
    role = Column(String(20), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    borrower_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, nullable=False)
    purpose = Column(Text)
    expected_return_date = Column(DateTime(timezone=True))
    actual_return_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    item = relationship("Item", back_populates="borrow_records")
    borrower = relationship("User", foreign_keys=[borrower_id])


class StockRecord(Base):
    __tablename__ = "stock_records"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    operator_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, nullable=False)
    type = Column(String(20))
    remark = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="stock_records")
    operator = relationship("User", foreign_keys=[operator_id])


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    record_id = Column(Integer)
    record_type = Column(String(20))
    applicant_id = Column(Integer, ForeignKey("users.id"))
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    quantity = Column(Integer)
    status = Column(String(20), default="pending")
    remark = Column(Text)
    approval_remark = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))

    item = relationship("Item", back_populates="approvals")
    applicant = relationship("User", foreign_keys=[applicant_id])
    approver = relationship("User", foreign_keys=[approver_id])


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))
    target_type = Column(String(50))
    target_id = Column(Integer)
    detail = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    operator = relationship("User")
