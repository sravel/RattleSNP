#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import setup, find_packages

NAME = "RattleSNP"
URL = "https://github.com/sravel/RattleSNP"
CURRENT_PATH = Path(__file__).resolve().parent
VERSION = CURRENT_PATH.joinpath("VERSION").open('r').readline().strip()

def main():
    setup(
        # Project information
        name=NAME,
        VERSION=VERSION,
        url=URL,
        project_urls={
            "Bug Tracker": f"{URL}/issues",
            "Documentation": f"https://{NAME}.readthedocs.io/en/latest/",
            "Source Code": URL
        },
        download_url=f"{URL}/archive/{VERSION}.tar.gz",
        author="Ravel Sebastien",
        description="",
        long_description=CURRENT_PATH.joinpath('README.md').open("r", encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        license='GPLv3',

        # docs compilation utils
        command_options={
            'build_sphinx': {
                'project': ('setup.py', NAME),
                'VERSION': ('setup.py', VERSION),
                'release': ('setup.py', VERSION),
                'source_dir': ('setup.py', CURRENT_PATH.joinpath("docs","source")),
                'build_dir': ('setup.py', CURRENT_PATH.joinpath("docs","build")),
            }},

        # Package information
        packages=find_packages(),
        package_data={
            'rattleSNP': ['*.ini'],
            'rattleSNP.fonts': ['*.ttf'],
            'rattleSNP.pictures': ['*/*.png'],
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
            'cookiecutter'
        ],
        extras_require={
            'docs': ['sphinx_copybutton',
                     'sphinx_rtd_theme',
                     'sphinx_click'],
        },
        entry_points={
            NAME: [NAME + " = __init__"],
            'console_scripts': ["rattleSNP = rattleSNP.run_rattleSNP:main",
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
