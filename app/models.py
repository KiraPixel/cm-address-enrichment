from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import app.config as config


Base = declarative_base()

class CashCesar(Base):
    __tablename__ = 'cash_cesar'
    unit_id = Column(Integer, primary_key=True, index=True)
    object_name = Column(Text, nullable=False)
    pin = Column(Integer, default=0)
    vin = Column(Text, nullable=False)
    last_time = Column(Integer, default=0)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    created_at = Column(Integer, default=0)
    device_type = Column(Text, nullable=False)
    linked = Column(Boolean, nullable=True, default=False)  # TINYINT(1) NULL DEFAULT '0'

class CashAxenta(Base):
    __tablename__ = 'cash_axenta'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False, default=0)
    nm = Column(Text, nullable=False)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    gps = Column(Integer, default=0)
    last_time = Column(Integer, default=0)
    last_pos_time = Column(Integer, default=0)
    connected_status = Column(Boolean, nullable=True, default=False)
    cmd = Column(Text, nullable=True, default='')
    sens = Column(Text, nullable=True, default='')
    valid_nav = Column(Integer, nullable=True, default=1)

class Coord(Base):
    __tablename__ = 'coord_cash'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    address = Column(String(100), nullable=True)
    updated_time = Column(Integer, nullable=False, default=0)


class SystemSettings(Base):
    __tablename__ = 'system_settings'
    id = Column(Integer, primary_key=True)
    enable_voperator = Column(Integer)
    enable_xml_parser = Column(Integer)
    enable_db_cashing = Column(Integer)
    enable_address_enrichment = Column(Integer)


def get_engine():
    """Возвращает объект engine для базы данных"""
    return create_engine(config.SQLALCHEMY_DATABASE_URL)


def create_db():
    """Создает базу данных и таблицы"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def create_session(engine):
    """Создает и возвращает сессию"""
    Session = sessionmaker(bind=engine)
    return Session()
