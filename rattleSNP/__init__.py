#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .module import get_last_version, get_version
from .run import run_cluster, runlocal
from .edit_tools import edit_tools
from .install import install_cluster
from .global_variable import *


logo = RATTLESNP_PATH.joinpath('SupplementaryFiles/RattleSNP_logo.png').as_posix()

__version__ = get_version(RATTLESNP_PATH)

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
    """+get_last_version()
