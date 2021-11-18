import click
from click import Abort
from pathlib import Path
from shutil import rmtree, copyfile
import rattleSNP
import os
from cookiecutter.main import cookiecutter
from rattleSNP.global_variable import *


@click.command("install_cluster", short_help='Install RattleSNP on HPC cluster')
@click.option('--scheduler', '-s', default="slurm", type=click.Choice(['slurm', 'sge', 'lsf'], case_sensitive=False),
              prompt='Enter type of install mode', show_default=True, help='Type mode for install')
@click.option('--bash_completion', '-b', is_flag=True, required=False, default=False, show_default=True,
              help='add bash completion on bashrc file')
def install_cluster(scheduler, bash_completion):
    """Run installation for HPC cluster"""
    # add file for installation mode:
    mode_file = RATTLESNP_PATH.joinpath(".mode.txt")
    with mode_file.open("w") as mode:
        mode.write("cluster")
    # build default profile path
    default_profile = RATTLESNP_PROFILE

    if default_profile.exists() and click.confirm(click.style(f'Profile "{default_profile}" exist do you want to remove and continue?', fg="red"), default=False, abort=True):
        rmtree(default_profile, ignore_errors=True)
    default_profile.mkdir(exist_ok=True)
    copyfile(RATTLESNP_PATH.joinpath("/IFB_profile/cluster_config.yaml"), default_profile.joinpath("cluster_config.yaml"))

    # Download cookiecutter of scheduler
    click.secho(f"You choose '{scheduler}' as scheduler. Download cookiecutter:\nhttps://github.com/Snakemake-Profiles/{scheduler.lower()}.git", fg="yellow")
    cookiecutter(f'https://github.com/Snakemake-Profiles/{scheduler.lower()}.git',
                 checkout=None,
                 no_input=True,
                 extra_context={"profile_name": f'',
                                "sbatch_defaults": "--export=ALL",
                                "cluster_config": f"{default_profile}/cluster_config.yaml",
                                "advanced_argument_conversion": 1,
                                "cluster_name": ""
                                },
                 replay=False, overwrite_if_exists=True,
                 output_dir=f'{default_profile}', config_file=None,
                 default_config=False, password=None, directory=None, skip_if_file_exists=True)

    # default slurm cookiecutter not contain all snakemake variables
    if scheduler == "slurm":
        extra_slurm = "use-envmodules: true\nuse-singularity: false\nrerun-incomplete: true\nprintshellcmds: true"
        with open(f"{default_profile}/config.yaml", "a") as config_file:
            config_file.write(extra_slurm)

    # Edit cluster_config.yaml, config.yaml and tools_path.yaml
    try:
        if click.confirm('Now Edit file cluster_config.yaml according to your HPC:\nMore info on ...\n(enter to continue)', default=True, abort=True):
            click.edit(require_save=False, extension='.yaml', filename=f"{default_profile}/cluster_config.yaml")

        if click.confirm('Now Edit file config.yaml according to your HPC:\nMore info on ...\n(enter to continue)', default=True, abort=True):
            click.edit(require_save=False, extension='.yaml', filename=f"{default_profile}/config.yaml")

        if click.confirm('Now Edit file tools_path.yaml according to your HPC:\nMore info on ...\n(enter to continue)', default=True, abort=True):
            click.edit(require_save=False, extension='.yaml', filename=f"{RATTLESNP_TOOLS_PATH}")
    except Abort:
        rmtree(default_profile, ignore_errors=True)
        click.secho(f"INSTALL FAIL remove previous install {default_profile} ", fg="red")

    # export to add bash completion
    if bash_completion:
        build_completion = f"_RATTLESNP_COMPLETE=bash_source rattleSNP > {RATTLESNP_PATH}/rattleSNP-complete.sh"
        os.system(build_completion)
        with open(Path("~/.bashrc").expanduser().as_posix(), "r") as bash_file_read:
            if not [True for line in bash_file_read if "RATTLESNP" in line]:
                with open(Path("~/.bashrc").expanduser().as_posix(), "a") as bash_file_open:
                    append_bashrc = f"\n#Add autocompletion for RATTLESNP\n. {RATTLESNP_PATH}/rattleSNP-complete.sh"
                    bash_file_open.write(append_bashrc)


# @click.command("update", short_help='Update RattleSNP version')
# def update():
#     update_cmd = f"cd {rattleSNP.RATTLESNP_PATH} && git pull"
#     os.system(update_cmd)
