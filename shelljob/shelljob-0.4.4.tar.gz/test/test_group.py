import sys

from shelljob import proc

def test_group():
	sp = proc.Group()

	for i in range(0,5):
		sp.run( ['ls', '-al', '/usr/local'] )
	while sp.is_pending():
		lines = sp.readlines()
		for pc, line in lines:
			sys.stdout.write( "{}:{}".format( pc.pid, line ) )
