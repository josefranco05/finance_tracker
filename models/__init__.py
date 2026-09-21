"""Paquete `models` de MyFin.

Marca `models/` como paquete de Python y expone la capa de datos para poder
importar las tablas directamente desde el paquete:

    from models import User, Categories, Transactions

Nota: `models/models.py` importa `from database import Base`, por lo que los
scripts deben ejecutarse desde la raíz del proyecto (donde están `database.py`,
`schemas.py` y `main.py`), p. ej.:

    uvicorn main:app --reload
    python -m models.models
"""

from .models import  User, Transactions

__all__ = ["User", "Transactions"]
