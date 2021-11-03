#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author Sebastien Ravel

##################################################
# Modules
##################################################
import os
from pathlib import Path
import argparse
from datetime import datetime
from pprint import pprint as pp

from script.toolbox import existant_file, welcome_args
from script.module import get_last_version, get_version
###################################

try:
    RATTLE_PATH = Path(os.environ["RATTLE"])
except KeyError:
    RATTLE_PATH = Path(__file__).resolve().parent
SNAKEFILE = RATTLE_PATH.joinpath("Snakefile")
version_RattleSNP = get_version(RATTLE_PATH)

##################################################
# build_parser function use with sphinxcontrib.autoprogram
##################################################
def build_parser():
    # Change the description HERE
    description_tools = f"""    Welcome to RattleSNP  !
    Created on November 2019
    version: """+version_RattleSNP+"""
    @author: Sebastien Ravel (CIRAD)
    @email: sebastien.ravel@cirad.fr

    #                       _.--....
    #              _....---;:'::' ^__/
    #            .' `'`___....---=-'`
    #           /::' (`
    #           \\'   `:.                   `OooOOo.                    o        .oOOOo.  o.     O OooOOo.
    #            `\::.  ';-"":::-._  {}      o     `o                  O         o     o  Oo     o O     `O
    #         _.--'`\:' .'`-.`'`.' `{I}      O      O         O    O   o         O.       O O    O o      O
    #      .-' `' .;;`\::.   '. _: {-I}`\\   o     .O        oOo  oOo  O          `OOoo.  O  o   o O     .o
    #    .'  .:.  `:: _):::  _;' `{=I}.:|    OOooOO'  .oOoO'  o    o   o  .oOo.        `O O   o  O oOooOO'
    #   /.  ::::`":::` ':'.-'`':. {_I}::/    o    o   O   o   O    O   O  OooO'         o o    O O o
    #   |:. ':'  :::::  .':'`:. `'|':|:'     O     O  o   O   o    o   o  O      O.    .O o     Oo O
    #    \:   .:. ''' .:| .:, _:./':.|       O      o `OoO'o  `oO  `oO Oo `OoO'   `oooO'  O     `o o'
    #     '--.:::...---'\:'.:`':`':./
    #                    '-::..:::-'

    Please cite our github https://github.com/sravel/RattleSNP
    Licencied under CeCill-C (http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
    and GPLv3 Intellectual property belongs to CIRAD and authors.
    """+get_last_version(version_RattleSNP)


    parser_mandatory = argparse.ArgumentParser(add_help=False)
    mandatory = parser_mandatory.add_argument_group('Input mandatory infos for running')

    # Write mandatory arguments HERE
    mandatory.add_argument('-c', '--config', metavar="path/to/file/config_file", type=existant_file, required=True,
                           dest='configfile', help='path to file params file')
    # END Write mandatory arguments HERE

    parser_other = argparse.ArgumentParser(
            parents=[parser_mandatory],
            add_help=False,
            prog=Path(__file__).name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=description_tools,
            epilog=get_last_version(version_RattleSNP)
    )

    optional = parser_other.add_argument_group('Input infos not mandatory')
    optional.add_argument('-v', '--version', action='version', version=version_RattleSNP,
                          help=f'Use if you want to know which version of {Path(__file__).name} you are using')
    optional.add_argument('-h', '--help', action='help', help=f'show this help message and exit')
    optional.add_argument('-d', '--debug', action='store_true', help='enter verbose/debug mode')

    # Write optional arguments HERE
    optional.add_argument('-n', '--dry_run', action='store_true', help='run with dry run mode')
    # optional.add_argument('-p', '--profile', action='store_true', help='run profile instead of cluster')
    # optional.add_argument('-p', '--profile', metavar="profile", type=str, required=False, default = None,
                           # dest='profile', help='path to file params file')


    # END Write optional arguments HERE

    return parser_other


@welcome_args(version_RattleSNP, build_parser())
def main():
    prog_args = build_parser().parse_args()
    # Main Code HERE
    # print(prog_args)
    cmd_snakemake = f"""snakemake -p -s {SNAKEFILE} -c1 --configfile {prog_args.configfile} --dry-run"""
    print(cmd_snakemake)
    os.system(cmd_snakemake)


if __name__ == '__main__':
    main()
