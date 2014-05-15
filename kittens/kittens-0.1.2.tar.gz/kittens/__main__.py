import sys
import kittens

def print_usage():
	"""
	Print a usage message and then quit.

	"""

	print("Usage: %s phone_number message [repetitions]" % sys.argv[0])
	sys.exit(1)

if len(sys.argv) < 3:
	print_usage()

phone_number = sys.argv[1]
message = sys.argv[2]
if len(sys.argv) > 3:
	repetitions = sys.argv[3]
else:
	repetitions = 1
for i in range(repetitions):
	print(kittens.fire_kitten(phone_number, message, kittens._select_image()))
