import click
from shutil import copyfile
from rattleSNP.global_variable import *


@click.command("edit_tools", short_help='Edit the tools version')
def edit_tools():
    """Edit the tools_config.yaml file to change tools version"""
    if not RATTLESNP_USER_TOOLS_PATH.exists():
        RATTLESNP_USER_TOOLS_PATH.parent.mkdir(parents=True, exist_ok=True)
        copyfile(RATTLESNP_TOOLS_PATH, RATTLESNP_USER_TOOLS_PATH)
    click.edit(require_save=True, extension='.yaml', filename=RATTLESNP_USER_TOOLS_PATH)
    click.secho(f"\n    Success install own tools_path.yaml on path '{RATTLESNP_USER_TOOLS_PATH}'\n    CulebrONT used it at default now !!", fg="yellow")


@click.command("create_config", short_help='create config.yaml for run')
@click.option('--configyaml', '-c', default=None,
              type=click.Path(exists=False, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
              required=True, show_default=True, help='Path to create config.yaml')
def create_config(configyaml):
    configyaml = Path(configyaml)
    configyaml.parent.mkdir(parents=True, exist_ok=True)
    copyfile(RATTLESNP_CONFIG_PATH.as_posix(), configyaml.as_posix())
    click.edit(require_save=True, extension='.yaml', filename=configyaml)
    click.secho(f"\n    Success create config file on path '{configyaml}'\n    RattleSNP can be run !!", fg="yellow")
