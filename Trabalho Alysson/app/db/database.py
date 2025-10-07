from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from sqlalchemy.engine import Engine

# URL de conexão para o banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./estoque.db"

# Cria a engine de conexão com o banco de dados
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# --- Boas práticas para SQLite: Habilitar PRAGMA foreign_keys ---
# Esta função garante que a verificação de chaves estrangeiras (foreign keys)
# seja ativada toda vez que uma nova conexão com o banco de dados for estabelecida.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
# -----------------------------------------------------------------

# Cria uma "fábrica" de sessões do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter uma sessão do banco de dados em cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()