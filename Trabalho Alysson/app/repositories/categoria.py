from sqlalchemy.orm import Session
# Tabela Categoria
from app.models.categoria import Categoria
# Contrato da API
from app.schemas.categoria import CategoriaCreate

def create(db:Session, payload: CategoriaCreate) -> Categoria:
    objeto = Categoria(**payload.model_dump())
    # objeto.nome = payload.nome
    db.add(objeto)
    db.commit()
    db.refresh(objeto)
    return objeto

def get(db: Session, categoria_id: int) -> Categoria | None:
    return db.get(Categoria, categoria_id)

def get_all(db: Session) -> list[Categoria]:
    return db.query(Categoria).order_by(Categoria.id).all()