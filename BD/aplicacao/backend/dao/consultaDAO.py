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