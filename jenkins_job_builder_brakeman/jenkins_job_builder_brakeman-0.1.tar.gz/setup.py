from setuptools import setup, find_packages

setup(name='jenkins_job_builder_brakeman',
    version='0.1',
    description='A jenkins job builder plugin to allow enabling Brakeman',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Topic :: System :: Systems Administration',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    keywords='jenkins, brakeman',
    url='http://github.com/garethr/jenkins-job-builder-brakeman',
    author='Gareth Rushgrove',
    author_email='gareth@morethanseven.net',
    license = "OSI",
    packages=find_packages(),
    install_requires=["jenkins-job-builder>=0.6.0"],
    entry_points={
        'jenkins_jobs.publishers': [
            'brakeman=jenkins_job_builder_brakeman.modules.publishers:brakeman',
        ],
    }
)
