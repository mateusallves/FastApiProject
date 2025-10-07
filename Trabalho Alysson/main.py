from fastapi import FastAPI
from app.db import models, database
from app.api.v1 import rotas_produtos, rotas_estoque

# Cria as tabelas no banco de dados (se não existirem)
models.Base.metadata.create_all(bind=database.engine)

# Instancia a aplicação FastAPI
app = FastAPI(
    title="API de Gestão de Estoques",
    description="Uma API para consolidar regras de negócio de estoque.",
    version="1.0.0"
)

# Inclui as rotas na aplicação
app.include_router(rotas_produtos.router, prefix="/api/v1/produtos", tags=["Produtos"])
app.include_router(rotas_estoque.router, prefix="/api/v1/estoque", tags=["Estoque"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API de Gestão de Estoques"}