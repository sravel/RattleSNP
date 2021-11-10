import click
from pathlib import Path
import shutil
import rattleSNP
import os
from cookiecutter.main import cookiecutter


@click.command("install_cluster", short_help='Install RattleSNP on HPC cluster')
@click.option('--editor', '-e', default="nano", type=click.Choice(['vi', 'vim', 'nano'], case_sensitive=False),
              prompt='Enter editor name', help='Editor name to mofify tools')
@click.option('--scheduler', '-s', default="slurm", type=click.Choice(['slurm', 'sge', 'lsf'], case_sensitive=False),
              prompt='Enter type of install mode', help='Type mode for install')
@click.option('--bash_completion', '-b', is_flag=True, required=False, default=True, help='add bash completion on bashrc file (default: true)')
def install_cluster(editor, scheduler, bash_completion):
    """Run installation for HPC cluster"""
    print(f"You choose '{scheduler}' as scheduler")
    default_profile = f"{rattleSNP.RATTLESNP_PROFILE}"
    if Path(default_profile).exists():
        shutil. rmtree(Path(default_profile).as_posix(), ignore_errors=True)
    Path(default_profile).mkdir(exist_ok=True)
    cp_cluster_config = f"cp {rattleSNP.RATTLESNP_PATH}/IFB_profile/cluster_config.yaml {default_profile}"
    os.system(cp_cluster_config)
    cookiecutter(f'https://github.com/Snakemake-Profiles/{scheduler.lower()}.git',
                 checkout=None,
                 no_input=True,
                 extra_context={"profile_name": f'',
                                "sbatch_defaults": "--export=ALL",
                                "cluster_config": f"{default_profile}cluster_config.yaml",
                                "advanced_argument_conversion": 1,
                                "cluster_name": ""
                                },
                 replay=False, overwrite_if_exists=True,
                 output_dir=f'{default_profile}', config_file=None,
                 default_config=False, password=None, directory=None, skip_if_file_exists=True)

    if scheduler == "slurm":
        extra_slurm = "use-envmodules: true\nuse-singularity: false\nrerun-incomplete: true\nprintshellcmds: true"
        with open(f"{default_profile}/config.yaml", "a") as config_file:
            config_file.write(extra_slurm)
    print("Now Edit file cluster_config.yaml according to your HPC:\nMore info on ...\n(enter to continue)")
    x = input()
    cmd_profile = f"{editor} {default_profile}/cluster_config.yaml;"
    os.system(cmd_profile)
    print("Now Edit file config.yaml according to your HPC:\nMore info on ...\n(enter to continue)")
    x = input()
    cmd_profile = f"{editor} {default_profile}/config.yaml;"
    os.system(cmd_profile)
    print("Now Edit file tools_path.yaml according to your HPC:\nMore info on ...\n(enter to continue)")
    x = input()
    cmd = f"{editor} {rattleSNP.RATTLESNP_TOOLS_PATH}"
    os.system(cmd)

    # export to add bash completion
    if bash_completion:
        build_completion = f"_RATTLESNP_COMPLETE=source rattleSNP > {rattleSNP.RATTLESNP_PATH}/rattleSNP-complete.sh"
        os.system(build_completion)
        with open(Path("~/.bashrc").expanduser().as_posix(), "r") as bash_file_read:
            if not [True for line in bash_file_read if "RATTLESNP" in line]:
                with open(Path("~/.bashrc").expanduser().as_posix(), "a") as bash_file_open:
                    append_bashrc = f"#Add autocompletion for RATTLESNP\n. {rattleSNP.RATTLESNP_PATH}/rattleSNP-complete.sh"
                    bash_file_open.write(append_bashrc)


@click.command("update", short_help='Update RattleSNP version')
def update():
    update_cmd = f"cd {rattleSNP.RATTLESNP_PATH} && git pull"
    os.system(update_cmd)