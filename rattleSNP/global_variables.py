from pathlib import Path

DOCS = "https://rattlesnp.readthedocs.io/en/latest/"
GIT_URL = "https://github.com/sravel/RattleSNP"

INSTALL_PATH = Path(__file__).resolve().parent
SINGULARITY_URL_FILES = [('https://itrop.ird.fr/culebront_utilities/singularity_build/Singularity.culebront_tools.sif',
                          f'{INSTALL_PATH}/containers/Singularity.rattleSNP_tools.sif'),
                         ('https://itrop.ird.fr/culebront_utilities/singularity_build/Singularity.report.sif',
                          f'{INSTALL_PATH}/containers/Singularity.report.sif')
                         ]

DATATEST_URL_FILES = ("Data-Xoo-sub.zip", "https://itrop.ird.fr/culebront_utilities/Data-Xoo-sub.zip")


ALLOW_FASTQ_EXT = (".fastq", ".fq", ".fq.gz", ".fastq.gz")
AVAIL_CLEANING = ("ATROPOS", "FASTQC")
AVAIL_MAPPING = ("BWA_MEM", "BWA_SAMPE")
