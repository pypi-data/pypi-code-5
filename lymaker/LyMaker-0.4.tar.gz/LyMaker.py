'''
LyMaker
@author: Acoustic E
'''
import sys, getopt,os
from LyMaker import LyMk,xmlreader


VERSION = "0.4"

def usage():
    print "LyMaker (Version %s)" % VERSION
    print "usage: LyMaker.py [options]"
    print "-h print help"
    print "-f xml filename (without extension)"
    print "-t create template xml file"
    print "-s show scale and valid chords"

#
# MAIN
# isn't it?
#
#
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htf:s:", ["help","template","file=","show="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    automatic = False
    template = False
    filename = "default"
    key = "c major"
    show = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            filename = a
            automatic = True
        elif o in ("-s", "--show"):
            key = a
            show = True
        elif o in ("-t", "--template"):
            template = True
    mm = LyMk.LyMaker(filename)
    if automatic:
        r = xmlreader.xmlreader(filename+ ".xml")
        r.importXML()
        text = mm.process(r)
        outf = None
        try:
            outf = open(filename + ".ly","w")
        except:
            print "Cannot open %s" % (filename + ".ly")
        if outf:    
            outf.write(text)
            outf.flush()
            outf.close
    elif template:
        outf = None
        try:
            outf = open("template.xml","w")
        except:
            print "Cannot open %s" % ("template.ly")
        if outf:    
            outf.write(mm.template())
            outf.flush()
            outf.close

    if show:
        print mm.showChords(key)
        
    sys.exit()

if __name__ == '__main__':
    main()

