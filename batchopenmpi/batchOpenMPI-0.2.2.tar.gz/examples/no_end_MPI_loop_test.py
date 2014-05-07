import batchOpenMPI

batchOpenMPI.begin_MPI_loop()

print('Basic test to see if mpirun hangs is no end_MPI_loop is called on the master')
