""" exercise module """
def printList( alist ) :
	for name in alist :
		if isinstance( name, list ) :
			printList( name );
		else :
			print( name );
