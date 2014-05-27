"""
Geoza

Usage:
    geoza  (<place>) [options]

Options:
  -h  --help                Show this screen.

"""

from geopy.geocoders import GoogleV3
from docopt import docopt
import requests
import subprocess as sub
import platform
import sys,os
try:
    import simplejson as json
except :
    import json


class Geoza(object):


    def __init__(self,place,areas_json,playlists_json):
        """
        args:
        place: location either name of coordinates to get data on 
        areas_json: json with data on how to classify areas. ex: a forest with > 125in of rain
        playlists_json: json with data on what playlists to play for areas 
        """
        areas_file =  open(areas_json)
        playlist_file = open(playlists_json)
        self.area_categories = json.load(areas_file)
        self.playlist_categories = json.load(playlist_file)
        google_geo = GoogleV3()
        name, (lat,lng) = google_geo.geocode(place)
        self.place = name
        print "Location:",self.place
        self.lat = str(lat)
        self.lng = str(lng)




    def make_coordinate2stats_request(self):
        """
        Makes request to coordinates2statistics to get statistics json

        args:
            lat: string of latitude
            lng: string of longitude

        returns:
            Json style dict of place statistics
        """
        url = "http://www.datasciencetoolkit.org/coordinates2statistics/"+self.lat+'%2c'+self.lng+"?statistics"
        result = requests.get(url)
        stats = json.loads(result.text)
        return stats[0]['statistics']



    def get_population(self):
        """
        Makes request to askgeo to find out the population of the city. We use 
        askgeo because it turns out coordinates2statistics population data isn't accurate.
        """
        delimiter = "%2c"
        place = self.lat+delimiter+self.lng
        key = 'e47a3ac34b80bb966261fb19c1b778979adf917c5f52282a80ce563cfdd54db3'
        base_url = "http://api.askgeo.com/v1/1111/"+key+"/query.json?databases=UsPlace2010&points="
        res = requests.get(base_url+place)
        data = json.loads(res.text)
        population = data["data"][0]["UsPlace2010"]["CensusTotalPopulation"]
        return population




    def is_in_range(self,string_range,number):
        """
        Cheecks if number is in the range indicated by a string.
        ex: is_in_range("10|20",5) >> false

        args:
            range: string of the the form 'number|number'
            number: int
        """
        lst = string_range.split('|')
        return number in range(int(lst[0]),int(lst[1]))




    def set_tags(self):
        """
        Parses the data the place_data from the coordinates2statistics api
        and returns a list of tags. If there's no tag to be set it plays the 
        blogged 50 playlist and exits.

        args:
            place_stats: json of coordinates2statistics data


        """
        self.tags = []    
        place_stats = self.make_coordinate2stats_request()                                                                                                                
        land_cover = place_stats["land_cover"]["value"]


        if "Artificial" in land_cover:
            self.get_city_type(place_stats,self.tags)

        elif "Tree Cover" in land_cover:
            print 
            self.get_forest_type(place_stats,self.tags)

     

    def get_forest_type(self,place_stats,tags):
        """
            Determines type of forest and appends appropriate tags to tags_lst

            args:
                place_stats: json of coordinates2statistics data
                tags_lst: list to put tags in
            returns:
                nothing
        """
        sum_strings= lambda x,y: int(x)+int(y)
        self.tags += ["forest"]

        total_rainfall = reduce(sum_strings,place_stats["precipitation"]["value"])
        print total_rainfall
        rain_ranges = self.area_categories["forest"]["rainfall"]
        self.get_type_tags(rain_ranges,total_rainfall)

        monthly_temps = place_stats["mean_temperature"]["value"]
        avg_temp = reduce(sum_strings,monthly_temps)/len("temps")
        print avg_temp
        temp_ranges = self.area_categories["forest"]["temp"]
        self.get_type_tags(temp_ranges,avg_temp)



    def get_city_type(self,place_stats,tags):
        """
            Determines type of forest and appends appropriate tags to tags_lst

            args:
                place_stats: json of coordinates2statistics data
                tags_lst: list to put tags in
            returns:
                nothing
        """
        self.tags += ["city"]
        population = self.get_population()
        population_ranges =  self.area_categories["city"]["population"]
        self.get_type_tags(population_ranges,population)






    def get_type_tags(self,category,value,delimiter='|'):
        """
        Adds tags to self.tags based on the rages in a category.
        ex: value = 0 category = self.area_categories["forests"]["temp]
            >> adds taiga to tags since a taiga avg_temp is between -10 - 5 degrees C.
        args:
            category: a dict of ranges and their tag. ex: {"-10|5":taiga}
            value: value to check value if in ranges. (usually float or int)
            delimiter: optional argument specifying how the ranges are delimited, defults to '|'
        """
        in_range = lambda num,lst: int(lst[0]) <= num < int(lst[1])
        for classifier in category:
            lst = classifier.split(delimiter)
            if in_range(value,lst):
                self.tags.append(category[classifier])




    def get_playlist(self,playlist_dict):
        """
        Recursively traverses a Json file to find name of playlist to play
        using the tags.

        args:
            playlist_dict: a json already loaded into a dict.

        returns:
            a url to a songza playlist corresponding to a set of tags

            None if a playlist can't be found
        """
        base_url = 'http://songza.com/listen/'

        tag = filter(lambda tag: tag in playlist_dict, self.tags)[:1]
     
        if tag:
            tag = tag[0]  
            if type(playlist_dict[tag]) == str:
                return base_url+playlist_dict[tag]
            else:
                return self.get_playlist(playlist_dict[tag])


    def open_url(self,url):
        if platform.system()=='Linux':
          proc=sub.Popen(['xdg-open',url],stdout = sub.PIPE)
        elif platform.system()=='OSX':
          proc=sub.Popen(['open',url],stdout = sub.PIPE)
        else:
          proc = sub.Popen(['start',url],stdout = sub.PIPE,shell = True)


    def play_playlist(self):
        self.set_tags()
        if self.tags:
            print "Tags:", ', '.join(self.tags)
            playlist = self.get_playlist(self.playlist_categories)
            self.open_url(playlist)
        else:
            print "Don't have anything for this kind of place yet."
            print "How bout some new music?"
            self.open_url('http://songza.com/listen/blogged-50-songza/')
            sys.exit(0)




 



def main():
    arguments = docopt(__doc__, version='Geoza 0.0.1')
    g = Geoza(arguments['<place>'],'areas.json','playlists.json')
    g.play_playlist()







if __name__ == '__main__':
    main()