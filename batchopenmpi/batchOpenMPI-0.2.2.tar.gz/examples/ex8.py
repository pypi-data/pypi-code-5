"""
 example of how2use batchOpenMPI, with lastProcessBatch=True to avoid process being tied down unessarcyilly
"""

import batchOpenMPI, time
def randomPause_base(pause) : 
    time.sleep(pause)
randomPause = batchOpenMPI.batchFunction(randomPause_base)

batchOpenMPI.begin_MPI_loop()
print('lastProcessBatch=True example/test')
pauses = [1,3]
for pause in pauses :
    randomPause.addtoBatch(pause)
batchOpenMPI.processBatch(lastProcessBatch=True) 
for pause in pauses:
    randomPause(pause)

batchOpenMPI.end_MPI_loop(print_stats=True)

print('The first worker should have exited before the last worker, and spent less time processing')
