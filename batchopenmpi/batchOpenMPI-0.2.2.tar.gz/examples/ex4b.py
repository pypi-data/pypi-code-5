"""
 simple dependency example, alternative version using multiRef
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
g = batchOpenMPI.batchFunction(g_org,True)
h = batchOpenMPI.batchFunction(h_org)

batchOpenMPI.begin_MPI_loop() 
# building processing que
print(f.addtoBatch(g.addtoBatch(3)))
print(h.addtoBatch(g.addtoBatch(3)))
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

batchOpenMPI.end_MPI_loop(print_stats=True)

print('** nothing should be solved on the masters')
