import click
from shutil import copyfile
from rattleSNP.global_variable import *


@click.command("edit_tools", short_help='Edit own tools version', no_args_is_help=False)
@click.option('--restore', '-r', is_flag=True, required=False, default=False, show_default=True, help='Restore default tools_config.yaml (from install)')
def edit_tools(restore):
    if restore:
        if RATTLESNP_USER_TOOLS_PATH.exists():
            RATTLESNP_USER_TOOLS_PATH.unlink()
            click.secho(f"\n    Success remove your own tools_path.yaml on path '{RATTLESNP_USER_TOOLS_PATH}'\n    RattleSNP used '{RATTLESNP_TOOLS_PATH}' at default now !!", fg="yellow")
    else:
        if not RATTLESNP_USER_TOOLS_PATH.exists():
            RATTLESNP_USER_TOOLS_PATH.parent.mkdir(parents=True, exist_ok=True)
            copyfile(RATTLESNP_TOOLS_PATH, RATTLESNP_USER_TOOLS_PATH)
        click.edit(require_save=True, extension='.yaml', filename=RATTLESNP_USER_TOOLS_PATH)
        click.secho(f"\n    Success install your own tools_path.yaml on path '{RATTLESNP_USER_TOOLS_PATH}'\n    RattleSNP used it at default now !!", fg="yellow")


@click.command("create_config", short_help='create config.yaml for run', no_args_is_help=True)
@click.option('--configyaml', '-c', default=None,
              type=click.Path(exists=False, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
              required=True, show_default=True, help='Path to create config.yaml')
def create_config(configyaml):
    configyaml = Path(configyaml)
    configyaml.parent.mkdir(parents=True, exist_ok=True)
    copyfile(RATTLESNP_CONFIG_PATH.as_posix(), configyaml.as_posix())
    click.edit(require_save=True, extension='.yaml', filename=configyaml)
    click.secho(f"\n    Success create config file on path '{configyaml}'\n    RattleSNP can be run !!", fg="yellow")


@click.command("create_cluster_config", short_help='create cluster_config.yaml', no_args_is_help=True)
@click.option('--clusterconfig', '-c', default=None,
              type=click.Path(exists=False, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
              required=True, show_default=True, help='Path to create cluster_config.yaml')
def create_cluster_config(configyaml):
    configyaml = Path(configyaml)
    configyaml.parent.mkdir(parents=True, exist_ok=True)
    copyfile(RATTLESNP_CLUSTER_CONFIG.as_posix(), configyaml.as_posix())
    click.edit(require_save=True, extension='.yaml', filename=configyaml)
    click.secho(f"\n    Success create cluster_config file on path '{configyaml}'\n   add to --clusterconfig args!!", fg="yellow")
