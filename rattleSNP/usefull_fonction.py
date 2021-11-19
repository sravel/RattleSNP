from pathlib import Path

def get_install_mode():
    """detect install mode"""
    if Path(__file__).resolve().parent.parent.joinpath(".mode.txt").exists():
        return Path(__file__).resolve().parent.parent.joinpath(".mode.txt").open("r").readline().strip()
    else:
        return "notInstall"

def get_version():
    """Read VERSION file to know current version
    Returns:
        version: actual version read on the VERSION file
    Examples:
        >>> version = get_version()
        >>> print(version)
            1.3.0
    """
    with open(Path(__file__).resolve().parent.parent.joinpath("VERSION"), 'r') as version_file:
        return version_file.readline().strip()

def get_last_version(url, current_version):
    """Function for know the last version of Git repo in website"""
    try:
        from urllib.request import urlopen
        from re import search
        import click
        module_mane = url.split('/')[-1]
        HTML = urlopen(f"{url}/tags").read().decode('utf-8')
        str_search = f"{url.replace('https://github.com', '')}/releases/tag/.*"
        lastRelease = search(str_search, HTML).group(0).split("/")[-1].split('"')[0]
        epilogTools = ""
        if str(current_version) != lastRelease:
            if lastRelease < str(current_version):
                epilogTools = click.style(f"\n    ** NOTE: This {module_mane} version is higher than the production version, you are using a dev version\n", fg="yellow", bold=True)
            elif lastRelease > str(current_version):
                epilogTools = click.style(f"\n    NOTE: The Latest version of {module_mane} {lastRelease} is available at {url}/releases\n",fg="yellow", underline=True)
        return epilogTools
    except Exception as e:
        epilogTools = click.style(f"\n    ** ENABLE TO GET LAST VERSION, check internet connection\n{e}\n", fg="red")
        return epilogTools

def get_list_chromosome_names(fasta_file):
    """
            Return the list of sequence name on the fasta file.
            Work with Biopython and python version >= 3.5
    """
    from Bio import SeqIO
    return [*SeqIO.to_dict(SeqIO.parse(fasta_file,"fasta"))]


def get_files_ext(path, extensions, add_ext=True):
    """List of files with specify extension include on folder
    Arguments:
        path (str): a path to folder
        extensions (list or tuple): a list or tuple of extension like (".py")
        add_ext (bool): if True (default), file have extension

    Returns:
        :class:`list`: List of files name with or without extension , with specify extension include on folder
        :class:`list`: List of  all extension found

    Examples:
        >>> all_files, files_ext = get_files_ext("/path/to/fastq")
        >>> print(files_ext)
            [".fastq"]
     """
    if not (extensions, (list, tuple)) or not extensions:
        raise ValueError(f'ERROR RattleSNP: "extensions" must be a list or tuple not "{type(extensions)}"\n')
    tmp_all_files = []
    all_files = []
    files_ext = []
    for ext in extensions:
        tmp_all_files.extend(Path(path).glob(f"**/*{ext}"))

    for elm in tmp_all_files:
        ext = "".join(elm.suffixes)
        if ext not in files_ext:
            files_ext.append(ext)
        if add_ext:
            all_files.append(elm.as_posix())
        else:
            if len(elm.suffixes) > 1:

                all_files.append(Path(elm.stem).stem)
            else:
                all_files.append(elm.stem)
    return all_files, files_ext
