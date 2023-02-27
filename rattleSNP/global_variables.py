from pathlib import Path

DOCS = "https://rattlesnp.readthedocs.io/en/latest/"
GIT_URL = "https://forge.ird.fr/phim/sravel/RattleSNP"

INSTALL_PATH = Path(__file__).resolve().parent
SINGULARITY_URL_FILES = [('http://nas-bgpi.myds.me/DOC/rattleSNP/Singularity.rattleSNP_tools.sif',
                        f'{INSTALL_PATH}/containers/Singularity.rattleSNP_tools.sif'),
                        ('http://nas-bgpi.myds.me/DOC/rattleSNP/Singularity.report.sif',
                        f'{INSTALL_PATH}/containers/Singularity.report.sif')
                        ]
SCRIPTS = INSTALL_PATH.joinpath("scripts")
DATATEST_URL_FILES = ("data_test_rattleSNP.zip", "http://nas-bgpi.myds.me/DOC/rattleSNP/data_test_rattleSNP.zip")

ALLOW_FASTQ_EXT = (".fastq", ".fq", ".fq.gz", ".fastq.gz")
AVAIL_CLEANING = ("ATROPOS", "FASTQC")
AVAIL_MAPPING = ("BWA_MEM", "BWA_SAMPE")
