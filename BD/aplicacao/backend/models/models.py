from typing import List, Optional

from sqlalchemy import BigInteger, CHAR, Double, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Countries(Base):
    __tablename__ = 'countries'
    __table_args__ = (
        PrimaryKeyConstraint('country_code', name='countries_pkey'),
        UniqueConstraint('name', name='countries_name_key')
    )

    country_code: Mapped[str] = mapped_column(CHAR(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    borders: Mapped[List['Borders']] = relationship('Borders', foreign_keys='[Borders.border_country_code]', back_populates='countries')
    borders_: Mapped[List['Borders']] = relationship('Borders', foreign_keys='[Borders.country_code]', back_populates='countries_')
    country_geography: Mapped[List['CountryGeography']] = relationship('CountryGeography', back_populates='countries')
    country_society: Mapped[List['CountrySociety']] = relationship('CountrySociety', back_populates='countries')
    currencies: Mapped[List['Currencies']] = relationship('Currencies', back_populates='countries')
    languages: Mapped[List['Languages']] = relationship('Languages', back_populates='countries')
    states: Mapped[List['States']] = relationship('States', back_populates='countries')


class Borders(Base):
    __tablename__ = 'borders'
    __table_args__ = (
        ForeignKeyConstraint(['border_country_code'], ['countries.country_code'], name='borders_border_country_code_fkey'),
        ForeignKeyConstraint(['country_code'], ['countries.country_code'], name='borders_country_code_fkey'),
        PrimaryKeyConstraint('id', name='borders_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(CHAR(3))
    border_country_code: Mapped[str] = mapped_column(CHAR(3))

    countries: Mapped['Countries'] = relationship('Countries', foreign_keys=[border_country_code], back_populates='borders')
    countries_: Mapped['Countries'] = relationship('Countries', foreign_keys=[country_code], back_populates='borders_')


class CountryGeography(Base):
    __tablename__ = 'country_geography'
    __table_args__ = (
        ForeignKeyConstraint(['country_code'], ['countries.country_code'], name='fk_country_geography'),
        PrimaryKeyConstraint('country_id', name='country_geography_pkey')
    )

    country_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(CHAR(3))
    area: Mapped[Optional[float]] = mapped_column(Double(53))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    lat: Mapped[Optional[float]] = mapped_column(Double(53))
    lng: Mapped[Optional[float]] = mapped_column(Double(53))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='country_geography')


class CountrySociety(Base):
    __tablename__ = 'country_society'
    __table_args__ = (
        ForeignKeyConstraint(['country_code'], ['countries.country_code'], name='fk_country_society'),
        PrimaryKeyConstraint('country_id', name='country_society_pkey')
    )

    country_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(CHAR(3))
    capital: Mapped[Optional[str]] = mapped_column(String(100))
    population: Mapped[Optional[int]] = mapped_column(BigInteger)

    countries: Mapped['Countries'] = relationship('Countries', back_populates='country_society')


class Currencies(Base):
    __tablename__ = 'currencies'
    __table_args__ = (
        ForeignKeyConstraint(['country_code'], ['countries.country_code'], name='currencies_country_code_fkey'),
        PrimaryKeyConstraint('id', name='currencies_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(CHAR(3))
    currency: Mapped[str] = mapped_column(String(100))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='currencies')


class Languages(Base):
    __tablename__ = 'languages'
    __table_args__ = (
        ForeignKeyConstraint(['country_code'], ['countries.country_code'], name='languages_country_code_fkey'),
        PrimaryKeyConstraint('id', name='languages_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(CHAR(3))
    language: Mapped[str] = mapped_column(String(100))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='languages')


class States(Base):
    __tablename__ = 'states'
    __table_args__ = (
        ForeignKeyConstraint(['country_code'], ['countries.country_code'], name='fk_states_country'),
        PrimaryKeyConstraint('state_id', name='states_pkey')
    )

    state_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(CHAR(3))
    name: Mapped[str] = mapped_column(String(100))
    abbreviation: Mapped[Optional[str]] = mapped_column(String(10))

    countries: Mapped['Countries'] = relationship('Countries', back_populates='states')
    cities: Mapped[List['Cities']] = relationship('Cities', back_populates='state')


class Cities(Base):
    __tablename__ = 'cities'
    __table_args__ = (
        ForeignKeyConstraint(['state_id'], ['states.state_id'], name='cities_state_id_fkey'),
        PrimaryKeyConstraint('city_id', name='cities_pkey')
    )

    city_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    population: Mapped[Optional[int]] = mapped_column(BigInteger)

    state: Mapped['States'] = relationship('States', back_populates='cities')
