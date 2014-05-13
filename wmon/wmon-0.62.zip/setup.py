from setuptools import setup
from setuptools import find_packages

setup(
    name = "wmon",
    version = "0.62",
    author = "Francisco Martinez",
    author_email = "fmartinez@pcpractico.es",
    description = ("This Script return a plain text report with a complete system info."),
    license = "BSD",
    keywords = "monitoring system",
    url = "https://github.com/pcpractico/Wmon",
    packages = find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
	install_requires = [
		'setuptools',
		'psutil',
	],
	entry_points= {
        'console_scripts': [
          'wmon = wmon.wmon:main',
        ],
	},
)