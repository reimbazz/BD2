from sqlalchemy import inspect
from dao.database import get_engine
from dao.database import connect

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
