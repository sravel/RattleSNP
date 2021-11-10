import click
import os
from pathlib import Path
from shutil import copyfile
import rattleSNP


@click.command("edit_tools", short_help='Edit the tools version')
@click.option('--editor', '-e', default="nano", type=click.Choice(['vi', 'vim', 'nano'], case_sensitive=False), prompt='Enter editor name', help='Editor name to mofify tools')
def edit_tools(editor):
    user_tools_path = Path("~/.config/RattlerSNP/tools_path.yaml").expanduser()

    if user_tools_path.exists():
        cmd = f"{editor} {user_tools_path.as_posix()}"
        os.system(cmd)
    else:
        user_tools_path.parent.mkdir(parents=True, exist_ok=True)
        copyfile(rattleSNP.RATTLESNP_TOOLS_PATH, user_tools_path)
        cmd = f"{editor} {user_tools_path}"
        os.system(cmd)