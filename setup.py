try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

config = {
    'description': 'Raw Tiles',
    'author': 'Matt Amos',
    'url': 'https://github.com/tilezen/raw_tiles',
    'download_url': 'https://github.com/tilezen/raw_tiles/releases',
    'author_email': 'zerebubuth@gmail.com',
    'version': '1.0',
    'install_requires': [
        'nose',
        'psycopg2',
        'shapely',
        'msgpack-python',
        'boto3'
    ],
    'include_package_data': True,
    'package_data': {'raw_tiles.source': ['*.sql']},
    'packages': find_packages(exclude=['ez_setup', 'examples', 'tests']),
    'scripts': [],
    'name': 'raw_tiles',
    'test_suite': 'tests',
    'entry_points': {
        'console_scripts': [
            'raw_tiles = raw_tiles.command:raw_tiles_main',
        ]
    },
}

setup(**config)
