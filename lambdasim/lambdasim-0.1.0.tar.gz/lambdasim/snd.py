import sndfileio
import os
import warnings


def split_channels(sndfile, suffixes=None):
    """
    Split the channels in `sndfile`, resulting in mono files
    with the same format as `sndfile`.

    sndfile  : the multichannel soundfile to be split
    suffixes : if given, it must match the number of channels
               in `sndfile` They will be used as suffixes

    Example
    =======

    Given a multichannel file 'snd.wav' with 3 channels,

    >>> split_channels(sndfile, ['L', 'R', 'C'])

    Will produce three files
    'snd-L.wav', 'snd-R.wav' and 'snd-C.wav'
    """
    info = sndfileio.sndinfo(sndfile)
    sample = sndfileio.sndread(sndfile)
    numchannels = sndfileio.numchannels(sample.samples)
    if numchannels == 1:
        raise ValueError("The given soundfile is already mono. Can't split it")
    if suffixes is None:
        suffixes = [str(i) for i in range(1, numchannels+1)]
    else:
        if len(suffixes) > numchannels:
            warnings.warn("More suffixes given than channels in the soundfile")
            suffixes = suffixes[:numchannels]
        else:
            raise IndexError("The soundfile has %d channels, but only %d suffixes were given" %
                             (numchannels, len(suffixes)))
    base, ext = os.path.splitext(sndfile)
    for idx, suffix in enumerate(suffixes):
        outfile = "%s-%s.%s" % (base, suffix, ext)
        monosamples = sample.samples[:,idx]
        sndfileio.sndwrite(monosamples, info.samplerate, outfile, encoding=info.encoding)