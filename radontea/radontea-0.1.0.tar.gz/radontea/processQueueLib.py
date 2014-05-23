from __future__ import division
from __future__ import print_function

import os
import time
import multiprocessing as mp


class ProcessPool(object):
    def __init__(self, target, argsList, maxNumOfRunningJobs, lock = None, quiet = True, const_args = (), updateInterval_sec = 1, print_status = True, additional_status_message = ""):
        self._target = target
        self._argsList = argsList
        if maxNumOfRunningJobs <= 0:
            nCPU = mp.cpu_count()
            self._maxNumOfRunningJobs = nCPU + maxNumOfRunningJobs
            
            if not quiet:
                print("non positive maxNumOfRunningJobs found (maxRun {})".format(maxNumOfRunningJobs))
                print("interpret them as number of unused cores")
                print(" numCores {}".format(nCPU))
            #have at least one job running
            if self._maxNumOfRunningJobs < 1:
                print(" resulting cores to use is non positive ({})".format(self._maxNumOfRunningJobs))
                print(" so maxRun will be set to 1")
                self._maxNumOfRunningJobs = 1
                
        else:
            self._maxNumOfRunningJobs = maxNumOfRunningJobs

        
        if not quiet:
            print("maxRun {}".format(self._maxNumOfRunningJobs))
            
        self._quiet = quiet
        self._const_args = const_args
        self._totalNumberOfJobs = len(self._argsList)
        self._jobsDone = mp.Value('i', 0)
        self._jobsRunning = mp.Value('i', 0)
        self._jobList = []
        self._lock = lock
        self._manager = mp.Manager()
        self._updateInterval_sec = updateInterval_sec
        self._print_status = print_status
        self._additional_status_message = additional_status_message
    
        for args in self._argsList[::-1]:
            self._jobList.append(mp.Process(target = self.__targteWrapper, args = (self._jobsDone, self._jobsRunning, self._target, self._lock) + self._const_args + args))

    def __targteWrapper(self, _jobsDone, _jobsRunning, target, *args):
        if not self._quiet:
            print("start job PID {}".format( os.getpid()))
            
        apply(target, args)
        _jobsDone.value += 1
        _jobsRunning.value -= 1
        
        if not self._quiet:
            print("finished job {}".format(os.getpid()))
# print("done/total {}/{} -- run/maxRun {}/{}".format(self._jobsDone.value, self._totalNumberOfJobs, self._jobsRunning.value, self._maxNumOfRunningJobs))
        if self._print_status:
            print("finished job {}/{} -- {}".format(self._jobsDone.value, self._totalNumberOfJobs, self._additional_status_message))


    def __triggerNewJobs(self):
        while (self._jobsRunning.value < self._maxNumOfRunningJobs) and (len(self._jobList) > 0):
            job = self._jobList.pop()
            if not self._quiet:
                print("trigger job #{}".format(self._totalNumberOfJobs - len(self._jobList)))
            job.start()
            self._jobsRunning.value += 1
        

    def run(self):
        stop = False
        while not stop:
            self.__triggerNewJobs()
            
            time.sleep(self._updateInterval_sec)
            stop = (self._jobsDone.value == self._totalNumberOfJobs)

        print("FINISHED!")


def test():
    def prcs(l, arg):
        l.acquire()
        t = 1
        print(" |{}| I got started with arg {}".format(os.getpid(), arg))
        print(" |{}| I will sleep for {}s ...".format(os.getpid(),t))
        time.sleep(t)
        print(" |{}| I woke up after sleeping for {}s!".format(os.getpid(),t))
        print(" |{}| I terminate now! Godbye!".format(os.getpid()))
        l.release()
    
    argsList = [(i, ) for i in range(1,10)]
    
    pool = ProcessPool(target=prcs, argsList=argsList, maxNumOfRunningJobs=0, lock = mp.Lock(), quiet=False, const_args=())
    pool.run()
    
if __name__ == "__main__":
    test()
