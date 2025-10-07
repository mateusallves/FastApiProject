# app/api/v1/routers/estoque.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from app.db.session import get_db
from app.schemas.estoque import (
    EstoqueMovimentoCreate, EstoqueMovimentoOut, SaldoOut, ResumoEstoqueOut
)
from app.models.estoque_movimento import TipoMovimento
from app.services.estoque_service import (
    criar_movimento, calcular_saldo, produtos_abaixo_minimo, listar_extrato
)


router = APIRouter(prefix="/api/v1/estoque", tags=["Estoque"])

# POST /api/v1/estoque/movimentos
@router.post("/movimentos", response_model=EstoqueMovimentoOut, status_code=201)
def criar_mov(mov_in: EstoqueMovimentoCreate, db: Session = Depends(get_db)):
    mov = criar_movimento(
        db,
        produto_id=mov_in.produto_id,
        tipo=TipoMovimento(mov_in.tipo),
        quantidade=mov_in.quantidade,
        motivo=mov_in.motivo
    )
    db.commit()
    db.refresh(mov)
    return mov

# GET /api/v1/estoque/saldo/{produto_id}
@router.get("/saldo/{produto_id}", response_model=SaldoOut)
def saldo(produto_id: int, db: Session = Depends(get_db)):
    s = calcular_saldo(db, produto_id)
    return {"produto_id": produto_id, "saldo": s}

# Operações compostas
@router.post("/venda", response_model=EstoqueMovimentoOut, status_code=201)
def venda(produto_id: int, quantidade: int = Query(gt=0), db: Session = Depends(get_db)):
    mov = criar_movimento(db, produto_id, TipoMovimento.SAIDA, quantidade, "venda")
    db.commit(); db.refresh(mov)
    return mov

@router.post("/devolucao", response_model=EstoqueMovimentoOut, status_code=201)
def devolucao(produto_id: int, quantidade: int = Query(gt=0), db: Session = Depends(get_db)):
    mov = criar_movimento(db, produto_id, TipoMovimento.ENTRADA, quantidade, "devolucao")
    db.commit(); db.refresh(mov)
    return mov

@router.post("/ajuste", response_model=EstoqueMovimentoOut, status_code=201)
def ajuste(
    produto_id: int,
    tipo: Literal["ENTRADA","SAIDA"],
    quantidade: int = Query(gt=0),
    motivo: str = Query(min_length=2),
    db: Session = Depends(get_db),
):
    mov = criar_movimento(db, produto_id, TipoMovimento(tipo), quantidade, motivo)
    db.commit(); db.refresh(mov)
    return mov

# Relatórios
@router.get("/extrato/{produto_id}", response_model=List[EstoqueMovimentoOut])
def extrato(
    produto_id: int,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = listar_extrato(db, produto_id, limit, offset)
    return rows

router = APIRouter(prefix="/api/v1/produtos", tags=["Produtos - Estoque"])

@router.get("/abaixo-minimo", response_model=List[ResumoEstoqueOut])
def abaixo_minimo(db: Session = Depends(get_db)):
    rows = produtos_abaixo_minimo(db)
    return [
        {
            "produto_id": pid,
            "nome": nome,
            "saldo": saldo,
            "estoque_minimo": minimo,
            "abaixo_minimo": abaixo
        }
        for (pid, nome, saldo, minimo, abaixo) in rows
        if abaixo
    ]

@router.get("/estoque/resumo", response_model=List[ResumoEstoqueOut])
def resumo(db: Session = Depends(get_db)):
    rows = produtos_abaixo_minimo(db)
    return [
        {
            "produto_id": pid,
            "nome": nome,
            "saldo": saldo,
            "estoque_minimo": minimo,
            "abaixo_minimo": abaixo
        }
        for (pid, nome, saldo, minimo, abaixo) in rows
    ]
