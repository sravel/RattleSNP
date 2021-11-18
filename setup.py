#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from io import open
import os.path as osp
from setuptools import setup, find_packages


HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE)
import rattleSNP  #no pep8 : import shall be done after adding setup to paths


def main():
    setup(
        # Project information
        name=rattleSNP.__name__,
        version=rattleSNP.__version__,
        url="https://github.com/sravel/RattleSNP",
        project_urls={
            "Bug Tracker": "https://github.com/sravel/RattleSNP/issues",
            "Documentation": "https://RattleSNP.readthedocs.io/en/latest/",
            "Source Code": "https://github.com/sravel/RattleSNP",
        },
        download_url="https://github.com/sravel/RattleSNP/archive/{}.tar.gz".format(rattleSNP.__version__),
        author="Ravel Sebastien",
        description=rattleSNP.__doc__,
        long_description=open(osp.join(HERE, 'README.md'), encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        license='GPLv3',

        # docs compilation utils
        command_options={
            'build_sphinx': {
                'project': ('setup.py', rattleSNP.__name__),
                'version': ('setup.py', rattleSNP.__version__),
                'release': ('setup.py', rattleSNP.__version__),
                'source_dir': ('setup.py', osp.join(HERE, r'docs', 'source')),
                'build_dir': ('setup.py', osp.join(HERE, r'docs', 'build')),
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
            rattleSNP.__name__: [rattleSNP.__name__ + " = __init__"],
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
