from abc import ABC, abstractmethod
from pydantic import BaseModel

class Factura(BaseModel):
    id: str
    cliente: str
    total: float
    vencimiento: str
    pagada: bool

class ERPGateway(ABC):
    @abstractmethod
    async def facturas_pendientes(self, token: str) -> list[Factura]: ...
