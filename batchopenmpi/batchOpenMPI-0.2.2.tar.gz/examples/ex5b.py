"""
 downward dependency example, in this case, 10 of the 11 jobs will dependen on 1, 
 call with 10 worker processes and see if all of them get given a job to perform
"""

import batchOpenMPI

#defining function
def f_org(x) :
    return (x[1] + x[0])
def g_org(x) :
    return x + 1

# creating batch functions
f = batchOpenMPI.batchFunction(f_org)
g = batchOpenMPI.batchFunction(g_org)

batchOpenMPI.begin_MPI_loop() 

print("""in this case, 10 of the 11 jobs will dependen on 1, 
 call with 10 worker processes and see if all of them get given a job to perform""")

# building processing que
gi = g.addtoBatch(3,10)
x_vals = range(10)
for x in x_vals :
    f.addtoBatch([x, gi], multiDep=True)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs

res = []
for x in x_vals :
    res.append(f([x, g(3)]))

print(res)

batchOpenMPI.end_MPI_loop(print_stats=True) #release workers

print('** nothing should be solved on the masters, make sure each worker has a job completed')
