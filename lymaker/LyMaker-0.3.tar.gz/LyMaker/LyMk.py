'''
LyMaker lib
@author: Acoustic E
'''
import sys,os,random
import xmlreader,ScaleUtil
from HarmonyMaker import HarmonyMaker
from GrooveMaker import GrooveMaker
from DrumMaker import DrumMaker
from Utils import Utils

VERSION = "0.3"
instances = [ 'I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XiV','XV','XVI','XVII','XVIII','XIX','XX','XXI','XXII','XXIII','XXIV','XXV','XXVI','XXVII','XXVIII','XXIX','XXX','XXXI','XXXII','XXXIII','XXXIV','XXXV','XXXVI','XXXVII','XXXVIII','XXXIX','XXXX']


#
#
# LYMAKER
# main class
#
#

class LyMaker(object):

    notepool = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
    notepool_alt = ['c','des','d','es','e','f','ges','g','as','a','bes','b']

    def __init__(self,name,quarters=4,beats=[],onbeat =False):
        self.chord = []
        self.chord.append("c")
        self.chord.append("e")
        self.chord.append("g")
        self.chord2 = []
        self.chord2.append("c")
        self.chord2.append("e")
        self.chord2.append("g")
        self.denominator = 4
        self.quarters = quarters
        self.eighths = quarters*2
        if not len(beats):
            self.downbeats = self._downbeats()
        else:
            self.downbeats = beats
        self.onbeat = onbeat # true = bass and drums only on pulse beats
        self.meter = "moderato"
        self.tempo = 100
        self.key = "c \\major"
        self.BbKey = "d \\major"
        self.name = name
        self.modal = False # true = do not use chord root of tonic chord in bass
        self.lasttempo = 0

    def getBeats(self):
        return self.downbeats

    def getQuarters(self):
        return self.quarters

    def getChord(self):
        return self.chord

    def getChord2(self):
        return self.chord2

    def isModal(self):
        return self.modal
    
    def setKey(self,key):
        key =key.strip()
        idx = key.rfind(" ")
        k = ""
        if idx > -1:
            k = key[:idx+1]
            k += "\\"
            k += key[idx+1:]
            if key[idx+1:] == "major" or key[idx+1:] == "minor":
                self.modal = False
            else:
                self.modal = True    
        self.key = k    
        try:
            idx2 = self.notepool.index(key[:idx])
        except:
            idx2 = self.notepool_alt.index(key[:idx])
        if idx2+2 < len(self.notepool)-1:
            k = self.notepool[idx2+2]
        else:
            idx2 = idx2+2  - len(self.notepool)
            k = self.notepool[idx2]
        k += " \\"
        k += key[idx+1:]
        self.BbKey = k
      
    # set numerator for x/4 time pieces
    def setQuarters(self,quarters):
        if quarters > 1 and quarters < 10:
            self.quarters = quarters
            self.denominator = 4
            self.setDownbeats(self._downbeats())
            self.eighths = quarters * 2
        else:
            print "%d is not a valid value for quarters" % quarters

    # set numerator for x/8 time pieces
    def setEighths(self,eighths):
        if eighths > 2 and eighths < 13:
            self.eighths = eighths
            self.denominator = 8
            self.setDownbeats(self._downbeats())
        else:
            print "%d is not a valid value for eighths" % eighths

    def setOnbeat(self,onbeat):
        self.onbeat = onbeat

    def showChords(self,key):
        sc = ScaleUtil.ScaleUtil()
        sc.setKey(key)
        return sc.getChords()
        

    def setTempo(self,tempo):
        self.tempo = tempo
        self._tempo2meter()

    def _tempo2meter(self):
        self.meter = "moderato"
        if self.tempo < 20:
            self.meter = "Larghissimo"
        elif self.tempo < 40:
            self.meter = "Grave"
        elif self.tempo < 45:
            self.meter = "Lento"
        elif self.tempo < 50:
            self.meter = "Largo"
        elif self.tempo < 55:
            self.meter = "Larghetto"
        elif self.tempo < 65:
            self.meter = "Adagio"
        elif self.tempo < 70:
            self.meter = "Adagietto"
        elif self.tempo < 73:
            self.meter = "Andante moderato"
        elif self.tempo < 78:
            self.meter = "Andante"
        elif self.tempo < 84:
            self.meter = "Andantino"
        elif self.tempo < 86:
            self.meter = "Marcia moderato"
        elif self.tempo < 98:
            self.meter = "Moderato"
        elif self.tempo < 110:
            self.meter = "Allegretto"
        elif self.tempo < 133:
            self.meter = "Allegro"
        elif self.tempo < 141:
            self.meter = "Vivace"
        elif self.tempo < 151:
            self.meter = "Vivacissimo"
        elif self.tempo < 168:
            self.meter = "Allegrissimo"
        elif self.tempo < 178:
            self.meter = "Presto"
        else:
            self.meter = "Prestissimo"

    # asXml is normally called without parameters
    # parameters are only for unit test
    def asXml(self,bassmode = 0,drummode = 0,odd = False,harmonymode = 0):
        template_chords =  "c,e,g|c,e,g|a,c,e,g|a,c,e,g;c,e,g|c,e,g|f,a,c|g,b,d|c,e,g,b"
        text = "<LyMk>\n"
        text += "<version>%s</version>\n" % VERSION
        text += "<song>\n<name>%s</name>\n" % self.name
        numerator = 4
        if self.denominator == 4:
            numerator = self.quarters
        else:
            numerator = self.eighths
        text += "<time>%d,%d</time>\n" % (numerator,self.denominator)
        tmp = self.key.replace('\\','')
        text += "<key>%s</key>\n" % tmp
        text += "<tempo>%d</tempo>\n" % self.tempo
        text += "<structure>ABAB</structure>\n"
        beats = self.getDownbeats()
        text += "<downbeats>"
        beat = ""
        for b in beats:
           if len(beat) > 0 :
               beat += ","
           beat += "%d" % b
        text += beat   
        text += "</downbeats>\n"
        on = 0
        if self.onbeat == True:
            on = 1
        text += "<onbeat>%d</onbeat>\n" % on
        text += "<part>\n"
        text += "<partname>Verse</partname>\n"
        text += "<ptempo>%d</ptempo>\n" % self.tempo
        text += "<progressions>"
        if odd == True:
            text += "c,e,g|c,e,g|a,c,e|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c,e"
        elif bassmode > 0 or drummode > 0: # for testing
            text += "c,e,g|c,e,g;a,c,e,g;c,e,g|a,c,e,d|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c|f,a,c,e"
        else:
            text += template_chords
        text += "</progressions>\n"
        text += "<groove>%d</groove>\n" % bassmode
        text += "<drummode>%d</drummode>\n" % drummode
        text += "<harmony>%d</harmony>\n" % harmonymode
        text += "</part>\n"
        text += "<part>\n"
        text += "<partname>Chorus</partname>\n"
        text += "<ptempo>%d</ptempo>\n" % self.tempo
        text += "<progressions>"
        if bassmode > 0 or drummode > 0:
            text += "c,e,g|c,e,g|a,c,e|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c|f,a,c,g"
        else:
            text += template_chords
        text += "</progressions>\n"
        text += "<groove>%d</groove>\n" % bassmode
        text += "<drummode>%d</drummode>\n" % drummode
        text += "<harmony>%d</harmony>\n" % harmonymode
        text += "</part>\n"
        text += "</song>\n"
        text += "</LyMk>"
        return text


    def _downbeats(self):
        beats = [0,32]
        if self.denominator == 4:
            if self.quarters < 4:
                beats = [0] # simple duple or triple
            elif self.quarters < 6:
                beats = [0,32] # 2-2 or 2-3
            elif self.quarters == 6:
                beats = [0,48] # 3-3 compound duple
            elif self.quarters == 7:
                beats = [0,32,64] # 2-2-3 compound triple
            elif self.quarters == 8:
                beats = [0,32,64,96] # 2-2-2-2 compound quadruple
            elif self.quarters == 9:
                beats = [0,48,96] # 3-3-3 compound triple
        elif self.denominator == 8:
            if self.eighths < 4:
                beats = [0]
            elif self.eighths == 4:
                beats = [0,16]
            elif self.eighths == 5:
                beats = [0,24]
            elif self.eighths == 6:
                beats = [0,24]
            elif self.eighths < 9:
                beats = [0,24]
            elif self.eighths == 9:
                beats = [0,24,48]
            elif self.eighths < 12:
                beats = [0,24,48]
            elif self.eighths == 12:
                beats = [0,24,48,72]
                
        return beats

    def setDownbeats(self,beats):
        if len(beats)  == 0:
            self.downbeats = self._downbeats()
        else:
            self.downbeats = beats

    def getDownbeats(self):
        beats = []
        for n in self.downbeats:
            b = 0
            if n == 0:
                b = 1
            else:
                if self.denominator == 4:
                    b = int(n / 16)
                elif self.denominator == 8:
                    b = int(n / 8)
                b += 1
            beats.append(b)
        return beats    


    def _getRiff(self,chord):
        result = ""
        mysum = 0
        eighths = self.eighths * 8
        while mysum < eighths:
            print_dur =""
            dur = 16
            note = ""
            play = 1
            if mysum in self.downbeats:
                slot = random.randint(0,len(chord)-1)
                note = chord[slot]
                dur = 16
            else:
                slot = random.randint(0,len(chord)-1)
                note = chord[slot]
                play = random.randint(0,1)
                if mysum+16 > eighths:
                    slot = 0
                else:    
                    slot = random.randint(0,1)
                if slot:
                    dur = 16
                else:
                    dur = 8    
            print_dur = Utils.findDuration(dur)
            if play == 0:
                note = "r"
            result += note
            result += print_dur
            result += " " 
            mysum += dur    
        return result


    def _addIntro(self):
        text = '\\version "2.12.3"\n\\header {\n title = "%s"\n  composer = "LyMaker"\n  meter = "%s"\n}\n\n' % (self.name,self.meter)
        if self.denominator == 4:
            text += 'global = { \\time %d/4 }\nKey = { \\key %s }\n\n' % (self.quarters,self.key)
        else:    
            text += 'global = { \\time %d/8 }\nKey = { \\key %s }\n\n' % (self.eighths,self.key)
        return text

    def _addHarmonies(self,name,chords):
        text = '\n%s = {\n' % name
        hm = HarmonyMaker(self.eighths,self.downbeats,self.denominator)
        for bar in chords:
            text += hm.makeChord(bar,False)
            text += ' |\n '
        text += "\n}\n"
        return text

    def _addStructure(self,name):
        return "\\%s\n    " % (name)

    def _addScorePart(self,instanceCount,harmonies):
            text = harmonies
            text += "Trumpet = \\transpose c c' {\n\\clef treble\n\\global\n\\Key \n" 
            i = 0
            while i < instanceCount:
                text += "\\Trumpet%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Right = \\transpose c c' {\n\\clef treble\n\\global\n\\Key\n" 
            i = 0
            while i < instanceCount:
                text += "\\Right%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Left = {\n\\clef bass\n\\global\n\\Key\n"
            i = 0
            while i < instanceCount:
                text += "\\Left%s   " % instances[i]
                i +=1
            text += "\n}\n"    
            text += 'Bass = \\transpose c c, {\n\\clef "bass_8"\n\\global\n\\Key\n'
            i = 0
            while i < instanceCount:
                text += "\\Bass%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Drums = \\drummode {\n\\global\n\\voiceOne\n"
            i = 0
            while i < instanceCount:
                text += "\\Drums%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Cymbals = \\drummode {\n\\global\n\\voiceTwo\n"
            i = 0
            while i < instanceCount:
                text += "\\Cymbals%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "SynthR = \\transpose c c'' {\n\\clef treble\n\\global\n\\Key\n"
            i = 0
            while i < instanceCount:
                text += "\\SynthR%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "SynthL = {\n\\clef bass\n\\global\n\\Key\n"
            i = 0
            while i < instanceCount:
                text += "\\SynthL%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "TenorSax = \\transpose c c' {\n\\clef treble\n\\global\n\\key %s\n\\transposition bes\n" % self.BbKey
            i = 0
            while i < instanceCount:
                text += "\\TenorSax%s   " % instances[i]
                i += 1
            text += "\n}\n"    


            text += '\npiano = {\n<<\n\\set PianoStaff.instrumentName = #"Piano"\n\\set PianoStaff.midiInstrument = #"acoustic grand"'
            text += '\n\\new Staff = "upper" \\Right\n\\new Staff = "lower" \\Left\n>>\n}\n'
            text += '\nsynth = {\n<<\n\\set PianoStaff.instrumentName = #"Synthesizer"\n\\set PianoStaff.midiInstrument = #"lead 1 (square)"'
            text += '\n\\new Staff = "upper" \\SynthR\n\\new Staff = "lower" \\SynthL\n>>\n}\n'
            text += '\ntrumpet = {\n\\set Staff.instrumentName = #"Trumpet in C"\n\\set Staff.midiInstrument = #"trumpet"\n<<\n\\Trumpet\n>>\n}\n'            
            text += '\ntenorSax = {\n\\set Staff.instrumentName = #"Tenor Sax"\n\\set Staff.midiInstrument = #"tenor sax"\n<<\n\\TenorSax\n>>\n}\n'
            text += '\nbass = {\n\\set Staff.instrumentName = #"Bass"\n\\set Staff.midiInstrument = #"acoustic bass"\n<<\n\\Bass\n>>\n}\n'
            text += '\ndrumContents = {\n<<\n\\set DrumStaff.instrumentName = #"Drums"\n'
            text += '\\new DrumVoice \\Cymbals\n\\new DrumVoice \\Drums\n>>\n}\n'
            text += '\n\\score {\n <<\n  \\new StaffGroup\n  <<\n   \\new PianoStaff = "piano" \\piano\n'
            text += '   \\new PianoStaff = "synthesizer" \\synth\n'
            text += '   \\new Staff = "trumpet" \\trumpet\n'
            text += '   \\new Staff = "tenorSax" \\tenorSax\n'
            text += '   \\new Staff = "bass" \\bass\n'
            text += '   \\new ChordNames {\n      \\harmonies\n   }\n'
            text += '   \\new DrumStaff \drumContents\n  >>\n >>\n'
            text += ' \\layout { }\n \\midi {\n'
            text += '   \context {\n  \\Score\n   tempoWholesPerMinute = #(ly:make-moment %d 4)\n    }\n }\n}\n' % self.tempo
            return text

    def _makeSong(self,chords):
        result = self._addIntro()
        riff = ""
        riff2 = ""
        if len(chords) > 0:
            riff = self._getRiff(chords[0][0])
        if len (chords) > 1:    
            riff2 = self._getRiff(chords[1][0])

        result += "Riff = {\n %s |\n  %s |\n}\n\n" %(riff,riff2)
        result += "\n\n"
        riff = ""
        riff2 = ""
        if len(chords) > 0:
            riff = self._getRiff(chords[0][0])
        if len (chords) > 1:    
            riff2 = self._getRiff(chords[1][0])

        result += "RiffII = {\n %s |\n  %s |\n}\n\n" %(riff,riff2)
        result += "\n\n"

        dm = DrumMaker(self.eighths,self.downbeats,self.onbeat,5,self.denominator)
        result += dm.getPattern()
        result += "\n\n"
        if self.quarters == 4 and self.denominator == 4:
            result += dm.getDrumRoll()
            result += "\n\n"
        return result

    def _makePart(self,name,chords,instance,bassmode,drummode,tempo,harmonymode):
        result = ""    
        key,type = self.key.split(" ")
        hm = HarmonyMaker(self.eighths,self.downbeats,self.denominator,harmonymode)
        gm = GrooveMaker(self.eighths,key,self.downbeats,self.onbeat,bassmode,self.isModal(),self.denominator)
        dm = DrumMaker(self.eighths,self.downbeats,self.onbeat,drummode,self.denominator)
        part = "% "
        part += "Part %s\n" % name
        if tempo == 0:
            tempo = self.tempo
        if tempo != self.lasttempo:
            part += "\\tempo 4 = %d\n" % tempo
            self.lasttempo = tempo
        
        resultT = "Trumpet%s =  {\n" % instance
        resultT += part
        resultT += "% range from fis, to c''\n"
        resultS = "TenorSax%s =  {\n" % instance
        resultS += part
        resultS += "% range from c to f''\n"
        resultM = "Right%s =  {\n" % instance
        resultM += part
        resultH = "Left%s = {\n" % instance
        resultH += part
        resultB = 'Bass%s = {\n' % instance 
        resultB += part
        resultD = "Drums%s = \\drummode {\n" % instance
        resultD += part
        resultC = "Cymbals%s = \\drummode {\n" % instance
        resultC += part
        resultSR = "SynthR%s =  {\n" % instance
        resultSR += part
        resultSL = "SynthL%s = {\n" % instance
        resultSL += part
        bars = 1
        length = len(chords)
        for bar in chords:
                barstr = "bar %d\n" % bars
                resultT += "% " + barstr
                resultT += " | \n"
                resultS += "% " + barstr                
                resultS += " | \n"
                resultSR += "% " + barstr
                resultSR += " | \n"
                resultSL += "% " + barstr
                resultSL += " | \n"
                resultM += "% " + barstr
                if bars % 2 and bars < length:
                    resultM += "\Riff\n"
                elif bars % 2 and bars == length:
                    resultM += hm.getEmptyBar()
                else:
                    resultM + ""

                resultM += "\n"
                resultH += "% " + barstr                
                resultH += hm.makeChord(bar,True)    
                resultH += " | \n"
                if bassmode != 5:
                    resultB += "% " + barstr                
                    resultB += gm.process(bar)
                    resultB += " | \n"
                else:    
                    resultB += "% " + barstr
                    if bars % 2 and bars < length:
                        resultB += "\RiffII\n"
                    elif bars % 2 and bars == length:
                        resultB += hm.getEmptyBar()
                    else:
                        resultM + ""
                    resultB += "\n"

                resultD += "% " + barstr                
                resultD += dm.process()
                resultD += " | \n"
                resultC += "% " + barstr                
                resultC += dm.getCymbals()
                resultC += " | \n"
                bars +=1
        resultT += "}"                
        resultS += "}"                
        resultSR += "}"                
        resultSL += "}"                
        resultM += "}"
        resultH += "}"
        resultB += "}"
        resultD += "}"
        resultC += "}"
        result += resultT
        result += "\n\n"
        result += resultS
        result += "\n\n"
        result += resultSR
        result += "\n\n"
        result += resultSL
        result += "\n\n"
        result += resultM
        result += "\n\n"
        result += resultH
        result += "\n\n"
        result += resultB
        result += "\n\n"
        result += resultD
        result += "\n\n"
        result += resultC
        result += "\n\n"
        return result

    def _makeScore(self,instances,harmonies):
        result = ""
        result += self._addScorePart(instances,harmonies)
        return result

    # main routine
    # takes an xmlreader object as input
    # and generates lilypond code.
    def process(self,r):
        text = ""
        count = r.getPartCount()
        self.setTempo(r.getTempo())
        self.setKey(r.getKey())
        self.setQuarters(r.getQuarters())
        if r.getEighths() > 0:
            self.setEighths(r.getEighths())
        self.setDownbeats(r.getDownbeats())
        self.setOnbeat(r.isOnbeat())
        harmonies = ""
        callstring =  '\nharmonies = {\n    '
        i = 0
        while i < count:
            part = r.getPart(i)
            chords = part.progressions
            if i == 0:
                text = self._makeSong(chords)        
            i += 1
            harmonies += self._addHarmonies(part.name,chords)

        structure = r.getStructure()
        i = 0
        for s in structure:
            if i >= len(instances):
                print "more than %d actual parts, can't proceed" % i
                break
            if s < "A" or s > "Z" :
                print "invalid structure string, parts start with uppercase A and run on alphabetically..."
                break
            offset = ord(s) - ord('A')
            part = None
            part = r.getPart(offset)
            chords = part.progressions
            bassmode = part.groove
            drummode = part.drummode
            harmonymode = part.harmony
            tempo = part.tempo
            instance = instances[i]
            i += 1
            text += self._makePart(part.name,chords,instance,bassmode,drummode,tempo,harmonymode)
            callstring += self._addStructure(part.name)

        callstring += '}\n'
        harmonies += callstring
        text += self._makeScore(i,harmonies)
        return text


