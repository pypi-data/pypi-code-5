#!/usr/bin/env python

class NoHeroError(Exception):
    pass

class NoUserError(Exception):
    pass

class HeroExistsError(Exception):
    pass

class UserExistsError(Exception):
    pass

class NoCellError(Exception):
    pass

class CellOccupiedError(Exception):
    pass
