import click
from shutil import copyfile
from rattleSNP.global_variable import *


@click.command("edit_tools", short_help='Edit the tools version')
def edit_tools():
    if not RATTLESNP_USER_TOOLS_PATH.exists():
        RATTLESNP_USER_TOOLS_PATH.parent.mkdir(parents=True, exist_ok=True)
        copyfile(RATTLESNP_TOOLS_PATH, RATTLESNP_USER_TOOLS_PATH)
    click.edit(require_save=True, extension='.yaml', filename=RATTLESNP_USER_TOOLS_PATH)
    click.secho(f"\n    Success install own tools_path.yaml on path '{RATTLESNP_USER_TOOLS_PATH}'\n    CulebrONT used it at default now !!", fg="yellow")
