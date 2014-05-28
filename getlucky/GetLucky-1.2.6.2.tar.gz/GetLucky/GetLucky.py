"""
Get Lucky.

Usage:
  gl
  gl lucky [options]
  gl mood (<mood>) [-h]
  gl genre (<genre>) [-h]
  gl activity (<activity>) [-h]
  

Options:
  -h  --help                Show this screen.

  -m, --makeout             Nothing too serious, just a two good looking people playing tonsil hockey to win.

  -s, --sexy                You got on the fanciest, frilliest underwear you were able to find for 20 bucks on ebay.
                           
  -d, --seductive           You've laid down a path of rose pedals down and somehow managed to coat
                            everything in velour so everything is as smooth as you are. 

  -a, --aggressive          While vanilla is it's own distinct delicous flavor, you're past that.
                            You try throw in some spanking, hair pulling, roaring. That last one usually
                            doesn't go over well. Don't worry you'll find someone to call you El Tigre.
                            
  -x, --extreme             Spanking? That's cute you know how to tie more knots than an eagle socut
                            and have your own personal collection of whips, chains and handc..holy shit 
                            is that a morningstar?  Well that's a new way to go medevil on someone's ass.
"""

from docopt import docopt
from collections import Iterable
from bs4 import BeautifulSoup
from string import maketrans 
from string import punctuation
import subprocess as sub
import platform
import sys,os
import ConfigParser
import requests
import random
import string




class Playlister(object):

  def __init__(self):
    pass


  def randomPlaylist(self, urls,idName,value,tagtype=True):
    """
    Returns a soup tag object that has data that allows us to accsess a playlist 
    from a url by using the identifier from the kwargs.
    
    For example the songza mood pages have  list items that look like this:

    <h3 class="browse-playlist-title"> Today's Americana </h3>

    In this case:
      tagtype = 'h3'
      idName = "class"
      value = "browse-playlist-title"

    We will return the li tag object so we can then use the station data-sz-station-id to play
    the playlist.

    We're returning a soup tag object instead of just directly playing from here so we can 
    extend functionality to diffrent services like Pandora.

    """
    playlists = []
    for url in urls:      ## so we can pick a random from multiple categories
      html_page = requests.get(url,timeout=2)

      if html_page.status_code != requests.codes.ok:  
        print  "Unable to load webpage. Did you spell all your arguments correctly?"
        sys.exit(0)

      soup = BeautifulSoup(html_page.text)
      identifier={idName:value}
      playlists += soup.find_all(tagtype,attrs=identifier)


    return random.choice(playlists)




class AbstractService(object):
  def __init__(self):
    self.proc = None

  def playRandom(self):
    abstract

  def handleInput(self):
    abstract

  def sanitize(self,string,delimiter="_"):
    """ Makes arguments url friendly"""
    clean = string.translate(None,punctuation).replace(" ",delimiter)
    return clean


  def openUrl(self,url):
    if platform.system()=='Linux':
      proc=sub.Popen(['xdg-open',url],stdout = sub.PIPE)
    elif platform.system()=='OSX':
      proc=sub.Popen(['open',url],stdout = sub.PIPE)
    else:
      proc = sub.Popen(['start',url],stdout = sub.PIPE,shell = True)

class Songza(AbstractService):

  def __init__(self,iniFile):
    super(Songza,self).__init__()
    self.baseUrl = "http://songza.com"
    self.moods = self.baseUrl+"/discover/moods/"
    self.genres = self.baseUrl+"/discover/genres/"
    self.activity = self.baseUrl+"/discover/activities/"
    self.listen = self.baseUrl+"/listen/"
    self.calls = {'mood':self.moods,'genre':self.genres,'activity':self.activity}
    self.config = ConfigParser.ConfigParser()
    self.config.read(iniFile)
    self.Playlister = Playlister()


  def playRandom(self,categories):

    """ 
      Plays random playlist from category

      args:
        categories list of tuples  denoting catageory and category type:
          ex: to play a playlist from the Seductive mood or the  makeout activities:
            categories = [('mood','Seductive'),('activities','makeout')]

      returns: nothing
    """
    if not isinstance(categories, list):  categories = [categories]
    urls = [self.calls[category[0]]+category[1] for category in categories]
    playlistTag = self.Playlister.randomPlaylist(urls,'class','browse-playlist playable',tagtype='li')
    playlist = playlistTag.a.get('href')
    self.openUrl(self.baseUrl+playlist)


  def handleInput(self, input):
    
    if input['lucky']==True:
      options = [ arg.replace('-','') for arg in input if '-'in arg and input[arg]] #get option name w/o -
      getCategory = lambda option: tuple(self.config.get('Songza Shortcuts',option).split(' '))

      if options:
        categories = [getCategory(option) for option in options]

      else:
        categories=('activity','getting_lucky')

      self.playRandom(categories)
      print "Get Down with your bad self"


    else:
        for arg in input:
          if '<' in arg and input[arg]: value = input[arg].lower()
          elif '-' not in arg and input[arg]: cmd = arg

        category = (cmd,self.sanitize(value))
        self.playRandom(category)



    
 
def main():
    arguments = docopt(__doc__, version='Get Lucky 1.0')
    iniFile = 'data/GetLucky.ini'
    if any(arguments[arg] for arg in arguments):
      s = Songza(iniFile)
      s.handleInput(arguments)
    else:
      print __doc__









if __name__ == '__main__':
  main()

    


