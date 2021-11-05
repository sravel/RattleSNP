#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from .module import get_last_version, get_version
from .run import run, runlocal
from .edit_tools import edit_tools
from .install import install

RATTLESNP_PATH = Path(__file__).resolve().parent.parent
RATTLESNP_SNAKEFILE = RATTLESNP_PATH.joinpath("Snakefile")
RATTLESNP_PROFILE = RATTLESNP_PATH.joinpath("IFB_profile")
RATTLESNP_TOOLS_PATH = RATTLESNP_PATH.joinpath("tools_path.yaml")

logo = RATTLESNP_PATH.joinpath('SupplementaryFiles/RattleSNP_logo.png').as_posix()

__version__ = get_version(RATTLESNP_PATH)

description_tools = f"""\b
    Welcome to RattleSNP !
    Created on November 2019
    version: """+__version__+"""
    @author: Sebastien Ravel (CIRAD)
    @email: sebastien.ravel@cirad.fr
    \b
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
    \b
    Please cite our github https://github.com/sravel/RattleSNP
    Licencied under CeCill-C (http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
    and GPLv3 Intellectual property belongs to CIRAD and authors.
    """+get_last_version(__version__)
