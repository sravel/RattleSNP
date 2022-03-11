#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .snakeWrapper import *
from .global_variables import *


logo = INSTALL_PATH.joinpath('RattleSNP_logo.png').as_posix()

__version__ = get_version()

__doc__ = """BLABLA"""

description_tools = f"""
    Welcome to RattleSNP version: {__version__}! Created on November 2019
    @author: Sebastien Ravel (CIRAD)
    @email: sebastien.ravel@cirad.fr
    
    #                       _.--....
    #              _....---;:'::' ^__/
    #            .' `'`___....---=-'`
    #           /::' (`
    #           \\\'   `:.                   `OooOOo.                    o        .oOOOo.  o.     O OooOOo.
    #            `\::.  ';-"":::-._  {{}}      o     `o                  O         o     o  Oo     o O     `O
    #         _.--'`\:' .'`-.`'`.' `{{I}}      O      O         O    O   o         O.       O O    O o      O
    #      .-' `' .;;`\::.   '. _: {{-I}}`\\\   o     .O        oOo  oOo  O          `OOoo.  O  o   o O     .o
    #    .'  .:.  `:: _):::  _;' `{{=I}}.:|    OOooOO'  .oOoO'  o    o   o  .oOo.        `O O   o  O oOooOO'
    #   /.  ::::`":::` ':'.-'`':. {{_I}}::/    o    o   O   o   O    O   O  OooO'         o o    O O o
    #   |:. ':'  :::::  .':'`:. `'|':|:'     O     O  o   O   o    o   o  O      O.    .O o     Oo O
    #    \:   .:. ''' .:| .:, _:./':.|       O      o `OoO'o  `oO  `oO Oo `OoO'   `oooO'  O     `o o'
    #     '--.:::...---'\:'.:`':`':./
    #                    '-::..:::-'
    
    Please cite our github: {GIT_URL}
    Licencied under CeCill-C (http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
    and GPLv3 Intellectual property belongs to IRD, CIRAD and authors.
    Documentation avail at: {DOCS}
    {get_last_version(url=GIT_URL, current_version=__version__)}"""


MODULE_FILE = f"""#%Module1.0
##

## Required internal variables
set     prefix       {INSTALL_PATH.as_posix().strip()}
set     version      {__version__.strip()}

# check if install directory exist
if {{![file exists $prefix]}} {{
    puts stderr "\t[module-info name] Load Error: $prefix does not exist"
    break
    exit 1
}}

## List conflicting modules here
conflict rattleSNP

## List prerequisite modules here
module load graphviz/2.40.1

set		fullname	CulebrONT-{__version__.strip()}
set		externalurl	"\n\t{DOCS.strip()}\n"
set		description	"\n\t{__doc__.strip()}

## Required for "module help ..."
proc ModulesHelp {{}} {{
  global description externalurl
  puts stderr "Description - $description"
  puts stderr "More Docs   - $externalurl"
}}

## Required for "module display ..." and SWDB
module-whatis   "loads the [module-info name] environment"

## Software-specific settings exported to user environment

prepend-path PATH $prefix

"""
