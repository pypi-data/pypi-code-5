#!/usr/bin/python

import threading
import time
import os, sys

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name + " with ID = " + str(self.threadID)

def createThreads(Browsers_args):
    # Creating new threads
    Browsers = Browsers_args
    threads_temp = []
    ThreadID=1
    for browser in Browsers:
        thread = myThread(ThreadID, "Thread_"+str(browser))
        # Add threads to thread list
        threads_temp.append(thread)
        ThreadID+=1
    return threads_temp

# Start running Threads
def startThreads(threads):
    for thread_t in threads:    
        thread_t.start()
    time.sleep(2)
    return 1

#Launch single browser for all threads  
def LaunchBrowserOnAll(threads, browser):
    for t in threads:
        browser_temp = browser
        URL = "http://amazon.com"
        return_value = OpenBrowser(browser_temp, URL, t.name)
        if (return_value.find("launched") == 0):
            plog = "provided browser is " + browser + " launching in thread " + t.name
            print "\n" + plog
        else:
            print "\n unable to open browser " + browser + "for thread " + t.name
    return 1

#Launch single browser on single thread
def LaunchBrowserOnOne(threads, thread_name, browser_call):
    #URL = "http://www.amazon.com"
    print "\n In updateOneThread for " + thread_name
    threads_temp = threads
    thread_name_temp = thread_name
    browser = browser_call
    URL = "http://www.cloudplayer.com"
    for t in threads_temp:
        if t.name == thread_name_temp:
            return_value = OpenBrowser(browser, URL, thread_name_temp)
            break
    if (return_value.find("launched") == 0):
        plog = "provided browser is " + browser + " launching in thread " + thread_name_temp
        print "\n" + plog
    else:
        print "\n unable to open browser " + browser + "for thread " + thread_name_temp

#OpenBrowser
def OpenBrowser(browser, URL, thread_name):
    BrowserList = ["chrome", "firefox", "iexplore"]
    cmd = "start " + browser + " " + URL
    if (browser in BrowserList):
        os.system(cmd)
        status = "launched for " + thread_name
    else:
        status = "failed to launch for " + thread_name + " Browser not in the List"
    return status

'''Terminating threads'''
def TerminateThreads(threads):
    for t in threads:
        t.join()
    print "Exiting Main Thread"
         
'''
Defining browser call. The browser names are fixed.
"iexplore" for IE any version
"chrome" for Google chrome
"firefox" for FF any version
"safari" for Safari Browser
'''
Browsers = ["chrome", "firefox"]

return_value = 0
browser_call = "iexplore"

threads = createThreads(Browsers)

return_value = startThreads(threads)

if return_value!= 1:
    print "exiting"
    sys.exit


#LaunchBrowserOnAll(threads, "iexplore")
#LaunchBrowserOnOne(threads, "Thread_chrome", "iexplore")

