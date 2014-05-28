import argparse
import glob2
import os

def parse_args(args):
    """ return results of parsing the given args
    
        ie:  "-c *.py -c *.img -c *.png -nc temp.py -n counter.html form.html -f / fallback.html -f /form fallbackform.html
        returns
        Namespace(cache=[['*.py'], ['*.img'], ['*.png']], fallback=[['/', 'fallback.html '], ['/form', 'fallbackform.html']], network=[['counter.html', 'form.html']], no cache=[['temp.py']])
    
    
    
    """
    """
    htmlacmg -d ~/doc_root -u /static/m -c **.py -nc temp.py -n counter.html -f /  fallback.html 

    """
    parser = argparse.ArgumentParser(description='Generate HTML5 app cache manifest')
    parser.add_argument('-d','--doc_root', nargs='+', dest='doc_root', help='top-level of static file tree structure on disk')
    parser.add_argument('-u','--url', nargs='+', dest='url_prefix', help='url prefix to add to generated file names')
    parser.add_argument('-c','--cache', action='append', nargs='+', dest="cache", help="a glob2 file expression of files to add to the cache")
    parser.add_argument('-nc','--nocache', action='append', nargs='+', dest="nocache", help="a glob2 expression of files to exclude from caching")
    parser.add_argument('-n','--network', action='append', nargs='+', dest="network")
    parser.add_argument('-f','--fallback', action='append', nargs='+', dest="fallback")
    parser.add_argument('-o','--output', default='cache.manifest', help="the output cache manifest file")
    parser.add_argument('--force', action='store_true', default=False, help="force updating of the cache manifest file") #TODO: add a timestamp to the file to force browsers to update


    args = parser.parse_args(args)
    return args



def glob_list_of_arg_values(arg_values):
    "expand a list of of arg_values in the format [ ['.py'], ['zr*.img'] ] etc to the contained file names, ignoring directories"
    all_files = []
    if arg_values:
        for arg_set in arg_values:
            for glob_spec in arg_set:
                these_files = glob2.glob(glob_spec)
                for file_name in these_files:
                    if os.path.isfile(file_name):
                        all_files.append(file_name)
    return all_files


    





