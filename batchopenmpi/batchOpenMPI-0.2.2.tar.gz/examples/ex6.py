"""
 batchOpenMPI.drop_previous_batch_results example
"""

import batchOpenMPI

#defining function
def f1_org(x) :
    return 4.0 / (x-1) / (x-3)
def f2_org(x) :
    return x + 1

# creating batch functions
f1 = batchOpenMPI.batchFunction(f1_org, permissible_exceptions = [ZeroDivisionError] )
f2 = batchOpenMPI.batchFunction(f2_org)

batchOpenMPI.begin_MPI_loop() 
batchOpenMPI.drop_previous_batch_results = True
# building processing que
inputs = range(10)

print("""
y(x) = f1(x) + f2(x)
where 
  f1(x) = 4 / (x-1) / (x-3)
  f2(x) = x + 1"")

inputs: """ + str(inputs))

print("""
as f1 will fail at 1 and 3. the results from f2 for these inputs will be uncollected.

the batchOpenMPI.drop_previous_batch_results = True, will when batchOpenMPI.processBatch() is called
again, will cause these uncollected results to be dropped.""")

f1.addtoBatch_multiple(inputs)
f2.addtoBatch_multiple(inputs)

batchOpenMPI.processBatch() #get the workers to calculate all the inputs

print("results") 
for x in inputs :
    try :
        print 'y(%d) = %f'%(x,f1(x) + f2(x))
    except ZeroDivisionError,msg :
        print 'y(%d) failed'%(x)
          
batchOpenMPI.processBatch() #get the workers to calculate all the inputs

batchOpenMPI.end_MPI_loop(print_stats=True) #releases workers

print('** should see 2 dropped results for the second function.')
