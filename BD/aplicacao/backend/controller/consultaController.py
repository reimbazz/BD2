"""
Controller para consultas e geração de relatórios ADHOC
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from dao.consultaDAO import ConsultaDAO

router = APIRouter()
consulta_dao = ConsultaDAO()

# Modelos Pydantic para validação

class JoinRequest(BaseModel):
    """Modelo para requisição de join entre tabelas"""
    targetTable: str = Field(..., description="Nome da tabela alvo")
    sourceAttribute: str = Field(..., description="Atributo da tabela origem")
    targetAttribute: str = Field(..., description="Atributo da tabela alvo")
    joinType: str = Field(default="INNER JOIN", description="Tipo de join")

class JoinedTablesRequest(BaseModel):
    """Modelo para requisição de colunas de tabelas joinadas"""
    baseTable: str = Field(..., description="Tabela base")
    joins: List[JoinRequest] = Field(default=[], description="Lista de joins")

class AggregateFunction(BaseModel):
    """Modelo para função de agregação"""
    function: str = Field(..., description="Nome da função (COUNT, SUM, etc.)")
    attribute: str = Field(..., description="Atributo para aplicar a função")
    alias: str = Field(..., description="Alias para o resultado")

class OrderByColumn(BaseModel):
    """Modelo para ordenação"""
    attribute: Optional[str] = Field(None, description="Nome do atributo")
    column: Optional[str] = Field(None, description="Nome da coluna (compatibilidade)")
    direction: str = Field(default="ASC", description="Direção da ordenação")

class FilterCondition(BaseModel):
    """Modelo para condição de filtro"""
    attribute: str = Field(..., description="Atributo para filtrar")
    operator: str = Field(..., description="Operador de comparação")
    value: Any = Field(..., description="Valor para comparação")
    function: Optional[str] = Field(None, description="Função a aplicar no atributo")

class ReportRequest(BaseModel):
    """Modelo para requisição de relatório ADHOC"""
    baseTable: str = Field(..., description="Tabela base")
    attributes: List[str] = Field(..., description="Lista de atributos")
    joins: List[JoinRequest] = Field(default=[], description="Lista de joins")
    groupByAttributes: List[str] = Field(default=[], description="Atributos para agrupamento")
    aggregateFunctions: List[AggregateFunction] = Field(default=[], description="Funções de agregação")
    orderByColumns: List[OrderByColumn] = Field(default=[], description="Colunas para ordenação")
    filters: List[FilterCondition] = Field(default=[], description="Filtros")
    limit: Optional[int] = Field(default=1000, description="Limite de resultados")

class TransitiveRelationsWithJoinsRequest(BaseModel):
    """Modelo para relações transitivas com joins"""
    baseTable: str = Field(..., description="Tabela base")
    joins: List[JoinRequest] = Field(..., description="Lista de joins existentes")

def handle_error(operation: str, error: Exception) -> HTTPException:
    """Função utilitária para tratamento de erros"""
    error_message = f"Erro ao {operation}: {str(error)}"
    print(error_message)  # Log do erro
    return HTTPException(status_code=500, detail=error_message)

@router.get("/tables", summary="Listar todas as tabelas")
async def get_all_tables():
    """Retorna todas as tabelas disponíveis no banco de dados"""
    try:
        tables = consulta_dao.getAllTables()
        return {"tables": tables}
    except Exception as e:
        raise handle_error("buscar tabelas", e)

@router.get("/tables/{table_name}/relations", summary="Obter relações de uma tabela")
async def get_table_relations(table_name: str):
    """Retorna as relações de uma tabela específica"""
    try:
        relations = consulta_dao.getTableRelations(table_name)
        return {"relations": relations}
    except Exception as e:
        raise handle_error(f"buscar relações da tabela {table_name}", e)

@router.get("/tables/{table_name}/transitive-relations", summary="Obter relações transitivas")
async def get_transitive_relations(table_name: str, used_tables: str = ""):
    """Retorna as relações diretas e transitivas de uma tabela específica"""
    try:
        used_tables_list = [table.strip() for table in used_tables.split(",") if table.strip()] if used_tables else []
        relations = consulta_dao.getTransitiveRelations(table_name, used_tables_list)
        return {"relations": relations}
    except Exception as e:
        raise handle_error(f"buscar relações transitivas da tabela {table_name}", e)

@router.post("/tables/{table_name}/transitive-relations-with-joins", summary="Obter relações transitivas com joins")
async def get_transitive_relations_with_joins(table_name: str, request: TransitiveRelationsWithJoinsRequest):
    """Retorna as relações diretas e transitivas considerando joins já existentes"""
    try:
        joins_dict = [join.model_dump() for join in request.joins]
        relations = consulta_dao.getTransitiveRelationsWithJoins(request.baseTable, joins_dict)
        return {"relations": relations}
    except Exception as e:
        raise handle_error(f"buscar relações transitivas com joins para {table_name}", e)

@router.get("/tables/{table_name}/columns", summary="Obter colunas de uma tabela")
async def get_table_columns(table_name: str):
    """Retorna as colunas de uma tabela específica"""
    try:
        columns = consulta_dao.getTableColumns(table_name)
        return {"columns": columns}
    except Exception as e:
        raise handle_error(f"buscar colunas da tabela {table_name}", e)

@router.post("/tables/joined-columns", summary="Obter colunas de tabelas joinadas")
async def get_joined_tables_columns(request: JoinedTablesRequest):
    """Retorna as colunas de todas as tabelas envolvidas em joins"""
    try:
        joins_dict = [join.model_dump() for join in request.joins]
        columns = consulta_dao.getJoinedTablesColumns(request.baseTable, joins_dict)
        return {"columns": columns}
    except Exception as e:
        raise handle_error("buscar colunas das tabelas joinadas", e)

@router.get("/tables/{source_table}/foreign-keys/{target_table}", summary="Obter relações de chave estrangeira")
async def get_foreign_key_relations(source_table: str, target_table: str):
    """Retorna as relações de chave estrangeira entre duas tabelas"""
    try:
        relations = consulta_dao.getForeignKeyRelations(source_table, target_table)
        return {"relations": relations}
    except Exception as e:
        raise handle_error(f"buscar relações FK entre {source_table} e {target_table}", e)

@router.post("/report", summary="Gerar relatório ADHOC")
async def generate_report(request: ReportRequest):
    """Gera um relatório adhoc com base nos parâmetros fornecidos"""
    try:
        # Converter objetos para dicionários antes de passar para o DAO
        joins_dict = [join.model_dump() for join in request.joins]
        agg_functions_dict = [agg.model_dump() for agg in request.aggregateFunctions]
        
        # Normalizar orderByColumns
        order_by_dict = []
        for order in request.orderByColumns:
            order_dict = order.model_dump()
            # Compatibilidade: usar 'column' como 'attribute' se 'attribute' não estiver presente
            if order_dict.get('column') and not order_dict.get('attribute'):
                order_dict['attribute'] = order_dict['column']
            order_by_dict.append(order_dict)
        
        # Converter filtros para dicionários
        filters_dict = [filter_obj.model_dump() for filter_obj in request.filters]
        
        result, sql_query = consulta_dao.generateAdhocReport(
            request.baseTable,
            request.attributes,
            joins_dict,
            request.groupByAttributes,
            agg_functions_dict,
            order_by_dict,
            filters_dict,
            request.limit
        )
        
        return {"data": result, "sql": sql_query}
    except Exception as e:
        import traceback
        error_detail = f"Erro ao gerar relatório: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/functions/available", summary="Obter funções disponíveis")
async def get_available_functions():
    """Retorna as funções disponíveis por tipo de dados"""
    try:
        functions_by_type = {
            "text": [
                {"value": "UPPER", "label": "Maiúsculo (UPPER)"},
                {"value": "LOWER", "label": "Minúsculo (LOWER)"},
                {"value": "LENGTH", "label": "Comprimento (LENGTH)"},
                {"value": "TRIM", "label": "Remover espaços (TRIM)"}
            ],
            "numeric": [
                {"value": "ABS", "label": "Valor absoluto (ABS)"},
                {"value": "ROUND", "label": "Arredondar (ROUND)"},
                {"value": "CEIL", "label": "Teto (CEIL)"},
                {"value": "FLOOR", "label": "Piso (FLOOR)"}
            ],
            "date": [
                {"value": "EXTRACT_YEAR", "label": "Extrair ano"},
                {"value": "EXTRACT_MONTH", "label": "Extrair mês"},
                {"value": "EXTRACT_DAY", "label": "Extrair dia"},
                {"value": "DATE_TRUNC_MONTH", "label": "Truncar para mês"},
                {"value": "DATE_TRUNC_YEAR", "label": "Truncar para ano"}
            ]
        }
        return {"functions": functions_by_type}
    except Exception as e:
        raise handle_error("buscar funções disponíveis", e)