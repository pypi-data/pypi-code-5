
import util_random as util
username = ''
password = ''

check = False
box_created = False
try:
    box_code = util.assign_code()
except:
    box_code=000
    print "Box Code creation failed!\n"
