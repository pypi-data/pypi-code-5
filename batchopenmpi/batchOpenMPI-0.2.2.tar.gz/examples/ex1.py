"""
 example of how2use batchOpenMPI,
 simple example
"""

import batchOpenMPI
def f_inv_org(x) : 
    "function returns the inverse of a number"
    return 1.0/x
f_inv = batchOpenMPI.batchFunction(f_inv_org, permissible_exceptions = [ZeroDivisionError]) #creating function wrapper

batchOpenMPI.begin_MPI_loop() # both the workers and the master process run the same code up until here
print('this example script prints in the inverse of the integers from 0 to 9')
no = range(10) # creates [0,1,2,3,4,5,6,7,8,9]
for i in no :# adding all f_inv input and queing them for parallel processing
    f_inv.addtoBatch(i)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs
res = [] #used for storing results
for i in no :
    try :
        res.append(f_inv(i))
    except ZeroDivisionError :
        print("couldn't inverse " + str(i) + " due to 0 division error") 
print(res)

batchOpenMPI.end_MPI_loop(print_stats=True) #release workers, and print stats

