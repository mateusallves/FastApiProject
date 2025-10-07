from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
## contrato da API - schemas
from app.schemas.categoria import CategoriaCreate, CategoriaOut
from app.repositories import categoria as repo

rotas = APIRouter(prefix="/v1/categoria", tags=["categoria"])

@rotas.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def create(payload: CategoriaCreate, db: Session = Depends(get_db)):
    return repo.create(db, payload)

@rotas.get("/", response_model=list[CategoriaOut])
def list_all(db: Session = Depends(get_db)):
    return repo.get_all(db)

@rotas.get("/", response_model=CategoriaOut)
def get_id(categoria_id:int, db: Session=Depends(get_db)):
    objeto = repo.get(db, categoria_id)
    if not objeto: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria nao encontrada")
    return objeto