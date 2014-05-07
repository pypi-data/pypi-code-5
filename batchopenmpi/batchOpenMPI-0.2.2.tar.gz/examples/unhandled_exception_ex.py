import sys, batchOpenMPI, apport_python_hook

batchOpenMPI.begin_MPI_loop()

raise RuntimeError, "mpirun should hang not hang and exit"

batchOpenMPI.end_MPI_loop() #release workers
