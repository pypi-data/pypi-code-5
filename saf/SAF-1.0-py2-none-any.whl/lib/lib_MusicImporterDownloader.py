'''
Created on Jul 17, 2013

@author: karthicm
'''
import AutoItLibrary
import time
import os

CurrentUser = os.path.expandvars("%USERPROFILE%")

AMD_InstallerPath = CurrentUser+"\Downloads\AmazonMP3DownloaderInstall._V383688046_.exe"
AMD_UnInstallerPath = CurrentUser+"\AppData\Local\Program Files\Amazon\MP3 Downloader\Uninstall.exe"
Morpho_InstallerPath = CurrentUser+"\Downloads\AmazonCloudPlayerInstaller332._V381017050_.exe" 
Morpho_UnInstallerPath = CurrentUser+"\AppData\Local\Amazon Cloud Player\Uninstall.exe"
#print CurrentUser


def install_morpho(Morpho_InstallerPath):
    SAF_Autoit = AutoItLibrary.AutoItLibrary()
    SAF_Autoit.Run(Morpho_InstallerPath)
    try:
        SAF_Autoit.WinWait("Amazon Cloud Player Setup","",120)
        if SAF_Autoit.WinExists("Amazon Cloud Player Setup"):
            SAF_Autoit.WinSetOnTop("Amazon Cloud Player Setup","",1)
            SAF_Autoit.WinActivate("Amazon Cloud Player Setup")
            Morpho_Install = SAF_Autoit.WinWaitActive("Amazon Cloud Player Setup","",100)
            if Morpho_Install != 0:
                SAF_Autoit.ControlClick("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                try:
                    SAF_Autoit.WinWaitActive("Amazon Cloud Player Setup","",180)
                    time.sleep(60)
                    #SAF_Autoit.WinWaitDelay(60000)
                    SAF_Autoit.ControlFocus("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                    SAF_Autoit.ControlClick("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                    SAF_Autoit.WinWaitActive("Amazon Cloud Player Setup","",180)
                except:
                    SAF_Autoit.ControlFocus("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                    SAF_Autoit.ControlClick("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                    pass
                finally:
                    SAF_Autoit.WinActivate("Amazon Cloud Player Setup")
                    SAF_Autoit.WinSetOnTop("Amazon Cloud Player Setup","",1)
                    SAF_Autoit.Send("{ENTER}")
                    SAF_Autoit.ControlFocus("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                    SAF_Autoit.ControlClick("Amazon Cloud Player Setup","","[CLASSNN:QWidget3]")
                    SAF_Autoit.WinSetOnTop("Amazon Cloud Player Setup","",0)
                    SAF_Autoit.WinActivate("Amazon Cloud Player Setup")
                    SAF_Autoit.WinWaitNotActive("Amazon Cloud Player Setup")
                    SAF_Autoit.WinWaitActive("Amazon Cloud Player","Amazon.com Sign In",120)
                    SAF_Autoit.WinSetOnTop("Amazon Cloud Player","Amazon.com Sign In",1)
                    SAF_Autoit.WinActivate("Amazon Cloud Player","Amazon.com Sign In")
                    print "MSG:Successfully installed MORPHO!!!"
                    SAF_Autoit.Send("{TAB}")
                    SAF_Autoit.Send("karthicm{+}ustest1@amazon.com")
                    SAF_Autoit.Send("{TAB}")
                    SAF_Autoit.Send("test123")
                    SAF_Autoit.Send("{TAB}")
                    SAF_Autoit.Send("{ENTER}")
        else:
            print "MORPHO installation window is not active!!!"
    except Exception as ex:
        print 'Exception occurred during MORPHO installation and the error is: %s' % ex

def uninstall_morpho(Morpho_UnInstallerPath):
    try:
        SAF_Autoit = AutoItLibrary.AutoItLibrary()
        SAF_Autoit.Run(Morpho_UnInstallerPath)
        SAF_Autoit.WinWait("Amazon Cloud Player Setup","",120)
        if SAF_Autoit.WinExists("Amazon Cloud Player Setup"):
            SAF_Autoit.WinActivate("Amazon Cloud Player Setup")
            SAF_Autoit.WinSetOnTop("Amazon Cloud Player Setup","",1)
            Morpho_UnInstall = SAF_Autoit.WinWaitActive("Amazon Cloud Player Setup")
            if Morpho_UnInstall!=0:
                SAF_Autoit.Send("!y")
                SAF_Autoit.WinWaitActive("Amazon Cloud Player Setup","Setup",120)
                SAF_Autoit.WinSetOnTop("Amazon Cloud Player Setup","",0)
                SAF_Autoit.WinActivate("Amazon Cloud Player Setup")
                SAF_Autoit.Send("{ENTER}")
                SAF_Autoit.WinWaitClose("Amazon Cloud Player Setup","Setup",120)
        else:
            print "MORPHO Un-install window is not active!!!"
    except Exception as ex:
        print 'Exception occurred during MORPHO un-installation and the error is: %s' % ex
                
def install_amd(AMD_InstallerPath):
    try:
        SAF_Autoit = AutoItLibrary.AutoItLibrary()
        SAF_Autoit.Run(AMD_InstallerPath)
        SAF_Autoit.WinSetOnTop("Amazon MP3 Downloader Setup ","",1)
        SAF_Autoit.WinActivate("Amazon MP3 Downloader Setup ")
        SAF_Autoit.WinWaitActive("Amazon MP3 Downloader Setup ","Amazon MP3 Downloader is being installed.",120)
        #SAF_Autoit.WinWaitNotActive("Amazon MP3 Downloader Setup ","Please wait while Amazon MP3 Downloader is being installed.",120)
        SAF_Autoit.WinWaitActive("Amazon MP3 Downloader Setup ","Amazon MP3 Downloader was successful",120)
        SAF_Autoit.ControlClick("Amazon MP3 Downloader Setup ","Close",1)
        AMD_Install = SAF_Autoit.WinWaitClose("Amazon MP3 Downloader Setup ","Installation of the Amazon MP3 Downloader was successful",120)
        if AMD_Install == 1:
            print "MSG: AMD Installed Successfully!!!"
        else:
            print "Error: Could not Install AMD!!!"
    except Exception as ex:
        print 'Exception occurred during AMD installation and the error is: %s' % ex

def uninstall_amd(AMD_UnInstallerPath):
    try:
        SAF_Autoit = AutoItLibrary.AutoItLibrary()
        SAF_Autoit.Run(AMD_UnInstallerPath)
        SAF_Autoit.WinSetOnTop("Amazon MP3 Downloader Uninstall","",1)
        SAF_Autoit.WinActivate("Amazon MP3 Downloader Uninstall")
        AMD_Uninstall = SAF_Autoit.WinWaitActive("Amazon MP3 Downloader Uninstall","",120)
        if AMD_Uninstall != 0:
            SAF_Autoit.WinWaitActive("Amazon MP3 Downloader Uninstall","be uninstalled from the following folder",120)
            SAF_Autoit.Send("!u")
            SAF_Autoit.WinWaitNotActive("Amazon MP3 Downloader Uninstall","be uninstalled from the following folder",120)
            SAF_Autoit.WinWaitActive("Amazon MP3 Downloader Uninstall","Amazon MP3 Downloader is being uninstalled.",120)
            SAF_Autoit.WinWaitActive("Amazon MP3 Downloader Uninstall","Uninstall was completed successfully.",120)
            SAF_Autoit.Send("!c")
            AMD_Uninstall = SAF_Autoit.WinWaitClose("Amazon MP3 Downloader Uninstall","Uninstall was completed successfully.",120)
            if AMD_Uninstall == 1:
                print "MSG: AMD Un-installed Successfully!!!"
            else:
                print "Error: Could not Un-install AMD!!!"
    except Exception as ex:
        print 'Exception occurred during AMD un-installation and the error is: %s' % ex


#install_morpho(CurrentUser+"\Downloads\AmazonCloudPlayerInstaller332._V381017050_.exe")
#uninstall_morpho(CurrentUser+"\AppData\Local\Amazon Cloud Player\Uninstall.exe")
#install_amd(CurrentUser+"\Downloads\AmazonMP3DownloaderInstall._V383688046_.exe")
#uninstall_amd(CurrentUser+"\AppData\Local\Program Files\Amazon\MP3 Downloader\Uninstall.exe")