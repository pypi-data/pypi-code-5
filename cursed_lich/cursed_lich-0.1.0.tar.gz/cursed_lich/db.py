#!/usr/bin/env python

import os
import datetime

from sqlalchemy import (
    create_engine, 
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime
)

from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Crypto.Hash import SHA256

import terrain
from error import *

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

    def __repr__(self):
        return ('Hero(name=%s, mp=%s, pos=(%d,%d), inv=%d, '
            'p/d/n/c/s=%d/%d/%d/%d/%d)' % (
            self.name, self.mp, self.cell.x, self.cell.y,
            len(self.stashes[0].items) if self.stashes else 0,
            self.power, self.druid, self.necro, self.chaos, self.steam))

    def __str__(self):
        return self.__repr__()

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

    def __repr__(self):
        return 'User(username=%s, heroes=[%s])' % (
            self.username,
            ','.join([hero.name for hero in self.heroes]))

    def __str__(self):
        return self.__repr__()

class Session(Base):
    __tablename__ = 'session'
    session_id = Column(Integer, primary_key=True)
    request_session_id = Column(String, unique=True)
    # *-1 sessions per user
    user_id = Column(Integer, ForeignKey('user.user_id'))
    created = Column(DateTime)
    last_accessed = Column(DateTime)

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

def add_hero(sesh, username, heroname, start_pos=(1,1)):
    user = sesh.query(User).filter_by(username=username).first()
    if user is None:
        raise NoUserError(username)
    hero = sesh.query(Hero).filter_by(name=heroname).first()
    if hero is not None:
        raise HeroExistsError(heroname)
    cell = sesh.query(Cell).filter_by(x=start_pos[0], y=start_pos[1]).first()
    if cell is None:
        raise NoCellError('%s/%s at %s' % (username, heroname, start_pos))
    if cell.hero is not None:
        raise CellOccupiedError('%s/%s at %s occupied by %s' % 
            (username, heroname, start_pos, cell.hero.name))
    stash = Stash(name="%s's inventory" % heroname)
    hero = Hero(name=heroname)
    hero.user = user
    hero.cell = cell
    hero.stashes = [stash]
    sesh.add(hero)
    sesh.commit()
    return hero

def add_user(sesh, username, password):
    user = sesh.query(User).filter_by(username=username).first()
    if user is not None:
        raise UserExistsError(username)
    user = User(username=username)
    user.save_password(password)
    sesh.add(user)
    sesh.commit()
    return user

def list_heroes(sesh, username):
    user = sesh.query(User).filter_by(username=username).first()
    if user is None:
        raise NoUserError(username)
    for hero in user.heroes:
        print(hero)

def list_users(sesh):
    users = sesh.query(User).all()
    for user in users:
        print(user)

def create_request_session(sesh, user):
    if isinstance(user, basestring):
        username = user
        user = sesh.query(User).filter_by(username=username).first()
    else:
        username = user.username
    if user is None:
        raise NoUserError(username)
    sid = os.urandom(12).encode('base64')
    session = Session(request_session_id=sid)
    session.user = user
    session.created = datetime.datetime.now()
    session.last_accessed = datetime.datetime.now()
    sesh.add(session)
    sesh.commit()
    return session.request_session_id

def get_request_session(sesh, sid):
    return sesh.query(Session).filter_by(request_session_id=sid).first()
    
