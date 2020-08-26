from setuptools import setup, find_packages
from setuptools.extension import Extension

setup(
    name='dosiv',
    description='DosIVServer',
    zip_safe=False,
    entry_points={
        'console_scripts':[
            #Define console commands here
        ]
    },
    ext_modules=[
        #Extension("cExtentionFeed", sources = ["cExtentionFeed.cpp"])
    ]
)
