from sqlalchemy import MetaData, Table, create_engine, inspect

# Substitua pela sua string de conexão real
DATABASE_URL = 'postgresql://paulo:1234@localhost:5432/trabalhoBD2'

engine = create_engine(DATABASE_URL)

# Teste manual
if __name__ == "__main__":
    insp = inspect(engine)
    colunas = insp.get_columns("countries", schema='public')
    for col in colunas:
        print(col)
