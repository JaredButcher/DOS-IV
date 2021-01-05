from setuptools import setup, find_packages
from setuptools.extension import Extension

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='gamesite',
    description='gamesite and gameserver',
    zip_safe=False,
    entry_points={
        'console_scripts':[
            'gamesite = gamesite.flaskApp:run',
            'gameserver = gameserver.main:main'
        ]
    },
    py_modules=['gamesite', 'gameserver'],
    ext_modules=[
        #Extension("cExtentionFeed", sources = ["cExtentionFeed.cpp"])
    ],
    install_requires=requirements
)
