
import os

from pymlconf.config_nodes import ConfigDict
from pymlconf.yaml_helper import load_yaml
from pymlconf.compat import basestring
import logging

logging.basicConfig()
logger = logging.getLogger('pymlconf')

class ConfigManager(ConfigDict):
    """
    The main class which exposes pymlconf package.

    Example::

        from pymlconf import ConfigManager
        from os import path
        config =  ConfigManager('''
            server:
                host: localhost
                port: 4455
            ''','conf','builtins/defaults.conf')

        print config.server.host
        print config.server.port

    """
    
    default_extension = ".conf"    
    
    def __init__(self, init_value=None, dirs=None, files=None, filename_as_namespace=True,
                 extension='.conf',root_file_name='root'):
        """
        :param init_value: Initial configuration value that you can pass it before reading the files and directories.can be 'yaml string' or python dictionary.
        :type init_value: str or dict
        
        :param dirs: Python list  or a string that contains semi-colon separated list of directories which contains configuration files with specified extension(default \*.conf).
        :type dirs: str or list
        
        :param files: Python list  or a string that contains semi-colon separated list of files which contains yaml configuration entries.
        :type files: str or list
        
        :param filename_as_namespace: when loading dirs, use the filename as a namespace. default: true.
        :type filename_as_namespace: bool
        
        :param extension: File extension to search for configuration files, in dirs parameter, default '.conf'
        :type extension: str
        
        :param root_file_name: Filename to treat as root configuration file, so it loads first, and do not uses the filesname as namespaces.   
        :type root_file_name: str
        
        """
        super(ConfigManager,self).__init__(data=init_value)
        self.default_extension = extension
        self.root_file_name = root_file_name
        if dirs:
            if isinstance(dirs, basestring):
                dirs = [d.strip() for d in dirs.split(';')]
            self.load_dirs(dirs, filename_as_namespace=filename_as_namespace)
            
        if files:
            if isinstance(files, basestring):
                files = [f.strip() for f in files.split(';')]
            self.load_files(files)

    def load_files(self, files, filename_as_namespace=False):
        """
        load files which contains yaml configuration entries.and merge it by current ConfigManager instance
        
        :param files: files to load and merge into exisiting configuration instance
        :type files: list
        
        :param filename_as_namespace: when loading files, use the filename as a namespace. default: false.
        :type filename_as_namespace: bool
        
        """
        for f in files:
            if not os.path.exists(f):
                logger.warning('File not found: %s' % f)
                continue
            if filename_as_namespace:
                assert f.endswith(self.default_extension), 'Invalid configuration filename.expected: ns1.ns2.*%s' % self.default_extension
                namespace = os.path.splitext(os.path.split(f)[1])[0]
                if namespace == self.root_file_name:
                    node = self
                else:
                    node = self._ensure_namespaces(*namespace.split('.'))
            else:
                node = self
            node.merge(load_yaml(f))

    def load_dirs(self, dirs, filename_as_namespace=True):
        """
        load directories which contains configuration files with specified extension, and merge it by current ConfigManager instance
        
        :param dirs: Dirs to search for configuration files.
        :type dirs: list
        
        :param filename_as_namespace: when loading dirs, use the filename as a namespace. default: true.
        :type filename_as_namespace: bool
        
        """
        candidate_files = []
        for d in dirs:
            full_paths = (os.path.join(d, f) for f in os.listdir(d))
            conf_files = (f for f in full_paths if (os.path.isfile(f) or os.path.islink(f)) and f.endswith(self.default_extension))
            candidate_files.extend(sorted(conf_files))
            
        root_file_name = None
        for f in candidate_files:
            if f.endswith(self.root_file_name + self.default_extension):
                root_file_name = f
                break
                
        # remove and insert root.conf in index 0. 
        if root_file_name:
            candidate_files = [root_file_name] + [f for f in candidate_files if f != root_file_name]
            
        self.load_files(candidate_files, filename_as_namespace=filename_as_namespace)
