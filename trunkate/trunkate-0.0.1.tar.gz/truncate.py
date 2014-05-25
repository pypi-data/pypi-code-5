import sys

def truncate(str, limit, ellipsis='...'): 
    return str[:limit] + ellipsis if len(str) > limit else str 

sys.modules[__name__] = truncate
