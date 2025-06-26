from typing import List, Dict, Any, Tuple
from sqlalchemy import inspect, select, func, and_, desc, asc
from sqlalchemy.orm import Session
from .database import get_engine, SessionLocal
import models.models as models_module

class ConsultaDAO:
    def __init__(self):
        self.engine = get_engine()

    def getAllTables(self) -> List[str]:
        try:
            insp = inspect(self.engine)
            return insp.get_table_names(schema='public')
        except Exception as e:
            print(f"Erro ao buscar tabelas: {e}")
            raise e
    
    def getTableRelations(self, table_name: str) -> List[str]:
        try:
            insp = inspect(self.engine)
            related_tables = set()

            # Relações onde table_name tem FKs para outras
            foreign_keys = insp.get_foreign_keys(table_name, schema='public')
            for fk in foreign_keys:
                related_tables.add(fk['referred_table'])

            # Relações onde outras tabelas apontam para table_name
            for other_table in insp.get_table_names(schema='public'):
                if other_table == table_name:
                    continue
                other_fks = insp.get_foreign_keys(other_table, schema='public')
                for fk in other_fks:
                    if fk['referred_table'] == table_name:
                        related_tables.add(other_table)

            return list(related_tables)
        except Exception as e:
            print(f"Erro ao buscar relações da tabela {table_name}: {e}")
            raise e

    def getTableColumns(self, table_name: str) -> List[Dict[str, Any]]:
        try:
            insp = inspect(self.engine)
            column_data = []

            columns = insp.get_columns(table_name, schema='public')
            for col in columns:
                column_data.append({"name": col['name'], "type": str(col['type'])})

            return column_data
        except Exception as e:
            print(f"Erro ao buscar atributos da tabela {table_name}: {e}")
            raise e

    def getJoinedTablesColumns(self, base_table: str, joins: list) -> List[Dict[str, Any]]:
        """
        Retorna os atributos de todas as tabelas envolvidas em joins
        """
        try:
            all_columns = []
            tables_processed = set()
            
            # Adicionar colunas da tabela base
            base_columns = self.getTableColumns(base_table)
            for col in base_columns:
                all_columns.append({
                    "name": col['name'],
                    "type": col['type'],
                    "table": base_table,
                    "qualified_name": f"{base_table}.{col['name']}"
                })
            tables_processed.add(base_table)
            
            # Adicionar colunas das tabelas joinadas
            for join in joins:
                target_table = join.get('targetTable')
                if target_table and target_table not in tables_processed:
                    target_columns = self.getTableColumns(target_table)
                    for col in target_columns:
                        all_columns.append({
                            "name": col['name'],
                            "type": col['type'],
                            "table": target_table,
                            "qualified_name": f"{target_table}.{col['name']}"
                        })
                    tables_processed.add(target_table)
            
            return all_columns
        except Exception as e:
            print(f"Erro ao buscar atributos das tabelas joinadas: {e}")
            raise e

    def getForeignKeyRelations(self, source_table: str, target_table: str) -> List[Dict[str, Any]]:
        """
        Busca as relações de chave estrangeira entre duas tabelas
        """
        try:
            insp = inspect(self.engine)
            relations = []
            
            # Verificar FKs da tabela de origem para a tabela de destino
            source_fks = insp.get_foreign_keys(source_table, schema='public')
            for fk in source_fks:
                if fk['referred_table'] == target_table:
                    relations.append({
                        'source_column': fk['constrained_columns'][0],
                        'target_column': fk['referred_columns'][0],
                        'direction': 'source_to_target'
                    })
            
            # Verificar FKs da tabela de destino para a tabela de origem
            target_fks = insp.get_foreign_keys(target_table, schema='public')
            for fk in target_fks:
                if fk['referred_table'] == source_table:
                    relations.append({
                        'source_column': fk['referred_columns'][0],
                        'target_column': fk['constrained_columns'][0],
                        'direction': 'target_to_source'
                    })
            
            return relations
        except Exception as e:
            print(f"Erro ao buscar relações FK entre {source_table} e {target_table}: {e}")
            raise e    
            
    def generateAdhocReport(self, base_table: str, attributes: List[str], joins: List,
                          group_by_attributes: List[str], aggregate_functions: List,
                          order_by_columns: List, filters: List[Dict[str, Any]] = [],
                          limit: int = 1000) -> Tuple[List[Dict[str, Any]], str]:
        """
        Gera um relatório adhoc baseado nos parâmetros fornecidos usando ORM SQLAlchemy.
        
        Args:
            base_table: Tabela base da consulta
            attributes: Lista de atributos a serem selecionados
            joins: Lista de joins a serem aplicados
            group_by_attributes: Lista de atributos para agrupar
            aggregate_functions: Lista de funções de agregação (função, atributo, alias)
            order_by_columns: Lista de colunas para ordenação
            filters: Lista de filtros a serem aplicados
            limit: Limite de registros a retornar
              Returns:
            Tuple com os dados do relatório e a consulta SQL gerada
        """
        try:
            with SessionLocal() as session:
                # Mapear nome da tabela para a classe do modelo ORM correspondente
                model_classes = {
                    cls.__tablename__: cls
                    for cls in [getattr(models_module, cls_name) for cls_name in dir(models_module) 
                               if not cls_name.startswith('_') and cls_name != 'Base' and hasattr(getattr(models_module, cls_name), '__tablename__')]
                }
                
                # Verificar se a tabela base existe no mapeamento
                if base_table not in model_classes:
                    raise ValueError(f"Tabela base '{base_table}' não encontrada nos modelos ORM")
                
                base_model = model_classes[base_table]
                
                # Dicionário para armazenar alias de tabelas joinadas para evitar duplicação
                table_aliases = {base_table: base_model}
                
                # Iniciar a consulta select
                query = select()
                
                # Armazenar colunas selecionadas e seus nomes para lidar com duplicações
                select_columns = []
                column_names_count = {}
                
                # Função auxiliar para obter uma coluna de uma tabela específica
                def get_column_from_table(table_name, column_name):
                    if table_name not in table_aliases:
                        if table_name not in model_classes:
                            raise ValueError(f"Tabela '{table_name}' não encontrada nos modelos ORM")
                        # Criar um alias para a tabela se não existir
                        table_aliases[table_name] = model_classes[table_name]
                    
                    model = table_aliases[table_name]
                    # Obter a coluna do modelo
                    if not hasattr(model, column_name):
                        raise ValueError(f"Coluna '{column_name}' não encontrada na tabela '{table_name}'")
                    
                    return getattr(model, column_name)
                  # Adicionar colunas selecionadas
                for attr in attributes:
                    if "." in attr:
                        table_name, col_name = attr.split(".")
                        column_obj = get_column_from_table(table_name, col_name)
                        
                        # Verificar se o nome da coluna já foi usado e criar um alias se necessário
                        if col_name in column_names_count:
                            column_names_count[col_name] += 1
                            column_alias = f"{col_name}_{table_name}"
                            select_columns.append(column_obj.label(column_alias))
                        else:
                            column_names_count[col_name] = 1
                            select_columns.append(column_obj)
                    else:
                        # Para colunas sem qualificador de tabela, tentar encontrar em todas as tabelas
                        found = False
                        for table_name, model in table_aliases.items():
                            if hasattr(model, attr):
                                column_obj = getattr(model, attr)
                                found = True
                                
                                # Adicionar um alias se o mesmo nome de coluna existe em múltiplas tabelas
                                if attr in column_names_count:
                                    column_names_count[attr] += 1
                                    column_alias = f"{attr}_{table_name}"
                                    select_columns.append(column_obj.label(column_alias))
                                else:
                                    column_names_count[attr] = 1
                                    select_columns.append(column_obj)
                                break
                        
                        if not found:
                            # Se não encontrou em nenhuma tabela, usar a tabela base
                            column_obj = get_column_from_table(base_table, attr)
                            
                            if attr in column_names_count:
                                column_names_count[attr] += 1
                                column_alias = f"{attr}_{base_table}"
                                select_columns.append(column_obj.label(column_alias))
                            else:
                                column_names_count[attr] = 1
                                select_columns.append(column_obj)
                
                # Adicionar funções de agregação
                for agg in aggregate_functions:
                    # Converter para dict se for um modelo Pydantic
                    agg_dict = agg
                    if hasattr(agg, 'model_dump'):
                        agg_dict = agg.model_dump()
                    
                    function_name = agg_dict.get("function")
                    attr = agg_dict.get("attribute")
                    alias_name = agg_dict.get("alias")
                    
                    if not function_name or not attr:
                        continue
                    
                    # Obter a função de agregação do SQLAlchemy
                    agg_func = getattr(func, function_name.lower(), None)
                    if not agg_func:
                        raise ValueError(f"Função de agregação '{function_name}' não suportada")
                      # Obter a coluna para aplicar a função
                    if "." in attr:
                        table_name, col_name = attr.split(".")
                        column_obj = get_column_from_table(table_name, col_name)
                    else:
                        # Se não tiver qualificação, buscar primeiro entre os aliases definidos
                        # e depois na tabela base
                        found = False
                        for table_name, model in table_aliases.items():
                            if hasattr(model, attr):
                                column_obj = getattr(model, attr)
                                found = True
                                break
                        
                        if not found:
                            column_obj = get_column_from_table(base_table, attr)
                    
                    # Adicionar a função de agregação com o alias
                    select_columns.append(agg_func(column_obj).label(alias_name))
                
                # Adicionar colunas ao select
                query = query.add_columns(*select_columns)
                
                # Definir a tabela base (FROM)
                from_obj = base_model
                  # Inicializar o objeto FROM
                from_obj = base_model.__table__
                
                # Adicionar JOINs
                for join_info in joins:
                    # Converter para dict se for um modelo Pydantic
                    join_dict = join_info
                    if hasattr(join_info, 'model_dump'):
                        join_dict = join_info.model_dump()
                    
                    target_table = join_dict.get("targetTable")
                    source_attr = join_dict.get("sourceAttribute")
                    target_attr = join_dict.get("targetAttribute")
                    join_type = join_dict.get("joinType", "INNER").upper()
                    
                    # Verificar se a tabela alvo existe
                    if target_table not in model_classes:
                        raise ValueError(f"Tabela alvo '{target_table}' não encontrada nos modelos ORM")
                    
                    # Extrair tabela e coluna do atributo fonte
                    if "." in source_attr:
                        source_table, source_col = source_attr.split(".")
                    else:
                        source_table = base_table
                        source_col = source_attr
                    
                    # Extrair tabela e coluna do atributo alvo
                    if "." in target_attr:
                        target_table_prefix, target_col = target_attr.split(".")
                    else:
                        target_col = target_attr
                    
                    # Obter os objetos de coluna para o join
                    source_column = get_column_from_table(source_table, source_col)
                    
                    # Criar um alias para a tabela alvo se ainda não existir
                    if target_table not in table_aliases:
                        target_model = model_classes[target_table]
                        table_aliases[target_table] = target_model
                    
                    target_model = table_aliases[target_table]
                    target_column = getattr(target_model, target_col)
                    
                    # Criar a condição de join
                    join_condition = source_column == target_column
                    
                    # Adicionar o join à consulta
                    if join_type == "INNER":
                        from_obj = from_obj.join(target_model.__table__, join_condition)
                    elif join_type == "LEFT":
                        from_obj = from_obj.join(target_model.__table__, join_condition, isouter=True)
                    elif join_type == "RIGHT":
                        # SQLAlchemy não tem right join diretamente, então invertemos a condição
                        # Note: essa abordagem não é ideal para múltiplos joins, mas mantida para compatibilidade
                        from_obj = target_model.__table__.join(from_obj, join_condition, isouter=True)
                    else:  # Default to INNER
                        from_obj = from_obj.join(target_model.__table__, join_condition)
                
                # Definir a cláusula FROM
                query = query.select_from(from_obj)
                
                # Adicionar filtros (WHERE)
                filter_conditions = []
                for filter_info in filters:
                    operator = filter_info.get("operator", "=")
                    attr = filter_info["attribute"]
                    value = filter_info["value"]
                    
                    # Obter a coluna para o filtro
                    if "." in attr:
                        table_name, col_name = attr.split(".")
                        column_obj = get_column_from_table(table_name, col_name)
                    else:
                        column_obj = get_column_from_table(base_table, attr)
                    
                    # Aplicar o operador correto
                    if operator == "=":
                        filter_conditions.append(column_obj == value)
                    elif operator == "!=":
                        filter_conditions.append(column_obj != value)
                    elif operator == ">":
                        filter_conditions.append(column_obj > value)
                    elif operator == "<":
                        filter_conditions.append(column_obj < value)
                    elif operator == ">=":
                        filter_conditions.append(column_obj >= value)
                    elif operator == "<=":
                        filter_conditions.append(column_obj <= value)
                    elif operator.upper() == "LIKE":
                        filter_conditions.append(column_obj.like(value))
                    elif operator.upper() == "ILIKE":
                        filter_conditions.append(column_obj.ilike(value))
                    elif operator.upper() == "IN":
                        if isinstance(value, str):
                            # Se for string, dividir por vírgulas
                            values = [v.strip() for v in value.split(",")]
                            filter_conditions.append(column_obj.in_(values))
                        elif isinstance(value, list):
                            filter_conditions.append(column_obj.in_(value))
                        else:
                            filter_conditions.append(column_obj.in_([value]))
                    elif operator.upper() == "NOT IN":
                        if isinstance(value, str):
                            values = [v.strip() for v in value.split(",")]
                            filter_conditions.append(column_obj.notin_(values))
                        elif isinstance(value, list):
                            filter_conditions.append(column_obj.notin_(value))
                        else:
                            filter_conditions.append(column_obj.notin_([value]))
                    else:
                        raise ValueError(f"Operador '{operator}' não suportado")
                
                # Adicionar as condições de filtro à consulta
                if filter_conditions:
                    query = query.where(and_(*filter_conditions))
                  # Adicionar GROUP BY
                if group_by_attributes:
                    group_by_columns = []
                    for attr in group_by_attributes:
                        if "." in attr:
                            table_name, col_name = attr.split(".")
                            column_obj = get_column_from_table(table_name, col_name)
                        else:
                            # Se não tiver qualificação, buscar primeiro entre os aliases definidos
                            # e depois na tabela base
                            found = False
                            for table_name, model in table_aliases.items():
                                if hasattr(model, attr):
                                    column_obj = getattr(model, attr)
                                    found = True
                                    break
                            
                            if not found:
                                column_obj = get_column_from_table(base_table, attr)
                                
                        group_by_columns.append(column_obj)
                    
                    query = query.group_by(*group_by_columns)
                
                # Adicionar ORDER BY
                if order_by_columns:
                    order_by_clauses = []
                    for order_info in order_by_columns:
                        # Converter para dict se for um modelo Pydantic
                        order_dict = order_info
                        if hasattr(order_info, 'model_dump'):
                            order_dict = order_info.model_dump()
                        
                        # Verificar se está usando 'attribute' ou 'column' (para compatibilidade)
                        attr = order_dict.get("attribute", order_dict.get("column", ""))
                        direction = order_dict.get("direction", "ASC").upper()
                        
                        if not attr:
                            continue
                          # Obter a coluna para ordenação
                        if "." in attr:
                            table_name, col_name = attr.split(".")
                            column_obj = get_column_from_table(table_name, col_name)
                        else:
                            # Se não tiver qualificação, buscar primeiro entre os aliases definidos
                            # e depois na tabela base
                            found = False
                            for table_name, model in table_aliases.items():
                                if hasattr(model, attr):
                                    column_obj = getattr(model, attr)
                                    found = True
                                    break
                            
                            if not found:
                                column_obj = get_column_from_table(base_table, attr)
                        
                        # Adicionar a direção de ordenação
                        if direction == "DESC":
                            order_by_clauses.append(desc(column_obj))
                        else:  # ASC
                            order_by_clauses.append(asc(column_obj))
                    
                    query = query.order_by(*order_by_clauses)
                
                # Adicionar LIMIT
                query = query.limit(limit)
                
                # Compilar a consulta para exibir o SQL gerado
                compiled_query = query.compile(dialect=self.engine.dialect, compile_kwargs={"literal_binds": True})
                sql_query = str(compiled_query)
                
                # Executar a consulta
                result = session.execute(query).mappings().all()
                
                # Converter para lista de dicionários
                data = [dict(row) for row in result]
                
                return data, sql_query
        except Exception as e:
            print(f"Erro ao gerar relatório adhoc: {e}")
            raise e
