from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas import TransactionCreate, TransactionResponse
import models
from database import Base, engine, get_db

summary_cards: list[dict] = [
    {
        "id": 1,
        "concepto": "Ingresos",
        "valor": 10000000,
    },
    {
        "id": 2,
        "concepto": "Gastos",
        "valor": 20000000,
    },
    {
        "id": 3,
        "concepto": "Deuda",
        "valor": 20000000,
    },
    {
        "id": 4,
        "concepto": "Balance",
        "valor": 20000000,
    }
]

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")


@app.get("/login", include_in_schema=False)
async def user_login(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@app.get("/", include_in_schema=False, name="home")
@app.get("/home", include_in_schema=False, name="home")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"summary_cards": summary_cards})


# !!! -------- TRANSACTIONS -------- !!! #
transactions_list: list[dict] = [
    {
        "transaction_id": 1,
        "user_id": 1,
        "category_id": 1,
        "description": "Salario Mensual",   
        "transaction_type": "Ingreso",
        "value": 800.00,
        "date": "2026-07-25",
        "created_at": "2026-07-25",
        "updated_at": "2025-07-25"
    }
]

@app.get("/transactions", include_in_schema=False)
def transactions(request: Request):
    return templates.TemplateResponse(request, "transactions.html", {"transactions_list": transactions_list})


@app.get("/register_transaction", include_in_schema=False)
async def register_transaction(request: Request):
    return templates.TemplateResponse(request, "register_transaction.html", {})


@app.get("/api/transactions", response_model=list[TransactionResponse])
def get_transactions():
    return transactions_list


@app.get("/api/transactions/{transaction_id}")
def get_transaction(transaction_id: int):
    for t in transactions_list:
        try:
            if t.get("transaction_id") == transaction_id:
                return t
        except (ValueError, TypeError):
            return {"Error": "Transaccion no encontrada"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="¡Transaccion no encontrada!")


@app.post(
        "/api/transactions",
        response_model=TransactionResponse,
        status_code=status.HTTP_201_CREATED  
)
def create_transaction(transaction: TransactionCreate):
    new_id = max(t["transaction_id"] for t in transactions_list) + 1 if transactions_list else 1
    new_transaction = {
        "transaction_type": transaction.transaction_type,
        "value": transaction.value,
        "date": transaction.date,
        "description": transaction.description,
        "transaction_id": new_id,
        "user_id": 1,
        "category_id": 2,
        "created_at": str(datetime.now().date()),
        "updated_at": str(datetime.now().date())
    }
    transactions_list.append(new_transaction)
    return new_transaction
    

# !!! -------- DASHBOARD -------- !!! #
fallback_cards = [
{"id": 1, "concepto": "Ingresos", "valor": 25000000},
{"id": 2, "concepto": "Gastos", "valor": 14800000},
{"id": 3, "concepto": "Deuda", "valor": 7500000},
{"id": 4, "concepto": "Balance", "valor": 2700000}
]

balance_bars = [
{"label": "Feb", "value": "4,2 M", "height": "46%"},
{"label": "Mar", "value": "5,6 M", "height": "58%"},
{"label": "Abr", "value": "3,8 M", "height": "42%"},
{"label": "May", "value": "6,1 M", "height": "64%"},
{"label": "Jun", "value": "5,0 M", "height": "52%"},
{"label": "Jul", "value": "7,4 M", "height": "76%"}
]

categories = [
    {"name": "Alimentación", "value": "4,2 M", "width": "82%", "alt": False},
    {"name": "Transporte", "value": "1,8 M", "width": "40%", "alt": True},
    {"name": "Servicios", "value": "2,5 M", "width": "55%", "alt": False},
    {"name": "Ocio", "value": "1,1 M", "width": "24%", "alt": True}
  ]

@app.get("/dashboard", include_in_schema=False)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request, 
        "dashboard.html", 
        {"fallback_cards": fallback_cards, 
         "balance_bars": balance_bars, 
         "categories": categories
         }
        )

@app.get("/user_settings", include_in_schema=False)
async def user_settings(request: Request):
    return templates.TemplateResponse(request, "user_settings.html", {})


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    error_message = (
        exception.detail if exception.detail else "Ha ocurrido un error. Por favor verifica tu solicitud e intenta nuevamente."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": error_message}
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exception.status_code, 
         "error_title": exception.status_code,
        "error_message": error_message
        },
        status_code=exception.status_code
    )

@app.exception_handler(RequestValidationError)
async def general_validation_error(request: Request, exception: RequestValidationError): 
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()}   
        )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": status.HTTP_422_UNPROCESSABLE_CONTENT, 
         "error_title": status.HTTP_422_UNPROCESSABLE_CONTENT,
         "error_message": "Solicitud invalida. Revisa tu solicitud e intenta nuevamente."
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )