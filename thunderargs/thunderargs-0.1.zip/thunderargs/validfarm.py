__author__ = 'thunder'


def len_gt(x):
    def validator(value):
        return len(value) > x
    return validator


def len_lt(x):
    def validator(value):
        return len(value) < x
    return validator


def len_eq(x):
    def validator(value):
        return len(value) == x
    return validator


def len_neq(x):
    def validator(value):
        return len(value) != x
    return validator


def val_gt(x):
    def validator(value):
        return value > x
    return validator


def val_lt(x):
    def validator(value):
        return value < x
    return validator


def val_eq(x):
    def validator(value):
        return value == x
    return validator


def val_neq(x):
    def validator(value):
        return value != x
    return validator


def val_in(x):
    def validator(value):
        return value in x
    return validator


def val_nin(x):
    def validator(value):
        return not value in x
    return validator