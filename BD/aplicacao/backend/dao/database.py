"""
Configuração do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# URL de conexão do banco de dados
# Em produção, isso deveria vir de variáveis de ambiente
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://paulo:1234@localhost:5432/trabalhoBD2'
)

# Configurar engine com pool de conexões otimizado
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=False
)

# Configurar sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# Base para os modelos ORM
Base = declarative_base()

def get_session():
    """
    Cria uma nova sessão do banco de dados
    """
    return SessionLocal()

def get_engine():
    """
    Retorna a engine do banco de dados
    """
    return engine
