import click
from shutil import copyfile
from rattleSNP.global_variable import *
import os


@click.command("run_cluster", short_help='Run workflow on HPC')
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True), required=True, show_default=True, help='Configuration file for run rattleSNP')
@click.option('--clusterconfig', '-cl', default=None, type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True), required=False, show_default=True, help='Overwrite profile clusterconfig file for run rattleSNP')
@click.option('--profile', '-p', default=RATTLESNP_PROFILE, type=click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True), required=False, show_default=True, help='Path to snakemake profile for run rattleSNP')
@click.option('--tools', '-t', default=RATTLESNP_TOOLS_PATH, type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True), required=False, show_default=True, help='Path to tools_path.yaml for run rattleSNP')
@click.option('--pdf', '-pdf', is_flag=True, required=False, default=False, show_default=True, help='run snakemake with --dag, --rulegraph and --filegraph')
@click.argument('snakemake_other', nargs=-1, type=click.UNPROCESSED)
def run_cluster(config, clusterconfig, profile, tools, pdf, snakemake_other):
    """    
    \b
    Run snakemake command line.
    SNAKEMAKE_OTHER: append other snakemake command such '--dry-run'
    Example:
        rattleSNP run_cluster -c config.yaml --dry-run --jobs 200
    """
    # get user arguments
    click.secho(f'    Config file: {config}', fg='yellow')

    if clusterconfig:
        click.secho(f'    Cluster config file: {clusterconfig}', fg='yellow')
        cmd_clusterconfig = f"--cluster-config {clusterconfig}"
    else:
        cmd_clusterconfig = ""

    click.secho(f'    Profile file: {profile}', fg='yellow')

    if tools:
        copyfile(tools, RATTLESNP_ARGS_TOOLS_PATH)
    elif RATTLESNP_USER_TOOLS_PATH.exists():
        tools = RATTLESNP_USER_TOOLS_PATH
    else:
        tools = RATTLESNP_TOOLS_PATH
    click.secho(f'    Tools file load: {tools}', fg='yellow')

    cmd_snakemake_base = f"snakemake --show-failed-logs -p -s {RATTLESNP_SNAKEFILE} --configfile {config} --profile {profile} {cmd_clusterconfig} {' '.join(snakemake_other)}"
    click.secho(f"    {cmd_snakemake_base}\n", fg='bright_blue')
    # exit()
    os.system(cmd_snakemake_base)

    if pdf:
        dag_cmd_snakemake = f"{cmd_snakemake_base} --dag | dot -Tpdf > schema_pipeline_dag.pdf"
        click.secho(f"    {dag_cmd_snakemake}\n", fg='bright_blue')
        os.system(dag_cmd_snakemake)
        rulegraph_cmd_snakemake = f"{cmd_snakemake_base} --rulegraph | dot -Tpdf > schema_pipeline_global.pdf"
        click.secho(f"    {rulegraph_cmd_snakemake}\n", fg='bright_blue')
        os.system(rulegraph_cmd_snakemake)
        filegraph_cmd_snakemake = f"{cmd_snakemake_base} --filegraph | dot -Tpdf > schema_pipeline_files.pdf"
        click.secho(f"    {filegraph_cmd_snakemake}\n", fg='bright_blue')
        os.system(filegraph_cmd_snakemake)


@click.command("runlocal", short_help='Run workflow on local computer (use singularity mandatory)')
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