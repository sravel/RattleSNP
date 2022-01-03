#!/usr/bin/env python3
import click
import rattleSNP
from rattleSNP.usefull_function import get_install_mode, check_privileges
from rattleSNP.global_variable import *


@click.group(help=click.secho(rattleSNP.description_tools, fg='green', nl=False), context_settings={'help_option_names': ('-h', '--help'),"max_content_width":800},
             invoke_without_command=True, no_args_is_help=True)
@click.option('--restore', '-r', is_flag=True, required=False, default=False, show_default=True, help='Restore installation mode (need root or sudo)')
@click.version_option(rattleSNP.__version__, '--version', '-v')
@click.pass_context
def main(ctx, restore):
    if ctx.invoked_subcommand is None and restore and check_privileges():

        if RATTLESNP_MODE.exists():
            RATTLESNP_MODE.unlink()
    pass


# Hack for build docs with unspecified install
args = str(sys.argv)
if "sphinx" in args:
    main.add_command(rattleSNP.run_cluster)
    main.add_command(rattleSNP.create_cluster_config)
    main.add_command(rattleSNP.create_config)
    main.add_command(rattleSNP.edit_tools)
    # main.add_command(rattleSNP.run_local)
    main.add_command(rattleSNP.install_cluster)
    # main.add_command(rattleSNP.install_local)
    # main.add_command(rattleSNP.test_install)
else:
    mode = get_install_mode()
    if mode == "cluster":
        # main.add_command(rattleSNP.test_install)
        main.add_command(rattleSNP.run_cluster)
        main.add_command(rattleSNP.create_cluster_config)
        main.add_command(rattleSNP.create_config)
        main.add_command(rattleSNP.edit_tools)
    # elif mode == "local":
    #     main.add_command(rattleSNP.test_install)
    #     main.add_command(rattleSNP.run_local)
    #     main.add_command(rattleSNP.create_config)
    else:
        main.add_command(rattleSNP.install_cluster)
        # main.add_command(rattleSNP.install_local)


if __name__ == '__main__':
    main()
