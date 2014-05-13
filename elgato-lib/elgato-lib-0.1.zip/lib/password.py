__author__ = 'dsedad'

import random
import string

def generate(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

