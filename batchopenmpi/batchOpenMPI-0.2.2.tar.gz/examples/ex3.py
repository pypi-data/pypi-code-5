"""
 example with 'calls_expected' in addtoBatch used
"""

import batchOpenMPI
def f_mult(x) : 
    return x*2.0
f = batchOpenMPI.batchFunction(f_mult) #creating function wrapper

batchOpenMPI.begin_MPI_loop() # both the workers and the master process run the same code up until here
f.addtoBatch(4,calls_expected=4)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs
res = [f(4),f(4),f(4)] 
print(res)

#another test
f.addtoBatch(1)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs
res = f(1), f(1)

batchOpenMPI.end_MPI_loop(print_stats=True) #releases workers

print("*** jobs executed by workers should be 2 ,(5 calls made),jobs uncollected should = 1, jobs_master=1")
