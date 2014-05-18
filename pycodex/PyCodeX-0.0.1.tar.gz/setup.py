from setuptools import setup

conf = {
    'name' : 'PyCodeX',
    'version' : '0.0.1',
    'description' : 'CodeX Python Libraries',
    'author' : 'Anthony De Leon',
    'author_email' : 'tonton.dev001@gmail.com',
    'url' : 'https://github.com/tontonskie/pycodex',
    'packages' : [
        'codex', 
        'codex.tornado'
    ],
    'package_dir' : {
        'codex' : 'codex',
        'codex.tornado' : 'codex/tornado'
    },
    'install_requires' : [
        'wtforms == 1.0.5',
        'pymongo == 2.7',
        'sqlalchemy == 0.9.3',
        'pytz == 2014.2',
        'tornado == 3.2.1',
        'pymysql == 0.6.2'
    ]
}

setup(**conf)