CREATE TABLE countries (
    alpha3code CHAR(3) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE country_geography (
    country_id SERIAL PRIMARY KEY,
    country_alpha3code CHAR(3) NOT NULL REFERENCES countries(alpha3code),
    area FLOAT,
    borders CHAR(3)[], -- lista de países vizinhos usando alpha3code
    region VARCHAR(100),
    lat FLOAT,
    lng FLOAT
);

CREATE TABLE country_society (
    country_id SERIAL PRIMARY KEY,
    country_alpha3code CHAR(3) NOT NULL REFERENCES countries(alpha3code),
    capital VARCHAR(100),
    population BIGINT,
    currencies VARCHAR[], -- array de moedas
    language VARCHAR[]     -- array de idiomas
);

CREATE TABLE states (
    state_id SERIAL PRIMARY KEY,
    country_alpha3code CHAR(3) NOT NULL REFERENCES countries(alpha3code),
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10)
);

CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    state_id INT NOT NULL REFERENCES states(state_id),
    name VARCHAR(100) NOT NULL,
    population BIGINT
);

--Scripts para correcao do banco

-- Renomeando coluna para ficar mais legível e consistente
ALTER TABLE countries RENAME COLUMN alpha3code TO country_code;
ALTER TABLE country_geography RENAME COLUMN country_alpha3code TO country_code;
ALTER TABLE country_society RENAME COLUMN country_alpha3code TO country_code;
ALTER TABLE states RENAME COLUMN country_alpha3code TO country_code;
ALTER TABLE country_geography
    DROP CONSTRAINT country_geography_country_alpha3code_fkey,
    ADD CONSTRAINT fk_country_geography FOREIGN KEY (country_code) REFERENCES countries(country_code);

ALTER TABLE country_society
    DROP CONSTRAINT country_society_country_alpha3code_fkey,
    ADD CONSTRAINT fk_country_society FOREIGN KEY (country_code) REFERENCES countries(country_code);

ALTER TABLE states
    DROP CONSTRAINT states_country_alpha3code_fkey,
    ADD CONSTRAINT fk_states_country FOREIGN KEY (country_code) REFERENCES countries(country_code);

-- Novas tabelas
CREATE TABLE languages (
    id SERIAL PRIMARY KEY,
    country_code CHAR(3) NOT NULL REFERENCES countries(country_code),
    language VARCHAR(100) NOT NULL
);

CREATE TABLE currencies (
    id SERIAL PRIMARY KEY,
    country_code CHAR(3) NOT NULL REFERENCES countries(country_code),
    currency VARCHAR(100) NOT NULL
);

CREATE TABLE borders (
    id SERIAL PRIMARY KEY,
    country_code CHAR(3) NOT NULL REFERENCES countries(country_code),
    border_country_code CHAR(3) NOT NULL REFERENCES countries(country_code)
);

-- Passando dados para as novas tabelas
INSERT INTO languages (country_code, language)
SELECT country_code, unnest(language)
FROM country_society
WHERE language IS NOT NULL;

INSERT INTO currencies (country_code, currency)
SELECT country_code, unnest(currencies)
FROM country_society
WHERE currencies IS NOT NULL;

INSERT INTO borders (country_code, border_country_code)
SELECT country_code, unnest(borders)
FROM country_geography
WHERE borders IS NOT NULL;

-- Removendo colunas antigas
ALTER TABLE country_society
    DROP COLUMN currencies,
    DROP COLUMN language;

ALTER TABLE country_geography
    DROP COLUMN borders;

-- Criacao dos usuarios e permissões
CREATE ROLE documentador;
CREATE ROLE programador;
CREATE ROLE dba;

CREATE USER hiara WITH PASSWORD '1234';
GRANT documentador TO hiara;

CREATE USER paulo WITH PASSWORD '1234';
GRANT programador TO paulo;

CREATE USER reimberg WITH PASSWORD '1234';
GRANT dba TO reimberg;

CREATE USER joao WITH PASSWORD '1234';
GRANT programador TO joao;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO documentador;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO programador;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dba WITH GRANT OPTION;

GRANT documentador TO dba WITH ADMIN OPTION;
GRANT programador TO dba WITH ADMIN OPTION;

GRANT USAGE ON SCHEMA public TO documentador, programador, dba;
--Criação de índices

-- Tabela countries
-- O campo country_code já é PK, então já tem índice
CREATE UNIQUE INDEX idx_country_name ON countries(name);

-- Tabela country_geography
-- FK
CREATE INDEX idx_geography_country_code ON country_geography(country_code);
-- Filtros por região ou área são comuns
CREATE INDEX idx_geography_region ON country_geography(region);
CREATE INDEX idx_geography_area ON country_geography(area);

-- Tabela country_society
-- FK
CREATE INDEX idx_society_country_code ON country_society(country_code);

-- Busca por capital e população
CREATE INDEX idx_society_capital ON country_society(capital);
CREATE INDEX idx_society_population ON country_society(population);

-- Tabela states
-- FK
CREATE INDEX idx_states_country_code ON states(country_code);

-- Nome e sigla são importantes para busca
CREATE INDEX idx_states_name ON states(name);
CREATE INDEX idx_states_abbreviation ON states(abbreviation);

-- Tabela cities
-- FK
CREATE INDEX idx_cities_state_id ON cities(state_id);

-- Nome da cidade e população são comuns em filtros
CREATE INDEX idx_cities_name ON cities(name);
CREATE INDEX idx_cities_population ON cities(population);

-- Tabela languages
-- FK
CREATE INDEX idx_languages_country_code ON languages(country_code);
CREATE INDEX idx_languages_language ON languages(language);

-- Tabela currencies
-- FK
CREATE INDEX idx_currencies_country_code ON currencies(country_code);
CREATE INDEX idx_currencies_currency ON currencies(currency);

-- Tabela borders
-- FKs
CREATE INDEX idx_borders_country_code ON borders(country_code);
CREATE INDEX idx_borders_border_country_code ON borders(border_country_code);
