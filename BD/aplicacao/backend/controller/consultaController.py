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

@router.get("/tables/{table_name}/relations")
async def get_table_relations(table_name: str):
    """Retorna as relações de uma tabela específica"""
    try:
        relations = consulta_dao.getTableRelations(table_name)
        return {"relations": relations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar relações da tabela {table_name}: {str(e)}")

@router.get("/tables/{table_name}/columns")
async def get_table_columns(table_name: str):
    """Retorna as colunas de uma tabela específica"""
    try:
        columns = consulta_dao.getTableColumns(table_name)
        return{"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar colunas da tabela {table_name}: {str(e)}")