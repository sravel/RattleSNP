#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from io import open
import os.path as osp
from setuptools import setup, find_packages


HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE)
import rattleSNP  # nopep8 : import shall be done after adding setup to paths


def main():
    setup(
        name=rattleSNP.__name__,
        version=rattleSNP.__version__,
        description=rattleSNP.__doc__,
        long_description=open(osp.join(HERE, 'README.md'), encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.9',
            'Natural Language :: English',
        ],
        author="Ravel Sebastien",
        url="https://github.com/sravel/RattleSNP",
        download_url="https://github.com/sravel/RattleSNP/archive/{}.tar.gz".format(rattleSNP.__version__),
        license='GPLv3',
        platforms=['unix', 'linux'],
        keywords=[
            'snakemake',
            'SNP calling',
            'workflow'
        ],
        packages=find_packages(),
        package_data={
            'rattleSNP': ['*.ini'],
            'rattleSNP.fonts': ['*.ttf'],
            'rattleSNP.pictures': ['*/*.png'],
        },
        include_package_data=True,
        python_requires=">=3.6",
        options={
            'bdist_wheel': {'universal': True}
        },
        zip_safe=False,  # Don't install the lib as an .egg zipfile
        entry_points={
            rattleSNP.__name__: [rattleSNP.__name__ + " = __init__"],
            'console_scripts'   : ["rattleSNP = rattleSNP.run_rattleSNP:main",
                                   "vcf2geno = rattleSNP.scripts.vcf2geno:main",
                                   "vcf2phylip = rattleSNP.scripts.vcf2phylip:main"]},
    )


if __name__ == '__main__':
    main()
