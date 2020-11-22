# coding: utf-8

from setuptools import setup

import pictureshow

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pictureshow',
    version=pictureshow.__version__,
    author='Michal Porteš',
    author_email='michalportes1@gmail.com',
    description='Save pictures to PDF',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/myrmica-habilis/pictureshow.git',
    license='MIT License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['pictureshow'],
    install_requires=['reportlab'],
    python_requires='>=3.6',
    entry_points={'console_scripts': ['pictureshow=pictureshow.cli:main']},
)
