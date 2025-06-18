from fastapi import APIRouter, HTTPException
from dao.consultaDAO import ConsultaDAO

router = APIRouter()
consulta_dao = ConsultaDAO()


@router.get("/tables")
async def get_all_tables():
    """Retorna todas as tabelas disponíveis no banco de dados"""
    try:
        tables = consulta_dao.getAllTables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tabelas: {str(e)}")
    
