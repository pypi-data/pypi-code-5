"""
 setting working directory example.
"""

import batchOpenMPI, os

def ex_prog(x) :
    "simulates an external program that writes its output to file"
    f = file('results.txt','w')
    f.write(str(x ** 2))
    f.close() 

def fun_org(x) :
    ex_prog(x)
    f = file('results.txt','r')
    res = float(f.readline().strip())
    f.close()
    return res

fun = batchOpenMPI.batchFunction(fun_org) #creating function wrapper
batchOpenMPI.WorkingDir_base = 'workspace' #giving each worker a directory to workin.

batchOpenMPI.begin_MPI_loop() #split workers and master
no = range(10)  #creating inputs

print("""f(x) = x ** 2

the results will be written to file, and as the result file name will be the same. 
each process will be given its own workspace using batchOpenMPI.WorkingDir_base""")

print("\ninputs :" + str(no))


for i in no :# adding all f_inv input and queing them for parallel processing
    fun.addtoBatch(i)
batchOpenMPI.processBatch() #get the workers to calculate all the inputs
res = [] #used for storing results
for i in no :
    res.append(fun(i))
print("results : " + str(res))

batchOpenMPI.end_MPI_loop(print_stats=True) #releases workers

print('note that the working directory are deleted when the job completes...')

