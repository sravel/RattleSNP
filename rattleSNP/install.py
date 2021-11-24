import click
from click import Abort
from pathlib import Path
from shutil import rmtree, copyfile
import rattleSNP
import os
from cookiecutter.main import cookiecutter
from rattleSNP.global_variable import *
from rattleSNP.usefull_fonction import command_required_option_from_option

required_options = {
    True: 'modules_dir',
    False: 'scheduler'
}

@click.command("install_cluster", short_help='Install RattleSNP on HPC cluster', context_settings=dict(max_content_width=800),
               cls=command_required_option_from_option('create_envmodule', required_options))
@click.option('--scheduler', '-s', default="slurm", type=click.Choice(['slurm', 'sge', 'lsf'], case_sensitive=False),
              prompt='Enter type of install mode', show_default=True, help='Type mode for install')
@click.option('--bash_completion', '-b', is_flag=True, required=False, default=False, show_default=True,
              help='add bash completion on bashrc file')
@click.option('--create_envmodule', '-c', is_flag=True, required=False, default=False, show_default=True,
              help='add env module file for cluster')
@click.option('--modules_dir', '-m', default=None,
              type=click.Path(exists=False, dir_okay=True, readable=True, resolve_path=True),
              required=False, show_default=True, help='Path to install module file', is_eager=True)
def install_cluster(scheduler, bash_completion, create_envmodule, modules_dir):
    """Run installation for HPC cluster"""

    # build default profile path
    default_profile = RATTLESNP_PROFILE
    mode_file = RATTLESNP_PATH.joinpath(".mode.txt")
    def fail():
        rmtree(default_profile, ignore_errors=True)
        mode_file.unlink(missing_ok=True)
        click.secho(f"INSTALL FAIL remove previous install {default_profile} ", fg="red")

    # test if install already run
    try:
        if default_profile.exists() and click.confirm(click.style(f'Profile "{default_profile}" exist do you want to remove and continue?', fg="red"), default=False, abort=True):
            rmtree(default_profile, ignore_errors=True)
        default_profile.mkdir(exist_ok=True)

        default_cluster = RATTLESNP_PATH.joinpath(f"profiles/cluster_config_{scheduler.upper()}.yaml")
        copyfile(default_cluster, default_profile.joinpath("cluster_config.yaml"))

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
        try:
            # default slurm cookiecutter not contain all snakemake variables
            if scheduler == "slurm":
                extra_slurm = "use-envmodules: true\nuse-singularity: false\nrerun-incomplete: true\nprintshellcmds: true"
                with open(f"{default_profile}/config.yaml", "a") as config_file:
                    config_file.write(extra_slurm)
            # add file for installation mode:

            with mode_file.open("w") as mode:
                mode.write("cluster")
            # Edit cluster_config.yaml, config.yaml and tools_path.yaml
            if click.confirm('Now Edit file cluster_config.yaml according to your HPC:\nMore info on ...\n(enter to continue)', default=True, abort=True):
                click.edit(require_save=False, extension='.yaml', filename=f"{default_profile}/cluster_config.yaml")

            if click.confirm('Now Edit file config.yaml according to your HPC:\nMore info on ...\n(enter to continue)', default=True, abort=True):
                click.edit(require_save=False, extension='.yaml', filename=f"{default_profile}/config.yaml")

            if click.confirm('Now Edit file tools_path.yaml according to your HPC:\nMore info on ...\n(enter to continue)', default=True, abort=True):
                click.edit(require_save=False, extension='.yaml', filename=f"{RATTLESNP_TOOLS_PATH}")
            else:
                print("else")
        except Abort:
            fail()
    except Abort:
        pass
    except Exception as e:
        print(e)
        fail()

    # if envmodule activation
    try:
        if create_envmodule:
            create_envmodules(modules_dir)

        # export to add bash completion
        if bash_completion:
            bashrc_file = Path("~/.bashrc").expanduser().as_posix()
            build_completion = f"_RATTLESNP_COMPLETE=bash_source rattleSNP > {RATTLESNP_PATH}/rattleSNP-complete.sh"
            os.system(build_completion)
            with open(bashrc_file, "r") as bash_file_read:
                if not [True for line in bash_file_read if "RATTLESNP" in line]:
                    with open(bashrc_file, "a") as bash_file_open:
                        append_bashrc = f"\n#Add autocompletion for RATTLESNP\n. {RATTLESNP_PATH}/rattleSNP-complete.sh"
                        bash_file_open.write(append_bashrc)
                        click.secho(f"INSTALL autocompletion for RATTLESNP on {bashrc_file} with command {append_bashrc} ", fg="yellow")
                else:
                    click.secho(f"warning autocompletion for RATTLESNP  already found on {bashrc_file} please check path",
                                fg="yellow")
    except Exception as e:
        print(e)
        fail()

# @click.command("create_envmodule", short_help='add env module file for cluster', context_settings=dict(max_content_width=800))
# @click.option('--modules_dir', '-m', default=RATTLESNP_MODULE_PATH,
#               type=click.Path(exists=False, dir_okay=True, readable=True, resolve_path=True),
#               required=False, show_default=True, help='Path to install module file')
def create_envmodules(modules_dir):
    from rattleSNP import MODULE_FILE
    modules_dir = Path(modules_dir)
    modules_dir.mkdir(parents=True, exist_ok=True)
    modules_dir.joinpath(f"{rattleSNP.__version__}").open("w").write(MODULE_FILE)
    click.edit(require_save=False, extension='', filename=modules_dir.joinpath(f"{rattleSNP.__version__}").as_posix())
    click.secho(f"\n    Success install module file for version {rattleSNP.__version__} on path '{modules_dir}'", fg="yellow")




# @click.command("update", short_help='Update RattleSNP version')
# def update():
#     update_cmd = f"cd {rattleSNP.RATTLESNP_PATH} && git pull"
#     os.system(update_cmd)
