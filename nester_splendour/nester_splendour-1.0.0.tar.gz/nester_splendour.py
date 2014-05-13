'''
    This is a module named "nester.py" by Splendour
'''
def sortlist (sortedlist):
    '''
        This is a function to print all the items in a list.
        "sortedlist" is the target list. It can be a single list,
            or a list including list.
    '''
    for listitem in sortedlist:
            if isinstance(listitem,list):
                    sortlist(listitem)
            else:
                    print(listitem)
