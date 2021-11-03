#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author Sebastien Ravel

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
    import sys
    from pathlib import Path
    import argparse
    from datetime import datetime

    def welcome_args(func):
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
    return welcome_args

