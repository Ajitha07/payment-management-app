# Backend Implementation using FastAPI

# Install required packages
# pip install fastapi uvicorn pymongo python-multipart pydantic pandas

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, date
from pymongo import MongoClient
from bson import ObjectId
import os
import pandas as pd
from decimal import Decimal

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["payment_db"]
payments_collection = db["payments"]

# Models
class Payment(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str
    payee_added_date_utc: datetime
    payee_due_date: date
    payee_address_line_1: str
    payee_address_line_2: Optional[str]
    payee_city: str
    payee_country: str
    payee_province_or_state: Optional[str]
    payee_postal_code: str
    payee_phone_number: str
    payee_email: EmailStr
    currency: str
    discount_percent: Optional[Decimal] = Field(default=0, ge=0, le=100)
    tax_percent: Optional[Decimal] = Field(default=0, ge=0, le=100)
    due_amount: Decimal

class PaymentUpdate(BaseModel):
    payee_due_date: Optional[date]
    due_amount: Optional[Decimal]
    payee_payment_status: Optional[str]

# Helper function to calculate total due
def calculate_total_due(due_amount, discount_percent, tax_percent):
    discounted = due_amount * (1 - discount_percent / 100)
    taxed = discounted * (1 + tax_percent / 100)
    return round(taxed, 2)

# Routes
@app.post("/create_payment")
async def create_payment(payment: Payment):
    payment_dict = payment.dict()
    payment_dict["total_due"] = calculate_total_due(payment.due_amount, payment.discount_percent, payment.tax_percent)
    result = payments_collection.insert_one(payment_dict)
    return {"message": "Payment created", "id": str(result.inserted_id)}

@app.get("/get_payments")
async def get_payments(status: Optional[str] = None, search: Optional[str] = None, page: int = 1, page_size: int = 10):
    query = {}
    if status:
        query["payee_payment_status"] = status
    if search:
        query["$or"] = [
            {"payee_first_name": {"$regex": search, "$options": "i"}},
            {"payee_last_name": {"$regex": search, "$options": "i"}}
        ]

    payments = list(payments_collection.find(query).skip((page - 1) * page_size).limit(page_size))
    for payment in payments:
        payment["_id"] = str(payment["_id"])
    return {"data": payments}

@app.put("/update_payment/{payment_id}")
async def update_payment(payment_id: str, update: PaymentUpdate):
    updated_data = {k: v for k, v in update.dict().items() if v is not None}
    if "payee_payment_status" in updated_data and updated_data["payee_payment_status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot mark as completed without evidence upload")

    result = payments_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": updated_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"message": "Payment updated"}

@app.delete("/delete_payment/{payment_id}")
async def delete_payment(payment_id: str):
    result = payments_collection.delete_one({"_id": ObjectId(payment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"message": "Payment deleted"}

@app.post("/upload_evidence/{payment_id}")
async def upload_evidence(payment_id: str, file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_path = f"evidence/{payment_id}_{file.filename}"
    os.makedirs("evidence", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    payments_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": {"evidence_file": file_path}})
    return {"message": "Evidence uploaded", "file_path": file_path}

@app.get("/download_evidence/{payment_id}")
async def download_evidence(payment_id: str):
    payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
    if not payment or "evidence_file" not in payment:
        raise HTTPException(status_code=404, detail="Evidence not found")

    return FileResponse(payment["evidence_file"])

# Run the application
# uvicorn main:app --reload
