import batchOpenMPI

batchOpenMPI.begin_MPI_loop(print_launch_messages=False)

print('First call should fail:')
batchOpenMPI.showStats()
print('Second call after end_MPI_loop should work')
batchOpenMPI.end_MPI_loop(print_stats=True)
