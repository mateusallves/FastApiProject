
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base

class TipoMovimento(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

class EstoqueMovimento(Base):
    __tablename__ = "estoque_movimentos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="RESTRICT"), nullable=False, index=True)
    tipo = Column(Enum(TipoMovimento), nullable=False)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String(200), nullable=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    produto = relationship("Produto")

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_mov_quantidade_pos"),
    )
