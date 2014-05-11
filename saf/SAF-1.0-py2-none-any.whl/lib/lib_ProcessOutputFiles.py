'''
Created on Jul 22, 2013

@author: karthicm
'''
import os
import glob
import shutil

global global_run_folder
global_run_folder = ''

def FileExists (folder_path, file_name):
    # verify file exists
    All_files = []
    for each_file in file_name:
        PATH = folder_path + "\\" + each_file
        All_files_temp = glob.glob(PATH)
        if not All_files_temp:
            All_files.append(False)
        else:
            All_files.append(True)
    return All_files

def LatestVersion(folder_path, files):
    Latest = []
    All_files = []
    for each_file in files:
        PATH = folder_path + "\\" + each_file.split(".")[0] + "*." + each_file.split(".")[1]
        All_files_temp = glob.glob(PATH)
        Latest_temp = GetLatestFile(All_files_temp)
        All_files.append(All_files_temp)
        Latest.append(Latest_temp)
    return Latest

def GetLatestFile(files):
    LatestVersion = ""
    LastModTime = 0
    if not files:
        return False   # returning empty files
    for each in files:          # search for latest modified file of the list 
        Modtime = os.path.getmtime(each)
        if Modtime > LastModTime:
            LastModTime = Modtime
            LatestVersion = each
    return LatestVersion

def CreateFolder (folder_path):
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return folder_path
        else:
            return folder_path
    except Exception, E:
        return E

def RenameFile(folder_path, filename_old, filename_new):
    filename_old_path = folder_path+"\\"+ filename_old
    filename_new_path = folder_path+"\\"+ filename_new
    newnames = []
    for fname in glob.glob(filename_old_path):
        fname_new = filename_new_path
        os.rename(fname, fname_new)
        newnames.append(fname_new)
    return newnames
    
def MoveFiles(source_path, dest_path, OutputFileNames=[]):
    try:
        l = len(OutputFileNames)
        #print "length: %s" % l
        source_file_paths = glob.glob(source_path+"\*.*")
        new_path = dest_path
        for fname in source_file_paths:
            fname_temp= fname.split("\\")[-1]
            if l > 0:
                if not fname_temp in OutputFileNames:
                    continue
            shutil.move(source_path+"\\"+fname_temp, new_path+"\\"+fname_temp)
        return True
    except Exception, e:
        print e
        return False

def CreateRunFolder (folder_path):
    count = 1
    local_run_directory = folder_path+"/Run"
    path = local_run_directory + "*"
    LatestTime = 0
    LatestFolder = local_run_directory
    length = len(local_run_directory)
    AllFolders = glob.glob(path)
    global global_run_folder
    local_variable_type = type(global_run_folder)
    #print AllFolders
    if not local_variable_type is bool:
        if not AllFolders: #check if there are any Run folders. If not create new one
            local_run_folder_status = CreateFolder (local_run_directory + str(count))
            local_screenshot_directory = local_run_folder_status + "/screenshots"
            CreateFolder(local_screenshot_directory)
            global_run_folder = True
            return local_run_folder_status
        #If Run folders already present, create a new Run folder
        for each in AllFolders:
            LatestTime_temp = os.path.getctime(each)  
            if LatestTime_temp > LatestTime:
                LatestTime = LatestTime_temp
                LatestFolder = each
        if LatestFolder[length:]:
            Folder_count = int(LatestFolder[length:])+1
        else:
            Folder_count = 1
        local_outputfile = LatestFolder+'\output.xml'
        if len(os.listdir(LatestFolder)) >2 or os.path.isfile(local_outputfile)==True:
            local_run_folder_status = CreateFolder (local_run_directory + str(Folder_count))
            local_screenshot_directory = local_run_folder_status + "/screenshots"
            CreateFolder(local_screenshot_directory)
            global_run_folder = True
            return local_run_folder_status
        else:
            local_run_folder_status = LatestFolder
            global_run_folder = True 
            return local_run_folder_status
    else:
        for each in AllFolders:
            LatestTime_temp = os.path.getctime(each)  
            if LatestTime_temp > LatestTime:
                LatestTime = LatestTime_temp
                LatestFolder = each
        local_run_folder_status = LatestFolder
        return local_run_folder_status
"""
def process_outputfiles(TEST_DIRECTORY='C:\SAF\OutputData\Reports'):
    '''
    *********************************************************************
    Keyword Name    :Process_OutputFiles
    Usage           :Process_OutputFiles is used to process the output files to the proper Run folders with datetime stamps.
    ToDo            :NIL
    =====================================================================
    Created By          :Karthick Mani
    Created Date        :07/23/2013
    Last Modified By    :
    Last Modified Date  :
    *********************************************************************
    '''
    try:
        DestinationFolder_Path = lib_Operations_Common.get_current_result_directory()
        onlyfiles = [ f for f in listdir(TEST_DIRECTORY) if isfile(join(TEST_DIRECTORY,f))]
        Output_FileNames = []
        for files in onlyfiles:
            if not files in framework_constants.OUTPUT_FILE_TYPES:
                continue
            filename_old = files.split("\\")[-1]
            DateTime = lib_Operations_Common.return_datetimestring()
            filenametemp = filename_old.split('.')
            filename_new = filenametemp[0]+"_"+DateTime+"."+filenametemp[1]
            RenameFile(TEST_DIRECTORY, filename_old, filename_new)
            Output_FileNames.append(filename_new)
        MoveFiles(TEST_DIRECTORY,DestinationFolder_Path,Output_FileNames)
    except Exception as ex:
        if ex:
            print 'Exception error is: %s' % ex


"""