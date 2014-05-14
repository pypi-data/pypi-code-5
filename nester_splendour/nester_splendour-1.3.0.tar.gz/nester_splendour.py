'''
    This is a module named "nester.py" by Splendour
'''
def sortlist (sortedlist, indent = False, level = 0):
    '''
        This is a function to print all the items in a list.
        "sortedlist" is the target list. It can be a single list,
            or a list including list.
        "level" is the num to print tabs when printing the items
            in a list.
    '''
    for listitem in sortedlist:
        if isinstance(listitem, list):
            sortlist(listitem, indent, level + 1)
        else:
            if indent:
                for tab_num in range(level):
                    print("\t", end = '')
            print(listitem)
