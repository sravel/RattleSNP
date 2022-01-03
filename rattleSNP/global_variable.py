from pathlib import Path
import sys

DOCS="https://rattlesnp.readthedocs.io/en/latest/"
# Hack for build docs with unspecified path install
args = str(sys.argv)
if "sphinx" in args:
    RATTLESNP_PATH = Path("/Path/to/culebrONT_install/")
else:
    RATTLESNP_PATH = Path(__file__).resolve().parent
RATTLESNP_SNAKEFILE = RATTLESNP_PATH.joinpath("snakefiles", "Snakefile")
RATTLESNP_MODE = RATTLESNP_PATH.joinpath(".mode.txt")
RATTLESNP_SCRIPTS = RATTLESNP_PATH.joinpath("snakemake_scripts")
RATTLESNP_PROFILE = RATTLESNP_PATH.joinpath("default_profile")
RATTLESNP_CONFIG_PATH = RATTLESNP_PATH.joinpath("install_files", "config.yaml")

RATTLESNP_TOOLS_PATH = RATTLESNP_PATH.joinpath("install_files", "tools_path.yaml")
RATTLESNP_USER_TOOLS_PATH = Path("~/.config/RattleSNP/tools_path.yaml").expanduser()
RATTLESNP_ARGS_TOOLS_PATH = Path("~/.config/RattleSNP/tools_path_args.yaml").expanduser()

RATTLESNP_CLUSTER_CONFIG = RATTLESNP_PROFILE.joinpath("cluster_config.yaml")
RATTLESNP_USER_CLUSTER_CONFIG = Path("~/.config/CulebrONT/cluster_config.yaml").expanduser()
RATTLESNP_ARGS_CLUSTER_CONFIG = Path("~/.config/CulebrONT/cluster_config_args.yaml").expanduser()


ALLOW_FASTQ_EXT = (".fastq",".fq",".fq.gz",".fastq.gz")
AVAIL_CLEANING = ("ATROPOS", "FASTQC")
AVAIL_MAPPING = ("BWA_MEM", "BWA_SAMPE")