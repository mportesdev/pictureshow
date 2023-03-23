# coding: utf-8

from setuptools import setup

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pictureshow',
    version='0.8.2',
    author='Michal Porteš',
    author_email='michalportes1@gmail.com',
    description='Save pictures to PDF.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/mportesdev/pictureshow',
    license='MIT License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['pictureshow'],
    install_requires=['Pillow==9.*', 'reportlab==3.*'],
    python_requires='>=3.7',
    entry_points={'console_scripts': ['pictureshow=pictureshow.cli:main']},
)
