try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Raw Tiles',
    'author': 'Matt Amos',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'matt.amos@mapzen.com',
    'version': '0.1',
    'install_requires': [
        'nose',
        'psycopg2',
        'shapely',
        'msgpack-python',
        'boto3'
    ],
    'packages': ['raw_tiles'],
    'scripts': [],
    'name': 'raw_tiles',
    'test_suite': 'tests',
}

setup(**config)
