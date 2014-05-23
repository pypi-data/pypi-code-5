from setuptools import setup
from setuptools import find_packages
from wmon import wmonversion
setup(
    name = "wmon",
    version = wmonversion,
    author = "Francisco Martinez",
    author_email = "fmartinez@pcpractico.es",
    description = ("This Script return a plain text report with a complete system info."),
    long_description=open('README.rst').read(),
    license = "BSD",
    keywords = "monitoring system",
    url = "https://github.com/pcpractico/Wmon",
    packages = find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
        "Topic :: Utilities",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft",
        "Operating System :: Microsoft :: Windows :: Windows NT/2000",
		"Operating System :: Microsoft :: Windows :: Windows Server 2003",
		"Operating System :: Microsoft :: Windows :: Windows Server 2008",
    ],
	install_requires = [
		'setuptools',
		'psutil',
	],
	entry_points= {
        'console_scripts': [
          'wmon = wmon.wmon:mainwmon',
        ],
	},
)