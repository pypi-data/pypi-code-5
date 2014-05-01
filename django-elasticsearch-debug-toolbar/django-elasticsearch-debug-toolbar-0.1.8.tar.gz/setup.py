from setuptools import setup, find_packages

with open('README.rst') as file_to_read:
    long_description = file_to_read.read()

setup(
    name='django-elasticsearch-debug-toolbar',
    version='0.1.8',
    description='A Django Debug Toolbar panel for Elasticsearch',
    long_description=long_description,
    author='Benoit Chabord',
    author_email='benauf@gmail.com',
    url='http://github.com/Benoss/elasticsearch-django-debug-toolbar',
    license='MIT',
    packages=find_packages(),
    provides=['elastic_toolbar'],
    install_requires=[
        'django-debug-toolbar>=1.2',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
