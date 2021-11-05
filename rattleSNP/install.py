import click
from pathlib import Path
import rattleSNP
import os


@click.option('--use_module', '-m', default=True, type=click.Choice(['True', 'False'], case_sensitive=False), prompt='use module envs?', help='Use modules on cluster')
def cluster(use_module=False):
    """Run the workflow"""
    if use_module :
        print("use_module")



@click.command("install", short_help='install RattleSNP')
@click.option('--editor', '-e', default="nano", type=click.Choice(['vi', 'vim', 'nano'], case_sensitive=False), prompt='Enter editor name', help='Editor name to mofify tools')
@click.option('--mode', '-m', default="local", type=click.Choice(['local', 'cluster'], case_sensitive=False), prompt='Enter type of install mode', help='Type mode for install')
def install(editor, mode):
    """Run the workflow"""
    if mode == "local":
        print("install for local")
    elif mode == "cluster":
        print("install for cluster")
        cluster()