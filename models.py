# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Destination(Base):
    __tablename__ = 'destination'

    did = Column(Integer, primary_key=True, unique=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    name = Column(String(45), nullable=False)
    points = Column(Integer, nullable=False, server_default=text("'0'"))
    elevation = Column(Integer, nullable=False, server_default=text("'0'"))


class Photo(Base):
    __tablename__ = 'photos'

    pid = Column(Integer, primary_key=True, unique=True)
    sid = Column(ForeignKey(u'sumit.sid', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)

    sumit = relationship(u'Sumit')


class Sumit(Base):
    __tablename__ = 'sumit'

    sid = Column(Integer, primary_key=True)
    uid = Column(ForeignKey(u'users.uid', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    did = Column(ForeignKey(u'destination.did', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    time = Column(DateTime, nullable=False)

    destination = relationship(u'Destination')
    user = relationship(u'User')


class User(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True, unique=True)
    username = Column(String(45), nullable=False)
    elevation = Column(Integer, nullable=False, server_default=text("'0'"))
    points = Column(Integer, nullable=False, server_default=text("'0'"))
