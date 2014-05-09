from os.path import join as pathjoin
from os.path import exists as pathexists
from os.path import dirname
from os.path import basename
from os import chmod

# import zc.buildout
from sys import platform

template = """#!%(executable)s
import subprocess
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-a", "--admin-user", dest="admin_user",
                    default="%(admin-user)s")
parser.add_argument("-p", "--profile", dest="profile", default='')
parser.add_argument("-u", "--update", dest="update", action='store_true')
parser.add_argument("-z", "--pack", dest="pack", action='store_true')
parser.add_argument("-i", "--install", dest="install", default='')

options = parser.parse_args()

args = []

args.append("--admin-user")
args.append(options.admin_user)

if options.profile != '':
    args.append("--profile")
    args.append(options.profile)

if options.update:
    args.append("--update")

if options.pack:
    args.append("--pack")

if options.install != '':
    args.append("--install")
    args.append(options.install)

%(zeo-start)s

instance_scripts = %(instance-scripts)s
instance_status = []

for instance in instance_scripts:
    if "program running" in subprocess.check_output([instance, "status"]):
        instance_status.append(True)
    else:
        instance_status.append(False)

if instance_status[0]:
    cmd = [instance_scripts[0], "stop"]
    subprocess.call(cmd)

cmd = [instance_scripts[0], "run", "%(script)s"]
cmd = cmd + args
subprocess.call(cmd)

for instance, status in zip(instance_scripts, instance_status):
    if status:
        cmd = [instance, "stop"]
        subprocess.call(cmd)
        cmd = [instance, "start"]
        subprocess.call(cmd)

%(zeo-stop)s
"""

zeo_start_template = """
zeostatus = False
if "program running" in subprocess.check_output(["%(zeo-script)s", "status"]):
    zeostatus = True

zeo_start = ["%(zeo-script)s", "start"]
zeo_stop = ["%(zeo-script)s", "stop"]

if not zeostatus:
    subprocess.call(zeo_start)
"""

zeo_stop_template = """
if not zeostatus:
    subprocess.call(zeo_stop)
"""


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.options['bin-directory'] = \
            self.buildout['buildout']['bin-directory']
        self.options['bin_dir'] = self.options['bin-directory']
        self.options.setdefault('admin-user', 'admin')
        self.options.setdefault('zeo_part', '')
        self.options.setdefault('zeo-start', '')
        self.options.setdefault('zeo-stop', '')

        python = buildout['buildout']['python']
        self.options['executable'] = buildout[python]['executable']

        self.options['script'] = pathjoin(dirname(__file__), 'ploneupdater.py')

        self.find_zeo_part()

        self.is_win = platform[:3].lower() == "win"

        self.set_instance_scipts()
        if self.options['zeo_part']:
            self.set_zeo_scipt()

    def find_zeo_part(self):
        zeo_recipes = ('plone.recipe.zeoserver', 'plone.recipe.zope2zeoserver')
        for id in self.buildout.keys():
            recipe = self.buildout[id].get('recipe', None)
            if recipe and recipe in zeo_recipes:
                self.options['zeo_part'] = id
                break

    def find_zope_parts(self):
        zope_recipes = ('plone.recipe.zope2instance')
        zope_parts = []
        for id in self.buildout.keys():
            recipe = self.buildout[id].get('recipe', None)
            if recipe and recipe in zope_recipes:
                zope_parts.append(id)
        return zope_parts

    def set_instance_scipts(self):
        zope_scripts = []
        for part in self.find_zope_parts():
            instance = self.buildout[part]
            instance_home = instance['location']
            instance_script = self.options['bin_dir'] + '/' + \
                              basename(instance_home)
            if self.is_win:
                instance_script = "%s.exe" % instance_script
            zope_scripts.append(instance_script)
        self.options['instance-scripts'] = "['" + "','".join(zope_scripts) + "']"

    def set_zeo_scipt(self):
        if self.is_win:
            if pathexists(pathjoin(self.options['bin-directory'],
                          'zeoservice.exe')):
                zeo_script = 'zeoservice.exe'
            else:
                zeo_script = "%s_service.exe" % self.options['zeo_part']
        else:
            zeo_home = self.buildout[self.options['zeo_part']]['location']
            zeo_script = self.options['bin_dir'] + '/' + basename(zeo_home)
        self.options['zeo-script'] = zeo_script
        self.options['zeo-start'] = zeo_start_template % self.options
        self.options['zeo-stop'] = zeo_stop_template % self.options

    def install(self):
        script_path = pathjoin(self.options['bin-directory'], self.name)
        open(script_path, 'w+').write(template % self.options)

        chmod(script_path, 0700)

        return tuple()

    def update(self):
        self.install()
