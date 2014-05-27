from setuptools import setup, find_packages


setup(
    name='incuna-videos',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'FeinCMS>=1.7',
        'django-imagekit==3.2.1',
    ],
    version='2.0.0',
    description='Generic extensible video content.',
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-videos',
)
