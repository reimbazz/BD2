import requests
import time
import unicodedata
import re
from sqlalchemy import create_engine, Column, String, Integer, BigInteger, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CONFIGURAÇÃO DO BANCO
DATABASE_URL = 'postgresql://paulo:1234@localhost:5432/trabalhoBD2'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# MODELOS (Com as novas alterações do banco)
class Country(Base):
    __tablename__ = 'countries'
    country_code = Column(String(3), primary_key=True)  # Coluna renomeada conforme Script.sql
    name = Column(String(100), unique=True, nullable=False)

class State(Base):
    __tablename__ = 'states'
    state_id = Column(Integer, primary_key=True)
    country_code = Column(String(3), ForeignKey('countries.country_code'), nullable=False)  # Coluna renomeada
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10))

class City(Base):
    __tablename__ = 'cities'
    city_id = Column(Integer, primary_key=True)
    state_id = Column(Integer, ForeignKey('states.state_id'), nullable=False)
    name = Column(String(100), nullable=False)
    population = Column(BigInteger)

# Função para normalizar texto (remover acentos, tornar minúsculo)
def normalize_text(text):
    if not text:
        return ''
    return ''.join(
        c for c in unicodedata.normalize('NFD', text.lower())
        if unicodedata.category(c) != 'Mn'
    )

# Função auxiliar para limpar o nome da cidade
def clean_city_name(city_name):
    """Remove conteúdos entre parênteses, como 'Flint (MI)' -> 'Flint'"""
    return re.sub(r"\s*\([^)]*\)", "", city_name).strip()

def load_missing_cities(start=236, end=251, pause=3):
    """
    Carrega cidades que não têm informação de população.
    Evita duplicar cidades que já existem no banco.
    
    Args:
        start: Índice inicial dos países a processar
        end: Índice final (None para processar todos)
        pause: Pausa entre requisições à API
    """
    # Obter todos os países do banco
    countries_query = select(Country).order_by(Country.country_code)
    
    if end is not None:
        countries = session.execute(countries_query.offset(start).limit(end - start)).scalars().all()
        print(f"\n🔢 Carregando países de {start} até {end - 1} (ordenados por country_code)...\n")
    else:
        countries = session.execute(countries_query.offset(start)).scalars().all()
        print(f"\n🔢 Carregando países a partir do índice {start}...\n")

    for country in countries:
        print(f"\n🔄 País: {country.name} ({country.country_code})")

        try:
            # Obter estados do país
            state_url = "https://countriesnow.space/api/v0.1/countries/states"
            state_resp = requests.post(state_url, json={"country": country.name}, timeout=10)
            state_data = state_resp.json()

            if state_data.get('error') or 'data' not in state_data or not state_data['data'].get('states'):
                print(f"❌ Estados não encontrados para {country.name}")
                continue

            for state_info in state_data['data']['states']:
                state_name = state_info.get('name')
                if not state_name:
                    continue

                # Verificar se o estado já existe no banco
                existing_state = session.execute(
                    select(State).where(
                        State.country_code == country.country_code,
                        State.name == state_name
                    )
                ).scalar_one_or_none()

                
                state_id = existing_state.state_id
                print(f"ℹ️ Usando estado existente: {state_name}")

                # Buscar cidades já existentes neste estado
                existing_cities = session.execute(
                    select(City.name).where(City.state_id == state_id)
                ).scalars().all()
                
                existing_cities_normalized = [normalize_text(city) for city in existing_cities]
                print(f"   ℹ️ {len(existing_cities)} cidades já existem para este estado")

                # Obter cidades deste estado via API
                city_url = "https://countriesnow.space/api/v0.1/countries/state/cities"
                city_resp = requests.post(
                    city_url,
                    json={"country": country.name, "state": state_name},
                    timeout=10
                )
                city_data = city_resp.json()

                if city_data.get('error') or not city_data.get('data'):
                    print(f"⚠️ Cidades não encontradas para estado: {state_name}")
                    continue

                cities_added = 0
                for city_name in city_data['data']:
                    cleaned_name = clean_city_name(city_name)
                    normalized_name = normalize_text(cleaned_name)
                    
                    # Verificar se a cidade já existe (ignorando acentos e maiúsculas/minúsculas)
                    if normalized_name in existing_cities_normalized:
                        continue
                    
                    # Adicionar cidade sem informação de população
                    session.add(City(
                        state_id=state_id,
                        name=city_name,
                        population=None  # População não disponível
                    ))
                    cities_added += 1

                if cities_added > 0:
                    print(f"   🏙 Adicionadas {cities_added} novas cidades sem informação de população")
                else:
                    print(f"   ℹ️ Nenhuma cidade nova encontrada para este estado")

            session.commit()
            print(f"\n✔ País {country.name} processado com sucesso.\n")
            time.sleep(pause)

        except Exception as e:
            print(f"❌ Erro ao processar {country.name}: {e}")
            session.rollback()
            time.sleep(pause)
            continue

if __name__ == "__main__":
    print("🚀 Iniciando carga de cidades sem informações de população...")
    
    load_missing_cities()
    
    print("\n✅ Processo concluído!")
