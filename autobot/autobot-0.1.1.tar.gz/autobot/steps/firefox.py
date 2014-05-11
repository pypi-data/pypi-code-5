"""
buildsteps related to the Firefox browser
"""

from buildbot.process.properties import WithProperties
from buildbot.steps.shell import ShellCommand  

class DownloadFirefoxRelease(ShellCommand):

    def __init__(self, os, version, locale='en-US', bits=32,
                 base_url='http://stage.mozilla.org/pub/mozilla.org/firefox/releases',
                 **kw):
        """
        - os : operating system to download for [linux, win, mac]
        - version : version of Firefox (e.g. 4.0b1)
        - locale : the full locale
        - bits : 32 or 64
        - base_url : location of the releases
        """
        ShellCommand.__init__(self, **kw)
        self.addFactoryArguments(os=os, version=version,
                                 locale=locale, bits=bits, base_url=url)
        url = base_url.rstrip('/') + '/' + version + '/'
        if os == 'linux':
            if bits == 32:
                platform = 'linux-i686'
            elif bits == 64:
                platform = 'linux-x86_64'
            else:
                raise NotImplementedError("bits must be 32 or 64")
        elif os == 'win':
            platform = 'win32' # for 32 + 64 bits, evidently
        elif os == 'mac':
            if bits == 32:
                platform == 'mac'
            elif bits == 64:
                platform == 'mac64'
            else:
                raise NotImplementedError("bits must be 32 or 64")
        
#        self.command = ['wget', '-o', url] # STUB
