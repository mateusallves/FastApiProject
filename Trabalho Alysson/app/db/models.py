import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

# Base para os modelos declarativos do SQLAlchemy
Base = declarative_base()

# Enum para o tipo de movimento de estoque
class TipoMovimento(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

# Modelo para a tabela de Produtos
class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    descricao = Column(String)
    preco = Column(Integer, nullable=False) # Armazenar em centavos para evitar problemas de ponto flutuante
    
    # Novos campos para gestão de estoque
    estoque_minimo = Column(Integer, default=0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamento com os movimentos de estoque
    movimentos = relationship("EstoqueMovimento", back_populates="produto")

# Modelo para a tabela de Movimentos de Estoque
class EstoqueMovimento(Base):
    __tablename__ = 'estoque_movimentos'

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    tipo = Column(SQLAlchemyEnum(TipoMovimento), nullable=False)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento com o produto
    produto = relationship("Produto", back_populates="movimentos")