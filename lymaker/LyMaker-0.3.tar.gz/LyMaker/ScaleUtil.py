import sys, getopt,os
from copy import deepcopy

note_names = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b'] 
note_names2 = ['c','des','d','es','e','f','ges','g','as','a','bes','b'] 


class Scale(object):
    
    major = [0,2,4,5,7,9,11]
    minorExt = [0,2,3,5,7,8,9,10,11]
    minor = [0,2,3,5,7,8,10]
    dorian = [0,2,3,5,7,9,10]
    phrygian = [0,1,3,5,7,8,10]
    lydian = [0,2,4,6,7,9,11]
    mixolydian = [0,2,4,5,7,9,10]
    aeolian = [0,2,3,5,7,8,10]
    locrian = [0,1,3,5,6,8,10]    
    pentatonic = [0,2,4,7,9]
    japanese = [0,1,5,7,10]
    blues = [0,2,3,4,7,9,11]
    bluesMin = [0,3,4,5,6,7,10]
    twelvetone = [0,1,2,3,4,5,6,7,8,9,10,11]
    dim = [0,2,3,5,6,8,10]
    aug = [0,2,4,5,8,9,10]
    augmaj = [0,2,4,5,8,9,11]
    
    
    def __init__(self):
        self.key = 0
        self.scale_type = self.major
        self.notes = []

    def initialize(self,key,stype):
        self.key = key
        self.scale_type = stype
        self._setNotes()
    
    def _setNotes(self):
        self.notes = []
        for i in self.scale_type:
            self.notes.append(self.key + i)
            
    def find(self,key):
        index = -1
        try:
            index = self.notes.index(key)
        except ValueError:
            index = -1
        return index
    
    def get(self,index):
        if index > len(self.notes)-1:
            return -1
        else:
            return self.notes[index]
        
    def getNameFromNote(self,note):
        if note >= 0 and note < 12:
            return note_names[note]
        elif note > 11 and note < 24:
            note -= 12
            return note_names[note]
        elif note > 23 and note < 36:
            note -= 24
            return note_names[note]
        else:
            return "unknown"
        
    def getTypeNameFromType(self,stype):
        if stype == self.major:
            return "major"
        elif stype == self.minor:
            return "minor"
        elif stype == self.minorExt:
            return "minor"
        elif stype == self.aeolian:
            return "aeolian"
        elif stype == self.locrian:
            return "locrian"
        elif stype == self.dorian:
            return "dorian"
        elif stype == self.lydian:
            return "lydian"
        elif stype == self.mixolydian:
            return "mixolydian"
        elif stype == self.phrygian:
            return "phrygian"
        elif stype == self.pentatonic:
            return "pentatonic"
        elif stype == self.blues:
            return "blues"
        elif stype == self.bluesMin:
            return "blues minor"
        elif stype == self.japanese:
            return "japanese"
        elif stype == self.twelvetone:
            return "twelve-tone"
        elif stype == self.dim:
            return "dim"
        elif stype == self.aug:
            return "aug"
        elif stype == self.augmaj:
            return "augmaj"
        else:
            return "unknown"
        
    def asString(self):
        buf = "scale: %s %s\n" % (self.getNameFromNote(self.key),self.getTypeNameFromType(self.scale_type))
        for n in self.notes:
            buf += self.getNameFromNote(n)
            buf +=","
        buf += "\n"    
        return buf


class ScaleUtil(object):

    def __init__(self):
        self.chords = []
        self.scale = Scale()
        self.chordNames = []

    def setKey(self,key):
        note,stype = self._getScaleFromString(key)
        self.scale.initialize(note,stype)
        self.chords = []
        self.chordNames = []

    def _isPlainMajor(self,chord,seventh=False):
        length = 3
        if seventh == True:
            length = 4
        if len(chord) != length:
            return False
        root = chord[0]
        second = chord[1]
        if second != root +4:
            return False
        third = chord[2]
        if third != root +7:
            return False
        if seventh == True:
            if chord[3] != root + 10 and chord[3] != root + 11:
                return False
        return True

    def _isPlainMinor(self,chord,seventh= False):
        length = 3
        if seventh == True:
            length = 4
        if len(chord) != length:
            return False
        root = chord[0]
        second = chord[1]
        if second != root +3:
            return False
        third = chord[2]
        if third != root +7:
            return False
        if seventh == True:
            if chord[3] != root + 10:
                return False
        return True
        
    def getChords(self):
	if len(self.chords) == 0:
	    self._findChords()
        text = self.scale.asString()
        text += "  CHORDS\n"
        i = 0
        for n in self.chordNames:
            ch = self.chords[i]
            if self._isPlainMajor(ch) or self._isPlainMinor(ch):
                text += "**" 
            elif self._isPlainMajor(ch,True) or self._isPlainMinor(ch,True):
                text += " *"
            else:
                text += "  "
            text += n
            text += " < "
            for note in ch:
                text += self.scale.getNameFromNote(note)
                text += " "
            text += ">\n"
            i += 1
        return text

    def _findChords(self):
        chords = []
        for n in self.scale.notes:
            for o in self.scale.notes:
                if o == n:
                    continue
                elif o < n:
                    if o+12 == n:
                        continue
                    o += 12
                for p in self.scale.notes:
                    if p == o or p == n:
                        continue
                    elif p < o:
                        if p+12 == o:
                            continue
                        p += 12
                    chord = []
                    chord.append(n)
                    chord.append(o)
                    chord.append(p)
                    chords.append(deepcopy(chord))
                    for q in self.scale.notes:
                        if q == p or q == o or q == n:
                            continue
                        elif q < p:
                            if q+12 == p:
                                continue
                            q += 12
                        chord = []
                        chord.append(n)
                        chord.append(o)
                        chord.append(p)
                        chord.append(q)
                        chords.append(deepcopy(chord))
        self.chords = []
        self.chordNames = []
        for ch in chords:
            chord = []
            for n in ch:
                nname = self.scale.getNameFromNote(n)
                chord.append(nname)
            name = self._shuffle(chord)
            if len(name) > 0:
                self.chords.append(ch)
                self.chordNames.append(name)

                                           

    def _getNoteFromName(self,key):
        index = -1
        try:
            index = note_names.index(key)
        except ValueError:
            index = -1
            try:
                index = note_names2.index(key)
            except ValueError:
                index = -1
        return index
        

    def _getScaleFromString(self,scale_str):
        key,stype = scale_str.split()
        note = self._getNoteFromName(key)
        if note < 0 and note > 11:
            print "wrong note %s, set to c" % key
            note = 0
        sctype = Scale.major
        if stype == "major":
            sctype = Scale.major
        elif stype == "minor":
            sctype = Scale.minor
        elif stype == "minorExt":
            sctype = Scale.minorExt
        elif stype == "dorian":
            sctype = Scale.dorian
        elif stype == "lydian":
            sctype = Scale.lydian
        elif stype == "locrian":
            sctype = Scale.locrian
        elif stype == "mixolydian":
            sctype = Scale.mixolydian
        elif stype == "phrygian":
            sctype = Scale.phrygian
        elif stype == "aeolian":
            sctype = Scale.aeolian
        elif stype == "pentatonic":
            sctype = Scale.pentatonic
        elif stype == "blues":
            sctype = Scale.blues
        elif stype == "bluesMin":
            sctype = Scale.bluesMin
        elif stype == "japanese":
            sctype = Scale.japanese
        elif stype == "twelve-tone":
            sctype = Scale.twelvetone
        elif stype == "dim":
            sctype = Scale.dim
        elif stype == "aug":
            sctype = Scale.aug
        elif stype == "augmaj":
            sctype = Scale.augmaj
        else:
            print "I don't know %s, set to major" % stype
        return note,sctype    

    def getChordInfo(self,notes):
        if len(notes) < 3:
            print "Chord must have at least 3 notes"
            return
        self.name = notes[0]
        name = self.name
        tonic = self._getNoteFromName(self.name)
        step1 =  self._getNoteFromName(notes[1])
        step2 = self._getNoteFromName(notes[2])
        
        while step1 < tonic:
            step1 += 12   
               
        while step2 < step1:
            step2 += 12      
        interval1 = step1 - tonic
        interval2 = step2 - tonic
        interval3 = -1
        if len(notes) > 3:
            step3 = self._getNoteFromName(notes[3])
            while step3 < step2:
                step3 += 12      

            interval3 = step3 -tonic
        #print 0,interval1,interval2,interval3
        
        if interval3 == -1: # triad
            if interval1 == 4: # major
                if interval2 == 7:
                    return name
                elif interval2 == 8:
                    name += "+"
            elif interval1 == 2:
                if interval2 == 7:
                    name +="sus2"
            elif interval1 == 3:
                if interval2 == 7:
                    name +="m"
                elif interval2 == 6:
                    name +="dim"
            elif interval1 == 5: 
                if interval2 == 7:
                    name+"sus4"
            elif interval1 == 7: 
                if interval2 == 12:
                    name += "5" #powerchord
        else:
            if interval1 == 4: #major:
                if interval2 == 7: #pure major
                    if interval3 == 10:
                        name += "7"
                    elif interval3 == 11:
                        name += "maj7"
                    elif interval3 == 9:
                        name +="6"
                    elif interval3 == 14:   
                        name +="add9"
                    elif interval3 == 8:   
                        name +="b13"
                    elif interval3 == 17:   
                        name +="add11"
                elif interval2 == 6:
                    if interval3 == 10:
                        name += "7/5-"
                    elif interval3 == 11:
                        name += "maj7/5-"
                    elif interval3 == 8:   
                        name +="7b13/5-"
                elif interval2 == 8:
                    if interval3 == 10:
                        name += "7/5+"
                    elif interval3 == 11:
                        name += "maj7/5+"
                    elif interval3 == 9:
                        name +="6/5+"
                elif interval2 == 9:
                    if interval3 == 14:
                        name += "6/9"
            elif interval1 == 3: #minor or dim         
                if interval2 == 7: #pure minor
                    if interval3 == 10:
                        name += "m7"
                    elif interval3 == 11:
                        name += "mmaj7"
                    elif interval3 == 9:
                        name +="m6"
                    elif interval3 == 14:   
                        name +="madd9"
                    elif interval3 == 8:   
                        name +="mb13"
                    elif interval3 == 17:   
                        name +="madd11"
                elif interval2 == 6: # dim
                    if interval3 == 9:   
                        name +="dim7"
            elif interval1 == 5: #sus4         
                if interval2 == 7: 
                    if interval3 == 10:
                        name += "7sus4"
                    elif interval3 == 11:
                        name += "maj7sus4"
                    elif interval3 == 9:
                        name +="6sus4"
                    elif interval3 == 14:   
                        name +="add9sus4"
                    elif interval3 == 8:   
                        name +="b13sus4"
                    elif interval3 == 17:   
                        name +="add11sus4"
            elif interval1 == 2: #sus2         
                if interval2 == 7: 
                    if interval3 == 10:
                        name += "7sus2"
                    elif interval3 == 11:
                        name += "maj7sus2"
                    elif interval3 == 9:
                        name +="6sus2"
                    elif interval3 == 14:   
                        name +="add9sus2"
                    elif interval3 == 8:   
                        name +="b13sus2"
                    elif interval3 == 17:   
                        name +="add11sus2"
        #print 0,interval1,interval2,interval3
        if name == notes[0]:
            name = ""            
        return name


    def _shuffle(self,notes):
        chordname = ""
        if len(notes) > 1:
            shuffle = []
            for n in notes:
                shuffle.append(n)
                
            steps = len(shuffle) -1
            step = 0    
            while step <= steps:
                lastname = chordname
                chordname += self.getChordInfo(shuffle)
                if len(chordname) != len(lastname):
                    chordname += ", "
                c = steps-1
                tmp = shuffle[steps]
                tmp1 = ""
                shuffle[steps] = shuffle[0]
                while c >= 0:
                    if len(tmp):
                        tmp1 = shuffle[c]
                        shuffle[c] = tmp
                        tmp = ""
                    else:    
                        tmp = shuffle[c]
                        shuffle[c] = tmp1
                        tmp1 = ""
                    c -= 1
                                    
                step += 1
        return chordname


def usage():
        print "ScaleUtil" 
        print "usage: ScaleUtil.py [options]"
        print "-h print help"
        print "-k the key and the type of the scale, e.g. c major"
        

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hk:", ["help","key="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    key = "c major"
    for o, a in opts:
        if o in ("-k", "--key"):
            key = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
    

    seq = ScaleUtil()
    seq.setKey(key)
    print seq.getChords()


if __name__ == "__main__":
    main()
