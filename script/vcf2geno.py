#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author Pierre Gladieux
# @author Sebastien Ravel

version = "0.0.1"
##################################################
# Modules
##################################################
import sys
import gzip
import argparse
from datetime import datetime
from pathlib import PosixPath, Path


##################################################
# Functions
def welcome_args(version_arg, parser_arg):
    """
    use this Decorator to add information to scripts with arguments

    Args:
        version_arg: the program version
        parser_arg: the function which return :class:`argparse.ArgumentParser`

    Returns:
        None:

    Notes:
        use at main() decorator for script with :class:`argparse.ArgumentParser`

    Examples:
        >>> from yoda_powers.toolbox import welcome_args
        >>> @welcome_args(version, build_parser())
        >>> def main():
        >>>     # some code
        >>> main()
        >>> ################################################################################
        >>> #                             prog_name and version                            #
        >>> ################################################################################
        >>> Start time: 16-09-2020 at 14:39:02
        >>> Commande line run: ./filter_mummer.py -l mummer/GUY0011.pp1.fasta.PH0014.pp1.fasta.mum
        >>>
        >>> - Intput Info:
        >>>         - debug: False
        >>>         - plot: False
        >>>         - scaff_min: 1000000
        >>>         - fragments_min: 5000
        >>>         - csv_file: blabla
        >>> PROGRAMME CODE HERE
        >>> Stop time: 16-09-2020 at 14:39:02       Run time: 0:00:00.139732
        >>> ################################################################################
        >>> #                               End of execution                               #
        >>> ################################################################################

    """
    def welcome(func):
        def wrapper():
            start_time = datetime.now()
            parser = parser_arg
            version = version_arg
            parse_args = parser.parse_args()
            # Welcome message
            print(
                    f"""{"#" * 80}\n#{Path(parser.prog).stem + " " + version:^78}#\n{"#" * 80}\nStart time: {start_time:%d-%m-%Y at %H:%M:%S}\nCommande line run: {" ".join(sys.argv)}\n""")
            # resume to user
            print(" - Intput Info:")
            for k, v in vars(parse_args).items():
                print(f"\t - {k}: {v}")
            print("\n")
            func()
            print(
                    f"""\nStop time: {datetime.now():%d-%m-%Y at %H:%M:%S}\tRun time: {datetime.now() - start_time}\n{"#" * 80}\n#{'End of execution':^78}#\n{"#" * 80}""")
        return wrapper
    return welcome

def existant_file(path):
    """
    'Type' for argparse - checks that file exists and return the absolute path as PosixPath() with pathlib

    Notes:
        function need modules:

        - pathlib
        - argparse


    Arguments:
        path (str): a path to existent file

    Returns:
        :class:`PosixPath`: ``Path(path).resolve()``

    Raises:
         ArgumentTypeError: If file `path` does not exist.
         ArgumentTypeError: If `path` is not a valid file.

    Examples:
        >>> import argparse
        >>> parser = argparse.ArgumentParser(prog='test.py', description='''This is demo''')
        >>> parser.add_argument('-f', '--file', metavar="<path/to/file>",type=existant_file, required=True,
            dest='path_file', help='path to file')

    """
    from argparse import ArgumentTypeError
    from pathlib import Path

    if not Path(path).exists():
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise ArgumentTypeError(f'ERROR: file "{path}" does not exist')
    elif not Path(path).is_file():
        raise ArgumentTypeError(f'ERROR: "{path}" is not a valid file')

    return Path(path).resolve()


##################################################
# build_parser function use with sphinxcontrib.autoprogram
##################################################
def build_parser():
    # Change the description HERE
    epilog_tools = """Documentation avail at: https://yoda-powers.readthedocs.io/en/latest/ \n\n"""
    description_tools = f"""
    More information:
        Script version: {version}
    """
    parser_mandatory = argparse.ArgumentParser(add_help=False)
    mandatory = parser_mandatory.add_argument_group('Input mandatory infos for running')

    # Write mandatory arguments HERE
    mandatory.add_argument('-vcf', '--vcf', metavar="path/to/file/vcf", type=existant_file, required=True,
                           dest='vcf_file', help='path to vcf(.gz) file (can be gzip)')
    # END Write mandatory arguments HERE

    parser_other = argparse.ArgumentParser(
            parents=[parser_mandatory],
            add_help=False,
            prog=Path(__file__).name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=description_tools,
            epilog=epilog_tools
    )

    optional = parser_other.add_argument_group('Input infos not mandatory')
    optional.add_argument('-v', '--version', action='version', version=version,
                          help=f'Use if you want to know which version of {Path(__file__).name} you are using')
    optional.add_argument('-h', '--help', action='help', help=f'show this help message and exit')
    optional.add_argument('-d', '--debug', action='store_true', help='enter verbose/debug mode')

    # Write optional arguments HERE
    optional.add_argument('-g', '--geno', metavar="path/to/file/geno", type=str, default="", dest='geno_file',
                          help='Name of output geno file (default = same as vcf)')

    return parser_other


def default_name(toto=None):

    geno_file = toto
    if build_parser().parse_known_args()[0].vcf_file.suffix == ".gz":
        if not geno_file:
            geno_file = build_parser().parse_known_args()[0].vcf_file.as_posix().replace(".vcf.gz",".geno")
    else:
        if not geno_file:
            geno_file = build_parser().parse_known_args()[0].vcf_file.as_posix().replace(".vcf", ".geno")
    return geno_file


@welcome_args(version, build_parser())
def main():
    prog_args = build_parser().parse_args()
    # Main Code HERE
    geno_file = prog_args.geno_file
    genotypes = {}
    index2isolate = {}
    if prog_args.vcf_file.suffix == ".gz":
        open_fn = gzip.open
        if not geno_file:
            geno_file = prog_args.vcf_file.as_posix().replace(".vcf.gz",".geno")
    else:
        open_fn = open
        if not geno_file:
            geno_file = prog_args.vcf_file.as_posix().replace(".vcf", ".geno")
    with open_fn(prog_args.vcf_file, "rt") as VCF, open(geno_file, 'w') as GENO:
        for line in VCF:
            items = line.strip().split()
            if line.startswith('#CHR'):
                for i in range(9, len(items)):
                    index2isolate[i] = items[i]
                print(f"vcf file contain {len(index2isolate)} samples")
            elif not line.startswith('#') and 'INDEL' not in line and ',' not in items[4]:
                for i in range(9, len(items)):
                    if index2isolate[i] not in genotypes:
                        genotypes[index2isolate[i]] = []
                    if items[i].split(':')[0] == '0':
                        allele = '1'
                    elif items[i].split(':')[0] == '1':
                        allele = '0'
                    elif items[i].split(':')[0] == ".":
                        allele = '9'
                    else:
                        print(items[i].split(':')[0])
                        allele = '9'
                    genotypes[index2isolate[i]].append(allele)
        for g in range(len(genotypes[list(genotypes.keys())[0]])):
            GENO.write(''.join([genotypes[isolate][g] for isolate in sorted(list(genotypes.keys()))]) + '\n')
        # for isolate in sorted(list(genotypes.keys())):
        #     print(isolate)


if __name__ == '__main__':
    main()
