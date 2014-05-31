#!/usr/bin/env python

import db

import random

class Terrain(object):
    ''' Types of terrain as enum. (number, character representation) '''
    DIRT = (0, ' ')
    WALL = (1, '#')
    TREE = (2, 't')

    ''' Access from CHARS array '''
    CHAR = zip(DIRT, WALL, TREE)[1]

    @staticmethod
    def create_terrain(width, height, z):
        cells = []
        for x in range(width):
            for y in range(height):
                t = random.randint(0,10)
                t = 0 if t > 2 else t
                cells += [db.Cell(x=x, y=y, z=z, typ=t)]
        return cells
