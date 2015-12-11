from setuptools import setup, find_packages

setup(
    name='ghostborders',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'click',
        'mysqlclient',
        'python-instagram',
        'shapely',
        'matplotlib',
        'python-igraph',
        'mercantile',
        'pillow'
    ],
    entry_points='''
        [console_scripts]
        ghostb=ghostb.ghostb:cli
    ''',
)
