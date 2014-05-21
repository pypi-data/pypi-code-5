#!/usr/bin/env python

'''
Copyright (C) 2014 Janina Mass

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
'''

import sys
import getopt
import subprocess
import threading
import os
import shutil
import matplotlib
#don't use X:
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy
from distutils import spawn
#########################
# last update:
# Fr 16 Mai 2014 14:25:46 CEST
# [JMass]
#########################
global GAP
GAP = "-"
class Alignment(object):
    def __init__(self, id=None, fasta = None, members = []):
        self.id = id
        self.fasta = fasta
        self.members = []
        self.gapPos = []
        self.mismatchPos = []
        self.matchPos = []
        self.matchGapPos = []
        self.attachSequences()
        self.calcNumbers()

    def __repr__(self):
        ids = self.members
        return("Alignment:{},{}".format(self.id, ids))

    def __len__(self):
        try:
            return(len(self.members[0].sequence))
        except TypeError as e:
            sys.stderr.write(e)
            sys.stderr.write("attachSequences first")
            return(0)

    def getStats(self):
        res = ""
        res+="{},{},{},{},{},{}".format(len(self.matchPos),len(self.matchGapPos),len(self.mismatchPos),len(self)-len(self.gapPos),len(self.gapPos),len(self) )
        return(res)
    def attachSequences(self):
        fp = FastaParser()
        print("FASTA:", self.fasta)
        for f in fp.read_fasta(self.fasta):
          newSeq = Sequence(id = f[0], sequence = f[1])
          self.members.append(newSeq)

    def calcNumbers(self):
        for i in range(0, len(self)):
            curpos = [m.sequence[i] for m in self.members]
            if GAP in curpos:
                #dynamic penalty:
                tmp = "".join(curpos)
                gappyness = tmp.count(GAP)/float(len(self.members))
                half = len(self.members)/2.0
                if gappyness > half:
                    toPunish = [m for m in self.members if m.sequence[i]!=GAP]
                    for t in toPunish:
                        t._dynamicPenalty+=gappyness
                elif gappyness < half:
                    #punish gappers
                    toPunish = [m for m in self.members if m.sequence[i]==GAP]
                    for t in toPunish:
                        t._dynamicPenalty+=1-gappyness
                else:
                    pass
                #/dyn penalty
                self.gapPos.append(i)
                #sequences that cause gaps:
                gappers = [m for m in self.members if m.sequence[i] == GAP]
                for m in gappers:
                    m.gapsCaused.append(i)
                #unique gaps caused:
                if len(gappers) == 1:
                    m.uniqueGapsCaused.append(i)
                #insertions
                inserters = [m for m in self.members if m.sequence[i] != GAP]
                for m in inserters:
                    m.insertionsCaused.append(i)
                #unique insertions caused:
                if len(inserters) == 1:
                    m.uniqueInsertionsCaused.append(i)

            nongap = [c for c in curpos if c != GAP]
            cpset = set(curpos)
            if (len(cpset) >1 and GAP not in cpset):
                self.mismatchPos.append(i)
                for m in self.members:
                    m.mismatchShared.append(i)
            elif (len(cpset) == 1 and GAP not in cpset):
                self.matchPos.append(i)
                for m in self.members:
                    m.matchShared.append(i)
            elif (len(cpset)==2 and GAP in cpset and len(nongap)>2):
                self.matchGapPos.append(i)

    def showAlignment(self, numbers = False):
        res = []
        mmPos = []
        alignmentLength = len(self.members[0].sequence)
        for i in range(0, alignmentLength):
            curpos = [m.sequence[i] for m in self.members]
            if numbers:
                res.append(str(i)+" "+" ".join(curpos))
            else:
                res.append(" ".join(curpos))
        return("\n".join(res))

class Sequence():
    def __init__(self, id = "", sequence = None, isForeground = False):
        self.id = id
        self.sequence = sequence
        self.isForeground = isForeground
        self.insertionsCaused  = [] #positions
        self.uniqueInsertionsCaused = []
        self.gapsCaused = []#positions
        self.uniqueGapsCaused = []
        self.matchShared = []
        self.mismatchShared = []
        self._penalty = None
        # penalize by site:
        # > n/2 gaps (@site): penalyze inserts by gaps/n
        # < n/2 gaps (@site): penalyze gaps by inserts/n
        self._dynamicPenalty = 0
    def setForeground(self, bool = True):
        self.isForeground = bool

    def __repr__(self):
        return("Sequence: {}".format(self.id))
    @property
    def penalty(self, uniqueGapPenalty=10, uniqueInsertPenalty=10, gapPenalty = 1, insertPenalty =1 ):
        self.penalty =sum([ len(self.insertionsCaused)*insertPenalty, len(self.uniqueInsertionsCaused)*uniqueGapPenalty, len(self.gapsCaused)*gapPenalty, len(self.uniqueGapsCaused)*uniqueGapPenalty])
        return(self.penalty)
    def summary(self):
        s = ""
        s+=self.id
        s+="insertionsCaused:{},uniqueInsertionsCaused:{}, gapsCaused:{}, uniqueGapsCaused:{}, penalty:{}, dynPenalty:{}".format(len(self.insertionsCaused), len(self.uniqueInsertionsCaused), len(self.gapsCaused), len(self.uniqueGapsCaused), self.penalty, self._dynamicPenalty)
        return(s)

    def getCustomPenalty(self,gapPenalty, uniqueGapPenalty, insertionPenalty , uniqueInsertionPenalty, mismatchPenalty, matchReward):
            res = (len(self.gapsCaused)-len(self.uniqueGapsCaused))* gapPenalty\
            + len(self.uniqueGapsCaused)*uniqueGapPenalty\
            + (len(self.insertionsCaused)-len(self.uniqueInsertionsCaused)) * insertionPenalty\
            + len(self.uniqueInsertionsCaused) * uniqueInsertionPenalty\
            + len(self.mismatchShared)* mismatchPenalty\
            + len(self.matchShared) *matchReward
            return(res)
class FastaParser(object):
    def read_fasta(self, fasta, delim = None, asID = 0):
        """read from fasta fasta file 'fasta'
        and split sequence id at 'delim' (if set)\n
        example:\n
        >idpart1|idpart2\n
        ATGTGA\n
        and 'delim="|"' returns ("idpart1", "ATGTGA")
        """
        name = ""
        fasta = open(fasta, "r")
        while True:
            line = name or fasta.readline()
            if not line:
                break
            seq = []
            while True:
                name = fasta.readline()
                name = name.rstrip()
                if not name or name.startswith(">"):
                    break
                else:
                    seq.append(name)
            joinedSeq = "".join(seq)
            line = line[1:]
            if delim:
                line = line.split(delim)[asID]
            yield (line.rstrip(), joinedSeq.rstrip())
        fasta.close()

###########################################
#TODO documentation
def usage():
    print ("""
    ######################################
    # pysickle.py v0.1.1
    ######################################
    usage:
        pysickle.py -f multifasta alignment
    options:
        -f, --fasta=FILE    multifasta alignment (eg. "align.fas")
        OR
        -F, --fasta_dir=DIR directory with multifasta files (needs -s SUFFIX)
        -s, --suffix=SUFFIX will try to work with files that end with SUFFIX (eg ".fas")

        -a, --msa_tool=STR  supported: "mafft" [default:"mafft"]
        -i, --max_iterations=NUM    force stop after NUM iterations
        -n, --num_threads=NUM   max number of threads to be executed in parallel [default: 1]
        -m, --mode=MODE         set strategy to remove outlier sequences [default: "Sites"]
                                available modes (not case sensitive):
                                    "Sites", "Gaps", "uGaps","Insertions",
                                    "uInsertions","uInstertionsGaps", "custom"
        -l, --log       write logfile
        -h, --help      prints this

    only for mode "custom":
        -g, --gap_penalty=NUM        set gap penalty [default: 1.0]
        -G, --unique_gap_penalty=NUM set unique gap penalty [default: 10.0]
        -j, --insertion_penalty=NUM  set insertion penalty [default:1.0]
        -J, --unique_insertion_penalty=NUM set insertion penalty [default:1.0]
        -M, --mismatch_penalty=NUM   set mismatch penalty [default:1.0]
        -r, --match_reward=NUM       set match reward [default: -10.0]

    """)
    sys.exit(2)
############################################
def checkPath(progname):
    #TODO extend
    avail = ["mafft"]
    if progname.lower() not in avail:
        raise Exception("Program not supported. Only {} allowed.".format(",".join(avail)))
    else:
        path = spawn.find_executable(progname)
        print("Found {} in {}\n".format(progname, path))
    if not path:
        raise Exception("Could not find {} on your system! Exiting. Available options:{}\n".format(progname, ",".join(avail)))
        sys.exit(127)
def checkMode(mode):
    avail = ["sites", "gaps", "ugaps","insertions", "uinsertions", "uinsertionsgaps", "custom"]
    if mode not in avail:
        raise Exception("Mode {} not available. Only {} allowed\n".format(mode, ",".join(avail)))
class TooFewSequencesException(Exception):
    pass

def adjustDir(dirname, mode):
    if mode == "unisertionsgaps":
        abbr = "uig"
    else:
        abbr = mode[0:2]
    return(dirname+"_"+abbr)

def getSeqToKeep(alignment, mode, gap_penalty, unique_gap_penalty,  insertion_penalty, unique_insertion_penalty , mismatch_penalty, match_reward):
    if mode == "sites":
        toKeep = removeDynamicPenalty(alignment)
    elif mode == "gaps":
        toKeep = removeCustomPenalty(alignment, gapPenalty=1, uniqueGapPenalty=1, insertionPenalty =0, uniqueInsertionPenalty=0, mismatchPenalty=0, matchReward = 0)
        if not toKeep:
                removeDynamicPenalty(alignment)
    elif mode == "ugaps":
        toKeep = removeMaxUniqueGappers(alignment)
        if not toKeep:
            toKeep = removeDynamicPenalty(alignment)
        return(toKeep)
    elif mode == "insertions":
        toKeep = removeCustomPenalty(alignment, gapPenalty=0, uniqueGapPenalty=0, insertionPenalty =1, uniqueInsertionPenalty=1, mismatchPenalty=0, matchReward = 0)
        if not toKeep:
                removeDynamicPenalty(alignment)
    elif mode == "uinsertions":
        toKeep = removeMaxUniqueInserters(alignment)
        if not toKeep:
                removeDynamicPenalty(alignment)
    elif mode == "uinsertionsgaps":
        toKeep = removeMaxUniqueInsertsPlusGaps(alignment)
        if not toKeep:
                removeDynamicPenalty(alignment)
    elif mode == "custom":
        toKeep = removeCustomPenalty(alignment, gapPenalty=gap_penalty, uniqueGapPenalty=unique_gap_penalty, insertionPenalty =insertion_penalty, uniqueInsertionPenalty=unique_insertion_penalty, mismatchPenalty=mismatch_penalty, matchReward = match_reward)
        if not toKeep:
                removeDynamicPenalty(alignment)
    else:
        raise Exception("Sorry, sth went wrong at getSeqToKeep\n")
    return(toKeep)
def schoenify(fasta=None, max_iter=None, finaldir = None, tmpdir = None, msa_tool = None,mode = None, logging = None, gap_penalty= None, unique_gap_penalty =  None, insertion_penalty = None, unique_insertion_penalty = None, mismatch_penalty = None, match_reward = None ):
    if not fasta:
        raise Exception("Schoenify: Need alignment in fasta format.")
    else:
        arr = numpy.empty([1, 8], dtype='int32')
        iteration = 0

        fastabase = os.path.basename(fasta)
        statsout = finaldir+os.sep+fastabase+".info"
        tabout = finaldir + os.sep+fastabase+".csv"
        resout = finaldir +os.sep+fastabase+".res"
        if logging:
            info = open(statsout,"w")
        iterTab = []
        headerTab = ["matches", "matchesWithGaps","mismatches"," nogap", "gaps","length","iteration","numSeq"]
        alignmentstats = []
        newAlignment = Alignment(fasta = fasta)
        #sanity check
        if len(newAlignment.members) < 3:
            raise TooFewSequencesException("Need more than 2 sequences in alignment: {}\n".format(newAlignment.fasta))
        if not max_iter or  (max_iter > len(newAlignment.members)-2):
          max_iter = len(newAlignment.members)-2
        print("#max iterations:{}".format(str(max_iter)))
        while (iteration < max_iter):
            toKeep = getSeqToKeep(alignment = newAlignment, mode = mode, gap_penalty = gap_penalty, unique_gap_penalty = unique_gap_penalty,  insertion_penalty=insertion_penalty, unique_insertion_penalty = unique_insertion_penalty,  mismatch_penalty=mismatch_penalty, match_reward=match_reward)
            print("# iteration: {}/{} \n".format(iteration, max_iter))
            if len(toKeep) <2 :
                break
            res= ""
            for k in toKeep:
                seq ="".join([s for s in k.sequence if s !=GAP])
                res+=(">{}\n{}\n".format(k.id,seq))
            iterfile = tmpdir+os.sep+".".join(fastabase.split(".")[0:-1])+"."+str(iteration)

            with open(iterfile+".tmp",'w') as out:
                out.write(res)
            #log
            if logging:
                for m in newAlignment.members:
                    info.write(m.summary()+"\n")
            #log
            alignmentstats.append(newAlignment.getStats().split(","))
            iterTab.append((",".join(x for y in alignmentstats for x in y))+","+ str(iteration)+","+str(len(newAlignment.members)))
            alignmentstats = []
            iteration +=1
            if msa_tool == "mafft":
                proc = subprocess.Popen(["mafft","--auto", iterfile+".tmp"], stdout=open(iterfile+".out",'w'), bufsize=1)
                proc.communicate()
                newAlignment = Alignment(id = iterfile, fasta=iterfile+".out")
            #TODO extend
        if logging:
            info.close()
        with open(tabout, 'w') as taboutf:
            taboutf.write(",".join(headerTab))
            taboutf.write("\n")
            taboutf.write("\n".join(iterTab ))
        for i in iterTab:
            row = [int(j) for j in i.split(",")]
            arr = numpy.vstack((arr,numpy.array(row)))
        #delete row filled with zeros
        arr = numpy.delete(arr,0,0)
        ###########
        LOCK.acquire()
        plt.figure(1)
        plt.suptitle(fastabase, fontsize=12)
        ax = plt.subplot(3,1,1)
        for i,l in zip([0,1,2,3,4,5,6,7],['match','matchWithGap','mismatch','nogap','gap','length','iteration','numSeq' ]):
            if not i in [6,7]:
                plt.plot(arr[:,6], arr[:,i], label=l)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        ax= plt.subplot(3,1,2)
        plt.plot(arr[:,6], arr[:,7])
        ax.set_ylabel('count')
        ax.legend(["numSeq"],bbox_to_anchor=(1.05, 0.3), loc=2, borderaxespad=0.)
        ax= plt.subplot(3,1,3)
        scoring =(arr[:,5]-arr[:,4])*arr[:,7]
        try:
            maxIndex = scoring.argmax()
            with open(resout,'w')as resouth:
                resouth.write("# Ranking: {}\n".format(scoring[:].argsort()[::-1]))
                resouth.write("# Best set: {}".format(str(maxIndex)))
            plt.plot(arr[:,6],scoring)
            ax.legend(["(length-gaps)*numSeq"],bbox_to_anchor=(1.05, 0.3), loc=2, borderaxespad=0.)
            ax.set_xlabel('iteration')
            plt.savefig(finaldir+os.sep+fastabase+'.fun.png', bbox_inches='tight')
            plt.clf()
            finalfa = tmpdir+os.sep+".".join(fastabase.split(".")[0:-1])+"."+str(maxIndex)+".tmp"
            finalfabase = os.path.basename(finalfa)
            shutil.copy(finalfa,finaldir+os.sep+finalfabase)
        except ValueError as e:
            sys.stderr.write(str(e))
        finally:
            LOCK.release()

def removeMaxUniqueGappers(alignment):
    if not isinstance(alignment, Alignment):
        raise Exception("Must be of class Alignment")

    s = alignment.showAlignment(numbers = True)
    mxUniqueGaps = max([len(k.uniqueGapsCaused) for k in alignment.members])
    keepers = [k for k in alignment.members if len(k.uniqueGapsCaused) < mxUniqueGaps]
    return(keepers)

def removeMaxUniqueInserters(alignment):
    if not isinstance(alignment, Alignment):
        raise Exception("Must be of class Alignment")

    s = alignment.showAlignment(numbers = True)
    mxUniqueIns = max([len(k.uniqueInsertionsCaused) for k in alignment.members])
    keepers = [k for k in alignment.members if len(k.uniqueInsertionsCaused) < mxUniqueIns]
    return(keepers)

def removeMaxPenalty(alignment):
    if not isinstance(alignment, Alignment):
        raise Exception("Must be of class Alignment")

    s = alignment.showAlignment(numbers = True)
    mx = max([k.penalty for k in alignment.members])
    keepers = [k for k in alignment.members if k.penalty < mx]
    return(keepers)

def removeCustomPenalty(alignment, gapPenalty=None, uniqueGapPenalty=None, insertionPenalty=None, uniqueInsertionPenalty=None, mismatchPenalty=None, matchReward = None):
    if not isinstance(alignment, Alignment):
        raise Exception("Must be of class Alignment")
    mx = max([k.getCustomPenalty( gapPenalty =gapPenalty, uniqueGapPenalty=uniqueGapPenalty, insertionPenalty=insertionPenalty, uniqueInsertionPenalty=uniqueInsertionPenalty,mismatchPenalty=mismatchPenalty, matchReward = matchReward) for k in alignment.members])
    print("MAX",mx)
    print([k.getCustomPenalty(gapPenalty=gapPenalty, uniqueGapPenalty=uniqueGapPenalty, insertionPenalty=insertionPenalty,                           uniqueInsertionPenalty=uniqueInsertionPenalty ,mismatchPenalty=mismatchPenalty, matchReward = matchReward) for k in alignment.members ])
    keepers = [k for k in alignment.members if k.getCustomPenalty(gapPenalty=gapPenalty, uniqueGapPenalty=uniqueGapPenalty, insertionPenalty=insertionPenalty, uniqueInsertionPenalty=uniqueInsertionPenalty ,mismatchPenalty=mismatchPenalty, matchReward = matchReward) < mx]
    return(keepers)

def removeDynamicPenalty(alignment):
    if not isinstance(alignment, Alignment):
        raise Exception("Must be of class Alignment")

    s = alignment.showAlignment(numbers = True)
    mx = max([k._dynamicPenalty for k in alignment.members])
    keepers = [k for k in alignment.members if k._dynamicPenalty < mx]
    return(keepers)

def removeMaxUniqueInsertsPlusGaps(alignment):
    if not isinstance(alignment, Alignment):
        raise Exception("Must be of class Alignment")

    s = alignment.showAlignment(numbers = True)
    mxUniqueIns = max([len(k.uniqueInsertionsCaused)+len(k.uniqueGapsCaused) for k in alignment.members])
    keepers = [k for k in alignment.members if (len(k.uniqueInsertionsCaused)+len(k.uniqueGapsCaused)) < mxUniqueIns]
    return(keepers)
class SchoenifyThread(threading.Thread):
    def __init__(self,fasta, max_iter, finaldir,tmpdir, msa_tool, mode, logging, gap_penalty, unique_gap_penalty, insertion_penalty, unique_insertion_penalty, mismatch_penalty , match_reward):
        super(SchoenifyThread, self).__init__()
        self.fasta=fasta
        self.max_iter=max_iter
        self.finaldir=finaldir
        self.tmpdir = tmpdir
        self.msa_tool =msa_tool
        self.mode = mode
        self.logging = logging
    #custom
        self.gap_penalty = gap_penalty
        self.unique_gap_penalty = unique_gap_penalty
        self.insertion_penalty = insertion_penalty
        self.unique_insertion_penalty = unique_insertion_penalty
        self.mismatch_penalty = mismatch_penalty
        self.match_reward = match_reward

    def run(self):
        SEMAPHORE.acquire()
        try:
            schoenify(fasta=self.fasta, max_iter = self.max_iter, finaldir=self.finaldir,tmpdir = self.tmpdir, msa_tool=self.msa_tool, mode = self.mode, logging = self.logging, gap_penalty= self.gap_penalty, unique_gap_penalty =  self.unique_gap_penalty, insertion_penalty =  self.insertion_penalty, unique_insertion_penalty = self.unique_insertion_penalty, mismatch_penalty =  self.mismatch_penalty, match_reward = self.match_reward )
        except TooFewSequencesException as e:
            sys.stderr.write(str(e))
        SEMAPHORE.release()
def getFastaList(dir=None, suffix=None):
    for f in os.listdir(dir):
        if f.endswith(suffix):
            yield(os.sep.join([dir,f]))

def main():
  fastalist  = []
  fastadir = None
  suffix= None
  max_iter = None
  finaldir = None
  tmpdir = None
  msa_tool = "mafft"
  num_threads = 1
  mode = "sites"
  logging = False

  #custom penalty:
  gap_penalty = 1.0
  unique_gap_penalty = 10.0
  insertion_penalty = 1.0
  unique_insertion_penalty = 1.0
  mismatch_penalty = 1.0
  match_reward = -10.0

  try:
      opts, args = getopt.gnu_getopt(sys.argv[1:], "f:F:s:i:a:n:m:g:G:j:J:M:r:lh", ["fasta=","fasta_dir=","suffix=","max_iteration=","msa_tool=",
          "num_threads=","mode=","gap_penalty", "unique_gap_penalty", "insertion_penalty=", "unique_insertion_penalty=", "mismatch_penalty=",
          "match_reward=", "log","help"])
  except getopt.GetoptError as err:
        print (str(err))
        usage()
  for o, a in opts:
        if o in ("-f", "--fasta"):
            fastalist = a.split(",")
            statsout = fastalist[0]+".info"
            tabout = fastalist[0]+".csv"
            finaldir = os.path.dirname(fastalist[0])+"ps_out"
            tmpdir = os.path.dirname(fastalist[0])+"ps_tmp"
        elif o in ("-h","--help"):
            usage()
        elif o in ("-n", "--num_threads"):
            num_threads = int(a)
        elif o in ("-F","--fasta_dir"):
            fastadir = a
            finaldir = fastadir+os.sep+"ps_out"
            tmpdir = fastadir+os.sep+"ps_tmp"
        elif o in ("-s", "--suffix"):
            suffix = a
        elif o in ("-i", "--max_iteration"):
            max_iter = int(a)
        elif o in ("-a", "--msa_tool"):
            msa_tool = a.lower()
        elif o in ("-m", "--mode"):
            mode = a.lower()
        elif o in ("-l", "--log"):
            logging = True

    #only for mode "custom":
        elif o in ("-g", "--gap_penalty"):
            gap_penalty = float(a)
        elif o in ("-G","--unique_gap_penalty"):
            unique_gap_penalty = float(a)
        elif o in ("-j", "--insertion_penalty"):
            insertion_penalty = float(a)
        elif o in ("-J", "--unique_insertion_penalty"):
            unique_insertion_penalty = float(a)
        elif o in ("-M", "--mismatch_penalty"):
            mismatch_penalty = float(a)
        elif o in ("-r", "--match_reward"):
            match_reward = float(a)



        else:
            assert False, "unhandled option"
  if not fastalist and not (fastadir and suffix):
      usage()
  else:
      checkPath(progname = msa_tool)
      checkMode(mode=mode)
      finaldir = adjustDir(finaldir, mode)
      tmpdir = adjustDir(tmpdir, mode)
      global SEMAPHORE
      SEMAPHORE=threading.BoundedSemaphore(num_threads)
      if not os.path.exists(finaldir):
          os.mkdir(finaldir)

      if not os.path.exists(tmpdir):
          os.mkdir(tmpdir)
      if fastadir:
          print(suffix)
          for f in getFastaList(fastadir, suffix):
              print(f)
              fastalist.append(f)
      for fasta in fastalist:
          SchoenifyThread(fasta, max_iter,finaldir,tmpdir, msa_tool, mode, logging, gap_penalty, unique_gap_penalty, insertion_penalty, unique_insertion_penalty, mismatch_penalty , match_reward).start()
#############################################
LOCK = threading.Lock()
SEMAPHORE = threading.BoundedSemaphore()
##########
if __name__ == "__main__":
    main()
