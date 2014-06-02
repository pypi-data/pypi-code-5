#!/usr/bin/env python

import os

from sqlalchemy import (
    create_engine, 
    MetaData, Table, Column, ForeignKey,
    Integer, String,
)

from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Crypto.Hash import SHA256

import terrain

Base = declarative_base()

class Item(Base):
    __tablename__ = 'item'
    item_id = Column(Integer, primary_key=True)
    # *-1 part of a stash
    stash_id = Column(Integer, ForeignKey('stash.stash_id'))
    # "Sword of Slicery"
    name = Column(String(64))

class Stash(Base):
    __tablename__ = 'stash'
    stash_id = Column(Integer, primary_key=True)
    # *-1 stashes on hero
    hero_id = Column(Integer, ForeignKey('hero.hero_id'))
    # *-1 stashes in cell
    cell_id = Column(Integer, ForeignKey('cell.cell_id'))
    # 1-* items
    items = relationship('Item', backref='stash')
    # "Foo's corpse"
    name = Column(String(64)) 

class Hero(Base):
    __tablename__ = 'hero'
    hero_id = Column(Integer, primary_key=True)
    # *-1 heros per user
    user_id = Column(Integer, ForeignKey('user.user_id'))
    # 1-1 hero per cell
    cell_id = Column(Integer, ForeignKey('cell.cell_id'))
    # 1-* stashes
    stashes = relationship('Stash', backref='hero')
    # "Foo the Barbarianator"
    name = Column(String(64), unique=True)
    mp = Column(Integer, default=10)
    power = Column(Integer, default=1)
    druid = Column(Integer, default=1)
    necro = Column(Integer, default=1)
    chaos = Column(Integer, default=1)
    steam = Column(Integer, default=1)

class Cell(Base):
    __tablename__ = 'cell'
    cell_id = Column(Integer, primary_key=True)
    # 1-1 hero per cell
    hero = relationship('Hero', uselist=False, backref='cell')
    # 1-* stashes in cell
    stashes = relationship('Stash', backref='cell')
    # x,y position to display
    x = Column(Integer, index=True)
    y = Column(Integer, index=True)
    # Integer z represents enum name of world: midgaard, underground...
    z = Column(Integer, index=True)
    # typ represents the type of terrain: brick, mountain, grass, swamp...
    typ = Column(Integer)

    def __repr__(self):
        return 'Cell(id=%s, pos=(%s, %s, %s), typ=%s, hero=%s, stash=%s)' % (
            self.cell_id, self.x, self.y, self.z, self.typ,
            self.hero.name if self.hero else 'None',
            len(self.stashes) if self.stashes else '0',
        )

    def __str__(self):
        return self.__repr__()

    def get_char(self):
        return terrain.Terrain.CHAR[self.z]

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    # 1-* heros
    heroes = relationship('Hero', backref='user')
    # 1-* sessions
    sessions = relationship('Session', backref='user')
    # login name
    username = Column(String, unique=True)
    # a salty SHA256 hash, about a zillion rounds, cryptographically speaking
    passhash = Column(String)
    
    @staticmethod
    def hash(password, salt=None):
        ''' Algo = sha256(salt + pass + salt_reversed)
        Stupid... but gets around prebuilt rainbow tables and
        stupid cloud hash cracking services.
        '''
        if salt is None:
            salt = os.urandom(8).encode('base64')
        plain_text = salt + password + salt[::-1]
        cypher_text = SHA256.new(plain_text).digest()
        return '%s:%s' % (
            salt.encode('base64').strip(),
            cypher_text.encode('base64').strip(),
        )

    def auth(self, password):
        salt, hash = self.passhash.split(':')
        return (self.passhash == User.hash(password,
            salt=salt.decode('base64')))
    
    def save_password(self, password):
        self.passhash = User.hash(password)

class Session(Base):
    __tablename__ = 'session'
    session_id = Column(Integer, primary_key=True)
    request_session_id = Column(String, unique=True)
    # *-1 sessions per user
    user_id = Column(Integer, ForeignKey('user.user_id'))

def init_db(eng):
    ''' initialize a db with starting tables '''
    Base.metadata.create_all(eng)

def create_session(db_path):
    ''' Start a db engine up, or create a new one '''
    from sqlalchemy.engine.reflection import Inspector
    eng = create_engine('sqlite:///%s' % db_path)
    inspector = Inspector.from_engine(eng)
    tables = list(inspector.get_table_names())
    if 'midgaard' not in tables:
        init_db(eng)
    Session = sessionmaker(bind=eng)
    return Session

