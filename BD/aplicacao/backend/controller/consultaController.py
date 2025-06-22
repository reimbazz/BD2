from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from dao.consultaDAO import ConsultaDAO

router = APIRouter()
consulta_dao = ConsultaDAO()

class JoinRequest(BaseModel):
    targetTable: str
    sourceAttribute: str
    targetAttribute: str
    joinType: str

class JoinedTablesRequest(BaseModel):
    baseTable: str
    joins: List[JoinRequest]

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

@router.post("/tables/joined-columns")
async def get_joined_tables_columns(request: JoinedTablesRequest):
    """Retorna as colunas de todas as tabelas envolvidas em joins"""
    try:
        joins_dict = [join.model_dump() for join in request.joins]
        columns = consulta_dao.getJoinedTablesColumns(request.baseTable, joins_dict)
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar colunas das tabelas joinadas: {str(e)}")

@router.get("/tables/{source_table}/foreign-keys/{target_table}")
async def get_foreign_key_relations(source_table: str, target_table: str):
    """Retorna as relações de chave estrangeira entre duas tabelas"""
    try:
        relations = consulta_dao.getForeignKeyRelations(source_table, target_table)
        return {"relations": relations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar relações FK entre {source_table} e {target_table}: {str(e)}")