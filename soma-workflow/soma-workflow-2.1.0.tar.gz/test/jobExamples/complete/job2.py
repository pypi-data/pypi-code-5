import sys
import time

if len(sys.argv)  < 4 or len(sys.argv) > 5:
  sys.stdout.write("The program takes 3 or 4 arguments! \n")
  sys.exit()

sys.stdout.write("Job2: What should we add to the end of the output file ?")
comment = sys.stdin.readline()
sys.stdout.write("Job2: added to the end of the output file : " + comment + "\n")


filePathIn1 = sys.argv[1]
filePathIn2 = sys.argv[2]
filePathOut = sys.argv[3]

timeToSleep=0
if len(sys.argv) == 5:
  timeToSleep = int(sys.argv[4])
for i in range(1,timeToSleep+1):
  time.sleep(1)
  sys.stdout.write(repr(i)+" ")
  sys.stdout.flush()
sys.stdout.write("\n")

#sys.stdout.write("Input file 1 = " + filePathIn1 + "\n")
#sys.stdout.write("Input file 2 = " + filePathIn2 + "\n")
#sys.stdout.write("Output file = " + filePathOut + "\n")

fileIn1 = open(filePathIn1)
fileOut = open(filePathOut, "w")

print >> fileOut, "2****************job2**************"
line = fileIn1.readline()
while line:
  print >> fileOut, "2 " + line,
  line = fileIn1.readline()
  


fileIn2 = open(filePathIn2)
nblines = len(fileIn2.readlines())
print >> fileOut, "2 "
print >> fileOut, "2  # lines:" + repr(nblines),

print >> fileOut, "2 "
print >> fileOut, "2 job2: stdin comment:"
print >> fileOut, "2 " + comment,
print >> fileOut, "2******************************************************"

