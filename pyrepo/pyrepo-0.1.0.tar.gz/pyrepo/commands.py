# -*- coding: utf-8 -*-
"""
    This module defines Command, the representation of binary commands 
    used to fetch and manage repositories.
"""

import subprocess
import re


class TagCmd(object):
    """
    Represents a command to list available tags to sync to.
    """

    def __init__(self, cmd, pattern):
        """
        :param cmd: command to list tags
        :param pattern: regex to extract tags
        """
        self.cmd = cmd
        self.pattern = pattern


class Command(object):
    """
    Represents a version control system (such as Git, Mercurial, etc.) 
    and its usage.
    """

    def __init__(self, **kwargs):
        """
        Make a repository management command.

        :param name: name of the version control system
        :param cmd: name of binary for version control system command
        :param create_cmd: command to clone a fresh copy of a repo
        :param update_cmd: command to download updates into existing 
            repo
        :param tag_list_cmd: command to list tags
        :param tag_lookup_cmd: command to lookup tags
        :param tag_sync_cmd: command to sync to specific tag
        :param tag_sync_default_cmd: command to sync to default tag
        :param schemes: vcs scheme names
        :param ping_cmd: command to ping for scheme
        """
        self.name = kwargs["name"]
        self.long_name = kwargs["long_name"]
        self.create_cmd = kwargs["create_cmd"]
        self.update_cmd = kwargs["update_cmd"]
        self.tag_list_cmd = kwargs["tag_list_cmd"]
        self.tag_lookup_cmd = kwargs["tag_lookup_cmd"]
        self.tag_sync_cmd = kwargs["tag_sync_cmd"]
        self.tag_sync_default_cmd = kwargs["tag_sync_cmd"]
        self.schemes = kwargs["schemes"]
        self.ping_cmd = kwargs["ping_cmd"]

    def _run(self, cmdline, keyvals, cwd=None):
        """
        Runs the version control system binary with the `cmdline`
        command, interpolated with named `keyvals` dict.
        :params cmdline: command to be executed, e.g. "clone {r} {t}"
        :params keyvals: key-values for interpolation, e.g. 
        {"r": "repourl", "t": "/tmp"}
        :params cwd: directory to execute from, defaults to current dir
        :returns: (standard_out, standard_error)
        """
        cmdline = cmdline.format(**keyvals)
        # 0th argument should always be the name of the binary to execute
        args = [self.name] + cmdline.split()
        return subprocess.Popen(
            args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=cwd).communicate()

    def clone(self, repo_url, target):
        """
        Runs the command to clone/create a new repository.
        :params repi_url: url to remote repo or path to local repo
        :params target: path to intended destination for repo
        """
        return self._run(self.create_cmd, 
                         {"repo_url": repo_url, "target": target})

    def update(self, cwd=None):
        """
        Runs the command to update a repo, from the given `cwd`
        directory
        """
        return self._run(self.update_cmd, {})

    def tag_list(self, cwd=None):
        """
        Runs the command to list tags, from the given `cwd` directory.
        """
        (stdout, stderr) = self._run(self.tag_list_cmd.cmd, {}, cwd)
        tags = []
        for line in stdout.decode().split("\n"):
            match = re.search(self.tag_list_cmd.pattern, line)
            if match:
                group_dict = match.groupdict()
                tag = group_dict["tag"]
                if tag is not None: 
                    tags.append(tag)
        return tags
            
    def ping(self, scheme, repo, cwd="."):
        """
        ping
        """
        return self._run(self.ping_cmd, {"scheme": scheme, "repo": repo}, cwd)


git = Command(
    name="git",
    long_name="Git",
    create_cmd="clone {repo_url} {target}",
    update_cmd="pull --ff-only",
    tag_list_cmd=TagCmd("show-ref", 
                        re.compile('(?:tags|origin)/(?P<tag>\S+)$')),
    tag_lookup_cmd="show-ref tags/{tag} origin/{tag}",
    tag_sync_cmd="checkout {tag}",
    tag_sync_default_cmd="checkout master",
    schemes=["git", "https", "http", "git+ssh"],
    ping_cmd="ls-remote {scheme}://{repo_root}")


default_commands = [git]


# class VcsList(object):
#     """
#     Collection of known version control systems.
#     """
#     DEFAULT_LIST = [git]

#     def __init__(self, vcs_list=DEFAULT_LIST):
#         """
#         Make a VcsList.

#         :param vcs_list: a list of version control systems
#         """ 
#         self.vcs_list = vcs_list

#     def add(self, vcs_command):
#         """
#         Adds an additional version control system to the collection

#         :param vcs: a VcsCmd that should be added
#         """
#         self.vcs_list.append(vcs_command)

#     def get_by_name(self, name):
#         """
#         :returns: version control system with given name or None if no
#             matches are found
#         """
#         for vcs in self.vcs_list:
#             if vcs.name == name:
#                 return vcs
#         return None
        
#     def get_by_command(self, command):
#         """
#         :returns: version control system with given command or None if 
#             no matches are found
#         """
#         for vcs in self.vcs_list:
#             if vcs.cmd == command:
#                 return vcs
#         return None


