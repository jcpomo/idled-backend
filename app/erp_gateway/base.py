from abc import ABC, abstractmethod
from pydantic import BaseModel

class Factura(BaseModel):
    id: str
    cliente: str
    total: float
    vencimiento: str
    pagada: bool

class Articulo(BaseModel):
    referencia: str
    descripcion: str
    stock: int

class ERPGateway(ABC):
    @abstractmethod
    async def facturas_pendientes(self, token: str) -> list[Factura]: ...

    @abstractmethod
    async def stock_articulo(self, token: str, referencia: str) -> "Articulo | None": ...
