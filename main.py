from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from pydantic import ValidationError

from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas import TransactionCreate, TransactionResponse, UserCreate, UserResponse
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


# !!! -------- LOGIN -------- !!! #
@app.get("/login", include_in_schema=False)
async def user_login(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


# !!! -------- HOME -------- !!! #
@app.get("/", include_in_schema=False, name="home")
@app.get("/home", include_in_schema=False, name="home")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"summary_cards": summary_cards})


# !!! -------- USERS -------- !!! #
"""
This function creates a new user via REST API POST.
"""
@app.post(
        "/api/users",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED  
)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user: models.User | None = db.scalars(
        select(models.User).where(models.User.username == user.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya esta en uso. Por favor selecciona otro."
        )

    existing_email = db.scalars(
        select(models.User).where(models.User.email == user.email)
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electronico ingresado ya esta en uso. Por favor selecciona otro."
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash="password",
        status="Active"

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get(
        "/api/users/{user_id}",
        response_model=UserResponse,
)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user: models.User | None = db.scalars(
        select(models.User).where(models.User.user_id == user_id)
    ).one_or_none()
    
    if user:
        return user
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El usuario no fue encontrado."
    )


# !!! -------- TRANSACTIONS -------- !!! #
transactions_list_dummy: list[dict] = [
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

@app.get("/transactions", include_in_schema=False, name="transactions")
def transactions(request: Request, db: Annotated[Session, Depends(get_db)]):
    transactions_list = db.scalars(
        select(models.Transactions)
    ).all()

    return templates.TemplateResponse(
        request, 
        "transactions.html", 
        {"transactions_list": transactions_list}
    )


CATEGORIAS_ESTANDAR: dict[str, list[str]] = {
    "ingreso": [
        "Salario", "Negocios / Emprendimiento", "Inversiones",
        "Intereses", "Regalos", "Otros ingresos",
    ],
    "gasto": [
        "Alimentación", "Transporte", "Servicios (agua, luz, internet)",
        "Vivienda / Arriendo", "Salud", "Educación",
        "Ocio y entretenimiento", "Ropa y calzado", "Mascotas", "Otros gastos",
    ],
    "deuda": [
        "Tarjeta de crédito", "Crédito de consumo", "Crédito hipotecario",
        "Crédito vehicular", "Préstamo personal", "Otros préstamos",
    ],
    }

@app.get(
        "/register_transaction", 
        include_in_schema=False, 
        name="register_transaction"
    )
async def register_transaction(request: Request): 
    return templates.TemplateResponse(
        request, 
        "register_transaction.html", 
        {"categorias": CATEGORIAS_ESTANDAR}
    )


@app.post("/register_transaction", include_in_schema=False)
async def post_transaction(
    request: Request, 
    db: Annotated[Session, Depends(get_db)],
    tipo: Annotated[str, Form()],
    categoria: Annotated[str, Form()],
    valor: Annotated[str, Form()],
    fecha: Annotated[datetime, Form()],
    descripcion: Annotated[str, Form()] = ""
    ):

    entry = models.Transactions(
        transaction_type=tipo,
        category=categoria,
        value=valor,
        date=fecha,
        description=descripcion,
        user_id=1
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return RedirectResponse(url=request.url_for("register_transaction"), status_code=status.HTTP_303_SEE_OTHER)


# !!! -------- REST API -------- !!! #
@app.get(
        "/api/transactions",
        response_model=list[TransactionResponse]
    )
def get_transactions(db: Annotated[Session, Depends(get_db)]):
    transactions_list = db.scalars(
        select(models.Transactions)
    ).all()
    return transactions_list


@app.get("/api/transactions/{transaction_id}")
def get_transaction(transaction_id: int):
    for t in transactions_list_dummy:
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
def create_transaction(transaction: TransactionCreate, db: Annotated[Session, Depends(get_db)]):
    cat_id = db.scalars(
        select(models.Transactions)
    )

    new_transaction = models.Transactions(
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        value=transaction.value,
        date=transaction.date,
        description=transaction.description,
        user_id=transaction.user_id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
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


# !!! -------- EXCEPTIONS -------- !!! #
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