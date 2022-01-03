#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .run import run_cluster
from .edit_files import edit_tools, create_config, create_cluster_config
from .install import install_cluster
from .usefull_function import get_version, get_last_version
from .global_variable import *


logo = RATTLESNP_PATH.joinpath('RattleSNP_logo.png').as_posix()
url = "https://github.com/sravel/RattleSNP"

__version__ = get_version()

__doc__ = """BLABLA"""

description_tools = f"""
    Welcome to RattleSNP version: """+__version__+"""! Created on November 2019
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
    Documentation avail at: https://RattleSNP.readthedocs.io/en/latest/ 
    """+get_last_version(url=url, current_version=__version__)


MODULE_FILE = """
#%Module1.0
##

## Required internal variables
set     prefix       """+RATTLESNP_PATH.as_posix()+"""
set     version      """+__version__+"""

# check if install directory exist
if {![file exists $prefix]} {
    puts stderr "\t[module-info name] Load Error: $prefix does not exist"
    break
    exit 1
}

## List conflicting modules here
conflict RattleSNP

## List prerequisite modules here
module load graphviz/2.40.1
module load r/4.1.0

set		fullname	RattleSNP-"""+__version__+"""
set		externalurl	"\n\t"""+url+"""\n"
set		description	"\n\t"""+__doc__+""""

## Required for "module help ..."
proc ModulesHelp { } {
  global description externalurl
  puts stderr "Description - $description"
  puts stderr "More Docs   - $externalurl"
}

## Required for "module display ..." and SWDB
module-whatis   "loads the [module-info name] environment"

## Software-specific settings exported to user environment

prepend-path PATH $prefix

"""
