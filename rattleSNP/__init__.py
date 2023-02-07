#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from .global_variables import GIT_URL, DOCS, DATATEST_URL_FILES, SINGULARITY_URL_FILES
from .snakemake_module import RattleSNP
from .snakemake_scripts.rattleSNP_module import *

logo = Path(__file__).parent.resolve().joinpath('RattleSNP_logo.png').as_posix()

__version__ = Path(__file__).parent.resolve().joinpath("VERSION").open("r").readline().strip()

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
    
    Please cite our github: GIT_URL
    Licencied under CeCill-C (http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
    and GPLv3 Intellectual property belongs to IRD, CIRAD and authors.
    Documentation avail at: DOCS"""

dico_tool = {
    "soft_path": Path(__file__).resolve().parent.as_posix(),
    "url": GIT_URL,
    "docs": DOCS,
    "description_tool": description_tools,
    "singularity_url_files": SINGULARITY_URL_FILES,
    "datatest_url_files": DATATEST_URL_FILES,
    "snakefile": Path(__file__).resolve().parent.joinpath("snakefiles", "Snakefile"),
    "snakemake_scripts": Path(__file__).resolve().parent.joinpath("snakemake_scripts")
}

