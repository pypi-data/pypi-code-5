import numpy

source_kinds = {
    'sin': 1,
    'square': 2,
    'deltapulse': 3,
    'expdecay': 4,
    'hannsin': 5,
    'vel-sin': 6,
    'vel-square': 7,
    'vel-deltapulse': 8,
    'vel-expdecay': 9,
    'vel-hannsin': 10,
    'whitenoise': 20,
    'pinknoise': 21,
    'sample': 30
}


class Source(object):
    def __init__(self, xpix, ypix, kind='hannsin', amp=1, freq=440, phase=0, sampleidx=None):
        """
        amp      : amplitude (sound pressure in Pa)
        freq     : freq of source (unused in whitenoise, pinknoise)
        phase    : phase of source (unused for whitenoise, pinknoise, sample)
        sampleidx: idx of a Sample definition, used only for the 'sample' kind

        NB: convert dB (sound-pressure-level) to Pa with dB2Pa
        """
        self.xpix = xpix
        self.ypix = ypix
        if isinstance(kind, Number):
            self.kind = kind
        else:
            source_kinds.get(kind, source_kinds.get('hannsin'))
        if kind == 'sample':
            freq = sampleidx
        self.freq = freq
        self.amp = amp
        self.phase = phase

    def __repr__(self):
        return "source kind:%d pos:(y=%d x=%d) amp:%f freq:%f phase:%d" % (
            self.kind, self.ypix, self.xpix, self.amp, self.freq, int(self.phase)
        )

    def asarray(self):
        return numpy.array(
            [self.ypix, self.xpix, self.kind, self.amp, self.freq, self.phase],
            dtype=float
        )

    def asmatlab(self):
        mat = self.asarray()
        mat[0] += 1
        mat[1] += 1
        return mat
