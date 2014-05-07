"""
 simple dependency example, where an input depency raises an error
"""

import batchOpenMPI

#defining function
def f_org(x) :
    return x ** 2
def g_org(x) :
    return 1.0/x  + 1
def h_org(x) :
    return x - 0.2

# creating batch functions
f = batchOpenMPI.batchFunction(f_org)
g = batchOpenMPI.batchFunction(g_org,True,permissible_exceptions=[ZeroDivisionError])
h = batchOpenMPI.batchFunction(h_org)

batchOpenMPI.begin_MPI_loop() 
# building processing que
print(f.addtoBatch(g.addtoBatch(3)))
print(h.addtoBatch(g.addtoBatch(3)))
print(f.addtoBatch(g.addtoBatch(0)))
batchOpenMPI.processBatch() #get the workers to calculate all the inputs

# now actuall code
try :
    res3 = str(f(g(0)))
except ZeroDivisionError,msg :
    res3 = 'no solution'

print("""
f(x) = x ** 2
g(x) = 1.0/x + 1
h(x) = x - 0.2

f(g(3)) = %f
h(g(3)) = %f
f(g(0)) = %s
""" ) % (f(g(3)), h(g(3)), res3)

batchOpenMPI.end_MPI_loop(print_stats=True) #releases workers

print('** nothing should be solved on the masters, also 5 jobs where passed but one was discarded')
