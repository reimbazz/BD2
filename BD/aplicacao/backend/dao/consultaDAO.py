from sqlalchemy import inspect
# Importação relativa dentro do mesmo pacote
from .database import get_engine
from .database import connect

class ConsultaDAO:
    def __init__(self):
        self.engine = get_engine()
        self.connect = connect()

    def getAllTables(self):
        try:
            insp = inspect(self.engine)
            return insp.get_table_names(schema='public')
        except Exception as e:
            print(f"Erro ao buscar tabelas: {e}")
            raise e
    
    def getTableRelations(self, table_name: str):
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

    def getTableColumns(self, table_name: str):
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

    def getJoinedTablesColumns(self, base_table: str, joins: list):
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

    def getForeignKeyRelations(self, source_table: str, target_table: str):
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