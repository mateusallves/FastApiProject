from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db import database, models
from app.schemas import estoque as schemas

router = APIRouter()

# --- Constante para a decisão de saldo negativo ---
# Mude para True para permitir saldo negativo
ALLOW_NEGATIVE_STOCK = False

# --- Funções Auxiliares ---
def get_produto_or_404(db: Session, produto_id: int):
    """Busca um produto pelo ID ou retorna erro 404."""
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produto com id {produto_id} não encontrado.")
    return produto

def calcular_saldo_produto(db: Session, produto_id: int) -> int:
    """Calcula o saldo atual de um produto a partir de suas movimentações."""
    entradas = db.query(func.sum(models.EstoqueMovimento.quantidade)).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.TipoMovimento.ENTRADA
    ).scalar() or 0

    saidas = db.query(func.sum(models.EstoqueMovimento.quantidade)).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.TipoMovimento.SAIDA
    ).scalar() or 0
    
    return entradas - saidas

# --- Etapa 1: Rotas Básicas ---
@router.post("/movimentos", response_model=schemas.EstoqueMovimentoOut, status_code=status.HTTP_201_CREATED)
def criar_movimento(movimento: schemas.EstoqueMovimentoCreate, db: Session = Depends(database.get_db)):
    """Registra uma movimentação de estoque (ENTRADA/SAIDA)."""
    get_produto_or_404(db, movimento.produto_id) # Valida se o produto existe

    if movimento.tipo == models.TipoMovimento.SAIDA and not ALLOW_NEGATIVE_STOCK:
        saldo_atual = calcular_saldo_produto(db, movimento.produto_id)
        if saldo_atual < movimento.quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Saldo atual: {saldo_atual}, Tentativa de saída: {movimento.quantidade}"
            )

    db_movimento = models.EstoqueMovimento(**movimento.dict())
    db.add(db_movimento)
    db.commit()
    db.refresh(db_movimento)
    return db_movimento

@router.get("/saldo/{produto_id}", response_model=schemas.SaldoOut)
def obter_saldo_atual(produto_id: int, db: Session = Depends(database.get_db)):
    """Calcula e retorna o saldo atual de um produto."""
    produto = get_produto_or_404(db, produto_id)
    saldo = calcular_saldo_produto(db, produto_id)
    return {"produto_id": produto_id, "nome_produto": produto.nome, "saldo": saldo}

# --- Etapa 2: Regras de Estoque Mínimo ---
@router.get("/produtos/abaixo-minimo", response_model=list[schemas.ResumoEstoqueOut])
def listar_produtos_abaixo_minimo(db: Session = Depends(database.get_db)):
    """Lista todos os produtos que estão com o saldo abaixo do estoque mínimo definido."""
    produtos = db.query(models.Produto).filter(models.Produto.ativo == True).all()
    produtos_abaixo_minimo = []

    for produto in produtos:
        saldo = calcular_saldo_produto(db, produto.id)
        if saldo < produto.estoque_minimo:
            produtos_abaixo_minimo.append({
                "produto_id": produto.id,
                "nome": produto.nome,
                "saldo": saldo,
                "estoque_minimo": produto.estoque_minimo,
                "abaixo_minimo": True
            })
    return produtos_abaixo_minimo

# --- Etapa 3: Operações Compostas ---
@router.post("/venda", response_model=schemas.EstoqueMovimentoOut)
def registrar_venda(venda: schemas.VendaCreate, db: Session = Depends(database.get_db)):
    """Registra uma SAÍDA com motivo 'venda'."""
    movimento_data = schemas.EstoqueMovimentoCreate(
        produto_id=venda.produto_id,
        tipo=models.TipoMovimento.SAIDA,
        quantidade=venda.quantidade,
        motivo="venda"
    )
    return criar_movimento(movimento_data, db)

@router.post("/devolucao", response_model=schemas.EstoqueMovimentoOut)
def registrar_devolucao(devolucao: schemas.DevolucaoCreate, db: Session = Depends(database.get_db)):
    """Registra uma ENTRADA com motivo 'devolucao'."""
    movimento_data = schemas.EstoqueMovimentoCreate(
        produto_id=devolucao.produto_id,
        tipo=models.TipoMovimento.ENTRADA,
        quantidade=devolucao.quantidade,
        motivo="devolucao"
    )
    return criar_movimento(movimento_data, db)

@router.post("/ajuste", response_model=schemas.EstoqueMovimentoOut)
def ajustar_estoque(ajuste: schemas.AjusteCreate, db: Session = Depends(database.get_db)):
    """Registra uma ENTRADA ou SAÍDA com motivo obrigatório."""
    movimento_data = schemas.EstoqueMovimentoCreate(
        produto_id=ajuste.produto_id,
        tipo=ajuste.tipo,
        quantidade=ajuste.quantidade,
        motivo=ajuste.motivo
    )
    return criar_movimento(movimento_data, db)

# --- Etapa 4: Relatórios e Consultas ---
@router.get("/extrato/{produto_id}", response_model=list[schemas.EstoqueMovimentoOut])
def obter_extrato_produto(produto_id: int, limit: int = 100, offset: int = 0, db: Session = Depends(database.get_db)):
    """Retorna os últimos movimentos de um produto (extrato)."""
    get_produto_or_404(db, produto_id)
    movimentos = db.query(models.EstoqueMovimento).filter(
        models.EstoqueMovimento.produto_id == produto_id
    ).order_by(models.EstoqueMovimento.criado_em.desc()).offset(offset).limit(limit).all()
    return movimentos

@router.get("/resumo", response_model=list[schemas.ResumoEstoqueOut])
def obter_resumo_estoque(db: Session = Depends(database.get_db)):
    """Fornece um resumo de todos os produtos com seu saldo e status de estoque mínimo."""
    produtos = db.query(models.Produto).filter(models.Produto.ativo == True).all()
    resumo = []

    for produto in produtos:
        saldo = calcular_saldo_produto(db, produto.id)
        resumo.append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "saldo": saldo,
            "estoque_minimo": produto.estoque_minimo,
            "abaixo_minimo": saldo < produto.estoque_minimo
        })
    return resumo