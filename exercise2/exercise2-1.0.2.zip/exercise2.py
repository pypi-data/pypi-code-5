""" exercise module """
def printList( alist, level=0 ) :
    for name in alist :
        if isinstance( name, list ) :
            printList( name, level+1 );
        else :
            for count in range( level ) :
                print( "\t", end='' );
            print( name );
