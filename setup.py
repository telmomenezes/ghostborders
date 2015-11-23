from setuptools import setup, find_packages

setup(
    name='phantomborders',
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
        'python-igraph'
    ],
    entry_points='''
        [console_scripts]
        phantomb=phantomb.phantomb:cli
    ''',
)
