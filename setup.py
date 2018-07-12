import os
from setuptools import setup

setup(
    name="taki",
    version="1.0",
    author="AmirMohammad Dehghan",
    author_email="amirmd76@gmail.com",
    description="Taki Ahmagh Game",
    license="MIT",
    url="https://github.com/amirmd76/taki",
    packages=['taki'],
    entry_points={
        'console_scripts':['taki = taki.taki:main']
    },
    data_files=[],
    install_requires=[
              'pynput'
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Games/Entertainment :: Arcade",
        "Programming Language :: Python :: 3.6"
    ],
)
