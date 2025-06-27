"""
Aplicação FastAPI para geração de relatórios ADHOC
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from controller import consultaController

# Configurações da aplicação
APP_TITLE = "API de Relatórios ADHOC"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API para geração dinâmica de relatórios a partir do banco de dados"

# Configurações de CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

# Criar a aplicação FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar routers
app.include_router(
    consultaController.router, 
    prefix="/api/db", 
    tags=["database"]
)

# Rotas básicas
@app.get("/", tags=["health"])
def read_root():
    """Endpoint de verificação de saúde da API"""
    return {
        "message": "API de Relatórios ADHOC",
        "version": APP_VERSION,
        "status": "running"
    }

@app.get("/health", tags=["health"])
def health_check():
    """Endpoint de verificação de saúde detalhado"""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "service": "adhoc-reports-api"
    }

# Iniciar o servidor se executado diretamente
if __name__ == "__main__":
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=reload,
        log_level="info"
    )
