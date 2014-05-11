'''
Created on May 22, 2013

@author: karthicm
'''
from lib_Operations_Common import is_element_present, ConvertToSeconds, FloatEquals

def cloudplayer_goto_songs_view(wd_handle):
    '''
    *********************************************************************
    
    Keyword Name    :Cloudplayer Goto Songs View
    
    Usage           :
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    SongsView = is_element_present(wd_handle,'SAF_Songs_Link')
    while SongsView is not None:
        try:
            SongsView.click()
            print 'MSG: Cloud Player successfully navigated to Songs View'
            return True
        except:
            SongsView = is_element_present(wd_handle,'SAF_Songs_Link')
    print 'Error: Cloud Player could not navigate to Songs View'
    assert False
    return False

def cloudplayer_goto_album_view(wd_handle):
    '''
    
    *********************************************************************
    
    Keyword Name    :Cloudplayer Goto Album View
    
    Usage           :
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    AlbumView = is_element_present(wd_handle,'SAF_Albums_Link')
    while AlbumView is not None:
        try:
            AlbumView.click()
            print 'MSG: Cloud Player successfully navigated to Albums View'
            return True
        except:
            AlbumView = is_element_present(wd_handle,'SAF_Albums_Link')
    print 'Error: Cloud Player could not navigate to Albums View'
    assert False
    return False
    
    
def cloudplayer_goto_artist_view(wd_handle):
    '''
    
    *********************************************************************
    
    Keyword Name    :Cloudplayer Goto Artist View
    
    Usage           :
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    ArtistView = is_element_present(wd_handle,'SAF_Artists_Link')
    while ArtistView is not None:
        try:
            ArtistView.click()
            print 'MSG: Cloud Player successfully navigated to Artist View'
            return True
        except:
            ArtistView = is_element_present(wd_handle,'SAF_Artists_Link')
    print 'Error: Cloud Player could not navigate to Artist View'
    assert False
    return False
    
def cloudplayer_goto_genres_view(wd_handle):
    '''
    
    *********************************************************************
    
    Keyword Name    :Cloudplayer Goto Genres View
    
    Usage           :Function navigates to Genres view in Cloud player
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    GenresView = is_element_present(wd_handle,'SAF_Genres_Link')
    while GenresView is not None:
        try:
            GenresView.click()
            print 'MSG: Cloud Player successfully navigated to Genres View'
            return True
        except:
            GenresView = is_element_present(wd_handle,'SAF_Genres_Link')
    print 'Error: Cloud Player could not navigate to Genres View'
    assert False
    return False
    
def play_album_in_cloudplayer(wd_handle,AlbumName):
    '''
    
    *********************************************************************
    
    Keyword Name    :Play Album In Cloudplayer
    
    Usage           :Function plays the Album with the given AlbumName in Cloudplayer on Album View
    
    Return Value    : Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    *********************************************************************
    '''
    try:
        #cloudplayer_goto_album_view(wd_handle)
        prvObj =  wd_handle.find_element_by_xpath("//li[@albumname='"+AlbumName+"']/div/div/a[@class='albumArtMp3PlaySprite playAlbum']")
        prvObj.click()
        return True
    except:
        return False
    
def play_artist_in_cloudplayer(wd_handle,ArtistName):
    '''
    *********************************************************************
    
    Keyword Name    :Play Artist In Cloudplayer
    
    Usage           :Function plays the Artist with the given ArtistName in Cloudplayer on Artist View
    
    Return Value    : Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        #cloudplayer_goto_artist_view(wd_handle)
        prvObj =  wd_handle.find_element_by_xpath("//div[@title='"+ArtistName+"']/div/a[@class='albumArtMp3PlaySprite playAlbum']")
        prvObj.click()
        return True
    except:
        return False
    
def play_genres_in_cloudplayer(wd_handle,GenresName):
    '''
    *********************************************************************
    
    Keyword Name    :Play Genre In Cloudplayer
    
    Usage           :Function plays the Genre with the given GenresName in Cloudplayer on Genre View
    
    Return Value    : Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    try:
        #cloudplayer_goto_genres_view(wd_handle)
        prvObj =  wd_handle.find_element_by_xpath("//div[@title='"+GenresName+"']/div/a[@class='albumArtMp3PlaySprite playAlbum']")
        prvObj.click()
        return True
    except:
        return False
    
def get_total_song_count(wd_handle):
    '''
    
    *********************************************************************
    
    Keyword Name    :Get Total Song Count
    
    Usage           :Function returns the total song count in the cloud player
    
    Return Value    : Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    TotalSong = is_element_present(wd_handle, "//*[@id='songsLinkCount']","XPATH")
    TotalSongCount = int(TotalSong.text)
    return TotalSongCount

def play_track_in_cloudplayer(wd_handle,SongName,ValidatePlay=False):
    '''
    *********************************************************************
    
    Keyword Name    :Play Track In Cloudplayer
    
    Usage           :Function plays the song in Songs view by the given SongName in Transport. Validating Play can be Optional, If True the Total vs played Duration, buffered vs played percentage of the song is validated for the Transport. 
    
    Return Value    : Returns True on Success and False on Failure
    
    ToDo            :NIL
    
    =====================================================================
    
    Created By          :Karthick Mani
    
    Created Date        :05/10/2013
    
    Last Modified By    :Karthick Mani
    
    Last Modified Date  :06/18/2013
    
    *********************************************************************
    '''
    i = 0
    BoolCompleteSearch = False
    SongPlayed = False
    #'CP_WebPlayer_SongsCount'
    try:
        cloudplayer_goto_songs_view(wd_handle)
    except:
        print "Could not go to Songs view"
    TotalSongCount= get_total_song_count(wd_handle)
    SongXpath = "//td[@title='"+SongName+"']/preceding-sibling::td/a[@class='mp3PlaySprite']"
    prvObj = is_element_present(wd_handle, SongXpath, 'XPATH')
    #prvObj = is_element_present(wd_handle, 'CP_WebPlayer_TrackPlay_Button', 'XPATH')
    #prvObj =  wd_handle.find_element_by_xpath(SongXpath)
    if prvObj is not None:
        prvObj.click()
        SongPlayed = True
    else:
        while prvObj is None:
            if i <TotalSongCount and i % 50== 0:
                i = i + 49
                if i>TotalSongCount:
                    i = TotalSongCount-1
                    BoolCompleteSearch = True
                Xpath_CheckBox = "//tr[@idx='"+str(i)+"']/td/input[@class='checkbox']"
                Element_CheckBox = wd_handle.find_element_by_xpath(Xpath_CheckBox)
                Element_CheckBox.click()
                if Element_CheckBox.is_selected():
                    Element_CheckBox.click()
                prvObj = is_element_present(wd_handle, SongXpath, 'XPATH')
                if prvObj is not None:
                    prvObj.click()
                    SongPlayed = True
                    break
            elif BoolCompleteSearch == True:
                break
            else:
                i = i+1
    if SongPlayed is True:
        if not ValidatePlay is False:
            ValidatePlayInTransport(wd_handle)
        else:
            print "MSG:Currently playing track '"+SongName+"' in Cloud player!!!"
            return True
    else:
        print "Error!!!, Could not play the given track '"+SongName+"' in Cloud player!!!"
        return False
        
def ValidatePlayInTransport(wd_handle):
    try:
        #title=wd_handle.find_element_by_xpath("//span[@class='nowPlay']/following-sibling::span[@class='title']")
        #TitleXpath = "//span[@class='nowPlay']/following-sibling::span[@class='title']"
        title= is_element_present(wd_handle, 'SAF_Transport_Title_Text')
        print "Title\t\t: "+title.text
        
        #artist=wd_handle.find_element_by_xpath("//span[@class='nowPlay']/following-sibling::span[2]")
        #artistXpath = "//span[@class='nowPlay']/following-sibling::span[2]"
        artist = is_element_present(wd_handle, 'SAF_Transport_artist_Text')
        print "Artist\t\t: "+artist.text
        
        #TotalSongDuration=wd_handle.find_element_by_xpath("//span[@id='currentTime']/following-sibling::span[2]")
        #TotalDurationXpath = "//span[@id='currentTime']/following-sibling::span[2]"
        TotalSongDuration=is_element_present(wd_handle,'SAF_Transport_TotalDuration_Text')
        TotalTime = ConvertToSeconds(TotalSongDuration.text)
        print "Total Song Duration\t\t: '%s' Seconds!!!" %(str(TotalTime))
        Bln_IsPlayingCorrect = False
        wd_handle.implicitly_wait(8)
        Scrubber=""
        #Total_Scrubber="width: 100%;"
        Slider=""
        while not Slider =="left: 100%;":
            #Scrubber = wd_handle.find_element_by_xpath("//span[@id='scrubberLoader']").get_attribute("style")
            #ScrubberXpath = "//span[@id='scrubberLoader']"
            #SliderXpath = "//div[@id='scrubber']/a[@class='ui-slider-handle ui-state-default ui-corner-all']"
            Scrubber = is_element_present(wd_handle, 'SAF_Transport_ScrubberLoad')
            Scrubber= Scrubber.get_attribute("style")
            #Slider= wd_handle.find_element_by_xpath("//div[@id='scrubber']/a[@class='ui-slider-handle ui-state-default ui-corner-all']").get_attribute("style")
            Slider = is_element_present(wd_handle, 'SAF_Transport_SliderPlay')
            Slider = Slider.get_attribute("style")
            if Scrubber:
                #print "Scrubber Loaded: "+Scrubber
                SliderPercent = Slider.split(':')
                SliderPercent = str(SliderPercent[1]).split('%')
                SliderPercentFloat = float(SliderPercent[0])
                #print "SliderPercent Loaded: "+str(abs(SliderPercentFloat))
                #CurrentPlayDuration = wd_handle.find_element_by_id("currentTime")
                CurrentPlayDuration = is_element_present(wd_handle,'SAF_Transport_CurrentPlayDuration')
                CurrentTime = ConvertToSeconds(CurrentPlayDuration.text)
                if CurrentTime:
                    PlayedBuffer = float((CurrentTime*100.0)/TotalTime)
                    #print PlayedBufferPercent
                    PlayedBufferPercent = float("{0:.5f}" .format(PlayedBuffer))
                    #print "Calculated Value:"+ str(abs(PlayedBufferPercent1)) + "%"
                    if FloatEquals(PlayedBufferPercent, SliderPercentFloat):
                        Bln_IsPlayingCorrect = True
                        print 'Validating Transport...'+'\n'+'Song slider percent is proportional to the played duration of the song'
                    else:
                        Bln_IsPlayingCorrect = False
                        print "Actual Slider Percent played: "+SliderPercentFloat +"is not equal to expected Played BufferPercent:"+ PlayedBufferPercent 
        if Bln_IsPlayingCorrect:
            print 'Validation Successfull!!!'
            return True
    except:
        return False