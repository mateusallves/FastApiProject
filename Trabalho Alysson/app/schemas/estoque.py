from pydantic import BaseModel, Field
from datetime import datetime
from app.db.models import TipoMovimento

# --- Schemas para Movimentos de Estoque ---
class EstoqueMovimentoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimento
    quantidade: int = Field(gt=0)
    motivo: str | None = None

class EstoqueMovimentoOut(BaseModel):
    id: int
    produto_id: int
    tipo: TipoMovimento
    quantidade: int
    motivo: str | None
    criado_em: datetime

    class Config:
        orm_mode = True

# --- Schemas para Operações Compostas ---
class VendaCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)

class DevolucaoCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)

class AjusteCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimento
    quantidade: int = Field(gt=0)
    motivo: str # Motivo é obrigatório no ajuste

# --- Schemas para Consultas e Relatórios ---
class SaldoOut(BaseModel):
    produto_id: int
    nome_produto: str
    saldo: int

class ResumoEstoqueOut(BaseModel):
    produto_id: int
    nome: str
    saldo: int
    estoque_minimo: int
    abaixo_minimo: bool