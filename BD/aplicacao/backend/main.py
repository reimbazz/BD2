from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from BD.aplicacao.backend.controller import consultaController

# Criar a aplicação FastAPI
app = FastAPI(title="API de Países e Cidades")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URLs do frontend Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar routers
app.include_router(consultaController.router, prefix="/api/db", tags=["database"])

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "API de Países e Cidades"}

# Iniciar o servidor se executado diretamente
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
