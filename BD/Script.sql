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