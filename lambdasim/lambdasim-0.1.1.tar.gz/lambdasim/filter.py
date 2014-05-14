import numpy


class Filter(object):
    _maxid = 0
    _used_ids = set()

    def __init__(self, b, a, numid=None):
        """
        numid = an integer id
        b     = the sequence of b coefficients
        a     = the sequence of a coefficients
        """
        if numid in self._used_ids:
            warnings.warn("ID already used!")

        if numid is None:
            numid = self.newid()

        self.numid = numid
        self.bb = b
        self.aa = a

    @classmethod
    def newid(cls):
        while True:
            cls._maxid += 1
            if cls._maxid not in self._used_ids:
                newid = cls._maxid
                self._used_ids.add(newid)
                return newid

    def __del__(self):
        self._used_ids.remove(self.numid)

    @classmethod
    def butter(cls, filtertype, freq, samplerate, order=5, numid=None):
        """
        filtertype: one of 'low', 'high', 'band'
        freq      : cutoff freq -- (low, high) for bandpass filter
        samplerate: samplerate of the simulation
        order     : order of the filter

        Returns --> a Filter
        """
        assert filtertype in ('low', 'high', 'band')
        from sndfileio import dsp
        b, a = dsp.filter_butter_coeffs(filtertype, freq, samplerate=samplerate, order=order)
        return cls(b, a, numid=numid)

    def __repr__(self):
        return "filter\nbb=%s \naa=%s" % (str(self.bb), str(self.aa))

    def asarray(self):
        """
        Format
        =======

        ID:       double
        NUMCOEFS: double
        AA:       list of doubles
        BB:       list of doubles

        :rtype : numpy.array
        """
        out = [self.numid, len(self.aa), len(self.bb)]
        out.extend(self.aa)
        out.extend(self.bb)
        return numpy.array(out, dtype=float)
