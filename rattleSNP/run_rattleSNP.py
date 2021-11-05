#!/usr/bin/env python3
import click
import rattleSNP

@click.group(help=rattleSNP.description_tools)
def rattle_cli():
    pass


rattle_cli.add_command(rattleSNP.run)
rattle_cli.add_command(rattleSNP.runlocal)
rattle_cli.add_command(rattleSNP.edit_tools)
rattle_cli.add_command(rattleSNP.install)

def main():
    rattle_cli()

if __name__ == '__main__':
    main()
