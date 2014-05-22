from distutils.core import setup
#from setuptools import setup #too create .egg

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
#files = ["icons/*"]

setup(name = "pyElphel",
    version = "0.1",
    description = "Use Elphel camera from python with opencv2",
    author = "CHAUVET Hugo",
    author_email = "chauvet@ipgp.fr",
    url = "https://github.com/hchauvet/pyElphel",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages = ['pyElphel', "pyElphel.test"],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    #package_data = {'pyElphel' : files },
    #'runner' is in the root.
    #scripts = ["pyElphel.py"],
    long_description = open('README', 'r').read(),
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []
    license='GPL',
    #install_requires=[
    #    'setuptools',
    #    'python-opencv'
    #],
    
     classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          "Intended Audience :: Science/Research",
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Video',
          'Topic :: Scientific/Engineering :: Visualization',
          ],
)

