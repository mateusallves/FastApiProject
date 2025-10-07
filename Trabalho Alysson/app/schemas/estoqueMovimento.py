from datetime import datetime
from pydantic import BaseModel, Field, conint
from typing import Optional, Literal

TipoMov = Literal["ENTRADA", "SAIDA"]

class EstoqueMovimentoCreate(BaseModel):
    produto_id: int
    tipo: TipoMov
    quantidade: conint(strict=True, gt=0)
    motivo: Optional[str] = None

class EstoqueMovimentoOut(BaseModel):
    id: int
    produto_id: int
    tipo: TipoMov
    quantidade: int
    motivo: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True

class SaldoOut(BaseModel):
    produto_id: int
    saldo: int

class ResumoEstoqueOut(BaseModel):
    produto_id: int
    nome: str
    saldo: int
    estoque_minimo: int
    abaixo_minimo: bool
