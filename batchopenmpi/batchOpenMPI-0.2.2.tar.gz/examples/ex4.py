"""
 simple dependency example,
"""

import batchOpenMPI

#defining function
def f_org(x) :
    return x ** 2
def g_org(x) :
    return x + 1
def h_org(x) :
    return x - 0.2

# creating batch functions
f = batchOpenMPI.batchFunction(f_org)
g = batchOpenMPI.batchFunction(g_org)
h = batchOpenMPI.batchFunction(h_org)

batchOpenMPI.begin_MPI_loop() 
# building processing que
bi = g.addtoBatch(3,2)
print(f.addtoBatch(bi))
print(h.addtoBatch(bi))
batchOpenMPI.processBatch() #get the workers to calculate all the inputs

# now actuall code
print (
"""
f(x) = x ** 2
g(x) = x + 1
h(x) = x - 0.2

f(g(3)) = %f
h(g(3)) = %f
""" ) % (f(g(3)), h(g(3)))

batchOpenMPI.end_MPI_loop(print_stats=True) #releases workers

print('** nothing should be solved on the masters')
