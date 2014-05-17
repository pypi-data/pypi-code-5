# Utility Module
import random
import math
import sys

def error(*arg):
    print ("Number of errors: %d\n" % len(arg))
    for i in range(len(arg)):
        print ("Error [%d]: %s\n" %(i,arg[i]),file = sys.stderr)

def assign_code():
    '''
        () -> int
        return the assigned number

        >> assign_code()
        10q0
        >> assign_code()
        547a4
    '''

    # Varibles used in the assign_code()
    value_to_use = [22,3,4,2,3,2,3,3,111,2232,44,323,90909,9,23]
    number_to_use = [1,2,3,42,5,3,5,3,4,3,32,4,2,2,4]
    assigned_code = '' # The end result

    big_number = number_to_use[0] # let big_number be the largest number
    big_value = value_to_use[0] # let big_value be the largest number

    try:
        for n in range(len(number_to_use)):
            if (number_to_use[n] > big_number):
                big_number = number_to_use[n]
        n_use = random.randint(0,big_number)
        n_use*=100
        for v in range(len(value_to_use)):
            if (number_to_use[v] > big_value):
                big_value = value_to_use[v] # Largest value
        # Making it more harder
        v_use = random.randint(0,big_value)
        v_use*=100
    except ValueError:
        error("Code Generation")

    if (n_use > v_use):
        v_use+=n_use


    assigned_code = int(math.sqrt(random.randint(n_use,v_use))) # Creating code...
    assigned_code = math.sqrt(assigned_code * 100 * 100)
    
    return (int(assigned_code))

    
        
