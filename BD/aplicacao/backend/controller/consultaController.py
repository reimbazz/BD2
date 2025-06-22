from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
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

class AggregateFunction(BaseModel):
    function: str
    attribute: str
    alias: str

class OrderByColumn(BaseModel):
    attribute: str = None
    column: str = None
    direction: str

class ReportRequest(BaseModel):
    baseTable: str
    attributes: List[str]
    joins: List[JoinRequest] = []
    groupByAttributes: List[str] = []
    aggregateFunctions: List[AggregateFunction] = []
    orderByColumns: List[OrderByColumn] = []
    filters: List[Dict[str, Any]] = []
    limit: Optional[int] = 1000

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

@router.post("/report")
async def generate_report(request: ReportRequest):
    """Gera um relatório adhoc com base nos parâmetros fornecidos"""
    try:
        # Converter objetos para dicionários antes de passar para o DAO
        joins_dict = [join.model_dump() for join in request.joins] if request.joins else []
        agg_functions_dict = [agg.model_dump() for agg in request.aggregateFunctions] if request.aggregateFunctions else []
        
        # Para orderByColumns, precisa normalizar column/attribute
        order_by_dict = []
        if request.orderByColumns:
            for order in request.orderByColumns:
                order_dict = order.model_dump()
                # Se column está presente mas attribute não está, usa column como attribute
                if order_dict.get('column') and not order_dict.get('attribute'):
                    order_dict['attribute'] = order_dict['column']
                order_by_dict.append(order_dict)
        
        result, sql_query = consulta_dao.generateAdhocReport(
            request.baseTable,
            request.attributes,
            joins_dict,
            request.groupByAttributes,
            agg_functions_dict,
            order_by_dict,
            request.filters,
            request.limit
        )
        return {"data": result, "sql": sql_query}
    except Exception as e:
        import traceback
        error_detail = f"Erro ao gerar relatório: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)