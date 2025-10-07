from pydantic import BaseModel, Field

class ProdutoBase(BaseModel):
    nome: str
    descricao: str | None = None
    preco: int = Field(gt=0, description="Preço em centavos")
    estoque_minimo: int = Field(ge=0, default=0)
    ativo: bool = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoOut(ProdutoBase):
    id: int

    class Config:
        orm_mode = True # Permite que o Pydantic leia dados de modelos do SQLAlchemy