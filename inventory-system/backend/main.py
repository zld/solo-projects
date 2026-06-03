from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import json

from database import engine, get_db, Base
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="共享仓库库存系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def log_operation(db: Session, operator_id: int, action: str, target_type: str, target_id: int, detail: dict, ip: str = ""):
    log = models.OperationLog(
        operator_id=operator_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=json.dumps(detail, ensure_ascii=False),
        ip_address=ip
    )
    db.add(log)


def get_or_create_user(db: Session, username: str, name: str, role: str = "user"):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        user = models.User(username=username, name=name, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@app.on_event("startup")
def init_data():
    db = next(get_db())
    get_or_create_user(db, "admin", "管理员", "admin")
    get_or_create_user(db, "user1", "张三")
    get_or_create_user(db, "user2", "李四")
    db.close()


@app.get("/")
def root():
    return {"message": "共享仓库库存系统 API"}


@app.get("/api/users", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.post("/api/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/api/items", response_model=List[schemas.Item])
def list_items(category: Optional[str] = None, low_stock: Optional[bool] = False, db: Session = Depends(get_db)):
    query = db.query(models.Item)
    if category:
        query = query.filter(models.Item.category == category)
    if low_stock:
        query = query.filter(models.Item.available_quantity < models.Item.min_threshold)
    return query.order_by(models.Item.id.desc()).all()


@app.get("/api/items/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    return item


@app.post("/api/items", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(models.Item).filter(models.Item.sku == item.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU已存在")
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    client_host = request.client.host if request.client else ""
    log_operation(db, 1, "创建物品", "item", db_item.id, {"name": item.name, "sku": item.sku}, client_host)
    db.commit()
    return db_item


@app.put("/api/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item_update: schemas.ItemUpdate, request: Request, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="物品不存在")
    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    client_host = request.client.host if request.client else ""
    log_operation(db, 1, "更新物品", "item", item_id, item_update.dict(exclude_unset=True), client_host)
    db.commit()
    return db_item


@app.post("/api/stock/in")
def stock_in(request_data: schemas.StockInRequest, request: Request, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == request_data.item_id).with_for_update().first()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    if request_data.need_approval:
        approval = models.Approval(
            item_id=request_data.item_id,
            record_type="stock_in",
            applicant_id=request_data.operator_id,
            quantity=request_data.quantity,
            remark=request_data.remark,
            status="pending"
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return {"success": True, "message": "已提交审批", "data": {"approval_id": approval.id}}
    
    old_version = item.version
    item.total_quantity += request_data.quantity
    item.available_quantity += request_data.quantity
    item.version += 1
    
    if item.version != old_version + 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="数据冲突，请重试")
    
    stock_record = models.StockRecord(
        item_id=request_data.item_id,
        operator_id=request_data.operator_id,
        quantity=request_data.quantity,
        type="in",
        remark=request_data.remark
    )
    db.add(stock_record)
    db.commit()
    db.refresh(stock_record)
    
    client_host = request.client.host if request.client else ""
    log_operation(db, request_data.operator_id, "入库", "item", request_data.item_id, {"quantity": request_data.quantity}, client_host)
    db.commit()
    
    return {"success": True, "message": "入库成功", "data": {"record_id": stock_record.id}}


@app.post("/api/borrow")
def borrow_item(request_data: schemas.BorrowRequest, request: Request, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == request_data.item_id).with_for_update().first()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    if item.available_quantity < request_data.quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    
    if request_data.need_approval:
        approval = models.Approval(
            item_id=request_data.item_id,
            record_type="borrow",
            applicant_id=request_data.borrower_id,
            quantity=request_data.quantity,
            remark=request_data.purpose,
            status="pending"
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return {"success": True, "message": "已提交审批", "data": {"approval_id": approval.id}}
    
    old_version = item.version
    item.available_quantity -= request_data.quantity
    item.borrowed_quantity += request_data.quantity
    item.version += 1
    
    borrow_record = models.BorrowRecord(
        item_id=request_data.item_id,
        borrower_id=request_data.borrower_id,
        quantity=request_data.quantity,
        purpose=request_data.purpose,
        expected_return_date=request_data.expected_return_date,
        status="borrowed"
    )
    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)
    
    client_host = request.client.host if request.client else ""
    log_operation(db, request_data.borrower_id, "借出", "item", request_data.item_id, {"quantity": request_data.quantity}, client_host)
    db.commit()
    
    return {"success": True, "message": "借出成功", "data": {"record_id": borrow_record.id}}


@app.post("/api/return")
def return_item(request_data: schemas.ReturnRequest, request: Request, db: Session = Depends(get_db)):
    borrow_record = db.query(models.BorrowRecord).filter(models.BorrowRecord.id == request_data.record_id).first()
    if not borrow_record:
        raise HTTPException(status_code=404, detail="借出记录不存在")
    if borrow_record.status == "returned":
        raise HTTPException(status_code=400, detail="该记录已归还")
    
    item = db.query(models.Item).filter(models.Item.id == borrow_record.item_id).with_for_update().first()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    return_quantity = request_data.quantity if request_data.quantity else borrow_record.quantity
    if return_quantity > borrow_record.quantity:
        raise HTTPException(status_code=400, detail="归还数量不能超过借出数量")
    
    item.available_quantity += return_quantity
    item.borrowed_quantity -= return_quantity
    item.version += 1
    
    if return_quantity == borrow_record.quantity:
        borrow_record.status = "returned"
    borrow_record.actual_return_date = datetime.now()
    
    db.commit()
    
    client_host = request.client.host if request.client else ""
    log_operation(db, request_data.operator_id, "归还", "item", borrow_record.item_id, {"quantity": return_quantity}, client_host)
    db.commit()
    
    return {"success": True, "message": "归还成功"}


@app.get("/api/borrow-records", response_model=List[schemas.BorrowRecord])
def list_borrow_records(status: Optional[str] = None, borrower_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.BorrowRecord)
    if status:
        query = query.filter(models.BorrowRecord.status == status)
    if borrower_id:
        query = query.filter(models.BorrowRecord.borrower_id == borrower_id)
    return query.order_by(models.BorrowRecord.id.desc()).all()


@app.get("/api/stock-records", response_model=List[schemas.StockRecord])
def list_stock_records(item_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.StockRecord)
    if item_id:
        query = query.filter(models.StockRecord.item_id == item_id)
    return query.order_by(models.StockRecord.id.desc()).all()


@app.get("/api/approvals", response_model=List[schemas.Approval])
def list_approvals(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Approval)
    if status:
        query = query.filter(models.Approval.status == status)
    return query.order_by(models.Approval.id.desc()).all()


@app.post("/api/approvals/{approval_id}/process")
def process_approval(approval_id: int, process_data: schemas.ApprovalProcess, request: Request, db: Session = Depends(get_db)):
    approval = db.query(models.Approval).filter(models.Approval.id == approval_id).with_for_update().first()
    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail="该审批已处理")
    
    approval.status = process_data.status
    approval.approver_id = process_data.approver_id
    approval.approval_remark = process_data.approval_remark
    approval.approved_at = datetime.now()
    
    if process_data.status == "approved":
        item = db.query(models.Item).filter(models.Item.id == approval.item_id).with_for_update().first()
        if not item:
            db.rollback()
            raise HTTPException(status_code=404, detail="物品不存在")
        
        if approval.record_type == "stock_in":
            item.total_quantity += approval.quantity
            item.available_quantity += approval.quantity
            item.version += 1
            
            stock_record = models.StockRecord(
                item_id=approval.item_id,
                operator_id=approval.applicant_id,
                quantity=approval.quantity,
                type="in",
                remark=approval.remark
            )
            db.add(stock_record)
        
        elif approval.record_type == "borrow":
            if item.available_quantity < approval.quantity:
                db.rollback()
                raise HTTPException(status_code=400, detail="库存不足")
            item.available_quantity -= approval.quantity
            item.borrowed_quantity += approval.quantity
            item.version += 1
            
            borrow_record = models.BorrowRecord(
                item_id=approval.item_id,
                borrower_id=approval.applicant_id,
                quantity=approval.quantity,
                purpose=approval.remark,
                status="borrowed"
            )
            db.add(borrow_record)
    
    db.commit()
    
    client_host = request.client.host if request.client else ""
    log_operation(db, process_data.approver_id, f"审批{process_data.status}", "approval", approval_id, {"status": process_data.status}, client_host)
    db.commit()
    
    return {"success": True, "message": "审批完成"}


@app.get("/api/operation-logs", response_model=List[schemas.OperationLog])
def list_operation_logs(target_type: Optional[str] = None, operator_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.OperationLog)
    if target_type:
        query = query.filter(models.OperationLog.target_type == target_type)
    if operator_id:
        query = query.filter(models.OperationLog.operator_id == operator_id)
    return query.order_by(models.OperationLog.id.desc()).limit(100).all()


@app.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    low_stock_items = db.query(models.Item).filter(
        models.Item.available_quantity < models.Item.min_threshold
    ).all()
    
    overdue_borrows = db.query(models.BorrowRecord).filter(
        and_(
            models.BorrowRecord.status == "borrowed",
            models.BorrowRecord.expected_return_date < datetime.now()
        )
    ).all()
    
    pending_approvals = db.query(models.Approval).filter(
        models.Approval.status == "pending"
    ).count()
    
    return {
        "low_stock_count": len(low_stock_items),
        "overdue_count": len(overdue_borrows),
        "pending_approvals": pending_approvals,
        "low_stock_items": [{"id": item.id, "name": item.name, "available": item.available_quantity, "min": item.min_threshold} for item in low_stock_items]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
