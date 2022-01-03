import click
from click import Abort
from pathlib import Path
from shutil import rmtree, copyfile, unpack_archive
import rattleSNP
import os
import re
from cookiecutter.main import cookiecutter
from rattleSNP.global_variable import *
from rattleSNP.usefull_function import command_required_option_from_option, multiprocessing_download, get_install_mode

required_options = {
    True: 'modules_dir',
    False: 'scheduler'
}


def create_bash_completion():
    bashrc_file = Path("~/.bashrc").expanduser().as_posix()
    import subprocess
    output = subprocess.run(
        ["bash", "-c", "echo ${BASH_VERSION}"], stdout=subprocess.PIPE
    )
    match = re.search(r"^(\d+)\.(\d+)\.\d+", output.stdout.decode())
    if match is not None:
        major, minor = match.groups()
    if major < "4" or (major == "4" and minor < "4"):
        raise RuntimeError("Shell completion is not supported for Bash versions older than 4.4.")
    else:
        if not Path(f"{RATTLESNP_PATH}/rattleSNP-complete.sh").exists():
            build_completion = f"_RATTLESNP_COMPLETE=bash_source rattleSNP > {RATTLESNP_PATH}/rattleSNP-complete.sh"
            os.system(build_completion)
        with open(bashrc_file, "r") as bash_file_read:
            if not [True for line in bash_file_read if "RATTLESNP" in line]:
                with open(bashrc_file, "a") as bash_file_open:
                    append_bashrc = f"\n#Add autocompletion for RATTLESNP\n. {RATTLESNP_PATH}/rattleSNP-complete.sh"
                    bash_file_open.write(append_bashrc)
                    click.secho(f"INSTALL autocompletion for RATTLESNP on {bashrc_file} with command {append_bashrc}\nUpdate with commande:\nsource ~/.bashrc",
                                fg="yellow")
            else:
                click.secho(f"warning autocompletion for RATTLESNP  already found on {bashrc_file} please check path",
                            fg="yellow")


def create_envmodules(modules_dir):
    from rattleSNP import MODULE_FILE
    modules_dir = Path(modules_dir)
    modules_dir.mkdir(parents=True, exist_ok=True)
    modules_dir.joinpath(f"{rattleSNP.__version__}").open("w").write(MODULE_FILE)
    click.edit(require_save=False, extension='', filename=modules_dir.joinpath(f"{rattleSNP.__version__}").as_posix())
    click.secho(f"\n    Success install module file for version {rattleSNP.__version__} on path '{modules_dir}'", fg="yellow")


@click.command("install_cluster", short_help='Install rattleSNP on HPC cluster', context_settings=dict(max_content_width=800),
               cls=command_required_option_from_option('create_envmodule', required_options), no_args_is_help=True)
@click.option('--scheduler', '-s', default="slurm", type=click.Choice(['slurm', 'sge', 'lsf'], case_sensitive=False),
              prompt='Choose your HPC scheduler', show_default=True, help='Type the HPC scheduler')
@click.option('--env', '-e', default="modules", type=click.Choice(['modules', 'singularity'], case_sensitive=False),
              prompt='Choose mode for tools dependencies', show_default=True, help='Mode for tools dependencies ')
@click.option('--bash_completion/--no-bash_completion', is_flag=True, required=False, default=True, show_default=True,
              help='Allow bash completion of rattleSNP commands on the bashrc file')
@click.option('--create_envmodule/--no-create_enmodules', is_flag=True, required=False, default=False, show_default=True,
              help='Create a env module file allowing load rattleSNP in a cluster')
@click.option('--modules_dir', '-m', default=None,
              type=click.Path(exists=False, dir_okay=True, file_okay=False, readable=True, resolve_path=True),
              required=False, show_default=True, help='Directory used to save the module created by --create_envmodule parameter', is_eager=True)
def install_cluster(scheduler, env, bash_completion, create_envmodule, modules_dir):
    """Run installation for HPC cluster"""
    # add file for installation mode:
    mode_file = RATTLESNP_MODE
    # build default profile path
    default_profile = RATTLESNP_PROFILE

    def fail():
        rmtree(default_profile, ignore_errors=True)
        mode_file.unlink(missing_ok=True)
        click.secho(f"INSTALL FAIL remove previous install {default_profile} ", fg="red")
        exit()

    # test if install already run
    try:
        if default_profile.exists() and click.confirm(click.style(f'Profile "{default_profile}" exist do you want to remove and continue?', fg="red"), default=False, abort=True):
            rmtree(default_profile, ignore_errors=True)
        default_profile.mkdir(exist_ok=True)

        default_cluster = RATTLESNP_PATH.joinpath("install_files",f"cluster_config_{scheduler.upper()}.yaml")
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
                extra_slurm = f"use-envmodules: {'true' if env == 'modules' else 'false' }\nuse-singularity: {'true' if env == 'singularity' else 'false' }\nrerun-incomplete: true\nprintshellcmds: true"
                with open(f"{default_profile}/config.yaml", "a") as config_file:
                    config_file.write(extra_slurm)

            # Edit cluster_config.yaml, config.yaml and tools_path.yaml
            if click.confirm(click.style(f'Now Edit file cluster_config.yaml according to your HPC:\nMore info on on {DOCS} \n(enter to continue)', fg="blue"), default=True, abort=True, show_default=True):
                click.edit(require_save=False, extension='.yaml', filename=f"{default_profile}/cluster_config.yaml")

            if click.confirm(click.style(f'Now Edit file config.yaml according to your HPC:\nMore info on {DOCS}\n(enter to continue)', fg="blue"), default=True, abort=True, show_default=True):
                click.edit(require_save=False, extension='.yaml', filename=f"{default_profile}/config.yaml")

            if click.confirm(click.style(f'Now Edit file tools_path.yaml according to your HPC:\nMore info on {DOCS}\n(enter to continue)', fg="blue"), default=True, abort=True, show_default=True):
                click.edit(require_save=False, extension='.yaml', filename=f"{RATTLESNP_TOOLS_PATH}")
            click.secho(f"\n    Profile is success install on {default_profile}", fg="yellow")
        except Abort:
            fail()
    except Abort:
        click.secho(f"\n    Profile is already created, skipping {default_profile}", fg="yellow")
    except Exception as e:
        print(e)
        fail()

    # if env == 'singularity'
    # if env == 'singularity':
    #     results = multiprocessing_download(SINGULARITY_URL_FILES)
    #     for r in results:
    #         click.secho(r, fg="blue")

    # if envmodule activation
    try:
        if create_envmodule:
            create_envmodules(modules_dir)

        # export to add bash completion
        if bash_completion:
            create_bash_completion()
        click.secho(f"\n    Congratulations, you have successfully installed rattleSNP !!!\n\n", fg="green", bold=True)
        mode_file.open("w").write("cluster")
    except Exception as e:
        click.secho(f"\n   ERROR : an error was detected, please check {e}",  fg="red")
        fail()
