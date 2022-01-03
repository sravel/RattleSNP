#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from setuptools import setup, find_packages

NAME = "RattleSNP"
URL = "https://github.com/sravel/RattleSNP"
CURRENT_PATH = Path(__file__).resolve().parent
VERSION = CURRENT_PATH.joinpath("rattleSNP", "VERSION").open('r').readline().strip()


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        if path not in [".git", "docs", "rattleSNP", ".snakemake", "RattleSNP.egg-info", "data_test"]:
            for filename in filenames:
                paths.append(os.path.join('..', path, filename))
        return paths

extra_files = package_files(CURRENT_PATH.as_posix())

from pprint import pprint as pp

# pp(extra_files)
# exit()

def main():
    setup(
        # Project information
        name=NAME,
        version=VERSION,
        url=URL,
        project_urls={
            "Bug Tracker": f"{URL}/issues",
            "Documentation": f"https://{NAME}.readthedocs.io/en/latest/",
            "Source Code": URL
        },
        download_url=f"{URL}/archive/{VERSION}.tar.gz",
        author="Ravel Sebastien",
        author_email="sebastien.ravel@cirad.fr",
        description="",
        long_description=CURRENT_PATH.joinpath('README.rst').open("r", encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        license='GPLv3',

        # docs compilation utils
        command_options={
            'build_sphinx': {
                'project': ('setup.py', NAME),
                'version': ('setup.py', VERSION),
                'release': ('setup.py', VERSION),
                'source_dir': ('setup.py', CURRENT_PATH.joinpath("docs","source").as_posix()),
                'build_dir': ('setup.py', CURRENT_PATH.joinpath("docs","build").as_posix()),
            }},

        # Package information
        use_scm_version=True,
        setup_requires=['setuptools_scm'],
        packages=find_packages(),
        package_data={
            '': ['*'],
        },
        include_package_data=True,
        python_requires=">=3.6",
        install_requires=[
            'PyYAML',
            'pandas',
            'matplotlib',
            'tabulate',
            'rpy2',
            'ipython',
            'biopython',
            'pysam<=0.15.4',
            'pysamstats',
            'numpy',
            'argparse',
            'snakemake',
            'click>=8.0.3',
            'cookiecutter',
            'tqdm'
        ],
        extras_require={
            'docs': ['sphinx_copybutton',
                     'sphinx_rtd_theme',
                     'sphinx_click'],
        },
        entry_points={
            NAME: [NAME + " = __init__"],
            'console_scripts': ["rattleSNP = rattleSNP.main:main",
                                "vcf2geno = rattleSNP.scripts.vcf2geno:main",
                                "vcf2phylip = rattleSNP.scripts.vcf2phylip:main"]},

        # Pypi information
        platforms=['unix', 'linux'],
        keywords=[
            'snakemake',
            'SNP calling',
            'workflow'
        ],
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.9',
            'Natural Language :: English',
        ],
        options={
            'bdist_wheel': {'universal': True}
        },
        zip_safe=False,  # Don't install the lib as an .egg zipfile
    )


if __name__ == '__main__':
    main()
