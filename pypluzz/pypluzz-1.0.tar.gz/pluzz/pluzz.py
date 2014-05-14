"""\
Pluzz Downloader

Downloads a movie from the French Television VOD

Usage:
  pluzz_downloader.py gui [<url>] [-t <target>] [--avconv <avconv>] [--verbose]
  pluzz_downloader.py <url> fetch [-t <target>] [--avconv <avconv>] [--verbose]
  pluzz_downloader.py <url> get [<key>]
  pluzz_downloader.py <url> show

Commands:
  gui                    Launch graphical user interface
  get                    Get list of keys
  get <key>              Get value for key
  show                   Give summary for key
  fetch                  Download the TV show

Options:
  <url>                  URL of the TV show
  -t --target <target>   Target directory to download the file to [default: ~/Downloads]
  --avconv <avconv>      Sets full path to avconv binary [default: /usr/bin/avconv]
  -V --verbose           Show more output.
  -h --help              Show this screen.

(c)2014 Bernard `Guyzmo` Pratz
Under the WTFPL <http://wtfpl.net>
"""

import io
import os
import re
import sys
import json
import time
import select
import requests
import textwrap
import functools
import subprocess
import collections
from lxml import etree

class PluzzMovie():
    data_url = "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={show}&catalogue=Pluzz&callback=webserviceCallback_{show}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:19.0) Gecko/20100101 Firefox/19.0'}
    avconv_args = ['-y', '-vcodec', 'copy', '-acodec', 'copy']

    def __init__(self, url):
        self.url = url
        self.show_id = None
        self.data = {}

    def retrieve_data(self):
        p = etree.HTML(requests.get(self.url, headers=self.headers).text)
        self.show_id = p.xpath('//meta[@property="og:url"]/@content')[0].split(',')[-1].split('.')[0]
        self.data = json.loads("".join(requests.get(self.data_url.format(show=self.show_id), headers=self.headers).text.split('(')[1:])[:-1])

    # Duration: 00:44:47.95, start: 0.100667, bitrate: 0 kb/s\n
    duration_r = re.compile(r'.*Duration: (\d\d):(\d\d):(\d\d.\d\d), .*')
    # frame=59282 fps=939 q=-1.0 size=  244134kB time=2371.24 bitrate= 843.4kbits/s
    processd_r = re.compile(r'.* time=(\d+.\d\d) .*')
    # already exists. Overwrite ? [y/N]
    overwrite_r = re.compile(r".*File '([^']+)' already exists.*")

    def save(self, target_path="~/Downloads", callback=lambda p, t, d, s: print(p, t, d, s), avconv_path='/usr/bin/avconv', verbose=False):
        if not os.path.isdir(os.path.expanduser(target_path)):
            raise Exception("Can't download and convert: target directory '{}' does not exists".format(target_path))
        def output_parser(output, env={}):
            if verbose:
                print(output, file=sys.stderr, end="")
                return
            duration_m = self.duration_r.match(output)
            if duration_m:
                h,m,s = duration_m.groups()
                env['duration'] = int(h)*3600 + int(m)*60 + float(s)
                env['start'] = time.time()
            elif 'duration' in env.keys():
                processd_m = self.processd_r.match(output)
                if processd_m:
                    pos = float(processd_m.groups()[0])
                    spt = int(time.time()-env['start'])
                    callback(pos, env['duration'], spt, env['start'])
                else:
                    overwrite_m = self.overwrite_r.match(output)
                    if overwrite_m:
                        path = overwrite_m.groups()[0]
                        raise Exception('Output file "{}" already exists in target directory.'.format(path))

        p = requests.get(list(filter(lambda x: x['format'] == 'm3u8-download', self.data['videos']))[0]['url'], headers=self.headers).text
        video_url = list(filter(lambda l: "index_2" in l, p.split()))[0]
        dest_file = "{}_{}.mkv".format(self.data['code_programme'], self.show_id)
        self.dest_file = os.path.join(os.path.expanduser(target_path), dest_file)
        p = subprocess.Popen([avconv_path, '-i', video_url] + self.avconv_args + [self.dest_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = io.TextIOWrapper(p.stdout)
        err = io.TextIOWrapper(p.stderr)
        while p.poll() == None:
            ret = select.select([out.fileno(), err.fileno()], [], [])
            for fd in ret[0]:
                if fd == out.fileno():
                    output_parser(out.readline())
                if fd == err.fileno():
                    output_parser(err.readline())
        for line in out.read().split('\n'):
            output_parser(line)
        for line in err.read().split('\n'):
            output_parser(line)

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def __getitem__(self, it):
        return self.data[it]

    def __setitem__(self, it, val):
        raise Exception("Movie data are immutables")

def get_term_size():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

def show_progress(position, total, spent, start):
    width = (get_term_size()[0]*0.6)
    adv = position/total
    eta = int((time.time() - start)*total/position)
    print((_('Download and convert')+': [{: <'+str(int(width))+'s}] {:0.0%} ETA: {}s/{}s').format('#'*int(width*adv), adv, spent, eta), end='\r')

def main():
    from docopt import docopt
    try:
        args = docopt(__doc__)
        if args['gui']:
            try:
                import pluzz.qtpluzz
                pluzz.qtpluzz.main(args)
            except ImportError:
                raise Exception(_("Couldn't load Qt libraries. Impossible to run the GUI, sorry."))
        elif args['fetch']:
                if not args['<url>']:
                    raise Exception(_('Missing URL!'))
                print(_('Init…'), end="\r", file=sys.stderr)
                m = PluzzMovie(args['<url>'])
                print(_('Get data…'), end="\r", file=sys.stderr)
                m.retrieve_data()
                print(_("Download and convert…"), end='\r', file=sys.stderr)
                m.save(args['--target'],
                       callback=show_progress,
                       avconv_path=args['--avconv'],
                       verbose=args['--verbose'])
                print(("{: <"+str(int(get_term_size()[0]))+"}").format("Download and convertion done: '{}' saved".format(m.dest_file)))
        elif args['get']:
            if not args['<url>']:
                raise Exception(_('Missing URL!'))
            print(_("Init…"), end="\r", file=sys.stderr)
            m = PluzzMovie(args['<url>'])
            print(_("Get data…"), end="\r", file=sys.stderr)
            m.retrieve_data()
            if args['<key>'] and args['<key>'] in m.keys():
                print((_("Showing {}:")+"               ").format(args['<key>']))
                if m[args['<key>']]:
                    if isinstance(m[args['<key>']], collections.Iterable) \
                                                    and len(m[args['<key>']]) > 70:
                        for line in textwrap.wrap(m[args['<key>']]):
                            print("  {}".format(line))
                    else:
                        print("  {}".format(str(m[args['<key>']])))
            else:
                print(_("List of all keys for the show: '{}'").format(m['titre']))
                for k in m.keys():
                    print("  {}".format(k))
        elif args['show']:
            print(_("Init…"), end="\r", file=sys.stderr)
            m = PluzzMovie(args['<url>'])
            print(_("Get data…"), end="\r", file=sys.stderr)
            m.retrieve_data()
            t = time.strftime(_("On %d %h %Y at %H:%M"), time.localtime(m['diffusion']['timestamp']))
            print(_("Summary of the show '{}'").format(m['titre']))
            print(_("        id: {:<30}").format(m['id']), end="")
            print(_("  id AEDRA: {:<30}").format(m['id_aedra']))
            print(_(" Broadcast: {:<30}").format(t), end="")
            print(_("    Length: {:<30}").format(m['duree']))
            print(_("     Genre: {:<30}").format(m['genre']), end="")
            print(_("    Season: {:<30}").format(m['saison']))
            print(_("   Website: {:<30}").format(m['url_site']))
            print(_("     Pluzz: {:<30}").format(m['url_reference']))
            print(_("   Channel: {:<30}").format(m['chaine']), end="")
            print(_("   Picture: {:<30}").format(m['image']))
            print(_("    Rights: {:<30}").format(m['droit']['csa']))

            print(_("      Crew:"))
            for p in m['personnes']:
                print(_("{f:>24}: {n}, {p}").format(f=", ".join(p['fonctions']), p=p['prenom'], n=p['nom'], ))
            print(_("  Synopsis:"))
            for line in textwrap.wrap(m['synopsis'], initial_indent="    "):
                print("  {}".format(line))


    except Exception as err:
        print("", file=sys.stderr)
        print(_("Error:"), err, file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
