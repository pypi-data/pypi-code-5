#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import glob
import numpy
import scipy.io
import tempfile
import subprocess

# Trait import
try:
    from traits.trait_base import _Undefined
    from traits.api import (Bool, Directory, Undefined, List, Str, Enum)
except ImportError:
    from enthought.traits.api import (Bool, Directory, Undefined, List, Str,
                                      Enum)

# Capsul import
from capsul.process import Process


class ConnProcess(Process):
    """ Base class to wrap conn interface.

    jobname : str : the conn module prefix

    Attributes
    ----------
    parameters
    batch
    header
    footer
    mlabcmdline

    Methods
    -------
    run
    _to_conn_value
    _generate_script
    _get_script_header
    _get_script_footer
    _get_batch
    _get_parameters
    _save_conn_parameters
    _get_matlab_command_line
    """

    def __init__(self, *args, **kwargs):
        """ Initialize the ConnProcess class.
        """

        # Inheritance
        super(ConnProcess, self).__init__(*args, **kwargs)

        # Process parameters
        self.add_trait("exit", Bool(
            False, #True
            optional=True,
            desc="if True, quit matlab after calling the CONN script"))
        self.add_trait("generate_mfile", Bool(
            True,
            optional=True,
            desc="generate the m-file during the execution"))
        self.add_trait("execute_mfile", Bool(
            False,
            optional=True,
            desc="if set to False, only generate the batch"))
        self.add_trait("matlab_paths", List(Directory(),
            optional=True,
            desc="paths to add to matlabpath"))
        self.add_trait("matlab_cmd", Str(
            "matlab",
            optional=True,
            desc="matlab command to use"))
        self.add_trait("batch_header", List(Str(),
            optional=True,
            desc="another batch to use"))

        # Output trait
        self.add_trait("output_directory", Directory(
            Undefined,
            exists=True,
            optional=False))
        self.add_trait("mat_filename", Str(
            "conn_study.mat",
            optional=True,
            desc="the output conn structure filename"))

        # Process outputs
        self.add_trait("conn_batch", List(Str(),
            output=True,
            desc="the generated conn batch"))

    ##############
    # Methods    #
    ##############

    def run(self):
        """ Method to execute the conn script

        Returns
        -------
        runtime: tuple
            tuple that contains the returncode, the stdout and stderr
        """
        # Get the con script
        script = self.header
        self.conn_batch = self.batch
        self.conn_batch.insert(0, "    batch.filename = '{0}';".format(
            os.path.join(self.output_directory, self.mat_filename)))
        self.conn_batch.insert(0, "    clear batch;")
        script.extend(self.conn_batch)
        script.append("    conn_batch(batch);")
        script.extend(self.footer)
        if self.exit:
            script.append("exit();")
        mscript = "\n".join(script)
        runtime = (0, None, None)

        # Write m-code in a tmp file
        if not self.generate_mfile:
            fd, self.mfile = tempfile.mkstemp(suffix=".m")
            os.write(fd, mscript)
            os.close(fd)
        # Write m-code in the output directory
        else:
            self.mfile = os.path.join(self.output_directory,
                 "pyconn_batch_{0}.m".format(self.jobname))
            f = open(self.mfile, "w")
            f.write(mscript)
            f.close()

        # Execute conn batch
        if self.execute_mfile:
            try:
                process = subprocess.Popen(self.mlabcmdline,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
            except:
                raise Exception("Matlab probably not installed on your "
                                "system.")   # TODO correct bug: when not connected to server, does not raise this exception

            print stdout
            print stderr

            runtime = (process.returncode, stdout, stderr)
        else:
            runtime = (None, None, None)

        # Delete tmp file
        if not self.generate_mfile:
            os.remove(self.mfile)

        return runtime

    def _to_conn_value(self, obj):
        """ Convert a Python object to a string which can be parsed by Conn.
        Supported Python object are:
        * Case1: numpy.ndarray of dimensions 1 and 2 : converted to a matrix
        * Case2: list : converted to a cell array
        * Case2: string and scalar types : converted to litterals

        Parameters
        ----------
        obj: object
            a Python object

        Returns
        -------
        result: str
            the Conn string representation of the Python object
        """
        result = ""
        # Case 1
        if isinstance(obj, numpy.ndarray):
            normalized = obj
            if obj.shape[0] == 1:
                normalized = obj.squeeze()
            if normalized.ndim == 1:
                result = str(normalized.tolist())
            elif normalized.ndim == 2:
                result += "[ "
                for row in normalized.tolist():
                    result += str(row)[1: -1] + "\n"
                result = result[:-1]
                result += " ]"
            else:
                raise Exception("Cannot convert a numpy.ndarray of "
                                "dimension {0}".format(normalized.ndim))
        # Case 2
        elif isinstance(obj, list):
            result = "{{ {0} }}".format(", ".join(self._to_conn_value(x)
                                                   for x in obj))
        # Case 3
        elif isinstance(obj, basestring):
            result = "'{0}'".format(obj)
        # Case 1
        elif numpy.isscalar(obj):
            if numpy.isnan(obj):
                result = "[]"
            else:
                result = "{0}".format(obj)
        else:
            raise Exception("Cannot convert an object of type "
                            "{0}".format(repr(type(obj).__name__)))
        return result

    def _generate_script(self, prefix, parameters):
        """ Recursively generates the Conn script.

        Returns
        -------
        script: list of str
            each row of the list is a configuration item of the conn module
        """
        script = []
        if isinstance(parameters, dict):
            for key, python_obj in parameters.items():
                script.extend(
                    self._generate_script("{0}.{1}".format(prefix, key),
                                          python_obj))
        else:
            script.append("{0} = {1}".format(prefix,
                          self._to_conn_value(parameters)))

        return script
    
    ##############
    # Properties #
    ##############

    def _get_script_header(self):
        """ Method to access the conn script header: paths + check
        """
        script_check = """
        %% Check rule
        if isempty(which('{0}'));
        throw(MException('ToolCheck:NotFound', '{0} not in matlab path'));
        end;
        fprintf(1, '%s\\n', which('{0}'));
        """
        script_header = [
            "fprintf(1,'Executing %s at %s:\\n',mfilename,datestr(now));",
            "ver,",
            "",
            "try,"]
        this_dir = os.path.abspath(os.path.dirname(__file__))
        conn_dir = os.path.join(this_dir, "conn")
        matlab_paths = self.matlab_paths
        if not conn_dir in matlab_paths:
            matlab_paths.append(conn_dir)
        script_header.extend(["    addpath('{0}');".format(matlab_path)
                         for matlab_path in matlab_paths])
        script_header.extend([script_check.format(tool)
                              for tool in ["spm", "conn"]])
        return script_header

    def _get_script_footer(self):
        """ Method to access the conn script footer
        """
        script_footer = [
            "",
            ",catch ME,",
            "    fprintf(2,'MATLAB code threw an exception:\\n');",
            "    fprintf(2,'%s\\n',ME.message);",
            ("    if length(ME.stack) ~= 0, fprintf(2,'File:%s\\nName:%s\\n"
            "Line:%d\\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;"),
             "end;"
        ]
        return script_footer

    def _get_batch(self):
        """ Method to get the conn batch
        """
        script = self.batch_header
        script.extend(["    {0}.{1};".format("batch", statement)
            for statement in self._generate_script(self.jobname,
                                                   self.parameters)])
        return script

    def _get_parameters(self):
        """Method to access the configuration parameters.

        Returns
        -------
        parameters: dict
            a dictionary with the conn module configuration items.
        """
        setup_dict = {}
        # Go through all user input traits
        for trait_name, trait in self.user_traits().iteritems():
            trait_value = getattr(self, trait_name)
            trait_default = trait.handler.default_value
            if (not trait.output and trait.field and
                (isinstance(trait.handler, Enum) or
                 trait_value != trait_default)):
                # Get the trait value
                trait_value = getattr(self, trait_name)
                # Get the Conn module parameter description
                conn_module = trait.field
                # Create a dict from the conn mdule description
                if "." in conn_module:
                    # Complex structure
                    split_name = conn_module.split(".")
                    current_dict = setup_dict
                    while split_name:
                        current_key = split_name[0]
                        split_name.remove(current_key)
                        if not current_key in current_dict:
                            if split_name:
                                current_dict[current_key] = {}
                            else:
                                current_dict[current_key] = trait_value
                        current_dict = current_dict[current_key]
                else:
                    # Simple structure
                    setup_dict[conn_module] = trait_value
        return setup_dict

    def _save_conn_parameters(self):
        """ Method to save the conn configuration parameters in a .mat file

        Returns
        -------
        matfile: str
            the destination .mat file that contains the configuration
            parameters
        """
        mat_file = os.path.join(self.output_directory,
                                     "input_CONN.mat")
        scipy.io.savemat(mat_file, self.parameters)
        return mat_file
        
    def _load_conn_parameters(self, matfile):
        """ Method to load the conn parameters from a .mat file

        Parameters
        -------
        matfile: str
            the .mat file that contains the parameters we want to read
            
        Returns
        -------
        parameters: dict
            the loaded parameters
        """
        return scipy.io.loadmat(matfile, squeeze_me=True)

    def _get_matlab_command_line(self):
        """ Method that return the matlab commandline to execute the conn
        method.

        Returns
        -------
        commandline: list of str
            the command line to execute with subprocess
        """
        #commandline = [self.matlab_cmd, "-nodisplay", "-nosplash",
        #               "-nojvm", "-r", "run('{0}');".format(self.mfile)]
        commandline = ["xterm", "-e", self.matlab_cmd, "-nodisplay", "-nosplash",
                       "-nojvm", "-r", "run('{0}');".format(self.mfile)]
        return commandline

    parameters = property(_get_parameters)
    batch = property(_get_batch)
    header = property(_get_script_header)
    footer = property(_get_script_footer)
    mlabcmdline = property(_get_matlab_command_line)


def join_functionals(paths, runs):
    functionals = [[glob.glob(os.path.join(path, run)) for run in runs] for
    path in paths]
    return functionals


def join_covariates(paths, prefixes):
    covariates = [[[glob.glob(os.path.join(path, prefix))[0] for prefix in
    sessions] for path in paths] for sessions in prefixes]
    return covariates


def join_anatomicals(paths, prefix):
    anats = [glob.glob(os.path.join(path, prefix)) for path in paths]
    anatomicals = [anat for sublist in
    anats for anat in sublist]
    return anatomicals
