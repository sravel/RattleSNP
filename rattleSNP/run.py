import click
from pathlib import Path
import rattleSNP
import os

@click.command("run", short_help='run workflow on HPC')
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help='Configuration file for run rattleSNP')
@click.option('--clusterconfig', '-k', default=None, type=click.Path(exists=True), required=False, help='Overwrite profile clusterconfig file for run rattleSNP')
@click.option('--profile', '-k', default=None, type=click.Path(exists=True), required=False, help='Path to snakemake profile for run rattleSNP')
@click.option('--tools', '-t', default=None, type=click.Path(exists=True), required=False, help='Path to tools_path.yaml for run rattleSNP')
@click.option('--additional', '-a', default=None, type=str, required=False, help='Additional snakemake command line arguments')
@click.option('--pdf', '-p', is_flag=True, required=False, default=False, help='run snakemake with --dag, --rulegraph and --filegraph')
def run(config, clusterconfig, profile, tools, additional, pdf):
    """Run the workflow"""

    user_tools_path = Path("~/.config/RattlerSNP/tools_path.yaml").expanduser()

    # get user arguments
    config = Path(config).resolve()

    if clusterconfig:
        clusterconfig = Path(clusterconfig).resolve()
        cmd_clusterconfig = f"--cluster-config {clusterconfig}"
    else:
        cmd_clusterconfig = ""

    if profile:
        profile = Path(profile).resolve()
    else:
        profile = rattleSNP.RATTLESNP_PROFILE

    if tools:
        rattleSNP.RATTLESNP_TOOLS_PATH = Path(tools).resolve()
    elif user_tools_path.exists():
        rattleSNP.RATTLESNP_TOOLS_PATH = user_tools_path

    print(rattleSNP.description_tools)
    print(f'    Config file: {config}')
    print(f'    Cluster config file: {clusterconfig}')
    print(f'    Profile file: {profile}')
    print(f'    Tools file load: {rattleSNP.RATTLESNP_TOOLS_PATH}')

    cmd_snakemake_base = f"snakemake --show-failed-logs -p -s {rattleSNP.RATTLESNP_SNAKEFILE} --configfile {config.as_posix()} --profile {profile.as_posix()} {cmd_clusterconfig} {additional}"
    print(f"    {cmd_snakemake_base}\n")

    os.system(cmd_snakemake_base)
    if pdf:
        dag_cmd_snakemake = f"{cmd_snakemake_base} --dag | dot -Tpdf > schema_pipeline_dag.pdf"
        os.system(dag_cmd_snakemake)
        rulegraph_cmd_snakemake = f"{cmd_snakemake_base} --rulegraph | dot -Tpdf > schema_pipeline_global.pdf"
        os.system(rulegraph_cmd_snakemake)
        filegraph_cmd_snakemake = f"{cmd_snakemake_base} --filegraph | dot -Tpdf > schema_pipeline_files.pdf"
        os.system(filegraph_cmd_snakemake)

@click.command("runlocal", short_help='run workflow on local computer (use singularity mandatory)')
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help='Configuration file for run rattleSNP')
@click.option('--threads', '-t', default=1, type=int, required=True, help='number of threads')
@click.option('--additional', '-a', default="", type=str, required=False, help='Additional snakemake command line arguments')
@click.option('--pdf', '-p', is_flag=True, required=False, default=False, help='run snakemake with --dag, --rulegraph and --filegraph')
def runlocal(config, threads, additional, pdf):
    """Run the workflow"""
    # get user arguments
    config = Path(config).resolve()

    print(rattleSNP.description_tools)
    print(f'    Config file: {config}')

    cmd_snakemake_base = f"snakemake --cores {threads} --show-failed-logs --printshellcmds -s {rattleSNP.RATTLESNP_SNAKEFILE} --configfile {config.as_posix()} {additional}"
    print(f"    {cmd_snakemake_base}\n")

    os.system(cmd_snakemake_base)
    if pdf:
        dag_cmd_snakemake = f"{cmd_snakemake_base} --dag | dot -Tpdf > schema_pipeline_dag.pdf"
        os.system(dag_cmd_snakemake)
        rulegraph_cmd_snakemake = f"{cmd_snakemake_base} --rulegraph | dot -Tpdf > schema_pipeline_global.pdf"
        os.system(rulegraph_cmd_snakemake)
        filegraph_cmd_snakemake = f"{cmd_snakemake_base} --filegraph | dot -Tpdf > schema_pipeline_files.pdf"
        os.system(filegraph_cmd_snakemake)