import requests
import time
import unicodedata
import re
from sqlalchemy import create_engine, Column, String, Integer, Float, BigInteger, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CONFIGURAÇÃO DO BANCO
DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/trabalhoBD2'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# MODELOS
class Country(Base):
    __tablename__ = 'countries'
    alpha3code = Column(String(3), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

class CountryGeography(Base):
    __tablename__ = 'country_geography'
    country_id = Column(Integer, primary_key=True)
    country_alpha3code = Column(String(3), ForeignKey('countries.alpha3code'), nullable=False)
    area = Column(Float)
    borders = Column(ARRAY(String(3)))
    region = Column(String(100))
    lat = Column(Float)
    lng = Column(Float)

class CountrySociety(Base):
    __tablename__ = 'country_society'
    country_id = Column(Integer, primary_key=True)
    country_alpha3code = Column(String(3), ForeignKey('countries.alpha3code'), nullable=False)
    capital = Column(String(100))
    population = Column(BigInteger)
    currencies = Column(ARRAY(String))
    language = Column(ARRAY(String))

class State(Base):
    __tablename__ = 'states'
    state_id = Column(Integer, primary_key=True)
    country_alpha3code = Column(String(3), ForeignKey('countries.alpha3code'), nullable=False)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10))

class City(Base):
    __tablename__ = 'cities'
    city_id = Column(Integer, primary_key=True)
    state_id = Column(Integer, ForeignKey('states.state_id'), nullable=False)
    name = Column(String(100), nullable=False)
    population = Column(BigInteger)

# CRIAR TABELAS (caso ainda não existam)
Base.metadata.create_all(engine)

# ETAPA 1: Carregar países (RestCountries)
def load_countries():
    url = 'https://restcountries.com/v3.1/all'
    response = requests.get(url)
    countries = response.json()

    for c in countries:
        try:
            name = c['name']['common']
            alpha3 = c.get('cca3')
            area = c.get('area')
            borders = c.get('borders', [])
            region = c.get('region')
            latlng = c.get('latlng', [None, None])
            lat, lng = (latlng + [None, None])[:2]
            capital = c.get('capital', [None])[0]
            population = c.get('population')
            currencies = list(c.get('currencies', {}).keys())
            languages = list(c.get('languages', {}).values())

            session.merge(Country(alpha3code=alpha3, name=name))
            session.add(CountryGeography(
                country_alpha3code=alpha3,
                area=area,
                borders=borders,
                region=region,
                lat=lat,
                lng=lng
            ))
            session.add(CountrySociety(
                country_alpha3code=alpha3,
                capital=capital,
                population=population,
                currencies=currencies,
                language=languages
            ))

        except Exception as e:
            print(f"[Erro - {c.get('name', {}).get('common', '')}]: {e}")

    session.commit()
    print("✔ Países carregados.")

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

def load_states_and_cities_with_population(start=0, end=10, pause=3):
    countries = (
        session.query(Country)
        .order_by(Country.alpha3code)
        .offset(start)
        .limit(end - start)
        .all()
    )
    print(f"\n🔢 Carregando países de {start} até {end - 1} (ordenados por alpha3code)...\n")

    for country in countries:
        print(f"\n🔄 País: {country.name} ({country.alpha3code})")

        try:
            # 1) Buscar todas as cidades com população do país via rota filter
            pop_url = "https://countriesnow.space/api/v0.1/countries/population/cities/filter"
            pop_resp = requests.post(
                pop_url,
                json={"country": country.name, "order": "asc", "orderBy": "name"},
                timeout=20
            )
            pop_data = pop_resp.json()

            if pop_data.get('error') or 'data' not in pop_data:
                print(f"❌ Não foi possível obter população das cidades de {country.name}")
                continue

            city_population_map = {}
            for city_info in pop_data['data']:
                city_name = city_info.get('city')
                counts = city_info.get('populationCounts', [])
                if counts:
                    latest_pop = counts[-1]
                    try:
                        population = int(latest_pop['value'].replace(',', ''))
                    except:
                        population = None
                else:
                    population = None

                if population is not None and city_name:
                    cleaned_name = clean_city_name(city_name)
                    city_population_map[normalize_text(cleaned_name)] = population

            print(f"✅ População obtida para {len(city_population_map)} cidades de {country.name}")

            # 2) Buscar estados
            state_url = "https://countriesnow.space/api/v0.1/countries/states"
            state_resp = requests.post(state_url, json={"country": country.name}, timeout=10)
            state_data = state_resp.json()

            if state_data.get('error') or 'data' not in state_data or not state_data['data'].get('states'):
                print(f"❌ Estados não encontrados para {country.name}")
                continue

            for state in state_data['data']['states']:
                state_name = state.get('name')
                state_abbr = state.get('state_code') or None
                if not state_name:
                    continue

                new_state = State(
                    country_alpha3code=country.alpha3code,
                    name=state_name,
                    abbreviation=state_abbr
                )
                session.add(new_state)
                session.flush()  # gera state_id

                # 3) Buscar cidades do estado
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
                    normalized_city_name = normalize_text(city_name)
                    population = city_population_map.get(normalized_city_name)
                    if population is not None:
                        session.add(City(
                            state_id=new_state.state_id,
                            name=city_name,
                            population=population
                        ))
                        print(f"   🏙 Cidade: {city_name} - População: {population}")
                        cities_added += 1

                print(f"✅ Estado {state_name} com {cities_added} cidades populadas")

            session.commit()
            print(f"\n✔ País {country.name} processado com sucesso.\n")

            time.sleep(pause)

        except Exception as e:
            print(f"❌ Erro ao processar {country.name}: {e}")
            session.rollback()
            continue


