"""
 downward dependency example
"""

import batchOpenMPI

#defining function
def f_org(x) :
    return x[0]*(x[1] + x[2])
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
bj = f.addtoBatch([2, g.addtoBatch(3) , h.addtoBatch(1)], multiDep=True)
print(bj)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs

print("""
f([x,y,z]) = x * (y + z)
g(x) = 1/x + 1
h(x) = x - 0.2

f([2,g(3),h(1)]) = %f
""" ) % (f([2,g(3),h(1)]))

print(bj)

batchOpenMPI.end_MPI_loop(print_stats=True)


print('** nothing should be solved on the masters')
