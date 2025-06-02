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
