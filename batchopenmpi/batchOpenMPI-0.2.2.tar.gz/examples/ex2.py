"""
 example with multiRef
"""

import batchOpenMPI
def f_mult(x) : 
    return x*2.0
f = batchOpenMPI.batchFunction(f_mult,multiRef=True) #creating function wrapper

batchOpenMPI.begin_MPI_loop(print_launch_messages=False) # both the workers and the master process run the same code up until here
no = range(10) + range(10) # creates [0,1,2,3,4,5,6,7,8,9] x 2
for i in no :# adding all f_inv input and queing them for parallel processing
    f.addtoBatch(i)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs
res = [] #used for storing results
for i in no :
    res.append(f(i))
print(res)

batchOpenMPI.end_MPI_loop(print_stats=True) #releases workers

print("*** jobs executed by workers should be %i, out of the total of %i" % (len(no)/2,len(no)) )
